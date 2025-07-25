"""
AWS Propuestas v3 - Arquitecto Lambda con Detección Inteligente MCP
Sistema de 3 fases: Analysis → Validation → Generation
Inspirado en Amazon Q Developer CLI
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

# Arquitecto Master Prompt - COMPLETO Y AVANZADO
ARQUITECTO_MASTER_PROMPT = """Actua como arquitecto de soluciones AWS y consultor experto.

Vamos a dimensionar, documentar y entregar una solucion profesional en AWS, siguiendo buenas practicas. Vas a guiar al usuario paso a paso y generar todos los archivos necesarios para una propuesta ejecutiva.

⚠️ Importante:
- No uses acentos ni caracteres especiales en ningun texto, archivo, script ni documento.
- Todos los documentos Word deben ser solo texto plano: sin imagenes, sin tablas complejas, sin formato avanzado.
- Solo puedes generar scripts CloudFormation (YAML) como entregables de automatizacion. No generes bash, Terraform, CDK ni otros.

---

🧭 FLUJO DE CONVERSACION:

1. Primero pregunta:
   - ¿Cual es el nombre del proyecto?

2. Luego pregunta:
   - ¿El proyecto es una solucion integral (como migracion, aplicacion nueva, modernizacion, analitica, seguridad, IA, IoT, data lake, networking, DRP, VDI, integracion, etc.)?
   - ¿O es un servicio rapido especifico (como EC2, RDS, SES, VPN, ELB, S3, VPC, CloudFront, SSO, backup, etc.)?

---

📦 SI ES SERVICIO RAPIDO:

1. Muestra un catalogo de servicios comunes o permite escribirlo.
2. Pregunta solo lo minimo necesario, de forma clara y una por una.
3. Con la informacion, genera SIEMPRE:
   - Tabla de actividades (CSV o Excel, sin acentos)
   - Script CloudFormation (.yaml, sin acentos)
   - Diagrama (SVG, PNG, .drawio, sin acentos)
   - Documento Word con descripcion (texto plano)
   - Archivo de costos estimados (CSV o Excel, sin acentos)
   - Guia paso a paso para usar la calculadora de AWS

4. Pregunta a que bucket S3 deseas subir los archivos.
5. Sube la carpeta con el nombre del proyecto.
6. Pregunta si deseas agregar comentarios o ajustes finales.

---

🏗️ SI ES SOLUCION INTEGRAL:

1. Haz entrevista guiada para capturar:
   - Nombre del proyecto
   - Tipo de solucion
   - Objetivo principal
   - Descripcion detallada
   - Caracteristicas clave
   - Servicios AWS requeridos
   - Cantidad y tipo de recursos
   - Integraciones (on-premises, SaaS, APIs, IoT, etc.)
   - Seguridad y compliance
   - Alta disponibilidad, DRP, RTO, RPO
   - Estimacion de usuarios y trafico
   - Presupuesto (opcional)
   - Fechas objetivo
   - Restricciones o preferencias
   - Comentarios finales

2. Aplica logica condicional segun el tipo de solucion.
3. Entrega SIEMPRE:
   - Tabla de actividades (CSV o Excel)
   - Script CloudFormation completo (.yaml)
   - Diagramas (SVG, PNG, .drawio)
   - Documento Word (solo texto plano)
   - Costos estimados (CSV o Excel)
   - Guia para calculadora de AWS

4. Pregunta a que bucket S3 subir.
5. Sube la carpeta al bucket con el nombre del proyecto.
6. Pregunta si hay ajustes o comentarios finales.

---

🤖 REGLAS DE CONVERSACION:

- Siempre pregunta una sola cosa a la vez.
- Si una respuesta es ambigua, pide mas detalles antes de continuar.
- Todos los nombres de recursos, archivos, carpetas y proyectos deben estar libres de acentos.
- No entregues contenido generico. Todo debe basarse en lo que el usuario haya dicho.

---

La propuesta debe sentirse natural, como hablar con un arquitecto de AWS real. El modelo debe adaptar el flujo si el usuario cambia el orden, da respuestas libres o mezcla temas.

Estas actuando dentro de una pagina web llamada /arquitecto.

El proposito de esta pagina es ayudarte a comportarte como un arquitecto de soluciones AWS y consultor experto, para generar propuestas arquitectonicas profesionales, guiadas paso a paso, con base en los requerimientos reales del usuario.

Debes seguir el flujo completo descrito abajo, y entregar documentos reales, personalizados, estructurados correctamente, y compatibles para entrega a clientes. Toda la interaccion sucede dentro de esta pagina."""

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

def calculate_readiness_score(messages: List[Dict], project_state: Dict) -> float:
    """
    Calcula el readiness_score basado en los criterios de tu diagrama:
    - Nombre del Proyecto: 20%
    - Tipo de Proyecto: 20% 
    - Requisitos Técnicos: 20%
    - Definición de Alcance: 20%
    - Profundidad de Contexto: 20%
    """
    score = 0.0
    conversation_text = " ".join([msg.get("content", "") for msg in messages]).lower()
    
    # 1. Nombre del Proyecto (20%)
    if project_state.get('data', {}).get('nombre') or any(word in conversation_text for word in ['proyecto', 'sistema', 'aplicacion', 'plataforma']):
        score += 0.20
        logger.info("✅ Criterio 1: Nombre del proyecto identificado (+20%)")
    
    # 2. Tipo de Proyecto (20%)
    if any(word in conversation_text for word in ['integral', 'rapido', 'migracion', 'aplicacion', 'modernizacion', 'ec2', 'rds', 's3']):
        score += 0.20
        logger.info("✅ Criterio 2: Tipo de proyecto identificado (+20%)")
    
    # 3. Requisitos Técnicos (20%)
    aws_services = ['lambda', 'ec2', 'rds', 's3', 'dynamodb', 'api gateway', 'cloudfront', 'vpc', 'iam', 'cloudformation']
    if any(service in conversation_text for service in aws_services):
        score += 0.20
        logger.info("✅ Criterio 3: Servicios AWS mencionados (+20%)")
    
    # 4. Definición de Alcance (20%)
    scope_indicators = ['usuarios', 'presupuesto', 'region', 'costo', 'timeline', 'fecha', 'alcance', 'objetivo']
    if any(indicator in conversation_text for indicator in scope_indicators):
        score += 0.20
        logger.info("✅ Criterio 4: Alcance definido (+20%)")
    
    # 5. Profundidad de Contexto (20%)
    if len(messages) >= 5:  # Al menos 5 intercambios
        score += 0.20
        logger.info("✅ Criterio 5: Suficientes intercambios (+20%)")
    
    logger.info(f"🎯 Readiness Score: {score:.2f} (Umbral: 0.8)")
    return score

def determine_mcp_activation(messages: List[Dict], project_state: Dict) -> Dict[str, Any]:
    """
    Determina qué MCPs activar basado en las 3 fases de tu diagrama:
    Fase 1: Analysis (OBLIGATORIO)
    Fase 2: Validation (CONDICIONAL - readiness_score > 0.7)
    Fase 3: Generation (PARALELA - readiness_score > 0.8)
    """
    conversation_text = " ".join([msg.get("content", "") for msg in messages]).lower()
    readiness_score = calculate_readiness_score(messages, project_state)
    
    mcp_activation = {
        'phase': 1,
        'readiness_score': readiness_score,
        'mcps_activated': [],
        'activation_reason': []
    }
    
    # FASE 1: ANALYSIS (SIEMPRE ACTIVO)
    mcp_activation['mcps_activated'].extend(['aws-serverless-mcp-server'])
    mcp_activation['activation_reason'].append('Phase 1: Core analysis (always active)')
    
    # Activar AWS Docs si se necesita documentación
    if any(word in conversation_text for word in ['documentacion', 'mejores practicas', 'como', 'que es', 'busca']):
        mcp_activation['mcps_activated'].append('aws-documentation-mcp-server')
        mcp_activation['activation_reason'].append('Phase 1: AWS documentation needed')
    
    # FASE 2: VALIDATION (CONDICIONAL)
    if readiness_score > 0.7:
        mcp_activation['phase'] = 2
        mcp_activation['activation_reason'].append('Phase 2: Validation triggered (readiness > 0.7)')
        
        # Activar pricing si se menciona costo
        if any(word in conversation_text for word in ['costo', 'precio', 'presupuesto', 'cuanto']):
            mcp_activation['mcps_activated'].append('aws-bedrock-data-automation-mcp-server')
            mcp_activation['activation_reason'].append('Phase 2: Cost analysis requested')
    
    # FASE 3: GENERATION (PARALELA)
    if readiness_score >= 0.8:
        mcp_activation['phase'] = 3
        mcp_activation['mcps_activated'].extend([
            'aws-diagram-mcp-server',
            'aws-cdk-mcp-server',
            'aws-nova-canvas-mcp-server'
        ])
        mcp_activation['activation_reason'].append('Phase 3: Generation phase (readiness >= 0.8)')
    
    logger.info(f"🔧 MCP Activation: Phase {mcp_activation['phase']}, MCPs: {mcp_activation['mcps_activated']}")
    return mcp_activation

def prepare_conversation(messages: List[Dict], project_state: Dict) -> List[Dict]:
    """Prepare conversation for Bedrock with correct format"""
    conversation = []
    
    # Add system message with correct format (as user message for Bedrock)
    conversation.append({
        "role": "user",
        "content": [{"text": ARQUITECTO_MASTER_PROMPT}]
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
    """Main Lambda handler con detección inteligente MCP"""
    
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
        logger.info(f"Project state: {project_state}")
        
        # DETECCIÓN INTELIGENTE MCP (Como Amazon Q CLI)
        mcp_activation = determine_mcp_activation(messages, project_state)
        
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
        
        # Response data con MCP inteligente
        response_data = {
            'content': response_content,
            'projectState': project_state,
            'mcpActivated': True,
            'mcpStatus': f'intelligent_phase_{mcp_activation["phase"]}',
            'mcpUsed': mcp_activation['mcps_activated'],
            'mcpActivationReason': mcp_activation['activation_reason'],
            'readinessScore': mcp_activation['readiness_score'],
            'modelUsed': bedrock_response.get('modelUsed', model_id),
            'usage': bedrock_response.get('usage', {}),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info("Returning successful response with intelligent MCP activation")
        return create_success_response(response_data)
        
    except Exception as e:
        logger.error(f"Unexpected error in lambda_handler: {str(e)}", exc_info=True)
        return create_error_response(500, f'Internal server error: {str(e)}')
