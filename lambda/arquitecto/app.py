import json
import boto3
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any
import logging

# Import MCP Orchestrator
from mcp_orchestrator import MCPOrchestrator

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
    """Process chat with arquitecto mode - Amazon Q Developer CLI Style"""
    
    try:
        messages = body.get('messages', [])
        model_id = body.get('modelId', 'anthropic.claude-3-haiku-20240307-v1:0')
        project_id = body.get('projectId', str(uuid.uuid4()))
        user_id = body.get('userId', 'anonymous')
        
        # Handle both projectInfo (Lambda format) and currentProject (Frontend format)
        project_info = body.get('projectInfo', body.get('currentProject', {}))
        project_phase = body.get('projectPhase', 'inicio')
        
        # Ensure project_info is a dict
        if not isinstance(project_info, dict):
            project_info = {}
        
        logger.info(f"🏗️ ARQUITECTO V3 - Processing chat with MCP Orchestrator")
        logger.info(f"Model ID: {model_id}")
        logger.info(f"Messages count: {len(messages)}")
        logger.info(f"Project info: {project_info}")
        logger.info(f"Project phase: {project_phase}")
        logger.info(f"Request body keys: {list(body.keys())}")
        
        if not messages:
            return create_response(400, {'error': 'Messages are required'})
        
        # Initialize MCP Orchestrator with bucket name
        mcp_orchestrator = MCPOrchestrator(DOCUMENTS_BUCKET)
        
        # System prompt for arquitecto mode
        system_prompt = get_arquitecto_system_prompt()
        
        # Prepare the prompt for Bedrock
        prompt_data = prepare_prompt(model_id, system_prompt, messages, project_info, 0)
        
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
        
        # 🎯 AMAZON Q DEVELOPER CLI STYLE MCP PROCESSING
        mcps_executed = []
        artifacts_generated = []
        
        try:
            logger.info("🚀 Activating MCP Orchestrator...")
            
            # Analyze conversation intent
            intent_analysis = mcp_orchestrator.analyze_conversation_intent(messages, ai_response)
            logger.info(f"Intent analysis: {intent_analysis}")
            
            # Execute MCP workflow based on intent
            project_context = {
                'project_id': project_id,
                'user_id': user_id,
                'project_name': project_info.get('name', ''),
                'project_phase': project_phase,
                **project_info
            }
            
            mcp_results = mcp_orchestrator.execute_mcp_workflow(
                intent_analysis, messages, ai_response, project_context
            )
            
            # Use enhanced response from MCP processing
            if mcp_results.get('success') and mcp_results.get('enhanced_response'):
                ai_response = mcp_results['enhanced_response']
                
            # Update project info with MCP context
            project_info.update(mcp_results.get('context_updates', {}))
            
            # Log MCP execution results
            mcps_executed = mcp_results.get('mcps_executed', [])
            artifacts_generated = mcp_results.get('artifacts_generated', [])
            
            logger.info(f"🔧 MCPs executed: {mcps_executed}")
            logger.info(f"📄 Artifacts generated: {len(artifacts_generated)}")
            
        except Exception as mcp_error:
            logger.error(f"MCP processing error: {str(mcp_error)}")
            # Don't fail the entire request if MCP processing fails
            mcps_executed = []
            artifacts_generated = []
            # Add a note to the response about MCP processing
            ai_response += "\n\n⚠️ *Nota: Algunas funciones avanzadas no están disponibles temporalmente.*"
        
        # Create response
        response_data = {
            'response': ai_response,
            'projectId': project_id,
            'userId': user_id,
            'timestamp': datetime.now().isoformat(),
            'model': model_id,
            'mcpUsed': mcps_executed,  # Frontend expects 'mcpUsed'
            'usage': {
                'inputTokens': len(str(messages)),
                'outputTokens': len(ai_response)
            },
            'projectUpdate': project_info,  # Frontend expects 'projectUpdate'
            'projectPhase': project_phase,  # Frontend expects 'projectPhase'
            'mcps_executed': mcps_executed,
            'artifacts_generated': artifacts_generated,
            'project_info': project_info
        }
        
        return create_response(200, response_data)
        
    except Exception as e:
        logger.error(f"Error in process_arquitecto_chat: {str(e)}")
        return create_response(500, {
            'error': 'Error processing chat',
            'details': str(e)
        })

def get_arquitecto_system_prompt() -> str:
    """Get system prompt for arquitecto mode - Amazon Q Developer CLI Style"""
    bucket_name = DOCUMENTS_BUCKET or 'aws-propuestas-v3-documents-prod'
    
    return f"""Actua como Amazon Q Developer CLI para AWS - Arquitecto de Soluciones Senior con 15+ años de experiencia.

🎯 MISION: Ser el asistente de arquitectura AWS más inteligente y completo, similar a Amazon Q Developer CLI, con capacidades de:
- Análisis inteligente de requerimientos
- Activación automática de herramientas especializadas (MCPs)
- Generación de artefactos profesionales
- Guía experta en AWS Well-Architected Framework

🧠 INTELIGENCIA ADAPTATIVA:
- Analiza el contexto completo de la conversación
- Detecta automáticamente el tipo de proyecto y necesidades
- Activa las herramientas correctas en el momento preciso
- Proporciona respuestas contextuales y personalizadas

📋 FLUJO MAESTRO INTELIGENTE:

1. **ANÁLISIS INICIAL** (Primera interacción):
   - Saluda profesionalmente como arquitecto AWS Senior
   - Pregunta: "¿Cuál es el nombre del proyecto que vamos a arquitectar?"
   - Analiza cualquier información adicional proporcionada

2. **CLASIFICACIÓN INTELIGENTE** (Segunda interacción):
   - Determina automáticamente si es:
     * **Servicio Rápido**: Implementación específica (EC2, S3, RDS, VPC, etc.)
     * **Solución Integral**: Arquitectura completa (migración, modernización, nueva aplicación)
   - Pregunta de confirmación si no está claro

3. **RECOPILACIÓN ADAPTATIVA**:
   
   **Para Servicios Rápidos:**
   - Identifica el servicio específico requerido
   - Hace SOLO las preguntas esenciales para ese servicio
   - Proporciona configuraciones optimizadas y best practices
   
   **Para Soluciones Integrales:**
   - Entrevista estructurada pero natural
   - Preguntas contextuales basadas en el tipo de solución
   - Análisis de requerimientos técnicos y de negocio

4. **GENERACIÓN AUTOMÁTICA** (Cuando detecte información suficiente):
   - Activa automáticamente las herramientas especializadas
   - Genera artefactos profesionales completos
   - Proporciona documentación ejecutiva y técnica

🛠️ HERRAMIENTAS ESPECIALIZADAS (MCPs) DISPONIBLES:
- **Diagramas**: Generación automática de arquitecturas visuales
- **Documentación**: Creación de propuestas ejecutivas y técnicas
- **CloudFormation**: Templates de infraestructura como código
- **Costos**: Análisis detallado de precios y optimización
- **Serverless**: Patrones y mejores prácticas Lambda/SAM
- **Frontend**: Guía para interfaces y experiencia de usuario
- **Seguridad**: Análisis IAM y configuraciones de seguridad

🎨 EXPERIENCIA DE USUARIO:
- Conversación natural y profesional
- Respuestas contextuales y personalizadas
- Activación transparente de herramientas
- Feedback continuo sobre el progreso
- Entrega de valor en cada interacción

📊 CALIDAD PROFESIONAL:
- Aplica AWS Well-Architected Framework
- Considera costos, seguridad, escalabilidad y disponibilidad
- Proporciona justificación técnica para decisiones
- Genera documentación lista para stakeholders
- Incluye métricas y monitoreo recomendados

🔧 REGLAS DE OPERACIÓN:
- Una pregunta clara a la vez
- Si la respuesta es ambigua, solicita clarificación
- NO generes documentos hasta tener información suficiente
- Activa herramientas automáticamente cuando sea apropiado
- Mantén el contexto del proyecto a lo largo de la conversación
- SIN acentos en archivos generados (compatibilidad)

💾 SISTEMA DE ARCHIVOS:
- Bucket S3 del sistema: {bucket_name}
- Organización automática por proyecto
- Versionado y backup automático
- Acceso desde sección "Proyectos"

🎯 OBJETIVO FINAL:
Proporcionar una experiencia similar a Amazon Q Developer CLI, donde cada interacción agrega valor, las herramientas se activan inteligentemente, y el resultado final es una propuesta AWS profesional y completa.

Recuerda: Eres el arquitecto AWS más avanzado disponible. Actúa con confianza, precisión técnica y enfoque en resultados ejecutivos."""

def prepare_prompt(model_id: str, system_prompt: str, messages: List[Dict], 
                  project_info: Dict, current_step: int) -> Dict:
    """Prepare prompt based on model type with correct Bedrock format"""
    
    if 'anthropic' in model_id:
        # Ensure messages have correct format for Anthropic
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "role": msg.get('role', 'user'),
                "content": msg.get('content', '')
            })
        
        return {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "temperature": 0.3,
            "system": system_prompt,
            "messages": formatted_messages
        }
    else:
        # For other models like Titan
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
