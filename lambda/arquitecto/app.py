import json
import boto3
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any
import logging

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
        
        # Extract service parameters from conversation
        service_params = extract_service_from_conversation(messages, ai_response)
        servicio = service_params['servicio']
        descripcion = service_params['descripcion']
        objetivo = service_params['objetivo']
        
        logger.info(f"🔍 EXTRACTED - Service: {servicio}, Description: {descripcion[:50]}...")
        
        # Check if project is complete - FIXED logic
        has_enough_info = len(descripcion) > 30 and servicio != "AWS"
        original_complete_check = check_if_complete(ai_response, project_info)
        
        # Project is complete if EITHER we have enough extracted info OR the original check passes
        is_complete = has_enough_info or original_complete_check
        
        logger.info(f"🎯 COMPLETION CHECK - Has info: {has_enough_info}, Original check: {original_complete_check}, Final: {is_complete}")
        
        # Generate documents if project is complete
        document_generation_results = None
        if is_complete:
            # Generate documents using the working intelligent system
            logger.info(f"✅ GENERATING DOCUMENTS for {servicio}")
            
            # Generate documents from AI response using working system
            document_generation_results = generate_documents_from_ai_response(
                ai_response, 
                servicio, 
                project_id, 
                user_id
            )
            
            # Create separate response for chat (not mixing with documents)
            chat_response = f"""✅ **PROPUESTA COMPLETADA PARA {servicio.upper()}**

He analizado tu proyecto: "{descripcion}"

**Objetivo identificado:** {objetivo}

**Documentos generados específicamente para {servicio}:**

📄 **Propuesta Ejecutiva** - Documento profesional centrado en {servicio}
🔧 **Documento Técnico** - Arquitectura específica de {servicio}  
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
            
            # Use chat response instead of AI response with documents mixed in
            final_response = chat_response
            
        else:
            # Continue conversation - use original AI response
            final_response = ai_response
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
            'projectId': project_id,
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
    """Get system prompt for arquitecto mode - INTELLIGENT AND ADAPTIVE"""
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
    
    # EXPLICIT completion indicators - only when the AI explicitly says it's ready to generate
    explicit_completion_indicators = [
        "procederé a generar",
        "voy a generar",
        "generar y entregar",
        "crear los documentos",
        "subir al bucket",
        "carpeta con todos los documentos",
        "todos los archivos generados",
        "documentos listos para subir",
        "información completa para generar"
    ]
    
    # Check for explicit completion signals
    has_explicit_completion = any(indicator in response_lower for indicator in explicit_completion_indicators)
    
    # For SERVICIO RAPIDO - need specific service details answered
    if project_info.get('type') == 'servicio_rapido':
        service_type = project_info.get('service_type')
        
        # For S3 service - need at least bucket name and basic config
        if service_type == 's3':
            required_s3_info = [
                project_info.get('bucket_name'),
                project_info.get('region') or project_info.get('aws_region'),
                project_info.get('storage_type') or project_info.get('storage_class')
            ]
            has_s3_details = any(info for info in required_s3_info)
            
            # Only complete if we have explicit completion AND some S3 details
            return has_explicit_completion and has_s3_details
        
        # For EC2 service - need instance type and basic config
        elif service_type == 'ec2':
            has_ec2_details = (
                project_info.get('instance_type') or 
                project_info.get('instance_size') or
                project_info.get('ec2_config')
            )
            return has_explicit_completion and has_ec2_details
        
        # For VPC service - need network details
        elif service_type == 'vpc':
            has_vpc_details = (
                project_info.get('cidr_blocks') or 
                project_info.get('vpc_config') or
                project_info.get('network_config')
            )
            return has_explicit_completion and has_vpc_details
        
        # For other services - need at least service type and explicit completion
        else:
            return has_explicit_completion and project_info.get('service_type')
    
    # For SOLUCION INTEGRAL - need comprehensive information
    elif project_info.get('type') == 'solucion_integral':
        required_integral_info = [
            project_info.get('objective'),
            project_info.get('description'),
            project_info.get('services') or project_info.get('aws_services'),
            project_info.get('requirements')
        ]
        has_integral_details = sum(1 for info in required_integral_info if info) >= 3
        
        return has_explicit_completion and has_integral_details
    
    # Default: only if explicit completion is mentioned
    return has_explicit_completion

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
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
        },
        'body': json.dumps(body, ensure_ascii=False)
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

def create_response(status_code: int, body: Dict) -> Dict:
    """
    Crea respuesta HTTP con headers CORS
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With'
        },
        'body': json.dumps(body, ensure_ascii=False, default=str)
    }
