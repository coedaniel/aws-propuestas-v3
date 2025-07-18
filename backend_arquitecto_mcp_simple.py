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

# Prompt maestro completo
PROMPT_MAESTRO = """
Actua como arquitecto de soluciones AWS y consultor experto. Vamos a dimensionar, documentar y entregar una solucion profesional en AWS, siguiendo mejores practicas y generando todos los archivos necesarios para una propuesta ejecutiva. No uses acentos ni caracteres especiales en ningun texto, archivo, script ni documento.

IMPORTANTE: Sigue este flujo paso a paso:

1. Primero pregunta: Cual es el nombre del proyecto

2. Despues pregunta: El proyecto es una solucion integral (como migracion, aplicacion nueva, modernizacion, analitica, seguridad, IA, IoT, data lake, networking, DRP, VDI, integracion, etc.) o es un servicio rapido especifico (implementacion de instancias EC2, RDS, SES, VPN, ELB, S3, VPC, CloudFront, SSO, backup, etc.)

3. Haz MUCHAS preguntas detalladas una por una para capturar toda la informacion necesaria

4. SOLO al final, cuando tengas TODA la informacion, di exactamente: "GENERO LOS SIGUIENTES DOCUMENTOS:" y lista todos los documentos que vas a crear.

NO generes documentos hasta tener toda la informacion completa del proyecto.
Pregunta una cosa a la vez. Se detallado y minucioso.
"""

def generate_mock_documents(project_info):
    """Genera documentos mock mientras se configuran los MCP services"""
    
    # CloudFormation Template
    cfn_template = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Description": f"CloudFormation template for {project_info.get('name', 'AWS Project')}",
        "Resources": {
            "S3Bucket": {
                "Type": "AWS::S3::Bucket",
                "Properties": {
                    "BucketName": f"{project_info.get('name', 'project').lower().replace(' ', '-')}-bucket"
                }
            },
            "LambdaFunction": {
                "Type": "AWS::Lambda::Function",
                "Properties": {
                    "FunctionName": f"{project_info.get('name', 'project').replace(' ', '-')}-function",
                    "Runtime": "python3.9",
                    "Handler": "index.handler",
                    "Code": {
                        "ZipFile": "def handler(event, context): return {'statusCode': 200}"
                    }
                }
            }
        }
    }
    
    # Cost Analysis CSV
    cost_analysis = """Service,Resource Type,Quantity,Unit Cost (USD),Monthly Cost (USD),Annual Cost (USD)
Lambda,Function Invocations,1000000,0.0000002,200,2400
S3,Standard Storage (GB),100,0.023,2.30,27.60
API Gateway,REST API Requests,1000000,0.0000035,3.50,42.00
DynamoDB,On-Demand Read/Write,1000000,0.000125,125,1500
CloudWatch,Log Storage (GB),10,0.50,5.00,60.00
Total,,,,,335.80,4029.60"""
    
    # Implementation Plan CSV
    implementation_plan = """Phase,Task,Duration (Days),Dependencies,Resources,Status
1,Project Setup,2,,AWS Architect,Pending
1,Environment Configuration,3,Project Setup,DevOps Engineer,Pending
2,Infrastructure Deployment,5,Environment Configuration,AWS Architect,Pending
2,Application Development,10,Infrastructure Deployment,Developer,Pending
3,Testing and QA,7,Application Development,QA Engineer,Pending
3,Security Review,3,Testing and QA,Security Engineer,Pending
4,Production Deployment,2,Security Review,DevOps Engineer,Pending
4,Documentation and Training,3,Production Deployment,Technical Writer,Pending"""
    
    # Project Documentation
    project_doc = f"""
# PROYECTO: {project_info.get('name', 'AWS Project')}

## OBJETIVO
Implementar una solucion robusta y escalable en AWS que cumpla con los requerimientos del negocio.

## DESCRIPCION
{project_info.get('description', 'Proyecto de implementacion en AWS con mejores practicas.')}

## SERVICIOS AWS UTILIZADOS
- Amazon S3: Almacenamiento de objetos
- AWS Lambda: Funciones serverless
- Amazon API Gateway: APIs REST
- Amazon DynamoDB: Base de datos NoSQL
- Amazon CloudWatch: Monitoreo y logs

## ARQUITECTURA
La solucion implementa una arquitectura serverless que garantiza:
- Alta disponibilidad
- Escalabilidad automatica
- Costos optimizados
- Seguridad integrada

## BENEFICIOS
- Reduccion de costos operativos
- Mayor agilidad en el desarrollo
- Escalabilidad automatica
- Seguridad mejorada

## CRONOGRAMA
Duracion estimada: 4-6 semanas
Fases principales:
1. Configuracion inicial (1 semana)
2. Desarrollo e implementacion (3 semanas)
3. Testing y deployment (1-2 semanas)

## COSTOS ESTIMADOS
Costo mensual aproximado: $335.80 USD
Costo anual aproximado: $4,029.60 USD

## PROXIMOS PASOS
1. Aprobacion del proyecto
2. Configuracion del entorno AWS
3. Inicio del desarrollo
4. Testing y validacion
5. Deployment a produccion
"""
    
    return {
        'cloudformation-template.json': json.dumps(cfn_template, indent=2),
        'cost-analysis.csv': cost_analysis,
        'implementation-plan.csv': implementation_plan,
        'project-documentation.md': project_doc
    }

def save_project_to_dynamodb(project_info, documents_generated):
    """Guarda el proyecto en DynamoDB"""
    try:
        table = dynamodb.Table(PROJECTS_TABLE)
        
        project_item = {
            'projectId': project_info['id'],
            'projectName': project_info['name'],
            'projectType': project_info.get('type', 'Solucion AWS'),
            'status': 'completed',
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat(),
            'description': project_info.get('description', ''),
            'documentsGenerated': documents_generated,
            's3Folder': f"{project_info['name'].lower().replace(' ', '-')}-{project_info['id'][:8]}",
            'estimatedCost': 335.80
        }
        
        table.put_item(Item=project_item)
        return True
    except Exception as e:
        print(f"Error saving to DynamoDB: {str(e)}")
        return False

def upload_documents_to_s3(project_info, documents):
    """Sube documentos a S3"""
    try:
        folder_name = f"{project_info['name'].lower().replace(' ', '-')}-{project_info['id'][:8]}"
        
        for doc_name, content in documents.items():
            key = f"{folder_name}/{doc_name}"
            s3_client.put_object(
                Bucket=DOCUMENTS_BUCKET,
                Key=key,
                Body=content,
                ContentType='text/plain' if doc_name.endswith('.txt') else 'application/json' if doc_name.endswith('.json') else 'text/csv'
            )
        
        return True
    except Exception as e:
        print(f"Error uploading to S3: {str(e)}")
        return False

def lambda_handler(event, context):
    try:
        # Parsear el cuerpo de la solicitud
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        messages = body.get('messages', [])
        selected_model = body.get('selected_model', 'amazon.nova-pro-v1:0')
        
        if not messages:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({'error': 'No messages provided'})
            }
        
        # Construir el prompt con el contexto maestro
        conversation_history = ""
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            conversation_history += f"\n{role.upper()}: {content}"
        
        # Prompt completo con contexto maestro
        full_prompt = f"{PROMPT_MAESTRO}\n\n--- CONVERSACION ACTUAL ---{conversation_history}\n\nARQUITECTO AWS:"
        
        # Preparar mensajes para Bedrock
        bedrock_messages = [
            {
                "role": "user",
                "content": [{"text": full_prompt}]
            }
        ]
        
        # Llamar a Bedrock
        if 'nova' in selected_model.lower():
            # Nova Pro
            payload = {
                "messages": bedrock_messages,
                "inferenceConfig": {
                    "maxTokens": 4000,
                    "temperature": 0.7
                }
            }
            
            response = bedrock_runtime.invoke_model(
                modelId=selected_model,
                body=json.dumps(payload),
                contentType='application/json',
                accept='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            ai_response = response_body['output']['message']['content'][0]['text']
            
        else:
            # Claude
            response = bedrock_runtime.converse(
                modelId=selected_model,
                messages=bedrock_messages,
                inferenceConfig={
                    'maxTokens': 4000,
                    'temperature': 0.7
                }
            )
            
            ai_response = response['output']['message']['content'][0]['text']
        
        # Detectar MCP services que se están usando
        response_lower = ai_response.lower()
        mcp_services_used = []
        
        if any(keyword in response_lower for keyword in ['diagrama', 'arquitectura']):
            mcp_services_used.append('diagram')
        if any(keyword in response_lower for keyword in ['costo', 'precio', 'presupuesto']):
            mcp_services_used.append('pricing')
        if any(keyword in response_lower for keyword in ['documento', 'archivo']):
            mcp_services_used.append('documents')
        if any(keyword in response_lower for keyword in ['cloudformation', 'template']):
            mcp_services_used.append('cfn')
        
        # Detectar si debe generar documentos REALES
        documents_generated = None
        project_id = None
        project_name = None
        
        # Buscar la frase exacta que indica generación
        if "GENERO LOS SIGUIENTES DOCUMENTOS:" in ai_response.upper():
            # Extraer información del proyecto de la conversación
            project_info = {
                'id': str(uuid.uuid4()),
                'name': 'Proyecto AWS',
                'type': 'Solucion Integral',
                'description': 'Proyecto generado por el Arquitecto AWS'
            }
            
            # Intentar extraer el nombre del proyecto de la conversación
            for msg in messages:
                if msg.get('role') == 'user':
                    content = msg.get('content', '').strip()
                    if len(content) < 50 and not any(word in content.lower() for word in ['como', 'que', 'cual', 'donde', 'cuando']):
                        project_info['name'] = content
                        break
            
            # Generar documentos usando mock data (mientras se configuran MCP services)
            documents = generate_mock_documents(project_info)
            
            # Subir a S3
            if upload_documents_to_s3(project_info, documents):
                # Guardar en DynamoDB
                documents_list = list(documents.keys())
                if save_project_to_dynamodb(project_info, documents_list):
                    documents_generated = [
                        'CloudFormation Template (JSON)',
                        'Analisis de Costos (CSV)',
                        'Plan de Implementacion (CSV)',
                        'Documentacion del Proyecto (MD)'
                    ]
                    project_id = project_info['id']
                    project_name = project_info['name']
                    mcp_services_used.extend(['documents', 'cfn', 'pricing', 's3', 'dynamodb'])
        
        # Respuesta estructurada
        result = {
            'response': ai_response,
            'modelId': selected_model,
            'mode': 'arquitecto-maestro-mcp',
            'timestamp': datetime.now().isoformat(),
            'mcpServicesUsed': list(set(mcp_services_used)),
            'documentsGenerated': documents_generated,
            'projectId': project_id,
            'projectName': project_name
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({'error': str(e)})
        }
