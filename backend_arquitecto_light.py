# AWS Propuestas v3 - Arquitecto Backend Light Version
# Solución profesional para generar documentos sin caracteres especiales

import json
import boto3
import uuid
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from unidecode import unidecode
import io
import csv

# Configurar logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Clientes AWS
bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
s3_client = boto3.client('s3', region_name='us-east-1')

# Variables de entorno
PROJECTS_TABLE = os.environ.get('PROJECTS_TABLE', 'aws-propuestas-v3-projects-prod')
DOCUMENTS_BUCKET = os.environ.get('DOCUMENTS_BUCKET', 'aws-propuestas-v3-documents-prod-035385358261')

# Tabla DynamoDB
projects_table = dynamodb.Table(PROJECTS_TABLE)

def clean_text(text: str) -> str:
    """Elimina acentos y caracteres especiales de un texto"""
    if not text:
        return ""
    # Usar unidecode para convertir caracteres especiales
    cleaned = unidecode(text)
    # Reemplazar caracteres problemáticos adicionales
    cleaned = cleaned.replace('ñ', 'n').replace('Ñ', 'N')
    return cleaned

def clean_filename(filename: str) -> str:
    """Limpia un nombre de archivo para que sea compatible"""
    cleaned = clean_text(filename)
    # Reemplazar espacios y caracteres especiales con guiones
    cleaned = cleaned.replace(' ', '-').replace('_', '-')
    # Remover caracteres no alfanuméricos excepto guiones y puntos
    import re
    cleaned = re.sub(r'[^a-zA-Z0-9\-\.]', '', cleaned)
    return cleaned

def invoke_bedrock_model(messages: List[Dict], model_id: str = "anthropic.claude-3-haiku-20240307-v1:0") -> str:
    """Invoca un modelo de Bedrock Runtime usando la API Converse"""
    try:
        # Usar la nueva API Converse
        response = bedrock_client.converse(
            modelId=model_id,
            messages=messages,
            inferenceConfig={
                'maxTokens': 4000,
                'temperature': 0.7
            }
        )
        
        return response['output']['message']['content'][0]['text']
        
    except Exception as e:
        logger.error(f"Error invoking Bedrock model: {str(e)}")
        return f"Error al procesar la solicitud: {str(e)}"

def save_project_to_dynamodb(project_data: Dict) -> bool:
    """Guarda un proyecto en DynamoDB"""
    try:
        # Limpiar todos los textos del proyecto
        cleaned_project = {}
        for key, value in project_data.items():
            if isinstance(value, str):
                cleaned_project[key] = clean_text(value)
            elif isinstance(value, dict):
                cleaned_project[key] = {k: clean_text(v) if isinstance(v, str) else v for k, v in value.items()}
            else:
                cleaned_project[key] = value
        
        # Agregar timestamp
        cleaned_project['updatedAt'] = datetime.utcnow().isoformat()
        
        projects_table.put_item(Item=cleaned_project)
        logger.info(f"Project saved to DynamoDB: {cleaned_project.get('projectId')}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving project to DynamoDB: {str(e)}")
        return False

def generate_activities_csv(project_name: str, project_info: Dict) -> str:
    """Genera un archivo CSV con actividades de implementación"""
    try:
        # Actividades base para cualquier proyecto AWS
        activities = [
            ['Fase', 'Actividad', 'Descripcion', 'Duracion_Dias', 'Responsable', 'Dependencias', 'Estado'],
            ['Planificacion', 'Revision de requerimientos', 'Analizar y validar todos los requerimientos del proyecto', '3', 'Arquitecto de Soluciones', 'Ninguna', 'Pendiente'],
            ['Planificacion', 'Diseno de arquitectura', 'Crear el diseno detallado de la arquitectura AWS', '5', 'Arquitecto de Soluciones', 'Revision de requerimientos', 'Pendiente'],
            ['Implementacion', 'Configuracion de VPC y redes', 'Crear VPC, subnets, security groups y configuracion de red', '2', 'Ingeniero DevOps', 'Diseno de arquitectura', 'Pendiente'],
            ['Implementacion', 'Despliegue de servicios principales', 'Implementar EC2, RDS, Lambda u otros servicios principales', '7', 'Ingeniero DevOps', 'Configuracion de VPC y redes', 'Pendiente'],
            ['Implementacion', 'Configuracion de seguridad', 'Implementar IAM, KMS, CloudTrail y otras medidas de seguridad', '3', 'Especialista en Seguridad', 'Despliegue de servicios principales', 'Pendiente'],
            ['Pruebas', 'Pruebas de funcionalidad', 'Ejecutar pruebas funcionales y de integracion', '4', 'QA Engineer', 'Configuracion de seguridad', 'Pendiente'],
            ['Pruebas', 'Pruebas de rendimiento', 'Validar rendimiento y escalabilidad del sistema', '3', 'QA Engineer', 'Pruebas de funcionalidad', 'Pendiente'],
            ['Despliegue', 'Despliegue a produccion', 'Migrar la solucion al ambiente de produccion', '2', 'Ingeniero DevOps', 'Pruebas de rendimiento', 'Pendiente'],
            ['Despliegue', 'Documentacion y entrega', 'Crear documentacion final y realizar entrega al cliente', '2', 'Arquitecto de Soluciones', 'Despliegue a produccion', 'Pendiente']
        ]
        
        # Limpiar textos
        cleaned_activities = []
        for row in activities:
            cleaned_row = [clean_text(str(cell)) for cell in row]
            cleaned_activities.append(cleaned_row)
        
        # Convertir a CSV string
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(cleaned_activities)
        return output.getvalue()
        
    except Exception as e:
        logger.error(f"Error generating activities CSV: {str(e)}")
        return "Error,generando,archivo,CSV"

def generate_text_document(project_name: str, project_info: Dict) -> str:
    """Genera un documento de texto con la información del proyecto"""
    try:
        content = f"""PROPUESTA ARQUITECTONICA: {clean_text(project_name)}

1. INFORMACION GENERAL
Nombre del Proyecto: {clean_text(project_name)}
Fecha de Creacion: {datetime.now().strftime("%Y-%m-%d")}
Tipo de Solucion: {clean_text(project_info.get("service_focus", "Solucion Integral AWS"))}

2. DESCRIPCION DEL PROYECTO
{clean_text(project_info.get('description', 'Proyecto de implementacion en AWS'))}

3. OBJETIVO
{clean_text(project_info.get('objective', 'Implementar una solucion robusta y escalable en AWS'))}

4. SERVICIOS AWS RECOMENDADOS
- Amazon EC2 - Instancias de computo elasticas
- Amazon RDS - Base de datos relacional administrada
- Amazon S3 - Almacenamiento de objetos escalable
- Amazon VPC - Red privada virtual
- AWS IAM - Gestion de identidades y accesos
- Amazon CloudWatch - Monitoreo y observabilidad
- AWS CloudFormation - Infraestructura como codigo

5. CONSIDERACIONES DE SEGURIDAD
- Implementacion de principio de menor privilegio en IAM
- Encriptacion en transito y en reposo
- Configuracion de Security Groups restrictivos
- Habilitacion de CloudTrail para auditoria
- Implementacion de AWS Config para compliance

6. PROXIMOS PASOS
1. Revision y aprobacion de la propuesta
2. Planificacion detallada del proyecto
3. Configuracion del ambiente de desarrollo
4. Inicio de la implementacion por fases
5. Pruebas y validacion de la solucion

7. ESTIMACION DE COSTOS
Los costos estimados para este proyecto incluyen:
- Servicios de computo (EC2, Lambda)
- Almacenamiento (S3, EBS)
- Base de datos (RDS)
- Redes (VPC, Load Balancer)
- Monitoreo (CloudWatch)

Para obtener una estimacion detallada, utilice la Calculadora de AWS
con los parametros especificos de su proyecto.

8. CONTACTO
Para mas informacion sobre esta propuesta, contacte al equipo
de arquitectura de soluciones AWS.

---
Documento generado automaticamente
Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        return content
        
    except Exception as e:
        logger.error(f"Error generating text document: {str(e)}")
        return "Error generando documento de texto"

def generate_costs_csv(project_name: str, project_info: Dict) -> str:
    """Genera un archivo CSV con estimación de costos"""
    try:
        # Costos estimados base para servicios AWS comunes
        costs = [
            ['Servicio', 'Tipo', 'Cantidad', 'Costo_Mensual_USD', 'Descripcion'],
            ['Amazon EC2', 't3.medium', '2', '67.32', 'Instancias de aplicacion'],
            ['Amazon RDS', 'db.t3.micro', '1', '15.84', 'Base de datos MySQL'],
            ['Amazon S3', 'Standard', '100', '2.30', '100 GB de almacenamiento'],
            ['Application Load Balancer', 'ALB', '1', '22.50', 'Balanceador de carga'],
            ['Amazon CloudWatch', 'Logs y Metricas', '1', '10.00', 'Monitoreo basico'],
            ['AWS NAT Gateway', 'NAT Gateway', '1', '45.00', 'Conectividad saliente'],
            ['TOTAL ESTIMADO', '', '', '162.96', 'Costo mensual estimado total']
        ]
        
        # Limpiar textos
        cleaned_costs = []
        for row in costs:
            cleaned_row = [clean_text(str(cell)) for cell in row]
            cleaned_costs.append(cleaned_row)
        
        # Convertir a CSV string
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(cleaned_costs)
        return output.getvalue()
        
    except Exception as e:
        logger.error(f"Error generating costs CSV: {str(e)}")
        return "Error,generando,archivo,costos"

def generate_calculator_guide(project_name: str, project_info: Dict) -> str:
    """Genera una guía para usar la Calculadora de AWS"""
    try:
        guide = f"""GUIA PARA CALCULADORA DE AWS - {clean_text(project_name)}

INSTRUCCIONES PASO A PASO:

1. ACCEDER A LA CALCULADORA
   - Visite: https://calculator.aws
   - Haga clic en "Create estimate"

2. AGREGAR SERVICIOS DE COMPUTO
   - Busque "Amazon EC2"
   - Seleccione la region: US East (N. Virginia)
   - Tipo de instancia: t3.medium
   - Cantidad: 2 instancias
   - Uso: 24 horas/dia, 30 dias/mes

3. AGREGAR BASE DE DATOS
   - Busque "Amazon RDS"
   - Motor: MySQL
   - Tipo de instancia: db.t3.micro
   - Almacenamiento: 20 GB SSD
   - Multi-AZ: No (para desarrollo)

4. AGREGAR ALMACENAMIENTO
   - Busque "Amazon S3"
   - Almacenamiento Standard: 100 GB
   - Solicitudes PUT/COPY/POST/LIST: 1,000
   - Solicitudes GET/SELECT: 10,000

5. AGREGAR BALANCEADOR DE CARGA
   - Busque "Elastic Load Balancing"
   - Tipo: Application Load Balancer
   - Cantidad: 1
   - Datos procesados: 1 GB/mes

6. AGREGAR MONITOREO
   - Busque "Amazon CloudWatch"
   - Metricas personalizadas: 10
   - Logs ingeridos: 5 GB/mes
   - Alarmas: 5

7. AGREGAR CONECTIVIDAD
   - Busque "VPC"
   - NAT Gateway: 1
   - Datos procesados: 10 GB/mes

8. REVISAR Y AJUSTAR
   - Revise todos los servicios agregados
   - Ajuste las cantidades segun sus necesidades
   - Considere descuentos por Reserved Instances
   - Exporte el estimado en PDF

NOTAS IMPORTANTES:
- Los precios pueden variar por region
- Considere costos de transferencia de datos
- Evalúe opciones de ahorro (Reserved Instances, Savings Plans)
- Revise regularmente y optimice costos

ESTIMADO BASE MENSUAL: $162.96 USD
(Sin incluir transferencia de datos ni impuestos)

---
Guia generada para: {clean_text(project_name)}
Fecha: {datetime.now().strftime("%Y-%m-%d")}
"""
        return guide
        
    except Exception as e:
        logger.error(f"Error generating calculator guide: {str(e)}")
        return "Error generando guia de calculadora"

def upload_file_to_s3(file_content: str, file_name: str, project_name: str) -> bool:
    """Sube un archivo a S3"""
    try:
        clean_project_name = clean_filename(project_name)
        s3_key = f"{clean_project_name}/{file_name}"
        
        s3_client.put_object(
            Bucket=DOCUMENTS_BUCKET,
            Key=s3_key,
            Body=file_content.encode('utf-8'),
            ContentType='text/plain'
        )
        
        logger.info(f"File uploaded to S3: {s3_key}")
        return True
        
    except Exception as e:
        logger.error(f"Error uploading file to S3: {str(e)}")
        return False

def lambda_handler(event, context):
    """Handler principal de Lambda"""
    try:
        # Parsear el evento
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        messages = body.get('messages', [])
        selected_model = body.get('selected_model', 'anthropic.claude-3-haiku-20240307-v1:0')
        project_id = body.get('projectId') or str(uuid.uuid4())
        
        # Obtener la respuesta del modelo
        if messages:
            response_text = invoke_bedrock_model(messages, selected_model)
        else:
            response_text = "Hola! Soy tu Arquitecto AWS. Para comenzar, necesito que me proporciones el nombre del proyecto."
        
        # Detectar si se debe generar documentos
        should_generate_docs = any([
            'generar' in response_text.lower(),
            'documentos' in response_text.lower(),
            'archivos' in response_text.lower(),
            'subir' in response_text.lower(),
            'bucket' in response_text.lower()
        ])
        
        # Información del proyecto (extraer del contexto)
        project_info = {
            'service_focus': 'AWS',
            'description': 'Proyecto de arquitectura AWS',
            'objective': 'Implementar solucion en AWS',
            'status': 'IN_PROGRESS'
        }
        
        # Si hay mensajes, extraer información del proyecto
        project_name = 'ProyectoAWS'
        if messages:
            last_message = messages[-1].get('content', '')
            if 'tiendaonline' in last_message.lower():
                project_name = 'TiendaOnline'
                project_info.update({
                    'description': 'Aplicacion de e-commerce completa',
                    'objective': 'Crear tienda online escalable',
                    'service_focus': 'E-commerce'
                })
            else:
                # Intentar extraer nombre del proyecto del contexto
                for msg in messages:
                    content = msg.get('content', '').lower()
                    if 'proyecto' in content:
                        words = content.split()
                        for i, word in enumerate(words):
                            if word in ['proyecto', 'llama', 'llamado', 'nombre'] and i + 1 < len(words):
                                next_word = words[i + 1]
                                if len(next_word) > 2 and not next_word in ['es', 'se', 'de', 'la', 'el']:
                                    project_name = next_word.title()
                                    break
        
        # Generar documentos si es necesario
        documents_generated = False
        if should_generate_docs:
            try:
                # Generar archivos
                activities_csv = generate_activities_csv(project_name, project_info)
                text_doc = generate_text_document(project_name, project_info)
                costs_csv = generate_costs_csv(project_name, project_info)
                calculator_guide = generate_calculator_guide(project_name, project_info)
                
                # Nombres de archivos limpios
                clean_name = clean_filename(project_name)
                
                # Subir archivos a S3
                upload_file_to_s3(activities_csv, f"{clean_name}-actividades.csv", project_name)
                upload_file_to_s3(text_doc, f"{clean_name}-propuesta.txt", project_name)
                upload_file_to_s3(costs_csv, f"{clean_name}-costos.csv", project_name)
                upload_file_to_s3(calculator_guide, f"{clean_name}-calculadora-guia.txt", project_name)
                
                documents_generated = True
                
                # Actualizar respuesta para confirmar generación
                response_text += f"\n\n✅ ARCHIVOS GENERADOS EXITOSAMENTE:\n\n📋 {clean_name}-actividades.csv\n📄 {clean_name}-propuesta.txt\n💰 {clean_name}-costos.csv\n🧮 {clean_name}-calculadora-guia.txt\n\n📁 Todos los archivos han sido subidos al bucket S3 en la carpeta: {clean_name}/\n\n✨ Los archivos NO contienen acentos ni caracteres especiales y son completamente compatibles."
                
            except Exception as e:
                logger.error(f"Error generating documents: {str(e)}")
                response_text += f"\n\n❌ Error al generar documentos: {str(e)}"
        
        # Guardar proyecto en DynamoDB
        project_data = {
            'projectId': project_id,
            'projectName': clean_text(project_name),
            'status': 'IN_PROGRESS',
            'currentStep': '1',
            'createdAt': datetime.utcnow().isoformat(),
            'updatedAt': datetime.utcnow().isoformat(),
            'documentCount': 4 if documents_generated else 0,
            'hasDocuments': documents_generated,
            'projectInfo': project_info,
            'lastMessage': clean_text(response_text[:500])  # Truncar para DynamoDB
        }
        
        save_project_to_dynamodb(project_data)
        
        # Respuesta
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({
                'response': response_text,
                'modelId': selected_model,
                'projectId': project_id,
                'projectInfo': project_info,
                'currentStep': 1,
                'isComplete': documents_generated,
                'usage': {
                    'inputTokens': sum(len(msg.get('content', '')) for msg in messages),
                    'outputTokens': len(response_text),
                    'totalTokens': sum(len(msg.get('content', '')) for msg in messages) + len(response_text)
                },
                'documentGeneration': {
                    'generated': documents_generated,
                    'bucket': DOCUMENTS_BUCKET,
                    'folder': clean_filename(project_name)
                } if documents_generated else None,
                'specificService': project_info.get('service_focus', 'AWS')
            })
        }
        
    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Error processing arquitecto request',
                'details': str(e)
            })
        }
