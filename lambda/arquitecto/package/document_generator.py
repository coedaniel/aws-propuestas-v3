"""
Document Generator - Amazon Q Developer CLI Style
Professional document generation using MCP services
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class DocumentGenerator:
    """Generates professional AWS documents using MCP services"""
    
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        
    def generate_complete_package(self, project_name: str, project_type: str, 
                                messages: List[Dict], ai_response: str, 
                                project_id: str, user_id: str) -> Dict:
        """Generate complete document package like Amazon Q Developer CLI"""
        
        try:
            logger.info(f"📄 Generating complete document package for: {project_name}")
            
            # Create project folder structure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_folder = f"projects/{user_id}/{project_id}_{timestamp}"
            
            documents = []
            
            # 1. Executive Proposal Document
            exec_doc = self._generate_executive_proposal(project_name, project_type, messages, ai_response)
            if exec_doc:
                documents.append({
                    'name': f"{project_name}_Propuesta_Ejecutiva.txt",
                    'type': 'executive_proposal',
                    'content': exec_doc,
                    'description': 'Documento ejecutivo para stakeholders',
                    'path': f"{project_folder}/{project_name}_Propuesta_Ejecutiva.txt"
                })
            
            # 2. Technical Architecture Document
            tech_doc = self._generate_technical_architecture(project_name, project_type, messages)
            if tech_doc:
                documents.append({
                    'name': f"{project_name}_Arquitectura_Tecnica.txt",
                    'type': 'technical_architecture',
                    'content': tech_doc,
                    'description': 'Documento técnico detallado',
                    'path': f"{project_folder}/{project_name}_Arquitectura_Tecnica.txt"
                })
            
            # 3. CloudFormation Template
            cfn_template = self._generate_cloudformation_template(project_name, project_type, messages)
            if cfn_template:
                documents.append({
                    'name': f"{project_name}_CloudFormation.yaml",
                    'type': 'cloudformation',
                    'content': cfn_template,
                    'description': 'Template de infraestructura como código',
                    'path': f"{project_folder}/{project_name}_CloudFormation.yaml"
                })
            
            # 4. Cost Analysis
            cost_analysis = self._generate_cost_analysis(project_name, project_type, messages)
            if cost_analysis:
                documents.append({
                    'name': f"{project_name}_Analisis_Costos.csv",
                    'type': 'cost_analysis',
                    'content': cost_analysis,
                    'description': 'Análisis detallado de costos AWS',
                    'path': f"{project_folder}/{project_name}_Analisis_Costos.csv"
                })
            
            # 5. Implementation Plan
            impl_plan = self._generate_implementation_plan(project_name, project_type, messages)
            if impl_plan:
                documents.append({
                    'name': f"{project_name}_Plan_Implementacion.csv",
                    'type': 'implementation_plan',
                    'content': impl_plan,
                    'description': 'Plan detallado de implementación',
                    'path': f"{project_folder}/{project_name}_Plan_Implementacion.csv"
                })
            
            # 6. AWS Calculator Guide
            calc_guide = self._generate_calculator_guide(project_name, project_type, messages)
            if calc_guide:
                documents.append({
                    'name': f"{project_name}_Guia_Calculadora_AWS.txt",
                    'type': 'calculator_guide',
                    'content': calc_guide,
                    'description': 'Guía para usar la calculadora oficial de AWS',
                    'path': f"{project_folder}/{project_name}_Guia_Calculadora_AWS.txt"
                })
            
            # Simulate S3 upload
            upload_success = self._simulate_s3_upload(documents)
            
            return {
                'success': True,
                'documents': documents,
                'project_folder': project_folder,
                'upload_success': upload_success,
                'total_documents': len(documents),
                'bucket': self.bucket_name
            }
            
        except Exception as e:
            logger.error(f"Error generating document package: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'documents': []
            }
    
    def _generate_executive_proposal(self, project_name: str, project_type: str, 
                                   messages: List[Dict], ai_response: str) -> str:
        """Generate executive proposal document"""
        
        # Extract key information from conversation
        objective = self._extract_objective(messages, ai_response)
        services = self._extract_services(messages)
        
        doc_content = f"""PROPUESTA EJECUTIVA - {project_name.upper()}

RESUMEN EJECUTIVO
================

Proyecto: {project_name}
Tipo: {project_type.replace('_', ' ').title()}
Fecha: {datetime.now().strftime('%d/%m/%Y')}
Arquitecto: AWS Solutions Architect Senior

OBJETIVO DEL PROYECTO
====================

{objective}

SOLUCION PROPUESTA
==================

La solucion propuesta utiliza servicios AWS nativos para garantizar:
- Alta disponibilidad y escalabilidad automatica
- Seguridad empresarial con cifrado end-to-end
- Optimizacion de costos con modelos pay-per-use
- Facilidad de mantenimiento y operacion

SERVICIOS AWS INCLUIDOS
=======================

{self._format_services_list(services)}

BENEFICIOS ESPERADOS
===================

- Reduccion de costos operativos hasta 30%
- Mejora en disponibilidad del servicio (99.9% SLA)
- Escalabilidad automatica segun demanda
- Seguridad de nivel empresarial
- Backup y recuperacion automatizada
- Monitoreo proactivo 24/7

ARQUITECTURA WELL-ARCHITECTED
============================

La solucion sigue los 6 pilares del AWS Well-Architected Framework:

1. Excelencia Operacional: Automatizacion y monitoreo continuo
2. Seguridad: Cifrado, IAM y controles de acceso
3. Confiabilidad: Multi-AZ y recuperacion automatica
4. Eficiencia de Rendimiento: Servicios optimizados
5. Optimizacion de Costos: Modelos de precios flexibles
6. Sostenibilidad: Servicios administrados eficientes

PROXIMOS PASOS
==============

1. Aprobacion de la propuesta por stakeholders
2. Definicion de cronograma de implementacion
3. Asignacion de recursos del equipo tecnico
4. Inicio de la fase de implementacion

CONTACTO
========

Para consultas adicionales sobre esta propuesta:
- Arquitecto AWS Solutions Senior
- Email: arquitecto@empresa.com

---
Documento generado por AWS Propuestas v3
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
        
        return doc_content
    
    def _generate_technical_architecture(self, project_name: str, project_type: str, 
                                       messages: List[Dict]) -> str:
        """Generate technical architecture document"""
        
        services = self._extract_services(messages)
        
        doc_content = f"""ARQUITECTURA TECNICA - {project_name.upper()}

VISION GENERAL DE LA ARQUITECTURA
=================================

Proyecto: {project_name}
Tipo: {project_type.replace('_', ' ').title()}
Fecha: {datetime.now().strftime('%d/%m/%Y')}

COMPONENTES PRINCIPALES
======================

{self._format_technical_components(services)}

PATRONES DE ARQUITECTURA
========================

La solucion implementa los siguientes patrones:
- Microservicios con contenedores
- Event-driven architecture
- Serverless computing
- Infrastructure as Code
- CI/CD automatizado

CONFIGURACION DE RED
====================

VPC Configuration:
- CIDR Block: 10.0.0.0/16
- Public Subnets: 10.0.1.0/24, 10.0.2.0/24
- Private Subnets: 10.0.10.0/24, 10.0.20.0/24
- Internet Gateway para acceso publico
- NAT Gateway para salida privada

SEGURIDAD
=========

Controles de Seguridad Implementados:
- AWS IAM para control de acceso
- Security Groups como firewall virtual
- NACLs para control de red adicional
- AWS KMS para cifrado de datos
- CloudTrail para auditoria
- GuardDuty para deteccion de amenazas

MONITOREO Y ALERTAS
==================

- CloudWatch para metricas y logs
- CloudWatch Alarms para alertas criticas
- AWS X-Ray para trazabilidad distribuida
- AWS Config para compliance
- SNS para notificaciones

BACKUP Y RECUPERACION
====================

- Snapshots automaticos de EBS
- Cross-region replication para S3
- RDS automated backups
- Point-in-time recovery
- Disaster recovery plan documentado

ESCALABILIDAD
=============

- Auto Scaling Groups para EC2
- Application Load Balancer
- CloudFront para distribucion global
- ElastiCache para performance
- Read replicas para bases de datos

---
Documento tecnico generado por AWS Propuestas v3
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
        
        return doc_content
    
    def _extract_objective(self, messages: List[Dict], ai_response: str) -> str:
        """Extract project objective from conversation"""
        
        # Look for objective-related keywords in messages
        objective_keywords = ['objetivo', 'meta', 'proposito', 'necesidad', 'problema']
        
        for msg in messages:
            content = msg.get('content', '').lower()
            for keyword in objective_keywords:
                if keyword in content:
                    # Extract sentence containing the keyword
                    sentences = content.split('.')
                    for sentence in sentences:
                        if keyword in sentence:
                            return sentence.strip().capitalize()
        
        # Default objective
        return "Implementar una solucion AWS robusta, escalable y segura que optimice los recursos tecnologicos y reduzca costos operativos."
    
    def _extract_services(self, messages: List[Dict]) -> List[str]:
        """Extract AWS services mentioned in conversation"""
        
        aws_services = [
            'ec2', 's3', 'rds', 'vpc', 'lambda', 'api gateway', 'cloudfront',
            'dynamodb', 'iam', 'cloudwatch', 'sns', 'sqs', 'efs', 'elb',
            'route53', 'cloudformation', 'elastic beanstalk', 'ecs', 'eks'
        ]
        
        mentioned_services = []
        conversation_text = ""
        
        for msg in messages:
            conversation_text += msg.get('content', '').lower()
        
        for service in aws_services:
            if service in conversation_text:
                mentioned_services.append(service.upper())
        
        # Default services if none mentioned
        if not mentioned_services:
            mentioned_services = ['EC2', 'S3', 'VPC', 'IAM', 'CloudWatch']
        
        return mentioned_services
    
    def _format_services_list(self, services: List[str]) -> str:
        """Format services list for executive document"""
        
        service_descriptions = {
            'EC2': 'Amazon EC2 - Instancias de computo escalables',
            'S3': 'Amazon S3 - Almacenamiento de objetos seguro',
            'RDS': 'Amazon RDS - Base de datos relacional administrada',
            'VPC': 'Amazon VPC - Red privada virtual',
            'LAMBDA': 'AWS Lambda - Computo serverless',
            'API GATEWAY': 'Amazon API Gateway - Gestion de APIs',
            'CLOUDFRONT': 'Amazon CloudFront - Red de distribucion de contenido',
            'DYNAMODB': 'Amazon DynamoDB - Base de datos NoSQL',
            'IAM': 'AWS IAM - Gestion de identidades y accesos',
            'CLOUDWATCH': 'Amazon CloudWatch - Monitoreo y observabilidad'
        }
        
        formatted_list = ""
        for i, service in enumerate(services, 1):
            description = service_descriptions.get(service, f'{service} - Servicio AWS especializado')
            formatted_list += f"{i}. {description}\n"
        
        return formatted_list
    
    def _format_technical_components(self, services: List[str]) -> str:
        """Format technical components for architecture document"""
        
        components = ""
        for service in services:
            components += f"- {service}: Configuracion optimizada para produccion\n"
        
        return components
    
    def _generate_cloudformation_template(self, project_name: str, project_type: str, 
                                        messages: List[Dict]) -> str:
        """Generate CloudFormation template"""
        
        services = self._extract_services(messages)
        project_name_clean = project_name.replace(' ', '-').lower()
        
        template = f"""AWSTemplateFormatVersion: '2010-09-09'
Description: 'CloudFormation template for {project_name}'

Parameters:
  ProjectName:
    Type: String
    Default: {project_name_clean}
    Description: Name of the project
    
  Environment:
    Type: String
    Default: prod
    AllowedValues: [dev, test, prod]
    Description: Environment type

Resources:
  # VPC Configuration
  ProjectVPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub '${{ProjectName}}-vpc'
        - Key: Environment
          Value: !Ref Environment

  # Internet Gateway
  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: !Sub '${{ProjectName}}-igw'

  AttachGateway:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref ProjectVPC
      InternetGatewayId: !Ref InternetGateway

  # Public Subnet
  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref ProjectVPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub '${{ProjectName}}-public-subnet'

  # Private Subnet
  PrivateSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref ProjectVPC
      CidrBlock: 10.0.10.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      Tags:
        - Key: Name
          Value: !Sub '${{ProjectName}}-private-subnet'"""

        # Add S3 bucket if mentioned
        if 'S3' in services:
            template += """

  # S3 Bucket
  ProjectS3Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '${{ProjectName}}-bucket-${{AWS::AccountId}}'
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
        RestrictPublicBuckets: true"""

        # Add EC2 instance if mentioned
        if 'EC2' in services:
            template += """

  # Security Group for EC2
  EC2SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for EC2 instances
      VpcId: !Ref ProjectVPC
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
  ProjectEC2Instance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-0c02fb55956c7d316  # Amazon Linux 2
      InstanceType: t3.micro
      SubnetId: !Ref PublicSubnet
      SecurityGroupIds:
        - !Ref EC2SecurityGroup
      Tags:
        - Key: Name
          Value: !Sub '${{ProjectName}}-instance'"""

        # Add RDS if mentioned
        if 'RDS' in services:
            template += """

  # RDS Subnet Group
  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: Subnet group for RDS
      SubnetIds:
        - !Ref PrivateSubnet
        - !Ref PublicSubnet
      Tags:
        - Key: Name
          Value: !Sub '${{ProjectName}}-db-subnet-group'

  # RDS Instance
  ProjectRDSInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: !Sub '${{ProjectName}}-database'
      DBInstanceClass: db.t3.micro
      Engine: mysql
      MasterUsername: admin
      MasterUserPassword: !Sub '${{ProjectName}}Password123!'
      AllocatedStorage: 20
      DBSubnetGroupName: !Ref DBSubnetGroup
      VPCSecurityGroups:
        - !Ref RDSSecurityGroup

  # RDS Security Group
  RDSSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for RDS
      VpcId: !Ref ProjectVPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 3306
          ToPort: 3306
          SourceSecurityGroupId: !Ref EC2SecurityGroup"""

        template += """

Outputs:
  VPCId:
    Description: VPC ID
    Value: !Ref ProjectVPC
    Export:
      Name: !Sub '${{AWS::StackName}}-VPC-ID'
      
  PublicSubnetId:
    Description: Public Subnet ID
    Value: !Ref PublicSubnet
    Export:
      Name: !Sub '${{AWS::StackName}}-PublicSubnet-ID'"""

        if 'S3' in services:
            template += """
            
  S3BucketName:
    Description: S3 Bucket Name
    Value: !Ref ProjectS3Bucket
    Export:
      Name: !Sub '${{AWS::StackName}}-S3Bucket-Name'"""

        return template

    def _generate_cost_analysis(self, project_name: str, project_type: str, 
                              messages: List[Dict]) -> str:
        """Generate cost analysis CSV"""
        
        services = self._extract_services(messages)
        
        # Base cost structure
        costs = [
            "Servicio,Tipo,Cantidad,Costo Mensual USD,Costo Anual USD,Descripcion"
        ]
        
        # Add costs based on services mentioned
        if 'EC2' in services:
            costs.append("Amazon EC2,t3.micro,1,8.50,102.00,Instancia de computo basica")
            
        if 'S3' in services:
            costs.append("Amazon S3,Standard,100 GB,2.30,27.60,Almacenamiento de objetos")
            
        if 'RDS' in services:
            costs.append("Amazon RDS,db.t3.micro,1,15.00,180.00,Base de datos MySQL")
            
        if 'VPC' in services:
            costs.append("Amazon VPC,NAT Gateway,1,45.00,540.00,Gateway para conectividad")
            
        if 'LAMBDA' in services:
            costs.append("AWS Lambda,Requests,1M,0.20,2.40,Ejecuciones serverless")
            
        # Always include monitoring and data transfer
        costs.extend([
            "AWS CloudWatch,Logs,10 GB,0.50,6.00,Monitoreo y logs",
            "Data Transfer,Outbound,100 GB,9.00,108.00,Transferencia de datos",
            "AWS Support,Basic,1,0.00,0.00,Soporte basico incluido"
        ])
        
        # Calculate total
        total_monthly = sum(float(line.split(',')[3]) for line in costs[1:] if line.split(',')[3].replace('.', '').isdigit())
        total_annual = total_monthly * 12
        
        costs.append(f"TOTAL,,,{total_monthly:.2f},{total_annual:.2f},Costo total estimado")
        
        return "\n".join(costs)

    def _generate_implementation_plan(self, project_name: str, project_type: str, 
                                    messages: List[Dict]) -> str:
        """Generate implementation plan CSV"""
        
        if project_type == "servicio_rapido":
            activities = [
                "Fase,Actividad,Descripcion,Duracion,Responsable,Dependencias,Estado",
                "1,Configuracion inicial,Setup basico del servicio AWS,4 horas,Ingeniero AWS,Ninguna,Pendiente",
                "2,Implementacion,Despliegue del servicio configurado,2 horas,DevOps Engineer,Configuracion,Pendiente",
                "3,Pruebas,Validacion de funcionalidad,1 hora,QA Engineer,Implementacion,Pendiente",
                "4,Documentacion,Entrega de documentacion tecnica,1 hora,Arquitecto AWS,Pruebas,Pendiente",
                "5,Go-live,Puesta en produccion,30 min,Todo el equipo,Documentacion,Pendiente"
            ]
        else:
            activities = [
                "Fase,Actividad,Descripcion,Duracion,Responsable,Dependencias,Estado",
                "1,Planificacion,Revision de requerimientos y arquitectura,2 dias,Arquitecto AWS,Ninguna,Pendiente",
                "2,Configuracion de red,Creacion de VPC y subredes,1 dia,Ingeniero de Red,Planificacion,Pendiente",
                "3,Seguridad,Configuracion de IAM y grupos de seguridad,1 dia,Especialista Seguridad,Red,Pendiente",
                "4,Servicios principales,Implementacion de servicios AWS core,3 dias,DevOps Engineer,Seguridad,Pendiente",
                "5,Base de datos,Configuracion de RDS y backups,1 dia,DBA,Servicios,Pendiente",
                "6,Monitoreo,Setup de CloudWatch y alertas,1 dia,SRE,Base de datos,Pendiente",
                "7,Pruebas integracion,Validacion de funcionalidad completa,2 dias,QA Engineer,Monitoreo,Pendiente",
                "8,Documentacion,Entrega de documentacion completa,1 dia,Technical Writer,Pruebas,Pendiente",
                "9,Go-live,Puesta en produccion y soporte inicial,1 dia,Todo el equipo,Documentacion,Pendiente"
            ]
        
        return "\n".join(activities)

    def _generate_calculator_guide(self, project_name: str, project_type: str, 
                                 messages: List[Dict]) -> str:
        """Generate AWS Calculator usage guide"""
        
        services = self._extract_services(messages)
        
        guide = f"""GUIA PARA CALCULADORA OFICIAL DE AWS
=====================================

Proyecto: {project_name}
URL: https://calculator.aws/
Fecha: {datetime.now().strftime('%d/%m/%Y')}

PASOS PARA CALCULAR COSTOS
=========================

1. ACCEDER A LA CALCULADORA
   - Visitar https://calculator.aws/
   - Hacer clic en "Create estimate"

2. SELECCIONAR REGION
   - Elegir la region AWS apropiada
   - Recomendado: us-east-1 (Virginia del Norte) para menor costo

3. AGREGAR SERVICIOS ESPECIFICOS

"""
        
        # Add service-specific guidance
        if 'EC2' in services:
            guide += """   Amazon EC2:
   - Tipo de instancia: t3.micro (capa gratuita elegible)
   - Sistema operativo: Linux
   - Horas de uso: 730 (24/7) o segun necesidad
   - Almacenamiento: 20 GB EBS gp3
   - Transferencia de datos: Estimar segun uso

"""
        
        if 'S3' in services:
            guide += """   Amazon S3:
   - Tipo de almacenamiento: Standard
   - Cantidad: Estimar segun necesidades
   - Requests PUT/COPY/POST/LIST: Estimar
   - Requests GET/SELECT: Estimar
   - Transferencia de datos: Considerar CDN

"""
        
        if 'RDS' in services:
            guide += """   Amazon RDS:
   - Motor: MySQL o PostgreSQL
   - Tipo de instancia: db.t3.micro
   - Almacenamiento: 20 GB SSD
   - Multi-AZ: Considerar para produccion
   - Backups: 7 dias retencion

"""
        
        guide += f"""4. CONFIGURACIONES ADICIONALES
   - VPC: Sin costo adicional
   - CloudWatch: Incluir metricas basicas
   - Data Transfer: Estimar trafico saliente
   - Support: Basic (gratuito) o Business segun necesidad

5. REVISAR Y OPTIMIZAR
   - Verificar todos los servicios agregados
   - Ajustar cantidades segun uso real esperado
   - Considerar Reserved Instances para ahorros
   - Evaluar Savings Plans para cargas estables

6. GUARDAR Y COMPARTIR
   - Hacer clic en "Save and share"
   - Copiar el enlace para referencia futura
   - Exportar a CSV para analisis detallado

OPTIMIZACION DE COSTOS
=====================

1. Right-sizing: Ajustar tamanos de instancias
2. Scheduling: Apagar recursos en horarios no productivos
3. Reserved Instances: Para cargas predecibles
4. Spot Instances: Para cargas tolerantes a interrupciones
5. S3 Lifecycle: Mover datos a clases de almacenamiento mas economicas
6. CloudWatch: Monitorear uso y optimizar continuamente

CONSIDERACIONES IMPORTANTES
===========================

- Los precios varian por region AWS
- Incluir costos de transferencia de datos
- Considerar crecimiento futuro (20-30% margen)
- Revisar estimaciones mensualmente
- Usar AWS Cost Explorer para seguimiento real

CONTACTO PARA DUDAS
==================

Para consultas sobre costos y optimizacion:
- AWS Solutions Architect
- Email: costos@empresa.com

---
Guia generada para: {project_name}
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
        
        return guide
