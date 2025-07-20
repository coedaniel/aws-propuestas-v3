import json
import boto3
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any
import logging

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

def lambda_handler(event, context):
    """AWS Lambda handler for arquitecto functionality"""
    try:
        # Handle CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return create_response(200, {})
        
        # Parse the request
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event
        
        # Extract parameters
        action = body.get('action', 'chat')
        project_id = body.get('projectId', str(uuid.uuid4()))
        user_id = body.get('userId', 'anonymous')
        
        logger.info(f"ARQUITECTO V3 - Action: {action}, Project: {project_id}")
        
        if action == 'chat':
            return process_arquitecto_chat(body, context)
        else:
            return create_response(400, {'error': 'Invalid action'})
        
    except Exception as e:
        logger.error(f"Error in arquitecto handler: {str(e)}")
        return create_response(500, {
            'error': 'Internal server error',
            'details': str(e)
        })

def process_arquitecto_chat(body: Dict, context) -> Dict:
    """Process chat with arquitecto mode"""
    
    try:
        messages = body.get('messages', [])
        model_id = body.get('modelId', 'anthropic.claude-3-haiku-20240307-v1:0')
        project_id = body.get('projectId', str(uuid.uuid4()))
        user_id = body.get('userId', 'anonymous')
        
        logger.info(f"Processing chat - Messages: {len(messages)}")
        
        if not messages:
            return create_response(400, {'error': 'Messages are required'})
        
        # System prompt for arquitecto mode
        system_prompt = get_arquitecto_system_prompt()
        
        # Prepare the prompt for Bedrock
        prompt_data = prepare_prompt(model_id, system_prompt, messages, {}, 0)
        
        # Call Bedrock
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps(prompt_data)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        
        if 'anthropic' in model_id:
            ai_response = response_body['content'][0]['text']
        else:
            ai_response = response_body.get('generation', response_body.get('outputText', ''))
        
        logger.info(f"AI Response length: {len(ai_response)}")
        
        # Create response
        response_data = {
            'response': ai_response,
            'projectId': project_id,
            'userId': user_id,
            'timestamp': datetime.now().isoformat(),
            'model': model_id
        }
        
        return create_response(200, response_data)
        
    except Exception as e:
        logger.error(f"Error in process_arquitecto_chat: {str(e)}")
        return create_response(500, {
            'error': 'Error processing chat',
            'details': str(e)
        })

def get_arquitecto_system_prompt() -> str:
    """Get system prompt for arquitecto mode"""
    bucket_name = DOCUMENTS_BUCKET or 'aws-propuestas-v3-documents-prod'
    
    return f"""Actua como arquitecto de soluciones AWS Senior con 10+ años de experiencia.

FLUJO MAESTRO:

1. PRIMERA PREGUNTA OBLIGATORIA:
¿Cual es el nombre del proyecto?

2. SEGUNDA PREGUNTA:
¿El proyecto es una solucion integral o un servicio rapido especifico?

Si elige "servicio rapido especifico":
- Muestra catalogo de servicios comunes (EC2, S3, RDS, VPC, etc.)
- Haz SOLO preguntas minimas necesarias
- ESPERA respuestas antes de continuar
- SOLO cuando tengas respuestas suficientes, genera documentos

Si elige "solucion integral":
- Entrevista guiada completa
- Una pregunta a la vez
- Aplica logica condicional segun tipo
- SOLO cuando tengas informacion completa, genera entregables

REGLAS CRITICAS:
- Pregunta una cosa a la vez
- Si respuesta es vaga, pide mas detalle
- NO generes documentos prematuramente
- SIN acentos ni caracteres especiales NUNCA
- Usa bucket del sistema: {bucket_name}
- Conversacion natural como arquitecto AWS real

Recuerda: Eres profesional, tecnico y enfocado en resultados ejecutivos."""

def prepare_prompt(model_id: str, system_prompt: str, messages: List[Dict], 
                  project_info: Dict, current_step: int) -> Dict:
    """Prepare prompt based on model type"""
    
    if 'anthropic' in model_id:
        return {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "temperature": 0.3,
            "system": system_prompt,
            "messages": messages
        }
    else:
        # For other models
        conversation = f"System: {system_prompt}\n\n"
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            conversation += f"{role.title()}: {content}\n"
        conversation += "Assistant:"
        
        return {
            "inputText": conversation,
            "textGenerationConfig": {
                "maxTokenCount": 4000,
                "temperature": 0.3,
                "topP": 0.9
            }
        }

def create_response(status_code: int, body: Dict) -> Dict:
    """Create HTTP response with CORS headers"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With'
        },
        'body': json.dumps(body, ensure_ascii=False)
    }
