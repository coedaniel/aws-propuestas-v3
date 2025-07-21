"""
AWS Propuestas v3 - Arquitecto Lambda FINAL
Funcionalidad completa con modelo Bedrock correcto
"""

import json
import boto3
import os
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ.get('REGION', 'us-east-1'))
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('REGION', 'us-east-1'))
s3 = boto3.client('s3', region_name=os.environ.get('REGION', 'us-east-1'))

# Get table and bucket names from environment
PROJECTS_TABLE = os.environ.get('PROJECTS_TABLE')
DOCUMENTS_BUCKET = os.environ.get('DOCUMENTS_BUCKET')

projects_table = dynamodb.Table(PROJECTS_TABLE) if PROJECTS_TABLE else None

# Arquitecto Master Prompt
ARQUITECTO_MASTER_PROMPT = """Actua como arquitecto de soluciones AWS y consultor experto.

IMPORTANTE: Tu objetivo es dimensionar, documentar y entregar una solucion profesional en AWS, siguiendo mejores practicas y generando todos los archivos necesarios para una propuesta ejecutiva.

REGLAS FUNDAMENTALES:
- No uses acentos ni caracteres especiales en ningun texto, archivo, script ni documento
- Todos los archivos Word seran funcionales y compatibles: solo texto plano, sin imagenes, sin tablas complejas, ni formato avanzado
- Solo genera scripts CloudFormation como entregable de automatizacion

PROCESO GUIADO INTELIGENTE:

1. INICIO: Pregunta "Cual es el nombre del proyecto?"

2. TIPO: Pregunta si el proyecto es:
   - Solucion integral (migracion, aplicacion nueva, modernizacion, analitica, seguridad, IA, IoT, data lake, networking, DRP, VDI, integracion, etc.)
   - Servicio rapido especifico (EC2, RDS, SES, VPN, ELB, S3, VPC, CloudFront, SSO, backup, etc.)

3. REQUERIMIENTOS: Segun el tipo, haz preguntas especificas para entender:
   - Alcance y objetivos
   - Usuarios y volumenes
   - Integraciones necesarias
   - Requisitos de seguridad y compliance
   - Presupuesto aproximado
   - Timeline

4. ARQUITECTURA: Diseña la solucion completa con:
   - Diagrama de arquitectura (descripcion detallada)
   - Servicios AWS recomendados
   - Configuraciones especificas
   - Mejores practicas de seguridad

5. DOCUMENTACION: Genera automaticamente:
   - Propuesta ejecutiva (Word)
   - Documento tecnico detallado (Word)
   - Script CloudFormation funcional
   - Estimacion de costos

IMPORTANTE: Siempre pregunta una cosa a la vez y espera la respuesta antes de continuar."""

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
        'body': body if isinstance(body, str) else json.dumps(body)
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

def prepare_conversation(messages: List[Dict], project_state: Dict) -> List[Dict]:
    """Prepare conversation for Bedrock with correct format"""
    conversation = []
    
    # Add system message with correct format
    conversation.append({
        "role": "user",
        "content": [{"text": ARQUITECTO_MASTER_PROMPT}]
    })
    
    # Add project state context if available
    if project_state.get('data'):
        context = f"CONTEXTO DEL PROYECTO: {json.dumps(project_state['data'], indent=2)}"
        conversation.append({
            "role": "user", 
            "content": [{"text": context}]
        })
    
    # Add conversation history with correct format
    for msg in messages:
        content = msg.get("content", "")
        conversation.append({
            "role": msg.get("role", "user"),
            "content": [{"text": content}]
        })
    
    return conversation

def call_bedrock_model(model_id: str, conversation: List[Dict]) -> Dict:
    """Call Bedrock model with correct format"""
    try:
        response = bedrock_runtime.converse(
            modelId=model_id,
            messages=conversation,
            inferenceConfig={
                'maxTokens': 4000,
                'temperature': 0.7,
                'topP': 0.9
            }
        )
        
        return {
            'content': response['output']['message']['content'][0]['text']
        }
        
    except Exception as e:
        logger.error(f"Error calling Bedrock: {str(e)}")
        return {'error': f'Error calling Bedrock: {str(e)}'}

def lambda_handler(event, context):
    """Main Lambda handler with CORS support and correct Bedrock model"""
    
    try:
        logger.info(f"Event received: {json.dumps(event)}")
        
        # Handle CORS preflight requests
        if event.get('httpMethod') == 'OPTIONS':
            logger.info("Handling OPTIONS preflight request")
            return handle_preflight_request()
        
        # Parse request
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        messages = body.get('messages', [])
        # Use Claude 3 Haiku as fallback (more reliable)
        model_id = body.get('modelId', 'anthropic.claude-3-haiku-20240307-v1:0')
        project_state = body.get('projectState', {'phase': 'inicio', 'data': {}})
        
        if not messages:
            logger.error("No messages provided")
            return create_error_response(400, 'No messages provided')
        
        logger.info(f"Processing {len(messages)} messages for project in phase: {project_state.get('phase')}")
        
        # Prepare conversation for Bedrock
        conversation = prepare_conversation(messages, project_state)
        
        # Call Bedrock model
        bedrock_response = call_bedrock_model(model_id, conversation)
        
        if 'error' in bedrock_response:
            return create_error_response(500, bedrock_response['error'])
        
        response_content = bedrock_response['content']
        
        # Response data (MCP disabled for now)
        response_data = {
            'content': response_content,
            'projectState': project_state,
            'mcpActivated': False,
            'mcpStatus': 'disabled_temporarily',
            'modelUsed': model_id,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info("Returning successful response")
        return create_success_response(response_data)
        
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}", exc_info=True)
        return create_error_response(500, f'Internal server error: {str(e)}')
