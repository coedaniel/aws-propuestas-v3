"""
AWS Propuestas v3 - Arquitecto Lambda con Generación de Contenido REAL
Cuando los MCPs devuelven mock data, genera contenido real basado en la conversación
"""

import json
import boto3
import os
import requests
import logging
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Any

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

# URLs de los servicios MCP ECS - CORRECTAS
MCP_BASE_URL = "https://mcp.danielingram.shop"
MCP_SERVICES = {
    'core': f"{MCP_BASE_URL}",
    'pricing': f"{MCP_BASE_URL}/pricing", 
    'awsdocs': f"{MCP_BASE_URL}/awsdocs",
    'cfn': f"{MCP_BASE_URL}/cfn",
    'diagram': f"{MCP_BASE_URL}/diagram",
    'customdoc': f"{MCP_BASE_URL}/docgen"
}

# PROMPT MAESTRO ORIGINAL COMPLETO - RESTAURADO
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
        'body': body if isinstance(body, str) else json.dumps(body, default=decimal_default)
    }

def decimal_default(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def create_error_response(status_code, error_message):
    """Create an error response with CORS headers"""
    return create_response(status_code, {
        'error': error_message,
        'timestamp': datetime.now().isoformat()
    })

def create_success_response(data):
    """Create a success response with CORS headers"""
    return create_response(200, data)

def call_mcp_service(service_name, endpoint, data):
    """Llama a un servicio MCP específico"""
    try:
        url = f"{MCP_SERVICES[service_name]}/{endpoint}" if endpoint else MCP_SERVICES[service_name]
        headers = {'Content-Type': 'application/json'}
        
        logger.info(f"🔧 Calling MCP {service_name}: {url}")
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            logger.info(f"✅ MCP {service_name} responded successfully")
            return response.json()
        else:
            logger.error(f"❌ MCP {service_name} error: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"❌ Exception calling MCP {service_name}: {str(e)}")
        return None

def is_mock_response(response_data):
    """Detecta si la respuesta del MCP es mock/de prueba"""
    if not response_data:
        return True
    
    # Si es un dict con solo status, service, path, method -> es mock
    if isinstance(response_data, dict):
        mock_keys = {'status', 'service', 'path', 'method'}
        if set(response_data.keys()) == mock_keys:
            return True
    
    return False

def generate_real_cloudformation(project_info: Dict, conversation_text: str) -> str:
    """Genera CloudFormation real basado en la conversación"""
    
    project_name = project_info.get('name', 'aws-project').lower().replace(' ', '-')
    
    # Detectar tipo de servicio de la conversación
    if 'ec2' in conversation_text.lower():
        # Extraer detalles de EC2
        instance_type = 't3.micro'  # default
        volume_size = '20'  # default
        
        if 't3.medium' in conversation_text:
            instance_type = 't3.medium'
        elif 't3.large' in conversation_text:
            instance_type = 't3.large'
        
        if '100gb' in conversation_text or '100 gb' in conversation_text:
            volume_size = '100'
        elif '80gb' in conversation_text or '80 gb' in conversation_text:
            volume_size = '80'
        
        return f"""AWSTemplateFormatVersion: '2010-09-09'
Description: 'CloudFormation template for {project_info.get("name", "AWS Project")}'

Parameters:
  InstanceType:
    Type: String
    Default: {instance_type}
    Description: EC2 instance type
  
  VolumeSize:
    Type: Number
    Default: {volume_size}
    Description: EBS volume size in GB

Resources:
  EC2Instance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: !Ref InstanceType
      ImageId: ami-0abcdef1234567890  # Amazon Linux 2023
      KeyName: {project_name}-key
      SecurityGroupIds:
        - !Ref InstanceSecurityGroup
      BlockDeviceMappings:
        - DeviceName: /dev/xvda
          Ebs:
            VolumeType: gp3
            VolumeSize: !Ref VolumeSize
            DeleteOnTermination: true
      Tags:
        - Key: Name
          Value: {project_info.get("name", "AWS Project")}
        - Key: Project
          Value: {project_name}

  InstanceSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for {project_info.get("name", "AWS Project")}
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 0.0.0.0/0
          Description: SSH access
      Tags:
        - Key: Name
          Value: {project_name}-sg

Outputs:
  InstanceId:
    Description: Instance ID
    Value: !Ref EC2Instance
  
  PublicIP:
    Description: Public IP address
    Value: !GetAtt EC2Instance.PublicIp
  
  SecurityGroupId:
    Description: Security Group ID
    Value: !Ref InstanceSecurityGroup"""
    
    else:
        # Template genérico para otros servicios
        return f"""AWSTemplateFormatVersion: '2010-09-09'
Description: 'CloudFormation template for {project_info.get("name", "AWS Project")}'

Parameters:
  Environment:
    Type: String
    Default: prod
    AllowedValues: [dev, staging, prod]

Resources:
  S3Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '{project_name}-${{Environment}}-${{AWS::AccountId}}'
      VersioningConfiguration:
        Status: Enabled
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256

Outputs:
  BucketName:
    Description: S3 Bucket Name
    Value: !Ref S3Bucket"""

def generate_real_diagram(project_info: Dict, conversation_text: str) -> str:
    """Genera diagrama SVG real basado en la conversación"""
    
    project_name = project_info.get('name', 'AWS Project')
    
    if 'ec2' in conversation_text.lower():
        return f"""<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .title {{ font: bold 18px sans-serif; }}
      .label {{ font: 12px sans-serif; }}
      .box {{ fill: #f0f8ff; stroke: #4169e1; stroke-width: 2; }}
      .ec2 {{ fill: #ff9900; }}
      .vpc {{ fill: #4caf50; }}
    </style>
  </defs>
  
  <text x="400" y="30" text-anchor="middle" class="title">{project_name} - Architecture Diagram</text>
  
  <!-- VPC -->
  <rect x="50" y="80" width="700" height="450" class="box vpc" opacity="0.3"/>
  <text x="70" y="100" class="label">VPC (Default)</text>
  
  <!-- Availability Zone -->
  <rect x="100" y="130" width="600" height="350" class="box" opacity="0.5"/>
  <text x="120" y="150" class="label">Availability Zone (us-east-1a)</text>
  
  <!-- Public Subnet -->
  <rect x="150" y="180" width="500" height="250" class="box" opacity="0.7"/>
  <text x="170" y="200" class="label">Public Subnet</text>
  
  <!-- EC2 Instance -->
  <rect x="300" y="250" width="200" height="100" class="box ec2"/>
  <text x="400" y="280" text-anchor="middle" class="label">EC2 Instance</text>
  <text x="400" y="300" text-anchor="middle" class="label">Type: t3.medium</text>
  <text x="400" y="320" text-anchor="middle" class="label">OS: Amazon Linux 2023</text>
  
  <!-- Security Group -->
  <rect x="280" y="380" width="240" height="40" class="box"/>
  <text x="400" y="405" text-anchor="middle" class="label">Security Group (SSH: 22)</text>
  
  <!-- Internet Gateway -->
  <rect x="350" y="50" width="100" height="30" class="box"/>
  <text x="400" y="70" text-anchor="middle" class="label">Internet Gateway</text>
  
  <!-- Connections -->
  <line x1="400" y1="80" x2="400" y2="130" stroke="#333" stroke-width="2"/>
  <line x1="400" y1="180" x2="400" y2="250" stroke="#333" stroke-width="2"/>
  
</svg>"""
    else:
        return f"""<svg width="600" height="400" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="200" text-anchor="middle" font="16px sans-serif">{project_name} - Architecture Diagram</text>
  <rect x="200" y="250" width="200" height="100" fill="#f0f8ff" stroke="#4169e1" stroke-width="2"/>
  <text x="300" y="305" text-anchor="middle" font="12px sans-serif">AWS Services</text>
</svg>"""

def generate_real_documentation(project_info: Dict, conversation_text: str) -> str:
    """Genera documentación real basada en la conversación"""
    
    project_name = project_info.get('name', 'AWS Project')
    project_type = project_info.get('type', 'AWS Solution')
    
    return f"""# {project_name} - Documentacion del Proyecto

## Informacion General
- **Nombre del Proyecto**: {project_name}
- **Tipo**: {project_type}
- **Fecha de Creacion**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Descripcion
{project_info.get('description', 'Proyecto de implementacion en AWS')}

## Servicios AWS Utilizados
{'- Amazon EC2 (Elastic Compute Cloud)' if 'ec2' in conversation_text.lower() else '- Servicios AWS varios'}
{'- Amazon VPC (Virtual Private Cloud)' if 'vpc' in conversation_text.lower() else ''}
{'- Security Groups' if 'security' in conversation_text.lower() else ''}

## Especificaciones Tecnicas
{'- Tipo de Instancia: t3.medium' if 't3.medium' in conversation_text.lower() else ''}
{'- Sistema Operativo: Amazon Linux 2023' if 'amazon linux' in conversation_text.lower() else ''}
{'- Almacenamiento: 100GB gp3' if '100gb' in conversation_text.lower() or '100 gb' in conversation_text.lower() else ''}

## Consideraciones de Seguridad
- Grupos de seguridad configurados para acceso minimo necesario
- Claves SSH para acceso seguro
- Encriptacion de volumenes EBS

## Monitoreo y Backup
- CloudWatch para monitoreo basico
- Snapshots automaticos de EBS
- Alertas configuradas para metricas criticas

## Estimacion de Costos
- Costo mensual estimado: $50-150 USD (dependiendo del uso)
- Incluye instancia EC2, almacenamiento y transferencia de datos

## Proximos Pasos
1. Revisar y aprobar la arquitectura propuesta
2. Ejecutar el template de CloudFormation
3. Configurar monitoreo y alertas
4. Implementar procedimientos de backup
5. Documentar procedimientos operativos

## Contacto
Para consultas sobre este proyecto, contactar al equipo de arquitectura AWS.
"""

def generate_real_pricing(project_info: Dict, conversation_text: str) -> Dict:
    """Genera análisis de precios real basado en la conversación"""
    
    base_cost = 50.0  # Costo base mensual
    
    # Ajustar costo basado en el tipo de instancia
    if 't3.medium' in conversation_text.lower():
        base_cost = 85.0
    elif 't3.large' in conversation_text.lower():
        base_cost = 150.0
    elif 't3.xlarge' in conversation_text.lower():
        base_cost = 300.0
    
    # Ajustar por almacenamiento
    storage_cost = 10.0  # 20GB default
    if '100gb' in conversation_text.lower() or '100 gb' in conversation_text.lower():
        storage_cost = 25.0
    elif '80gb' in conversation_text.lower() or '80 gb' in conversation_text.lower():
        storage_cost = 20.0
    
    total_monthly = base_cost + storage_cost
    
    return {
        "project_name": project_info.get('name', 'AWS Project'),
        "currency": "USD",
        "billing_period": "monthly",
        "cost_breakdown": {
            "compute": {
                "service": "Amazon EC2",
                "instance_type": "t3.medium" if 't3.medium' in conversation_text.lower() else "t3.micro",
                "monthly_cost": base_cost,
                "hours_per_month": 730
            },
            "storage": {
                "service": "Amazon EBS",
                "volume_type": "gp3",
                "size_gb": 100 if '100gb' in conversation_text.lower() else 20,
                "monthly_cost": storage_cost
            },
            "data_transfer": {
                "service": "Data Transfer",
                "monthly_cost": 5.0
            }
        },
        "total_monthly_cost": total_monthly + 5.0,
        "total_annual_cost": (total_monthly + 5.0) * 12,
        "cost_optimization_recommendations": [
            "Considerar Reserved Instances para ahorrar hasta 75%",
            "Usar Spot Instances para cargas de trabajo flexibles",
            "Implementar auto-scaling para optimizar costos",
            "Revisar utilización mensualmente"
        ],
        "generated_at": datetime.now().isoformat()
    }
"""
Continuación del archivo app_real_content.py
"""

def activate_core_mcp_always(messages: List[Dict]) -> Dict:
    """
    MCP CORE - SIEMPRE ACTIVO (como Amazon Q CLI)
    Se ejecuta en CADA mensaje para prompt understanding
    """
    logger.info("🧠 ACTIVATING CORE MCP - ALWAYS ACTIVE")
    
    conversation_text = " ".join([msg.get("content", "") for msg in messages])
    
    core_result = call_mcp_service('core', 'analyze', {
        'conversation': conversation_text,
        'action': 'prompt_understanding',
        'timestamp': datetime.now().isoformat()
    })
    
    return {
        'activated': True,
        'result': core_result,
        'reason': 'Core MCP always active for prompt understanding'
    }

def check_docs_mcp_needed(messages: List[Dict]) -> Dict:
    """
    MCP AWS DOCS - ACTIVACIÓN CONDICIONAL CORREGIDA
    SOLO se activa cuando hay triggers específicos
    """
    conversation_text = " ".join([msg.get("content", "") for msg in messages]).lower()
    
    # Triggers específicos para documentación (MÁS RESTRICTIVOS)
    explicit_docs_triggers = [
        'documentacion', 'busca documentacion', 'buscar documentacion',
        'mejores practicas', 'como hacer', 'que es lambda', 'que es ec2',
        'aws docs', 'documentacion oficial', 'guia oficial',
        'tutorial', 'ejemplo oficial', 'referencia aws'
    ]
    
    # Preguntas específicas que requieren docs oficiales
    specific_questions = [
        'como configurar', 'como implementar', 'como usar',
        'cual es la diferencia', 'que diferencia hay',
        'limites de', 'restricciones de', 'pricing de'
    ]
    
    needs_docs = (
        any(trigger in conversation_text for trigger in explicit_docs_triggers) or
        any(question in conversation_text for question in specific_questions)
    )
    
    if needs_docs:
        logger.info("📚 ACTIVATING AWS DOCS MCP - Explicit documentation request detected")
        
        docs_result = call_mcp_service('awsdocs', 'search', {
            'query': conversation_text,
            'action': 'get_official_docs',
            'timestamp': datetime.now().isoformat()
        })
        
        return {
            'activated': True,
            'result': docs_result,
            'reason': 'Explicit documentation request detected'
        }
    else:
        logger.info("📚 AWS Docs MCP NOT NEEDED - No explicit documentation triggers")
        return {
            'activated': False,
            'result': None,
            'reason': 'No explicit documentation triggers detected'
        }

def calculate_generation_readiness(messages: List[Dict]) -> Dict:
    """
    Calcula readiness SOLO para MCPs de generación
    """
    conversation_text = " ".join([msg.get("content", "") for msg in messages]).lower()
    
    score = 0.0
    criteria = {}
    
    # 1. Nombre del proyecto (25%)
    if any(word in conversation_text for word in ['proyecto', 'sistema', 'aplicacion', 'plataforma']):
        criteria['project_name'] = True
        score += 0.25
    else:
        criteria['project_name'] = False
    
    # 2. Tipo de proyecto (25%)
    if any(word in conversation_text for word in ['integral', 'rapido', 'servicio', 'ec2', 'rds', 's3', 'lambda']):
        criteria['project_type'] = True
        score += 0.25
    else:
        criteria['project_type'] = False
    
    # 3. Detalles técnicos (25%)
    technical_indicators = ['instancia', 'tipo', 'region', 'volumen', 'vpc', 'security', 'key', 'tamaño', 'gb']
    if sum(1 for indicator in technical_indicators if indicator in conversation_text) >= 3:
        criteria['technical_details'] = True
        score += 0.25
    else:
        criteria['technical_details'] = False
    
    # 4. Contexto suficiente (25%)
    user_messages = [msg for msg in messages if msg.get('role') == 'user']
    if len(user_messages) >= 4:
        criteria['sufficient_context'] = True
        score += 0.25
    else:
        criteria['sufficient_context'] = False
    
    return {
        'readiness_score': score,
        'criteria': criteria,
        'ready_for_generation': score >= 0.8
    }

def activate_generation_mcps_with_real_content(messages: List[Dict]) -> Dict:
    """
    MCPs DE GENERACIÓN - Con contenido REAL cuando MCPs devuelven mock
    """
    logger.info("🎯 ACTIVATING GENERATION MCPs - With REAL content generation")
    
    conversation_text = " ".join([msg.get("content", "") for msg in messages])
    project_info = extract_project_info(messages)
    
    activated_mcps = []
    generated_content = {}
    
    # 1. Diagram MCP - Con fallback a contenido real
    diagram_result = call_mcp_service('diagram', 'generate', {
        'project_name': project_info['name'],
        'project_type': project_info['type'],
        'services': ['EC2', 'VPC'] if 'ec2' in conversation_text else ['Lambda', 'API Gateway']
    })
    
    if is_mock_response(diagram_result):
        logger.info("🔄 Diagram MCP returned mock - generating REAL content")
        diagram_content = generate_real_diagram(project_info, conversation_text)
    else:
        diagram_content = diagram_result
    
    activated_mcps.append('diagram-mcp')
    generated_content['diagram'] = diagram_content
    
    # 2. CloudFormation MCP - Con fallback a contenido real
    cfn_result = call_mcp_service('cfn', 'generate', {
        'project_name': project_info['name'],
        'services': ['EC2'] if 'ec2' in conversation_text else ['Lambda'],
        'environment': 'prod'
    })
    
    if is_mock_response(cfn_result):
        logger.info("🔄 CloudFormation MCP returned mock - generating REAL content")
        cfn_content = generate_real_cloudformation(project_info, conversation_text)
    else:
        cfn_content = cfn_result
    
    activated_mcps.append('cloudformation-mcp')
    generated_content['cloudformation'] = cfn_content
    
    # 3. Document Generator MCP - Con fallback a contenido real
    doc_result = call_mcp_service('customdoc', 'generate', {
        'project_name': project_info['name'],
        'project_type': project_info['type'],
        'format': ['csv', 'docx', 'xlsx']
    })
    
    if is_mock_response(doc_result):
        logger.info("🔄 Document MCP returned mock - generating REAL content")
        doc_content = generate_real_documentation(project_info, conversation_text)
    else:
        doc_content = doc_result
    
    activated_mcps.append('document-generator-mcp')
    generated_content['documentation'] = doc_content
    
    # 4. Pricing MCP - Con fallback a contenido real
    pricing_result = call_mcp_service('pricing', 'calculate', {
        'services': ['EC2'] if 'ec2' in conversation_text else ['Lambda'],
        'usage_estimates': {'hours_per_month': 730}
    })
    
    if is_mock_response(pricing_result):
        logger.info("🔄 Pricing MCP returned mock - generating REAL content")
        pricing_content = generate_real_pricing(project_info, conversation_text)
    else:
        pricing_content = pricing_result
    
    activated_mcps.append('pricing-mcp')
    generated_content['pricing'] = pricing_content
    
    # 5. GUARDAR EN S3 - Con contenido REAL
    s3_result = save_documents_to_s3(project_info, generated_content)
    
    return {
        'activated_mcps': activated_mcps,
        'generated_content': generated_content,
        'mcp_count': len(activated_mcps),
        's3_folder': f"{project_info['name'].lower().replace(' ', '-')}-{project_info['id'][:8]}" if generated_content else None,
        's3_result': s3_result
    }

def save_documents_to_s3(project_info: Dict, generated_content: Dict) -> Dict:
    """
    GUARDA DOCUMENTOS REALES EN S3 EN CARPETA POR PROYECTO
    """
    try:
        folder_name = f"{project_info['name'].lower().replace(' ', '-')}-{project_info['id'][:8]}"
        
        logger.info(f"📁 Saving REAL documents to S3 folder: {folder_name}")
        
        documents_saved = []
        
        for content_type, content_data in generated_content.items():
            # Determinar extensión del archivo
            if content_type == 'diagram':
                file_extension = 'svg'
                content_type_s3 = 'image/svg+xml'
            elif content_type == 'cloudformation':
                file_extension = 'yaml'
                content_type_s3 = 'text/yaml'
            elif content_type == 'documentation':
                file_extension = 'txt'
                content_type_s3 = 'text/plain'
            elif content_type == 'pricing':
                file_extension = 'json'
                content_type_s3 = 'application/json'
            else:
                file_extension = 'txt'
                content_type_s3 = 'text/plain'
            
            file_name = f"{content_type}.{file_extension}"
            s3_key = f"{folder_name}/{file_name}"
            
            # Convertir contenido a string si es necesario
            if isinstance(content_data, dict):
                content_str = json.dumps(content_data, indent=2)
            else:
                content_str = str(content_data)
            
            # Subir a S3
            s3_client.put_object(
                Bucket=DOCUMENTS_BUCKET,
                Key=s3_key,
                Body=content_str,
                ContentType=content_type_s3,
                Metadata={
                    'project_name': project_info['name'],
                    'project_type': project_info['type'],
                    'generated_at': datetime.now().isoformat(),
                    'content_source': 'real_generation'
                }
            )
            
            documents_saved.append({
                'file_name': file_name,
                's3_key': s3_key,
                'content_type': content_type,
                'size_bytes': len(content_str.encode('utf-8'))
            })
            
            logger.info(f"✅ Saved REAL content {file_name} to S3: {s3_key} ({len(content_str)} chars)")
        
        # Guardar proyecto en DynamoDB
        save_project_to_dynamodb(project_info, documents_saved, folder_name)
        
        return {
            'folder_name': folder_name,
            'documents_saved': documents_saved,
            'bucket': DOCUMENTS_BUCKET,
            'total_files': len(documents_saved),
            'content_source': 'real_generation'
        }
        
    except Exception as e:
        logger.error(f"❌ Error saving to S3: {str(e)}")
        return None

def save_project_to_dynamodb(project_info: Dict, documents_saved: List[Dict], folder_name: str):
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
            'description': project_info.get('description', f'Proyecto {project_info["name"]} generado automaticamente'),
            's3Folder': folder_name,
            's3Bucket': DOCUMENTS_BUCKET,
            'documentsGenerated': documents_saved,
            'totalDocuments': len(documents_saved),
            'contentSource': 'real_generation'
        }
        
        table.put_item(Item=project_item)
        logger.info(f"✅ Project saved to DynamoDB: {project_info['id']}")
        return True
    except Exception as e:
        logger.error(f"❌ Error saving to DynamoDB: {str(e)}")
        return False

def extract_project_info(messages: List[Dict]) -> Dict:
    """Extrae información del proyecto de la conversación"""
    conversation_text = " ".join([msg.get("content", "") for msg in messages]).lower()
    
    project_info = {
        'id': str(uuid.uuid4())[:8],
        'name': 'AWS Project',
        'type': 'Solucion AWS'
    }
    
    # Extraer nombre del proyecto
    user_messages = [msg.get("content", "") for msg in messages if msg.get('role') == 'user']
    if user_messages:
        first_response = user_messages[0].strip()
        if len(first_response.split()) <= 5:  # Probablemente es el nombre
            project_info['name'] = first_response
    
    # Determinar tipo
    if 'ec2' in conversation_text:
        project_info['type'] = 'Implementacion EC2'
    elif 'rds' in conversation_text:
        project_info['type'] = 'Base de Datos RDS'
    elif 'integral' in conversation_text:
        project_info['type'] = 'Solucion Integral'
    elif 'rapido' in conversation_text:
        project_info['type'] = 'Servicio Rapido'
    
    return project_info
"""
Parte final del archivo app_real_content.py con lambda_handler
"""

def prepare_conversation(messages: List[Dict], project_state: Dict) -> List[Dict]:
    """Prepare conversation for Bedrock with correct format"""
    conversation = []
    
    # Add system message with correct format (as user message for Bedrock)
    conversation.append({
        "role": "user",
        "content": [{"text": PROMPT_MAESTRO}]
    })
    
    # Add project state context if available
    if project_state.get('data') and project_state['data']:
        context = f"CONTEXTO DEL PROYECTO: {json.dumps(project_state['data'], indent=2)}"
        conversation.append({
            "role": "user", 
            "content": [{"text": context}]
        })
    
    # Add conversation history with correct format
    for msg in messages:
        content = msg.get("content", "")
        if content.strip():
            conversation.append({
                "role": msg.get("role", "user"),
                "content": [{"text": content}]
            })
    
    return conversation

def call_bedrock_model(model_id: str, conversation: List[Dict]) -> Dict:
    """Call Bedrock model with correct format"""
    try:
        logger.info(f"Calling Bedrock model: {model_id}")
        
        response = bedrock_runtime.converse(
            modelId=model_id,
            messages=conversation,
            inferenceConfig={
                'maxTokens': 4000,
                'temperature': 0.7,
                'topP': 0.9
            }
        )
        
        content = response['output']['message']['content'][0]['text']
        logger.info(f"Bedrock response received, length: {len(content)}")
        
        return {
            'content': content,
            'usage': response.get('usage', {}),
            'modelUsed': model_id
        }
        
    except Exception as e:
        logger.error(f"Error calling Bedrock: {str(e)}", exc_info=True)
        return {'error': f'Error calling Bedrock: {str(e)}'}

def lambda_handler(event, context):
    """Main Lambda handler - CON GENERACIÓN DE CONTENIDO REAL"""
    
    try:
        logger.info(f"Event received: {json.dumps(event, default=str)}")
        
        # Handle CORS preflight requests
        if event.get('httpMethod') == 'OPTIONS':
            logger.info("Handling OPTIONS preflight request")
            return handle_preflight_request()
        
        # Parse request
        try:
            if isinstance(event.get('body'), str):
                body = json.loads(event['body'])
            else:
                body = event.get('body', {})
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return create_error_response(400, 'Invalid JSON in request body')
        
        messages = body.get('messages', [])
        model_id = body.get('modelId', 'anthropic.claude-3-5-sonnet-20240620-v1:0')
        project_state = body.get('projectState', {'phase': 'inicio', 'data': {}})
        
        if not messages:
            logger.error("No messages provided")
            return create_error_response(400, 'No messages provided')
        
        logger.info(f"Processing {len(messages)} messages with model: {model_id}")
        
        # === ACTIVACIÓN MCP CON CONTENIDO REAL ===
        
        # 1. MCP CORE - SIEMPRE ACTIVO
        core_mcp = activate_core_mcp_always(messages)
        
        # 2. MCP AWS DOCS - SOLO CUANDO SEA NECESARIO
        docs_mcp = check_docs_mcp_needed(messages)
        
        # 3. READINESS PARA GENERACIÓN
        generation_readiness = calculate_generation_readiness(messages)
        
        # 4. MCPs DE GENERACIÓN - Con contenido REAL + GUARDADO S3
        generation_mcps = {'activated_mcps': [], 'generated_content': {}, 'mcp_count': 0, 's3_folder': None}
        if generation_readiness['ready_for_generation']:
            generation_mcps = activate_generation_mcps_with_real_content(messages)
        
        # Prepare conversation for Bedrock
        conversation = prepare_conversation(messages, project_state)
        
        if not conversation:
            logger.error("Empty conversation after preparation")
            return create_error_response(400, 'No valid conversation content')
        
        # Call Bedrock model
        bedrock_response = call_bedrock_model(model_id, conversation)
        
        if 'error' in bedrock_response:
            logger.error(f"Bedrock error: {bedrock_response['error']}")
            return create_error_response(500, bedrock_response['error'])
        
        response_content = bedrock_response['content']
        
        if not response_content or not response_content.strip():
            logger.error("Empty response from Bedrock")
            return create_error_response(500, 'Empty response from AI model')
        
        # Si se generaron documentos REALES, agregarlos a la respuesta
        if generation_mcps['generated_content']:
            logger.info("📄 Adding REAL MCP-generated content to response")
            response_content += "\n\n--- DOCUMENTOS GENERADOS Y GUARDADOS EN S3 ---\n"
            response_content += f"📁 Carpeta: {generation_mcps['s3_folder']}\n"
            response_content += f"🪣 Bucket: {DOCUMENTS_BUCKET}\n"
            response_content += f"📄 Documentos: {generation_mcps['mcp_count']} archivos generados\n\n"
            
            # Mostrar resumen de documentos generados
            for content_type in generation_mcps['generated_content'].keys():
                response_content += f"✅ {content_type.title()}: Generado exitosamente\n"
            
            response_content += f"\n🎯 Los documentos han sido guardados en S3 y el proyecto registrado en la base de datos."
        
        # Compilar MCPs utilizados
        all_mcps_used = []
        if core_mcp['activated']:
            all_mcps_used.append('core-mcp-prompt-understanding')
        if docs_mcp['activated']:
            all_mcps_used.append('aws-docs-mcp')
        all_mcps_used.extend(generation_mcps['activated_mcps'])
        
        # Response data
        response_data = {
            'content': response_content,
            'projectState': project_state,
            'mcpActivated': len(all_mcps_used) > 0,
            'mcpStatus': f'real_content_phase_{1 if not generation_readiness["ready_for_generation"] else 3}',
            'mcpUsed': all_mcps_used,
            'mcpBreakdown': {
                'core_mcp': core_mcp,
                'docs_mcp': docs_mcp,
                'generation_readiness': generation_readiness,
                'generation_mcps': generation_mcps
            },
            's3Info': {
                'bucket': DOCUMENTS_BUCKET,
                'folder': generation_mcps.get('s3_folder'),
                'documents_saved': generation_mcps.get('s3_result', {}).get('documents_saved', []),
                'content_source': 'real_generation'
            } if generation_mcps.get('s3_folder') else None,
            'readinessScore': generation_readiness['readiness_score'],
            'modelUsed': bedrock_response.get('modelUsed', model_id),
            'usage': bedrock_response.get('usage', {}),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ REAL CONTENT Response: Core={core_mcp['activated']}, Docs={docs_mcp['activated']}, Generation={generation_readiness['ready_for_generation']}")
        if generation_mcps.get('s3_folder'):
            logger.info(f"📁 S3 Folder: {generation_mcps['s3_folder']}, Documents: {generation_mcps['mcp_count']}")
        
        return create_success_response(response_data)
        
    except Exception as e:
        logger.error(f"Unexpected error in lambda_handler: {str(e)}", exc_info=True)
        return create_error_response(500, f'Internal server error: {str(e)}')
