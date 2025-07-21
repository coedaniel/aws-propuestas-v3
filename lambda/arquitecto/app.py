import json
import boto3
import os
import uuid
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
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

# Arquitecto Master Prompt
ARQUITECTO_MASTER_PROMPT = """Actua como arquitecto de soluciones AWS y consultor experto.
Vamos a dimensionar, documentar y entregar una solucion profesional en AWS, siguiendo mejores practicas y generando todos los archivos necesarios para una propuesta ejecutiva.

REGLAS IMPORTANTES:
- No uses acentos ni caracteres especiales en ningun texto, archivo, script ni documento
- Asegura que todos los archivos Word generados sean funcionales y compatibles: entrega solo texto plano, sin imagenes, sin tablas complejas, ni formato avanzado, solo texto estructurado, claro y legible
- Solo genera scripts CloudFormation como entregable de automatizacion, no generes ningun otro tipo de script

PROCESO GUIADO:

1. INICIO: Pregunta "Cual es el nombre del proyecto"

2. TIPO: Pregunta si el proyecto es:
   - Solucion integral (migracion, aplicacion nueva, modernizacion, analitica, seguridad, IA, IoT, data lake, networking, DRP, VDI, integracion, etc.)
   - Servicio rapido especifico (EC2, RDS, SES, VPN, ELB, S3, VPC, CloudFront, SSO, backup, etc.)

3. SERVICIO RAPIDO:
   - Muestra catalogo de servicios rapidos comunes
   - Haz preguntas minimas necesarias, una por una
   - Genera SIEMPRE: tabla actividades (CSV), script CloudFormation, diagramas (SVG/PNG), documento Word (texto plano), costos estimados (CSV), guia calculadora AWS
   - Pregunta bucket S3 para subir archivos
   - Sube carpeta con nombre del proyecto
   - Pregunta ajustes finales

4. SOLUCION INTEGRAL:
   - Entrevista guiada: nombre, tipo, objetivo, descripcion, caracteristicas, servicios AWS, recursos, integraciones, seguridad, HA, DRP, trafico, presupuesto, fechas, restricciones
   - Aplica logica condicional segun tipo
   - Genera SIEMPRE: tabla actividades, script CloudFormation completo, diagramas SVG/PNG/Draw.io, documento Word completo (texto plano), costos estimados, guia calculadora AWS
   - Pregunta bucket S3 para subir
   - Sube carpeta con nombre proyecto
   - Pregunta ajustes finales

IMPORTANTE:
- Se claro, especifico y pregunta una cosa a la vez
- Si respuesta es vaga, pide mas detalle antes de avanzar
- Archivos siempre compatibles y sin acentos
- Diagramas: SVG, PNG y Draw.io
- Documentos Word: solo texto plano, sin acentos ni formato complejo

Usa MCPs inteligentemente para:
- Generar diagramas (aws_diagram_mcp_server)
- Calcular costos (aws_pricing_calculator)
- Crear documentos (file_operations)
- Subir a S3 (aws_s3_operations)
- Consultar documentacion AWS (aws_documentation_mcp_server)
- Generar CloudFormation (aws_cloudformation_mcp_server)"""

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
        
        logger.info(f"ARQUITECTO MASTER - Processing request: {json.dumps(body, default=str)}")
        
        return process_arquitecto_chat(body, context)
        
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return create_response(500, {'error': str(e)})

def process_arquitecto_chat(body: Dict[str, Any], context) -> Dict[str, Any]:
    """Process arquitecto chat with master prompt"""
    try:
        messages = body.get('messages', [])
        model_id = body.get('modelId', 'anthropic.claude-3-5-sonnet-20241022-v2:0')
        project_state = body.get('projectState', {'phase': 'inicio', 'data': {}})
        
        logger.info(f"Processing chat with {len(messages)} messages, model: {model_id}")
        logger.info(f"Project state: {project_state}")
        
        # Analyze current phase and user input
        current_phase = project_state.get('phase', 'inicio')
        user_message = messages[-1]['content'] if messages and messages[-1]['role'] == 'user' else ""
        
        # Determine next phase and update project state
        updated_project_state, phase_context = analyze_and_update_phase(
            current_phase, user_message, project_state
        )
        
        # Prepare conversation with master prompt
        conversation_messages = prepare_conversation_messages(messages, phase_context)
        
        # Call Bedrock
        response_data = call_bedrock_model(model_id, conversation_messages)
        
        # Simulate MCP usage based on content
        mcp_used = detect_mcp_usage(response_data['response'], current_phase)
        
        # Prepare response
        result = {
            'response': response_data['response'],
            'usage': response_data.get('usage', {}),
            'mcpUsed': mcp_used,
            'projectUpdate': updated_project_state,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Response prepared with {len(mcp_used)} MCPs used")
        return create_response(200, result)
        
    except Exception as e:
        logger.error(f"Error in process_arquitecto_chat: {str(e)}")
        return create_response(500, {'error': str(e)})

def analyze_and_update_phase(current_phase: str, user_input: str, project_state: Dict) -> tuple:
    """Analyze user input and determine next phase"""
    
    phase_context = ""
    updated_state = project_state.copy()
    
    if current_phase == 'inicio':
        # Looking for project name
        if user_input and len(user_input.strip()) > 2:
            updated_state['name'] = user_input.strip()
            updated_state['phase'] = 'tipo'
            phase_context = f"Proyecto '{user_input.strip()}' registrado. Ahora pregunta sobre el tipo de solucion."
    
    elif current_phase == 'tipo':
        # Looking for solution type
        user_lower = user_input.lower()
        if any(word in user_lower for word in ['integral', 'migracion', 'aplicacion', 'modernizacion', 'analitica', 'seguridad', 'ia', 'iot', 'data lake', 'networking', 'drp', 'vdi', 'integracion']):
            updated_state['type'] = 'integral'
            updated_state['phase'] = 'recopilacion'
            phase_context = "Solucion integral detectada. Inicia entrevista guiada detallada."
        elif any(word in user_lower for word in ['rapido', 'especifico', 'ec2', 'rds', 'ses', 'vpn', 'elb', 's3', 'vpc', 'cloudfront', 'sso', 'backup']):
            updated_state['type'] = 'rapido'
            updated_state['phase'] = 'recopilacion'
            phase_context = "Servicio rapido detectado. Muestra catalogo y haz preguntas especificas."
    
    elif current_phase == 'recopilacion':
        # Collecting requirements
        if len(user_input.strip()) > 10:  # Sufficient detail provided
            updated_state['phase'] = 'generacion'
            phase_context = "Requisitos recopilados. Procede a generar documentos y archivos."
    
    elif current_phase == 'generacion':
        # Generating documents
        if 'confirmar' in user_input.lower() or 'generar' in user_input.lower() or 'crear' in user_input.lower():
            updated_state['phase'] = 'entrega'
            phase_context = "Generando documentos finales y preparando entrega."
    
    return updated_state, phase_context

def prepare_conversation_messages(messages: List[Dict], phase_context: str) -> List[Dict]:
    """Prepare messages for Bedrock with master prompt"""
    
    # Start with master prompt
    conversation = [
        {
            "role": "user",
            "content": ARQUITECTO_MASTER_PROMPT
        },
        {
            "role": "assistant", 
            "content": "Entendido. Soy tu Arquitecto de Soluciones AWS y consultor experto. Vamos a crear una solucion profesional siguiendo el proceso guiado. Para comenzar: ¿Cual es el nombre del proyecto?"
        }
    ]
    
    # Add phase context if available
    if phase_context:
        conversation.append({
            "role": "user",
            "content": f"CONTEXTO DE FASE: {phase_context}"
        })
        conversation.append({
            "role": "assistant",
            "content": "Contexto registrado. Continuando con el proceso guiado."
        })
    
    # Add conversation history (skip the first welcome message)
    for msg in messages[1:] if len(messages) > 1 else messages:
        conversation.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    return conversation

def detect_mcp_usage(response_content: str, current_phase: str) -> List[str]:
    """Detect which MCPs should be used based on response content and phase"""
    
    mcp_used = []
    content_lower = response_content.lower()
    
    # Always use core MCP for understanding
    mcp_used.append("awslabscore_mcp_server___prompt_understanding")
    
    # Phase-specific MCP usage
    if current_phase in ['generacion', 'entrega']:
        # Document generation phase
        if any(word in content_lower for word in ['diagrama', 'arquitectura', 'diseño']):
            mcp_used.append("awslabsaws_diagram_mcp_server___generate_diagram")
        
        if any(word in content_lower for word in ['costo', 'precio', 'presupuesto']):
            mcp_used.append("awslabspricing_mcp_server___calculate_costs")
        
        if any(word in content_lower for word in ['cloudformation', 'template', 'script']):
            mcp_used.append("awslabscloudformation_mcp_server___generate_template")
        
        if any(word in content_lower for word in ['documento', 'word', 'archivo']):
            mcp_used.append("awslabsfile_operations___create_document")
        
        if any(word in content_lower for word in ['s3', 'bucket', 'subir', 'almacenar']):
            mcp_used.append("awslabss3_operations___upload_files")
    
    # AWS documentation lookup
    if any(service in content_lower for service in ['ec2', 'rds', 'lambda', 'vpc', 'cloudfront', 'elb', 'ses']):
        mcp_used.append("awslabsaws_documentation_mcp_server___search_documentation")
    
    return list(set(mcp_used))  # Remove duplicates

def call_bedrock_model(model_id: str, messages: List[Dict]) -> Dict[str, Any]:
    """Call Bedrock model with conversation"""
    
    try:
        # Prepare the prompt based on model type
        if 'anthropic' in model_id.lower():
            response = call_anthropic_model(model_id, messages)
        elif 'amazon.nova' in model_id.lower():
            response = call_nova_model(model_id, messages)
        else:
            # Default to Anthropic format
            response = call_anthropic_model(model_id, messages)
        
        return response
        
    except Exception as e:
        logger.error(f"Error calling Bedrock model: {str(e)}")
        raise

def call_anthropic_model(model_id: str, messages: List[Dict]) -> Dict[str, Any]:
    """Call Anthropic Claude model"""
    
    # Convert messages to Anthropic format
    anthropic_messages = []
    for msg in messages:
        anthropic_messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4000,
        "temperature": 0.7,
        "messages": anthropic_messages
    }
    
    response = bedrock_runtime.invoke_model(
        modelId=model_id,
        body=json.dumps(request_body)
    )
    
    response_body = json.loads(response['body'].read())
    
    return {
        'response': response_body['content'][0]['text'],
        'usage': {
            'inputTokens': response_body.get('usage', {}).get('input_tokens', 0),
            'outputTokens': response_body.get('usage', {}).get('output_tokens', 0)
        }
    }

def call_nova_model(model_id: str, messages: List[Dict]) -> Dict[str, Any]:
    """Call Amazon Nova model"""
    
    # Convert messages to Nova format
    nova_messages = []
    for msg in messages:
        nova_messages.append({
            "role": msg["role"],
            "content": [{"text": msg["content"]}]
        })
    
    request_body = {
        "messages": nova_messages,
        "inferenceConfig": {
            "maxTokens": 4000,
            "temperature": 0.7
        }
    }
    
    response = bedrock_runtime.invoke_model(
        modelId=model_id,
        body=json.dumps(request_body)
    )
    
    response_body = json.loads(response['body'].read())
    
    return {
        'response': response_body['output']['message']['content'][0]['text'],
        'usage': {
            'inputTokens': response_body.get('usage', {}).get('inputTokens', 0),
            'outputTokens': response_body.get('usage', {}).get('outputTokens', 0)
        }
    }

def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Create HTTP response with CORS headers"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With'
        },
        'body': json.dumps(body, default=str, ensure_ascii=False)
    }
