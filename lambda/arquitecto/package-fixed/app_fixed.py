import json
import boto3
import logging
from datetime import datetime
import uuid
from project_extractor import ProjectExtractor
from mcp_caller_fixed import MCPCaller
from readiness_checker import check_conversation_readiness, get_next_question
from cors_config import create_response, handle_preflight_request

# Configuración de logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Inicializar servicios AWS
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    """Handler principal de la función Lambda"""
    
    # Manejar preflight CORS
    if event.get('httpMethod') == 'OPTIONS':
        return handle_preflight_request()

    try:
        # Extraer body del request
        body = json.loads(event.get('body', '{}'))
        messages = body.get('messages', [])
        model_id = body.get('modelId', 'amazon.nova-pro-v1:0')
        project_state = body.get('projectState', {})
        
        # Extraer información del proyecto
        extractor = ProjectExtractor()
        project_data = extractor.extract_project_data(messages, project_state)
        
        # Verificar preparación para generar documentos
        readiness = check_conversation_readiness(messages, project_data)
        
        # Inicializar MCP Caller
        mcp = MCPCaller()
        
        # Si no está listo para generar documentos
        if not readiness['ready_for_generation']:
            next_question = get_next_question(readiness)
            return create_response(200, {
                'content': next_question,
                'projectState': project_data,
                'mcpActivated': True,
                'mcpUsed': [],
                'readinessScore': readiness['readiness_score'],
                'readinessStatus': readiness['status_message']
            })
        
        # Si está listo, generar documentos
        if readiness['ready_for_generation']:
            # Generar documentos usando MCPs
            generated_docs = mcp.generate_project_documents(project_data)
            
            # Guardar proyecto en DynamoDB
            projects_table = dynamodb.Table('aws-propuestas-v3-projects-prod')
            project_id = str(uuid.uuid4())
            
            project_item = {
                'id': project_id,
                'name': project_data['name'],
                'createdAt': datetime.utcnow().isoformat(),
                'services': project_data.get('services', []),
                'requirements': project_data.get('requirements', []),
                'documents': generated_docs['documents'],
                'status': 'COMPLETED'
            }
            
            projects_table.put_item(Item=project_item)
            
            # Subir documentos a S3
            bucket_name = 'aws-propuestas-v3-documents-prod-035385358261'
            for doc in generated_docs['documents']:
                s3.put_object(
                    Bucket=bucket_name,
                    Key=f"{project_data['name']}/{doc['filename']}",
                    Body=doc['content'].encode('utf-8')
                )
            
            # Preparar mensaje de éxito
            success_message = f"""✅ DOCUMENTOS GENERADOS EXITOSAMENTE PARA: {project_data['name']}
🏗️ Servicios AWS: {', '.join(project_data.get('services', []))}
📁 Carpeta S3: {project_data['name']}
📄 Archivos: {len(generated_docs['documents'])} documentos específicos
💾 Proyecto guardado en base de datos

🎯 Documentos incluyen:
   • Diagrama de arquitectura con iconos AWS oficiales
   • CloudFormation template para {', '.join(project_data.get('services', []))}
   • Estimación de costos específica del proyecto
   • Documentos técnicos personalizados

📱 Puedes revisar todos los archivos en la sección 'Proyectos'."""
            
            return create_response(200, {
                'content': success_message,
                'projectState': project_data,
                'mcpActivated': True,
                'mcpUsed': generated_docs.get('mcp_used', []),
                'readinessScore': readiness['readiness_score'],
                'readinessStatus': readiness['status_message']
            })
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return create_response(500, {
            'content': f"Lo siento, ocurrió un error: {str(e)}",
            'projectState': project_state,
            'mcpActivated': True,
            'mcpUsed': [],
            'readinessScore': 0,
            'readinessStatus': "Error en el procesamiento"
        })
