import json
import boto3
import os
import urllib3
from datetime import datetime
import uuid
from smart_mcp_handler import smart_mcp

# Clientes AWS
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
s3_client = boto3.client('s3', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Variables de entorno
DOCUMENTS_BUCKET = os.environ.get('DOCUMENTS_BUCKET', 'aws-propuestas-v3-documents-prod-035385358261')
PROJECTS_TABLE = os.environ.get('PROJECTS_TABLE', 'aws-propuestas-v3-projects-prod')

def create_response(status_code, body, headers=None):
    """Crear respuesta HTTP con headers CORS"""
    default_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With'
    }
    
    if headers:
        default_headers.update(headers)
    
    return {
        'statusCode': status_code,
        'headers': default_headers,
        'body': json.dumps(body) if isinstance(body, dict) else body
    }

def call_bedrock(prompt, max_tokens=4000):
    """Llamar a Bedrock Claude"""
    try:
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        response = bedrock_runtime.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
        
    except Exception as e:
        return f"Error llamando a Bedrock: {str(e)}"

def save_to_s3(content, filename):
    """Guardar contenido en S3"""
    try:
        s3_client.put_object(
            Bucket=DOCUMENTS_BUCKET,
            Key=filename,
            Body=content,
            ContentType='text/plain'
        )
        return f"https://{DOCUMENTS_BUCKET}.s3.amazonaws.com/{filename}"
    except Exception as e:
        return f"Error guardando en S3: {str(e)}"

def save_project_to_dynamodb(project_data):
    """Guardar proyecto en DynamoDB"""
    try:
        table = dynamodb.Table(PROJECTS_TABLE)
        
        project_item = {
            'project_id': project_data.get('project_id', str(uuid.uuid4())),
            'name': project_data.get('name', ''),
            'description': project_data.get('description', ''),
            'status': project_data.get('status', 'draft'),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'data': project_data
        }
        
        table.put_item(Item=project_item)
        return project_item['project_id']
        
    except Exception as e:
        return f"Error guardando en DynamoDB: {str(e)}"

def extract_project_data_from_conversation(user_message, conversation_history):
    """Extraer datos del proyecto de la conversación"""
    project_data = {}
    
    # Análisis básico del mensaje para extraer información del proyecto
    message_lower = user_message.lower()
    
    # Detectar tipo de proyecto
    if any(word in message_lower for word in ['web', 'aplicación web', 'website']):
        project_data['type'] = 'web_application'
        project_data['services'] = ['ec2', 's3', 'cloudfront', 'rds']
    elif any(word in message_lower for word in ['api', 'microservicio', 'backend']):
        project_data['type'] = 'api_backend'
        project_data['services'] = ['lambda', 'api-gateway', 'dynamodb']
    elif any(word in message_lower for word in ['datos', 'analytics', 'etl']):
        project_data['type'] = 'data_processing'
        project_data['services'] = ['s3', 'glue', 'redshift', 'lambda']
    
    # Detectar requisitos de presupuesto
    if any(word in message_lower for word in ['precio', 'costo', 'presupuesto', 'barato', 'económico']):
        project_data['budget_required'] = True
    
    # Detectar necesidad de documentación
    if any(word in message_lower for word in ['documento', 'documentación', 'propuesta']):
        project_data['documentation_required'] = True
    
    # Extraer nombre del proyecto si se menciona
    if 'proyecto' in message_lower:
        # Lógica simple para extraer nombre
        words = user_message.split()
        for i, word in enumerate(words):
            if word.lower() in ['proyecto', 'aplicación', 'sistema'] and i + 1 < len(words):
                project_data['name'] = words[i + 1].title()
                break
    
    if not project_data.get('name'):
        project_data['name'] = 'Proyecto AWS'
    
    return project_data

def lambda_handler(event, context):
    """Handler principal de Lambda"""
    
    # Manejar preflight CORS
    if event.get('httpMethod') == 'OPTIONS':
        return create_response(200, {})
    
    try:
        # Log the incoming event for debugging
        print(f"Received event: {json.dumps(event)}")
        
        # Parsear el cuerpo de la solicitud
        if 'body' in event and event['body']:
            if isinstance(event['body'], str):
                try:
                    body = json.loads(event['body'])
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {str(e)}")
                    return create_response(400, {
                        'error': 'Invalid JSON format'
                    })
            else:
                body = event['body']
        else:
            body = {}
        
        # Obtener el mensaje del usuario - manejar tanto formato simple como formato de chat
        user_message = ""
        
        # Formato simple: {"message": "texto"}
        if 'message' in body:
            user_message = body.get('message', '').strip()
        
        # Formato de chat: {"messages": [{"role": "user", "content": "texto"}]}
        elif 'messages' in body and isinstance(body['messages'], list):
            messages = body['messages']
            # Obtener el último mensaje del usuario
            for msg in reversed(messages):
                if msg.get('role') == 'user' and msg.get('content'):
                    user_message = msg['content'].strip()
                    break
        
        # También manejar query parameter
        if not user_message and 'query' in body:
            user_message = body.get('query', '').strip()
        
        conversation_history = body.get('conversation_history', [])
        project_data = body.get('project_data', {})
        project_info = body.get('project_info', {})
        
        # Log para debugging
        print(f"Request body: {json.dumps(body)}")
        print(f"User message: '{user_message}'")
        
        # Si no hay mensaje, proporcionar un mensaje de bienvenida
        if not user_message:
            user_message = "Hola, necesito ayuda para crear un proyecto en AWS"
        
        # Extraer datos del proyecto de la conversación si no se proporcionaron
        if not project_data and not project_info:
            project_data = extract_project_data_from_conversation(user_message, conversation_history)
        elif project_info:
            project_data = project_info
        
        # PROMPT MAESTRO COMPLETO - Tu flujo específico
        system_prompt = """
Actua como arquitecto de soluciones AWS y consultor experto. Vamos a dimensionar, documentar y entregar una solucion profesional en AWS, siguiendo mejores practicas y generando todos los archivos necesarios para una propuesta ejecutiva. No uses acentos ni caracteres especiales en ningun texto, archivo, script ni documento. Asegura que todos los archivos Word generados sean funcionales y compatibles: entrega solo texto plano, sin imagenes, sin tablas complejas, ni formato avanzado, solo texto estructurado, claro y legible. Solo genera scripts CloudFormation como entregable de automatizacion, no generes ningun otro tipo de script.

FLUJO OBLIGATORIO PASO A PASO:

1. Primero pregunta: Cual es el nombre del proyecto

2. Despues pregunta: El proyecto es una solucion integral (como migracion, aplicacion nueva, modernizacion, analitica, seguridad, IA, IoT, data lake, networking, DRP, VDI, integracion, etc.) o es un servicio rapido especifico (implementacion de instancias EC2, RDS, SES, VPN, ELB, S3, VPC, CloudFront, SSO, backup, etc.)

Si elige "servicio rapido especifico":
1. Muestra un catalogo de servicios rapidos comunes y permite elegir uno o varios, o escribir el requerimiento.
2. Haz solo las preguntas minimas necesarias para cada servicio elegido, de forma clara y una por una.
3. Con la informacion, genera y entrega SIEMPRE: Tabla de actividades, Script CloudFormation, Diagrama de arquitectura, Documento Word, Archivo de costos, Guia calculadora AWS.
4. Pregunta en que bucket S3 deseas subir la carpeta con todos los documentos generados.
5. Sube todos los archivos y confirma que la carga fue exitosa.
6. Pregunta si deseas agregar algun comentario o ajuste final.

Si elige "solucion integral":
1. Haz una entrevista guiada, una pregunta a la vez, para capturar todos los requisitos del proyecto complejo.
2. Aplica logica condicional segun tipo de solucion para profundizar en temas especificos.
3. Genera y entrega SIEMPRE todos los entregables profesionales.
4. Pregunta bucket S3 y sube archivos.
5. Permite comentarios finales.

IMPORTANTE: Se claro, especifico y pregunta una cosa a la vez. Si alguna respuesta es vaga, pide mas detalle antes de avanzar. El flujo debe ser guiado y conversacional. Adapta dinamicamente segun lo que el usuario escriba, detecta que informacion ya tienes y cual falta.
"""
        
        # Construir el prompt completo con contexto del proyecto
        project_context = ""
        if project_data:
            project_context = f"\nCONTEXTO DEL PROYECTO:\n"
            project_context += f"- Nombre: {project_data.get('name', 'No especificado')}\n"
            project_context += f"- Tipo: {project_data.get('type', 'No especificado')}\n"
            project_context += f"- Servicios sugeridos: {', '.join(project_data.get('services', []))}\n"
            if project_data.get('budget_required'):
                project_context += "- Análisis de costos requerido\n"
            if project_data.get('documentation_required'):
                project_context += "- Documentación técnica requerida\n"
        
        full_prompt = f"{system_prompt}{project_context}\n\nUsuario: {user_message}"
        
        # Llamar a Bedrock para obtener la respuesta
        ai_response = call_bedrock(full_prompt)
        
        # SMART MCP ACTIVATION - Esta es la parte clave que faltaba
        print(f"Activating Smart MCP Handler...")
        try:
            mcp_results = smart_mcp.process_smart_request(
                user_message=user_message,
                project_data=project_data,
                conversation_history=conversation_history
            )
            
            print(f"MCP Services activated: {mcp_results['services_activated']}")
            print(f"Artifacts generated: {mcp_results['artifacts_generated']}")
            
        except Exception as e:
            print(f"Error in Smart MCP Handler: {str(e)}")
            # Fallback to basic response if MCP fails
            mcp_results = {
                'services_activated': [],
                'mcp_results': {},
                'artifacts_generated': []
            }
        
        # Construir respuesta con resultados MCP
        response_data = {
            'response': ai_response,  # Frontend expects 'response' not 'message'
            'message': ai_response,   # Keep both for compatibility
            'timestamp': datetime.now().isoformat(),
            'mode': 'arquitecto',
            'modelId': 'anthropic.claude-3-5-sonnet-20240620-v1:0',
            'mcpServicesUsed': mcp_results['services_activated'],
            'mcpResults': mcp_results['mcp_results'],
            'artifacts': mcp_results['mcp_results'],  # Alias for compatibility
            'artifactsGenerated': mcp_results['artifacts_generated'],
            'transparency': {
                'smart_mcp_activated': True,
                'services_detected': mcp_results['services_activated'],
                'project_data_extracted': project_data
            },
            'promptUnderstanding': {
                'user_intent': 'arquitecto_consultation',
                'project_type': project_data.get('type', 'general'),
                'services_needed': project_data.get('services', [])
            }
        }
        
        # Guardar proyecto si hay datos significativos
        if project_data and project_data.get('name') and project_data.get('name') != 'Proyecto AWS':
            project_id = save_project_to_dynamodb(project_data)
            response_data['project_id'] = project_id
        
        return create_response(200, response_data)
        
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return create_response(500, {
            'error': f'Error interno del servidor: {str(e)}'
        })
