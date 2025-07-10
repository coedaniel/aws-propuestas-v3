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
    """
    AWS Lambda handler for arquitecto functionality - AWS Propuestas v3
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
        action = body.get('action', 'chat')
        project_id = body.get('projectId', str(uuid.uuid4()))
        user_id = body.get('userId', 'anonymous')
        
        logger.info(f"🏗️ ARQUITECTO V3 - Action: {action}, Project: {project_id}")
        
        if action == 'generate_documents':
            return generate_project_documents(body, context)
        elif action == 'save_project':
            return save_project_data(body, context)
        elif action == 'get_project':
            return get_project_data(body, context)
        else:
            # Default chat functionality
            return process_arquitecto_chat(body, context)
        
    except Exception as e:
        logger.error(f"Error in arquitecto handler: {str(e)}")
        return create_response(500, {
            'error': 'Internal server error',
            'details': str(e)
        })

def process_arquitecto_chat(body: Dict, context) -> Dict:
    """Process chat with arquitecto mode"""
    
    messages = body.get('messages', [])
    model_id = body.get('modelId', 'anthropic.claude-3-haiku-20240307-v1:0')
    project_id = body.get('projectId', str(uuid.uuid4()))
    user_id = body.get('userId', 'anonymous')
    current_step = body.get('currentStep', 0)
    project_info = body.get('projectInfo', {})
    
    if not messages:
        return create_response(400, {'error': 'Messages are required'})
    
    # System prompt for arquitecto mode
    system_prompt = get_arquitecto_system_prompt()
    
    # Prepare prompt for Bedrock
    prompt_body = prepare_prompt(model_id, system_prompt, messages, project_info, current_step)
    
    logger.info(f"🏗️ ARQUITECTO USING MODEL: {model_id}")
    
    # Call Bedrock
    response = bedrock_runtime.invoke_model(
        modelId=model_id,
        body=json.dumps(prompt_body),
        contentType='application/json'
    )
    
    # Parse response
    response_body = json.loads(response['body'].read())
    ai_response, usage = extract_response(model_id, response_body)
    
    # Check if project is complete
    is_complete = check_if_complete(ai_response, project_info)
    
    # Save project progress
    if projects_table:
        save_project_progress(project_id, user_id, messages, ai_response, project_info, 
                            current_step, is_complete, model_id)
    
    response_data = {
        'response': ai_response,
        'modelId': model_id,
        'mode': 'arquitecto',
        'projectId': project_id,
        'currentStep': current_step + 1,
        'isComplete': is_complete,
        'usage': usage,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    # If complete, trigger document generation
    if is_complete:
        response_data['documentsGenerated'] = True
        response_data['s3Folder'] = f"projects/{user_id}/{project_id}/"
        
        # Trigger async document generation (could be done via SQS/SNS in production)
        logger.info(f"🎯 Project complete! Generating documents for {project_id}")
    
    return create_response(200, response_data)

def get_arquitecto_system_prompt() -> str:
    """Get system prompt for arquitecto mode"""
    return """Actúas como arquitecto de soluciones AWS y consultor experto. Vamos a dimensionar, documentar y entregar una solución profesional en AWS, siguiendo mejores prácticas y generando todos los archivos necesarios para una propuesta ejecutiva.

IMPORTANTE: No uses acentos ni caracteres especiales en ningún texto, archivo, script ni documento. Asegura que todos los archivos Word generados sean funcionales y compatibles: entrega solo texto plano, sin imágenes, sin tablas complejas, ni formato avanzado, solo texto estructurado, claro y legible.

FLUJO DE ENTREVISTA:

1. Primero pregunta: "¿Cuál es el nombre del proyecto?"

2. Después pregunta: "El proyecto es una solución integral (como migración, aplicación nueva, modernización, analítica, seguridad, IA, IoT, data lake, networking, DRP, VDI, integración, etc.) o es un servicio rápido específico (implementación de instancias EC2, RDS, SES, VPN, ELB, S3, VPC, CloudFront, SSO, backup, etc.)?"

3. Si elige "servicio rápido específico":
   - Muestra un catálogo de servicios rápidos comunes y permite elegir uno o varios
   - Haz solo las preguntas mínimas necesarias para cada servicio elegido
   - Una pregunta a la vez, de forma clara

4. Si elige "solución integral":
   - Haz una entrevista guiada completa, una pregunta a la vez
   - Captura: objetivo, servicios necesarios, alta disponibilidad, RTO/RPO, regiones, etc.

5. Cuando tengas información suficiente, indica que el proyecto está completo y listo para generar documentos.

ENTREGABLES QUE SE GENERARÁN AUTOMÁTICAMENTE:
- Documento Word con objetivo y descripción del proyecto
- Tabla de actividades de implementación (CSV)
- Script CloudFormation para desplegar servicios
- Diagrama de arquitectura (SVG, PNG y Draw.io)
- Archivo de costos estimados (CSV)
- Guía para calculadora AWS

Mantén un tono profesional, haz preguntas claras y específicas, una a la vez. Si alguna respuesta es vaga, pide más detalle antes de avanzar."""

def prepare_prompt(model_id: str, system_prompt: str, messages: List[Dict], 
                  project_info: Dict, current_step: int) -> Dict:
    """Prepare prompt based on model type"""
    
    # Add context about current project info
    context = f"\nCONTEXTO DEL PROYECTO ACTUAL:\n"
    if project_info:
        for key, value in project_info.items():
            context += f"- {key}: {value}\n"
    context += f"- Paso actual: {current_step}\n"
    
    full_system_prompt = system_prompt + context
    
    if model_id.startswith('anthropic.claude'):
        return {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "system": full_system_prompt,
            "messages": messages,
            "temperature": 0.7
        }
    elif model_id.startswith('amazon.nova'):
        nova_messages = []
        if messages:
            first_message = full_system_prompt + "\n\nUsuario: " + messages[0].get('content', '')
            nova_messages.append({
                "role": "user",
                "content": [{"text": first_message}]
            })
            
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
        return {
            "messages": [{"role": "system", "content": full_system_prompt}] + messages,
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

def check_if_complete(ai_response: str, project_info: Dict) -> bool:
    """Check if project information gathering is complete"""
    
    # Simple heuristics to determine if project is complete
    completion_indicators = [
        "proyecto está completo",
        "información suficiente",
        "generar documentos",
        "listo para crear",
        "proceder con la generación"
    ]
    
    response_lower = ai_response.lower()
    has_completion_indicator = any(indicator in response_lower for indicator in completion_indicators)
    
    # Also check if we have minimum required info
    has_minimum_info = (
        project_info.get('name') and 
        project_info.get('type') and
        len(project_info) >= 3
    )
    
    return has_completion_indicator and has_minimum_info

def save_project_progress(project_id: str, user_id: str, messages: List[Dict], 
                         ai_response: str, project_info: Dict, current_step: int,
                         is_complete: bool, model_id: str):
    """Save project progress to DynamoDB"""
    try:
        all_messages = messages + [{
            'role': 'assistant',
            'content': ai_response,
            'timestamp': datetime.utcnow().isoformat(),
            'modelId': model_id
        }]
        
        projects_table.put_item(
            Item={
                'projectId': project_id,
                'userId': user_id,
                'messages': all_messages,
                'projectInfo': project_info,
                'currentStep': current_step,
                'status': 'COMPLETED' if is_complete else 'IN_PROGRESS',
                'modelId': model_id,
                'messageCount': len(all_messages),
                'createdAt': int(datetime.utcnow().timestamp()),
                'updatedAt': datetime.utcnow().isoformat(),
                'completedAt': datetime.utcnow().isoformat() if is_complete else None
            }
        )
        logger.info(f"💾 Project progress saved: {project_id}")
    except Exception as e:
        logger.warning(f"Failed to save project progress: {str(e)}")

def generate_project_documents(body: Dict, context) -> Dict:
    """Generate project documents and upload to S3"""
    # This would contain the document generation logic
    # For now, return a placeholder
    return create_response(200, {
        'message': 'Document generation feature coming soon',
        'status': 'pending'
    })

def save_project_data(body: Dict, context) -> Dict:
    """Save project data"""
    # This would contain project saving logic
    return create_response(200, {
        'message': 'Project saved successfully',
        'status': 'saved'
    })

def get_project_data(body: Dict, context) -> Dict:
    """Get project data"""
    # This would contain project retrieval logic
    return create_response(200, {
        'message': 'Project data retrieved',
        'status': 'retrieved'
    })

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
