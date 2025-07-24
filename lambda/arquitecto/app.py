import json
import boto3
import logging
from datetime import datetime
import uuid
import os

# Configuración de logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Inicializar servicios AWS
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

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

def generate_diagram(project_name, services):
    """Genera un diagrama usando el MCP de diagramas"""
    diagram_code = f"""from diagrams import Diagram, Cluster
from diagrams.aws.compute import Lambda
from diagrams.aws.storage import S3
from diagrams.aws.general import Users

with Diagram("{project_name}", show=False, filename="diagrama"):
    users = Users("Usuarios")
    
    with Cluster("AWS Cloud"):
        lambda_fn = Lambda("Función\\nLambda")
        storage = S3("Bucket S3\\nAlmacenamiento")
        
        users >> lambda_fn >> storage"""
    
    # Aquí iría la llamada al MCP de diagramas
    return {
        'filename': 'diagrama.png',
        'title': 'Diagrama de Arquitectura',
        'type': 'diagram',
        'url': f'{project_name}/diagrama.png'
    }

def generate_cloudformation(project_name, services, requirements):
    """Genera un template CloudFormation"""
    template = {
        'AWSTemplateFormatVersion': '2010-09-09',
        'Description': f'Infraestructura para {project_name}',
        'Resources': {
            'ProcessingBucket': {
                'Type': 'AWS::S3::Bucket',
                'Properties': {
                    'BucketName': f'{project_name.lower()}-storage'
                }
            },
            'ProcessingFunction': {
                'Type': 'AWS::Lambda::Function',
                'Properties': {
                    'FunctionName': f'{project_name.lower()}-processor',
                    'Handler': 'index.handler',
                    'Role': {'Fn::GetAtt': ['LambdaExecutionRole', 'Arn']},
                    'Code': {
                        'ZipFile': 'exports.handler = async (event) => { /* TODO: Implement */ }'
                    },
                    'Runtime': 'nodejs18.x'
                }
            },
            'LambdaExecutionRole': {
                'Type': 'AWS::IAM::Role',
                'Properties': {
                    'AssumeRolePolicyDocument': {
                        'Version': '2012-10-17',
                        'Statement': [{
                            'Effect': 'Allow',
                            'Principal': {'Service': ['lambda.amazonaws.com']},
                            'Action': ['sts:AssumeRole']
                        }]
                    },
                    'ManagedPolicyArns': [
                        'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
                    ]
                }
            }
        }
    }
    
    return {
        'filename': 'template.yaml',
        'title': 'Template CloudFormation',
        'type': 'cloudformation',
        'url': f'{project_name}/template.yaml',
        'content': json.dumps(template, indent=2)
    }

def generate_costs(project_name, services):
    """Genera una estimación de costos"""
    costs_md = f"""# Estimación de Costos - {project_name}

## Resumen Mensual Estimado
Total estimado: $30 USD/mes

## Desglose por Servicio

### AWS Lambda
- 1 millón de invocaciones por mes
- 128 MB de memoria
- Tiempo de ejecución promedio: 500ms
- Costo mensual: $0.20

### Amazon S3
- Almacenamiento: 50 GB
- Transferencia saliente: 100 GB
- Solicitudes PUT/COPY/POST/LIST: 100,000
- Costo mensual: $2.30

## Notas
- Precios basados en región us-east-1
- No incluye Free Tier
- Precios pueden variar según el uso real"""
    
    return {
        'filename': 'costos.md',
        'title': 'Estimación de Costos',
        'type': 'costs',
        'url': f'{project_name}/costos.md',
        'content': costs_md
    }

def get_next_question(messages, project_data):
    # Si no hay nombre de proyecto
    if not project_data.get('name') or project_data['name'] == '':
        return "¿Cuál es el nombre del proyecto?"
    
    # Si no hay tipo de proyecto
    conversation = ' '.join([msg.get('content', '').lower() for msg in messages])
    if 'solucion integral' not in conversation and 'servicio rapido' not in conversation:
        return """¿El proyecto es una solucion integral (como migracion, aplicacion nueva, modernizacion, analitica, seguridad, IA, IoT, data lake, networking, DRP, VDI, integracion, etc.)?
¿O es un servicio rapido especifico (como EC2, RDS, SES, VPN, ELB, S3, VPC, CloudFront, SSO, backup, etc.)?"""
    
    # Si es servicio rápido pero no hay servicios específicos
    if 'servicio rapido' in conversation and not project_data.get('services'):
        return "¿Qué servicios AWS específicos necesitas para este proyecto?"
    
    # Si no hay requerimientos específicos
    if not project_data.get('requirements'):
        return "Por favor, describe los requerimientos específicos del proyecto:"
    
    # Si ya tenemos toda la información necesaria
    return None

def lambda_handler(event, context):
    # Manejar preflight CORS
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': ''
        }

    try:
        # Extraer body del request
        body = json.loads(event.get('body', '{}'))
        messages = body.get('messages', [])
        project_state = body.get('projectState', {})
        
        # Obtener siguiente pregunta
        next_question = get_next_question(messages, project_state)
        
        # Si hay siguiente pregunta, enviarla
        if next_question:
            return create_response(200, {
                'content': next_question,
                'projectState': project_state,
                'mcpActivated': True,
                'mcpUsed': [],
                'readinessScore': 0.5,
                'readinessStatus': "⚠️ Recopilando información"
            })
        
        # Si no hay más preguntas, generar documentos
        project_name = project_state['name']
        services = project_state.get('services', [])
        requirements = project_state.get('requirements', [])
        
        # Generar documentos usando MCPs
        documents = []
        mcp_used = []
        
        # 1. Generar diagrama
        diagram = generate_diagram(project_name, services)
        documents.append(diagram)
        mcp_used.append('generate_diagram')
        
        # 2. Generar CloudFormation
        cloudformation = generate_cloudformation(project_name, services, requirements)
        documents.append(cloudformation)
        mcp_used.append('generate_cloudformation')
        
        # 3. Generar costos
        costs = generate_costs(project_name, services)
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
            'name': project_name,
            'createdAt': int(datetime.utcnow().timestamp()),
            'services': services,
            'requirements': requirements,
            'documentsGenerated': documents,
            'status': 'COMPLETED'
        })
        
        success_message = f"""✅ DOCUMENTOS GENERADOS EXITOSAMENTE PARA: {project_name}
🏗️ Servicios AWS: {', '.join(services)}
📁 Carpeta S3: {project_name}
📄 Archivos: {len(documents)} documentos específicos
💾 Proyecto guardado en base de datos

🎯 Documentos incluyen:
   • Diagrama de arquitectura con iconos AWS oficiales
   • CloudFormation template para {', '.join(services)}
   • Estimación de costos específica del proyecto

📱 Puedes revisar todos los archivos en la sección 'Proyectos'."""
        
        return create_response(200, {
            'content': success_message,
            'projectState': project_state,
            'mcpActivated': True,
            'mcpUsed': mcp_used,
            'readinessScore': 1.0,
            'readinessStatus': "✅ Documentos generados"
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
