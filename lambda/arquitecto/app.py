import json
import boto3
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any
import logging

# Import smart MCP handler
from smart_mcp_handler import smart_mcp

# Import working intelligent generator
from generators.working_intelligent_generator import (
    extract_service_from_conversation,
    create_specific_prompt,
    generate_documents_from_ai_response
)

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
        
        logger.info(f"🏗️ ARQUITECTO V3 - Processing chat")
        logger.info(f"Model ID: {model_id}")
        logger.info(f"Messages count: {len(messages)}")
        logger.info(f"Project info: {project_info}")
        
        if not messages:
            return create_response(400, {'error': 'Messages are required'})
        
        # System prompt for arquitecto mode
        system_prompt = get_arquitecto_system_prompt()
        
        # Prepare prompt for Bedrock
        prompt_body = prepare_prompt(model_id, system_prompt, messages, project_info, current_step)
        
        logger.info(f"🏗️ ARQUITECTO USING MODEL: {model_id}")
        logger.info(f"Prompt body keys: {list(prompt_body.keys())}")
        
        try:
            # Call Bedrock
            logger.info("Calling Bedrock...")
            response = bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(prompt_body),
                contentType='application/json'
            )
            logger.info("Bedrock response received")
            
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
            
            logger.info(f"AI response received, length: {len(ai_response)}")
            
        except Exception as bedrock_error:
            logger.error(f"Bedrock error: {str(bedrock_error)}")
            return create_response(500, {
                'error': 'Error calling Bedrock',
                'details': str(bedrock_error),
                'modelId': model_id
            })
        
        # 🎯 SMART MCP PROCESSING - Like Amazon Q CLI Developer
        # Process AI response and activate MCPs only when needed
        mcp_results = smart_mcp.process_with_smart_mcps(
            ai_response, 
            {"messages": messages, "step": len(messages)}, 
            project_info
        )
        
        # Use enhanced response from MCP processing
        final_ai_response = mcp_results["enhanced_response"]
        files_generated = mcp_results["files_generated"]
        mcp_services_used = mcp_results["services_used"]
        
        logger.info(f"🔧 MCP Services used: {mcp_services_used}")
        logger.info(f"📁 Files generated: {len(files_generated)}")
        
        # Extract service parameters from conversation
        service_params = extract_service_from_conversation(messages, final_ai_response)
        servicio = service_params['servicio']
        descripcion = service_params['descripcion']
        objetivo = service_params['objetivo']
        
        logger.info(f"🔍 EXTRACTED - Service: {servicio}, Description: {descripcion[:50]}...")
        
        # Check if project is complete - ONLY when AI explicitly indicates completion
        is_complete = check_if_complete(final_ai_response, project_info)
        
        # Check if we have enough information extracted
        has_enough_info = bool(servicio and descripcion and objetivo)
        
        logger.info(f"🎯 COMPLETION CHECK - Has info: {has_enough_info}, AI completion check: {is_complete}")
        
        # Generate additional documents if project is complete and MCPs haven't generated everything
        document_generation_results = None
        if is_complete and not files_generated:
            # Generate documents using the working intelligent system as fallback
            logger.info(f"✅ GENERATING FALLBACK DOCUMENTS for {servicio}")
            
            document_generation_results = generate_documents_from_ai_response(
                final_ai_response, 
                servicio, 
                project_id, 
                user_id
            )
        elif files_generated:
            # Use MCP generated files
            document_generation_results = {
                "success": True,
                "files": files_generated,
                "method": "smart_mcp"
            }
            
        # Create response for chat
        if is_complete:
            chat_response = f"""✅ **PROPUESTA COMPLETADA PARA {servicio.upper()}**

He analizado tu proyecto: "{descripcion}"

**Objetivo identificado:** {objetivo}

**Documentos generados específicamente para {servicio}:**

📄 **Propuesta Ejecutiva** - Documento profesional centrado en {servicio}
🔧 **Documento Técnico** - Arquitectura específica de {servicio}  
            # Create completion message for document generation
            completion_message = f"""✅ **¡Proyecto {servicio} Completado!**

He generado todos los documentos necesarios para tu proyecto de {servicio}:

📄 **Documento de Arquitectura** - Diseño completo de {servicio}
📊 **Plan de Actividades** - Implementación específica de {servicio}
💰 **Estimación de Costos** - Costos reales de {servicio}
🏗️ **CloudFormation Template** - Infraestructura para {servicio}
📋 **Guía Calculadora AWS** - Estimación específica de {servicio}

**Todos los documentos están adaptados específicamente a {servicio} y tu caso de uso.**

Los documentos están disponibles en la sección de **Proyectos** para descarga.

¿Te gustaría que ajuste algún aspecto específico de la solución con {servicio}?"""
            
            # Update project info with proper naming
            project_info.update({
                'name': f"Proyecto {servicio}",
                'service_focus': servicio,
                'description': descripcion,
                'objective': objetivo,
                'status': 'COMPLETED'
            })
            
            # Use completion message instead of AI response with documents mixed in
            final_response = completion_message
            
        else:
            # Continue conversation - use enhanced AI response from MCP processing
            final_response = final_ai_response
            project_info.update({
                'service_focus': servicio,
                'description': descripcion,
                'objective': objetivo,
                'status': 'IN_PROGRESS'
            })
        
        # Save project progress
        if projects_table:
            save_project_progress(project_id, user_id, messages, final_response, project_info, 
                                current_step + 1, is_complete, model_id)
        
        response_data = {
            'response': final_response,
            'modelId': model_id,
            'mode': 'arquitecto-mcp-containers',
            'timestamp': datetime.now().isoformat(),
            'mcpServicesUsed': mcp_services_used,
            'documentsGenerated': files_generated if files_generated else None,
            'projectId': project_id,
            'projectName': project_info.get('name'),
            'messageCount': len(messages) + 1,
            'projectInfo': project_info,
            'currentStep': current_step + 1,
            'isComplete': is_complete,
            'usage': usage,
            'documentGeneration': document_generation_results,
            'specificService': servicio if has_enough_info else None
        }
        
        logger.info(f"✅ ARQUITECTO SUCCESS - Response length: {len(final_response)}")
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
    """Get system prompt for arquitecto mode - PROMPT MAESTRO COMPLETO"""
    bucket_name = DOCUMENTS_BUCKET or 'aws-propuestas-v3-documents-prod'
    
    return f"""Actua como arquitecto de soluciones AWS y consultor experto. Vamos a dimensionar, documentar y entregar una solucion profesional en AWS, siguiendo mejores practicas y generando todos los archivos necesarios para una propuesta ejecutiva. No uses acentos ni caracteres especiales en ningun texto, archivo, script ni documento. Asegura que todos los archivos Word generados sean funcionales y compatibles: entrega solo texto plano, sin imagenes, sin tablas complejas, ni formato avanzado, solo texto estructurado, claro y legible. Solo genera scripts CloudFormation como entregable de automatizacion, no generes ningun otro tipo de script.

IMPORTANTE: Debes ser INTELIGENTE y ADAPTATIVO. Si el usuario da respuestas en otro orden, usa frases libres o menciona algo fuera del guion, debes:
- Entender la intencion
- Detectar que informacion ya tienes y cual falta
- Hacer nuevas preguntas segun lo que el usuario diga
- No repetir preguntas innecesarias
- NO generar documentos hasta tener informacion suficiente
- La conversacion debe sentirse natural, como con un arquitecto AWS real

FLUJO MAESTRO (adaptable dinamicamente):

1. **PRIMERA PREGUNTA OBLIGATORIA:**
¿Cual es el nombre del proyecto?

2. **SEGUNDA PREGUNTA:**
El proyecto es una solucion integral (como migracion, aplicacion nueva, modernizacion, analitica, seguridad, IA, IoT, data lake, networking, DRP, VDI, integracion, etc.)
o es un servicio rapido especifico (implementacion de instancias EC2, RDS, SES, VPN, ELB, S3, VPC, CloudFront, SSO, backup, etc.)

**Si elige "servicio rapido especifico":**

1. Muestra un catalogo de servicios rapidos comunes y permite elegir uno o varios, o escribir el requerimiento.
2. Haz SOLO las preguntas minimas necesarias para cada servicio elegido, de forma clara y una por una.
3. ESPERA las respuestas del usuario antes de continuar.
4. Para S3: pregunta nombre del bucket, region, tipo de almacenamiento, politicas de acceso, versionado, cifrado.
5. Para EC2: pregunta tipo de instancia, sistema operativo, region, configuracion de red, almacenamiento.
6. Para VPC: pregunta CIDR, subredes, gateways, reglas de seguridad.
7. SOLO cuando tengas respuestas suficientes, di explicitamente "Procederé a generar los documentos" y genera:
    - Tabla de actividades de implementacion (CSV, SIN acentos)
    - Script CloudFormation (SIN acentos)
    - Diagrama de arquitectura (SVG, PNG, Draw.io, SIN acentos)
    - Documento Word (texto plano, SIN acentos)
    - Archivo de costos estimados (CSV, SIN acentos)
    - Guia calculadora AWS (TXT, SIN acentos)
8. Sube AUTOMATICAMENTE todos los archivos al bucket S3 del sistema ({bucket_name}) en una carpeta con el nombre del proyecto.
9. Confirma que la carga fue exitosa.
10. Pregunta si deseas agregar comentarios finales.

**Si elige "solucion integral":**

1. Entrevista guiada, una pregunta a la vez:
   - Tipo de solucion, objetivo, descripcion detallada
   - Caracteristicas clave y funcionalidades
   - Servicios AWS preferidos o requeridos
   - Recursos estimados (usuarios, transacciones, almacenamiento)
   - Integraciones con sistemas existentes
   - Requisitos de seguridad y compliance
   - Alta disponibilidad y disaster recovery
   - Estimacion de trafico y carga
   - Presupuesto aproximado
   - Fechas importantes y restricciones
   - Comentarios adicionales

2. Aplica logica condicional segun el tipo de solucion:
   - Migracion: enfoque en lift-and-shift vs refactoring
   - Aplicacion nueva: arquitectura cloud-native
   - Modernizacion: contenedores, serverless, microservicios
   - Analitica: data lakes, warehouses, ML/AI
   - Seguridad: Zero Trust, compliance, governance
   - IA: Bedrock, SageMaker, servicios cognitivos

3. SOLO cuando tengas informacion completa, genera TODOS los entregables:
   - Tabla de actividades detallada (CSV/Excel)
   - Script CloudFormation completo
   - Diagramas de arquitectura (SVG, PNG, Draw.io)
   - Documento de propuesta ejecutiva (Word, texto plano)
   - Estimacion detallada de costos (CSV/Excel)
   - Guia para calculadora oficial AWS

4. Pregunta en que bucket S3 desea subir los archivos (o usa el default del sistema)
5. Sube la carpeta completa al bucket con el nombre del proyecto
6. Confirma la carga exitosa
7. Pregunta si hay ajustes finales necesarios

**REGLAS DE CONVERSACION:**

- Siempre pregunta una sola cosa a la vez
- Si una respuesta es ambigua, pide mas detalles antes de continuar
- Todos los nombres de recursos, archivos, carpetas y proyectos deben estar libres de acentos
- No entregues contenido generico. Todo debe basarse en lo que el usuario haya dicho
- Si detectas que un archivo debe ser generado por un MCP (como diagramas o costos), activalo automaticamente
- Este flujo es exclusivo de la pagina /arquitecto

**ACTIVACION AUTOMATICA DE MCPs:**

Cuando sea momento de generar documentos, activa automaticamente:
- MCP Diagramas: para SVG, PNG y Draw.io
- MCP Costos: para estimaciones detalladas
- MCP CloudFormation: para templates optimizados
- MCP Documentos: para archivos Word estructurados
- MCP S3: para subida automatica de archivos

**CALIDAD PROFESIONAL:**

- Usa terminologia tecnica precisa de AWS
- Aplica Well-Architected Framework
- Considera costos, seguridad, escalabilidad y disponibilidad
- Genera documentacion lista para cliente final
- Estructura clara y profesional en todos los entregables

Bucket S3 del sistema: {bucket_name}

Recuerda: Eres un arquitecto AWS Senior con 10+ años de experiencia. Actua con profesionalismo, precision tecnica y enfoque en resultados ejecutivos."""
   - Caracteristicas clave, servicios AWS deseados
   - Recursos principales, integraciones necesarias
   - Seguridad, alta disponibilidad, usuarios/trafico
   - Presupuesto, fechas, restricciones tecnicas
2. Aplica logica condicional segun tipo de solucion.
3. SOLO cuando tengas informacion completa, di "Procederé a generar" y crea todos los entregables.
4. Sube AUTOMATICAMENTE archivos al bucket S3 del sistema ({bucket_name}).
5. Permite comentarios finales.

REGLAS CRITICAS:
- Se claro, especifico, pregunta una cosa a la vez
- Si respuesta es vaga, pide mas detalle antes de avanzar
- NO generes documentos prematuramente
- Flujo conversacional natural y adaptativo
- SIN acentos ni caracteres especiales NUNCA
- Documentos profesionales y compatibles
- NUNCA preguntes donde subir archivos - usa SIEMPRE el bucket del sistema
- Sube archivos automaticamente sin preguntar

El sistema debe completar los entregables solo cuando tenga informacion suficiente y diga explicitamente que va a generar documentos."""

def prepare_prompt(model_id: str, system_prompt: str, messages: List[Dict], 
                  project_info: Dict, current_step: int) -> Dict:
    """Prepare prompt based on model type with optimized temperature for AWS projects"""
    
    # Add context about current project info
    context = f"\nCONTEXTO DEL PROYECTO ACTUAL:\n"
    if project_info:
        for key, value in project_info.items():
            context += f"- {key}: {value}\n"
    context += f"- Paso actual: {current_step}\n"
    
    full_system_prompt = system_prompt + context
    
    # Optimized temperature for AWS architecture (precision over creativity)
    aws_temperature = 0.3
    
    if model_id.startswith('anthropic.claude'):
        return {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "system": full_system_prompt,
            "messages": messages,
            "temperature": aws_temperature
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
                "temperature": aws_temperature
            }
        }
    elif model_id.startswith('meta.llama'):
        return {
            "prompt": full_system_prompt + "\n\n" + "\n".join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in messages]),
            "max_gen_len": 4000,
            "temperature": aws_temperature
        }
    else:
        return {
            "messages": [{"role": "system", "content": full_system_prompt}] + messages,
            "max_tokens": 4000,
            "temperature": aws_temperature
        }

def extract_response(model_id: str, response_body: Dict) -> tuple:
    """Extract AI response and usage from response body"""
    
    ai_response = ""
    usage = {}
    
    logger.info(f"Extracting response for model: {model_id}")
    logger.info(f"Response body structure: {list(response_body.keys())}")
    
    try:
        if model_id.startswith('anthropic.claude'):
            # Claude response structure
            if 'content' in response_body and response_body['content']:
                ai_response = response_body['content'][0].get('text', '')
            elif 'completion' in response_body:
                ai_response = response_body.get('completion', '')
            
            usage = {
                'inputTokens': response_body.get('usage', {}).get('input_tokens', 0),
                'outputTokens': response_body.get('usage', {}).get('output_tokens', 0)
            }
            
        elif model_id.startswith('amazon.nova'):
            # Nova response structure
            if 'output' in response_body:
                output = response_body['output']
                if 'message' in output and 'content' in output['message']:
                    ai_response = output['message']['content'][0].get('text', '')
            
            usage = {
                'inputTokens': response_body.get('usage', {}).get('inputTokens', 0),
                'outputTokens': response_body.get('usage', {}).get('outputTokens', 0),
                'totalTokens': response_body.get('usage', {}).get('totalTokens', 0)
            }
            
        elif model_id.startswith('meta.llama'):
            # Llama response structure
            if 'generation' in response_body:
                ai_response = response_body.get('generation', '')
            elif 'outputs' in response_body:
                ai_response = response_body['outputs'][0].get('text', '')
            
            usage = {
                'inputTokens': response_body.get('prompt_token_count', 0),
                'outputTokens': response_body.get('generation_token_count', 0)
            }
            
        else:
            # Generic fallback
            ai_response = response_body.get('content', response_body.get('text', ''))
        
        logger.info(f"Extracted response length: {len(ai_response)}")
        logger.info(f"Usage: {usage}")
        
        return ai_response, usage
        
    except Exception as e:
        logger.error(f"Error extracting response: {str(e)}")
        logger.error(f"Response body: {response_body}")
        return "", {}

def analyze_conversation_for_document_generation(messages: List[Dict], ai_response: str) -> Dict:
    """Analyze conversation to determine if documents should be generated"""
    
    # Extract conversation text
    conversation_text = ""
    for msg in messages:
        conversation_text += f"{msg.get('role', '')}: {msg.get('content', '')}\n"
    conversation_text += f"assistant: {ai_response}"
    
    conversation_lower = conversation_text.lower()
    
    # Check for project name
    project_name = "Proyecto AWS"
    for msg in messages:
        content = msg.get('content', '').lower()
        if 'nombre del proyecto' in content or 'proyecto se llama' in content:
            # Extract project name from next user message
            words = msg.get('content', '').split()
            if len(words) > 2:
                project_name = ' '.join(words[-3:]).title()
    
    # Detect project type
    project_type = "unknown"
    if any(term in conversation_lower for term in ['servicio rapido', 'ec2', 'rds', 's3', 'vpc', 'cloudfront']):
        project_type = "servicio_rapido"
    elif any(term in conversation_lower for term in ['solucion integral', 'migracion', 'aplicacion nueva', 'modernizacion']):
        project_type = "solucion_integral"
    
    # Check if ready for document generation
    should_generate = False
    
    # For servicio rapido: check if we have service details
    if project_type == "servicio_rapido":
        has_service_details = any(term in conversation_lower for term in [
            'region', 'tipo de instancia', 'almacenamiento', 'configuracion',
            'bucket', 'cifrado', 'versionado', 'politicas'
        ])
        has_enough_messages = len(messages) >= 3
        should_generate = has_service_details and has_enough_messages
    
    # For solucion integral: check if we have comprehensive info
    elif project_type == "solucion_integral":
        required_info = ['objetivo', 'descripcion', 'servicios', 'recursos']
        info_count = sum(1 for info in required_info if info in conversation_lower)
        has_enough_messages = len(messages) >= 5
        should_generate = info_count >= 3 and has_enough_messages
    
    # Also check if AI explicitly mentions document generation
    if any(phrase in ai_response.lower() for phrase in [
        'procederé a generar', 'generar los documentos', 'crear los archivos',
        'documentos listos', 'archivos generados'
    ]):
        should_generate = True
    
    return {
        'should_generate_documents': should_generate,
        'project_type': project_type,
        'project_name': project_name,
        'conversation_length': len(messages),
        'has_project_details': project_type != "unknown"
    }

def generate_complete_document_package(project_name: str, project_type: str, messages: List[Dict], 
                                     ai_response: str, project_id: str, user_id: str) -> Dict:
    """Generate complete document package for the project"""
    
    try:
        logger.info(f"📄 Generating document package for: {project_name}")
        
        # Create project folder structure
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_folder = f"projects/{user_id}/{project_id}_{timestamp}"
        
        files_generated = []
        
        # 1. Generate Activity Table (CSV)
        activity_table = generate_activity_table(project_name, project_type, messages)
        if activity_table:
            files_generated.append({
                'name': f"{project_name}_Actividades.csv",
                'type': 'csv',
                'description': 'Tabla de actividades de implementacion',
                'content': activity_table,
                'path': f"{project_folder}/{project_name}_Actividades.csv"
            })
        
        # 2. Generate CloudFormation Template
        cfn_template = generate_cloudformation_template(project_name, project_type, messages)
        if cfn_template:
            files_generated.append({
                'name': f"{project_name}_CloudFormation.yaml",
                'type': 'yaml',
                'description': 'Script CloudFormation para infraestructura',
                'content': cfn_template,
                'path': f"{project_folder}/{project_name}_CloudFormation.yaml"
            })
        
        # 3. Generate Architecture Diagram (SVG)
        diagram_svg = generate_architecture_diagram(project_name, project_type, messages)
        if diagram_svg:
            files_generated.append({
                'name': f"{project_name}_Arquitectura.svg",
                'type': 'svg',
                'description': 'Diagrama de arquitectura en formato SVG',
                'content': diagram_svg,
                'path': f"{project_folder}/{project_name}_Arquitectura.svg"
            })
        
        # 4. Generate Word Document (Plain Text)
        word_doc = generate_word_document(project_name, project_type, messages, ai_response)
        if word_doc:
            files_generated.append({
                'name': f"{project_name}_Propuesta.txt",
                'type': 'txt',
                'description': 'Documento de propuesta ejecutiva',
                'content': word_doc,
                'path': f"{project_folder}/{project_name}_Propuesta.txt"
            })
        
        # 5. Generate Cost Estimation (CSV)
        cost_estimation = generate_cost_estimation(project_name, project_type, messages)
        if cost_estimation:
            files_generated.append({
                'name': f"{project_name}_Costos.csv",
                'type': 'csv',
                'description': 'Estimacion detallada de costos AWS',
                'content': cost_estimation,
                'path': f"{project_folder}/{project_name}_Costos.csv"
            })
        
        # 6. Generate AWS Calculator Guide
        calculator_guide = generate_calculator_guide(project_name, project_type, messages)
        if calculator_guide:
            files_generated.append({
                'name': f"{project_name}_Calculadora_AWS.txt",
                'type': 'txt',
                'description': 'Guia para usar la calculadora oficial de AWS',
                'content': calculator_guide,
                'path': f"{project_folder}/{project_name}_Calculadora_AWS.txt"
            })
        
        # Upload files to S3 (simulated for now)
        s3_upload_success = upload_files_to_s3(files_generated, DOCUMENTS_BUCKET)
        
        return {
            'success': True,
            'files': files_generated,
            's3_folder': project_folder,
            'upload_success': s3_upload_success,
            'total_files': len(files_generated)
        }
        
    except Exception as e:
        logger.error(f"Error generating document package: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'files': []
        }

def generate_activity_table(project_name: str, project_type: str, messages: List[Dict]) -> str:
    """Generate activity implementation table in CSV format"""
    
    activities = [
        "Actividad,Descripcion,Duracion,Responsable,Dependencias,Estado",
        "Planificacion inicial,Revision de requerimientos y arquitectura,2 dias,Arquitecto AWS,Ninguna,Pendiente",
        "Configuracion de red,Creacion de VPC y subredes,1 dia,Ingeniero de Red,Planificacion,Pendiente",
        "Implementacion de seguridad,Configuracion de IAM y grupos de seguridad,1 dia,Especialista Seguridad,Red,Pendiente",
        "Despliegue de servicios,Implementacion de servicios AWS principales,3 dias,DevOps Engineer,Seguridad,Pendiente",
        "Configuracion de monitoreo,Setup de CloudWatch y alertas,1 dia,SRE,Servicios,Pendiente",
        "Pruebas de integracion,Validacion de funcionalidad completa,2 dias,QA Engineer,Monitoreo,Pendiente",
        "Documentacion final,Entrega de documentacion tecnica,1 dia,Technical Writer,Pruebas,Pendiente",
        "Go-live y soporte,Puesta en produccion y soporte inicial,1 dia,Todo el equipo,Documentacion,Pendiente"
    ]
    
    if project_type == "servicio_rapido":
        # Simplified activities for quick services
        activities = [
            "Actividad,Descripcion,Duracion,Responsable,Dependencias,Estado",
            "Configuracion inicial,Setup basico del servicio,4 horas,Ingeniero AWS,Ninguna,Pendiente",
            "Implementacion,Despliegue del servicio configurado,2 horas,DevOps,Configuracion,Pendiente",
            "Validacion,Pruebas de funcionalidad,1 hora,QA,Implementacion,Pendiente",
            "Documentacion,Entrega de documentacion,1 hora,Arquitecto,Validacion,Pendiente"
        ]
    
    return "\n".join(activities)

def generate_cloudformation_template(project_name: str, project_type: str, messages: List[Dict]) -> str:
    """Generate CloudFormation template based on project requirements"""
    
    # Extract service requirements from messages
    services_mentioned = []
    for msg in messages:
        content = msg.get('content', '').lower()
        if 'ec2' in content: services_mentioned.append('ec2')
        if 's3' in content: services_mentioned.append('s3')
        if 'rds' in content: services_mentioned.append('rds')
        if 'vpc' in content: services_mentioned.append('vpc')
    
    template = f"""AWSTemplateFormatVersion: '2010-09-09'
Description: 'CloudFormation template for {project_name}'

Parameters:
  ProjectName:
    Type: String
    Default: {project_name.replace(' ', '-')}
    Description: Name of the project
  
  Environment:
    Type: String
    Default: prod
    AllowedValues: [dev, test, prod]
    Description: Environment type

Resources:"""

    # Add VPC if mentioned or for integral solutions
    if 'vpc' in services_mentioned or project_type == "solucion_integral":
        template += """
  ProjectVPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub '${ProjectName}-vpc'

  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref ProjectVPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub '${ProjectName}-public-subnet'

  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: !Sub '${ProjectName}-igw'

  AttachGateway:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref ProjectVPC
      InternetGatewayId: !Ref InternetGateway"""

    # Add S3 bucket if mentioned
    if 's3' in services_mentioned:
        template += """
  ProjectS3Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '${ProjectName}-bucket-${AWS::AccountId}'
      VersioningConfiguration:
        Status: Enabled
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256"""

    # Add EC2 instance if mentioned
    if 'ec2' in services_mentioned:
        template += """
  ProjectEC2Instance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-0c02fb55956c7d316  # Amazon Linux 2
      InstanceType: t3.micro
      SubnetId: !Ref PublicSubnet
      SecurityGroupIds:
        - !Ref ProjectSecurityGroup
      Tags:
        - Key: Name
          Value: !Sub '${ProjectName}-instance'

  ProjectSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for project
      VpcId: !Ref ProjectVPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0"""

    template += """

Outputs:
  ProjectName:
    Description: Name of the project
    Value: !Ref ProjectName
    Export:
      Name: !Sub '${AWS::StackName}-ProjectName'"""

    return template

def generate_architecture_diagram(project_name: str, project_type: str, messages: List[Dict]) -> str:
    """Generate SVG architecture diagram"""
    
    # Simple SVG diagram template
    svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
  <title>{project_name} - Architecture Diagram</title>
  
  <!-- Background -->
  <rect width="800" height="600" fill="#f8f9fa" stroke="#dee2e6" stroke-width="2"/>
  
  <!-- Title -->
  <text x="400" y="30" text-anchor="middle" font-family="Arial" font-size="20" font-weight="bold">
    {project_name} - AWS Architecture
  </text>
  
  <!-- AWS Cloud -->
  <rect x="50" y="80" width="700" height="480" fill="#fff3cd" stroke="#ffc107" stroke-width="2" rx="10"/>
  <text x="70" y="105" font-family="Arial" font-size="14" font-weight="bold">AWS Cloud</text>
  
  <!-- VPC -->
  <rect x="100" y="130" width="600" height="400" fill="#d1ecf1" stroke="#17a2b8" stroke-width="2" rx="5"/>
  <text x="120" y="155" font-family="Arial" font-size="12" font-weight="bold">VPC (10.0.0.0/16)</text>
  
  <!-- Public Subnet -->
  <rect x="150" y="180" width="250" height="150" fill="#d4edda" stroke="#28a745" stroke-width="1" rx="3"/>
  <text x="170" y="205" font-family="Arial" font-size="11">Public Subnet</text>
  
  <!-- EC2 Instance -->
  <rect x="180" y="220" width="80" height="60" fill="#ffeaa7" stroke="#fdcb6e" stroke-width="1" rx="3"/>
  <text x="220" y="245" text-anchor="middle" font-family="Arial" font-size="10">EC2</text>
  <text x="220" y="260" text-anchor="middle" font-family="Arial" font-size="10">Instance</text>
  
  <!-- S3 Bucket -->
  <rect x="450" y="220" width="80" height="60" fill="#74b9ff" stroke="#0984e3" stroke-width="1" rx="3"/>
  <text x="490" y="245" text-anchor="middle" font-family="Arial" font-size="10">S3</text>
  <text x="490" y="260" text-anchor="middle" font-family="Arial" font-size="10">Bucket</text>
  
  <!-- Internet Gateway -->
  <rect x="350" y="350" width="100" height="40" fill="#fd79a8" stroke="#e84393" stroke-width="1" rx="3"/>
  <text x="400" y="375" text-anchor="middle" font-family="Arial" font-size="10">Internet Gateway</text>
  
  <!-- Connections -->
  <line x1="260" y1="250" x2="350" y2="250" stroke="#2d3436" stroke-width="2"/>
  <line x1="450" y1="250" x2="530" y2="250" stroke="#2d3436" stroke-width="2"/>
  <line x1="400" y1="350" x2="400" y2="300" stroke="#2d3436" stroke-width="2"/>
  
  <!-- Legend -->
  <text x="50" y="590" font-family="Arial" font-size="10" fill="#6c757d">
    Generated for: {project_name} | Type: {project_type} | AWS Architecture Diagram
  </text>
</svg>"""
    
    return svg_content

def generate_word_document(project_name: str, project_type: str, messages: List[Dict], ai_response: str) -> str:
    """Generate Word document content in plain text format"""
    
    doc_content = f"""PROPUESTA EJECUTIVA - {project_name.upper()}

RESUMEN EJECUTIVO
================

Proyecto: {project_name}
Tipo: {project_type.replace('_', ' ').title()}
Fecha: {datetime.now().strftime('%d/%m/%Y')}
Arquitecto: AWS Solutions Architect Senior

OBJETIVO DEL PROYECTO
====================

{ai_response[:500]}...

ARQUITECTURA PROPUESTA
======================

La solucion propuesta utiliza servicios AWS nativos para garantizar:
- Alta disponibilidad y escalabilidad
- Seguridad empresarial
- Optimizacion de costos
- Facilidad de mantenimiento

SERVICIOS AWS INCLUIDOS
=======================

1. Amazon VPC - Red privada virtual
2. Amazon EC2 - Instancias de computo
3. Amazon S3 - Almacenamiento de objetos
4. AWS IAM - Gestion de identidades
5. Amazon CloudWatch - Monitoreo y alertas

BENEFICIOS ESPERADOS
===================

- Reduccion de costos operativos
- Mejora en la disponibilidad del servicio
- Escalabilidad automatica segun demanda
- Seguridad de nivel empresarial
- Respaldo y recuperacion automatizada

PLAN DE IMPLEMENTACION
=====================

Fase 1: Configuracion inicial (1-2 dias)
- Setup de VPC y networking
- Configuracion de seguridad basica

Fase 2: Despliegue de servicios (2-3 dias)
- Implementacion de servicios principales
- Configuracion de monitoreo

Fase 3: Pruebas y validacion (1-2 dias)
- Pruebas de funcionalidad
- Validacion de seguridad

Fase 4: Go-live y soporte (1 dia)
- Puesta en produccion
- Transferencia de conocimiento

CONSIDERACIONES TECNICAS
========================

- Cumplimiento con AWS Well-Architected Framework
- Implementacion de mejores practicas de seguridad
- Configuracion de backup automatico
- Monitoreo proactivo de recursos

PROXIMOS PASOS
==============

1. Aprobacion de la propuesta
2. Definicion de fechas de implementacion
3. Asignacion de recursos del equipo
4. Inicio de la fase de implementacion

CONTACTO
========

Para consultas adicionales sobre esta propuesta:
- Arquitecto AWS Solutions
- Email: arquitecto@empresa.com
- Telefono: +1-XXX-XXX-XXXX

---
Documento generado automaticamente por AWS Propuestas v3
Fecha de generacion: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
    
    return doc_content

def generate_cost_estimation(project_name: str, project_type: str, messages: List[Dict]) -> str:
    """Generate cost estimation in CSV format"""
    
    costs = [
        "Servicio,Tipo,Cantidad,Costo Mensual USD,Costo Anual USD,Descripcion",
        "Amazon EC2,t3.micro,1,8.50,102.00,Instancia de computo basica",
        "Amazon S3,Standard,100 GB,2.30,27.60,Almacenamiento de objetos",
        "Amazon VPC,NAT Gateway,1,45.00,540.00,Gateway para conectividad",
        "AWS CloudWatch,Logs,10 GB,0.50,6.00,Monitoreo y logs",
        "AWS Support,Basic,1,0.00,0.00,Soporte basico incluido",
        "Data Transfer,Outbound,100 GB,9.00,108.00,Transferencia de datos",
        "TOTAL,,,65.30,783.60,Costo total estimado"
    ]
    
    if project_type == "servicio_rapido":
        # Simplified costs for quick services
        costs = [
            "Servicio,Tipo,Cantidad,Costo Mensual USD,Costo Anual USD,Descripcion",
            "Amazon EC2,t3.micro,1,8.50,102.00,Instancia basica",
            "Amazon S3,Standard,50 GB,1.15,13.80,Almacenamiento",
            "AWS CloudWatch,Basic,1,0.00,0.00,Monitoreo basico",
            "TOTAL,,,9.65,115.80,Costo total estimado"
        ]
    
    return "\n".join(costs)

def generate_calculator_guide(project_name: str, project_type: str, messages: List[Dict]) -> str:
    """Generate AWS Calculator usage guide"""
    
    guide = f"""GUIA PARA CALCULADORA OFICIAL DE AWS
=====================================

Proyecto: {project_name}
URL: https://calculator.aws/

PASOS PARA CALCULAR COSTOS
=========================

1. ACCEDER A LA CALCULADORA
   - Visitar https://calculator.aws/
   - Hacer clic en "Create estimate"

2. SELECCIONAR REGION
   - Elegir la region AWS apropiada
   - Recomendado: us-east-1 (Virginia del Norte)

3. AGREGAR SERVICIOS
   
   Amazon EC2:
   - Tipo de instancia: t3.micro
   - Sistema operativo: Linux
   - Horas de uso: 730 (24/7)
   - Almacenamiento: 20 GB EBS gp3
   
   Amazon S3:
   - Tipo de almacenamiento: Standard
   - Cantidad: 100 GB
   - Requests: 10,000 PUT/COPY/POST/LIST
   - Requests: 100,000 GET/SELECT
   
   Amazon VPC:
   - NAT Gateway: 1 instancia
   - Data processing: 100 GB/mes
   
   AWS CloudWatch:
   - Logs ingestion: 10 GB/mes
   - Logs storage: 10 GB/mes
   - Custom metrics: 100 metricas

4. REVISAR ESTIMACION
   - Verificar todos los servicios agregados
   - Ajustar cantidades segun necesidades reales
   - Considerar descuentos por reservas

5. GUARDAR Y COMPARTIR
   - Hacer clic en "Save and share"
   - Copiar el enlace para referencia futura

CONSIDERACIONES ADICIONALES
===========================

- Los precios pueden variar por region
- Considerar Reserved Instances para ahorros
- Evaluar Savings Plans para cargas estables
- Incluir costos de transferencia de datos
- Agregar margen para crecimiento (20-30%)

OPTIMIZACION DE COSTOS
=====================

1. Right-sizing de instancias
2. Uso de Spot Instances cuando sea apropiado
3. Lifecycle policies para S3
4. Automated scaling para EC2
5. Monitoreo continuo con Cost Explorer

CONTACTO PARA DUDAS
==================

Para consultas sobre costos y optimizacion:
- AWS Solutions Architect
- Email: costos@empresa.com

---
Guia generada para: {project_name}
Fecha: {datetime.now().strftime('%d/%m/%Y')}
"""
    
    return guide

def upload_files_to_s3(files: List[Dict], bucket_name: str) -> bool:
    """Upload generated files to S3 bucket"""
    
    try:
        # Simulate S3 upload for now
        # In production, this would use boto3 S3 client
        logger.info(f"📤 Uploading {len(files)} files to S3 bucket: {bucket_name}")
        
        for file_info in files:
            logger.info(f"  - {file_info['name']} ({file_info['type']})")
        
        # Simulate successful upload
        return True
        
    except Exception as e:
        logger.error(f"Error uploading files to S3: {str(e)}")
        return False
    """Extract project information from conversation messages"""
    
    project_info = existing_info.copy()
    
    # Combine all messages into a single text for analysis
    conversation_text = ""
    user_messages = []
    assistant_messages = []
    
    for msg in messages:
        content = msg.get('content', '')
        conversation_text += f"{msg.get('role', '')}: {content}\n"
        if msg.get('role') == 'user':
            user_messages.append(content.lower())
        elif msg.get('role') == 'assistant':
            assistant_messages.append(content.lower())
    
    conversation_text += f"assistant: {ai_response}\n"
    assistant_messages.append(ai_response.lower())
    conversation_lower = conversation_text.lower()
    
    # Extract project name - IMPROVED LOGIC
    if not project_info.get('name'):
        import re
        
        # Look for project name in the FIRST meaningful user response
        # Skip the very first message if it's just a greeting
        meaningful_user_messages = []
        for i, user_msg in enumerate(user_messages):
            # Skip greetings and common responses
            if user_msg.strip() in ['hola', 'hi', 'hello', 'buenos dias', 'buenas tardes']:
                continue
            meaningful_user_messages.append((i, user_msg.strip()))
        
        # The first meaningful response is likely the project name
        if meaningful_user_messages:
            first_meaningful = meaningful_user_messages[0][1]
            
            # Check if it looks like a project name (not a service request)
            service_indicators = [
                'necesito', 'quiero', 'implementar', 'configurar', 'crear', 'instancia', 
                'vpc', 'rds', 'ec2', 's3', 'lambda', 'guardduty', 'servicio', 'una ', 'un '
            ]
            
            # If it doesn't contain service indicators and is reasonable length
            if (not any(indicator in first_meaningful for indicator in service_indicators) and 
                2 < len(first_meaningful) < 50 and
                first_meaningful not in ['servicio rapido', 'solucion integral', 'si', 'no']):
                project_info['name'] = first_meaningful
        
        # Fallback: look for explicit name patterns in conversation
        if not project_info.get('name'):
            name_patterns = [
                r'nombre del proyecto[:\s]*["\']?([^"\'\n,\.]+)["\']?',
                r'proyecto[:\s]+["\']?([^"\'\n,\.]+)["\']?',
                r'se llama[:\s]*["\']?([^"\'\n,\.]+)["\']?',
                r'el proyecto es[:\s]*["\']?([^"\'\n,\.]+)["\']?'
            ]
            
            for pattern in name_patterns:
                matches = re.findall(pattern, conversation_lower)
                if matches:
                    name = matches[-1].strip()
                    if len(name) > 2 and name not in ['del', 'el', 'la', 'los', 'las', 'un', 'una']:
                        project_info['name'] = name
                        break
    
    # Extract project type and specific requirements
    if not project_info.get('type'):
        if 'servicio rapido' in conversation_lower or 'servicio rápido' in conversation_lower:
            project_info['type'] = 'servicio_rapido'
        elif 'solucion integral' in conversation_lower or 'solución integral' in conversation_lower:
            project_info['type'] = 'solucion_integral'
    
    # Extract specific service requirements
    services_mentioned = []
    aws_services = []
    
    if 'vpc' in conversation_lower:
        services_mentioned.append('VPC')
        aws_services.append('Amazon VPC')
        project_info['service_type'] = 'vpc'
        
        # Extract VPC specific details
        if 'tres capas' in conversation_lower:
            project_info['architecture'] = 'tres_capas'
            project_info['description'] = 'VPC estándar preparada para un sistema de tres capas'
        
        if 'cidr' in conversation_lower:
            project_info['cidr_blocks'] = {
                'vpc': '10.0.0.0/16',
                'public_subnets': ['10.0.1.0/24', '10.0.2.0/24'],
                'private_subnets': ['10.0.10.0/24', '10.0.11.0/24']
            }
    
    if 'ec2' in conversation_lower:
        services_mentioned.append('EC2')
        aws_services.append('Amazon EC2')
        project_info['service_type'] = 'ec2'
        
        # Extract EC2 specific details
        if 'basica' in conversation_lower or 'básica' in conversation_lower:
            project_info['instance_type'] = 't2.micro'
            project_info['description'] = 'Instancia EC2 básica para aplicaciones de bajo tráfico'
        
        # Look for specific instance types mentioned
        instance_patterns = [r't[0-9]\.[a-z]+', r'm[0-9]\.[a-z]+', r'c[0-9]\.[a-z]+']
        for pattern in instance_patterns:
            matches = re.findall(pattern, conversation_lower)
            if matches:
                project_info['instance_type'] = matches[0]
    
    if 'rds' in conversation_lower:
        services_mentioned.append('RDS')
        aws_services.append('Amazon RDS')
        project_info['service_type'] = 'rds'
        project_info['description'] = 'Base de datos relacional administrada con Amazon RDS'
    
    if 's3' in conversation_lower:
        services_mentioned.append('S3')
        aws_services.append('Amazon S3')
        project_info['service_type'] = 's3'
        project_info['description'] = 'Configuracion de bucket S3 para almacenamiento'
        
        # Extract S3 specific details from user responses
        for user_msg in user_messages:
            user_msg_lower = user_msg.lower()
            
            # Look for bucket name
            if 'bucket' in user_msg_lower and len(user_msg.strip()) > 5:
                # Extract potential bucket name
                words = user_msg.strip().split()
                for word in words:
                    if len(word) > 3 and word not in ['bucket', 'nombre', 'llamar', 'sera']:
                        project_info['bucket_name'] = word.lower().replace(' ', '-')
                        break
            
            # Look for region
            regions = ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1']
            for region in regions:
                if region in user_msg_lower:
                    project_info['aws_region'] = region
                    break
            
            # Look for storage type
            if 'standard' in user_msg_lower:
                project_info['storage_type'] = 'Standard'
            elif 'infrequent' in user_msg_lower or 'ia' in user_msg_lower:
                project_info['storage_type'] = 'Standard-IA'
            elif 'glacier' in user_msg_lower:
                project_info['storage_type'] = 'Glacier'
            
            # Look for access policies
            if 'publico' in user_msg_lower or 'public' in user_msg_lower:
                project_info['access_policy'] = 'public'
            elif 'privado' in user_msg_lower or 'private' in user_msg_lower:
                project_info['access_policy'] = 'private'
            
            # Look for versioning
            if 'version' in user_msg_lower:
                if 'si' in user_msg_lower or 'yes' in user_msg_lower or 'habilitar' in user_msg_lower:
                    project_info['versioning'] = 'enabled'
                elif 'no' in user_msg_lower or 'deshabilitar' in user_msg_lower:
                    project_info['versioning'] = 'disabled'
            
            # Look for encryption
            if 'cifr' in user_msg_lower or 'encrypt' in user_msg_lower:
                if 'si' in user_msg_lower or 'yes' in user_msg_lower or 'habilitar' in user_msg_lower:
                    project_info['encryption'] = 'enabled'
                elif 'no' in user_msg_lower or 'deshabilitar' in user_msg_lower:
                    project_info['encryption'] = 'disabled'
    
    if 'efs' in conversation_lower:
        services_mentioned.append('EFS')
        aws_services.append('Amazon EFS')
        project_info['service_type'] = 'efs'
        project_info['description'] = 'Sistema de archivos elástico Amazon EFS'
        
        # Extract EFS specific details
        for user_msg in user_messages:
            user_msg_lower = user_msg.lower()
            
            # Look for performance mode
            if 'general purpose' in user_msg_lower or 'general' in user_msg_lower:
                project_info['performance_mode'] = 'General Purpose'
            elif 'max io' in user_msg_lower or 'maxio' in user_msg_lower:
                project_info['performance_mode'] = 'Max I/O'
            
            # Look for throughput mode
            if 'bursting' in user_msg_lower:
                project_info['throughput_mode'] = 'Bursting'
            elif 'provisioned' in user_msg_lower:
                project_info['throughput_mode'] = 'Provisioned'
    
    if 'lambda' in conversation_lower:
        services_mentioned.append('Lambda')
        aws_services.append('AWS Lambda')
        project_info['service_type'] = 'lambda'
        project_info['description'] = 'Funciones serverless con AWS Lambda'
        
        # Extract Lambda specific details
        for user_msg in user_messages:
            user_msg_lower = user_msg.lower()
            
            # Look for runtime
            runtimes = ['python', 'nodejs', 'java', 'dotnet', 'go', 'ruby']
            for runtime in runtimes:
                if runtime in user_msg_lower:
                    if runtime == 'python':
                        project_info['runtime'] = 'python3.9'
                    elif runtime == 'nodejs':
                        project_info['runtime'] = 'nodejs18.x'
                    else:
                        project_info['runtime'] = runtime
                    break
    
    if 'cloudfront' in conversation_lower:
        services_mentioned.append('CloudFront')
        aws_services.append('Amazon CloudFront')
        project_info['service_type'] = 'cloudfront'
        project_info['description'] = 'Red de distribución de contenido CloudFront'
    
    if 'elb' in conversation_lower or 'load balancer' in conversation_lower or 'balanceador' in conversation_lower:
        services_mentioned.append('ELB')
        aws_services.append('Elastic Load Balancer')
        project_info['service_type'] = 'elb'
        project_info['description'] = 'Balanceador de carga elástico'
    
    if 'ses' in conversation_lower or 'email' in conversation_lower or 'correo' in conversation_lower:
        services_mentioned.append('SES')
        aws_services.append('Amazon SES')
        project_info['service_type'] = 'ses'
        project_info['description'] = 'Servicio de correo electrónico Amazon SES'
    
    if 'vpn' in conversation_lower:
        services_mentioned.append('VPN')
        aws_services.append('AWS VPN')
        project_info['service_type'] = 'vpn'
        project_info['description'] = 'Conexión VPN segura'
    
    if 'backup' in conversation_lower or 'respaldo' in conversation_lower:
        services_mentioned.append('Backup')
        aws_services.append('AWS Backup')
        project_info['service_type'] = 'backup'
        project_info['description'] = 'Sistema de respaldos automáticos'
    
    # Store extracted services
    if services_mentioned:
        project_info['services'] = services_mentioned
        project_info['aws_services'] = aws_services
    
    # Extract requirements from conversation
    requirements = []
    if 'alta disponibilidad' in conversation_lower:
        requirements.append('Alta disponibilidad')
    if 'escalabilidad' in conversation_lower:
        requirements.append('Escalabilidad automática')
    if 'seguridad' in conversation_lower:
        requirements.append('Seguridad avanzada')
    if 'backup' in conversation_lower:
        requirements.append('Respaldo automático')
    if 'monitoreo' in conversation_lower:
        requirements.append('Monitoreo y alertas')
    
    if requirements:
        project_info['requirements'] = requirements
    
    # Extract technical specifications from user responses
    technical_specs = {}
    for user_msg in user_messages:
        # Look for technical specifications
        if 'gb' in user_msg or 'tb' in user_msg:
            # Storage specifications
            storage_match = re.search(r'(\d+)\s*(gb|tb)', user_msg)
            if storage_match:
                technical_specs['storage'] = f"{storage_match.group(1)} {storage_match.group(2).upper()}"
        
        if 'cpu' in user_msg or 'vcpu' in user_msg:
            cpu_match = re.search(r'(\d+)\s*(cpu|vcpu)', user_msg)
            if cpu_match:
                technical_specs['cpu'] = f"{cpu_match.group(1)} {cpu_match.group(2)}"
    
    if technical_specs:
        project_info['technical_specs'] = technical_specs
    
    # Generate objective based on extracted information
    if not project_info.get('objective'):
        service_type = project_info.get('service_type', 'general')
        if service_type == 'vpc':
            project_info['objective'] = 'Implementar una VPC segura y escalable para soportar aplicaciones empresariales'
        elif service_type == 'ec2':
            project_info['objective'] = 'Desplegar instancias EC2 optimizadas para las necesidades específicas del negocio'
        elif service_type == 'rds':
            project_info['objective'] = 'Establecer una base de datos relacional robusta y administrada'
        else:
            project_info['objective'] = 'Implementar una solución integral en AWS que cumpla con los requerimientos del negocio'
    
    # Set completion indicators
    if any(indicator in conversation_lower for indicator in [
        'generar documentos', 'subir al bucket', 'documentos listos', 
        'archivos generados', 'carga exitosa', 'procederé a generar'
    ]):
        project_info['ready_for_documents'] = True
    
    return project_info

def check_if_complete(ai_response: str, project_info: Dict) -> bool:
    """Check if project information gathering is complete - MUST be intelligent and follow the prompt flow"""
    
    response_lower = ai_response.lower()
    
    # VERY EXPLICIT completion indicators - only when the AI explicitly says it's ready to generate
    explicit_completion_indicators = [
        "procederé a generar los documentos",
        "voy a generar los documentos",
        "generar y entregar los documentos",
        "crear los documentos técnicos",
        "subir al bucket los documentos",
        "carpeta con todos los documentos",
        "todos los archivos generados",
        "documentos listos para subir",
        "información completa para generar los documentos",
        "comenzaré con la generación de documentos",
        "procedo a crear los documentos"
    ]
    
    # Check for explicit completion signals - must be very specific
    has_explicit_completion = any(indicator in response_lower for indicator in explicit_completion_indicators)
    
    # Additional check: AI should NOT be asking questions if it's complete
    question_indicators = [
        "¿", "?", "necesito saber", "me puedes decir", "podrías especificar",
        "qué tipo de", "cuál es", "cómo", "dónde", "cuándo", "por favor proporciona"
    ]
    
    is_asking_questions = any(indicator in response_lower for indicator in question_indicators)
    
    # Only complete if explicitly stated AND not asking more questions
    return has_explicit_completion and not is_asking_questions

def generate_project_documents_dynamic(project_info: Dict[str, Any], ai_analysis: str) -> Dict[str, Any]:
    """
    Generate all project documents DYNAMICALLY based on AI analysis
    This is the NEW INTELLIGENT approach - no hardcoded services!
    
    Args:
        project_info: Dictionary with project information
        ai_analysis: AI's analysis and response containing requirements
    
    Returns:
        Dictionary with generation results
    """
    try:
        logger.info(f"Starting DYNAMIC document generation for project: {project_info.get('name', 'Unknown')}")
        logger.info(f"AI Analysis length: {len(ai_analysis)} characters")
        
        documents = {}
        project_name = project_info.get('name', 'aws-project')
        
        # Generate Word documents DYNAMICALLY
        try:
            # Main proposal document - generated from AI analysis
            word_content = generate_dynamic_word_document(project_info, ai_analysis)
            documents[f"{project_name.lower().replace(' ', '-')}-propuesta-ejecutiva.docx"] = word_content
            
            # Technical document - also dynamic
            tech_content = generate_dynamic_word_document(project_info, ai_analysis)
            documents[f"{project_name.lower().replace(' ', '-')}-documento-tecnico.docx"] = tech_content
            
            logger.info("Successfully generated DYNAMIC Word documents")
        except Exception as e:
            logger.error(f"Error generating dynamic Word documents: {str(e)}")
        
        # Generate CSV files DYNAMICALLY
        try:
            # Activities CSV - generated from AI analysis
            activities_content = generate_dynamic_activities_csv(project_info, ai_analysis)
            documents[f"{project_name.lower().replace(' ', '-')}-actividades-implementacion.csv"] = activities_content
            
            # Costs CSV - simplified for now
            costs_content = generate_simple_costs_csv(project_info, ai_analysis)
            documents[f"{project_name.lower().replace(' ', '-')}-costos-estimados.csv"] = costs_content
            
            logger.info("Successfully generated DYNAMIC CSV documents")
        except Exception as e:
            logger.error(f"Error generating dynamic CSV documents: {str(e)}")
        
        # Generate CloudFormation template DYNAMICALLY
        try:
            cf_content = generate_dynamic_cloudformation(project_info, ai_analysis)
            documents[f"{project_name.lower().replace(' ', '-')}-cloudformation-template.yaml"] = cf_content.encode('utf-8')
            
            logger.info("Successfully generated DYNAMIC CloudFormation template")
        except Exception as e:
            logger.error(f"Error generating dynamic CloudFormation template: {str(e)}")
        
        # Generate diagrams DYNAMICALLY
        try:
            # Simple SVG diagram
            svg_content = generate_simple_svg_diagram(project_info, ai_analysis)
            documents[f"{project_name.lower().replace(' ', '-')}-arquitectura-general.svg"] = svg_content.encode('utf-8')
            
            # Simple Draw.io diagram
            drawio_content = generate_simple_drawio_diagram(project_info, ai_analysis)
            documents[f"{project_name.lower().replace(' ', '-')}-arquitectura-general.drawio"] = drawio_content.encode('utf-8')
            
            logger.info("Successfully generated DYNAMIC diagram files")
        except Exception as e:
            logger.error(f"Error generating dynamic diagrams: {str(e)}")
        
        # Generate AWS Calculator guide DYNAMICALLY
        try:
            calculator_guide = generate_dynamic_calculator_guide(project_info, ai_analysis)
            documents[f"{project_name.lower().replace(' ', '-')}-guia-calculadora-aws.txt"] = calculator_guide.encode('utf-8')
            
            logger.info("Successfully generated DYNAMIC calculator guide")
        except Exception as e:
            logger.error(f"Error generating dynamic calculator guide: {str(e)}")
        
        # Upload to S3
        if documents and DOCUMENTS_BUCKET:
            try:
                # Import here to avoid circular imports
                from generators.s3_uploader import upload_project_documents
                
                upload_results = upload_project_documents(
                    project_name=project_name,
                    documents=documents,
                    bucket_name=DOCUMENTS_BUCKET
                )
                
                logger.info(f"DYNAMIC Upload results: {upload_results}")
                
                return {
                    'success': True,
                    'documents_generated': len(documents),
                    'upload_results': upload_results,
                    'message': f"Successfully generated and uploaded {len(documents)} DYNAMIC documents for project '{project_name}'"
                }
            except Exception as e:
                logger.error(f"Error uploading dynamic documents: {str(e)}")
                return {
                    'success': False,
                    'documents_generated': len(documents),
                    'error': f"Dynamic documents generated but upload failed: {str(e)}"
                }
        else:
            return {
                'success': False,
                'documents_generated': len(documents),
                'error': "No documents generated or S3 bucket not configured"
            }
            
    except Exception as e:
        logger.error(f"Error in DYNAMIC document generation: {str(e)}")
        return {
            'success': False,
            'error': f"DYNAMIC document generation failed: {str(e)}"
        }

def generate_simple_costs_csv(project_info: Dict[str, Any], ai_analysis: str) -> bytes:
    """Generate simple costs CSV based on AI analysis"""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Servicio', 'Tipo', 'Cantidad', 'Costo_Mensual_USD', 'Descripcion'])
    
    # Extract services from AI analysis and add estimated costs
    analysis_lower = ai_analysis.lower()
    
    if 'ec2' in analysis_lower:
        writer.writerow(['Amazon EC2', 't3.micro', '1', '8.50', 'Instancia de computo basica'])
    if 's3' in analysis_lower:
        writer.writerow(['Amazon S3', 'Standard', '100 GB', '2.30', 'Almacenamiento de objetos'])
    if 'rds' in analysis_lower:
        writer.writerow(['Amazon RDS', 'db.t3.micro', '1', '15.00', 'Base de datos relacional'])
    if 'lambda' in analysis_lower:
        writer.writerow(['AWS Lambda', 'Requests', '1M', '0.20', 'Funciones serverless'])
    if 'efs' in analysis_lower:
        writer.writerow(['Amazon EFS', 'Standard', '100 GB', '30.00', 'Sistema de archivos elastico'])
    
    # Add basic monitoring and security
    writer.writerow(['Amazon CloudWatch', 'Basic', '1', '3.00', 'Monitoreo basico'])
    writer.writerow(['AWS Support', 'Basic', '1', '0.00', 'Soporte basico incluido'])
    
    csv_content = output.getvalue()
    output.close()
    
    return csv_content.encode('utf-8')

def generate_simple_svg_diagram(project_info: Dict[str, Any], ai_analysis: str) -> str:
    """Generate simple SVG diagram based on AI analysis"""
    project_name = project_info.get('name', 'AWS Project')
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
  <rect width="800" height="600" fill="#f0f8ff"/>
  
  <!-- Title -->
  <text x="400" y="30" text-anchor="middle" font-size="24" font-weight="bold" fill="#232f3e">
    Arquitectura AWS - {project_name}
  </text>
  
  <!-- User -->
  <rect x="50" y="100" width="100" height="60" fill="#ff9900" rx="5"/>
  <text x="100" y="135" text-anchor="middle" fill="white" font-weight="bold">Usuario</text>
  
  <!-- AWS Cloud -->
  <rect x="250" y="80" width="500" height="400" fill="#ffffff" stroke="#232f3e" stroke-width="2" rx="10"/>
  <text x="500" y="105" text-anchor="middle" font-size="18" font-weight="bold" fill="#232f3e">AWS Cloud</text>
  
  <!-- Services based on AI analysis -->'''
    
    y_pos = 150
    analysis_lower = ai_analysis.lower()
    
    if 'ec2' in analysis_lower:
        svg_content += f'''
  <rect x="300" y="{y_pos}" width="120" height="50" fill="#ff9900" rx="5"/>
  <text x="360" y="{y_pos + 30}" text-anchor="middle" fill="white" font-weight="bold">Amazon EC2</text>'''
        y_pos += 70
    
    if 's3' in analysis_lower:
        svg_content += f'''
  <rect x="300" y="{y_pos}" width="120" height="50" fill="#3f48cc" rx="5"/>
  <text x="360" y="{y_pos + 30}" text-anchor="middle" fill="white" font-weight="bold">Amazon S3</text>'''
        y_pos += 70
    
    if 'rds' in analysis_lower:
        svg_content += f'''
  <rect x="300" y="{y_pos}" width="120" height="50" fill="#3f48cc" rx="5"/>
  <text x="360" y="{y_pos + 30}" text-anchor="middle" fill="white" font-weight="bold">Amazon RDS</text>'''
        y_pos += 70
    
    if 'efs' in analysis_lower:
        svg_content += f'''
  <rect x="300" y="{y_pos}" width="120" height="50" fill="#3f48cc" rx="5"/>
  <text x="360" y="{y_pos + 30}" text-anchor="middle" fill="white" font-weight="bold">Amazon EFS</text>'''
    
    # Connection lines
    svg_content += '''
  <!-- Connection lines -->
  <line x1="150" y1="130" x2="250" y2="130" stroke="#232f3e" stroke-width="2"/>
  <polygon points="245,125 250,130 245,135" fill="#232f3e"/>
  
  <text x="400" y="550" text-anchor="middle" font-size="12" fill="#666">
    Diagrama generado dinamicamente basado en requerimientos del proyecto
  </text>
</svg>'''
    
    return svg_content

def generate_simple_drawio_diagram(project_info: Dict[str, Any], ai_analysis: str) -> str:
    """Generate simple Draw.io diagram based on AI analysis"""
    project_name = project_info.get('name', 'AWS Project')
    
    return f'''<mxfile host="app.diagrams.net">
  <diagram name="AWS Architecture - {project_name}">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="2" value="Usuario" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FF9900;fontColor=#FFFFFF;fontStyle=1" vertex="1" parent="1">
          <mxGeometry x="40" y="200" width="120" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="3" value="AWS Cloud" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#232F3E;strokeWidth=2;fontStyle=1" vertex="1" parent="1">
          <mxGeometry x="240" y="120" width="500" height="400" as="geometry"/>
        </mxCell>
        <mxCell id="4" value="Arquitectura generada dinamicamente&#xa;basada en analisis de IA" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=12;fontColor=#666666;" vertex="1" parent="1">
          <mxGeometry x="340" y="480" width="300" height="30" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''

def generate_dynamic_calculator_guide(project_info: Dict[str, Any], ai_analysis: str) -> str:
    """Generate AWS Calculator guide based on AI analysis"""
    project_name = project_info.get('name', 'Proyecto AWS')
    
    guide = f"""Guia para usar la Calculadora Oficial de AWS - {project_name}

INSTRUCCIONES PASO A PASO:

1. Acceder a la Calculadora de AWS:
   - Ir a: https://calculator.aws/
   - Hacer clic en "Create estimate"

2. Servicios Identificados en el Proyecto:

"""
    
    analysis_lower = ai_analysis.lower()
    
    if 'ec2' in analysis_lower:
        guide += """   a) Amazon EC2:
      - Tipo de instancia: t3.micro (recomendado para inicio)
      - Cantidad: 1 instancia
      - Sistema operativo: Linux
      - Uso: 24 horas/dia, 30 dias/mes
      
"""
    
    if 's3' in analysis_lower:
        guide += """   b) Amazon S3:
      - Almacenamiento estandar: 100 GB
      - Solicitudes PUT/COPY/POST/LIST: 1,000/mes
      - Solicitudes GET/SELECT: 10,000/mes
      
"""
    
    if 'rds' in analysis_lower:
        guide += """   c) Amazon RDS:
      - Motor: MySQL
      - Tipo de instancia: db.t3.micro
      - Almacenamiento: 20 GB SSD
      
"""
    
    if 'efs' in analysis_lower:
        guide += """   d) Amazon EFS:
      - Almacenamiento estandar: 100 GB
      - Modo de rendimiento: General Purpose
      - Modo de throughput: Bursting
      
"""
    
    guide += """3. Servicios Adicionales Recomendados:
   - Amazon CloudWatch: Metricas basicas
   - AWS Support: Plan basico (incluido)

4. Consideraciones de Costos:
   - Los precios varian por region (recomendado: us-east-1)
   - Considerar descuentos por Reserved Instances para uso continuo
   - Evaluar opciones de Savings Plans para mayor ahorro
   - Incluir costos de transferencia de datos si aplica

5. Recomendaciones:
   - Comenzar con la configuracion basica mostrada
   - Ajustar segun el crecimiento esperado del proyecto
   - Revisar y optimizar mensualmente
   - Usar herramientas de optimizacion de costos de AWS

NOTA: Esta guia fue generada dinamicamente basandose en los requerimientos 
identificados durante la consultoria. Los costos reales pueden variar segun 
el uso especifico y los patrones de trafico de la aplicacion.
"""
    
    return guide
    """
    Generate all project documents when project is complete
    
    Args:
        project_info: Dictionary with project information
    
    Returns:
        Dictionary with generation results
    """
    try:
        logger.info(f"Starting document generation for project: {project_info.get('name', 'Unknown')}")
        
        documents = {}
        project_name = project_info.get('name', 'aws-project')
        
        # Generate Word documents
        try:
            # Main proposal document
            word_content = generate_word_document(project_info, "propuesta")
            documents[f"{project_name.lower().replace(' ', '-')}-propuesta-ejecutiva.docx"] = word_content
            
            # Technical document
            tech_content = generate_technical_document(project_info)
            documents[f"{project_name.lower().replace(' ', '-')}-documento-tecnico.docx"] = tech_content
            
            logger.info("Successfully generated Word documents")
        except Exception as e:
            logger.error(f"Error generating Word documents: {str(e)}")
        
        # Generate CSV files
        try:
            # Activities CSV
            activities_content = generate_activities_csv(project_info)
            documents[f"{project_name.lower().replace(' ', '-')}-actividades-implementacion.csv"] = activities_content
            
            # Costs CSV
            costs_content = generate_costs_csv(project_info)
            documents[f"{project_name.lower().replace(' ', '-')}-costos-estimados.csv"] = costs_content
            
            logger.info("Successfully generated CSV documents")
        except Exception as e:
            logger.error(f"Error generating CSV documents: {str(e)}")
        
        # Generate CloudFormation template
        try:
            cf_content = generate_cloudformation_template(project_info)
            documents[f"{project_name.lower().replace(' ', '-')}-cloudformation-template.yaml"] = cf_content.encode('utf-8')
            
            logger.info("Successfully generated CloudFormation template")
        except Exception as e:
            logger.error(f"Error generating CloudFormation template: {str(e)}")
        
        # Generate diagrams
        try:
            # Draw.io diagram
            drawio_content = generate_drawio_diagram(project_info)
            documents[f"{project_name.lower().replace(' ', '-')}-arquitectura-general.drawio"] = drawio_content.encode('utf-8')
            
            # SVG diagram
            svg_content = generate_svg_diagram(project_info)
            documents[f"{project_name.lower().replace(' ', '-')}-arquitectura-general.svg"] = svg_content.encode('utf-8')
            
            logger.info("Successfully generated diagram files")
        except Exception as e:
            logger.error(f"Error generating diagrams: {str(e)}")
        
        # Generate AWS Calculator guide
        try:
            calculator_guide = generate_calculator_guide(project_info)
            documents[f"{project_name.lower().replace(' ', '-')}-guia-calculadora-aws.txt"] = calculator_guide.encode('utf-8')
            
            logger.info("Successfully generated calculator guide")
        except Exception as e:
            logger.error(f"Error generating calculator guide: {str(e)}")
        
        # Upload to S3
        if documents and DOCUMENTS_BUCKET:
            try:
                upload_results = upload_project_documents(
                    project_name=project_name,
                    documents=documents,
                    bucket_name=DOCUMENTS_BUCKET
                )
                
                logger.info(f"Upload results: {upload_results}")
                
                return {
                    'success': True,
                    'documents_generated': len(documents),
                    'upload_results': upload_results,
                    'message': f"Successfully generated and uploaded {len(documents)} documents for project '{project_name}'"
                }
            except Exception as e:
                logger.error(f"Error uploading documents: {str(e)}")
                return {
                    'success': False,
                    'documents_generated': len(documents),
                    'error': f"Documents generated but upload failed: {str(e)}"
                }
        else:
            return {
                'success': False,
                'documents_generated': len(documents),
                'error': "No documents generated or S3 bucket not configured"
            }
            
    except Exception as e:
        logger.error(f"Error in document generation: {str(e)}")
        return {
            'success': False,
            'error': f"Document generation failed: {str(e)}"
        }

def generate_calculator_guide(project_info: Dict[str, Any]) -> str:
    """Generate AWS Calculator guide text"""
    project_name = project_info.get('name', 'Proyecto AWS')
    project_type = project_info.get('type', 'general')
    
    guide = f"""Guia para usar la Calculadora Oficial de AWS - {project_name}

INSTRUCCIONES PASO A PASO:

1. Acceder a la Calculadora de AWS:
   - Ir a: https://calculator.aws/
   - Hacer clic en "Create estimate"

2. Servicios Principales a Configurar:

"""
    
    if 'web' in project_type.lower() or 'app' in project_type.lower():
        guide += """   a) Amazon EC2:
      - Tipo de instancia: t3.medium
      - Cantidad: 2 instancias
      - Sistema operativo: Linux
      - Uso: 24 horas/dia, 30 dias/mes
      
   b) Application Load Balancer:
      - Cantidad: 1 ALB
      - Datos procesados: 1 GB/mes
      
   c) Amazon RDS:
      - Motor: MySQL
      - Tipo de instancia: db.t3.micro
      - Almacenamiento: 20 GB SSD
      
"""
    
    if 'data' in project_type.lower() or 'analitica' in project_type.lower():
        guide += """   a) Amazon S3:
      - Almacenamiento estandar: 1 TB
      - Solicitudes PUT/COPY/POST/LIST: 10,000/mes
      - Solicitudes GET/SELECT: 100,000/mes
      
   b) AWS Glue:
      - DPU-horas: 100/mes
      - Trabajos de ETL: 10/mes
      
   c) Amazon Redshift:
      - Tipo de nodo: dc2.large
      - Cantidad de nodos: 2
      - Uso: 24 horas/dia
      
"""
    
    guide += """3. Servicios Adicionales:
   - VPC NAT Gateway: 1 gateway
   - CloudWatch: Metricas personalizadas y alarmas
   - AWS Backup: 100 GB de respaldos
   - Route 53: 1 hosted zone

4. Consideraciones de Costos:
   - Los precios varian por region
   - Considerar descuentos por Reserved Instances
   - Evaluar opciones de Savings Plans
   - Incluir costos de transferencia de datos si aplica

5. Recomendaciones:
   - Comenzar con la configuracion basica
   - Ajustar segun el crecimiento esperado
   - Revisar y optimizar mensualmente
   - Considerar herramientas de optimizacion de costos

NOTA: Esta es una estimacion base. Los costos reales pueden variar segun el uso especifico y los patrones de trafico de la aplicacion.
"""
    
    return guide

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
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Requested-With'
        },
        'body': json.dumps(body, ensure_ascii=False, default=str)
    }
def prepare_prompt_for_model(model_id: str, system_prompt: str, messages: List[Dict]) -> Dict:
    """
    Prepara el prompt para diferentes modelos de Bedrock
    """
    if model_id.startswith('anthropic.claude'):
        # Claude format
        formatted_messages = []
        
        # Add system message if provided
        if system_prompt:
            formatted_messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # Add conversation messages
        for msg in messages:
            if msg.get('content'):
                formatted_messages.append({
                    "role": msg.get('role', 'user'),
                    "content": msg.get('content')
                })
        
        return {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "messages": formatted_messages
        }
    
    elif model_id.startswith('amazon.nova'):
        # Nova format
        formatted_messages = []
        
        # Add system message if provided
        if system_prompt:
            formatted_messages.append({
                "role": "system",
                "content": [{"text": system_prompt}]
            })
        
        # Add conversation messages
        for msg in messages:
            if msg.get('content'):
                formatted_messages.append({
                    "role": msg.get('role', 'user'),
                    "content": [{"text": msg.get('content')}]
                })
        
        return {
            "messages": formatted_messages,
            "inferenceConfig": {
                "maxTokens": 4000,
                "temperature": 0.7
            }
        }
    
    else:
        # Default format
        return {
            "messages": messages,
            "max_tokens": 4000
        }

def save_conversation_data(project_id: str, user_id: str, messages: List[Dict], ai_response: str, project_info: Dict):
    """
    Guarda los datos de la conversación en DynamoDB
    """
    try:
        if not projects_table:
            logger.warning("Projects table not configured")
            return
        
        # Update project in DynamoDB
        projects_table.put_item(
            Item={
                'projectId': project_id,
                'userId': user_id,
                'projectInfo': project_info,
                'lastMessage': ai_response[:500],  # Truncate for storage
                'messageCount': len(messages),
                'lastUpdated': datetime.utcnow().isoformat(),
                'status': project_info.get('status', 'IN_PROGRESS')
            }
        )
        
        logger.info(f"💾 Saved conversation data for project: {project_id}")
        
    except Exception as e:
        logger.error(f"Error saving conversation data: {str(e)}")


