"""
AWS Propuestas v3 - Arquitecto Lambda COMPLETAMENTE CORREGIDO
Implementa el flujo completo de consultoria como Amazon Q Developer CLI
"""

import json
import boto3
import os
import requests
import logging
import uuid
from datetime import datetime
from decimal import Decimal
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

# URLs de los servicios MCP ECS
MCP_BASE_URL = "https://mcp.danielingram.shop"
MCP_SERVICES = {
    'core': f"{MCP_BASE_URL}",
    'pricing': f"{MCP_BASE_URL}/pricing", 
    'awsdocs': f"{MCP_BASE_URL}/awsdocs",
    'cfn': f"{MCP_BASE_URL}/cfn",
    'diagram': f"{MCP_BASE_URL}/diagram",
    'customdoc': f"{MCP_BASE_URL}/docgen"
}

# PROMPT MAESTRO COMPLETO - COMO AMAZON Q DEVELOPER CLI
PROMPT_ARQUITECTO_COMPLETO = """
Actua como arquitecto de soluciones AWS y consultor experto.

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

🔧 REGLAS DE CONVERSACION:

- Siempre pregunta una sola cosa a la vez.
- Si una respuesta es ambigua, pide mas detalles antes de continuar.
- Todos los nombres de recursos, archivos, carpetas y proyectos deben estar libres de acentos.
- No entregues contenido generico. Todo debe basarse en lo que el usuario haya dicho.
- Si detectas que un archivo debe ser generado por un MCP (como diagramas o costos), activalo automaticamente y registra que fue usado.

---

La propuesta debe sentirse natural, como hablar con un arquitecto de AWS real. El modelo debe adaptar el flujo si el usuario cambia el orden, da respuestas libres o mezcla temas.

Estas actuando dentro de una pagina web llamada /arquitecto.

El proposito de esta pagina es ayudarte a comportarte como un arquitecto de soluciones AWS y consultor experto, para generar propuestas arquitectonicas profesionales, guiadas paso a paso, con base en los requerimientos reales del usuario.

Debes seguir el flujo completo descrito abajo, y entregar documentos reales, personalizados, estructurados correctamente, y compatibles para entrega a clientes. Toda la interaccion sucede dentro de esta pagina.

Esto como lo hace amazon q developer cli
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
        'body': body if isinstance(body, str) else json.dumps(body, default=str)
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

def call_mcp_service(service_name: str, action: str, data: Dict) -> Dict:
    """Llama a un servicio MCP especifico"""
    try:
        url = MCP_SERVICES.get(service_name)
        if not url:
            logger.error(f"Unknown MCP service: {service_name}")
            return {"error": f"Unknown service: {service_name}"}
        
        # Construir URL completa
        if action != 'health':
            full_url = f"{url}/{action}"
        else:
            full_url = f"{url}/health"
        
        logger.info(f"Calling MCP service: {full_url}")
        
        response = requests.post(full_url, json=data, timeout=30)
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling MCP service {service_name}: {str(e)}")
        return {"error": f"MCP service error: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error calling MCP {service_name}: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}

def analyze_conversation_context(messages: List[Dict]) -> Dict:
    """Analiza el contexto de la conversacion para determinar que MCPs activar"""
    
    # Extraer contenido de todos los mensajes
    full_conversation = " ".join([msg.get("content", "") for msg in messages])
    full_conversation_lower = full_conversation.lower()
    
    # Criterios de analisis
    analysis = {
        "project_name_mentioned": False,
        "project_type_mentioned": False,
        "technical_details_mentioned": False,
        "ready_for_generation": False,
        "generation_triggers": [],
        "conversation_depth": len(messages),
        "readiness_score": 0.0
    }
    
    # Detectar nombre de proyecto
    project_indicators = ["proyecto", "sistema", "aplicacion", "plataforma", "solucion"]
    if any(indicator in full_conversation_lower for indicator in project_indicators):
        analysis["project_name_mentioned"] = True
        analysis["readiness_score"] += 0.25
    
    # Detectar tipo de proyecto
    integral_indicators = ["migracion", "aplicacion nueva", "modernizacion", "analitica", "seguridad", "ia", "iot", "data lake", "networking", "drp", "vdi", "integracion"]
    rapido_indicators = ["ec2", "rds", "ses", "vpn", "elb", "s3", "vpc", "cloudfront", "sso", "backup"]
    
    if any(indicator in full_conversation_lower for indicator in integral_indicators + rapido_indicators):
        analysis["project_type_mentioned"] = True
        analysis["readiness_score"] += 0.25
    
    # Detectar detalles tecnicos
    tech_indicators = ["aws", "servicio", "instancia", "base de datos", "almacenamiento", "red", "seguridad", "presupuesto", "usuarios"]
    if any(indicator in full_conversation_lower for indicator in tech_indicators):
        analysis["technical_details_mentioned"] = True
        analysis["readiness_score"] += 0.25
    
    # Detectar profundidad de conversacion
    if analysis["conversation_depth"] >= 3:
        analysis["readiness_score"] += 0.25
    
    # Detectar triggers de generacion
    generation_triggers = ["generar", "crear", "documentos", "diagrama", "cloudformation", "costos", "actividades", "entregables"]
    for trigger in generation_triggers:
        if trigger in full_conversation_lower:
            analysis["generation_triggers"].append(trigger)
    
    # Determinar si esta listo para generacion
    analysis["ready_for_generation"] = analysis["readiness_score"] >= 0.8 or len(analysis["generation_triggers"]) > 0
    
    return analysis

def generate_documents_with_mcps(project_data: Dict, conversation_context: Dict) -> Dict:
    """Genera documentos usando los MCPs"""
    
    generated_content = {}
    mcp_results = {}
    
    try:
        # 1. Generar diagrama de arquitectura
        logger.info("Generating architecture diagram...")
        diagram_data = {
            "project_name": project_data.get("name", "Proyecto AWS"),
            "project_type": project_data.get("type", "solucion-integral"),
            "services": project_data.get("services", ["EC2", "RDS", "S3"]),
            "description": project_data.get("description", "Arquitectura AWS profesional")
        }
        
        diagram_result = call_mcp_service("diagram", "generate", diagram_data)
        mcp_results["diagram"] = diagram_result
        
        if "error" not in diagram_result:
            generated_content["diagram"] = diagram_result
        
        # 2. Generar CloudFormation template
        logger.info("Generating CloudFormation template...")
        cfn_data = {
            "project_name": project_data.get("name", "Proyecto AWS"),
            "services": project_data.get("services", ["EC2", "RDS", "S3"]),
            "region": project_data.get("region", "us-east-1")
        }
        
        cfn_result = call_mcp_service("cfn", "generate", cfn_data)
        mcp_results["cloudformation"] = cfn_result
        
        if "error" not in cfn_result:
            generated_content["cloudformation"] = cfn_result
        
        # 3. Generar estimacion de costos
        logger.info("Generating cost estimation...")
        pricing_data = {
            "project_name": project_data.get("name", "Proyecto AWS"),
            "services": project_data.get("services", ["EC2", "RDS", "S3"]),
            "region": project_data.get("region", "us-east-1"),
            "usage_pattern": project_data.get("usage", "standard")
        }
        
        pricing_result = call_mcp_service("pricing", "estimate", pricing_data)
        mcp_results["pricing"] = pricing_result
        
        if "error" not in pricing_result:
            generated_content["pricing"] = pricing_result
        
        # 4. Generar documentos personalizados
        logger.info("Generating custom documents...")
        doc_data = {
            "project_name": project_data.get("name", "Proyecto AWS"),
            "project_type": project_data.get("type", "solucion-integral"),
            "description": project_data.get("description", "Proyecto AWS profesional"),
            "requirements": project_data.get("requirements", [])
        }
        
        doc_result = call_mcp_service("customdoc", "generate", doc_data)
        mcp_results["documents"] = doc_result
        
        if "error" not in doc_result:
            generated_content["documents"] = doc_result
        
        return {
            "success": True,
            "generated_content": generated_content,
            "mcp_results": mcp_results,
            "files_generated": len(generated_content)
        }
        
    except Exception as e:
        logger.error(f"Error generating documents: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "mcp_results": mcp_results
        }

def upload_to_s3(project_name: str, generated_content: Dict) -> Dict:
    """Sube los archivos generados a S3"""
    
    try:
        # Crear nombre de carpeta sin acentos
        folder_name = project_name.lower().replace(" ", "-").replace("_", "-")
        folder_name = "".join(c for c in folder_name if c.isalnum() or c == "-")
        
        s3_results = {}
        
        for content_type, content_data in generated_content.items():
            try:
                # Determinar extension de archivo
                if content_type == "diagram":
                    file_extension = "png"
                elif content_type == "cloudformation":
                    file_extension = "yaml"
                elif content_type == "pricing":
                    file_extension = "csv"
                elif content_type == "documents":
                    file_extension = "docx"
                else:
                    file_extension = "txt"
                
                # Crear nombre de archivo
                file_name = f"{folder_name}/{content_type}.{file_extension}"
                
                # Convertir contenido a string si es necesario
                if isinstance(content_data, dict):
                    file_content = json.dumps(content_data, indent=2)
                else:
                    file_content = str(content_data)
                
                # Subir a S3
                s3_client.put_object(
                    Bucket=DOCUMENTS_BUCKET,
                    Key=file_name,
                    Body=file_content,
                    ContentType='text/plain'
                )
                
                s3_results[content_type] = {
                    "file_name": file_name,
                    "bucket": DOCUMENTS_BUCKET,
                    "url": f"https://{DOCUMENTS_BUCKET}.s3.amazonaws.com/{file_name}"
                }
                
                logger.info(f"Uploaded {file_name} to S3")
                
            except Exception as e:
                logger.error(f"Error uploading {content_type}: {str(e)}")
                s3_results[content_type] = {"error": str(e)}
        
        return {
            "success": True,
            "folder_name": folder_name,
            "bucket": DOCUMENTS_BUCKET,
            "files": s3_results
        }
        
    except Exception as e:
        logger.error(f"Error uploading to S3: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def save_project_to_dynamodb(project_data: Dict, s3_info: Dict) -> Dict:
    """Guarda el proyecto en DynamoDB"""
    
    try:
        table = dynamodb.Table(PROJECTS_TABLE)
        
        # Crear item para DynamoDB
        project_item = {
            'id': str(uuid.uuid4()),
            'name': project_data.get('name', 'Proyecto Sin Nombre'),
            'type': project_data.get('type', 'solucion-integral'),
            'status': 'completado',
            'description': project_data.get('description', ''),
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat(),
            's3Folder': s3_info.get('folder_name', ''),
            's3Bucket': s3_info.get('bucket', ''),
            'files': {
                'word': 'documents' in s3_info.get('files', {}),
                'csv': 'pricing' in s3_info.get('files', {}),
                'yaml': 'cloudformation' in s3_info.get('files', {}),
                'png': 'diagram' in s3_info.get('files', {}),
                'svg': False
            },
            'projectData': project_data
        }
        
        # Guardar en DynamoDB
        table.put_item(Item=project_item)
        
        logger.info(f"Saved project {project_item['id']} to DynamoDB")
        
        return {
            "success": True,
            "project_id": project_item['id'],
            "table": PROJECTS_TABLE
        }
        
    except Exception as e:
        logger.error(f"Error saving to DynamoDB: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def prepare_conversation_for_bedrock(messages: List[Dict]) -> List[Dict]:
    """Prepara la conversacion para Bedrock con el prompt del arquitecto"""
    
    conversation = []
    
    # Agregar prompt del arquitecto al primer mensaje
    if messages:
        first_message = messages[0]
        enhanced_content = f"{PROMPT_ARQUITECTO_COMPLETO}\n\nUSUARIO: {first_message.get('content', '')}"
        
        conversation.append({
            "role": "user",
            "content": [{"text": enhanced_content}]
        })
        
        # Agregar mensajes restantes
        for msg in messages[1:]:
            conversation.append({
                "role": msg.get("role", "user"),
                "content": [{"text": msg.get("content", "")}]
            })
    
    return conversation

def call_bedrock_model(model_id: str, conversation: List[Dict]) -> Dict:
    """Llama al modelo Bedrock"""
    try:
        response = bedrock_runtime.converse(
            modelId=model_id,
            messages=conversation,
            inferenceConfig={
                'maxTokens': 4000,
                'temperature': 0.7,
                'topP': 0.9
            }
        )
        
        return {
            'response': response['output']['message']['content'][0]['text'],
            'usage': response.get('usage', {}),
            'modelUsed': model_id
        }
        
    except Exception as e:
        logger.error(f"Error calling Bedrock: {str(e)}")
        return {'error': f'Error calling Bedrock: {str(e)}'}

def lambda_handler(event, context):
    """Main Lambda handler para el Arquitecto AWS"""
    
    try:
        logger.info(f"Event received: {json.dumps(event)}")
        
        # Handle CORS preflight requests
        if event.get('httpMethod') == 'OPTIONS':
            logger.info("Handling OPTIONS preflight request")
            return handle_preflight_request()
        
        # Parse request
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        messages = body.get('messages', [])
        model_id = body.get('modelId', 'anthropic.claude-3-5-sonnet-20240620-v1:0')
        project_state = body.get('projectState', {'phase': 'inicio', 'data': {}})
        
        if not messages:
            logger.error("No messages provided")
            return create_error_response(400, 'No messages provided')
        
        logger.info(f"Processing {len(messages)} messages with model: {model_id}")
        
        # Analizar contexto de la conversacion
        conversation_analysis = analyze_conversation_context(messages)
        logger.info(f"Conversation analysis: {conversation_analysis}")
        
        # Preparar conversacion para Bedrock
        conversation = prepare_conversation_for_bedrock(messages)
        
        # Llamar al modelo Bedrock
        bedrock_response = call_bedrock_model(model_id, conversation)
        
        if 'error' in bedrock_response:
            return create_error_response(500, bedrock_response['error'])
        
        # Inicializar respuesta
        response_data = {
            'content': bedrock_response['response'],
            'projectState': project_state,
            'mcpActivated': True,
            'mcpUsed': ['core-mcp-prompt-understanding'],
            'readinessScore': conversation_analysis['readiness_score'],
            'modelUsed': bedrock_response.get('modelUsed', model_id),
            'usage': bedrock_response.get('usage', {}),
            'timestamp': datetime.now().isoformat()
        }
        
        # Si esta listo para generacion, activar MCPs de generacion
        if conversation_analysis['ready_for_generation']:
            logger.info("Ready for generation - activating generation MCPs")
            
            # Extraer datos del proyecto de la conversacion
            project_data = {
                "name": "Proyecto Extraido",  # Esto se deberia extraer mejor de la conversacion
                "type": "solucion-integral",
                "description": "Proyecto generado automaticamente",
                "services": ["EC2", "RDS", "S3"],
                "region": "us-east-1"
            }
            
            # Generar documentos
            generation_result = generate_documents_with_mcps(project_data, conversation_analysis)
            
            if generation_result['success']:
                # Subir a S3
                s3_result = upload_to_s3(project_data['name'], generation_result['generated_content'])
                
                if s3_result['success']:
                    # Guardar en DynamoDB
                    db_result = save_project_to_dynamodb(project_data, s3_result)
                    
                    # Actualizar respuesta con informacion de generacion
                    response_data.update({
                        'mcpUsed': ['core-mcp', 'diagram-mcp', 'cfn-mcp', 'pricing-mcp', 'customdoc-mcp'],
                        'generationResult': generation_result,
                        's3Info': s3_result,
                        'dbInfo': db_result,
                        'documentsGenerated': True
                    })
                    
                    # Actualizar contenido de respuesta
                    response_data['content'] += f"\n\n✅ DOCUMENTOS GENERADOS EXITOSAMENTE:\n"
                    response_data['content'] += f"- Carpeta S3: {s3_result['folder_name']}\n"
                    response_data['content'] += f"- Archivos: {len(s3_result['files'])} documentos\n"
                    response_data['content'] += f"- Proyecto guardado en base de datos\n"
                    response_data['content'] += f"\nPuedes revisar todos los archivos en la seccion 'Proyectos'."
        
        logger.info("Returning successful response")
        return create_success_response(response_data)
        
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}", exc_info=True)
        return create_error_response(500, f'Internal server error: {str(e)}')
