"""
AWS Propuestas v3 - Arquitecto Lambda con Detección Inteligente MCP
Sistema automático como Amazon Q CLI - NO depende de frases específicas
"""

import json
import boto3
import os
import requests
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ.get('REGION', 'us-east-1'))
s3_client = boto3.client('s3', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Variables de entorno
DOCUMENTS_BUCKET = os.environ.get('DOCUMENTS_BUCKET', 'aws-propuestas-v3-documents-prod-035385358261')
PROJECTS_TABLE = os.environ.get('PROJECTS_TABLE', 'aws-propuestas-v3-projects-prod')

# URLs de los servicios MCP ECS - CORREGIDAS
MCP_BASE_URL = "https://mcp.danielingram.shop"
MCP_SERVICES = {
    'core': f"{MCP_BASE_URL}",
    'pricing': f"{MCP_BASE_URL}/pricing", 
    'awsdocs': f"{MCP_BASE_URL}/awsdocs",
    'cfn': f"{MCP_BASE_URL}/cfn",
    'diagram': f"{MCP_BASE_URL}/diagram",
    'customdoc': f"{MCP_BASE_URL}/docgen"
}

# Prompt maestro completo - MANTENER IGUAL
PROMPT_MAESTRO = """
Actua como arquitecto de soluciones AWS y consultor experto. Vamos a dimensionar, documentar y entregar una solucion profesional en AWS, siguiendo mejores practicas y generando todos los archivos necesarios para una propuesta ejecutiva. No uses acentos ni caracteres especiales en ningun texto, archivo, script ni documento.

IMPORTANTE: Sigue este flujo paso a paso:

1. Primero pregunta: Cual es el nombre del proyecto

2. Despues pregunta: El proyecto es una solucion integral (como migracion, aplicacion nueva, modernizacion, analitica, seguridad, IA, IoT, data lake, networking, DRP, VDI, integracion, etc.) o es un servicio rapido especifico (implementacion de instancias EC2, RDS, SES, VPN, ELB, S3, VPC, CloudFront, SSO, backup, etc.)

3. Haz MUCHAS preguntas detalladas una por una para capturar toda la informacion necesaria

4. SOLO al final, cuando tengas TODA la informacion, di exactamente: "GENERO LOS SIGUIENTES DOCUMENTOS:" y lista todos los documentos que vas a crear.

NO generes documentos hasta tener toda la informacion completa del proyecto.
Pregunta una cosa a la vez. Se detallado y minucioso.
"""

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

def calculate_intelligent_readiness(messages: List[Dict]) -> Dict[str, Any]:
    """
    Calcula readiness automáticamente como Amazon Q CLI
    NO depende de frases específicas, sino del CONTEXTO
    """
    conversation_text = " ".join([msg.get("content", "") for msg in messages]).lower()
    
    # Criterios de detección inteligente
    criteria = {
        'project_name': False,
        'project_type': False,
        'technical_details': False,
        'sufficient_context': False,
        'ready_for_generation': False
    }
    
    score = 0.0
    
    # 1. Nombre del proyecto (25%)
    if any(word in conversation_text for word in ['proyecto', 'sistema', 'aplicacion', 'plataforma']) or len([msg for msg in messages if msg.get('role') == 'user']) >= 1:
        criteria['project_name'] = True
        score += 0.25
        logger.info("✅ Criterio 1: Proyecto identificado (+25%)")
    
    # 2. Tipo de proyecto (25%)
    if any(word in conversation_text for word in ['integral', 'rapido', 'servicio', 'ec2', 'rds', 's3', 'lambda', 'aplicacion']):
        criteria['project_type'] = True
        score += 0.25
        logger.info("✅ Criterio 2: Tipo identificado (+25%)")
    
    # 3. Detalles técnicos suficientes (25%)
    technical_indicators = ['instancia', 'tipo', 'region', 'volumen', 'vpc', 'security', 'key', 'tamaño', 'gb', 'micro', 'large']
    if sum(1 for indicator in technical_indicators if indicator in conversation_text) >= 3:
        criteria['technical_details'] = True
        score += 0.25
        logger.info("✅ Criterio 3: Detalles técnicos suficientes (+25%)")
    
    # 4. Contexto suficiente (25%)
    user_messages = [msg for msg in messages if msg.get('role') == 'user']
    if len(user_messages) >= 4:  # Al menos 4 respuestas del usuario
        criteria['sufficient_context'] = True
        score += 0.25
        logger.info("✅ Criterio 4: Contexto suficiente (+25%)")
    
    # Determinar si está listo para generación
    if score >= 0.8:  # 80% o más
        criteria['ready_for_generation'] = True
        logger.info("🎯 READY FOR GENERATION: Score >= 0.8")
    
    return {
        'readiness_score': score,
        'criteria': criteria,
        'ready_for_mcps': criteria['ready_for_generation'],
        'phase': 3 if score >= 0.8 else (2 if score >= 0.5 else 1)
    }

def call_mcp_service(service_name, endpoint, data):
    """Llama a un servicio MCP específico"""
    try:
        url = f"{MCP_SERVICES[service_name]}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        logger.info(f"🔧 Calling MCP {service_name}: {url}")
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            logger.info(f"✅ MCP {service_name} responded successfully")
            return response.json()
        else:
            logger.error(f"❌ MCP {service_name} error: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"❌ Exception calling MCP {service_name}: {str(e)}")
        return None

def extract_project_info(messages: List[Dict]) -> Dict:
    """Extrae información del proyecto de la conversación"""
    conversation_text = " ".join([msg.get("content", "") for msg in messages]).lower()
    
    project_info = {
        'id': str(uuid.uuid4())[:8],
        'name': 'AWS Project',
        'type': 'Solucion AWS',
        'description': 'Proyecto AWS generado automaticamente'
    }
    
    # Extraer nombre del proyecto
    user_messages = [msg.get("content", "") for msg in messages if msg.get('role') == 'user']
    if user_messages:
        first_response = user_messages[0].strip()
        if len(first_response.split()) <= 3:  # Probablemente es el nombre
            project_info['name'] = first_response
    
    # Determinar tipo
    if 'ec2' in conversation_text:
        project_info['type'] = 'Implementacion EC2'
    elif 'rds' in conversation_text:
        project_info['type'] = 'Base de Datos RDS'
    elif 'integral' in conversation_text:
        project_info['type'] = 'Solucion Integral'
    
    return project_info

def activate_mcps_intelligently(project_info: Dict, conversation_text: str) -> Dict:
    """Activa MCPs automáticamente basado en el contexto"""
    logger.info("🚀 ACTIVATING MCPs INTELLIGENTLY...")
    
    activated_mcps = []
    generated_content = {}
    
    # 1. SIEMPRE: Core MCP para análisis
    core_result = call_mcp_service('core', 'analyze', {
        'project_name': project_info['name'],
        'conversation': conversation_text
    })
    if core_result:
        activated_mcps.append('core-mcp-analysis')
        generated_content['analysis'] = core_result
    
    # 2. Diagram MCP para generar arquitectura
    diagram_result = call_mcp_service('diagram', 'generate', {
        'project_name': project_info['name'],
        'project_type': project_info['type'],
        'services': ['EC2', 'VPC', 'Security Groups'] if 'ec2' in conversation_text else ['Lambda', 'API Gateway']
    })
    if diagram_result:
        activated_mcps.append('diagram-mcp-generation')
        generated_content['diagram'] = diagram_result
    
    # 3. CloudFormation MCP para templates
    cfn_result = call_mcp_service('cfn', 'generate', {
        'project_name': project_info['name'],
        'services': ['EC2'] if 'ec2' in conversation_text else ['Lambda'],
        'environment': 'prod'
    })
    if cfn_result:
        activated_mcps.append('cloudformation-mcp-generation')
        generated_content['cloudformation'] = cfn_result
    
    # 4. Custom Doc MCP para documentación
    doc_result = call_mcp_service('customdoc', 'generate', {
        'project_name': project_info['name'],
        'project_type': project_info['type'],
        'description': f'Documentacion automatica para {project_info["name"]}'
    })
    if doc_result:
        activated_mcps.append('documentation-mcp-generation')
        generated_content['documentation'] = doc_result
    
    return {
        'activated_mcps': activated_mcps,
        'generated_content': generated_content,
        'mcp_count': len(activated_mcps)
    }

def prepare_conversation(messages: List[Dict], project_state: Dict) -> List[Dict]:
    """Prepare conversation for Bedrock with correct format"""
    conversation = []
    
    # Add system message with correct format (as user message for Bedrock)
    conversation.append({
        "role": "user",
        "content": [{"text": PROMPT_MAESTRO}]
    })
    
    # Add project state context if available
    if project_state.get('data') and project_state['data']:
        context = f"CONTEXTO DEL PROYECTO: {json.dumps(project_state['data'], indent=2)}"
        conversation.append({
            "role": "user", 
            "content": [{"text": context}]
        })
    
    # Add conversation history with correct format
    for msg in messages:
        content = msg.get("content", "")
        if content.strip():  # Only add non-empty messages
            conversation.append({
                "role": msg.get("role", "user"),
                "content": [{"text": content}]
            })
    
    return conversation

def call_bedrock_model(model_id: str, conversation: List[Dict]) -> Dict:
    """Call Bedrock model with correct format"""
    try:
        logger.info(f"Calling Bedrock model: {model_id}")
        logger.info(f"Conversation length: {len(conversation)}")
        
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
        logger.info(f"Bedrock response received, length: {len(content)}")
        
        return {
            'content': content,
            'usage': response.get('usage', {}),
            'modelUsed': model_id
        }
        
    except Exception as e:
        logger.error(f"Error calling Bedrock: {str(e)}", exc_info=True)
        return {'error': f'Error calling Bedrock: {str(e)}'}

def lambda_handler(event, context):
    """Main Lambda handler con detección inteligente automática"""
    
    try:
        logger.info(f"Event received: {json.dumps(event, default=str)}")
        
        # Handle CORS preflight requests
        if event.get('httpMethod') == 'OPTIONS':
            logger.info("Handling OPTIONS preflight request")
            return handle_preflight_request()
        
        # Parse request
        try:
            if isinstance(event.get('body'), str):
                body = json.loads(event['body'])
            else:
                body = event.get('body', {})
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return create_error_response(400, 'Invalid JSON in request body')
        
        messages = body.get('messages', [])
        model_id = body.get('modelId', 'anthropic.claude-3-5-sonnet-20240620-v1:0')
        project_state = body.get('projectState', {'phase': 'inicio', 'data': {}})
        
        if not messages:
            logger.error("No messages provided")
            return create_error_response(400, 'No messages provided')
        
        logger.info(f"Processing {len(messages)} messages with model: {model_id}")
        
        # DETECCIÓN INTELIGENTE AUTOMÁTICA (Como Amazon Q CLI)
        readiness = calculate_intelligent_readiness(messages)
        logger.info(f"🧠 Intelligent Analysis: Score={readiness['readiness_score']:.2f}, Phase={readiness['phase']}, Ready={readiness['ready_for_mcps']}")
        
        # Prepare conversation for Bedrock
        conversation = prepare_conversation(messages, project_state)
        
        if not conversation:
            logger.error("Empty conversation after preparation")
            return create_error_response(400, 'No valid conversation content')
        
        # Call Bedrock model
        bedrock_response = call_bedrock_model(model_id, conversation)
        
        if 'error' in bedrock_response:
            logger.error(f"Bedrock error: {bedrock_response['error']}")
            return create_error_response(500, bedrock_response['error'])
        
        response_content = bedrock_response['content']
        
        if not response_content or not response_content.strip():
            logger.error("Empty response from Bedrock")
            return create_error_response(500, 'Empty response from AI model')
        
        # ACTIVACIÓN INTELIGENTE DE MCPs
        mcp_results = {'activated_mcps': [], 'generated_content': {}, 'mcp_count': 0}
        
        if readiness['ready_for_mcps']:
            logger.info("🎯 TRIGGERING INTELLIGENT MCP ACTIVATION")
            conversation_text = " ".join([msg.get("content", "") for msg in messages])
            project_info = extract_project_info(messages)
            mcp_results = activate_mcps_intelligently(project_info, conversation_text)
            
            # Si se generaron documentos reales, reemplazar la respuesta
            if mcp_results['generated_content']:
                logger.info("📄 Replacing response with MCP-generated content")
                response_content += "\n\n--- DOCUMENTOS GENERADOS AUTOMATICAMENTE ---\n"
                
                if 'diagram' in mcp_results['generated_content']:
                    response_content += f"\n**DIAGRAMA DE ARQUITECTURA:**\n{mcp_results['generated_content']['diagram']}\n"
                
                if 'cloudformation' in mcp_results['generated_content']:
                    response_content += f"\n**CLOUDFORMATION TEMPLATE:**\n{mcp_results['generated_content']['cloudformation']}\n"
                
                if 'documentation' in mcp_results['generated_content']:
                    response_content += f"\n**DOCUMENTACION:**\n{mcp_results['generated_content']['documentation']}\n"
        
        # Response data con MCP inteligente
        response_data = {
            'content': response_content,
            'projectState': project_state,
            'mcpActivated': readiness['ready_for_mcps'],
            'mcpStatus': f'intelligent_phase_{readiness["phase"]}',
            'mcpUsed': mcp_results['activated_mcps'],
            'readinessScore': readiness['readiness_score'],
            'readinessCriteria': readiness['criteria'],
            'mcpGeneratedContent': mcp_results['generated_content'],
            'modelUsed': bedrock_response.get('modelUsed', model_id),
            'usage': bedrock_response.get('usage', {}),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Response ready: MCP Activated={readiness['ready_for_mcps']}, MCPs Used={len(mcp_results['activated_mcps'])}")
        return create_success_response(response_data)
        
    except Exception as e:
        logger.error(f"Unexpected error in lambda_handler: {str(e)}", exc_info=True)
        return create_error_response(500, f'Internal server error: {str(e)}')
