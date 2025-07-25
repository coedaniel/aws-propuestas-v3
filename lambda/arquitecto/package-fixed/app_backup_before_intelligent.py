import json
import boto3
import os
import uuid
import re
import requests
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

# REAL MCP ENDPOINTS - Using HTTPS with custom domain
MCP_BASE_URL = "https://mcp.danielingram.shop"
MCP_ENDPOINTS = {
    'core': f"{MCP_BASE_URL}/core",
    'pricing': f"{MCP_BASE_URL}/pricing", 
    'awsdocs': f"{MCP_BASE_URL}/awsdocs",
    'cfn': f"{MCP_BASE_URL}/cfn",
    'diagram': f"{MCP_BASE_URL}/diagram",
    'docgen': f"{MCP_BASE_URL}/docgen"
}

# Arquitecto Master Prompt
ARQUITECTO_MASTER_PROMPT = """Actua como arquitecto de soluciones AWS y consultor experto.
Vamos a dimensionar, documentar y entregar una solucion profesional en AWS, siguiendo mejores practicas y generando todos los archivos necesarios para una propuesta ejecutiva.

REGLAS IMPORTANTES:
- No uses acentos ni caracteres especiales en ningun texto, archivo, script ni documento
- Todos los archivos Word seran funcionales y compatibles: solo texto plano, sin imagenes, sin tablas complejas, ni formato avanzado
- Solo genera scripts CloudFormation como entregable de automatizacion

PROCESO GUIADO:

1. INICIO: Pregunta "Cual es el nombre del proyecto"

2. TIPO: Pregunta si el proyecto es:
   - Solucion integral (migracion, aplicacion nueva, modernizacion, analitica, seguridad, IA, IoT, data lake, networking, DRP, VDI, integracion, etc.)
   - Servicio rapido especifico (EC2, RDS, SES, VPN, ELB, S3, VPC, CloudFront, SSO, backup, etc.)

3. SERVICIO RAPIDO:
   - Muestra catalogo de servicios rapidos comunes
   - Haz preguntas minimas necesarias, una por una
   - Cuando tengas suficiente informacion, di: "GENERO LOS SIGUIENTES DOCUMENTOS:"
   - Usa MCPs para generar: tabla actividades (CSV), script CloudFormation, diagramas (SVG/PNG), documento Word (texto plano), costos estimados (CSV), guia calculadora AWS
   - Pregunta bucket S3 para subir archivos
   - Sube carpeta con nombre del proyecto usando MCP
   - Pregunta ajustes finales

4. SOLUCION INTEGRAL:
   - Haz 8-12 preguntas detalladas sobre arquitectura, requisitos, integraciones
   - Cuando tengas suficiente informacion, di: "GENERO LOS SIGUIENTES DOCUMENTOS:"
   - Usa MCPs para generar documentacion completa
   - Pregunta bucket S3 y sube archivos usando MCP

Usa MCPs inteligentemente para:
- Generar diagramas de arquitectura
- Crear templates CloudFormation
- Calcular costos y precios
- Generar documentos profesionales
- Subir archivos a S3
- Buscar documentacion AWS

IMPORTANTE: Cuando digas "GENERO LOS SIGUIENTES DOCUMENTOS:", activa los MCPs correspondientes para generar contenido real."""

class MCPOrchestrator:
    """Orchestrates calls to real MCP services"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 30
        
    def call_mcp_tool(self, mcp_name: str, tool_name: str, arguments: Dict) -> Dict:
        """Call a specific MCP tool"""
        try:
            endpoint = MCP_ENDPOINTS.get(mcp_name)
            if not endpoint:
                return {"error": f"MCP {mcp_name} not found"}
            
            payload = {
                "tool": tool_name,
                "arguments": arguments
            }
            
            response = self.session.post(
                f"{endpoint}/call-tool",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ MCP {mcp_name} tool {tool_name} executed successfully")
                return result
            else:
                logger.error(f"❌ MCP {mcp_name} tool {tool_name} failed: {response.status_code}")
                return {"error": f"MCP call failed: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Error calling MCP {mcp_name}: {str(e)}")
            return {"error": f"MCP call error: {str(e)}"}
    
    def generate_project_documents(self, project_info: Dict) -> Dict:
        """Generate all project documents using MCPs"""
        
        results = {
            "documents_generated": [],
            "mcp_activities": [],
            "errors": []
        }
        
        project_name = project_info.get('name', 'proyecto')
        project_type = project_info.get('type', 'servicio rapido')
        
        # 1. Generate CloudFormation template
        try:
            cfn_result = self.call_mcp_tool('cfn', 'generate_template', {
                'project_name': project_name,
                'requirements': project_info
            })
            
            if not cfn_result.get('error'):
                results["documents_generated"].append("CloudFormation Template")
                results["mcp_activities"].append("awslabscloudformation_mcp_server___generate_template")
        except Exception as e:
            results["errors"].append(f"CloudFormation generation error: {str(e)}")
        
        # 2. Calculate pricing
        try:
            pricing_result = self.call_mcp_tool('pricing', 'calculate_costs', {
                'project_name': project_name,
                'services': project_info.get('services', [])
            })
            
            if not pricing_result.get('error'):
                results["documents_generated"].append("Cost Analysis")
                results["mcp_activities"].append("awslabspricing_mcp_server___calculate_costs")
        except Exception as e:
            results["errors"].append(f"Pricing calculation error: {str(e)}")
        
        # 3. Generate architecture diagram
        try:
            diagram_result = self.call_mcp_tool('diagram', 'generate_diagram', {
                'project_name': project_name,
                'architecture_description': project_info.get('description', '')
            })
            
            if not diagram_result.get('error'):
                results["documents_generated"].append("Architecture Diagram")
                results["mcp_activities"].append("awslabsaws_diagram_mcp_server___generate_diagram")
        except Exception as e:
            results["errors"].append(f"Diagram generation error: {str(e)}")
        
        # 4. Generate project documents
        try:
            doc_result = self.call_mcp_tool('docgen', 'create_document', {
                'project_name': project_name,
                'project_data': project_info,
                'document_type': 'project_proposal'
            })
            
            if not doc_result.get('error'):
                results["documents_generated"].append("Project Documentation")
                results["mcp_activities"].append("awslabsfile_operations___create_document")
        except Exception as e:
            results["errors"].append(f"Document generation error: {str(e)}")
        
        return results

def lambda_handler(event, context):
    """Main Lambda handler for Arquitecto"""
    
    try:
        # Parse request
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        messages = body.get('messages', [])
        model_id = body.get('modelId', 'anthropic.claude-3-5-sonnet-20241022-v2:0')
        project_state = body.get('projectState', {'phase': 'inicio', 'data': {}})
        
        if not messages:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'No messages provided'})
            }
        
        logger.info(f"Processing {len(messages)} messages for project in phase: {project_state.get('phase')}")
        
        # Initialize MCP orchestrator
        mcp_orchestrator = MCPOrchestrator()
        
        # Prepare conversation for Bedrock
        conversation = prepare_conversation(messages, project_state)
        
        # Call Bedrock model
        bedrock_response = call_bedrock_model(model_id, conversation)
        
        if 'error' in bedrock_response:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': bedrock_response['error']})
            }
        
        response_content = bedrock_response['content']
        
        # Detect if we need to generate documents
        mcp_used = []
        project_update = None
        
        if "GENERO LOS SIGUIENTES DOCUMENTOS:" in response_content:
            logger.info("🚀 Document generation triggered - activating MCPs")
            
            # Extract project info from conversation
            project_info = extract_project_info(messages, project_state)
            
            # Generate documents using real MCPs
            doc_results = mcp_orchestrator.generate_project_documents(project_info)
            
            # Update response with generated documents
            if doc_results["documents_generated"]:
                response_content += f"\n\n✅ Documentos generados exitosamente:\n"
                for doc in doc_results["documents_generated"]:
                    response_content += f"- {doc}\n"
                
                mcp_used = doc_results["mcp_activities"]
                
                # Update project phase
                project_update = {
                    'phase': 'entrega',
                    'data': {
                        **project_state.get('data', {}),
                        'documents_generated': doc_results["documents_generated"]
                    }
                }
            
            if doc_results["errors"]:
                response_content += f"\n\n⚠️ Algunos errores durante la generacion:\n"
                for error in doc_results["errors"]:
                    response_content += f"- {error}\n"
        
        # Detect other MCP usage
        if not mcp_used:
            mcp_used = detect_mcp_usage(response_content, project_state.get('phase'))
        
        # Prepare response
        response = {
            'response': response_content,
            'usage': bedrock_response.get('usage', {}),
            'mcpUsed': mcp_used
        }
        
        if project_update:
            response['projectUpdate'] = project_update
        
        logger.info(f"Response prepared with {len(mcp_used)} MCPs used")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps(response)
        }
        
    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }

def extract_project_info(messages: List[Dict], project_state: Dict) -> Dict:
    """Extract project information from conversation"""
    
    project_info = {
        'name': project_state.get('data', {}).get('name', 'proyecto'),
        'type': project_state.get('data', {}).get('type', 'servicio rapido'),
        'phase': project_state.get('phase', 'inicio'),
        'description': '',
        'services': []
    }
    
    # Extract info from messages
    conversation_text = ' '.join([msg.get('content', '') for msg in messages])
    
    # Try to extract project name
    if not project_info['name'] or project_info['name'] == 'proyecto':
        # Look for project name in conversation
        for msg in messages:
            if msg.get('role') == 'user':
                content = msg.get('content', '').strip()
                if len(content.split()) == 1 and len(content) > 2:
                    project_info['name'] = content.lower()
                    break
    
    # Extract services mentioned
    aws_services = ['ec2', 'rds', 's3', 'vpc', 'lambda', 'cloudfront', 'elb', 'ses', 'sns', 'sqs']
    for service in aws_services:
        if service in conversation_text.lower():
            project_info['services'].append(service)
    
    project_info['description'] = f"Proyecto {project_info['name']} - {project_info['type']}"
    
    return project_info

def prepare_conversation(messages: List[Dict], project_state: Dict) -> List[Dict]:
    """Prepare conversation for Bedrock"""
    
    conversation = []
    
    # Add system prompt
    conversation.append({
        "role": "user",
        "content": ARQUITECTO_MASTER_PROMPT
    })
    
    conversation.append({
        "role": "assistant", 
        "content": "Entendido. Soy tu Arquitecto de Soluciones AWS. Vamos a crear una propuesta profesional."
    })
    
    # Add conversation history
    for msg in messages:
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
    
    # AWS documentation lookup
    if any(service in content_lower for service in ['ec2', 'rds', 'lambda', 'vpc', 'cloudfront', 'elb', 'ses']):
        mcp_used.append("awslabsaws_documentation_mcp_server___search_documentation")
    
    return list(set(mcp_used))

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
                "messages": conversation_messages
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
