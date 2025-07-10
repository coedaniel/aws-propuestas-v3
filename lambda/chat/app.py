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

# Get table names from environment
CHAT_SESSIONS_TABLE = os.environ.get('CHAT_SESSIONS_TABLE')
chat_table = dynamodb.Table(CHAT_SESSIONS_TABLE) if CHAT_SESSIONS_TABLE else None

def lambda_handler(event, context):
    """
    AWS Lambda handler for chat functionality - AWS Propuestas v3
    """
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
        messages = body.get('messages', [])
        model_id = body.get('modelId', 'amazon.nova-pro-v1:0')
        mode = body.get('mode', 'chat-libre')
        session_id = body.get('sessionId', str(uuid.uuid4()))
        user_id = body.get('userId', 'anonymous')
        
        # Validate input
        if not messages:
            return create_response(400, {'error': 'Messages are required'})
        
        logger.info(f"🚀 CHAT V3 - USING MODEL: {model_id}")
        logger.info(f"👤 User: {user_id}, Session: {session_id}")
        
        # Get system prompt based on mode
        system_prompt = get_system_prompt(mode)
        
        # Prepare the prompt for Bedrock
        prompt_body = prepare_prompt(model_id, system_prompt, messages)
        
        # Call Bedrock
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps(prompt_body),
            contentType='application/json'
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        ai_response, usage = extract_response(model_id, response_body)
        
        # Save to DynamoDB if session_id provided
        if session_id and chat_table:
            save_chat_session(session_id, user_id, messages, ai_response, model_id, mode, usage)
        
        return create_response(200, {
            'response': ai_response,
            'modelId': model_id,
            'mode': mode,
            'sessionId': session_id,
            'usage': usage,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in chat handler: {str(e)}")
        return create_response(500, {
            'error': 'Internal server error',
            'details': str(e)
        })

def get_system_prompt(mode: str) -> str:
    """Get system prompt based on mode"""
    
    if mode == 'chat-libre':
        return """Eres un asistente experto en AWS (Amazon Web Services) con amplio conocimiento en:

- Arquitecturas de soluciones en la nube
- Servicios de AWS y sus casos de uso
- Mejores prácticas de seguridad, escalabilidad y costos
- Diseño de infraestructura serverless y tradicional
- Migración a la nube y modernización de aplicaciones
- DevOps, CI/CD y automatización en AWS
- Análisis de costos y optimización
- Inteligencia Artificial y Machine Learning en AWS
- Contenedores y Kubernetes en AWS
- Bases de datos y analytics

Proporciona respuestas técnicas precisas, prácticas y profesionales. Incluye ejemplos específicos cuando sea relevante y sugiere mejores prácticas. Mantén un tono profesional pero accesible.

Si la pregunta no está relacionada con AWS o tecnología en la nube, redirige amablemente la conversación hacia temas de AWS donde puedas ser más útil.

Siempre considera:
- Principios del Well-Architected Framework
- Optimización de costos
- Seguridad y compliance
- Escalabilidad y rendimiento
- Operaciones y monitoreo"""
    
    return "Eres un asistente experto en AWS. Proporciona respuestas técnicas precisas y profesionales."

def prepare_prompt(model_id: str, system_prompt: str, messages: List[Dict]) -> Dict:
    """Prepare prompt based on model type"""
    
    if model_id.startswith('anthropic.claude'):
        # Claude format
        return {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "system": system_prompt,
            "messages": messages,
            "temperature": 0.7
        }
    elif model_id.startswith('amazon.nova'):
        # Nova format - combine system prompt with first user message
        nova_messages = []
        if messages:
            first_message = system_prompt + "\n\nUsuario: " + messages[0].get('content', '')
            nova_messages.append({
                "role": "user",
                "content": [{"text": first_message}]
            })
            
            # Add remaining messages
            for msg in messages[1:]:
                nova_messages.append({
                    "role": msg.get('role', 'user'),
                    "content": [{"text": msg.get('content', '')}]
                })
        
        return {
            "messages": nova_messages,
            "inferenceConfig": {
                "max_new_tokens": 4000,
                "temperature": 0.7
            }
        }
    else:
        # Default format
        return {
            "messages": [{"role": "system", "content": system_prompt}] + messages,
            "max_tokens": 4000,
            "temperature": 0.7
        }

def extract_response(model_id: str, response_body: Dict) -> tuple:
    """Extract AI response and usage from response body"""
    
    ai_response = ""
    usage = {}
    
    if model_id.startswith('anthropic.claude'):
        ai_response = response_body.get('content', [{}])[0].get('text', '')
        usage = {
            'inputTokens': response_body.get('usage', {}).get('input_tokens'),
            'outputTokens': response_body.get('usage', {}).get('output_tokens')
        }
    elif model_id.startswith('amazon.nova'):
        ai_response = response_body.get('output', {}).get('message', {}).get('content', [{}])[0].get('text', '')
        usage = {
            'inputTokens': response_body.get('usage', {}).get('inputTokens'),
            'outputTokens': response_body.get('usage', {}).get('outputTokens'),
            'totalTokens': response_body.get('usage', {}).get('totalTokens')
        }
    else:
        ai_response = response_body.get('content', '')
    
    return ai_response, usage

def save_chat_session(session_id: str, user_id: str, messages: List[Dict], 
                     ai_response: str, model_id: str, mode: str, usage: Dict):
    """Save chat session to DynamoDB"""
    try:
        # Add AI response to messages
        all_messages = messages + [{
            'role': 'assistant',
            'content': ai_response,
            'timestamp': datetime.utcnow().isoformat(),
            'modelId': model_id,
            'usage': usage
        }]
        
        chat_table.put_item(
            Item={
                'sessionId': session_id,
                'userId': user_id,
                'messages': all_messages,
                'modelId': model_id,
                'mode': mode,
                'lastMessage': ai_response[:200] + '...' if len(ai_response) > 200 else ai_response,
                'messageCount': len(all_messages),
                'timestamp': int(datetime.utcnow().timestamp()),
                'createdAt': datetime.utcnow().isoformat(),
                'updatedAt': datetime.utcnow().isoformat(),
                'usage': usage
            }
        )
        logger.info(f"💾 Chat session saved: {session_id}")
    except Exception as e:
        logger.warning(f"Failed to save chat session: {str(e)}")

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
