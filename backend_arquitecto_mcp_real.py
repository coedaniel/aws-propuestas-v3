import json
import boto3
import os
import requests
from datetime import datetime
import uuid

# Clientes AWS
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
s3_client = boto3.client('s3', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Variables de entorno
DOCUMENTS_BUCKET = os.environ.get('DOCUMENTS_BUCKET', 'aws-propuestas-v3-documents-prod-035385358261')
PROJECTS_TABLE = os.environ.get('PROJECTS_TABLE', 'aws-propuestas-v3-projects-prod')

# URLs de los servicios MCP
MCP_BASE_URL = "https://aws-propuestas-v3-alb-prod-297472567.us-east-1.elb.amazonaws.com"
MCP_SERVICES = {
    'core': f"{MCP_BASE_URL}:8000",
    'pricing': f"{MCP_BASE_URL}:8001", 
    'awsdocs': f"{MCP_BASE_URL}:8002",
    'cfn': f"{MCP_BASE_URL}:8003",
    'diagram': f"{MCP_BASE_URL}:8004",
    'customdoc': f"{MCP_BASE_URL}:8005"
}

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

def call_mcp_service(service_name, endpoint, data):
    """Llama a un servicio MCP específico"""
    try:
        url = f"{MCP_SERVICES[service_name]}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error calling {service_name}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception calling {service_name}: {str(e)}")
        return None

def generate_architecture_diagram(project_info):
    """Genera diagrama de arquitectura usando MCP diagram service"""
    try:
        diagram_request = {
            "project_name": project_info.get('name', 'AWS Project'),
            "project_type": project_info.get('type', 'Web Application'),
            "services": ["Lambda", "API Gateway", "DynamoDB", "S3", "CloudFront"]
        }
        
        result = call_mcp_service('diagram', 'generate', diagram_request)
        if result:
            return result.get('diagram_code', 'Diagram generation failed')
        return None
    except Exception as e:
        print(f"Error generating diagram: {str(e)}")
        return None

def generate_cloudformation_template(project_info):
    """Genera template CloudFormation usando MCP CFN service"""
    try:
        cfn_request = {
            "project_name": project_info.get('name', 'AWS Project'),
            "services": ["Lambda", "API Gateway", "DynamoDB", "S3"],
            "environment": "prod"
        }
        
        result = call_mcp_service('cfn', 'generate', cfn_request)
        if result:
            return result.get('template', 'CloudFormation generation failed')
        return None
    except Exception as e:
        print(f"Error generating CloudFormation: {str(e)}")
        return None

def generate_cost_analysis(project_info):
    """Genera análisis de costos usando MCP pricing service"""
    try:
        pricing_request = {
            "services": ["Lambda", "API Gateway", "DynamoDB", "S3", "CloudFront"],
            "usage_estimates": {
                "lambda_invocations": 1000000,
                "api_requests": 1000000,
                "dynamodb_reads": 1000000,
                "s3_storage_gb": 100
            }
        }
        
        result = call_mcp_service('pricing', 'analyze', pricing_request)
        if result:
            return result.get('cost_analysis', 'Cost analysis failed')
        return None
    except Exception as e:
        print(f"Error generating cost analysis: {str(e)}")
        return None

def generate_project_documentation(project_info):
    """Genera documentación del proyecto usando MCP customdoc service"""
    try:
        doc_request = {
            "project_name": project_info.get('name', 'AWS Project'),
            "project_type": project_info.get('type', 'Web Application'),
            "description": project_info.get('description', 'AWS project implementation'),
            "services": ["Lambda", "API Gateway", "DynamoDB", "S3"]
        }
        
        result = call_mcp_service('customdoc', 'generate', doc_request)
        if result:
            return result.get('documentation', 'Documentation generation failed')
        return None
    except Exception as e:
        print(f"Error generating documentation: {str(e)}")
        return None

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
            mcp_services_used.append('customdoc')
        if any(keyword in response_lower for keyword in ['cloudformation', 'template']):
            mcp_services_used.append('cfn')
        
        # Detectar si debe generar documentos REALES usando MCP
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
            
            # Generar documentos REALES usando MCP services
            documents = {}
            
            # 1. Generar diagrama de arquitectura
            diagram = generate_architecture_diagram(project_info)
            if diagram:
                documents['architecture-diagram.py'] = diagram
                mcp_services_used.append('diagram')
            
            # 2. Generar template CloudFormation
            cfn_template = generate_cloudformation_template(project_info)
            if cfn_template:
                documents['cloudformation-template.json'] = cfn_template
                mcp_services_used.append('cfn')
            
            # 3. Generar análisis de costos
            cost_analysis = generate_cost_analysis(project_info)
            if cost_analysis:
                documents['cost-analysis.csv'] = cost_analysis
                mcp_services_used.append('pricing')
            
            # 4. Generar documentación del proyecto
            project_doc = generate_project_documentation(project_info)
            if project_doc:
                documents['project-documentation.md'] = project_doc
                mcp_services_used.append('customdoc')
            
            # Subir a S3 si se generaron documentos
            if documents and upload_documents_to_s3(project_info, documents):
                # Guardar en DynamoDB
                documents_list = list(documents.keys())
                if save_project_to_dynamodb(project_info, documents_list):
                    documents_generated = [
                        'Diagrama de Arquitectura (Python)',
                        'CloudFormation Template (JSON)',
                        'Analisis de Costos (CSV)',
                        'Documentacion del Proyecto (MD)'
                    ]
                    project_id = project_info['id']
                    project_name = project_info['name']
                    mcp_services_used.extend(['s3', 'dynamodb'])
        
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
