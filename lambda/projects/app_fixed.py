"""
AWS Propuestas v3 - Projects Lambda COMPLETAMENTE CORREGIDO
Conecta con DynamoDB real y S3 para gestionar proyectos
"""

import json
import boto3
import os
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Any
from boto3.dynamodb.conditions import Key, Attr

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Variables de entorno
DOCUMENTS_BUCKET = os.environ.get('DOCUMENTS_BUCKET', 'aws-propuestas-v3-documents-prod-035385358261')
PROJECTS_TABLE = os.environ.get('PROJECTS_TABLE', 'aws-propuestas-v3-projects-prod')

def get_cors_headers():
    """Get standard CORS headers for all responses"""
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With, Accept, Origin',
        'Access-Control-Max-Age': '86400',
        'Content-Type': 'application/json'
    }

def handle_preflight_request():
    """Handle OPTIONS preflight requests"""
    return {
        'statusCode': 200,
        'headers': get_cors_headers(),
        'body': ''
    }

def create_response(status_code, body, additional_headers=None):
    """Create a properly formatted response with CORS headers"""
    headers = get_cors_headers()
    
    if additional_headers:
        headers.update(additional_headers)
    
    return {
        'statusCode': status_code,
        'headers': headers,
        'body': body if isinstance(body, str) else json.dumps(body, default=str)
    }

def create_error_response(status_code, error_message):
    """Create an error response with CORS headers"""
    return create_response(status_code, {
        'error': error_message,
        'timestamp': datetime.now().isoformat()
    })

def create_success_response(data):
    """Create a success response with CORS headers"""
    return create_response(200, data)

def decimal_to_float(obj):
    """Convert Decimal objects to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [decimal_to_float(v) for v in obj]
    return obj

def get_all_projects() -> List[Dict]:
    """Obtiene todos los proyectos de DynamoDB"""
    try:
        table = dynamodb.Table(PROJECTS_TABLE)
        
        response = table.scan()
        projects = response.get('Items', [])
        
        # Handle pagination
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            projects.extend(response.get('Items', []))
        
        # Convert Decimal to float for JSON serialization
        projects = decimal_to_float(projects)
        
        logger.info(f"Retrieved {len(projects)} projects from DynamoDB")
        return projects
        
    except Exception as e:
        logger.error(f"Error getting projects from DynamoDB: {str(e)}")
        return []

def get_project_by_id(project_id: str) -> Dict:
    """Obtiene un proyecto especifico por ID"""
    try:
        table = dynamodb.Table(PROJECTS_TABLE)
        
        response = table.get_item(Key={'id': project_id})
        
        if 'Item' in response:
            project = decimal_to_float(response['Item'])
            logger.info(f"Retrieved project {project_id}")
            return project
        else:
            logger.warning(f"Project {project_id} not found")
            return {}
            
    except Exception as e:
        logger.error(f"Error getting project {project_id}: {str(e)}")
        return {}

def delete_project(project_id: str) -> Dict:
    """Elimina un proyecto y sus archivos"""
    try:
        # Primero obtener el proyecto para conocer sus archivos
        project = get_project_by_id(project_id)
        
        if not project:
            return {"success": False, "error": "Project not found"}
        
        # Eliminar archivos de S3 si existen
        s3_folder = project.get('s3Folder', '')
        if s3_folder:
            try:
                # Listar objetos en la carpeta
                response = s3_client.list_objects_v2(
                    Bucket=DOCUMENTS_BUCKET,
                    Prefix=f"{s3_folder}/"
                )
                
                # Eliminar cada objeto
                if 'Contents' in response:
                    for obj in response['Contents']:
                        s3_client.delete_object(
                            Bucket=DOCUMENTS_BUCKET,
                            Key=obj['Key']
                        )
                        logger.info(f"Deleted S3 object: {obj['Key']}")
                
            except Exception as e:
                logger.error(f"Error deleting S3 files: {str(e)}")
        
        # Eliminar proyecto de DynamoDB
        table = dynamodb.Table(PROJECTS_TABLE)
        table.delete_item(Key={'id': project_id})
        
        logger.info(f"Deleted project {project_id}")
        return {"success": True, "message": "Project deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting project {project_id}: {str(e)}")
        return {"success": False, "error": str(e)}

def generate_presigned_url(s3_key: str, expiration: int = 3600) -> str:
    """Genera una URL firmada para descargar un archivo de S3"""
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': DOCUMENTS_BUCKET, 'Key': s3_key},
            ExpiresIn=expiration
        )
        return url
    except Exception as e:
        logger.error(f"Error generating presigned URL for {s3_key}: {str(e)}")
        return ""

def get_project_files(project_id: str) -> Dict:
    """Obtiene las URLs de descarga para los archivos de un proyecto"""
    try:
        project = get_project_by_id(project_id)
        
        if not project:
            return {"error": "Project not found"}
        
        s3_folder = project.get('s3Folder', '')
        if not s3_folder:
            return {"error": "No S3 folder found for project"}
        
        # Generar URLs firmadas para cada tipo de archivo
        file_urls = {}
        file_types = {
            'word': 'documents.docx',
            'csv': 'pricing.csv',
            'yaml': 'cloudformation.yaml',
            'png': 'diagram.png',
            'svg': 'diagram.svg'
        }
        
        for file_type, filename in file_types.items():
            if project.get('files', {}).get(file_type, False):
                s3_key = f"{s3_folder}/{filename}"
                presigned_url = generate_presigned_url(s3_key)
                if presigned_url:
                    file_urls[file_type] = {
                        'url': presigned_url,
                        'filename': filename,
                        's3_key': s3_key
                    }
        
        return {
            "success": True,
            "project_id": project_id,
            "s3_folder": s3_folder,
            "files": file_urls
        }
        
    except Exception as e:
        logger.error(f"Error getting project files for {project_id}: {str(e)}")
        return {"error": str(e)}

def update_project_status(project_id: str, status: str) -> Dict:
    """Actualiza el estado de un proyecto"""
    try:
        table = dynamodb.Table(PROJECTS_TABLE)
        
        response = table.update_item(
            Key={'id': project_id},
            UpdateExpression='SET #status = :status, updatedAt = :updated',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': status,
                ':updated': datetime.now().isoformat()
            },
            ReturnValues='ALL_NEW'
        )
        
        updated_project = decimal_to_float(response.get('Attributes', {}))
        
        logger.info(f"Updated project {project_id} status to {status}")
        return {"success": True, "project": updated_project}
        
    except Exception as e:
        logger.error(f"Error updating project {project_id}: {str(e)}")
        return {"success": False, "error": str(e)}

def get_project_statistics() -> Dict:
    """Obtiene estadisticas de los proyectos"""
    try:
        projects = get_all_projects()
        
        stats = {
            "total_projects": len(projects),
            "completed_projects": len([p for p in projects if p.get('status') == 'completado']),
            "in_progress_projects": len([p for p in projects if p.get('status') == 'en-progreso']),
            "error_projects": len([p for p in projects if p.get('status') == 'error']),
            "total_files": sum(len([f for f in p.get('files', {}).values() if f]) for p in projects),
            "by_type": {
                "servicio_rapido": len([p for p in projects if p.get('type') == 'servicio-rapido']),
                "solucion_integral": len([p for p in projects if p.get('type') == 'solucion-integral'])
            }
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting project statistics: {str(e)}")
        return {}

def lambda_handler(event, context):
    """Main Lambda handler para Projects"""
    
    try:
        logger.info(f"Event received: {json.dumps(event)}")
        
        # Handle CORS preflight requests
        if event.get('httpMethod') == 'OPTIONS':
            logger.info("Handling OPTIONS preflight request")
            return handle_preflight_request()
        
        # Get HTTP method and path
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        path_parameters = event.get('pathParameters') or {}
        query_parameters = event.get('queryStringParameters') or {}
        
        # Parse request body if present
        body = {}
        if event.get('body'):
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            else:
                body = event['body']
        
        logger.info(f"Processing {http_method} request to {path}")
        
        # Route requests
        if http_method == 'GET':
            if path == '/projects' or path == '/projects/':
                # Get all projects
                projects = get_all_projects()
                stats = get_project_statistics()
                
                return create_success_response({
                    "projects": projects,
                    "statistics": stats,
                    "total": len(projects)
                })
                
            elif path.startswith('/projects/') and '/files' in path:
                # Get project files - /projects/{id}/files
                project_id = path.split('/')[2]
                files_info = get_project_files(project_id)
                return create_success_response(files_info)
                
            elif path.startswith('/projects/'):
                # Get specific project - /projects/{id}
                project_id = path.split('/')[2]
                project = get_project_by_id(project_id)
                
                if project:
                    return create_success_response({"project": project})
                else:
                    return create_error_response(404, "Project not found")
        
        elif http_method == 'PUT':
            if path.startswith('/projects/') and '/status' in path:
                # Update project status - /projects/{id}/status
                project_id = path.split('/')[2]
                new_status = body.get('status', 'en-progreso')
                
                result = update_project_status(project_id, new_status)
                
                if result.get('success'):
                    return create_success_response(result)
                else:
                    return create_error_response(400, result.get('error', 'Update failed'))
        
        elif http_method == 'DELETE':
            if path.startswith('/projects/'):
                # Delete project - /projects/{id}
                project_id = path.split('/')[2]
                
                result = delete_project(project_id)
                
                if result.get('success'):
                    return create_success_response(result)
                else:
                    return create_error_response(400, result.get('error', 'Delete failed'))
        
        # Default response for unhandled routes
        return create_error_response(404, f"Route not found: {http_method} {path}")
        
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}", exc_info=True)
        return create_error_response(500, f'Internal server error: {str(e)}')
