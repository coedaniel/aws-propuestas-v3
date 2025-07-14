"""
Enhanced S3 uploader with better error handling and monitoring
"""
import boto3
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import os
from botocore.exceptions import ClientError, NoCredentialsError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class EnhancedS3DocumentUploader:
    def __init__(self):
        """Initialize S3 client with enhanced error handling"""
        try:
            self.s3_client = boto3.client('s3')
            self.bucket_name = os.environ.get('S3_BUCKET_NAME', 'aws-propuestas-documents')
            logger.info(f"✅ S3 CLIENT INITIALIZED - Bucket: {self.bucket_name}")
            
            # Test bucket access
            self._test_bucket_access()
            
        except NoCredentialsError:
            logger.error("❌ AWS CREDENTIALS NOT FOUND")
            raise
        except Exception as e:
            logger.error(f"❌ FAILED TO INITIALIZE S3 CLIENT: {str(e)}")
            raise
    
    def _test_bucket_access(self) -> bool:
        """Test if bucket is accessible"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"✅ BUCKET ACCESS VERIFIED: {self.bucket_name}")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.error(f"❌ BUCKET NOT FOUND: {self.bucket_name}")
            elif error_code == '403':
                logger.error(f"❌ BUCKET ACCESS DENIED: {self.bucket_name}")
            else:
                logger.error(f"❌ BUCKET ACCESS ERROR: {error_code}")
            return False
        except Exception as e:
            logger.error(f"❌ UNEXPECTED BUCKET ERROR: {str(e)}")
            return False
    
    def upload_document(self, content: str, filename: str, content_type: str = 'text/plain', metadata: Dict[str, str] = None) -> Optional[str]:
        """
        Upload document to S3 with enhanced error handling and retry logic
        """
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Validate inputs
                if not content or not filename:
                    logger.error("❌ UPLOAD FAILED: Missing content or filename")
                    return None
                
                # Generate unique key with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                key = f"documents/{timestamp}_{filename}"
                
                logger.info(f"📤 UPLOADING TO S3 (attempt {retry_count + 1}): {key} ({len(content)} bytes)")
                
                # Prepare metadata
                upload_metadata = {
                    'upload_time': timestamp,
                    'content_length': str(len(content)),
                    'generator': 'intelligent_architect_v3.2.1',
                    'retry_count': str(retry_count)
                }
                
                if metadata:
                    upload_metadata.update(metadata)
                
                # Upload with metadata
                response = self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=key,
                    Body=content.encode('utf-8'),
                    ContentType=content_type,
                    Metadata=upload_metadata,
                    ServerSideEncryption='AES256'  # Enable encryption
                )
                
                # Generate public URL
                url = f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
                
                logger.info(f"✅ UPLOAD SUCCESS: {url}")
                return url
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                retry_count += 1
                
                if error_code in ['NoSuchBucket', 'AccessDenied']:
                    logger.error(f"❌ PERMANENT ERROR - {error_code}: {str(e)}")
                    break
                elif retry_count < max_retries:
                    logger.warning(f"⚠️ RETRY {retry_count}/{max_retries} - {error_code}: {str(e)}")
                    continue
                else:
                    logger.error(f"❌ MAX RETRIES EXCEEDED - {error_code}: {str(e)}")
                    break
                    
            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    logger.warning(f"⚠️ RETRY {retry_count}/{max_retries} - Unexpected error: {str(e)}")
                    continue
                else:
                    logger.error(f"❌ UPLOAD FAILED AFTER {max_retries} RETRIES: {str(e)}")
                    break
        
        return None
    
    def upload_multiple_documents(self, documents: Dict[str, str], service_name: str, project_id: str = None) -> Dict[str, Optional[str]]:
        """
        Upload multiple documents with service-specific naming
        Enhanced with better error handling and progress tracking
        """
        results = {}
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        logger.info(f"📤 UPLOADING {len(documents)} DOCUMENTS FOR {service_name}")
        
        for doc_type, content in documents.items():
            try:
                if not content or len(content.strip()) < 10:
                    logger.warning(f"⚠️ SKIPPING EMPTY/SHORT DOCUMENT: {doc_type}")
                    results[doc_type] = None
                    continue
                
                # Service-specific filename
                filename_parts = [service_name.replace(' ', '_')]
                if project_id:
                    filename_parts.append(project_id)
                filename_parts.extend([doc_type.replace(' ', '_'), timestamp])
                filename = f"{'_'.join(filename_parts)}.txt"
                
                # Determine content type
                content_type = self._get_content_type(doc_type, content)
                
                # Prepare metadata
                metadata = {
                    'service': service_name,
                    'document_type': doc_type,
                    'project_id': project_id or 'unknown'
                }
                
                # Upload document
                url = self.upload_document(content, filename, content_type, metadata)
                results[doc_type] = url
                
                if url:
                    logger.info(f"✅ {doc_type}: SUCCESS")
                else:
                    logger.error(f"❌ {doc_type}: FAILED")
                    
            except Exception as e:
                logger.error(f"❌ ERROR UPLOADING {doc_type}: {str(e)}")
                results[doc_type] = None
        
        # Summary
        successful = sum(1 for url in results.values() if url)
        total = len(results)
        logger.info(f"📊 UPLOAD SUMMARY: {successful}/{total} successful")
        
        return results
    
    def _get_content_type(self, doc_type: str, content: str) -> str:
        """Determine content type based on document type and content"""
        doc_type_lower = doc_type.lower()
        
        if 'json' in doc_type_lower or content.strip().startswith('{'):
            return 'application/json'
        elif 'yaml' in doc_type_lower or 'yml' in doc_type_lower or content.strip().startswith('AWSTemplateFormatVersion'):
            return 'text/yaml'
        elif 'csv' in doc_type_lower or ',' in content[:100]:
            return 'text/csv'
        elif 'html' in doc_type_lower or content.strip().startswith('<'):
            return 'text/html'
        else:
            return 'text/plain'
    
    def create_project_summary(self, project_info: Dict[str, Any], documents: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """
        Create comprehensive project summary with enhanced metadata
        """
        try:
            successful_uploads = [url for url in documents.values() if url]
            failed_uploads = [doc_type for doc_type, url in documents.items() if not url]
            
            summary = {
                'project_id': project_info.get('project_id', 'unknown'),
                'service': project_info.get('service', 'AWS'),
                'description': project_info.get('description', ''),
                'objective': project_info.get('objective', ''),
                'created_at': datetime.now().isoformat(),
                'documents': documents,
                'status': 'completed' if successful_uploads else 'failed',
                'document_count': len(successful_uploads),
                'total_documents': len(documents),
                'failed_documents': failed_uploads,
                'success_rate': len(successful_uploads) / len(documents) if documents else 0,
                'bucket_name': self.bucket_name
            }
            
            logger.info(f"📋 PROJECT SUMMARY CREATED: {summary['project_id']} - {summary['success_rate']:.1%} success rate")
            return summary
            
        except Exception as e:
            logger.error(f"❌ ERROR CREATING PROJECT SUMMARY: {str(e)}")
            return {
                'project_id': 'error',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_upload_stats(self) -> Dict[str, Any]:
        """
        Get upload statistics and health check
        """
        try:
            bucket_accessible = self._test_bucket_access()
            
            stats = {
                'bucket_name': self.bucket_name,
                'bucket_accessible': bucket_accessible,
                'timestamp': datetime.now().isoformat(),
                'status': 'healthy' if bucket_accessible else 'error',
                'version': '3.2.1'
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ ERROR GETTING UPLOAD STATS: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

# Global instance
enhanced_uploader = EnhancedS3DocumentUploader()

def upload_documents_to_s3_enhanced(documents: Dict[str, str], service_name: str, project_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function to upload documents with comprehensive error handling
    """
    try:
        logger.info(f"🚀 STARTING ENHANCED DOCUMENT UPLOAD FOR {service_name}")
        
        # Upload documents
        upload_results = enhanced_uploader.upload_multiple_documents(
            documents, 
            service_name, 
            project_info.get('project_id')
        )
        
        # Create project summary
        project_summary = enhanced_uploader.create_project_summary(project_info, upload_results)
        
        # Add upload stats
        upload_stats = enhanced_uploader.get_upload_stats()
        project_summary['upload_stats'] = upload_stats
        
        logger.info(f"🎉 ENHANCED UPLOAD PROCESS COMPLETED FOR {service_name}")
        return project_summary
        
    except Exception as e:
        logger.error(f"❌ CRITICAL ERROR IN ENHANCED UPLOAD PROCESS: {str(e)}")
        return {
            'status': 'critical_error',
            'error': str(e),
            'service': service_name,
            'timestamp': datetime.now().isoformat(),
            'version': '3.2.1'
        }
