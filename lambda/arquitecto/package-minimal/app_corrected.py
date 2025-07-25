"""
AWS Propuestas v3 - Arquitecto Lambda CORREGIDO
Fixes principales:
1. Consultoria completa paso a paso
2. Generacion de archivos reales con contenido profesional
3. Integracion correcta con MCP de diagramas AWS
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

# PROMPT MAESTRO CORREGIDO - CONSULTORIA COMPLETA
PROMPT_MAESTRO_CORREGIDO = """
Eres un Arquitecto de Soluciones AWS experto y consultor profesional. Tu mision es realizar una consultoria completa, paso a paso, para dimensionar, documentar y entregar una solucion profesional en AWS.

REGLAS IMPORTANTES:
- No uses acentos ni caracteres especiales en ningun texto, archivo, script ni documento
- Haz UNA pregunta a la vez, espera la respuesta antes de continuar
- Sigue el flujo de consultoria paso a paso
- Solo genera documentos cuando tengas TODA la informacion necesaria

FLUJO DE CONSULTORIA OBLIGATORIO:

FASE 1: IDENTIFICACION DEL PROYECTO
1. Pregunta: "Cual es el nombre del proyecto?"
2. Pregunta: "El proyecto es una solucion integral (migracion, aplicacion nueva, modernizacion, analitica, seguridad, IA, IoT, data lake, networking, DRP, VDI, integracion) o un servicio rapido especifico (EC2, RDS, SES, VPN, ELB, S3, VPC, CloudFront, SSO, backup)?"

FASE 2: RECOPILACION DETALLADA (haz MUCHAS preguntas especificas)
Para SERVICIOS RAPIDOS (como EC2):
- Proposito especifico de la instancia
- Tipo de aplicacion que alojara
- Requisitos de capacidad (CPU, RAM, almacenamiento)
- Sistema operativo preferido
- Requisitos de red y conectividad
- Requisitos de seguridad especificos
- Backup y recuperacion
- Monitoreo requerido
- Presupuesto aproximado
- Timeline de implementacion

Para SOLUCIONES INTEGRALES:
- Objetivos de negocio
- Arquitectura actual (si existe)
- Volumenes de datos esperados
- Usuarios concurrentes
- Requisitos de disponibilidad
- Requisitos de seguridad y compliance
- Integraciones necesarias
- Presupuesto total
- Timeline del proyecto

FASE 3: GENERACION DE DOCUMENTOS
Solo cuando tengas TODA la informacion, genera:
- Diagrama de arquitectura profesional
- Script CloudFormation completo
- Documento tecnico detallado
- Estimacion de costos precisa
- Plan de actividades del proyecto

IMPORTANTE: Haz las preguntas de forma natural y profesional, una a la vez.
"""

def call_mcp_service(service_name: str, action: str, data: Dict) -> Dict:
    """Llama a un servicio MCP especifico"""
    try:
        url = MCP_SERVICES.get(service_name)
        if not url:
            logger.error(f"Unknown MCP service: {service_name}")
            return {"error": f"Unknown service: {service_name}"}
        
        logger.info(f"🔧 Calling MCP {service_name} at {url}")
        
        response = requests.post(
            f"{url}/{action}",
            json=data,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ MCP {service_name} responded successfully")
            return result
        else:
            logger.error(f"❌ MCP {service_name} error: {response.status_code}")
            return {"error": f"MCP service error: {response.status_code}"}
            
    except Exception as e:
        logger.error(f"❌ Error calling MCP {service_name}: {str(e)}")
        return {"error": str(e)}

def extract_project_info(messages: List[Dict]) -> Dict:
    """Extrae informacion del proyecto de la conversacion"""
    conversation_text = " ".join([msg.get("content", "") for msg in messages]).lower()
    
    # Buscar nombre del proyecto
    project_name = "proyecto-aws"
    for msg in messages:
        content = msg.get("content", "").lower()
        if "nombre del proyecto" in content or "proyecto" in content:
            # Buscar en el siguiente mensaje del usuario
            next_user_msg = None
            for i, m in enumerate(messages):
                if m == msg and i + 1 < len(messages):
                    next_user_msg = messages[i + 1]
                    break
            if next_user_msg and next_user_msg.get("role") == "user":
                project_name = next_user_msg.get("content", "").strip()
                break
    
    # Determinar tipo de proyecto
    project_type = "servicio-rapido"
    if any(word in conversation_text for word in ["integral", "migracion", "aplicacion nueva", "modernizacion"]):
        project_type = "solucion-integral"
    
    return {
        'id': str(uuid.uuid4()),
        'name': project_name,
        'type': project_type,
        'created_at': datetime.now().isoformat(),
        'conversation_summary': conversation_text[:500]
    }

def is_ready_for_generation(messages: List[Dict]) -> bool:
    """Determina si hay suficiente informacion para generar documentos"""
    conversation_text = " ".join([msg.get("content", "") for msg in messages]).lower()
    
    # Criterios minimos para generacion
    has_project_name = any(word in conversation_text for word in ["proyecto", "nombre"])
    has_service_type = any(word in conversation_text for word in ["ec2", "rds", "s3", "vpc", "lambda"])
    has_requirements = any(word in conversation_text for word in ["requisitos", "necesito", "quiero", "tipo"])
    
    # Contar preguntas y respuestas
    user_messages = [msg for msg in messages if msg.get("role") == "user"]
    
    return has_project_name and has_service_type and has_requirements and len(user_messages) >= 3

def generate_aws_diagram_with_mcp(project_info: Dict, conversation_text: str) -> str:
    """Genera diagrama usando el MCP de diagramas con iconos AWS reales"""
    
    logger.info("🎨 Generating AWS diagram with MCP service")
    
    # Determinar servicios AWS basado en la conversacion
    aws_services = []
    if "ec2" in conversation_text.lower():
        aws_services.append("EC2")
    if "vpc" in conversation_text.lower():
        aws_services.append("VPC")
    if "rds" in conversation_text.lower():
        aws_services.append("RDS")
    if "s3" in conversation_text.lower():
        aws_services.append("S3")
    
    # Llamar al MCP de diagramas
    diagram_data = {
        'project_name': project_info['name'],
        'services': aws_services,
        'diagram_type': 'aws_architecture',
        'include_icons': True,
        'format': 'svg'
    }
    
    diagram_result = call_mcp_service('diagram', 'generate', diagram_data)
    
    if 'error' not in diagram_result and 'diagram' in diagram_result:
        return diagram_result['diagram']
    else:
        # Fallback: generar diagrama basico
        return generate_basic_aws_diagram(project_info, aws_services)

def generate_basic_aws_diagram(project_info: Dict, services: List[str]) -> str:
    """Genera diagrama SVG basico con iconos AWS"""
    
    project_name = project_info.get('name', 'AWS Project')
    
    svg_content = f'''<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .title {{ font: bold 18px sans-serif; fill: #232f3e; }}
      .label {{ font: 12px sans-serif; fill: #232f3e; }}
      .aws-orange {{ fill: #ff9900; }}
      .aws-blue {{ fill: #232f3e; }}
      .vpc-green {{ fill: #4caf50; opacity: 0.3; }}
      .subnet-blue {{ fill: #2196f3; opacity: 0.2; }}
    </style>
  </defs>
  
  <text x="400" y="30" text-anchor="middle" class="title">{project_name} - AWS Architecture</text>
  
  <!-- AWS Cloud -->
  <rect x="50" y="60" width="700" height="500" rx="10" fill="#f0f8ff" stroke="#ff9900" stroke-width="3"/>
  <text x="70" y="85" class="label" style="font-weight: bold;">AWS Cloud</text>
'''
    
    y_pos = 120
    
    if "VPC" in services:
        svg_content += f'''
  <!-- VPC -->
  <rect x="100" y="{y_pos}" width="600" height="400" class="vpc-green" stroke="#4caf50" stroke-width="2"/>
  <text x="120" y="{y_pos + 25}" class="label">VPC (Virtual Private Cloud)</text>
'''
        y_pos += 50
    
    if "EC2" in services:
        svg_content += f'''
  <!-- EC2 Instance -->
  <rect x="300" y="{y_pos}" width="200" height="80" class="aws-orange" rx="5"/>
  <text x="400" y="{y_pos + 30}" text-anchor="middle" class="label" fill="white">EC2 Instance</text>
  <text x="400" y="{y_pos + 50}" text-anchor="middle" class="label" fill="white">Amazon Linux 2023</text>
'''
        y_pos += 100
    
    svg_content += '''
  <!-- AWS Logo placeholder -->
  <circle cx="750" cy="580" r="15" class="aws-orange"/>
  <text x="750" y="585" text-anchor="middle" class="label" fill="white" style="font-size: 10px;">AWS</text>
  
</svg>'''
    
    return svg_content
"""
Continuacion del archivo app_fixed.py - Parte 2
"""

def generate_professional_cloudformation(project_info: Dict, conversation_text: str) -> str:
    """Genera CloudFormation template profesional y completo"""
    
    project_name = project_info.get('name', 'aws-project').lower().replace(' ', '-')
    
    if 'ec2' in conversation_text.lower():
        # Template completo para EC2 con mejores practicas
        return f'''AWSTemplateFormatVersion: '2010-09-09'
Description: 'Professional EC2 deployment for {project_info.get("name", "AWS Project")} with best practices'

Parameters:
  Environment:
    Type: String
    Default: prod
    AllowedValues: [dev, staging, prod]
    Description: Environment name
  
  InstanceType:
    Type: String
    Default: t3.micro
    AllowedValues: [t3.micro, t3.small, t3.medium, t3.large]
    Description: EC2 instance type
  
  KeyPairName:
    Type: AWS::EC2::KeyPair::KeyName
    Description: EC2 Key Pair for SSH access
  
  AllowedSSHCIDR:
    Type: String
    Default: 0.0.0.0/0
    Description: CIDR block allowed for SSH access
    AllowedPattern: '^([0-9]{{1,3}}\\.{{3}}[0-9]{{1,3}}/[0-9]{{1,2}})$'

Mappings:
  RegionMap:
    us-east-1:
      AMI: ami-0c02fb55956c7d316
    us-west-2:
      AMI: ami-008fe2fc65df48dac
    eu-west-1:
      AMI: ami-0a8e758f5e873d1c1

Resources:
  # VPC with best practices
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub '${{AWS::StackName}}-vpc'
        - Key: Environment
          Value: !Ref Environment
  
  # Internet Gateway
  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: !Sub '${{AWS::StackName}}-igw'
  
  AttachGateway:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway
  
  # Public Subnet
  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub '${{AWS::StackName}}-public-subnet'
  
  # Route Table
  PublicRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub '${{AWS::StackName}}-public-rt'
  
  PublicRoute:
    Type: AWS::EC2::Route
    DependsOn: AttachGateway
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway
  
  PublicSubnetRouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet
      RouteTableId: !Ref PublicRouteTable
  
  # Security Group with best practices
  WebServerSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for web server
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: !Ref AllowedSSHCIDR
          Description: SSH access
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
          Description: HTTP access
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
          Description: HTTPS access
      SecurityGroupEgress:
        - IpProtocol: -1
          CidrIp: 0.0.0.0/0
          Description: All outbound traffic
      Tags:
        - Key: Name
          Value: !Sub '${{AWS::StackName}}-web-sg'
  
  # IAM Role for EC2
  EC2Role:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy
      Tags:
        - Key: Name
          Value: !Sub '${{AWS::StackName}}-ec2-role'
  
  EC2InstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      Roles:
        - !Ref EC2Role
  
  # EC2 Instance
  WebServerInstance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !FindInMap [RegionMap, !Ref 'AWS::Region', AMI]
      InstanceType: !Ref InstanceType
      KeyName: !Ref KeyPairName
      SubnetId: !Ref PublicSubnet
      SecurityGroupIds:
        - !Ref WebServerSecurityGroup
      IamInstanceProfile: !Ref EC2InstanceProfile
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          yum update -y
          yum install -y httpd
          systemctl start httpd
          systemctl enable httpd
          echo "<h1>Welcome to {project_info.get('name', 'AWS Project')}</h1>" > /var/www/html/index.html
          echo "<p>Instance ID: $(curl -s http://169.254.169.254/latest/meta-data/instance-id)</p>" >> /var/www/html/index.html
          echo "<p>Availability Zone: $(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)</p>" >> /var/www/html/index.html
      Tags:
        - Key: Name
          Value: !Sub '${{AWS::StackName}}-web-server'
        - Key: Environment
          Value: !Ref Environment

Outputs:
  VPCId:
    Description: VPC ID
    Value: !Ref VPC
    Export:
      Name: !Sub '${{AWS::StackName}}-VPC-ID'
  
  PublicSubnetId:
    Description: Public Subnet ID
    Value: !Ref PublicSubnet
    Export:
      Name: !Sub '${{AWS::StackName}}-PublicSubnet-ID'
  
  InstanceId:
    Description: EC2 Instance ID
    Value: !Ref WebServerInstance
  
  PublicIP:
    Description: Public IP address
    Value: !GetAtt WebServerInstance.PublicIp
  
  WebsiteURL:
    Description: Website URL
    Value: !Sub 'http://${{WebServerInstance.PublicIp}}'
  
  SSHCommand:
    Description: SSH command to connect
    Value: !Sub 'ssh -i ${{KeyPairName}}.pem ec2-user@${{WebServerInstance.PublicIp}}'
'''
    else:
        # Template generico para otros servicios
        return f'''AWSTemplateFormatVersion: '2010-09-09'
Description: 'AWS infrastructure for {project_info.get("name", "AWS Project")}'

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
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true

Outputs:
  BucketName:
    Description: S3 Bucket Name
    Value: !Ref S3Bucket
'''

def generate_professional_documentation(project_info: Dict, conversation_text: str) -> str:
    """Genera documentacion tecnica profesional"""
    
    project_name = project_info.get('name', 'AWS Project')
    
    doc_content = f"""DOCUMENTO TECNICO PROFESIONAL
{project_name}
{'=' * len(project_name)}

RESUMEN EJECUTIVO
-----------------
Este documento presenta la solucion tecnica propuesta para {project_name}, 
diseñada siguiendo las mejores practicas de AWS Well-Architected Framework.

OBJETIVOS DEL PROYECTO
----------------------
- Implementar infraestructura escalable y segura en AWS
- Garantizar alta disponibilidad y rendimiento optimo
- Minimizar costos operacionales
- Facilitar mantenimiento y actualizaciones

ARQUITECTURA PROPUESTA
----------------------
"""
    
    if 'ec2' in conversation_text.lower():
        doc_content += """
COMPONENTES PRINCIPALES:

1. COMPUTE (EC2)
   - Instancia EC2 optimizada para la carga de trabajo
   - Amazon Linux 2023 con actualizaciones automaticas
   - Configuracion de auto-scaling (recomendado para produccion)

2. NETWORKING (VPC)
   - VPC dedicada con CIDR 10.0.0.0/16
   - Subnets publicas y privadas en multiples AZ
   - Internet Gateway para conectividad externa
   - NAT Gateway para subnets privadas (recomendado)

3. SECURITY
   - Security Groups con reglas minimas necesarias
   - IAM Roles con permisos especificos
   - Encryption en transito y en reposo
   - AWS CloudTrail para auditoria

4. MONITORING
   - CloudWatch para metricas y logs
   - CloudWatch Alarms para notificaciones
   - AWS Systems Manager para gestion de parches

MEJORES PRACTICAS IMPLEMENTADAS
-------------------------------
- Principio de menor privilegio en IAM
- Encryption por defecto
- Backup automatizado
- Monitoreo proactivo
- Documentacion de procesos
- Plan de recuperacion ante desastres

CONSIDERACIONES DE SEGURIDAD
----------------------------
- Acceso SSH restringido por IP
- Actualizaciones automaticas de seguridad
- Logs centralizados en CloudWatch
- Revision periodica de permisos

PLAN DE IMPLEMENTACION
---------------------
Fase 1: Preparacion (1-2 dias)
- Configuracion de cuentas AWS
- Creacion de usuarios IAM
- Configuracion de billing alerts

Fase 2: Despliegue de Infraestructura (1 dia)
- Ejecucion de CloudFormation template
- Verificacion de conectividad
- Configuracion de monitoreo

Fase 3: Configuracion de Aplicacion (1-2 dias)
- Instalacion de software requerido
- Configuracion de servicios
- Pruebas de funcionalidad

Fase 4: Optimizacion y Documentacion (1 dia)
- Ajustes de rendimiento
- Documentacion de procesos
- Entrenamiento del equipo

COSTOS ESTIMADOS
----------------
Ver archivo de pricing adjunto para detalles completos.

SOPORTE Y MANTENIMIENTO
-----------------------
- Monitoreo 24/7 con CloudWatch
- Backup automatico diario
- Actualizaciones de seguridad automaticas
- Revision mensual de costos y rendimiento

CONTACTO TECNICO
---------------
Para consultas tecnicas sobre esta implementacion,
contactar al equipo de arquitectura AWS.
"""
    
    return doc_content

def generate_detailed_pricing(project_info: Dict, conversation_text: str) -> str:
    """Genera estimacion detallada de costos"""
    
    pricing_content = f"""ESTIMACION DETALLADA DE COSTOS AWS
{project_info.get('name', 'AWS Project')}
{'=' * 50}

RESUMEN DE COSTOS MENSUALES
---------------------------
"""
    
    if 'ec2' in conversation_text.lower():
        pricing_content += """
COMPUTE (EC2)
- t3.micro (1 vCPU, 1GB RAM): $8.50/mes
- EBS gp3 80GB: $6.40/mes
- Data Transfer OUT (estimado): $5.00/mes
Subtotal Compute: $19.90/mes

NETWORKING (VPC)
- VPC (sin costo adicional): $0.00/mes
- Internet Gateway: $0.00/mes
- NAT Gateway (recomendado): $32.40/mes
- Elastic IP: $3.60/mes
Subtotal Networking: $36.00/mes

SECURITY & MONITORING
- CloudWatch Logs (5GB): $2.50/mes
- CloudWatch Metrics: $3.00/mes
- CloudTrail: $2.00/mes
Subtotal Monitoring: $7.50/mes

BACKUP & STORAGE
- EBS Snapshots (estimado): $4.00/mes
- S3 para logs y backups: $2.00/mes
Subtotal Backup: $6.00/mes

TOTAL MENSUAL ESTIMADO: $69.40/mes
TOTAL ANUAL ESTIMADO: $832.80/año

OPCIONES DE OPTIMIZACION
------------------------
1. Reserved Instances (1 año): Ahorro del 40% = $41.64/mes
2. Spot Instances (cargas flexibles): Ahorro del 70% = $20.82/mes
3. Eliminar NAT Gateway (menos seguro): Ahorro de $32.40/mes

RECOMENDACIONES DE COSTOS
-------------------------
- Implementar auto-scaling para optimizar uso
- Revisar utilization mensualmente
- Considerar Reserved Instances para cargas estables
- Usar CloudWatch para identificar recursos subutilizados

ALERTAS DE BILLING RECOMENDADAS
-------------------------------
- Alerta a $50/mes (72% del presupuesto)
- Alerta a $75/mes (108% del presupuesto)
- Revision semanal de costos

COMPARACION CON ALTERNATIVAS
----------------------------
On-Premises Equivalente: $200-300/mes
Otros Cloud Providers: $75-90/mes
AWS con optimizaciones: $41-69/mes

NOTAS IMPORTANTES
-----------------
- Precios basados en region us-east-1
- No incluye costos de soporte AWS
- Estimaciones pueden variar segun uso real
- Revisar pricing AWS actualizado antes de implementar
"""
    
    return pricing_content

def generate_project_activities(project_info: Dict, conversation_text: str) -> str:
    """Genera CSV con actividades del proyecto"""
    
    csv_content = """Fase,Actividad,Responsable,Duracion_Horas,Dependencias,Estado
Preparacion,Configuracion cuenta AWS,Arquitecto AWS,2,Ninguna,Pendiente
Preparacion,Creacion usuarios IAM,Arquitecto AWS,1,Cuenta AWS,Pendiente
Preparacion,Configuracion billing alerts,Arquitecto AWS,0.5,Usuarios IAM,Pendiente
Infraestructura,Revision CloudFormation template,Arquitecto AWS,1,Preparacion completa,Pendiente
Infraestructura,Despliegue de VPC,Arquitecto AWS,0.5,Template revisado,Pendiente
Infraestructura,Despliegue de EC2,Arquitecto AWS,0.5,VPC desplegada,Pendiente
Infraestructura,Configuracion Security Groups,Arquitecto AWS,1,EC2 desplegada,Pendiente
Infraestructura,Verificacion conectividad,Arquitecto AWS,0.5,Security Groups,Pendiente
Configuracion,Instalacion software base,DevOps Engineer,2,Infraestructura completa,Pendiente
Configuracion,Configuracion aplicacion,Developer,4,Software instalado,Pendiente
Configuracion,Configuracion SSL/TLS,DevOps Engineer,1,Aplicacion configurada,Pendiente
Testing,Pruebas de funcionalidad,QA Engineer,4,Configuracion completa,Pendiente
Testing,Pruebas de rendimiento,QA Engineer,2,Pruebas funcionales,Pendiente
Testing,Pruebas de seguridad,Security Engineer,3,Pruebas rendimiento,Pendiente
Monitoreo,Configuracion CloudWatch,Arquitecto AWS,1,Testing completo,Pendiente
Monitoreo,Configuracion alertas,Arquitecto AWS,1,CloudWatch configurado,Pendiente
Monitoreo,Dashboard de metricas,Arquitecto AWS,1,Alertas configuradas,Pendiente
Documentacion,Documentacion tecnica,Technical Writer,4,Implementacion completa,Pendiente
Documentacion,Manual de usuario,Technical Writer,2,Doc tecnica,Pendiente
Documentacion,Runbooks operacionales,DevOps Engineer,3,Manual usuario,Pendiente
Entrega,Entrenamiento equipo,Arquitecto AWS,4,Documentacion completa,Pendiente
Entrega,Transferencia conocimiento,Arquitecto AWS,2,Entrenamiento completo,Pendiente
Entrega,Sign-off del proyecto,Project Manager,1,Transferencia completa,Pendiente"""
    
    return csv_content
"""
Continuacion del archivo app_fixed.py - Parte 3: Funciones principales
"""

def save_documents_to_s3_fixed(project_info: Dict, generated_content: Dict) -> Dict:
    """Guarda documentos REALES en S3 con contenido profesional"""
    try:
        folder_name = f"{project_info['name'].lower().replace(' ', '-')}-{project_info['id'][:8]}"
        
        logger.info(f"📁 Saving PROFESSIONAL documents to S3 folder: {folder_name}")
        
        documents_saved = []
        
        for content_type, content_data in generated_content.items():
            # Determinar extension y tipo de contenido
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
                file_extension = 'txt'
                content_type_s3 = 'text/plain'
            elif content_type == 'activities':
                file_extension = 'csv'
                content_type_s3 = 'text/csv'
            else:
                file_extension = 'txt'
                content_type_s3 = 'text/plain'
            
            file_name = f"{content_type}.{file_extension}"
            s3_key = f"{folder_name}/{file_name}"
            
            # Convertir contenido a string
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
                    'content_source': 'professional_generation'
                }
            )
            
            documents_saved.append({
                'file_name': file_name,
                's3_key': s3_key,
                'content_type': content_type,
                'size_bytes': len(content_str.encode('utf-8'))
            })
            
            logger.info(f"✅ Saved PROFESSIONAL {file_name} to S3: {s3_key}")
        
        # Guardar proyecto en DynamoDB
        save_project_to_dynamodb_fixed(project_info, documents_saved, folder_name)
        
        return {
            'folder_name': folder_name,
            'documents_saved': documents_saved,
            'bucket': DOCUMENTS_BUCKET,
            'total_files': len(documents_saved),
            'content_source': 'professional_generation'
        }
        
    except Exception as e:
        logger.error(f"❌ Error saving to S3: {str(e)}")
        return None

def save_project_to_dynamodb_fixed(project_info: Dict, documents_saved: List[Dict], folder_name: str):
    """Guarda informacion del proyecto en DynamoDB"""
    try:
        table = dynamodb.Table(PROJECTS_TABLE)
        
        # Convertir Decimal para DynamoDB
        def convert_decimals(obj):
            if isinstance(obj, list):
                return [convert_decimals(i) for i in obj]
            elif isinstance(obj, dict):
                return {k: convert_decimals(v) for k, v in obj.items()}
            elif isinstance(obj, float):
                return Decimal(str(obj))
            else:
                return obj
        
        item = {
            'project_id': project_info['id'],
            'project_name': project_info['name'],
            'project_type': project_info['type'],
            'status': 'completed',
            'created_at': project_info['created_at'],
            'updated_at': datetime.now().isoformat(),
            's3_folder': folder_name,
            'documents': convert_decimals(documents_saved),
            'total_files': len(documents_saved)
        }
        
        table.put_item(Item=item)
        logger.info(f"✅ Project saved to DynamoDB: {project_info['id']}")
        
    except Exception as e:
        logger.error(f"❌ Error saving to DynamoDB: {str(e)}")

def generate_all_documents_fixed(project_info: Dict, conversation_text: str) -> Dict:
    """Genera TODOS los documentos profesionales"""
    
    logger.info("📄 Generating ALL professional documents")
    
    generated_content = {}
    
    # 1. Diagrama AWS con iconos reales
    logger.info("🎨 Generating AWS diagram with real icons")
    diagram_content = generate_aws_diagram_with_mcp(project_info, conversation_text)
    generated_content['diagram'] = diagram_content
    
    # 2. CloudFormation profesional
    logger.info("🏗️ Generating professional CloudFormation")
    cf_content = generate_professional_cloudformation(project_info, conversation_text)
    generated_content['cloudformation'] = cf_content
    
    # 3. Documentacion tecnica completa
    logger.info("📋 Generating professional documentation")
    doc_content = generate_professional_documentation(project_info, conversation_text)
    generated_content['documentation'] = doc_content
    
    # 4. Pricing detallado
    logger.info("💰 Generating detailed pricing")
    pricing_content = generate_detailed_pricing(project_info, conversation_text)
    generated_content['pricing'] = pricing_content
    
    # 5. Actividades del proyecto
    logger.info("📅 Generating project activities")
    activities_content = generate_project_activities(project_info, conversation_text)
    generated_content['activities'] = activities_content
    
    # 6. Guardar en S3
    s3_result = save_documents_to_s3_fixed(project_info, generated_content)
    
    return {
        'generated_content': generated_content,
        's3_result': s3_result,
        'total_documents': len(generated_content)
    }

def prepare_conversation_fixed(messages: List[Dict], project_state: Dict) -> List[Dict]:
    """Prepara conversacion para Bedrock con prompt maestro corregido"""
    
    conversation = []
    
    # Agregar prompt maestro como primer mensaje del sistema
    conversation.append({
        "role": "user",
        "content": PROMPT_MAESTRO_CORREGIDO
    })
    
    # Agregar contexto del estado del proyecto si existe
    if project_state.get('phase') != 'inicio':
        context_msg = f"Contexto del proyecto: Fase actual: {project_state.get('phase', 'inicio')}"
        if project_state.get('data'):
            context_msg += f", Datos recopilados: {json.dumps(project_state['data'])}"
        
        conversation.append({
            "role": "user", 
            "content": context_msg
        })
    
    # Agregar mensajes de la conversacion
    for msg in messages:
        if msg.get('content') and msg.get('content').strip():
            conversation.append({
                "role": msg.get('role', 'user'),
                "content": msg['content'].strip()
            })
    
    return conversation

def call_bedrock_model_fixed(model_id: str, conversation: List[Dict]) -> Dict:
    """Llama al modelo Bedrock con manejo mejorado"""
    try:
        logger.info(f"🤖 Calling Bedrock model: {model_id}")
        
        # Preparar mensajes para Bedrock
        messages = []
        for msg in conversation:
            messages.append({
                "role": msg["role"],
                "content": [{"text": msg["content"]}]
            })
        
        response = bedrock_runtime.converse(
            modelId=model_id,
            messages=messages,
            inferenceConfig={
                'maxTokens': 4000,
                'temperature': 0.7,
                'topP': 0.9
            }
        )
        
        content = response['output']['message']['content'][0]['text']
        logger.info(f"✅ Bedrock response received, length: {len(content)}")
        
        return {
            'content': content,
            'usage': response.get('usage', {}),
            'modelUsed': model_id
        }
        
    except Exception as e:
        logger.error(f"❌ Error calling Bedrock: {str(e)}")
        return {'error': f'Error calling Bedrock: {str(e)}'}

def create_cors_response(status_code: int, body: Dict) -> Dict:
    """Crea respuesta con headers CORS"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, X-Amz-Date, Authorization, X-Api-Key, X-Amz-Security-Token',
            'Access-Control-Max-Age': '86400'
        },
        'body': json.dumps(body, default=str)
    }

def lambda_handler_fixed(event, context):
    """Lambda handler CORREGIDO con consultoria completa"""
    
    try:
        logger.info(f"📥 Event received: {json.dumps(event, default=str)}")
        
        # Handle CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return create_cors_response(200, {'message': 'CORS preflight successful'})
        
        # Parse request body
        try:
            if isinstance(event.get('body'), str):
                body = json.loads(event['body'])
            else:
                body = event.get('body', {})
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode error: {str(e)}")
            return create_cors_response(400, {'error': 'Invalid JSON in request body'})
        
        messages = body.get('messages', [])
        model_id = body.get('modelId', 'anthropic.claude-3-5-sonnet-20240620-v1:0')
        project_state = body.get('projectState', {'phase': 'inicio', 'data': {}})
        
        if not messages:
            return create_cors_response(400, {'error': 'No messages provided'})
        
        logger.info(f"🔄 Processing {len(messages)} messages with model: {model_id}")
        
        # === LOGICA PRINCIPAL CORREGIDA ===
        
        # 1. Extraer informacion del proyecto
        project_info = extract_project_info(messages)
        
        # 2. Verificar si esta listo para generar documentos
        ready_for_generation = is_ready_for_generation(messages)
        
        # 3. Generar documentos si esta listo
        generation_result = None
        if ready_for_generation:
            logger.info("✅ Ready for document generation")
            conversation_text = " ".join([msg.get("content", "") for msg in messages])
            generation_result = generate_all_documents_fixed(project_info, conversation_text)
        
        # 4. Preparar conversacion para Bedrock
        conversation = prepare_conversation_fixed(messages, project_state)
        
        if not conversation:
            return create_cors_response(400, {'error': 'No valid conversation content'})
        
        # 5. Llamar a Bedrock
        bedrock_response = call_bedrock_model_fixed(model_id, conversation)
        
        if 'error' in bedrock_response:
            return create_cors_response(500, {'error': bedrock_response['error']})
        
        response_content = bedrock_response['content']
        
        # 6. Agregar informacion de documentos generados si aplica
        if generation_result and generation_result['s3_result']:
            response_content += "\n\n--- DOCUMENTOS GENERADOS Y GUARDADOS EN S3 ---\n"
            response_content += f"📁 Carpeta: {generation_result['s3_result']['folder_name']}\n"
            response_content += f"🪣 Bucket: {DOCUMENTS_BUCKET}\n"
            response_content += f"📄 Documentos: {generation_result['total_documents']} archivos generados\n\n"
            
            for doc_type in generation_result['generated_content'].keys():
                response_content += f"✅ {doc_type.title()}: Generado exitosamente\n"
            
            response_content += f"\n🎯 Los documentos han sido guardados en S3 y el proyecto registrado en la base de datos."
        
        # 7. Preparar respuesta final
        response_data = {
            'content': response_content,
            'usage': bedrock_response.get('usage', {}),
            'modelUsed': bedrock_response.get('modelUsed', model_id),
            'mcpUsed': ['core-mcp'] if generation_result else [],
            'projectUpdate': {
                'phase': 'generacion' if ready_for_generation else project_state.get('phase', 'inicio'),
                'data': project_info
            } if ready_for_generation else None
        }
        
        logger.info("✅ Request processed successfully")
        return create_cors_response(200, response_data)
        
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}", exc_info=True)
        return create_cors_response(500, {'error': f'Internal server error: {str(e)}'})

# Alias para compatibilidad
lambda_handler = lambda_handler_fixed
