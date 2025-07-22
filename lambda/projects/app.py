"""
AWS Propuestas v3 - Projects API Lambda
Conecta con DynamoDB para obtener proyectos reales generados por el arquitecto
"""

import json
import boto3
import os
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('REGION', 'us-east-1'))
s3_client = boto3.client('s3', region_name='us-east-1')

# Variables de entorno
PROJECTS_TABLE = os.environ.get('PROJECTS_TABLE', 'aws-propuestas-v3-projects-prod')
DOCUMENTS_BUCKET = os.environ.get('DOCUMENTS_BUCKET', 'aws-propuestas-v3-documents-prod-035385358261')

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
        'body': body if isinstance(body, str) else json.dumps(body, default=decimal_default)
    }

def decimal_default(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def create_error_response(status_code, error_message):
    """Create an error response with CORS headers"""
    return create_response(status_code, {
        'error': error_message,
        'timestamp': datetime.now().isoformat()
    })

def create_success_response(data):
    """Create a success response with CORS headers"""
    return create_response(200, data)

def get_all_projects():
    """Obtiene todos los proyectos de DynamoDB"""
    try:
        table = dynamodb.Table(PROJECTS_TABLE)
        
        logger.info(f"Scanning projects table: {PROJECTS_TABLE}")
        response = table.scan()
        
        projects = response.get('Items', [])
        logger.info(f"Found {len(projects)} projects in DynamoDB")
        
        # Procesar proyectos para el frontend
        processed_projects = []
        for project in projects:
            processed_project = {
                'projectId': project.get('projectId', ''),
                'projectName': project.get('projectName', 'Proyecto Sin Nombre'),
                'projectType': project.get('projectType', 'Solucion AWS'),
                'status': project.get('status', 'completed'),
                'createdAt': project.get('createdAt', ''),
                'updatedAt': project.get('updatedAt', ''),
                'description': project.get('description', ''),
                's3Folder': project.get('s3Folder', ''),
                's3Bucket': project.get('s3Bucket', DOCUMENTS_BUCKET),
                'documentsGenerated': project.get('documentsGenerated', []),
                'totalDocuments': project.get('totalDocuments', 0),
                'estimatedCost': float(project.get('estimatedCost', 0)) if project.get('estimatedCost') else None
            }
            processed_projects.append(processed_project)
        
        # Ordenar por fecha de creación (más recientes primero)
        processed_projects.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
        
        return processed_projects
        
    except Exception as e:
        logger.error(f"Error getting projects from DynamoDB: {str(e)}")
        return []

def get_project_statistics(projects: List[Dict]) -> Dict:
    """Calcula estadísticas de los proyectos"""
    total_projects = len(projects)
    completed_projects = len([p for p in projects if p.get('status') == 'completed'])
    in_progress_projects = len([p for p in projects if p.get('status') == 'in_progress'])
    total_documents = sum(p.get('totalDocuments', 0) for p in projects)
    
    return {
        'totalProjects': total_projects,
        'completedProjects': completed_projects,
        'inProgressProjects': in_progress_projects,
        'totalDocuments': total_documents
    }

def get_s3_document_urls(s3_folder: str, documents: List[Dict]) -> List[Dict]:
    """Genera URLs pre-firmadas para documentos en S3"""
    try:
        document_urls = []
        
        for doc in documents:
            s3_key = f"{s3_folder}/{doc.get('file_name', '')}"
            
            try:
                # Generar URL pre-firmada válida por 1 hora
                presigned_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': DOCUMENTS_BUCKET, 'Key': s3_key},
                    ExpiresIn=3600
                )
                
                document_urls.append({
                    'fileName': doc.get('file_name', ''),
                    'contentType': doc.get('content_type', ''),
                    's3Key': s3_key,
                    'downloadUrl': presigned_url
                })
                
            except Exception as e:
                logger.error(f"Error generating presigned URL for {s3_key}: {str(e)}")
                document_urls.append({
                    'fileName': doc.get('file_name', ''),
                    'contentType': doc.get('content_type', ''),
                    's3Key': s3_key,
                    'downloadUrl': None,
                    'error': 'URL generation failed'
                })
        
        return document_urls
        
    except Exception as e:
        logger.error(f"Error processing S3 documents: {str(e)}")
        return []

def get_project_details(project_id: str):
    """Obtiene detalles completos de un proyecto específico"""
    try:
        table = dynamodb.Table(PROJECTS_TABLE)
        
        response = table.get_item(Key={'projectId': project_id})
        
        if 'Item' not in response:
            return None
        
        project = response['Item']
        
        # Procesar proyecto con URLs de documentos
        processed_project = {
            'projectId': project.get('projectId', ''),
            'projectName': project.get('projectName', 'Proyecto Sin Nombre'),
            'projectType': project.get('projectType', 'Solucion AWS'),
            'status': project.get('status', 'completed'),
            'createdAt': project.get('createdAt', ''),
            'updatedAt': project.get('updatedAt', ''),
            'description': project.get('description', ''),
            's3Folder': project.get('s3Folder', ''),
            's3Bucket': project.get('s3Bucket', DOCUMENTS_BUCKET),
            'documentsGenerated': project.get('documentsGenerated', []),
            'totalDocuments': project.get('totalDocuments', 0),
            'estimatedCost': float(project.get('estimatedCost', 0)) if project.get('estimatedCost') else None
        }
        
        # Agregar URLs de descarga si hay documentos
        if project.get('s3Folder') and project.get('documentsGenerated'):
            processed_project['documentUrls'] = get_s3_document_urls(
                project.get('s3Folder'), 
                project.get('documentsGenerated', [])
            )
        
        return processed_project
        
    except Exception as e:
        logger.error(f"Error getting project details: {str(e)}")
        return None

def lambda_handler(event, context):
    """Main Lambda handler para Projects API"""
    
    try:
        logger.info(f"Event received: {json.dumps(event, default=str)}")
        
        # Handle CORS preflight requests
        if event.get('httpMethod') == 'OPTIONS':
            logger.info("Handling OPTIONS preflight request")
            return handle_preflight_request()
        
        http_method = event.get('httpMethod', 'GET')
        path_parameters = event.get('pathParameters') or {}
        query_parameters = event.get('queryStringParameters') or {}
        
        # GET /projects - Obtener todos los proyectos
        if http_method == 'GET' and not path_parameters.get('projectId'):
            logger.info("Getting all projects")
            
            projects = get_all_projects()
            statistics = get_project_statistics(projects)
            
            response_data = {
                'projects': projects,
                'statistics': statistics,
                'total': len(projects),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Returning {len(projects)} projects with statistics")
            return create_success_response(response_data)
        
        # GET /projects/{projectId} - Obtener proyecto específico
        elif http_method == 'GET' and path_parameters.get('projectId'):
            project_id = path_parameters['projectId']
            logger.info(f"Getting project details for: {project_id}")
            
            project = get_project_details(project_id)
            
            if not project:
                return create_error_response(404, f'Project not found: {project_id}')
            
            logger.info(f"Returning project details for: {project_id}")
            return create_success_response(project)
        
        # DELETE /projects/{projectId} - Eliminar proyecto
        elif http_method == 'DELETE' and path_parameters.get('projectId'):
            project_id = path_parameters['projectId']
            logger.info(f"Deleting project: {project_id}")
            
            # TODO: Implementar eliminación de proyecto y archivos S3
            return create_error_response(501, 'Delete functionality not implemented yet')
        
        else:
            return create_error_response(400, f'Unsupported method or path: {http_method}')
        
    except Exception as e:
        logger.error(f"Unexpected error in lambda_handler: {str(e)}", exc_info=True)
        return create_error_response(500, f'Internal server error: {str(e)}')
