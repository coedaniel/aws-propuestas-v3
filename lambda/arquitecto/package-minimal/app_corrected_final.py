"""
AWS Propuestas v3 - Arquitecto Lambda CORREGIDO
1. Prompt maestro original restaurado
2. Lógica MCP corregida (Docs solo cuando necesario)
3. Guardado en S3 implementado
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

# URLs de los servicios MCP ECS - CORRECTAS
MCP_BASE_URL = "https://mcp.danielingram.shop"
MCP_SERVICES = {
    'core': f"{MCP_BASE_URL}",
    'pricing': f"{MCP_BASE_URL}/pricing", 
    'awsdocs': f"{MCP_BASE_URL}/awsdocs",
    'cfn': f"{MCP_BASE_URL}/cfn",
    'diagram': f"{MCP_BASE_URL}/diagram",
    'customdoc': f"{MCP_BASE_URL}/docgen"
}

# PROMPT MAESTRO ORIGINAL COMPLETO - RESTAURADO
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

def call_mcp_service(service_name, endpoint, data):
    """Llama a un servicio MCP específico"""
    try:
        url = f"{MCP_SERVICES[service_name]}/{endpoint}" if endpoint else MCP_SERVICES[service_name]
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

def activate_core_mcp_always(messages: List[Dict]) -> Dict:
    """
    MCP CORE - SIEMPRE ACTIVO (como Amazon Q CLI)
    Se ejecuta en CADA mensaje para prompt understanding
    """
    logger.info("🧠 ACTIVATING CORE MCP - ALWAYS ACTIVE")
    
    conversation_text = " ".join([msg.get("content", "") for msg in messages])
    
    core_result = call_mcp_service('core', 'analyze', {
        'conversation': conversation_text,
        'action': 'prompt_understanding',
        'timestamp': datetime.now().isoformat()
    })
    
    return {
        'activated': True,
        'result': core_result,
        'reason': 'Core MCP always active for prompt understanding'
    }

def check_docs_mcp_needed(messages: List[Dict]) -> Dict:
    """
    MCP AWS DOCS - ACTIVACIÓN CONDICIONAL CORREGIDA
    SOLO se activa cuando hay triggers específicos
    """
    conversation_text = " ".join([msg.get("content", "") for msg in messages]).lower()
    
    # Triggers específicos para documentación (MÁS RESTRICTIVOS)
    explicit_docs_triggers = [
        'documentacion', 'busca documentacion', 'buscar documentacion',
        'mejores practicas', 'como hacer', 'que es lambda', 'que es ec2',
        'aws docs', 'documentacion oficial', 'guia oficial',
        'tutorial', 'ejemplo oficial', 'referencia aws'
    ]
    
    # Preguntas específicas que requieren docs oficiales
    specific_questions = [
        'como configurar', 'como implementar', 'como usar',
        'cual es la diferencia', 'que diferencia hay',
        'limites de', 'restricciones de', 'pricing de'
    ]
    
    needs_docs = (
        any(trigger in conversation_text for trigger in explicit_docs_triggers) or
        any(question in conversation_text for question in specific_questions)
    )
    
    if needs_docs:
        logger.info("📚 ACTIVATING AWS DOCS MCP - Explicit documentation request detected")
        
        docs_result = call_mcp_service('awsdocs', 'search', {
            'query': conversation_text,
            'action': 'get_official_docs',
            'timestamp': datetime.now().isoformat()
        })
        
        return {
            'activated': True,
            'result': docs_result,
            'reason': 'Explicit documentation request detected'
        }
    else:
        logger.info("📚 AWS Docs MCP NOT NEEDED - No explicit documentation triggers")
        return {
            'activated': False,
            'result': None,
            'reason': 'No explicit documentation triggers detected'
        }

def calculate_generation_readiness(messages: List[Dict]) -> Dict:
    """
    Calcula readiness SOLO para MCPs de generación
    """
    conversation_text = " ".join([msg.get("content", "") for msg in messages]).lower()
    
    score = 0.0
    criteria = {}
    
    # 1. Nombre del proyecto (25%)
    if any(word in conversation_text for word in ['proyecto', 'sistema', 'aplicacion', 'plataforma']):
        criteria['project_name'] = True
        score += 0.25
    else:
        criteria['project_name'] = False
    
    # 2. Tipo de proyecto (25%)
    if any(word in conversation_text for word in ['integral', 'rapido', 'servicio', 'ec2', 'rds', 's3', 'lambda']):
        criteria['project_type'] = True
        score += 0.25
    else:
        criteria['project_type'] = False
    
    # 3. Detalles técnicos (25%)
    technical_indicators = ['instancia', 'tipo', 'region', 'volumen', 'vpc', 'security', 'key', 'tamaño', 'gb']
    if sum(1 for indicator in technical_indicators if indicator in conversation_text) >= 3:
        criteria['technical_details'] = True
        score += 0.25
    else:
        criteria['technical_details'] = False
    
    # 4. Contexto suficiente (25%)
    user_messages = [msg for msg in messages if msg.get('role') == 'user']
    if len(user_messages) >= 4:
        criteria['sufficient_context'] = True
        score += 0.25
    else:
        criteria['sufficient_context'] = False
    
    return {
        'readiness_score': score,
        'criteria': criteria,
        'ready_for_generation': score >= 0.8
    }

def activate_generation_mcps(messages: List[Dict]) -> Dict:
    """
    MCPs DE GENERACIÓN - Solo cuando readiness_score >= 0.8
    INCLUYE GUARDADO EN S3
    """
    logger.info("🎯 ACTIVATING GENERATION MCPs - Project ready for document generation")
    
    conversation_text = " ".join([msg.get("content", "") for msg in messages])
    project_info = extract_project_info(messages)
    
    activated_mcps = []
    generated_content = {}
    
    # 1. Diagram MCP
    diagram_result = call_mcp_service('diagram', 'generate', {
        'project_name': project_info['name'],
        'project_type': project_info['type'],
        'services': ['EC2', 'VPC'] if 'ec2' in conversation_text else ['Lambda', 'API Gateway']
    })
    if diagram_result:
        activated_mcps.append('diagram-mcp')
        generated_content['diagram'] = diagram_result
    
    # 2. CloudFormation MCP
    cfn_result = call_mcp_service('cfn', 'generate', {
        'project_name': project_info['name'],
        'services': ['EC2'] if 'ec2' in conversation_text else ['Lambda'],
        'environment': 'prod'
    })
    if cfn_result:
        activated_mcps.append('cloudformation-mcp')
        generated_content['cloudformation'] = cfn_result
    
    # 3. Document Generator MCP
    doc_result = call_mcp_service('customdoc', 'generate', {
        'project_name': project_info['name'],
        'project_type': project_info['type'],
        'format': ['csv', 'docx', 'xlsx']
    })
    if doc_result:
        activated_mcps.append('document-generator-mcp')
        generated_content['documentation'] = doc_result
    
    # 4. Pricing MCP
    pricing_result = call_mcp_service('pricing', 'calculate', {
        'services': ['EC2'] if 'ec2' in conversation_text else ['Lambda'],
        'usage_estimates': {'hours_per_month': 730}
    })
    if pricing_result:
        activated_mcps.append('pricing-mcp')
        generated_content['pricing'] = pricing_result
    
    # 5. GUARDAR EN S3 - IMPLEMENTADO
    if generated_content:
        s3_result = save_documents_to_s3(project_info, generated_content)
        if s3_result:
            logger.info(f"📁 Documents saved to S3: {s3_result['folder_name']}")
    
    return {
        'activated_mcps': activated_mcps,
        'generated_content': generated_content,
        'mcp_count': len(activated_mcps),
        's3_folder': f"{project_info['name'].lower().replace(' ', '-')}-{project_info['id'][:8]}" if generated_content else None
    }

def save_documents_to_s3(project_info: Dict, generated_content: Dict) -> Dict:
    """
    GUARDA DOCUMENTOS EN S3 EN CARPETA POR PROYECTO
    """
    try:
        folder_name = f"{project_info['name'].lower().replace(' ', '-')}-{project_info['id'][:8]}"
        
        logger.info(f"📁 Saving documents to S3 folder: {folder_name}")
        
        documents_saved = []
        
        for content_type, content_data in generated_content.items():
            # Determinar extensión del archivo
            if content_type == 'diagram':
                file_extension = 'svg'
                content_type_s3 = 'image/svg+xml'
            elif content_type == 'cloudformation':
                file_extension = 'yaml'
                content_type_s3 = 'text/yaml'
            elif content_type == 'documentation':
                file_extension = 'txt'
                content_type_s3 = 'text/plain'
            elif content_type == 'pricing':
                file_extension = 'json'
                content_type_s3 = 'application/json'
            else:
                file_extension = 'txt'
                content_type_s3 = 'text/plain'
            
            file_name = f"{content_type}.{file_extension}"
            s3_key = f"{folder_name}/{file_name}"
            
            # Convertir contenido a string si es necesario
            if isinstance(content_data, dict):
                content_str = json.dumps(content_data, indent=2)
            else:
                content_str = str(content_data)
            
            # Subir a S3
            s3_client.put_object(
                Bucket=DOCUMENTS_BUCKET,
                Key=s3_key,
                Body=content_str,
                ContentType=content_type_s3,
                Metadata={
                    'project_name': project_info['name'],
                    'project_type': project_info['type'],
                    'generated_at': datetime.now().isoformat()
                }
            )
            
            documents_saved.append({
                'file_name': file_name,
                's3_key': s3_key,
                'content_type': content_type
            })
            
            logger.info(f"✅ Saved {file_name} to S3: {s3_key}")
        
        # Guardar proyecto en DynamoDB
        save_project_to_dynamodb(project_info, documents_saved, folder_name)
        
        return {
            'folder_name': folder_name,
            'documents_saved': documents_saved,
            'bucket': DOCUMENTS_BUCKET,
            'total_files': len(documents_saved)
        }
        
    except Exception as e:
        logger.error(f"❌ Error saving to S3: {str(e)}")
        return None

def save_project_to_dynamodb(project_info: Dict, documents_saved: List[Dict], folder_name: str):
    """Guarda el proyecto en DynamoDB"""
    try:
        table = dynamodb.Table(PROJECTS_TABLE)
        
        project_item = {
            'projectId': project_info['id'],
            'projectName': project_info['name'],
            'projectType': project_info.get('type', 'Solucion AWS'),
            'status': 'completed',
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat(),
            's3Folder': folder_name,
            's3Bucket': DOCUMENTS_BUCKET,
            'documentsGenerated': documents_saved,
            'totalDocuments': len(documents_saved)
        }
        
        table.put_item(Item=project_item)
        logger.info(f"✅ Project saved to DynamoDB: {project_info['id']}")
        return True
    except Exception as e:
        logger.error(f"❌ Error saving to DynamoDB: {str(e)}")
        return False

def extract_project_info(messages: List[Dict]) -> Dict:
    """Extrae información del proyecto de la conversación"""
    conversation_text = " ".join([msg.get("content", "") for msg in messages]).lower()
    
    project_info = {
        'id': str(uuid.uuid4())[:8],
        'name': 'AWS Project',
        'type': 'Solucion AWS'
    }
    
    # Extraer nombre del proyecto
    user_messages = [msg.get("content", "") for msg in messages if msg.get('role') == 'user']
    if user_messages:
        first_response = user_messages[0].strip()
        if len(first_response.split()) <= 3:
            project_info['name'] = first_response
    
    # Determinar tipo
    if 'ec2' in conversation_text:
        project_info['type'] = 'Implementacion EC2'
    elif 'rds' in conversation_text:
        project_info['type'] = 'Base de Datos RDS'
    elif 'integral' in conversation_text:
        project_info['type'] = 'Solucion Integral'
    
    return project_info

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
        if content.strip():
            conversation.append({
                "role": msg.get("role", "user"),
                "content": [{"text": content}]
            })
    
    return conversation

def call_bedrock_model(model_id: str, conversation: List[Dict]) -> Dict:
    """Call Bedrock model with correct format"""
    try:
        logger.info(f"Calling Bedrock model: {model_id}")
        
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
    """Main Lambda handler - CORREGIDO PROFESIONALMENTE"""
    
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
        
        # === ACTIVACIÓN MCP CORREGIDA ===
        
        # 1. MCP CORE - SIEMPRE ACTIVO
        core_mcp = activate_core_mcp_always(messages)
        
        # 2. MCP AWS DOCS - SOLO CUANDO SEA NECESARIO (CORREGIDO)
        docs_mcp = check_docs_mcp_needed(messages)
        
        # 3. READINESS PARA GENERACIÓN
        generation_readiness = calculate_generation_readiness(messages)
        
        # 4. MCPs DE GENERACIÓN - Solo si readiness >= 0.8 + GUARDADO S3
        generation_mcps = {'activated_mcps': [], 'generated_content': {}, 'mcp_count': 0, 's3_folder': None}
        if generation_readiness['ready_for_generation']:
            generation_mcps = activate_generation_mcps(messages)
        
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
        
        # Si se generaron documentos reales, agregarlos a la respuesta
        if generation_mcps['generated_content']:
            logger.info("📄 Adding MCP-generated content to response")
            response_content += "\n\n--- DOCUMENTOS GENERADOS Y GUARDADOS EN S3 ---\n"
            response_content += f"📁 Carpeta: {generation_mcps['s3_folder']}\n"
            response_content += f"🪣 Bucket: {DOCUMENTS_BUCKET}\n\n"
            
            for content_type, content_data in generation_mcps['generated_content'].items():
                response_content += f"**{content_type.upper()}:**\n{content_data}\n\n"
        
        # Compilar MCPs utilizados
        all_mcps_used = []
        if core_mcp['activated']:
            all_mcps_used.append('core-mcp-prompt-understanding')
        if docs_mcp['activated']:
            all_mcps_used.append('aws-docs-mcp')
        all_mcps_used.extend(generation_mcps['activated_mcps'])
        
        # Response data
        response_data = {
            'content': response_content,
            'projectState': project_state,
            'mcpActivated': len(all_mcps_used) > 0,
            'mcpStatus': f'corrected_phase_{1 if not generation_readiness["ready_for_generation"] else 3}',
            'mcpUsed': all_mcps_used,
            'mcpBreakdown': {
                'core_mcp': core_mcp,
                'docs_mcp': docs_mcp,
                'generation_readiness': generation_readiness,
                'generation_mcps': generation_mcps
            },
            's3Info': {
                'bucket': DOCUMENTS_BUCKET,
                'folder': generation_mcps.get('s3_folder'),
                'documents_saved': generation_mcps.get('documents_saved', [])
            } if generation_mcps.get('s3_folder') else None,
            'modelUsed': bedrock_response.get('modelUsed', model_id),
            'usage': bedrock_response.get('usage', {}),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ CORRECTED Response: Core={core_mcp['activated']}, Docs={docs_mcp['activated']}, Generation={generation_readiness['ready_for_generation']}")
        return create_success_response(response_data)
        
    except Exception as e:
        logger.error(f"Unexpected error in lambda_handler: {str(e)}", exc_info=True)
        return create_error_response(500, f'Internal server error: {str(e)}')
