"""
Lambda handler principal con logging detallado
"""
import json
import boto3
import logging
from datetime import datetime
import uuid
import os
from conversation_handler import ConversationState
from mcp_integration import generate_diagram, generate_cloudformation, generate_costs

# Configuración de logging detallado
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def log_request(event, body):
    """Log detallado de la petición"""
    logger.info("=== INICIO REQUEST LOGGING ===")
    logger.info(f"Headers: {json.dumps(event.get('headers', {}))}")
    logger.info(f"Body: {json.dumps(body)}")
    logger.info(f"Messages: {json.dumps(body.get('messages', []))}")
    logger.info(f"Project State: {json.dumps(body.get('projectState', {}))}")
    logger.info("=== FIN REQUEST LOGGING ===")

def get_cors_headers():
    return {
        'Access-Control-Allow-Origin': 'https://main.d2xsphsjdxlk24.amplifyapp.com',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With, Accept, Origin',
        'Access-Control-Max-Age': '86400',
        'Content-Type': 'application/json'
    }

def create_response(status_code, body):
    logger.info(f"=== RESPONSE ===")
    logger.info(f"Status: {status_code}")
    logger.info(f"Body: {json.dumps(body)}")
    logger.info("=== FIN RESPONSE ===")
    return {
        'statusCode': status_code,
        'headers': get_cors_headers(),
        'body': json.dumps(body)
    }

def lambda_handler(event, context):
    """Handler principal con logging detallado"""
    
    # Manejar preflight CORS
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': ''
        }

    try:
        # Extraer y loggear datos del request
        body = json.loads(event.get('body', '{}'))
        log_request(event, body)
        
        messages = body.get('messages', [])
        project_state = body.get('projectState', {})
        
        # Inicializar manejador de conversación
        conversation = ConversationState()
        
        # Validar estado actual
        is_complete = conversation.validate_state(messages, project_state)
        logger.info(f"Estado de conversación: {conversation.current_step}")
        logger.info(f"Campos requeridos: {json.dumps(conversation.required_fields)}")
        
        # Si no está completo, obtener siguiente pregunta
        if not is_complete:
            next_question = conversation.get_next_question()
            completion = conversation.get_completion_percentage()
            missing = conversation.get_missing_fields()
            
            return create_response(200, {
                'content': next_question,
                'projectState': project_state,
                'mcpActivated': True,
                'mcpUsed': [],
                'readinessScore': completion / 100,
                'readinessStatus': f"⚠️ Falta información: {', '.join(missing)}"
            })
        
        # Si está completo, generar documentos
        project_data = conversation.project_data
        logger.info(f"Generando documentos para: {json.dumps(project_data)}")
        
        generation_result = generate_documents(project_data)
        
        if not generation_result:
            raise Exception("Error generando documentos")
        
        success_message = f"""✅ DOCUMENTOS GENERADOS EXITOSAMENTE PARA: {project_data['name']}
🏗️ Servicios AWS: {', '.join(project_data.get('services', []))}
📁 Carpeta S3: {project_data['name']}
📄 Archivos: {len(generation_result['documents'])} documentos específicos
💾 Proyecto guardado en base de datos

🎯 Documentos incluyen:
   • Diagrama de arquitectura con iconos AWS oficiales
   • CloudFormation template para {', '.join(project_data.get('services', []))}
   • Estimación de costos específica del proyecto

📱 Puedes revisar todos los archivos en la sección 'Proyectos'."""
        
        return create_response(200, {
            'content': success_message,
            'projectState': project_state,
            'mcpActivated': True,
            'mcpUsed': generation_result['mcp_used'],
            'readinessScore': 1.0,
            'readinessStatus': "✅ Documentos generados"
        })
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.error(f"Stack trace:", exc_info=True)
        return create_response(500, {
            'content': f"Lo siento, ocurrió un error: {str(e)}",
            'projectState': project_state,
            'mcpActivated': True,
            'mcpUsed': [],
            'readinessScore': 0,
            'readinessStatus': "Error en el procesamiento"
        })
