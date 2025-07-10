import json
import boto3
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any
import logging

# Import document generators
from generators.word_generator import generate_word_document, generate_technical_document
from generators.csv_generator import generate_activities_csv, generate_costs_csv
from generators.cloudformation_generator import generate_cloudformation_template
from generators.diagram_generator import generate_drawio_diagram, generate_svg_diagram
from generators.s3_uploader import upload_project_documents, list_project_documents

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
        
        if not messages:
            return create_response(400, {'error': 'Messages are required'})
        
        # System prompt for arquitecto mode
        system_prompt = get_arquitecto_system_prompt()
        
        # Prepare prompt for Bedrock
        prompt_body = prepare_prompt(model_id, system_prompt, messages, project_info, current_step)
        
        logger.info(f"🏗️ ARQUITECTO USING MODEL: {model_id}")
        logger.info(f"Prompt body keys: {list(prompt_body.keys())}")
        
        # Call Bedrock
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps(prompt_body),
            contentType='application/json'
        )
        
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
        
        # Extract and update project information from conversation
        project_info = extract_project_info_from_conversation(messages, ai_response, project_info)
        
        # Check if project is complete
        is_complete = check_if_complete(ai_response, project_info)
        
        # Generate documents if project is complete
        document_generation_results = None
        if is_complete:
            # Use project name from extracted info or generate a default one
            project_name = project_info.get('name', f'proyecto-{project_id[:8]}')
            logger.info(f"Project '{project_name}' is complete. Starting document generation...")
            document_generation_results = generate_project_documents(project_info)
            
            # Update AI response to include document generation status
            if document_generation_results.get('success'):
                ai_response += f"\n\n✅ **DOCUMENTOS GENERADOS EXITOSAMENTE**\n\n"
                ai_response += f"He generado y subido {document_generation_results.get('documents_generated', 0)} documentos al bucket S3:\n"
                ai_response += f"- Propuesta ejecutiva (Word)\n"
                ai_response += f"- Documento tecnico (Word)\n"
                ai_response += f"- Plan de actividades (CSV)\n"
                ai_response += f"- Estimacion de costos (CSV)\n"
                ai_response += f"- Template CloudFormation (YAML)\n"
                ai_response += f"- Diagramas de arquitectura (SVG, Draw.io)\n"
                ai_response += f"- Guia de calculadora AWS (TXT)\n\n"
                ai_response += f"Todos los archivos estan organizados en la carpeta '{project_info.get('name')}' del bucket S3.\n\n"
                ai_response += f"¿Deseas agregar algun comentario o ajuste final antes de cerrar este proyecto?"
            else:
                ai_response += f"\n\n⚠️ **ERROR EN GENERACION DE DOCUMENTOS**\n\n"
                ai_response += f"Hubo un problema generando los documentos: {document_generation_results.get('error', 'Error desconocido')}\n"
                ai_response += f"Por favor, intenta nuevamente o contacta al administrador del sistema."
        
        # Save project progress
        if projects_table:
            save_project_progress(project_id, user_id, messages, ai_response, project_info, 
                                current_step + 1, is_complete, model_id)
        
        response_data = {
            'response': ai_response,
            'modelId': model_id,
            'projectId': project_id,
            'currentStep': current_step + 1,
            'isComplete': is_complete,
            'usage': usage,
            'documentGeneration': document_generation_results
        }
        
        logger.info(f"✅ ARQUITECTO SUCCESS - Response length: {len(ai_response)}")
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
    """Get system prompt for arquitecto mode"""
    bucket_name = DOCUMENTS_BUCKET or 'aws-propuestas-v3-documents-prod'
    
    return f"""Actua como arquitecto de soluciones AWS y consultor experto. Vamos a dimensionar, documentar y entregar una solucion profesional en AWS, siguiendo mejores practicas y generando todos los archivos necesarios para una propuesta ejecutiva. No uses acentos ni caracteres especiales en ningun texto, archivo, script ni documento. Asegura que todos los archivos Word generados sean funcionales y compatibles: entrega solo texto plano, sin imagenes, sin tablas complejas, ni formato avanzado, solo texto estructurado, claro y legible. Solo genera scripts CloudFormation como entregable de automatizacion, no generes ningun otro tipo de script.

IMPORTANTE: Cuando el usuario inicie la conversacion, pregunta INMEDIATAMENTE por el nombre del proyecto. No pidas que describa el proyecto primero.

1. **PRIMERA PREGUNTA OBLIGATORIA:**
¿Cual es el nombre del proyecto?

2. **SEGUNDA PREGUNTA:**
El proyecto es una solucion integral (como migracion, aplicacion nueva, modernizacion, analitica, seguridad, IA, IoT, data lake, networking, DRP, VDI, integracion, etc.)
o es un servicio rapido especifico (implementacion de instancias EC2, RDS, SES, VPN, ELB, S3, VPC, CloudFront, SSO, backup, etc.)

**Si elige "servicio rapido especifico":**

1. Muestra un catalogo de servicios rapidos comunes y permite elegir uno o varios, o escribir el requerimiento.
2. Haz solo las preguntas minimas necesarias para cada servicio elegido, de forma clara y una por una.
3. Con la informacion, genera y entrega SIEMPRE:
    - Tabla de actividades de implementacion (CSV o Excel, clara y lista para importar o compartir, SIN acentos ni caracteres especiales).
    - Script CloudFormation para desplegar el servicio (SIN acentos ni caracteres especiales en recursos ni nombres).
    - Diagrama de arquitectura en SVG, PNG y Draw.io editable (nombres y etiquetas SIN acentos ni caracteres especiales).
    - Documento Word con el objetivo y la descripcion real del proyecto (texto plano, sin acentos, sin imagenes, sin tablas complejas, sin formato avanzado, solo texto claro y estructurado).
    - Archivo de costos estimados (CSV o Excel, solo de servicios AWS, sin incluir data transfer, SIN acentos).
    - Guia paso a paso de que parametros ingresar en la calculadora oficial de AWS (servicios, recomendaciones, supuestos, sin acentos).
4. Al finalizar la entrevista, genera automaticamente todos los documentos y los sube al bucket S3 del sistema ({bucket_name}).
5. Sube todos los archivos en una carpeta con el nombre del proyecto y confirma que la carga fue exitosa.
6. Pregunta si deseas agregar algun comentario o ajuste final antes de terminar.

**Si elige "solucion integral" (proyecto complejo):**

1. Haz una entrevista guiada, una pregunta a la vez, para capturar:
    - Nombre del proyecto (si no lo has hecho ya)
    - Tipo de solucion (puede ser varias: migracion, app nueva, modernizacion, etc.)
    - Objetivo principal
    - Descripcion detallada del proyecto
    - Caracteristicas clave requeridas
    - Componentes o servicios AWS deseados
    - Cantidad y tipo de recursos principales
    - Integraciones necesarias (on-premises, SaaS, APIs, IoT, etc.)
    - Requisitos de seguridad y compliance
    - Alta disponibilidad, DRP, continuidad (multi-AZ, multi-region, RTO, RPO, backups)
    - Estimacion de usuarios, trafico, cargas
    - Presupuesto disponible (opcional)
    - Fechas de inicio y entrega deseadas
    - Restricciones tecnicas, negocio o preferencias tecnologicas
    - Comentarios o necesidades adicionales (opcional)
2. Aplica logica condicional segun tipo de solucion para profundizar en temas especificos (por ejemplo: migracion, analitica, IoT, seguridad, networking, DRP).
3. Con la informacion capturada, genera y entrega SIEMPRE:
    - Tabla de actividades de implementacion (CSV o Excel, profesional y clara, SIN acentos ni caracteres especiales).
    - Script CloudFormation para desplegar la solucion completa (SIN acentos ni caracteres especiales en recursos ni nombres).
    - Dos diagramas de arquitectura (SVG, PNG, Draw.io editable, layout profesional, SIN acentos).
    - Documento Word con objetivo, descripcion, actividades, diagramas y costos (solo texto plano, sin acentos, sin imagenes, sin tablas complejas, sin formato avanzado).
    - Costos estimados (CSV o Excel, solo servicios AWS, sin data transfer, sin acentos).
    - Guia paso a paso para la calculadora oficial de AWS (sin acentos).
4. Al finalizar, genera automaticamente todos los documentos y los sube al bucket S3 del sistema ({bucket_name}).
5. Sube todos los archivos generados a una carpeta con el nombre del proyecto y confirma la carga exitosa.
6. Permite agregar comentarios o ajustes antes de cerrar la propuesta.

**En todas las preguntas y entregas:**

- Se claro, especifico y pregunta una cosa a la vez.
- Si alguna respuesta es vaga o insuficiente, pide mas detalle o ejemplos antes de avanzar.
- Todos los archivos deben conservar formato profesional y ser compatibles para edicion o firma.
- El flujo es siempre guiado y conversacional.
- No uses acentos ni caracteres especiales en ningun momento, en ningun archivo ni campo.

**Nota:**

- Los diagramas siempre deben entregarse en SVG, PNG y Draw.io editable, sin acentos ni caracteres especiales.
- La carpeta final debe contener todos los entregables bien organizados, y estar subida automaticamente al bucket S3 del sistema ({bucket_name}).
- Los documentos Word deben ser funcionales y abrirse correctamente en Microsoft Word o editores compatibles, solo texto plano, sin acentos ni caracteres especiales, sin imagenes, sin tablas complejas."""

def prepare_prompt(model_id: str, system_prompt: str, messages: List[Dict], 
                  project_info: Dict, current_step: int) -> Dict:
    """Prepare prompt based on model type"""
    
    # Add context about current project info
    context = f"\nCONTEXTO DEL PROYECTO ACTUAL:\n"
    if project_info:
        for key, value in project_info.items():
            context += f"- {key}: {value}\n"
    context += f"- Paso actual: {current_step}\n"
    
    full_system_prompt = system_prompt + context
    
    if model_id.startswith('anthropic.claude'):
        return {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "system": full_system_prompt,
            "messages": messages,
            "temperature": 0.7
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
                "temperature": 0.7
            }
        }
    else:
        return {
            "messages": [{"role": "system", "content": full_system_prompt}] + messages,
            "max_tokens": 4000,
            "temperature": 0.7
        }

def extract_response(model_id: str, response_body: Dict) -> tuple:
    """Extract AI response and usage from response body"""
    
    ai_response = ""
    usage = {}
    
    if model_id.startswith('anthropic.claude'):
        ai_response = response_body.get('content', [{}])[0].get('text', '')
        usage = {
            'inputTokens': response_body.get('usage', {}).get('input_tokens'),
            'outputTokens': response_body.get('usage', {}).get('output_tokens')
        }
    elif model_id.startswith('amazon.nova'):
        ai_response = response_body.get('output', {}).get('message', {}).get('content', [{}])[0].get('text', '')
        usage = {
            'inputTokens': response_body.get('usage', {}).get('inputTokens'),
            'outputTokens': response_body.get('usage', {}).get('outputTokens'),
            'totalTokens': response_body.get('usage', {}).get('totalTokens')
        }
    else:
        ai_response = response_body.get('content', '')
    
    return ai_response, usage

def extract_project_info_from_conversation(messages: List[Dict], ai_response: str, existing_info: Dict) -> Dict:
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
    
    # Extract project name
    if not project_info.get('name'):
        import re
        
        # Look for project name patterns in user messages
        for user_msg in user_messages:
            # Skip common responses
            if user_msg in ['hola', 'si', 'no', 'servicio rapido', 'solucion integral']:
                continue
            
            # If it's a short meaningful response, it might be the project name
            if len(user_msg.strip()) > 2 and len(user_msg.strip()) < 50:
                # Check if it's not a common phrase
                common_phrases = ['una instancia', 'una vpc', 'un rds', 'servicio', 'proyecto']
                if not any(phrase in user_msg for phrase in common_phrases):
                    project_info['name'] = user_msg.strip()
                    break
        
        # Fallback: look for explicit name patterns
        if not project_info.get('name'):
            name_patterns = [
                r'nombre del proyecto[:\s]*["\']?([^"\'\n,\.]+)["\']?',
                r'proyecto[:\s]*["\']?([^"\'\n,\.]+)["\']?',
                r'se llama[:\s]*["\']?([^"\'\n,\.]+)["\']?'
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
    
    if 'lambda' in conversation_lower:
        services_mentioned.append('Lambda')
        aws_services.append('AWS Lambda')
    
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
    """Check if project information gathering is complete"""
    
    # Enhanced completion indicators
    completion_indicators = [
        "proyecto está completo",
        "información suficiente",
        "generar documentos",
        "listo para crear",
        "proceder con la generación",
        "procederé a generar",
        "subir al bucket",
        "carpeta con todos los documentos",
        "entregables generados",
        "propuesta finalizada",
        "documentos listos",
        "archivos generados",
        "carga exitosa",
        "comentario final",
        "ajuste final",
        "cerrar la propuesta",
        "proyecto terminado",
        "todos los documentos",
        "carga de los documentos",
        "bucket s3"
    ]
    
    response_lower = ai_response.lower()
    has_completion_indicator = any(indicator in response_lower for indicator in completion_indicators)
    
    # Check if we have minimum required info for a complete project
    has_minimum_info = (
        project_info.get('name') and 
        project_info.get('type')
    )
    
    # Check if response mentions document generation or file uploads
    mentions_deliverables = any(term in response_lower for term in [
        "documento", "archivo", "diagrama", "cloudformation", "csv", "excel", "word",
        "tabla de actividades", "script", "guia", "bucket"
    ])
    
    # More lenient completion check
    return has_completion_indicator or (has_minimum_info and mentions_deliverables)

def generate_project_documents(project_info: Dict[str, Any]) -> Dict[str, Any]:
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
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
        },
        'body': json.dumps(body, ensure_ascii=False)
    }
