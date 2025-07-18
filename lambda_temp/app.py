import json
import boto3
import os
import urllib3
from datetime import datetime
import uuid

# Clientes AWS
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
s3_client = boto3.client('s3', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Variables de entorno
DOCUMENTS_BUCKET = os.environ.get('DOCUMENTS_BUCKET', 'aws-propuestas-v3-documents-prod-035385358261')
PROJECTS_TABLE = os.environ.get('PROJECTS_TABLE', 'aws-propuestas-v3-projects-prod')

# URLs de los contenedores MCP reales
DOCUMENT_GENERATOR_URL = "https://mcp.danielingram.shop/customdoc"
CLOUDFORMATION_GENERATOR_URL = "https://mcp.danielingram.shop/cfn"
PRICING_ANALYZER_URL = "https://mcp.danielingram.shop/pricing"
DIAGRAM_GENERATOR_URL = "https://mcp.danielingram.shop/diagram"

# HTTP client
http = urllib3.PoolManager()

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

def call_mcp_service(url, data):
    """Llamar a un servicio MCP"""
    try:
        response = http.request(
            'POST',
            url,
            body=json.dumps(data),
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status == 200:
            return json.loads(response.data.decode('utf-8'))
        else:
            return {"error": f"MCP service error: {response.status}"}
    except Exception as e:
        return {"error": f"Failed to call MCP service: {str(e)}"}

def generate_document(project_data):
    """Generar documento usando MCP"""
    mcp_data = {
        "project_name": project_data.get('name', 'Proyecto AWS'),
        "description": project_data.get('description', ''),
        "requirements": project_data.get('requirements', []),
        "architecture": project_data.get('architecture', {}),
        "services": project_data.get('services', [])
    }
    
    return call_mcp_service(DOCUMENT_GENERATOR_URL, mcp_data)

def generate_cloudformation(project_data):
    """Generar CloudFormation usando MCP"""
    mcp_data = {
        "project_name": project_data.get('name', 'Proyecto AWS'),
        "services": project_data.get('services', []),
        "architecture": project_data.get('architecture', {}),
        "requirements": project_data.get('requirements', [])
    }
    
    return call_mcp_service(CLOUDFORMATION_GENERATOR_URL, mcp_data)

def analyze_pricing(project_data):
    """Analizar precios usando MCP"""
    mcp_data = {
        "services": project_data.get('services', []),
        "region": project_data.get('region', 'us-east-1'),
        "usage_patterns": project_data.get('usage_patterns', {})
    }
    
    return call_mcp_service(PRICING_ANALYZER_URL, mcp_data)

def generate_diagram(project_data):
    """Generar diagrama usando MCP"""
    mcp_data = {
        "project_name": project_data.get('name', 'Proyecto AWS'),
        "architecture": project_data.get('architecture', {}),
        "services": project_data.get('services', []),
        "connections": project_data.get('connections', [])
    }
    
    return call_mcp_service(DIAGRAM_GENERATOR_URL, mcp_data)

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

def lambda_handler(event, context):
    """Handler principal de Lambda"""
    
    # Manejar preflight CORS
    if event.get('httpMethod') == 'OPTIONS':
        return create_response(200, {})
    
    try:
        # Parsear el cuerpo de la solicitud
        if 'body' in event and event['body']:
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            else:
                body = event['body']
        else:
            body = {}
        
        # Obtener el mensaje del usuario
        user_message = body.get('message', '').strip()
        conversation_history = body.get('conversation_history', [])
        project_data = body.get('project_data', {})
        
        if not user_message:
            return create_response(400, {
                'error': 'Mensaje requerido'
            })
        
        # Prompt maestro para el arquitecto
        system_prompt = """
Actúa como arquitecto de soluciones AWS experto. Tu objetivo es ayudar a dimensionar, documentar y entregar soluciones profesionales en AWS.

CAPACIDADES DISPONIBLES:
- Generar documentación técnica completa
- Crear templates de CloudFormation
- Analizar costos y precios
- Generar diagramas de arquitectura
- Recomendar mejores prácticas de AWS

FLUJO DE TRABAJO:
1. Entender los requisitos del proyecto
2. Proponer arquitectura AWS apropiada
3. Generar documentación y artefactos necesarios
4. Proporcionar estimaciones de costos
5. Crear diagramas de la solución

Responde de manera profesional y técnica, enfocándote en soluciones prácticas y escalables.
"""
        
        # Construir el prompt completo
        full_prompt = f"{system_prompt}\n\nUsuario: {user_message}"
        
        # Llamar a Bedrock para obtener la respuesta
        ai_response = call_bedrock(full_prompt)
        
        # Detectar si necesitamos generar artefactos específicos
        response_data = {
            'message': ai_response,
            'timestamp': datetime.now().isoformat(),
            'artifacts': {}
        }
        
        # Detectar necesidad de generar documentos
        if any(keyword in user_message.lower() for keyword in ['documento', 'documentación', 'propuesta', 'informe']):
            if project_data:
                doc_result = generate_document(project_data)
                if 'error' not in doc_result:
                    response_data['artifacts']['document'] = doc_result
        
        # Detectar necesidad de CloudFormation
        if any(keyword in user_message.lower() for keyword in ['cloudformation', 'template', 'infraestructura', 'despliegue']):
            if project_data:
                cfn_result = generate_cloudformation(project_data)
                if 'error' not in cfn_result:
                    response_data['artifacts']['cloudformation'] = cfn_result
        
        # Detectar necesidad de análisis de precios
        if any(keyword in user_message.lower() for keyword in ['precio', 'costo', 'presupuesto', 'estimación']):
            if project_data:
                pricing_result = analyze_pricing(project_data)
                if 'error' not in pricing_result:
                    response_data['artifacts']['pricing'] = pricing_result
        
        # Detectar necesidad de diagrama
        if any(keyword in user_message.lower() for keyword in ['diagrama', 'arquitectura', 'esquema', 'diseño']):
            if project_data:
                diagram_result = generate_diagram(project_data)
                if 'error' not in diagram_result:
                    response_data['artifacts']['diagram'] = diagram_result
        
        # Guardar proyecto si hay datos
        if project_data and project_data.get('name'):
            project_id = save_project_to_dynamodb(project_data)
            response_data['project_id'] = project_id
        
        return create_response(200, response_data)
        
    except Exception as e:
        return create_response(500, {
            'error': f'Error interno del servidor: {str(e)}'
        })
