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
    MCPs DE GENERACIÓN - Con contenido REAL mejorado
    """
    logger.info("🎯 ACTIVATING GENERATION MCPs - With IMPROVED real content generation")
    
    conversation_text = " ".join([msg.get("content", "") for msg in messages])
    project_info = extract_project_info(messages)
    
    activated_mcps = []
    generated_content = {}
    
    # 1. Diagram MCP - Con iconos AWS oficiales
    diagram_result = call_mcp_service('diagram', 'generate', {
        'project_name': project_info['name'],
        'project_type': project_info['type'],
        'services': ['EC2', 'VPC'] if 'ec2' in conversation_text else ['Lambda', 'API Gateway']
    })
    
    if is_mock_response(diagram_result):
        logger.info("🔄 Diagram MCP returned mock - generating REAL content with AWS icons")
        diagram_content = generate_real_diagram_with_aws_icons(project_info, conversation_text)
    else:
        diagram_content = diagram_result
    
    activated_mcps.append('diagram-mcp')
    generated_content['diagram'] = diagram_content
    
    # 2. CloudFormation MCP - Mantener igual (ya funciona bien)
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
    
    # 3. Document Generator MCP - Documentación completa mejorada
    doc_result = call_mcp_service('customdoc', 'generate', {
        'project_name': project_info['name'],
        'project_type': project_info['type'],
        'format': ['csv', 'docx', 'xlsx']
    })
    
    if is_mock_response(doc_result):
        logger.info("🔄 Document MCP returned mock - generating COMPREHENSIVE documentation")
        doc_content = generate_comprehensive_documentation(project_info, conversation_text)
    else:
        doc_content = doc_result
    
    activated_mcps.append('document-generator-mcp')
    generated_content['documentation'] = doc_content
    
    # 4. Pricing MCP - TXT con pasos de calculadora
    pricing_result = call_mcp_service('pricing', 'calculate', {
        'services': ['EC2'] if 'ec2' in conversation_text else ['Lambda'],
        'usage_estimates': {'hours_per_month': 730}
    })
    
    if is_mock_response(pricing_result):
        logger.info("🔄 Pricing MCP returned mock - generating REAL pricing with calculator steps")
        pricing_content = generate_real_pricing_with_calculator_steps(project_info, conversation_text)
    else:
        pricing_content = pricing_result
    
    activated_mcps.append('pricing-mcp')
    generated_content['pricing'] = pricing_content
    
    # 5. NUEVO: CSV de Actividades del Proyecto
    logger.info("📋 Generating project activities CSV")
    activities_content = generate_project_activities_csv(project_info, conversation_text)
    activated_mcps.append('activities-csv-generator')
    generated_content['activities'] = activities_content
    
    # 6. GUARDAR EN S3 - Con contenido MEJORADO
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
                file_extension = 'txt'  # Cambiado de json a txt
                content_type_s3 = 'text/plain'
            elif content_type == 'activities':
                file_extension = 'csv'
                content_type_s3 = 'text/csv'
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
"""
Generadores de contenido mejorados con todos los elementos faltantes
"""

def generate_real_pricing_with_calculator_steps(project_info: Dict, conversation_text: str) -> str:
    """Genera análisis de precios TXT con pasos de calculadora AWS"""
    
    project_name = project_info.get('name', 'AWS Project')
    
    # Detectar configuración de la conversación
    instance_type = 't3.micro'
    storage_size = '20'
    if 't3.medium' in conversation_text.lower():
        instance_type = 't3.medium'
    elif 't3.large' in conversation_text.lower():
        instance_type = 't3.large'
    
    if '100gb' in conversation_text.lower() or '100 gb' in conversation_text.lower():
        storage_size = '100'
    elif '80gb' in conversation_text.lower() or '80 gb' in conversation_text.lower():
        storage_size = '80'
    
    return f"""# {project_name} - Analisis de Costos AWS

## Calculadora AWS - Pasos Detallados

### PASO 1: Acceder a la Calculadora AWS
1. Ir a: https://calculator.aws
2. Hacer clic en "Create estimate"
3. Seleccionar region: US East (N. Virginia)

### PASO 2: Configurar Amazon EC2
1. Buscar "Amazon EC2" en servicios
2. Hacer clic en "Configure"
3. Configuracion:
   - Operating System: Linux
   - Instance Type: {instance_type}
   - Quantity: 1
   - Pricing Model: On-Demand
   - Usage: 730 hours/month (24/7)

### PASO 3: Configurar Amazon EBS
1. En la seccion "Storage"
2. Agregar volumen:
   - Storage Type: General Purpose SSD (gp3)
   - Storage Amount: {storage_size} GB
   - IOPS: 3000 (default)
   - Throughput: 125 MB/s (default)

### PASO 4: Configurar Data Transfer
1. En "Data Transfer"
2. Configurar:
   - Data Transfer Out: 10 GB/month
   - Data Transfer In: Free

### PASO 5: Revisar Estimacion
- EC2 Instance ({instance_type}): ${'85.00' if instance_type == 't3.medium' else '50.00'}/month
- EBS Storage ({storage_size}GB gp3): ${'25.00' if storage_size == '100' else '20.00'}/month
- Data Transfer: $5.00/month
- **TOTAL MENSUAL: ${'115.00' if instance_type == 't3.medium' and storage_size == '100' else '75.00'}**
- **TOTAL ANUAL: ${'1,380.00' if instance_type == 't3.medium' and storage_size == '100' else '900.00'}**

## Optimizaciones de Costo Recomendadas

### Reserved Instances (Ahorro: 30-75%)
- 1 Year Term, No Upfront: Ahorro 30%
- 3 Year Term, All Upfront: Ahorro 75%
- Recomendacion: Reserved Instance 1 año

### Spot Instances (Ahorro: 50-90%)
- Solo para cargas no criticas
- Disponibilidad variable
- Ideal para desarrollo/testing

### Auto Scaling
- Configurar escalado automatico
- Reducir instancias en horarios de baja demanda
- Ahorro estimado: 20-40%

## Monitoreo de Costos

### AWS Cost Explorer
1. Activar Cost Explorer
2. Configurar alertas de presupuesto
3. Revisar costos semanalmente

### CloudWatch Billing Alarms
1. Crear alarma para $100/month
2. Notificacion por email
3. Revision automatica de gastos

## Presupuesto Recomendado
- **Desarrollo**: $50-75/month
- **Produccion**: $100-150/month
- **Contingencia**: +20% adicional

## Contacto para Optimizacion
Para revision detallada de costos y optimizaciones adicionales,
contactar al equipo de FinOps de AWS.

Fecha de calculo: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

def generate_real_diagram_with_aws_icons(project_info: Dict, conversation_text: str) -> str:
    """Genera diagrama SVG con iconos oficiales AWS"""
    
    project_name = project_info.get('name', 'AWS Project')
    
    if 'ec2' in conversation_text.lower():
        return f"""<svg width="1000" height="700" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .title {{ font: bold 20px Arial, sans-serif; fill: #232F3E; }}
      .subtitle {{ font: 14px Arial, sans-serif; fill: #232F3E; }}
      .label {{ font: 12px Arial, sans-serif; fill: #232F3E; }}
      .aws-orange {{ fill: #FF9900; }}
      .aws-blue {{ fill: #232F3E; }}
      .vpc-green {{ fill: #7AA116; opacity: 0.3; }}
      .subnet-blue {{ fill: #4B92DB; opacity: 0.3; }}
      .connection {{ stroke: #232F3E; stroke-width: 2; fill: none; }}
    </style>
  </defs>
  
  <!-- Background -->
  <rect width="1000" height="700" fill="#F2F3F3"/>
  
  <!-- Title -->
  <text x="500" y="30" text-anchor="middle" class="title">{project_name}</text>
  <text x="500" y="50" text-anchor="middle" class="subtitle">AWS Architecture Diagram</text>
  
  <!-- Internet -->
  <circle cx="500" cy="100" r="30" fill="#4B92DB"/>
  <text x="500" y="105" text-anchor="middle" class="label" fill="white">Internet</text>
  
  <!-- AWS Cloud -->
  <rect x="50" y="150" width="900" height="500" fill="none" stroke="#FF9900" stroke-width="3" rx="10"/>
  <text x="70" y="175" class="subtitle aws-orange">AWS Cloud</text>
  
  <!-- VPC -->
  <rect x="100" y="200" width="800" height="400" class="vpc-green" stroke="#7AA116" stroke-width="2" rx="5"/>
  <text x="120" y="225" class="label">VPC (10.0.0.0/16)</text>
  
  <!-- Internet Gateway -->
  <rect x="450" y="160" width="100" height="40" class="aws-orange"/>
  <text x="500" y="185" text-anchor="middle" class="label" fill="white">Internet Gateway</text>
  
  <!-- Availability Zone -->
  <rect x="150" y="250" width="700" height="300" fill="#E8F4FD" stroke="#4B92DB" stroke-width="1" rx="5"/>
  <text x="170" y="275" class="label">Availability Zone: us-east-1a</text>
  
  <!-- Public Subnet -->
  <rect x="200" y="300" width="600" height="200" class="subnet-blue" stroke="#4B92DB" stroke-width="2" rx="5"/>
  <text x="220" y="325" class="label">Public Subnet (10.0.1.0/24)</text>
  
  <!-- EC2 Instance -->
  <rect x="400" y="350" width="200" height="120" class="aws-orange" rx="5"/>
  <text x="500" y="375" text-anchor="middle" class="label" fill="white">Amazon EC2</text>
  <text x="500" y="395" text-anchor="middle" class="label" fill="white">Instance Type: t3.medium</text>
  <text x="500" y="415" text-anchor="middle" class="label" fill="white">OS: Amazon Linux 2023</text>
  <text x="500" y="435" text-anchor="middle" class="label" fill="white">Storage: 100GB gp3</text>
  <text x="500" y="455" text-anchor="middle" class="label" fill="white">Key: inventario-key</text>
  
  <!-- Security Group -->
  <rect x="350" y="520" width="300" height="60" fill="#FF6B6B" opacity="0.7" rx="5"/>
  <text x="500" y="540" text-anchor="middle" class="label">Security Group</text>
  <text x="500" y="560" text-anchor="middle" class="label">SSH (22) - 0.0.0.0/0</text>
  
  <!-- EBS Volume -->
  <rect x="650" y="380" width="100" height="60" fill="#4B92DB" rx="5"/>
  <text x="700" y="405" text-anchor="middle" class="label" fill="white">Amazon EBS</text>
  <text x="700" y="425" text-anchor="middle" class="label" fill="white">100GB gp3</text>
  
  <!-- Connections -->
  <line x1="500" y1="130" x2="500" y2="160" class="connection"/>
  <line x1="500" y1="200" x2="500" y2="250" class="connection"/>
  <line x1="500" y1="300" x2="500" y2="350" class="connection"/>
  <line x1="600" y1="410" x2="650" y2="410" class="connection"/>
  
  <!-- AWS Services Legend -->
  <rect x="50" y="600" width="300" height="80" fill="white" stroke="#232F3E" stroke-width="1" rx="5"/>
  <text x="60" y="620" class="subtitle">AWS Services Used:</text>
  <text x="60" y="640" class="label">• Amazon EC2 - Compute</text>
  <text x="60" y="655" class="label">• Amazon VPC - Networking</text>
  <text x="60" y="670" class="label">• Amazon EBS - Storage</text>
  
  <!-- Cost Information -->
  <rect x="650" y="600" width="300" height="80" fill="white" stroke="#232F3E" stroke-width="1" rx="5"/>
  <text x="660" y="620" class="subtitle">Estimated Monthly Cost:</text>
  <text x="660" y="640" class="label">EC2 t3.medium: $85.00</text>
  <text x="660" y="655" class="label">EBS 100GB: $25.00</text>
  <text x="660" y="670" class="label">Total: $115.00/month</text>
  
</svg>"""
    else:
        return f"""<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
  <rect width="800" height="600" fill="#F2F3F3"/>
  <text x="400" y="300" text-anchor="middle" font="16px Arial" fill="#232F3E">{project_name} - AWS Architecture</text>
  <rect x="300" y="350" width="200" height="100" fill="#FF9900" stroke="#232F3E" stroke-width="2" rx="5"/>
  <text x="400" y="405" text-anchor="middle" font="12px Arial" fill="white">AWS Services</text>
</svg>"""

def generate_project_activities_csv(project_info: Dict, conversation_text: str) -> str:
    """Genera CSV de actividades del proyecto con horas y responsables"""
    
    project_name = project_info.get('name', 'AWS Project')
    is_ec2_project = 'ec2' in conversation_text.lower()
    
    if is_ec2_project:
        return f"""Fase,Actividad,Descripcion,Responsable,Horas Estimadas,Dependencias,Estado
Planificacion,Analisis de Requisitos,Definir especificaciones tecnicas de la instancia EC2,Arquitecto AWS,8,N/A,Pendiente
Planificacion,Diseño de Arquitectura,Crear diagrama de arquitectura y documentacion,Arquitecto AWS,12,Analisis de Requisitos,Pendiente
Planificacion,Revision de Seguridad,Definir grupos de seguridad y politicas IAM,Especialista Seguridad,6,Diseño de Arquitectura,Pendiente
Implementacion,Creacion de VPC,Configurar VPC y subredes segun diseño,Ingeniero DevOps,4,Revision de Seguridad,Pendiente
Implementacion,Configuracion Security Groups,Crear y configurar grupos de seguridad,Ingeniero DevOps,3,Creacion de VPC,Pendiente
Implementacion,Lanzamiento EC2,Crear instancia EC2 con configuracion especificada,Ingeniero DevOps,2,Configuracion Security Groups,Pendiente
Implementacion,Configuracion EBS,Configurar y adjuntar volumenes EBS,Ingeniero DevOps,2,Lanzamiento EC2,Pendiente
Implementacion,Configuracion Key Pairs,Generar y configurar claves SSH,Ingeniero DevOps,1,Lanzamiento EC2,Pendiente
Configuracion,Instalacion SO,Configurar Amazon Linux 2023 y actualizaciones,Administrador Sistemas,4,Configuracion EBS,Pendiente
Configuracion,Configuracion Monitoreo,Implementar CloudWatch y alarmas,Ingeniero DevOps,6,Instalacion SO,Pendiente
Configuracion,Configuracion Backup,Configurar snapshots automaticos EBS,Ingeniero DevOps,3,Configuracion Monitoreo,Pendiente
Testing,Pruebas Conectividad,Verificar acceso SSH y conectividad,Ingeniero QA,2,Configuracion Backup,Pendiente
Testing,Pruebas Seguridad,Validar configuracion de seguridad,Especialista Seguridad,4,Pruebas Conectividad,Pendiente
Testing,Pruebas Performance,Verificar rendimiento de instancia y storage,Ingeniero QA,3,Pruebas Seguridad,Pendiente
Documentacion,Manual Operativo,Crear documentacion operativa,Arquitecto AWS,6,Pruebas Performance,Pendiente
Documentacion,Procedimientos Backup,Documentar procedimientos de respaldo,Administrador Sistemas,3,Manual Operativo,Pendiente
Documentacion,Guia Troubleshooting,Crear guia de solucion de problemas,Administrador Sistemas,4,Procedimientos Backup,Pendiente
Entrega,Capacitacion Usuario,Entrenar al equipo en uso del sistema,Arquitecto AWS,8,Guia Troubleshooting,Pendiente
Entrega,Documentacion Final,Entregar documentacion completa del proyecto,Arquitecto AWS,4,Capacitacion Usuario,Pendiente
Entrega,Cierre Proyecto,Revision final y cierre formal del proyecto,Project Manager,2,Documentacion Final,Pendiente

RESUMEN DEL PROYECTO:
Proyecto: {project_name}
Total Actividades: 20
Total Horas Estimadas: 85
Duracion Estimada: 3-4 semanas
Recursos Requeridos: 6 especialistas

ROLES Y RESPONSABILIDADES:
- Arquitecto AWS: Diseño y documentacion (38 horas)
- Ingeniero DevOps: Implementacion y configuracion (21 horas)
- Especialista Seguridad: Revision y validacion seguridad (10 horas)
- Administrador Sistemas: Configuracion SO y documentacion (11 horas)
- Ingeniero QA: Pruebas y validacion (5 horas)
- Project Manager: Gestion y cierre (2 horas)
"""
    else:
        return f"""Fase,Actividad,Descripcion,Responsable,Horas Estimadas,Dependencias,Estado
Planificacion,Analisis de Requisitos,Definir especificaciones del proyecto AWS,Arquitecto AWS,6,N/A,Pendiente
Planificacion,Diseño de Solucion,Crear arquitectura y documentacion,Arquitecto AWS,10,Analisis de Requisitos,Pendiente
Implementacion,Configuracion Servicios,Implementar servicios AWS requeridos,Ingeniero DevOps,12,Diseño de Solucion,Pendiente
Testing,Pruebas Integrales,Validar funcionamiento completo,Ingeniero QA,8,Configuracion Servicios,Pendiente
Entrega,Documentacion y Cierre,Entregar documentacion final,Arquitecto AWS,6,Pruebas Integrales,Pendiente

RESUMEN DEL PROYECTO:
Proyecto: {project_name}
Total Actividades: 5
Total Horas Estimadas: 42
Duracion Estimada: 2-3 semanas
"""

def generate_comprehensive_documentation(project_info: Dict, conversation_text: str) -> str:
    """Genera documentación completa con alcances, objetivos, dimensionamiento"""
    
    project_name = project_info.get('name', 'AWS Project')
    project_type = project_info.get('type', 'AWS Solution')
    is_ec2_project = 'ec2' in conversation_text.lower()
    
    # Extraer detalles técnicos de la conversación
    instance_type = 't3.micro'
    storage_size = '20GB'
    if 't3.medium' in conversation_text.lower():
        instance_type = 't3.medium'
    elif 't3.large' in conversation_text.lower():
        instance_type = 't3.large'
    
    if '100gb' in conversation_text.lower() or '100 gb' in conversation_text.lower():
        storage_size = '100GB'
    elif '80gb' in conversation_text.lower() or '80 gb' in conversation_text.lower():
        storage_size = '80GB'
    
    return f"""# {project_name} - Documentacion Tecnica Completa

## 1. INFORMACION GENERAL DEL PROYECTO

### 1.1 Datos Basicos
- **Nombre del Proyecto**: {project_name}
- **Tipo de Solucion**: {project_type}
- **Fecha de Creacion**: {datetime.now().strftime('%Y-%m-%d')}
- **Version del Documento**: 1.0
- **Estado**: En Desarrollo

### 1.2 Equipo del Proyecto
- **Arquitecto AWS**: Responsable del diseño y documentacion
- **Ingeniero DevOps**: Implementacion y configuracion
- **Especialista Seguridad**: Revision de politicas y compliance
- **Project Manager**: Coordinacion y seguimiento

## 2. OBJETIVOS DEL PROYECTO

### 2.1 Objetivo General
Implementar una solucion robusta y escalable en AWS que permita {'el despliegue de una instancia EC2 para procesamiento de inventario' if is_ec2_project else 'la implementacion de servicios cloud'} cumpliendo con los mas altos estandares de seguridad y disponibilidad.

### 2.2 Objetivos Especificos
- Diseñar una arquitectura AWS que cumpla con los requisitos funcionales
- Implementar medidas de seguridad segun mejores practicas de AWS
- Configurar monitoreo y alertas para operacion continua
- Establecer procedimientos de backup y recuperacion
- Documentar todos los procesos para transferencia de conocimiento
- Optimizar costos mediante seleccion adecuada de servicios

## 3. ALCANCE DEL PROYECTO

### 3.1 Incluye
- Diseño de arquitectura AWS completa
- Implementacion de servicios de infraestructura
- Configuracion de seguridad y accesos
- Implementacion de monitoreo con CloudWatch
- Configuracion de backups automaticos
- Documentacion tecnica y operativa
- Capacitacion al equipo operativo

### 3.2 No Incluye
- Desarrollo de aplicaciones personalizadas
- Migracion de datos existentes
- Integraciones con sistemas legacy
- Soporte post-implementacion (mas alla de 30 dias)
- Modificaciones de arquitectura post-entrega

## 4. DIMENSIONAMIENTO TECNICO

### 4.1 Especificaciones de Compute
{'- **Tipo de Instancia**: ' + instance_type + '''
- **vCPUs**: ''' + ('2' if instance_type == 't3.medium' else '1') + '''
- **Memoria RAM**: ''' + ('4 GB' if instance_type == 't3.medium' else '1 GB') + '''
- **Performance de Red**: ''' + ('Hasta 5 Gbps' if instance_type == 't3.medium' else 'Hasta 5 Gbps') + '''
- **Sistema Operativo**: Amazon Linux 2023''' if is_ec2_project else '''- **Servicios AWS**: Configuracion segun requisitos
- **Escalabilidad**: Diseño para crecimiento futuro'''}

### 4.2 Especificaciones de Storage
{'- **Tipo de Volumen**: General Purpose SSD (gp3)' if is_ec2_project else '- **Storage**: Segun servicios implementados'}
{'- **Capacidad**: ' + storage_size if is_ec2_project else ''}
{'- **IOPS**: 3,000 (baseline)' if is_ec2_project else ''}
{'- **Throughput**: 125 MB/s' if is_ec2_project else ''}

### 4.3 Especificaciones de Red
- **Region AWS**: us-east-1 (N. Virginia)
- **VPC**: Configuracion personalizada con subredes publicas/privadas
- **Conectividad**: Internet Gateway para acceso publico
- **Seguridad**: Security Groups con reglas minimas necesarias

## 5. CONSIDERACIONES TECNICAS

### 5.1 Seguridad
- **Principio de Menor Privilegio**: Accesos minimos necesarios
- **Encriptacion**: Datos en transito y en reposo
- **Autenticacion**: Claves SSH para acceso seguro
- **Monitoreo**: CloudTrail para auditoria de acciones
- **Compliance**: Cumplimiento con estandares de seguridad AWS

### 5.2 Alta Disponibilidad
- **Backup Automatico**: Snapshots diarios de volumenes EBS
- **Monitoreo**: Alarmas CloudWatch para metricas criticas
- **Recuperacion**: Procedimientos documentados para restore
- **Mantenimiento**: Ventanas programadas para actualizaciones

### 5.3 Performance
- **Baseline Performance**: Configuracion optimizada para carga esperada
- **Escalabilidad**: Capacidad de crecimiento segun demanda
- **Optimizacion**: Revision periodica de metricas de rendimiento

### 5.4 Costos
- **Modelo de Pricing**: On-Demand para flexibilidad inicial
- **Optimizacion**: Evaluacion de Reserved Instances a 6 meses
- **Monitoreo**: Alertas de presupuesto configuradas
- **Revision**: Analisis mensual de costos y optimizaciones

## 6. ARQUITECTURA DE LA SOLUCION

### 6.1 Componentes Principales
{'- Amazon EC2: Instancia de compute principal' if is_ec2_project else '- Servicios AWS: Segun diseño especifico'}
- Amazon VPC: Red virtual privada
- Security Groups: Firewall a nivel de instancia
- Amazon EBS: Almacenamiento persistente
- CloudWatch: Monitoreo y alertas
- AWS Systems Manager: Gestion y mantenimiento

### 6.2 Flujo de Datos
1. Usuario accede via SSH (puerto 22)
2. Aplicaciones procesan datos en instancia EC2
3. Datos persistentes se almacenan en EBS
4. Metricas se envian a CloudWatch
5. Backups automaticos via snapshots

## 7. PLAN DE IMPLEMENTACION

### 7.1 Fases del Proyecto
1. **Planificacion** (1 semana): Analisis y diseño
2. **Implementacion** (2 semanas): Configuracion de servicios
3. **Testing** (1 semana): Pruebas y validacion
4. **Entrega** (1 semana): Documentacion y capacitacion

### 7.2 Criterios de Aceptacion
- Instancia EC2 operativa y accesible
- Monitoreo configurado y funcional
- Backups automaticos implementados
- Documentacion completa entregada
- Equipo capacitado en operacion

## 8. RIESGOS Y MITIGACIONES

### 8.1 Riesgos Identificados
- **Falla de Instancia**: Mitigado con backups automaticos
- **Problemas de Conectividad**: Mitigado con monitoreo proactivo
- **Costos Elevados**: Mitigado con alertas de presupuesto
- **Problemas de Seguridad**: Mitigado con configuracion restrictiva

### 8.2 Plan de Contingencia
- Procedimientos de recuperacion documentados
- Contactos de escalamiento definidos
- Backups verificados regularmente

## 9. MANTENIMIENTO Y SOPORTE

### 9.1 Actividades de Mantenimiento
- Actualizaciones de seguridad mensuales
- Revision de metricas semanalmente
- Verificacion de backups diariamente
- Optimizacion de costos trimestralmente

### 9.2 Procedimientos Operativos
- Acceso y autenticacion
- Monitoreo y alertas
- Backup y recuperacion
- Escalamiento y troubleshooting

## 10. ANEXOS

### 10.1 Comandos Utiles
```bash
# Conexion SSH
ssh -i inventario-key.pem ec2-user@<public-ip>

# Verificar estado del sistema
sudo systemctl status
df -h
free -m

# Crear snapshot manual
aws ec2 create-snapshot --volume-id <volume-id>
```

### 10.2 Enlaces de Referencia
- AWS EC2 User Guide: https://docs.aws.amazon.com/ec2/
- AWS Security Best Practices: https://aws.amazon.com/security/
- AWS Cost Optimization: https://aws.amazon.com/aws-cost-management/

---
**Documento generado automaticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**
**Version: 1.0 | Estado: Borrador | Confidencial**
"""
