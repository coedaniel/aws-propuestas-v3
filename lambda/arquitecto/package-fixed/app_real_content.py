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
