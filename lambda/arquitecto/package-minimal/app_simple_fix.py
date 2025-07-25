"""
AWS Propuestas v3 - Arquitecto Lambda SIMPLIFICADO
Versión simplificada sin MCP para estabilidad
"""

import json
import boto3
import os
import logging
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ.get('REGION', 'us-east-1'))

# Simplified Architect Prompt
ARQUITECTO_PROMPT = """Eres un Arquitecto de Soluciones AWS experto y consultor senior.

Tu trabajo es ayudar a diseñar soluciones completas en AWS siguiendo este proceso:

1. RECOPILAR INFORMACIÓN:
   - Nombre del proyecto
   - Tipo de aplicación (web, móvil, API, etc.)
   - Usuarios esperados
   - Presupuesto aproximado
   - Requisitos especiales

2. DISEÑAR ARQUITECTURA:
   - Servicios AWS recomendados
   - Diagrama de arquitectura
   - Mejores prácticas de seguridad
   - Estimación de costos

3. ENTREGAR PROPUESTA:
   - Resumen ejecutivo
   - Detalles técnicos
   - Plan de implementación

IMPORTANTE: Pregunta una cosa a la vez, mantén un tono profesional y guía paso a paso."""

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

def prepare_simple_conversation(messages: List[Dict], project_state: Dict) -> List[Dict]:
    """Prepare simple conversation for Bedrock"""
    conversation = []
    
    # Add architect prompt
    conversation.append({
        "role": "user",
        "content": [{"text": ARQUITECTO_PROMPT}]
    })
    
    # Add project context if available
    if project_state.get('data'):
        context = f"CONTEXTO: {json.dumps(project_state['data'], ensure_ascii=False, indent=2)}"
        conversation.append({
            "role": "user",
            "content": [{"text": context}]
        })
    
    # Add messages
    for msg in messages:
        if msg.get("content", "").strip():
            conversation.append({
                "role": msg.get("role", "user"),
                "content": [{"text": msg["content"]}]
            })
    
    return conversation

def call_bedrock_simple(model_id: str, conversation: List[Dict]) -> Dict:
    """Simple Bedrock call"""
    try:
        logger.info(f"Calling Bedrock with model: {model_id}")
        
        response = bedrock_runtime.converse(
            modelId=model_id,
            messages=conversation,
            inferenceConfig={
                'maxTokens': 4000,
                'temperature': 0.7,
                'topP': 0.9
            }
        )
        
        content = response['output']['message']['content'][0]['text']
        
        return {
            'content': content,
            'usage': response.get('usage', {}),
            'modelUsed': model_id
        }
        
    except Exception as e:
        logger.error(f"Bedrock error: {str(e)}", exc_info=True)
        return {'error': f'Error calling Bedrock: {str(e)}'}

def lambda_handler(event, context):
    """Simplified Lambda handler"""
    
    try:
        logger.info("Arquitecto Lambda started")
        
        # Handle CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return handle_preflight_request()
        
        # Parse body
        try:
            body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event.get('body', {})
        except json.JSONDecodeError:
            return create_error_response(400, 'Invalid JSON')
        
        messages = body.get('messages', [])
        model_id = body.get('modelId', 'anthropic.claude-3-5-sonnet-20240620-v1:0')
        project_state = body.get('projectState', {'phase': 'inicio', 'data': {}})
        
        if not messages:
            return create_error_response(400, 'No messages provided')
        
        logger.info(f"Processing {len(messages)} messages with {model_id}")
        
        # Prepare conversation
        conversation = prepare_simple_conversation(messages, project_state)
        
        # Call Bedrock
        result = call_bedrock_simple(model_id, conversation)
        
        if 'error' in result:
            return create_error_response(500, result['error'])
        
        # Success response
        response_data = {
            'content': result['content'],
            'projectState': project_state,
            'mcpActivated': False,
            'mcpStatus': 'simplified_version',
            'modelUsed': result.get('modelUsed', model_id),
            'usage': result.get('usage', {}),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info("Success response ready")
        return create_success_response(response_data)
        
    except Exception as e:
        logger.error(f"Lambda error: {str(e)}", exc_info=True)
        return create_error_response(500, f'Internal error: {str(e)}')
