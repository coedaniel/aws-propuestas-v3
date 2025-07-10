import json
import boto3
import os
from datetime import datetime
from typing import Dict, List, Any
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3 = boto3.client('s3', region_name=os.environ.get('REGION', 'us-east-1'))
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('REGION', 'us-east-1'))

# Get table and bucket names from environment
PROJECTS_TABLE = os.environ.get('PROJECTS_TABLE')
DOCUMENTS_BUCKET = os.environ.get('DOCUMENTS_BUCKET')

projects_table = dynamodb.Table(PROJECTS_TABLE) if PROJECTS_TABLE else None

def lambda_handler(event, context):
    """
    AWS Lambda handler for documents functionality - AWS Propuestas v3
    """
    try:
        # Handle CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return create_response(200, {})
        
        # Parse the request
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event
        
        action = body.get('action', 'generate')
        project_id = body.get('projectId')
        user_id = body.get('userId', 'anonymous')
        
        logger.info(f"📄 DOCUMENTS V3 - Action: {action}, Project: {project_id}")
        
        if action == 'generate':
            return generate_documents(body, context)
        elif action == 'list':
            return list_documents(body, context)
        elif action == 'download':
            return get_download_url(body, context)
        else:
            return create_response(400, {'error': 'Invalid action'})
        
    except Exception as e:
        logger.error(f"Error in documents handler: {str(e)}")
        return create_response(500, {
            'error': 'Internal server error',
            'details': str(e)
        })

def generate_documents(body: Dict, context) -> Dict:
    """Generate all project documents"""
    
    project_id = body.get('projectId')
    user_id = body.get('userId', 'anonymous')
    project_info = body.get('projectInfo', {})
    
    if not project_id:
        return create_response(400, {'error': 'Project ID is required'})
    
    logger.info(f"🎯 Generating documents for project: {project_id}")
    
    try:
        # Generate different document types
        documents = {}
        s3_folder = f"projects/{user_id}/{project_id}/"
        
        # 1. Generate Word document
        word_content = generate_word_document(project_info)
        word_key = f"{s3_folder}propuesta-{project_id}.txt"
        upload_to_s3(word_key, word_content, 'text/plain')
        documents['word'] = word_key
        
        # 2. Generate Activities CSV
        activities_content = generate_activities_csv(project_info)
        activities_key = f"{s3_folder}actividades-{project_id}.csv"
        upload_to_s3(activities_key, activities_content, 'text/csv')
        documents['activities'] = activities_key
        
        # 3. Generate Costs CSV
        costs_content = generate_costs_csv(project_info)
        costs_key = f"{s3_folder}costos-{project_id}.csv"
        upload_to_s3(costs_key, costs_content, 'text/csv')
        documents['costs'] = costs_key
        
        # 4. Generate CloudFormation YAML
        cfn_content = generate_cloudformation_yaml(project_info)
        cfn_key = f"{s3_folder}cloudformation-{project_id}.yaml"
        upload_to_s3(cfn_key, cfn_content, 'text/yaml')
        documents['cloudformation'] = cfn_key
        
        # 5. Generate Calculator Guide
        guide_content = generate_calculator_guide(project_info)
        guide_key = f"{s3_folder}guia-calculadora-{project_id}.txt"
        upload_to_s3(guide_key, guide_content, 'text/plain')
        documents['guide'] = guide_key
        
        # 6. Generate Architecture Diagram (placeholder)
        diagram_content = generate_architecture_diagram(project_info)
        diagram_key = f"{s3_folder}diagrama-{project_id}.svg"
        upload_to_s3(diagram_key, diagram_content, 'image/svg+xml')
        documents['diagram'] = diagram_key
        
        # Update project with document URLs
        if projects_table:
            update_project_documents(project_id, documents)
        
        return create_response(200, {
            'message': 'Documents generated successfully',
            'projectId': project_id,
            'documents': documents,
            's3Folder': s3_folder,
            'downloadUrls': generate_download_urls(documents)
        })
        
    except Exception as e:
        logger.error(f"Error generating documents: {str(e)}")
        return create_response(500, {'error': 'Failed to generate documents'})

def generate_word_document(project_info: Dict) -> str:
    """Generate Word document content (plain text)"""
    
    project_name = project_info.get('name', 'Proyecto AWS')
    project_type = project_info.get('type', 'No especificado')
    
    content = f"""PROPUESTA TECNICA AWS
{project_name}

RESUMEN EJECUTIVO
Este documento presenta la propuesta tecnica para la implementacion de {project_name} en Amazon Web Services (AWS).

OBJETIVO DEL PROYECTO
{project_info.get('objective', 'Implementar solucion en AWS siguiendo mejores practicas.')}

TIPO DE SOLUCION
{project_type}

SERVICIOS AWS RECOMENDADOS
"""
    
    services = project_info.get('services', [])
    if services:
        for service in services:
            content += f"- {service}\n"
    else:
        content += "- Amazon EC2 (Compute)\n- Amazon S3 (Storage)\n- Amazon VPC (Networking)\n"
    
    content += f"""
ARQUITECTURA PROPUESTA
La solucion propuesta sigue los principios del AWS Well-Architected Framework:

1. Excelencia Operacional
2. Seguridad
3. Confiabilidad
4. Eficiencia de Rendimiento
5. Optimizacion de Costos

CONSIDERACIONES DE SEGURIDAD
- Implementacion de IAM roles y policies
- Encriptacion en transito y en reposo
- Monitoreo con CloudWatch y CloudTrail
- Configuracion de VPC con subnets privadas

ALTA DISPONIBILIDAD
- Despliegue multi-AZ
- Auto Scaling configurado
- Load Balancers para distribucion de carga
- Backups automatizados

ESTIMACION DE COSTOS
Ver archivo de costos adjunto para detalles especificos.

CRONOGRAMA DE IMPLEMENTACION
Ver archivo de actividades adjunto para el plan detallado.

PROXIMOS PASOS
1. Aprobacion de la propuesta
2. Configuracion del entorno AWS
3. Implementacion por fases
4. Pruebas y validacion
5. Go-live y soporte

CONTACTO
Para mas informacion sobre esta propuesta, contactar al equipo de arquitectura AWS.

Documento generado automaticamente por AWS Propuestas v3
Fecha: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
"""
    
    return content

def generate_activities_csv(project_info: Dict) -> str:
    """Generate activities CSV content"""
    
    content = "Fase,Actividad,Descripcion,Duracion (dias),Responsable,Dependencias\n"
    
    activities = [
        ("Planificacion", "Revision de requerimientos", "Analisis detallado de necesidades", "2", "Arquitecto AWS", ""),
        ("Planificacion", "Diseno de arquitectura", "Creacion de diagramas y especificaciones", "3", "Arquitecto AWS", "Revision de requerimientos"),
        ("Configuracion", "Setup de cuenta AWS", "Configuracion inicial de servicios", "1", "DevOps Engineer", "Diseno de arquitectura"),
        ("Configuracion", "Implementacion de VPC", "Creacion de red virtual privada", "2", "Network Engineer", "Setup de cuenta AWS"),
        ("Desarrollo", "Despliegue de servicios", "Implementacion de servicios AWS", "5", "DevOps Engineer", "Implementacion de VPC"),
        ("Desarrollo", "Configuracion de seguridad", "Implementacion de IAM y politicas", "2", "Security Engineer", "Despliegue de servicios"),
        ("Testing", "Pruebas funcionales", "Validacion de funcionalidad", "3", "QA Engineer", "Configuracion de seguridad"),
        ("Testing", "Pruebas de rendimiento", "Validacion de performance", "2", "QA Engineer", "Pruebas funcionales"),
        ("Deployment", "Go-live", "Puesta en produccion", "1", "DevOps Engineer", "Pruebas de rendimiento"),
        ("Soporte", "Monitoreo inicial", "Supervision post-deployment", "5", "Support Team", "Go-live")
    ]
    
    for fase, actividad, descripcion, duracion, responsable, dependencias in activities:
        content += f'"{fase}","{actividad}","{descripcion}","{duracion}","{responsable}","{dependencias}"\n'
    
    return content

def generate_costs_csv(project_info: Dict) -> str:
    """Generate costs CSV content"""
    
    content = "Servicio AWS,Tipo de Instancia,Cantidad,Costo Mensual (USD),Costo Anual (USD),Notas\n"
    
    # Basic cost estimates
    costs = [
        ("Amazon EC2", "t3.medium", "2", "67.00", "804.00", "Instancias para aplicacion"),
        ("Amazon RDS", "db.t3.micro", "1", "15.00", "180.00", "Base de datos MySQL"),
        ("Amazon S3", "Standard", "100 GB", "2.30", "27.60", "Almacenamiento de archivos"),
        ("Amazon VPC", "NAT Gateway", "1", "45.00", "540.00", "Conectividad de red"),
        ("Application Load Balancer", "ALB", "1", "22.00", "264.00", "Balanceador de carga"),
        ("Amazon CloudWatch", "Logs y Metricas", "1", "10.00", "120.00", "Monitoreo y logs"),
        ("AWS Support", "Business", "1", "100.00", "1200.00", "Soporte tecnico 24/7")
    ]
    
    total_monthly = 0
    for servicio, tipo, cantidad, mensual, anual, notas in costs:
        content += f'"{servicio}","{tipo}","{cantidad}","{mensual}","{anual}","{notas}"\n'
        total_monthly += float(mensual)
    
    content += f'"TOTAL","","","{total_monthly:.2f}","{total_monthly * 12:.2f}","Estimacion total"\n'
    
    return content

def generate_cloudformation_yaml(project_info: Dict) -> str:
    """Generate CloudFormation YAML content"""
    
    project_name = project_info.get('name', 'proyecto-aws').lower().replace(' ', '-')
    
    content = f"""AWSTemplateFormatVersion: '2010-09-09'
Description: 'CloudFormation template para {project_info.get("name", "Proyecto AWS")}'

Parameters:
  Environment:
    Type: String
    Default: prod
    AllowedValues: [dev, staging, prod]
    Description: Nombre del entorno

  InstanceType:
    Type: String
    Default: t3.medium
    AllowedValues: [t3.micro, t3.small, t3.medium, t3.large]
    Description: Tipo de instancia EC2

Resources:
  # VPC
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub '{project_name}-vpc-${{Environment}}'

  # Internet Gateway
  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: !Sub '{project_name}-igw-${{Environment}}'

  # Attach Internet Gateway to VPC
  InternetGatewayAttachment:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      InternetGatewayId: !Ref InternetGateway
      VpcId: !Ref VPC

  # Public Subnet
  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [0, !GetAZs '']
      CidrBlock: 10.0.1.0/24
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub '{project_name}-public-subnet-${{Environment}}'

  # Private Subnet
  PrivateSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [1, !GetAZs '']
      CidrBlock: 10.0.2.0/24
      Tags:
        - Key: Name
          Value: !Sub '{project_name}-private-subnet-${{Environment}}'

  # Security Group
  WebServerSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub '{project_name}-web-sg-${{Environment}}'
      GroupDescription: Security group para servidores web
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 10.0.0.0/16

  # EC2 Instance
  WebServerInstance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-0c02fb55956c7d316  # Amazon Linux 2
      InstanceType: !Ref InstanceType
      SubnetId: !Ref PublicSubnet
      SecurityGroupIds:
        - !Ref WebServerSecurityGroup
      Tags:
        - Key: Name
          Value: !Sub '{project_name}-web-server-${{Environment}}'

  # S3 Bucket
  S3Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '{project_name}-storage-${{Environment}}-${{AWS::AccountId}}'
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true

Outputs:
  VPCId:
    Description: ID de la VPC
    Value: !Ref VPC
    Export:
      Name: !Sub '${{AWS::StackName}}-VPC-ID'

  WebServerInstanceId:
    Description: ID de la instancia del servidor web
    Value: !Ref WebServerInstance

  S3BucketName:
    Description: Nombre del bucket S3
    Value: !Ref S3Bucket
"""
    
    return content

def generate_calculator_guide(project_info: Dict) -> str:
    """Generate AWS Calculator guide content"""
    
    content = f"""GUIA PARA AWS PRICING CALCULATOR
{project_info.get('name', 'Proyecto AWS')}

Esta guia te ayudara a estimar los costos usando la Calculadora Oficial de AWS.

PASO 1: Acceder a la Calculadora
1. Ve a https://calculator.aws/
2. Haz clic en "Create estimate"

PASO 2: Configurar Region
1. Selecciona la region: US East (N. Virginia) - us-east-1
2. Esta es la region recomendada para el proyecto

PASO 3: Agregar Servicios

AMAZON EC2:
- Tipo de instancia: t3.medium
- Cantidad: 2 instancias
- Sistema operativo: Linux
- Tenancy: Shared
- Pricing model: On-Demand
- Utilizacion: 100% (24/7)

AMAZON RDS:
- Engine: MySQL
- Tipo de instancia: db.t3.micro
- Deployment: Single-AZ
- Storage: 20 GB General Purpose SSD
- Backup: 7 dias de retencion

AMAZON S3:
- Storage class: S3 Standard
- Cantidad: 100 GB
- Requests: 10,000 PUT/COPY/POST/LIST por mes
- Data transfer: 10 GB salida por mes

AMAZON VPC:
- NAT Gateway: 1 instancia
- Data processing: 100 GB por mes

APPLICATION LOAD BALANCER:
- Numero de balanceadores: 1
- Processed bytes: 100 GB por mes

AMAZON CLOUDWATCH:
- Logs ingested: 10 GB por mes
- Logs stored: 5 GB por mes
- Custom metrics: 100 metricas

AWS SUPPORT:
- Plan: Business Support
- Costo base mensual

PASO 4: Revisar Estimacion
1. Revisa todos los servicios agregados
2. Verifica las configuraciones
3. Guarda la estimacion con un nombre descriptivo

PASO 5: Optimizaciones Recomendadas
1. Considera Reserved Instances para EC2 (ahorro del 30-60%)
2. Evalua Savings Plans para uso consistente
3. Configura S3 Intelligent Tiering para optimizar costos
4. Implementa CloudWatch para monitorear uso real

NOTAS IMPORTANTES:
- Los precios pueden variar por region
- Considera costos de transferencia de datos
- Incluye costos de soporte tecnico
- Revisa regularmente para optimizar

CONTACTO:
Para dudas sobre la estimacion, contacta al equipo de arquitectura AWS.

Guia generada automaticamente por AWS Propuestas v3
Fecha: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
"""
    
    return content

def generate_architecture_diagram(project_info: Dict) -> str:
    """Generate architecture diagram (SVG placeholder)"""
    
    project_name = project_info.get('name', 'Proyecto AWS')
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .title {{ font-family: Arial, sans-serif; font-size: 24px; font-weight: bold; }}
      .service {{ font-family: Arial, sans-serif; font-size: 14px; }}
      .aws-orange {{ fill: #FF9900; }}
      .aws-blue {{ fill: #232F3E; }}
      .connection {{ stroke: #666; stroke-width: 2; fill: none; }}
    </style>
  </defs>
  
  <!-- Background -->
  <rect width="800" height="600" fill="#f8f9fa"/>
  
  <!-- Title -->
  <text x="400" y="40" text-anchor="middle" class="title aws-blue">
    Arquitectura AWS - {project_name}
  </text>
  
  <!-- Internet -->
  <circle cx="400" cy="100" r="30" class="aws-orange"/>
  <text x="400" y="105" text-anchor="middle" class="service" fill="white">Internet</text>
  
  <!-- Load Balancer -->
  <rect x="350" y="180" width="100" height="60" rx="10" class="aws-orange"/>
  <text x="400" y="205" text-anchor="middle" class="service" fill="white">Application</text>
  <text x="400" y="220" text-anchor="middle" class="service" fill="white">Load Balancer</text>
  
  <!-- EC2 Instances -->
  <rect x="200" y="300" width="80" height="60" rx="10" class="aws-blue"/>
  <text x="240" y="325" text-anchor="middle" class="service" fill="white">EC2</text>
  <text x="240" y="340" text-anchor="middle" class="service" fill="white">Instance 1</text>
  
  <rect x="520" y="300" width="80" height="60" rx="10" class="aws-blue"/>
  <text x="560" y="325" text-anchor="middle" class="service" fill="white">EC2</text>
  <text x="560" y="340" text-anchor="middle" class="service" fill="white">Instance 2</text>
  
  <!-- RDS Database -->
  <rect x="350" y="450" width="100" height="60" rx="10" class="aws-orange"/>
  <text x="400" y="475" text-anchor="middle" class="service" fill="white">Amazon RDS</text>
  <text x="400" y="490" text-anchor="middle" class="service" fill="white">MySQL</text>
  
  <!-- S3 Bucket -->
  <rect x="100" y="450" width="80" height="60" rx="10" class="aws-blue"/>
  <text x="140" y="475" text-anchor="middle" class="service" fill="white">Amazon S3</text>
  <text x="140" y="490" text-anchor="middle" class="service" fill="white">Storage</text>
  
  <!-- CloudWatch -->
  <rect x="620" y="450" width="80" height="60" rx="10" class="aws-blue"/>
  <text x="660" y="475" text-anchor="middle" class="service" fill="white">CloudWatch</text>
  <text x="660" y="490" text-anchor="middle" class="service" fill="white">Monitoring</text>
  
  <!-- Connections -->
  <line x1="400" y1="130" x2="400" y2="180" class="connection"/>
  <line x1="400" y1="240" x2="240" y2="300" class="connection"/>
  <line x1="400" y1="240" x2="560" y2="300" class="connection"/>
  <line x1="240" y1="360" x2="350" y2="450" class="connection"/>
  <line x1="560" y1="360" x2="450" y2="450" class="connection"/>
  <line x1="240" y1="360" x2="140" y2="450" class="connection"/>
  <line x1="560" y1="360" x2="660" y2="450" class="connection"/>
  
  <!-- Legend -->
  <text x="50" y="550" class="service aws-blue">Diagrama generado automaticamente por AWS Propuestas v3</text>
  <text x="50" y="570" class="service aws-blue">Fecha: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</text>
</svg>'''
    
    return svg_content

def upload_to_s3(key: str, content: str, content_type: str):
    """Upload content to S3"""
    try:
        s3.put_object(
            Bucket=DOCUMENTS_BUCKET,
            Key=key,
            Body=content.encode('utf-8'),
            ContentType=content_type,
            ServerSideEncryption='AES256'
        )
        logger.info(f"📤 Uploaded to S3: {key}")
    except Exception as e:
        logger.error(f"Failed to upload {key}: {str(e)}")
        raise

def update_project_documents(project_id: str, documents: Dict):
    """Update project with document URLs"""
    try:
        projects_table.update_item(
            Key={'projectId': project_id},
            UpdateExpression='SET documents = :docs, updatedAt = :updated',
            ExpressionAttributeValues={
                ':docs': documents,
                ':updated': datetime.utcnow().isoformat()
            }
        )
        logger.info(f"📝 Updated project documents: {project_id}")
    except Exception as e:
        logger.warning(f"Failed to update project documents: {str(e)}")

def generate_download_urls(documents: Dict) -> Dict:
    """Generate presigned URLs for document download"""
    urls = {}
    try:
        for doc_type, s3_key in documents.items():
            url = s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': DOCUMENTS_BUCKET, 'Key': s3_key},
                ExpiresIn=3600  # 1 hour
            )
            urls[doc_type] = url
    except Exception as e:
        logger.warning(f"Failed to generate download URLs: {str(e)}")
    
    return urls

def list_documents(body: Dict, context) -> Dict:
    """List documents for a project"""
    return create_response(200, {
        'message': 'Document listing feature coming soon'
    })

def get_download_url(body: Dict, context) -> Dict:
    """Get download URL for a document"""
    return create_response(200, {
        'message': 'Download URL feature coming soon'
    })

def create_response(status_code: int, body: Dict) -> Dict:
    """Create HTTP response with CORS headers"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
        },
        'body': json.dumps(body, ensure_ascii=False)
    }
