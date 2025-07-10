"""
S3 uploader for generated documents
"""
import boto3
import os
from typing import Dict, Any, List
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

def upload_project_documents(project_name: str, documents: Dict[str, bytes], bucket_name: str) -> Dict[str, str]:
    """
    Upload all project documents to S3
    
    Args:
        project_name: Name of the project (used as folder name)
        documents: Dictionary with filename -> content mapping
        bucket_name: S3 bucket name
    
    Returns:
        Dict with upload results
    """
    s3_client = boto3.client('s3')
    
    # Clean project name for folder
    folder_name = project_name.lower().replace(' ', '-').replace('_', '-')
    
    upload_results = {
        'success': True,
        'uploaded_files': [],
        'failed_files': [],
        'folder_name': folder_name,
        'bucket_name': bucket_name
    }
    
    for filename, content in documents.items():
        try:
            # Create S3 key with project folder
            s3_key = f"{folder_name}/{filename}"
            
            # Determine content type
            content_type = get_content_type(filename)
            
            # Upload to S3
            s3_client.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=content,
                ContentType=content_type,
                ServerSideEncryption='AES256',
                Metadata={
                    'project-name': project_name,
                    'generated-by': 'aws-propuestas-v3',
                    'upload-timestamp': str(int(os.time.time()) if hasattr(os, 'time') else 0)
                }
            )
            
            upload_results['uploaded_files'].append({
                'filename': filename,
                's3_key': s3_key,
                'size': len(content) if isinstance(content, (bytes, str)) else 0
            })
            
            logger.info(f"Successfully uploaded {filename} to s3://{bucket_name}/{s3_key}")
            
        except ClientError as e:
            error_msg = f"Failed to upload {filename}: {str(e)}"
            logger.error(error_msg)
            upload_results['failed_files'].append({
                'filename': filename,
                'error': error_msg
            })
            upload_results['success'] = False
        except Exception as e:
            error_msg = f"Unexpected error uploading {filename}: {str(e)}"
            logger.error(error_msg)
            upload_results['failed_files'].append({
                'filename': filename,
                'error': error_msg
            })
            upload_results['success'] = False
    
    return upload_results

def get_content_type(filename: str) -> str:
    """Get content type based on file extension"""
    extension = filename.lower().split('.')[-1] if '.' in filename else ''
    
    content_types = {
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'doc': 'application/msword',
        'pdf': 'application/pdf',
        'csv': 'text/csv',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'xls': 'application/vnd.ms-excel',
        'yaml': 'application/x-yaml',
        'yml': 'application/x-yaml',
        'json': 'application/json',
        'txt': 'text/plain',
        'svg': 'image/svg+xml',
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'drawio': 'application/xml',
        'xml': 'application/xml'
    }
    
    return content_types.get(extension, 'application/octet-stream')

def list_project_documents(project_name: str, bucket_name: str) -> List[Dict[str, Any]]:
    """
    List all documents for a project
    
    Args:
        project_name: Name of the project
        bucket_name: S3 bucket name
    
    Returns:
        List of document information
    """
    s3_client = boto3.client('s3')
    
    # Clean project name for folder
    folder_name = project_name.lower().replace(' ', '-').replace('_', '-')
    
    try:
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=f"{folder_name}/",
            Delimiter='/'
        )
        
        documents = []
        for obj in response.get('Contents', []):
            # Skip the folder itself
            if obj['Key'].endswith('/'):
                continue
                
            filename = obj['Key'].split('/')[-1]
            documents.append({
                'filename': filename,
                's3_key': obj['Key'],
                'size': obj['Size'],
                'last_modified': obj['LastModified'].isoformat(),
                'download_url': generate_presigned_url(bucket_name, obj['Key'])
            })
        
        return documents
        
    except ClientError as e:
        logger.error(f"Failed to list documents for project {project_name}: {str(e)}")
        return []

def generate_presigned_url(bucket_name: str, s3_key: str, expiration: int = 3600) -> str:
    """
    Generate presigned URL for document download
    
    Args:
        bucket_name: S3 bucket name
        s3_key: S3 object key
        expiration: URL expiration time in seconds
    
    Returns:
        Presigned URL
    """
    s3_client = boto3.client('s3')
    
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': s3_key},
            ExpiresIn=expiration
        )
        return url
    except ClientError as e:
        logger.error(f"Failed to generate presigned URL for {s3_key}: {str(e)}")
        return ""

def list_all_projects(bucket_name: str) -> List[Dict[str, Any]]:
    """
    List all project folders in the bucket
    
    Args:
        bucket_name: S3 bucket name
    
    Returns:
        List of project information
    """
    s3_client = boto3.client('s3')
    
    try:
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Delimiter='/'
        )
        
        projects = []
        for prefix in response.get('CommonPrefixes', []):
            folder_name = prefix['Prefix'].rstrip('/')
            
            # Get project documents count
            docs_response = s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=f"{folder_name}/",
                Delimiter='/'
            )
            
            document_count = len([obj for obj in docs_response.get('Contents', []) if not obj['Key'].endswith('/')])
            
            # Get latest modification date
            latest_modified = None
            for obj in docs_response.get('Contents', []):
                if not obj['Key'].endswith('/'):
                    if latest_modified is None or obj['LastModified'] > latest_modified:
                        latest_modified = obj['LastModified']
            
            projects.append({
                'project_name': folder_name.replace('-', ' ').title(),
                'folder_name': folder_name,
                'document_count': document_count,
                'last_modified': latest_modified.isoformat() if latest_modified else None
            })
        
        return sorted(projects, key=lambda x: x['last_modified'] or '', reverse=True)
        
    except ClientError as e:
        logger.error(f"Failed to list projects: {str(e)}")
        return []

def delete_project_documents(project_name: str, bucket_name: str) -> Dict[str, Any]:
    """
    Delete all documents for a project
    
    Args:
        project_name: Name of the project
        bucket_name: S3 bucket name
    
    Returns:
        Deletion results
    """
    s3_client = boto3.client('s3')
    
    # Clean project name for folder
    folder_name = project_name.lower().replace(' ', '-').replace('_', '-')
    
    try:
        # List all objects in the project folder
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=f"{folder_name}/"
        )
        
        if 'Contents' not in response:
            return {
                'success': True,
                'message': 'No documents found to delete',
                'deleted_count': 0
            }
        
        # Delete all objects
        objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]
        
        delete_response = s3_client.delete_objects(
            Bucket=bucket_name,
            Delete={'Objects': objects_to_delete}
        )
        
        deleted_count = len(delete_response.get('Deleted', []))
        errors = delete_response.get('Errors', [])
        
        return {
            'success': len(errors) == 0,
            'deleted_count': deleted_count,
            'errors': errors,
            'message': f"Successfully deleted {deleted_count} documents" if len(errors) == 0 else f"Deleted {deleted_count} documents with {len(errors)} errors"
        }
        
    except ClientError as e:
        logger.error(f"Failed to delete project documents: {str(e)}")
        return {
            'success': False,
            'message': f"Failed to delete project documents: {str(e)}",
            'deleted_count': 0
        }
