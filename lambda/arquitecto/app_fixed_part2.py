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
