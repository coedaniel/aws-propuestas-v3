import json
import boto3
import logging
from datetime import datetime
import uuid
import os
from mcp_integration import generate_diagram, generate_cloudformation, generate_costs

# Configuración de logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Inicializar servicios AWS
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime')

# Configuración de modelos
MODELS = {
    'nova-pro': {
        'id': 'amazon.nova-pro-v1:0',
        'temp': 0.7,
        'top_p': 0.9
    },
    'claude': {
        'id': 'anthropic.claude-3.5-sonnet-v1',
        'temp': 0.7,
        'top_p': 0.9
    }
}

def get_cors_headers():
    return {
        'Access-Control-Allow-Origin': 'https://main.d2xsphsjdxlk24.amplifyapp.com',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With, Accept, Origin',
        'Access-Control-Max-Age': '86400',
        'Content-Type': 'application/json'
    }

def create_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': get_cors_headers(),
        'body': json.dumps(body)
    }

def validate_project_state(project_state):
    """Validación exhaustiva del estado del proyecto"""
    required_fields = ['name', 'services', 'requirements']
    for field in required_fields:
        if field not in project_state:
            project_state[field] = []
    return project_state

def analyze_conversation(messages):
    """Análisis profundo de la conversación usando Bedrock"""
    try:
        # Preparar el prompt para análisis
        conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        prompt = f"""Analiza esta conversación y extrae:
1. Nombre del proyecto
2. Tipo de proyecto (integral/rápido)
3. Servicios AWS mencionados
4. Requerimientos específicos
5. Estado actual de la conversación
6. Siguiente paso recomendado

Conversación:
{conversation_text}

Responde en formato JSON."""

        # Llamar a Bedrock con Claude para análisis
        response = bedrock.invoke_model(
            modelId=MODELS['claude']['id'],
            body=json.dumps({
                'prompt': prompt,
                'temperature': MODELS['claude']['temp'],
                'top_p': MODELS['claude']['top_p']
            })
        )
        
        analysis = json.loads(response['body'].read())
        logger.info(f"Análisis de conversación: {analysis}")
        return analysis
        
    except Exception as e:
        logger.error(f"Error en análisis de conversación: {str(e)}")
        return None

def generate_documents(project_data):
    """Generación de documentos usando MCPs"""
    try:
        documents = []
        mcp_used = []
        
        # 1. Generar diagrama
        diagram = generate_diagram(project_data)
        if diagram:
            documents.append(diagram)
            mcp_used.append('generate_diagram')
        
        # 2. Generar CloudFormation
        cloudformation = generate_cloudformation(project_data)
        if cloudformation:
            documents.append(cloudformation)
            mcp_used.append('generate_cloudformation')
        
        # 3. Generar costos
        costs = generate_costs(project_data)
        if costs:
            documents.append(costs)
            mcp_used.append('generate_costs')
        
        # Guardar documentos en S3
        bucket_name = os.environ['DOCUMENTS_BUCKET']
        for doc in documents:
            if 'content' in doc:
                s3.put_object(
                    Bucket=bucket_name,
                    Key=doc['url'],
                    Body=doc['content'].encode('utf-8')
                )
        
        # Guardar proyecto en DynamoDB
        table = dynamodb.Table(os.environ['PROJECTS_TABLE'])
        project_id = str(uuid.uuid4())
        
        table.put_item(Item={
            'projectId': project_id,
            'name': project_data['name'],
            'createdAt': int(datetime.utcnow().timestamp()),
            'services': project_data.get('services', []),
            'requirements': project_data.get('requirements', []),
            'documentsGenerated': documents,
            'status': 'COMPLETED'
        })
        
        return {
            'documents': documents,
            'mcp_used': mcp_used
        }
        
    except Exception as e:
        logger.error(f"Error generando documentos: {str(e)}")
        return None

def get_next_question(analysis):
    """Determinar siguiente pregunta basada en el análisis de Bedrock"""
    try:
        if not analysis.get('project_name'):
            return "¿Cuál es el nombre del proyecto?"
            
        if not analysis.get('project_type'):
            return """¿El proyecto es una solucion integral (como migracion, aplicacion nueva, modernizacion, analitica, seguridad, IA, IoT, data lake, networking, DRP, VDI, integracion, etc.)?
¿O es un servicio rapido especifico (como EC2, RDS, SES, VPN, ELB, S3, VPC, CloudFront, SSO, backup, etc.)?"""
            
        if not analysis.get('services'):
            return "¿Qué servicios AWS específicos necesitas para este proyecto?"
            
        if not analysis.get('requirements'):
            if 'servicio rapido' in analysis.get('project_type', '').lower():
                services = ', '.join(analysis.get('services', []))
                return f"Para implementar {services}, necesito saber los requerimientos específicos:"
            else:
                return """Para diseñar la solución integral, necesito saber:
- ¿Cuáles son los objetivos principales del proyecto?
- ¿Qué sistemas o aplicaciones están involucrados?
- ¿Tienes requisitos específicos de rendimiento o escalabilidad?
- ¿Hay consideraciones especiales de seguridad o cumplimiento?"""
        
        return None
        
    except Exception as e:
        logger.error(f"Error obteniendo siguiente pregunta: {str(e)}")
        return "¿Podrías proporcionar más detalles sobre el proyecto?"

def lambda_handler(event, context):
    """Handler principal mejorado"""
    
    # Manejar preflight CORS
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': ''
        }

    try:
        # Extraer y validar datos
        body = json.loads(event.get('body', '{}'))
        messages = body.get('messages', [])
        project_state = validate_project_state(body.get('projectState', {}))
        
        # Analizar conversación con Bedrock
        analysis = analyze_conversation(messages)
        
        # Obtener siguiente pregunta o generar documentos
        next_question = get_next_question(analysis) if analysis else None
        
        if next_question:
            return create_response(200, {
                'content': next_question,
                'projectState': project_state,
                'mcpActivated': True,
                'mcpUsed': [],
                'readinessScore': 0.5,
                'readinessStatus': "⚠️ Recopilando información",
                'analysis': analysis
            })
        
        # Generar documentos
        generation_result = generate_documents(project_state)
        
        if not generation_result:
            raise Exception("Error generando documentos")
        
        success_message = f"""✅ DOCUMENTOS GENERADOS EXITOSAMENTE PARA: {project_state['name']}
🏗️ Servicios AWS: {', '.join(project_state.get('services', []))}
📁 Carpeta S3: {project_state['name']}
📄 Archivos: {len(generation_result['documents'])} documentos específicos
💾 Proyecto guardado en base de datos

🎯 Documentos incluyen:
   • Diagrama de arquitectura con iconos AWS oficiales
   • CloudFormation template para {', '.join(project_state.get('services', []))}
   • Estimación de costos específica del proyecto

📱 Puedes revisar todos los archivos en la sección 'Proyectos'."""
        
        return create_response(200, {
            'content': success_message,
            'projectState': project_state,
            'mcpActivated': True,
            'mcpUsed': generation_result['mcp_used'],
            'readinessScore': 1.0,
            'readinessStatus': "✅ Documentos generados",
            'analysis': analysis
        })
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return create_response(500, {
            'content': f"Lo siento, ocurrió un error: {str(e)}",
            'projectState': project_state,
            'mcpActivated': True,
            'mcpUsed': [],
            'readinessScore': 0,
            'readinessStatus': "Error en el procesamiento"
        })
