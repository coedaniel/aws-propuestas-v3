import json
import boto3
import os
from datetime import datetime
from typing import Dict, List, Any
import logging
from boto3.dynamodb.conditions import Key

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
        
        if method == 'GET':
            return get_projects(event, context)
        elif method == 'POST':
            return create_or_update_project(event, context)
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
