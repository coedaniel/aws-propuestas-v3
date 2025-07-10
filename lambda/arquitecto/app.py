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
    
    try:
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
        logger.info(f"Prompt body keys: {list(prompt_body.keys())}")
        
        # Call Bedrock
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps(prompt_body),
            contentType='application/json'
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        logger.info(f"Response body keys: {list(response_body.keys())}")
        
        ai_response, usage = extract_response(model_id, response_body)
        
        if not ai_response:
            logger.error(f"Empty response from model {model_id}")
            return create_response(500, {
                'error': 'Empty response from AI model',
                'modelId': model_id
            })
        
        # Check if project is complete
        is_complete = check_if_complete(ai_response, project_info)
        
        # Save project progress
        if projects_table:
            save_project_progress(project_id, user_id, messages, ai_response, project_info, 
                                current_step + 1, is_complete, model_id)
        
        response_data = {
            'response': ai_response,
            'modelId': model_id,
            'projectId': project_id,
            'currentStep': current_step + 1,
            'isComplete': is_complete,
            'usage': usage
        }
        
        logger.info(f"✅ ARQUITECTO SUCCESS - Response length: {len(ai_response)}")
        return create_response(200, response_data)
        
    except Exception as e:
        logger.error(f"Error in process_arquitecto_chat: {str(e)}")
        logger.error(f"Model ID: {model_id}")
        logger.error(f"Messages count: {len(messages) if messages else 0}")
        return create_response(500, {
            'error': 'Error processing arquitecto request',
            'details': str(e),
            'modelId': model_id
        })
        response_data['s3Folder'] = f"projects/{user_id}/{project_id}/"
        
        # Trigger async document generation (could be done via SQS/SNS in production)
        logger.info(f"🎯 Project complete! Generating documents for {project_id}")
    
    return create_response(200, response_data)

def get_arquitecto_system_prompt() -> str:
    """Get system prompt for arquitecto mode"""
    return """Actua como arquitecto de soluciones AWS y consultor experto. Vamos a dimensionar, documentar y entregar una solucion profesional en AWS, siguiendo mejores practicas y generando todos los archivos necesarios para una propuesta ejecutiva. No uses acentos ni caracteres especiales en ningun texto, archivo, script ni documento. Asegura que todos los archivos Word generados sean funcionales y compatibles: entrega solo texto plano, sin imagenes, sin tablas complejas, ni formato avanzado, solo texto estructurado, claro y legible. Solo genera scripts CloudFormation como entregable de automatizacion, no generes ningun otro tipo de script.

1. **Primero pregunta:**
Cual es el nombre del proyecto

2. **Despues pregunta:**
El proyecto es una solucion integral (como migracion, aplicacion nueva, modernizacion, analitica, seguridad, IA, IoT, data lake, networking, DRP, VDI, integracion, etc.)
o es un servicio rapido especifico (implementacion de instancias EC2, RDS, SES, VPN, ELB, S3, VPC, CloudFront, SSO, backup, etc.)

**Si elige "servicio rapido especifico":**

1. Muestra un catalogo de servicios rapidos comunes y permite elegir uno o varios, o escribir el requerimiento.
2. Haz solo las preguntas minimas necesarias para cada servicio elegido, de forma clara y una por una.
3. Con la informacion, genera y entrega SIEMPRE:
    - Tabla de actividades de implementacion (CSV o Excel, clara y lista para importar o compartir, SIN acentos ni caracteres especiales).
    - Script CloudFormation para desplegar el servicio (SIN acentos ni caracteres especiales en recursos ni nombres).
    - Diagrama de arquitectura en SVG, PNG y Draw.io editable (nombres y etiquetas SIN acentos ni caracteres especiales).
    - Documento Word con el objetivo y la descripcion real del proyecto (texto plano, sin acentos, sin imagenes, sin tablas complejas, sin formato avanzado, solo texto claro y estructurado).
    - Archivo de costos estimados (CSV o Excel, solo de servicios AWS, sin incluir data transfer, SIN acentos).
    - Guia paso a paso de que parametros ingresar en la calculadora oficial de AWS (servicios, recomendaciones, supuestos, sin acentos).
4. Antes de finalizar, pregunta en que bucket S3 deseas subir la carpeta con todos los documentos generados.
5. Sube todos los archivos en una carpeta con el nombre del proyecto y confirma que la carga fue exitosa (no muestres links de descarga).
6. Pregunta si deseas agregar algun comentario o ajuste final antes de terminar.

**Si elige "solucion integral" (proyecto complejo):**

1. Haz una entrevista guiada, una pregunta a la vez, para capturar:
    - Nombre del proyecto (si no lo has hecho ya)
    - Tipo de solucion (puede ser varias: migracion, app nueva, modernizacion, etc.)
    - Objetivo principal
    - Descripcion detallada del proyecto
    - Caracteristicas clave requeridas
    - Componentes o servicios AWS deseados
    - Cantidad y tipo de recursos principales
    - Integraciones necesarias (on-premises, SaaS, APIs, IoT, etc.)
    - Requisitos de seguridad y compliance
    - Alta disponibilidad, DRP, continuidad (multi-AZ, multi-region, RTO, RPO, backups)
    - Estimacion de usuarios, trafico, cargas
    - Presupuesto disponible (opcional)
    - Fechas de inicio y entrega deseadas
    - Restricciones tecnicas, negocio o preferencias tecnologicas
    - Comentarios o necesidades adicionales (opcional)
2. Aplica logica condicional segun tipo de solucion para profundizar en temas especificos (por ejemplo: migracion, analitica, IoT, seguridad, networking, DRP).
3. Con la informacion capturada, genera y entrega SIEMPRE:
    - Tabla de actividades de implementacion (CSV o Excel, profesional y clara, SIN acentos ni caracteres especiales).
    - Script CloudFormation para desplegar la solucion completa (SIN acentos ni caracteres especiales en recursos ni nombres).
    - Dos diagramas de arquitectura (SVG, PNG, Draw.io editable, layout profesional, SIN acentos).
    - Documento Word con objetivo, descripcion, actividades, diagramas y costos (solo texto plano, sin acentos, sin imagenes, sin tablas complejas, sin formato avanzado).
    - Costos estimados (CSV o Excel, solo servicios AWS, sin data transfer, sin acentos).
    - Guia paso a paso para la calculadora oficial de AWS (sin acentos).
4. Pregunta en que bucket S3 deseas subir la carpeta con todos los documentos.
5. Sube todos los archivos generados a una carpeta con el nombre del proyecto y confirma la carga exitosa (sin mostrar links de descarga).
6. Permite agregar comentarios o ajustes antes de cerrar la propuesta.

**En todas las preguntas y entregas:**

- Se claro, especifico y pregunta una cosa a la vez.
- Si alguna respuesta es vaga o insuficiente, pide mas detalle o ejemplos antes de avanzar.
- Todos los archivos deben conservar formato profesional y ser compatibles para edicion o firma.
- El flujo es siempre guiado y conversacional.
- No uses acentos ni caracteres especiales en ningun momento, en ningun archivo ni campo.

**Nota:**

- Los diagramas siempre deben entregarse en SVG, PNG y Draw.io editable, sin acentos ni caracteres especiales.
- La carpeta final debe contener todos los entregables bien organizados, y estar subida al bucket S3 indicado.
- Los documentos Word deben ser funcionales y abrirse correctamente en Microsoft Word o editores compatibles, solo texto plano, sin acentos ni caracteres especiales, sin imagenes, sin tablas complejas."""

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
