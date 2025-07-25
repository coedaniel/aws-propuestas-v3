"""
AWS Propuestas v3 - Arquitecto Lambda FINAL CORREGIDO
- Extrae datos específicos del proyecto de la conversación
- Genera documentos específicos usando MCPs con datos reales
- Diagrama con iconos oficiales AWS
- CloudFormation específico para los servicios mencionados
- Costos específicos del proyecto real
"""

import json
import boto3
import os
import logging
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Any

# Importar módulos locales
from project_extractor import extract_and_validate_project_data
from mcp_caller_fixed import generate_all_documents_with_specific_data

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

def upload_to_s3_with_specific_content(project_data: Dict, generated_content: Dict) -> Dict:
    """Sube los archivos generados a S3 con contenido específico"""
    
    try:
        # Usar el nombre limpio para S3
        folder_name = project_data.get("s3_folder_name", "proyecto-aws")
        
        s3_results = {}
        
        for content_type, content_data in generated_content.items():
            try:
                # Determinar extension de archivo
                if content_type == "diagram":
                    file_extension = "png"
                    content_type_s3 = "image/png"
                elif content_type == "cloudformation":
                    file_extension = "yaml"
                    content_type_s3 = "text/yaml"
                elif content_type == "pricing":
                    file_extension = "csv"
                    content_type_s3 = "text/csv"
                elif content_type == "documents":
                    file_extension = "docx"
                    content_type_s3 = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                elif content_type == "aws_docs":
                    file_extension = "md"
                    content_type_s3 = "text/markdown"
                else:
                    file_extension = "txt"
                    content_type_s3 = "text/plain"
                
                # Crear nombre de archivo
                file_name = f"{folder_name}/{content_type}.{file_extension}"
                
                # Procesar contenido según el tipo
                if isinstance(content_data, dict):
                    if content_type == "diagram" and "image_data" in content_data:
                        # Para diagramas, usar los datos de imagen
                        file_content = content_data.get("image_data", json.dumps(content_data, indent=2))
                    elif content_type == "cloudformation" and "template" in content_data:
                        # Para CloudFormation, usar el template
                        file_content = content_data.get("template", json.dumps(content_data, indent=2))
                    elif content_type == "pricing" and "csv_data" in content_data:
                        # Para pricing, usar los datos CSV
                        file_content = content_data.get("csv_data", json.dumps(content_data, indent=2))
                    else:
                        file_content = json.dumps(content_data, indent=2)
                else:
                    file_content = str(content_data)
                
                # Subir a S3
                s3_client.put_object(
                    Bucket=DOCUMENTS_BUCKET,
                    Key=file_name,
                    Body=file_content,
                    ContentType=content_type_s3,
                    Metadata={
                        'project-name': project_data.get("name", "Proyecto AWS"),
                        'project-type': project_data.get("type", "solucion-integral"),
                        'generated-by': 'aws-propuestas-v3-arquitecto',
                        'timestamp': datetime.now().isoformat()
                    }
                )
                
                s3_results[content_type] = {
                    "file_name": file_name,
                    "bucket": DOCUMENTS_BUCKET,
                    "url": f"https://{DOCUMENTS_BUCKET}.s3.amazonaws.com/{file_name}",
                    "size": len(file_content.encode('utf-8')) if isinstance(file_content, str) else len(file_content)
                }
                
                logger.info(f"✅ Uploaded {file_name} to S3 ({s3_results[content_type]['size']} bytes)")
                
            except Exception as e:
                logger.error(f"❌ Error uploading {content_type}: {str(e)}")
                s3_results[content_type] = {"error": str(e)}
        
        return {
            "success": True,
            "folder_name": folder_name,
            "bucket": DOCUMENTS_BUCKET,
            "files": s3_results,
            "total_files": len([f for f in s3_results.values() if "error" not in f])
        }
        
    except Exception as e:
        logger.error(f"❌ Error uploading to S3: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def save_project_to_dynamodb_with_details(project_data: Dict, s3_info: Dict) -> Dict:
    """Guarda el proyecto en DynamoDB con detalles específicos"""
    
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
            'projectData': {
                'services': project_data.get('services', []),
                'region': project_data.get('region', 'us-east-1'),
                'architecture_type': project_data.get('architecture_type', 'standard'),
                'requirements': project_data.get('requirements', [])
            },
            'filesGenerated': s3_info.get('total_files', 0)
        }
        
        # Guardar en DynamoDB
        table.put_item(Item=project_item)
        
        logger.info(f"✅ Saved project {project_item['id']} to DynamoDB")
        logger.info(f"📋 Project details: {project_item['name']} - {len(project_item['projectData']['services'])} services")
        
        return {
            "success": True,
            "project_id": project_item['id'],
            "table": PROJECTS_TABLE,
            "project_item": project_item
        }
        
    except Exception as e:
        logger.error(f"❌ Error saving to DynamoDB: {str(e)}")
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
        logger.error(f"❌ Error calling Bedrock: {str(e)}")
        return {'error': f'Error calling Bedrock: {str(e)}'}

def lambda_handler(event, context):
    """Main Lambda handler para el Arquitecto AWS FINAL CORREGIDO"""
    
    try:
        logger.info(f"🚀 Event received: {json.dumps(event)}")
        
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
        
        logger.info(f"📝 Processing {len(messages)} messages with model: {model_id}")
        
        # PASO 1: Extraer datos específicos del proyecto de la conversación
        logger.info("1️⃣ Extracting specific project data from conversation...")
        project_data = extract_and_validate_project_data(messages)
        logger.info(f"📋 Extracted project data: {json.dumps(project_data, indent=2)}")
        
        # PASO 2: Analizar contexto de la conversacion
        conversation_analysis = analyze_conversation_context(messages)
        logger.info(f"🔍 Conversation analysis: {conversation_analysis}")
        
        # PASO 3: Preparar conversacion para Bedrock
        conversation = prepare_conversation_for_bedrock(messages)
        
        # PASO 4: Llamar al modelo Bedrock
        bedrock_response = call_bedrock_model(model_id, conversation)
        
        if 'error' in bedrock_response:
            return create_error_response(500, bedrock_response['error'])
        
        # PASO 5: Inicializar respuesta
        response_data = {
            'content': bedrock_response['response'],
            'projectState': project_state,
            'mcpActivated': True,
            'mcpUsed': ['core-mcp-prompt-understanding'],
            'readinessScore': conversation_analysis['readiness_score'],
            'projectDataExtracted': project_data,
            'modelUsed': bedrock_response.get('modelUsed', model_id),
            'usage': bedrock_response.get('usage', {}),
            'timestamp': datetime.now().isoformat()
        }
        
        # PASO 6: Si esta listo para generacion, activar MCPs con datos específicos
        if conversation_analysis['ready_for_generation']:
            logger.info("🎯 Ready for generation - activating generation MCPs with specific project data")
            
            # PASO 7: Generar documentos con datos específicos del proyecto
            generation_result = generate_all_documents_with_specific_data(project_data)
            
            if generation_result['success']:
                logger.info(f"✅ Documents generated successfully: {generation_result['files_generated']} files")
                
                # PASO 8: Subir a S3 con contenido específico
                s3_result = upload_to_s3_with_specific_content(project_data, generation_result['generated_content'])
                
                if s3_result['success']:
                    logger.info(f"✅ Files uploaded to S3: {s3_result['total_files']} files")
                    
                    # PASO 9: Guardar en DynamoDB con detalles específicos
                    db_result = save_project_to_dynamodb_with_details(project_data, s3_result)
                    
                    # PASO 10: Actualizar respuesta con informacion de generacion
                    response_data.update({
                        'mcpUsed': ['core-mcp', 'diagram-mcp', 'cfn-mcp', 'pricing-mcp', 'customdoc-mcp', 'awsdocs-mcp'],
                        'generationResult': generation_result,
                        's3Info': s3_result,
                        'dbInfo': db_result,
                        'documentsGenerated': True,
                        'specificProjectData': project_data
                    })
                    
                    # PASO 11: Actualizar contenido de respuesta con detalles específicos
                    response_data['content'] += f"\n\n✅ DOCUMENTOS GENERADOS EXITOSAMENTE PARA: {project_data['name']}\n"
                    response_data['content'] += f"🏗️ Servicios AWS: {', '.join(project_data['services'])}\n"
                    response_data['content'] += f"📁 Carpeta S3: {s3_result['folder_name']}\n"
                    response_data['content'] += f"📄 Archivos: {s3_result['total_files']} documentos especificos\n"
                    response_data['content'] += f"💾 Proyecto guardado en base de datos\n"
                    response_data['content'] += f"\n🎯 Documentos incluyen:\n"
                    response_data['content'] += f"   • Diagrama de arquitectura con iconos AWS oficiales\n"
                    response_data['content'] += f"   • CloudFormation template para {', '.join(project_data['services'][:3])}\n"
                    response_data['content'] += f"   • Estimacion de costos especifica del proyecto\n"
                    response_data['content'] += f"   • Documentos tecnicos personalizados\n"
                    response_data['content'] += f"\n📱 Puedes revisar todos los archivos en la seccion 'Proyectos'."
                    
                else:
                    logger.error(f"❌ S3 upload failed: {s3_result.get('error')}")
            else:
                logger.error(f"❌ Document generation failed: {generation_result.get('error')}")
        
        logger.info("✅ Returning successful response")
        return create_success_response(response_data)
        
    except Exception as e:
        logger.error(f"❌ Error in lambda_handler: {str(e)}", exc_info=True)
        return create_error_response(500, f'Internal server error: {str(e)}')
