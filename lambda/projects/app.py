import json
import boto3
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any
import logging
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('REGION', 'us-east-1'))
s3 = boto3.client('s3', region_name=os.environ.get('REGION', 'us-east-1'))

# Get table and bucket names from environment
PROJECTS_TABLE = os.environ.get('PROJECTS_TABLE')
DOCUMENTS_BUCKET = os.environ.get('DOCUMENTS_BUCKET')

projects_table = dynamodb.Table(PROJECTS_TABLE) if PROJECTS_TABLE else None

def lambda_handler(event, context):
    """
    AWS Lambda handler for projects functionality - AWS Propuestas v3
    """
    try:
        # Handle CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return create_response(200, {})
        
        method = event.get('httpMethod', 'GET')
        path_parameters = event.get('pathParameters') or {}
        query_parameters = event.get('queryStringParameters') or {}
        
        if method == 'GET':
            # Check if requesting specific project documents
            if query_parameters.get('action') == 'documents':
                project_name = query_parameters.get('project_name')
                if project_name:
                    return get_project_documents(project_name)
                else:
                    return create_response(400, {'error': 'project_name parameter required'})
            else:
                return get_projects(event, context)
        elif method == 'POST':
            return create_or_update_project(event, context)
        elif method == 'DELETE':
            project_id = path_parameters.get('projectId')
            if project_id:
                return delete_project(project_id)
            else:
                return create_response(400, {'error': 'projectId path parameter required'})
        else:
            return create_response(405, {'error': 'Method not allowed'})
        
    except Exception as e:
        logger.error(f"Error in projects handler: {str(e)}")
        return create_response(500, {
            'error': 'Internal server error',
            'details': str(e)
        })

def get_projects(event, context) -> Dict:
    """Get projects for a user"""
    try:
        query_params = event.get('queryStringParameters') or {}
        user_id = query_params.get('userId', 'anonymous')
        status_filter = query_params.get('status')  # 'completed', 'in_progress', 'all'
        
        if not projects_table:
            return create_response(500, {'error': 'Projects table not configured'})
        
        # Scan projects table (in production, consider using GSI for better performance)
        scan_params = {}
        if status_filter and status_filter != 'all':
            if status_filter == 'completed':
                scan_params['FilterExpression'] = 'isComplete = :completed'
                scan_params['ExpressionAttributeValues'] = {':completed': True}
            elif status_filter == 'in_progress':
                scan_params['FilterExpression'] = 'isComplete = :completed'
                scan_params['ExpressionAttributeValues'] = {':completed': False}
        
        response = projects_table.scan(**scan_params)
        projects = response.get('Items', [])
        
        # Enrich projects with S3 document information
        enriched_projects = []
        for project in projects:
            project_name = project.get('projectInfo', {}).get('name', project.get('projectId', ''))
            
            # Get document count from S3
            document_count = 0
            documents = []
            if DOCUMENTS_BUCKET and project_name:
                try:
                    documents = list_project_documents_from_s3(project_name)
                    document_count = len(documents)
                except Exception as e:
                    logger.warning(f"Could not get documents for project {project_name}: {str(e)}")
            
            enriched_project = {
                'projectId': project.get('projectId'),
                'projectName': project_name,
                'status': 'completed' if (project.get('status') == 'COMPLETED' or project.get('isComplete')) else 'in_progress',
                'currentStep': project.get('currentStep', 0),
                'createdAt': project.get('createdAt'),
                'updatedAt': project.get('updatedAt'),
                'documentCount': document_count,
                'hasDocuments': document_count > 0,
                'projectInfo': project.get('projectInfo', {}),
                'lastMessage': get_last_message(project.get('messages', []))
            }
            
            enriched_projects.append(enriched_project)
        
        # Sort by updatedAt descending
        enriched_projects.sort(key=lambda x: x.get('updatedAt', ''), reverse=True)
        
        return create_response(200, {
            'projects': enriched_projects,
            'total': len(enriched_projects),
            'completed': len([p for p in enriched_projects if p['status'] == 'completed']),
            'in_progress': len([p for p in enriched_projects if p['status'] == 'in_progress'])
        })
        
    except Exception as e:
        logger.error(f"Error getting projects: {str(e)}")
        return create_response(500, {'error': f'Failed to get projects: {str(e)}'})

def get_project_documents(project_name: str) -> Dict:
    """Get documents for a specific project"""
    try:
        if not DOCUMENTS_BUCKET:
            return create_response(500, {'error': 'Documents bucket not configured'})
        
        documents = list_project_documents_from_s3(project_name)
        
        return create_response(200, {
            'projectName': project_name,
            'documents': documents,
            'documentCount': len(documents)
        })
        
    except Exception as e:
        logger.error(f"Error getting project documents: {str(e)}")
        return create_response(500, {'error': f'Failed to get project documents: {str(e)}'})

def list_project_documents_from_s3(project_name: str) -> List[Dict[str, Any]]:
    """List documents for a project from S3"""
    try:
        # Clean project name for folder
        folder_name = project_name.lower().replace(' ', '-').replace('_', '-')
        
        response = s3.list_objects_v2(
            Bucket=DOCUMENTS_BUCKET,
            Prefix=f"{folder_name}/",
            Delimiter='/'
        )
        
        documents = []
        for obj in response.get('Contents', []):
            # Skip the folder itself
            if obj['Key'].endswith('/'):
                continue
                
            filename = obj['Key'].split('/')[-1]
            
            # Generate presigned URL for download
            download_url = generate_presigned_url(obj['Key'])
            
            documents.append({
                'filename': filename,
                's3_key': obj['Key'],
                'size': obj['Size'],
                'lastModified': obj['LastModified'].isoformat(),
                'downloadUrl': download_url,
                'fileType': get_file_type(filename)
            })
        
        return documents
        
    except ClientError as e:
        logger.error(f"S3 error listing documents for {project_name}: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Error listing documents for {project_name}: {str(e)}")
        return []

def generate_presigned_url(s3_key: str, expiration: int = 3600) -> str:
    """Generate presigned URL for document download"""
    try:
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': DOCUMENTS_BUCKET, 'Key': s3_key},
            ExpiresIn=expiration
        )
        return url
    except ClientError as e:
        logger.error(f"Failed to generate presigned URL for {s3_key}: {str(e)}")
        return ""

def get_file_type(filename: str) -> str:
    """Get file type based on extension"""
    extension = filename.lower().split('.')[-1] if '.' in filename else ''
    
    file_types = {
        'docx': 'Word Document',
        'doc': 'Word Document',
        'pdf': 'PDF Document',
        'csv': 'CSV Spreadsheet',
        'xlsx': 'Excel Spreadsheet',
        'xls': 'Excel Spreadsheet',
        'yaml': 'CloudFormation Template',
        'yml': 'CloudFormation Template',
        'json': 'JSON File',
        'txt': 'Text File',
        'svg': 'SVG Diagram',
        'png': 'PNG Image',
        'jpg': 'JPEG Image',
        'jpeg': 'JPEG Image',
        'drawio': 'Draw.io Diagram',
        'xml': 'XML File'
    }
    
    return file_types.get(extension, 'Unknown File')

def get_last_message(messages: List[Dict]) -> str:
    """Get the last message content for preview"""
    if not messages:
        return ""
    
    # Get the last assistant message
    for message in reversed(messages):
        if message.get('role') == 'assistant':
            content = message.get('content', '')
            # Return first 100 characters
            return content[:100] + '...' if len(content) > 100 else content
    
    return ""

def create_or_update_project(event, context) -> Dict:
    
    query_params = event.get('queryStringParameters') or {}
    user_id = query_params.get('userId', 'anonymous')
    status = query_params.get('status')
    limit = int(query_params.get('limit', 20))
    page = int(query_params.get('page', 1))
    
    logger.info(f"📊 Getting projects for user: {user_id}")
    
    if not projects_table:
        return create_response(500, {'error': 'Projects table not configured'})
    
    try:
        # Query projects by user
        if status:
            # Query by status if provided
            response = projects_table.query(
                IndexName='StatusIndex',
                KeyConditionExpression=Key('status').eq(status),
                FilterExpression=Key('userId').eq(user_id),
                Limit=limit,
                ScanIndexForward=False  # Most recent first
            )
        else:
            # Query all projects for user
            response = projects_table.query(
                IndexName='UserIndex',
                KeyConditionExpression=Key('userId').eq(user_id),
                Limit=limit,
                ScanIndexForward=False  # Most recent first
            )
        
        projects = response.get('Items', [])
        
        # Process projects for response
        processed_projects = []
        for project in projects:
            processed_project = {
                'projectId': project.get('projectId'),
                'userId': project.get('userId'),
                'projectInfo': project.get('projectInfo', {}),
                'status': project.get('status'),
                'messageCount': project.get('messageCount', 0),
                'createdAt': project.get('createdAt'),
                'updatedAt': project.get('updatedAt'),
                'completedAt': project.get('completedAt'),
                'modelId': project.get('modelId')
            }
            
            # Add project name from projectInfo
            if project.get('projectInfo'):
                processed_project['name'] = project['projectInfo'].get('name', 'Proyecto sin nombre')
                processed_project['type'] = project['projectInfo'].get('type', 'No especificado')
            
            processed_projects.append(processed_project)
        
        return create_response(200, {
            'projects': processed_projects,
            'total': len(processed_projects),
            'page': page,
            'limit': limit,
            'hasMore': len(projects) == limit
        })
        
    except Exception as e:
        logger.error(f"Error querying projects: {str(e)}")
        return create_response(500, {'error': 'Failed to retrieve projects'})

def create_or_update_project(event, context) -> Dict:
    """Create or update a project"""
    
    if 'body' in event:
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
    else:
        body = event
    
    project_id = body.get('projectId')
    user_id = body.get('userId', 'anonymous')
    project_info = body.get('projectInfo', {})
    status = body.get('status', 'IN_PROGRESS')
    
    if not project_id:
        return create_response(400, {'error': 'Project ID is required'})
    
    logger.info(f"💾 Creating/updating project: {project_id}")
    
    if not projects_table:
        return create_response(500, {'error': 'Projects table not configured'})
    
    try:
        # Create or update project
        timestamp = int(datetime.utcnow().timestamp())
        
        item = {
            'projectId': project_id,
            'userId': user_id,
            'projectInfo': project_info,
            'status': status,
            'updatedAt': datetime.utcnow().isoformat()
        }
        
        # Check if project exists
        try:
            existing = projects_table.get_item(Key={'projectId': project_id})
            if 'Item' in existing:
                # Update existing project
                item['createdAt'] = existing['Item'].get('createdAt', timestamp)
            else:
                # New project
                item['createdAt'] = timestamp
        except:
            # New project
            item['createdAt'] = timestamp
        
        # Add completion timestamp if completed
        if status == 'COMPLETED':
            item['completedAt'] = datetime.utcnow().isoformat()
        
        projects_table.put_item(Item=item)
        
        return create_response(200, {
            'message': 'Project saved successfully',
            'projectId': project_id,
            'status': status
        })
        
    except Exception as e:
        logger.error(f"Error saving project: {str(e)}")
        return create_response(500, {'error': 'Failed to save project'})

def create_response(status_code: int, body: Dict) -> Dict:
    """Create HTTP response with CORS headers"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
        },
        'body': json.dumps(body, ensure_ascii=False)
    }
    return file_types.get(extension, 'Unknown File')

def get_last_message(messages: List[Dict]) -> str:
    """Get the last message content for preview"""
    if not messages:
        return ""
    
    # Get the last assistant message
    for message in reversed(messages):
        if message.get('role') == 'assistant':
            content = message.get('content', '')
            # Return first 100 characters
            return content[:100] + '...' if len(content) > 100 else content
    
    return ""

def create_or_update_project(event, context) -> Dict:
    """Create or update a project"""
    try:
        body = json.loads(event.get('body', '{}'))
        
        # This endpoint is mainly for manual project creation
        # Most projects are created automatically by the arquitecto
        
        project_data = {
            'projectId': body.get('projectId', str(uuid.uuid4())),
            'projectInfo': body.get('projectInfo', {}),
            'createdAt': datetime.utcnow().isoformat(),
            'updatedAt': datetime.utcnow().isoformat(),
            'isComplete': body.get('isComplete', False),
            'currentStep': body.get('currentStep', 0),
            'messages': body.get('messages', [])
        }
        
        if projects_table:
            projects_table.put_item(Item=project_data)
        
        return create_response(200, {
            'message': 'Project created/updated successfully',
            'projectId': project_data['projectId']
        })
        
    except Exception as e:
        logger.error(f"Error creating/updating project: {str(e)}")
        return create_response(500, {'error': f'Failed to create/update project: {str(e)}'})

def delete_project(project_id: str) -> Dict:
    """Delete a project from DynamoDB and all its documents from S3"""
    try:
        logger.info(f"🗑️ DELETING PROJECT: {project_id}")
        
        if not projects_table:
            return create_response(500, {'error': 'Projects table not configured'})
        
        # First, get the project to check if it exists and get document info
        try:
            response = projects_table.get_item(Key={'projectId': project_id})
            if 'Item' not in response:
                return create_response(404, {
                    'success': False,
                    'message': 'Project not found'
                })
            
            project = response['Item']
            logger.info(f"Found project: {project.get('projectInfo', {}).get('name', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Error getting project: {str(e)}")
            return create_response(500, {
                'success': False,
                'message': f'Error retrieving project: {str(e)}'
            })
        
        # Delete documents from S3 if bucket is configured
        deleted_files = []
        if DOCUMENTS_BUCKET:
            try:
                # List all objects with the project prefix
                s3_prefix = f"projects/{project_id}/"
                logger.info(f"Deleting S3 objects with prefix: {s3_prefix}")
                
                # List objects
                response = s3.list_objects_v2(
                    Bucket=DOCUMENTS_BUCKET,
                    Prefix=s3_prefix
                )
                
                if 'Contents' in response:
                    # Delete all objects
                    objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]
                    
                    if objects_to_delete:
                        delete_response = s3.delete_objects(
                            Bucket=DOCUMENTS_BUCKET,
                            Delete={'Objects': objects_to_delete}
                        )
                        
                        deleted_files = [obj['Key'] for obj in objects_to_delete]
                        logger.info(f"Deleted {len(deleted_files)} files from S3")
                    else:
                        logger.info("No files found in S3 for this project")
                else:
                    logger.info("No S3 objects found for this project")
                    
            except Exception as e:
                logger.error(f"Error deleting S3 objects: {str(e)}")
                # Continue with DynamoDB deletion even if S3 fails
        
        # Delete project from DynamoDB
        try:
            projects_table.delete_item(Key={'projectId': project_id})
            logger.info(f"Successfully deleted project {project_id} from DynamoDB")
            
        except Exception as e:
            logger.error(f"Error deleting from DynamoDB: {str(e)}")
            return create_response(500, {
                'success': False,
                'message': f'Error deleting project from database: {str(e)}'
            })
        
        return create_response(200, {
            'success': True,
            'message': f'Project deleted successfully. Removed {len(deleted_files)} documents from S3.',
            'deletedFiles': len(deleted_files),
            'projectId': project_id
        })
        
    except Exception as e:
        logger.error(f"Error in delete_project: {str(e)}")
        return create_response(500, {
            'success': False,
            'message': f'Failed to delete project: {str(e)}'
        })

def create_response(status_code: int, body: Dict) -> Dict:
    """Create HTTP response with CORS headers"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, X-Amz-Date, Authorization, X-Api-Key, X-Amz-Security-Token'
        },
        'body': json.dumps(body, default=str)
    }
