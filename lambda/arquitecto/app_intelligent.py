"""
AWS Propuestas v3 - Arquitecto Lambda with Intelligent MCP Orchestration
Amazon Q Developer CLI Style Implementation
"""

import json
import boto3
import os
import uuid
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Import our custom modules
from cors_handler import handle_preflight_request, create_response, create_error_response, create_success_response
from intelligent_mcp_orchestrator import IntelligentMCPOrchestrator

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

# Arquitecto Master Prompt - Enhanced for intelligent MCP activation
ARQUITECTO_MASTER_PROMPT = """Actua como arquitecto de soluciones AWS y consultor experto.

IMPORTANTE: Tu objetivo es dimensionar, documentar y entregar una solucion profesional en AWS, siguiendo mejores practicas y generando todos los archivos necesarios para una propuesta ejecutiva.

REGLAS FUNDAMENTALES:
- No uses acentos ni caracteres especiales en ningun texto, archivo, script ni documento
- Todos los archivos Word seran funcionales y compatibles: solo texto plano, sin imagenes, sin tablas complejas, ni formato avanzado
- Solo genera scripts CloudFormation como entregable de automatizacion

PROCESO GUIADO INTELIGENTE:

1. INICIO: Pregunta "Cual es el nombre del proyecto?"

2. TIPO: Pregunta si el proyecto es:
   - Solucion integral (migracion, aplicacion nueva, modernizacion, analitica, seguridad, IA, IoT, data lake, networking, DRP, VDI, integracion, etc.)
   - Servicio rapido especifico (EC2, RDS, SES, VPN, ELB, S3, VPC, CloudFront, SSO, backup, etc.)

3. RECOPILACION INTELIGENTE:
   - Para SERVICIO RAPIDO: Haz 3-5 preguntas especificas y tecnicas
   - Para SOLUCION INTEGRAL: Haz 8-12 preguntas detalladas sobre arquitectura, requisitos, integraciones

4. ACTIVACION AUTOMATICA:
   Cuando tengas suficiente contexto (nombre, tipo, servicios, requisitos basicos), el sistema activara automaticamente los MCPs especializados para generar:
   - Tabla de actividades (CSV)
   - Script CloudFormation
   - Diagramas de arquitectura (SVG/PNG)
   - Documento tecnico (Word/texto plano)
   - Analisis de costos (CSV)
   - Guia calculadora AWS

5. ENTREGA:
   - Pregunta bucket S3 para subir archivos
   - Sube carpeta con nombre del proyecto
   - Pregunta ajustes finales

ACTIVACION DE MCPs:
El sistema cuenta con MCPs especializados que se activan automaticamente:
- Core MCP: Analisis de contexto y comprension
- AWS Docs MCP: Documentacion oficial y mejores practicas
- Pricing MCP: Calculos de costos reales
- CloudFormation MCP: Templates de infraestructura
- Diagram MCP: Diagramas de arquitectura

NO menciones explicitamente los MCPs al usuario. Simplemente di que estas "generando los documentos" cuando el sistema los active automaticamente."""


def lambda_handler(event, context):
    """Main Lambda handler with intelligent MCP orchestration and CORS support"""
    
    try:
        # Handle CORS preflight requests
        if event.get('httpMethod') == 'OPTIONS':
            return handle_preflight_request()
        
        # Parse request
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        messages = body.get('messages', [])
        model_id = body.get('modelId', 'anthropic.claude-3-5-sonnet-20241022-v2:0')
        project_state = body.get('projectState', {'phase': 'inicio', 'data': {}})
        
        if not messages:
            return create_error_response(400, 'No messages provided')
        
        logger.info(f"Processing {len(messages)} messages for project in phase: {project_state.get('phase')}")
        
        # Prepare conversation for Bedrock
        conversation = prepare_conversation(messages, project_state)
        
        # Call Bedrock model
        bedrock_response = call_bedrock_model(model_id, conversation)
        
        if 'error' in bedrock_response:
            return create_error_response(500, bedrock_response['error'])
        
        response_content = bedrock_response['content']
        
        # INTELLIGENT MCP ORCHESTRATION
        orchestrator = IntelligentMCPOrchestrator()
        
        try:
            # Run intelligent MCP activation
            activation_result = asyncio.run(
                orchestrator.intelligent_mcp_activation(
                    messages=messages,
                    project_state=project_state,
                    model_response=response_content
                )
            )
            
            # Process activation result
            mcp_used = []
            project_update = None
            
            if activation_result['status'] == 'SUCCESS':
                logger.info("🚀 Documents generated successfully via intelligent MCP orchestration")
                
                # Update response with generated documents
                response_content += f"\n\n✅ Documentos generados exitosamente:\n"
                for doc in activation_result['documents_generated']:
                    response_content += f"- {doc}\n"
                
                mcp_used = activation_result['total_mcps_used']
                
                # Update project phase
                project_update = {
                    'phase': 'entrega',
                    'data': {
                        **project_state.get('data', {}),
                        'documents_generated': activation_result['documents_generated'],
                        'mcp_execution_log': activation_result['mcp_execution_log']
                    }
                }
                
                response_content += f"\n\nPor favor, proporciona el nombre del bucket S3 donde deseas subir los archivos."
            
            elif activation_result['status'] == 'NEEDS_MORE_CONTEXT':
                logger.info("📝 Requesting more context from user")
                
                response_content += f"\n\nNecesito mas informacion para generar una propuesta completa:\n"
                for question in activation_result['suggested_questions']:
                    response_content += f"- {question}\n"
                
                mcp_used = ['awslabscore_mcp_server___prompt_understanding']
            
            elif activation_result['status'] == 'CLARIFICATION_NEEDED':
                logger.info("❓ Clarification needed from user")
                
                response_content += f"\n\nPara continuar, necesito que me aclares:\n"
                for question in activation_result['suggested_questions']:
                    response_content += f"- {question}\n"
                
                mcp_used = ['awslabscore_mcp_server___prompt_understanding']
            
            elif activation_result['status'] == 'ERROR':
                logger.error(f"MCP orchestration error: {activation_result['error']}")
                # Continue with basic response, don't fail the entire request
                mcp_used = ['awslabscore_mcp_server___prompt_understanding']
            
            else:
                # CONTINUE_CONVERSATION
                mcp_used = ['awslabscore_mcp_server___prompt_understanding']
        
        finally:
            # Always close the orchestrator session
            try:
                asyncio.run(orchestrator.close())
            except:
                pass
        
        # Prepare final response
        response_data = {
            'response': response_content,
            'usage': bedrock_response.get('usage', {}),
            'mcpUsed': mcp_used
        }
        
        if project_update:
            response_data['projectUpdate'] = project_update
        
        logger.info(f"Response prepared with {len(mcp_used)} MCPs used")
        
        return create_success_response(response_data)
        
    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}")
        return create_error_response(500, f'Internal server error: {str(e)}')


def prepare_conversation(messages: List[Dict], project_state: Dict) -> List[Dict]:
    """Prepare conversation for Bedrock with enhanced context"""
    
    conversation = []
    
    # Add system prompt
    conversation.append({
        "role": "user",
        "content": ARQUITECTO_MASTER_PROMPT
    })
    
    conversation.append({
        "role": "assistant",
        "content": "Entendido. Soy tu Arquitecto de Soluciones AWS con capacidades avanzadas de generacion automatica de documentos. Vamos a crear una propuesta profesional completa."
    })
    
    # Add project context if available
    if project_state.get('data'):
        context_info = f"Contexto del proyecto: {json.dumps(project_state['data'], indent=2)}"
        conversation.append({
            "role": "user",
            "content": f"Contexto actual: {context_info}"
        })
        
        conversation.append({
            "role": "assistant",
            "content": "Contexto registrado. Continuando con el proceso guiado."
        })
    
    # Add conversation history
    for msg in messages:
        conversation.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    return conversation


def call_bedrock_model(model_id: str, messages: List[Dict]) -> Dict[str, Any]:
    """Call Bedrock model with conversation"""
    
    try:
        # Prepare the prompt based on model type
        if 'anthropic' in model_id.lower():
            # Claude format
            system_message = messages[0]['content'] if messages and messages[0]['role'] == 'user' else ""
            conversation_messages = messages[1:] if len(messages) > 1 else messages
            
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,
                "system": system_message,
                "messages": conversation_messages,
                "temperature": 0.7
            }
        else:
            # Other models format
            prompt = "\n\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
            body = {
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 4000,
                    "temperature": 0.7
                }
            }
        
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        
        if 'anthropic' in model_id.lower():
            content = response_body['content'][0]['text']
            usage = {
                'inputTokens': response_body.get('usage', {}).get('input_tokens', 0),
                'outputTokens': response_body.get('usage', {}).get('output_tokens', 0)
            }
        else:
            content = response_body.get('results', [{}])[0].get('outputText', '')
            usage = {
                'inputTokens': response_body.get('inputTextTokenCount', 0),
                'outputTokens': response_body.get('results', [{}])[0].get('tokenCount', 0)
            }
        
        return {
            'content': content,
            'usage': usage
        }
        
    except Exception as e:
        logger.error(f"Bedrock model call error: {str(e)}")
        return {'error': f'Model call failed: {str(e)}'}
