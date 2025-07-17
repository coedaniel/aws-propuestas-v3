import json
import boto3
import os
from datetime import datetime
import uuid

# Clientes AWS
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
s3_client = boto3.client('s3', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Variables de entorno
DOCUMENTS_BUCKET = os.environ.get('DOCUMENTS_BUCKET', 'aws-propuestas-v3-documents-prod-035385358261')
PROJECTS_TABLE = os.environ.get('PROJECTS_TABLE', 'aws-propuestas-v3-projects-prod')

# Prompt maestro FUNCIONAL
PROMPT_MAESTRO = """
Actua como arquitecto de soluciones AWS y consultor experto. Tu objetivo es dimensionar, documentar y entregar una solucion profesional en AWS.

FLUJO CONVERSACIONAL:

1. Si es la primera interaccion, pregunta: "Cual es el nombre de tu proyecto?"

2. Despues pregunta el tipo de solucion:
   - Solucion integral (migracion, aplicacion nueva, modernizacion, analitica, IA, etc.)
   - Servicio especifico (EC2, RDS, S3, VPN, etc.)

3. Haz 3-5 preguntas relevantes sobre:
   - Objetivo principal
   - Requisitos tecnicos
   - Usuarios estimados
   - Presupuesto aproximado
   - Integraciones necesarias

4. Despues de 5-7 intercambios, di exactamente: "GENERO LOS SIGUIENTES DOCUMENTOS:"

IMPORTANTE:
- Se conversacional y profesional
- Haz preguntas especificas
- Despues de suficiente informacion, SIEMPRE di "GENERO LOS SIGUIENTES DOCUMENTOS:"
- No uses acentos en los textos
"""

def generate_real_documents(project_name, conversation_context=""):
    """Genera documentos reales profesionales basados en la conversacion"""
    
    # Extraer informacion de la conversacion
    project_type = "Solucion AWS"
    estimated_cost = 500.0
    
    if "migracion" in conversation_context.lower():
        project_type = "Migracion a AWS"
        estimated_cost = 2500.0
    elif "aplicacion" in conversation_context.lower():
        project_type = "Desarrollo de Aplicacion"
        estimated_cost = 1500.0
    elif "analitica" in conversation_context.lower():
        project_type = "Solucion de Analitica"
        estimated_cost = 3000.0
    elif "ia" in conversation_context.lower() or "machine learning" in conversation_context.lower():
        project_type = "Solucion de IA/ML"
        estimated_cost = 4000.0

    # CloudFormation Template funcional
    cfn_template = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Description": f"Infrastructure for {project_name} - {project_type}",
        "Parameters": {
            "Environment": {
                "Type": "String",
                "Default": "prod",
                "AllowedValues": ["dev", "staging", "prod"],
                "Description": "Environment name"
            },
            "ProjectName": {
                "Type": "String",
                "Default": project_name.replace(' ', '-').lower(),
                "Description": "Project name for resource naming"
            }
        },
        "Resources": {
            "S3Bucket": {
                "Type": "AWS::S3::Bucket",
                "Properties": {
                    "BucketName": {"Fn::Sub": "${ProjectName}-${Environment}-${AWS::AccountId}"},
                    "VersioningConfiguration": {"Status": "Enabled"},
                    "BucketEncryption": {
                        "ServerSideEncryptionConfiguration": [{
                            "ServerSideEncryptionByDefault": {
                                "SSEAlgorithm": "AES256"
                            }
                        }]
                    },
                    "PublicAccessBlockConfiguration": {
                        "BlockPublicAcls": True,
                        "BlockPublicPolicy": True,
                        "IgnorePublicAcls": True,
                        "RestrictPublicBuckets": True
                    }
                }
            },
            "LambdaExecutionRole": {
                "Type": "AWS::IAM::Role",
                "Properties": {
                    "RoleName": {"Fn::Sub": "${ProjectName}-lambda-role-${Environment}"},
                    "AssumeRolePolicyDocument": {
                        "Version": "2012-10-17",
                        "Statement": [{
                            "Effect": "Allow",
                            "Principal": {"Service": "lambda.amazonaws.com"},
                            "Action": "sts:AssumeRole"
                        }]
                    },
                    "ManagedPolicyArns": [
                        "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
                    ],
                    "Policies": [{
                        "PolicyName": "S3Access",
                        "PolicyDocument": {
                            "Version": "2012-10-17",
                            "Statement": [{
                                "Effect": "Allow",
                                "Action": [
                                    "s3:GetObject",
                                    "s3:PutObject",
                                    "s3:DeleteObject"
                                ],
                                "Resource": {"Fn::Sub": "${S3Bucket}/*"}
                            }]
                        }
                    }]
                }
            },
            "LambdaFunction": {
                "Type": "AWS::Lambda::Function",
                "Properties": {
                    "FunctionName": {"Fn::Sub": "${ProjectName}-function-${Environment}"},
                    "Runtime": "python3.9",
                    "Handler": "index.handler",
                    "Role": {"Fn::GetAtt": ["LambdaExecutionRole", "Arn"]},
                    "Environment": {
                        "Variables": {
                            "BUCKET_NAME": {"Ref": "S3Bucket"},
                            "ENVIRONMENT": {"Ref": "Environment"}
                        }
                    },
                    "Code": {
                        "ZipFile": """import json
import boto3
import os

def handler(event, context):
    bucket_name = os.environ['BUCKET_NAME']
    environment = os.environ['ENVIRONMENT']
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'Hello from {environment} environment!',
            'bucket': bucket_name,
            'timestamp': context.aws_request_id
        })
    }"""
                    }
                }
            },
            "DynamoDBTable": {
                "Type": "AWS::DynamoDB::Table",
                "Properties": {
                    "TableName": {"Fn::Sub": "${ProjectName}-table-${Environment}"},
                    "BillingMode": "PAY_PER_REQUEST",
                    "AttributeDefinitions": [
                        {"AttributeName": "id", "AttributeType": "S"},
                        {"AttributeName": "timestamp", "AttributeType": "S"}
                    ],
                    "KeySchema": [
                        {"AttributeName": "id", "KeyType": "HASH"},
                        {"AttributeName": "timestamp", "KeyType": "RANGE"}
                    ],
                    "StreamSpecification": {
                        "StreamViewType": "NEW_AND_OLD_IMAGES"
                    },
                    "PointInTimeRecoverySpecification": {
                        "PointInTimeRecoveryEnabled": True
                    }
                }
            },
            "APIGateway": {
                "Type": "AWS::ApiGateway::RestApi",
                "Properties": {
                    "Name": {"Fn::Sub": "${ProjectName}-api-${Environment}"},
                    "Description": f"API Gateway for {project_name}",
                    "EndpointConfiguration": {
                        "Types": ["REGIONAL"]
                    }
                }
            }
        },
        "Outputs": {
            "S3BucketName": {
                "Description": "Name of the S3 bucket",
                "Value": {"Ref": "S3Bucket"},
                "Export": {"Name": {"Fn::Sub": "${AWS::StackName}-S3Bucket"}}
            },
            "LambdaFunctionArn": {
                "Description": "ARN of the Lambda function",
                "Value": {"Fn::GetAtt": ["LambdaFunction", "Arn"]},
                "Export": {"Name": {"Fn::Sub": "${AWS::StackName}-LambdaArn"}}
            },
            "DynamoDBTableName": {
                "Description": "Name of the DynamoDB table",
                "Value": {"Ref": "DynamoDBTable"},
                "Export": {"Name": {"Fn::Sub": "${AWS::StackName}-DynamoTable"}}
            },
            "APIGatewayURL": {
                "Description": "API Gateway URL",
                "Value": {"Fn::Sub": "https://${APIGateway}.execute-api.${AWS::Region}.amazonaws.com/prod"},
                "Export": {"Name": {"Fn::Sub": "${AWS::StackName}-APIURL"}}
            }
        }
    }

    # Cost Analysis detallado
    cost_analysis = f"""Servicio AWS,Tipo de Recurso,Cantidad Estimada,Costo Unitario (USD),Costo Mensual (USD),Costo Anual (USD),Notas
AWS Lambda,Invocaciones,1000000,0.0000002,200.00,2400.00,Incluye 1M invocaciones gratuitas
AWS Lambda,Duracion (GB-segundo),500000,0.0000166667,8.33,100.00,Basado en 512MB por 1 segundo
Amazon S3,Almacenamiento Standard (GB),100,0.023,2.30,27.60,Primeros 50TB
Amazon S3,Solicitudes PUT/POST,10000,0.0005,5.00,60.00,Por cada 1000 solicitudes
Amazon DynamoDB,Lectura On-Demand (RRU),1000000,0.000125,125.00,1500.00,Unidades de lectura
Amazon DynamoDB,Escritura On-Demand (WRU),500000,0.000625,312.50,3750.00,Unidades de escritura
Amazon API Gateway,Solicitudes REST API,1000000,0.0000035,3.50,42.00,Por millon de solicitudes
Amazon CloudWatch,Metricas personalizadas,50,0.30,15.00,180.00,Por metrica por mes
Amazon CloudWatch,Logs (GB),10,0.50,5.00,60.00,Ingestion y almacenamiento
Amazon CloudFront,Transferencia de datos (GB),1000,0.085,85.00,1020.00,Primeros 10TB
AWS WAF,Solicitudes web,1000000,0.0000006,0.60,7.20,Por millon de solicitudes
SUBTOTAL,,,,,761.23,9139.80,
Soporte AWS (Business),10% del costo,,,76.12,913.98,Recomendado para produccion
TOTAL ESTIMADO,,,,,837.35,10053.78,Costo total mensual/anual"""

    # Implementation Plan detallado
    implementation_plan = f"""Fase,Tarea,Duracion (Dias),Dependencias,Recursos Necesarios,Entregables,Estado,Notas
Fase 1 - Planificacion,Revision de Arquitectura,2,,Arquitecto AWS Senior,Documento de Arquitectura,Pendiente,Validacion de requisitos
Fase 1 - Planificacion,Configuracion de Cuentas AWS,1,Revision de Arquitectura,DevOps Engineer,Cuentas y permisos configurados,Pendiente,Incluye IAM y organizaciones
Fase 1 - Planificacion,Setup de Repositorios,1,Configuracion de Cuentas,DevOps Engineer,Repositorios Git configurados,Pendiente,GitHub/GitLab con CI/CD
Fase 2 - Desarrollo,Desarrollo de Infraestructura,5,Setup de Repositorios,Arquitecto AWS + DevOps,Templates CloudFormation,Pendiente,IaC completa
Fase 2 - Desarrollo,Desarrollo de Aplicacion,10,Desarrollo de Infraestructura,Desarrollador Senior,Codigo de aplicacion,Pendiente,Funciones Lambda y APIs
Fase 2 - Desarrollo,Configuracion de Monitoreo,3,Desarrollo de Aplicacion,DevOps Engineer,Dashboard CloudWatch,Pendiente,Metricas y alertas
Fase 3 - Testing,Pruebas Unitarias,5,Desarrollo de Aplicacion,QA Engineer,Reportes de pruebas,Pendiente,Cobertura minima 80%
Fase 3 - Testing,Pruebas de Integracion,7,Pruebas Unitarias,QA Engineer + DevOps,Pruebas automatizadas,Pendiente,End-to-end testing
Fase 3 - Testing,Pruebas de Carga,3,Pruebas de Integracion,Performance Engineer,Reporte de rendimiento,Pendiente,Usando Artillery o JMeter
Fase 4 - Seguridad,Revision de Seguridad,5,Pruebas de Carga,Security Engineer,Reporte de seguridad,Pendiente,Penetration testing
Fase 4 - Seguridad,Configuracion de WAF,2,Revision de Seguridad,Security Engineer,WAF configurado,Pendiente,Proteccion contra ataques
Fase 4 - Seguridad,Auditoria de Compliance,3,Configuracion de WAF,Compliance Officer,Certificacion de compliance,Pendiente,SOC2/ISO27001 si aplica
Fase 5 - Deployment,Despliegue a Staging,2,Auditoria de Compliance,DevOps Engineer,Ambiente staging funcional,Pendiente,Replica de produccion
Fase 5 - Deployment,Pruebas de Aceptacion,5,Despliegue a Staging,Product Owner + QA,Sign-off de aceptacion,Pendiente,Validacion de negocio
Fase 5 - Deployment,Despliegue a Produccion,3,Pruebas de Aceptacion,DevOps Engineer,Sistema en produccion,Pendiente,Blue-green deployment
Fase 6 - Operaciones,Documentacion Tecnica,5,Despliegue a Produccion,Technical Writer,Documentacion completa,Pendiente,Runbooks y procedimientos
Fase 6 - Operaciones,Capacitacion del Equipo,3,Documentacion Tecnica,Arquitecto AWS,Equipo capacitado,Pendiente,Transferencia de conocimiento
Fase 6 - Operaciones,Monitoreo Post-Deploy,7,Capacitacion del Equipo,Site Reliability Engineer,Sistema estabilizado,Pendiente,Optimizacion continua"""

    # Project Documentation completa
    project_doc = f"""# {project_name} - Documentacion Tecnica Completa

## Resumen Ejecutivo

### Objetivo del Proyecto
{project_name} es una {project_type.lower()} implementada en Amazon Web Services (AWS) que utiliza arquitectura serverless y servicios completamente administrados para garantizar escalabilidad, confiabilidad y costo-efectividad.

### Beneficios Clave
- **Escalabilidad Automatica**: Los servicios se ajustan automaticamente a la demanda
- **Alta Disponibilidad**: Distribucion en multiples zonas de disponibilidad
- **Costo Optimizado**: Modelo de pago por uso sin infraestructura ociosa
- **Seguridad Integrada**: Cifrado en transito y en reposo por defecto
- **Mantenimiento Minimo**: Servicios completamente administrados por AWS

## Arquitectura de la Solucion

### Componentes Principales

#### 1. Capa de Presentacion
- **Amazon CloudFront**: CDN global para distribucion de contenido
- **Amazon S3**: Hosting de sitios web estaticos
- **AWS WAF**: Firewall de aplicaciones web para proteccion

#### 2. Capa de Aplicacion
- **AWS Lambda**: Funciones serverless para logica de negocio
- **Amazon API Gateway**: Gestion y exposicion de APIs REST
- **AWS Step Functions**: Orquestacion de workflows complejos

#### 3. Capa de Datos
- **Amazon DynamoDB**: Base de datos NoSQL para datos transaccionales
- **Amazon S3**: Almacenamiento de objetos y data lake
- **Amazon ElastiCache**: Cache en memoria para optimizacion

#### 4. Capa de Seguridad
- **AWS IAM**: Gestion de identidades y accesos
- **AWS KMS**: Gestion de claves de cifrado
- **AWS CloudTrail**: Auditoria y logging de actividades

#### 5. Capa de Monitoreo
- **Amazon CloudWatch**: Metricas, logs y alertas
- **AWS X-Ray**: Trazabilidad distribuida
- **Amazon SNS**: Notificaciones y alertas

### Patrones de Arquitectura Implementados

1. **Microservicios Serverless**: Cada funcion Lambda maneja una responsabilidad especifica
2. **Event-Driven Architecture**: Comunicacion asincrona entre componentes
3. **CQRS (Command Query Responsibility Segregation)**: Separacion de operaciones de lectura y escritura
4. **Circuit Breaker**: Manejo de fallos y recuperacion automatica

## Especificaciones Tecnicas

### Configuracion de Servicios

#### AWS Lambda
- **Runtime**: Python 3.9
- **Memoria**: 512 MB (ajustable segun carga)
- **Timeout**: 30 segundos
- **Variables de Entorno**: Configuradas por ambiente
- **Layers**: Dependencias compartidas optimizadas

#### Amazon DynamoDB
- **Modo de Facturacion**: On-Demand
- **Cifrado**: Habilitado con AWS KMS
- **Point-in-Time Recovery**: Habilitado
- **Streams**: Configurados para integraciones

#### Amazon S3
- **Clases de Almacenamiento**: Standard, IA, Glacier
- **Versionado**: Habilitado
- **Cifrado**: AES-256 por defecto
- **Lifecycle Policies**: Configuradas para optimizacion de costos

### Consideraciones de Rendimiento

#### Metricas Objetivo
- **Latencia API**: < 200ms percentil 95
- **Disponibilidad**: 99.9% SLA
- **Throughput**: 1000 TPS sostenido
- **Recovery Time**: < 5 minutos

#### Optimizaciones Implementadas
- **Connection Pooling**: Para bases de datos
- **Caching Strategy**: Multi-nivel con TTL optimizado
- **Compression**: Gzip para APIs y contenido estatico
- **CDN Configuration**: Cache headers optimizados

## Seguridad y Compliance

### Medidas de Seguridad Implementadas

#### Autenticacion y Autorizacion
- **AWS Cognito**: Gestion de usuarios y autenticacion
- **JWT Tokens**: Para sesiones de usuario
- **API Keys**: Para integraciones de terceros
- **IAM Roles**: Principio de menor privilegio

#### Cifrado
- **En Transito**: TLS 1.2+ para todas las comunicaciones
- **En Reposo**: AES-256 para todos los datos almacenados
- **Key Management**: AWS KMS con rotacion automatica

#### Monitoreo de Seguridad
- **AWS GuardDuty**: Deteccion de amenazas
- **AWS Config**: Compliance y configuracion
- **VPC Flow Logs**: Monitoreo de trafico de red

### Compliance
- **GDPR**: Implementacion de derecho al olvido
- **SOC 2**: Controles de seguridad y disponibilidad
- **ISO 27001**: Gestion de seguridad de la informacion

## Estimacion de Costos

### Costo Mensual Detallado: ${estimated_cost:.2f} USD

#### Desglose por Servicio
- **Compute (Lambda)**: 35% del costo total
- **Storage (S3, DynamoDB)**: 25% del costo total
- **Networking (CloudFront, API Gateway)**: 20% del costo total
- **Monitoring (CloudWatch)**: 10% del costo total
- **Security (WAF, GuardDuty)**: 10% del costo total

#### Optimizaciones de Costo
- **Reserved Capacity**: Para cargas predecibles
- **Spot Instances**: Para procesamiento batch
- **Lifecycle Policies**: Transicion automatica a storage mas economico
- **Right Sizing**: Monitoreo continuo y ajuste de recursos

## Plan de Implementacion

### Cronograma General: 8-10 semanas

#### Hitos Principales
1. **Semana 1-2**: Planificacion y setup inicial
2. **Semana 3-5**: Desarrollo de infraestructura y aplicacion
3. **Semana 6-7**: Testing y seguridad
4. **Semana 8-9**: Deployment y documentacion
5. **Semana 10**: Estabilizacion y optimizacion

### Equipo Requerido
- **1x Arquitecto AWS Senior**: Liderazgo tecnico
- **2x Desarrolladores Senior**: Desarrollo de aplicacion
- **1x DevOps Engineer**: Infraestructura y CI/CD
- **1x QA Engineer**: Testing y calidad
- **1x Security Engineer**: Seguridad y compliance

## Operaciones y Mantenimiento

### Monitoreo Continuo
- **Dashboards**: CloudWatch dashboards personalizados
- **Alertas**: Configuradas para metricas criticas
- **Logs**: Centralizados y estructurados
- **Metricas de Negocio**: KPIs especificos del dominio

### Procedimientos de Respuesta
- **Incident Response**: Playbooks documentados
- **Escalation Matrix**: Contactos y procedimientos
- **Post-Mortem**: Analisis de incidentes y mejoras
- **Change Management**: Proceso controlado de cambios

### Backup y Recuperacion
- **RTO (Recovery Time Objective)**: 15 minutos
- **RPO (Recovery Point Objective)**: 5 minutos
- **Backup Strategy**: Automatizada y multi-region
- **Disaster Recovery**: Plan documentado y probado

## Proximos Pasos

### Fase Inmediata (Proximas 2 semanas)
1. **Aprobacion de Arquitectura**: Review y sign-off ejecutivo
2. **Setup de Ambiente**: Configuracion de cuentas AWS
3. **Team Onboarding**: Incorporacion del equipo de desarrollo
4. **Repository Setup**: Configuracion de Git y CI/CD

### Fase de Desarrollo (Semanas 3-7)
1. **Infrastructure as Code**: Implementacion de CloudFormation
2. **Core Services**: Desarrollo de servicios principales
3. **Integration Testing**: Pruebas de integracion continua
4. **Security Review**: Revision de seguridad iterativa

### Fase de Deployment (Semanas 8-10)
1. **Staging Deployment**: Despliegue a ambiente de pruebas
2. **User Acceptance Testing**: Validacion con usuarios finales
3. **Production Deployment**: Go-live controlado
4. **Post-Launch Monitoring**: Monitoreo intensivo inicial

## Contacto y Soporte

### Equipo del Proyecto
- **Arquitecto Principal**: [Nombre] - [email]
- **Project Manager**: [Nombre] - [email]
- **DevOps Lead**: [Nombre] - [email]

### Soporte AWS
- **Account Manager**: Contacto directo con AWS
- **Technical Account Manager**: Soporte tecnico especializado
- **Support Plan**: Business o Enterprise segun necesidades

---

**Documento generado automaticamente por el Arquitecto AWS**  
**Fecha de generacion**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Version**: 1.0  
**Estado**: Borrador para revision**"""

    return {
        'cloudformation-template.json': json.dumps(cfn_template, indent=2),
        'cost-analysis.csv': cost_analysis,
        'implementation-plan.csv': implementation_plan,
        'project-documentation.md': project_doc
    }
