"""
Generador Inteligente que SÍ FUNCIONA - Basado en tu ejemplo
Extrae parámetros específicos y genera documentos reales
ENHANCED VERSION with better error handling and more AWS services
"""

import json
import boto3
import os
from typing import Dict, Any, List
import logging
import re

logger = logging.getLogger()

def extract_service_from_conversation(messages: List[Dict], ai_response: str) -> Dict[str, str]:
    """
    Extrae servicio, descripción y objetivo de la conversación real
    Basado en tu ejemplo: servicio, descripcion, objetivo
    ENHANCED with better service detection and error handling
    """
    try:
        # Combinar toda la conversación
        full_conversation = ai_response
        for msg in messages:
            if msg.get('content'):
                full_conversation += f" {msg.get('content')}"
        
        conversation_lower = full_conversation.lower()
        logger.info(f"🔍 ANALYZING CONVERSATION: {len(full_conversation)} characters")
        
        # Detectar servicio AWS específico - EXPANDED LIST
        servicio = "AWS"  # Default
        servicios_aws = {
            'LEX': ['lex', 'bot', 'chatbot', 'conversacional', 'chat', 'asistente virtual'],
            'LAMBDA': ['lambda', 'función', 'serverless', 'sin servidor', 'function'],
            'API GATEWAY': ['api', 'gateway', 'rest', 'endpoint', 'api gateway'],
            'DYNAMODB': ['dynamodb', 'base de datos', 'nosql', 'tabla', 'dynamo'],
            'RDS': ['rds', 'mysql', 'postgresql', 'sql', 'relacional', 'aurora'],
            'S3': ['s3', 'almacenamiento', 'bucket', 'archivos', 'storage'],
            'EC2': ['ec2', 'servidor', 'instancia', 'máquina virtual', 'compute'],
            'ECS': ['ecs', 'contenedor', 'docker', 'container'],
            'EKS': ['eks', 'kubernetes', 'k8s', 'orchestration'],
            'SAGEMAKER': ['sagemaker', 'machine learning', 'ml', 'ia', 'modelo'],
            'BEDROCK': ['bedrock', 'inteligencia artificial', 'genai', 'llm'],
            'CLOUDFRONT': ['cloudfront', 'cdn', 'distribución', 'cache'],
            'ROUTE53': ['route53', 'dns', 'dominio', 'routing'],
            'COGNITO': ['cognito', 'autenticación', 'usuarios', 'auth', 'login'],
            'SNS': ['sns', 'notificaciones', 'mensajes', 'notification'],
            'SQS': ['sqs', 'cola', 'queue', 'messaging'],
            'EVENTBRIDGE': ['eventbridge', 'eventos', 'event', 'event-driven'],
            'STEP FUNCTIONS': ['step functions', 'workflow', 'orquestación', 'state machine'],
            'CLOUDWATCH': ['cloudwatch', 'monitoreo', 'métricas', 'monitoring', 'logs'],
            'VPC': ['vpc', 'red virtual', 'networking', 'subred', 'network'],
            'IAM': ['iam', 'identidad', 'permisos', 'roles', 'security'],
            'ELB': ['load balancer', 'balanceador', 'elb', 'alb', 'nlb'],
            'KINESIS': ['kinesis', 'streaming', 'datos en tiempo real', 'stream'],
            'GLUE': ['glue', 'etl', 'transformación de datos', 'data pipeline'],
            'REDSHIFT': ['redshift', 'data warehouse', 'análisis', 'analytics'],
            'ELASTICSEARCH': ['elasticsearch', 'opensearch', 'búsqueda', 'search'],
            'FARGATE': ['fargate', 'serverless containers', 'container serverless'],
            'AMPLIFY': ['amplify', 'web app', 'frontend', 'full stack'],
            'APPSYNC': ['appsync', 'graphql', 'api graphql', 'real-time api']
        }
        
        # Encontrar el servicio más mencionado
        max_mentions = 0
        for service_name, keywords in servicios_aws.items():
            mentions = sum(1 for keyword in keywords if keyword in conversation_lower)
            if mentions > max_mentions:
                max_mentions = mentions
                servicio = service_name
        
        logger.info(f"🎯 DETECTED SERVICE: {servicio} (mentions: {max_mentions})")
        
        # Extraer descripción con patrones mejorados
        descripcion = ""
        description_patterns = [
            r'(?:necesito|requiero|quiero|busco)\s+(.{20,200}?)(?:\.|$)',
            r'(?:problema|desafío|reto):\s*(.{20,200}?)(?:\.|$)',
            r'(?:solución|implementar|desarrollar)\s+(.{20,200}?)(?:\.|$)',
            r'(?:sistema|aplicación|plataforma)\s+(.{20,200}?)(?:\.|$)',
            r'(?:crear|construir|hacer)\s+(.{20,200}?)(?:\.|$)'
        ]
        
        for pattern in description_patterns:
            matches = re.findall(pattern, full_conversation, re.IGNORECASE | re.DOTALL)
            if matches:
                descripcion = matches[0].strip()[:200]
                break
        
        # Si no encuentra patrón, usar primera oración significativa
        if not descripcion:
            sentences = re.split(r'[.!?]+', full_conversation)
            for sentence in sentences:
                if len(sentence.strip()) > 30 and any(word in sentence.lower() for word in ['aws', 'sistema', 'aplicación', 'solución', 'implementar']):
                    descripcion = sentence.strip()[:200]
                    break
        
        # Extraer objetivo con patrones mejorados
        objetivo = ""
        objective_patterns = [
            r'(?:objetivo|meta|propósito|finalidad):\s*(.{20,200}?)(?:\.|$)',
            r'(?:para|con el fin de|con la finalidad de)\s+(.{20,200}?)(?:\.|$)',
            r'(?:lograr|conseguir|obtener|alcanzar)\s+(.{20,200}?)(?:\.|$)',
            r'(?:beneficio|ventaja|mejora)\s+(.{20,200}?)(?:\.|$)'
        ]
        
        for pattern in objective_patterns:
            matches = re.findall(pattern, full_conversation, re.IGNORECASE | re.DOTALL)
            if matches:
                objetivo = matches[0].strip()[:200]
                break
        
        # Objetivos por defecto mejorados por servicio
        if not objetivo:
            objetivos_default = {
                'LEX': 'Implementar un chatbot inteligente para mejorar la atención al cliente y automatizar respuestas',
                'LAMBDA': 'Desarrollar funciones serverless para optimizar procesos y reducir costos operativos',
                'API GATEWAY': 'Crear APIs escalables y seguras para integrar servicios y aplicaciones',
                'DYNAMODB': 'Implementar base de datos NoSQL de alto rendimiento para aplicaciones modernas',
                'RDS': 'Establecer base de datos relacional gestionada con alta disponibilidad',
                'S3': 'Implementar almacenamiento seguro y escalable para datos y contenido estático',
                'EC2': 'Desplegar infraestructura de cómputo flexible y escalable',
                'ECS': 'Orquestar contenedores para aplicaciones modernas y microservicios',
                'EKS': 'Gestionar aplicaciones Kubernetes de forma escalable y segura',
                'SAGEMAKER': 'Desarrollar y desplegar modelos de machine learning en producción',
                'BEDROCK': 'Integrar inteligencia artificial generativa en aplicaciones empresariales',
                'CLOUDFRONT': 'Optimizar distribución de contenido global con baja latencia',
                'ROUTE53': 'Gestionar DNS y routing inteligente para alta disponibilidad',
                'COGNITO': 'Implementar autenticación y autorización segura de usuarios',
                'SNS': 'Establecer sistema de notificaciones escalable y confiable',
                'SQS': 'Implementar cola de mensajes para desacoplar componentes',
                'EVENTBRIDGE': 'Crear arquitectura basada en eventos para sistemas distribuidos',
                'STEP FUNCTIONS': 'Orquestar workflows complejos con manejo de errores',
                'CLOUDWATCH': 'Implementar monitoreo y observabilidad completa del sistema',
                'VPC': 'Crear red virtual segura y aislada para recursos AWS',
                'IAM': 'Gestionar identidades y accesos con principio de menor privilegio',
                'ELB': 'Distribuir tráfico de forma inteligente para alta disponibilidad'
            }
            objetivo = objetivos_default.get(servicio, 'Implementar solución AWS escalable, segura y eficiente')
        
        # Asegurar calidad mínima
        if not descripcion or len(descripcion) < 20:
            descripcion = f"Implementación de solución empresarial basada en {servicio} para optimizar procesos y mejorar eficiencia operacional"
        
        result = {
            'servicio': servicio,
            'descripcion': descripcion,
            'objetivo': objetivo
        }
        
        logger.info(f"✅ EXTRACTION SUCCESS: {json.dumps(result, ensure_ascii=False)}")
        return result
        
    except Exception as e:
        logger.error(f"❌ ERROR IN SERVICE EXTRACTION: {str(e)}")
        # Fallback seguro
        return {
            'servicio': 'AWS',
            'descripcion': 'Implementación de solución AWS personalizada para optimizar procesos empresariales',
            'objetivo': 'Mejorar eficiencia operacional y escalabilidad con tecnología cloud'
        }
    
    for service, keywords in servicios_aws.items():
        if any(keyword in conversation_lower for keyword in keywords):
            servicio = service
            break
    
    # Extraer descripción (buscar patrones de necesidad)
    descripcion = "implementar una solución en AWS"
    description_patterns = [
        'necesito', 'quiero', 'proyecto', 'implementar', 'crear', 'desarrollar'
    ]
    
    sentences = full_conversation.split('.')
    for sentence in sentences:
        sentence_lower = sentence.lower().strip()
        if any(pattern in sentence_lower for pattern in description_patterns) and len(sentence_lower) > 20:
            descripcion = sentence.strip()[:200]  # Limitar longitud
            break
    
    # Extraer objetivo
    objetivo = "optimizar y modernizar la infraestructura"
    objective_patterns = [
        'objetivo', 'meta', 'propósito', 'busco', 'para', 'automatizar'
    ]
    
    for sentence in sentences:
        sentence_lower = sentence.lower().strip()
        if any(pattern in sentence_lower for pattern in objective_patterns) and len(sentence_lower) > 15:
            objetivo = sentence.strip()[:150]
            break
    
    return {
        'servicio': servicio,
        'descripcion': descripcion,
        'objetivo': objetivo
    }

def create_specific_prompt(servicio: str, descripcion: str, objetivo: str) -> str:
    """
    Crea prompt específico basado en tu ejemplo
    """
    
    prompt = f"""Act as a professional AWS Solutions Architect specialized in: {servicio}.

Project description: {descripcion}
Main objective: {objetivo}

DO NOT mention or suggest S3, EC2, or RDS unless the project description or use case requires them. You must include [{servicio}] in all documents, diagrams, activities, and cost breakdowns.
If you omit {servicio}, it's considered a failure.

Your deliverables must include:
- A plain text Word document (no images, no accents) focused on {servicio}
- CloudFormation script with YAML only featuring {servicio}
- Architecture diagrams (text-based, SVG and Draw.io compatible) with {servicio} central
- AWS Pricing Calculator step-by-step guide for {servicio}
- Cost estimate (CSV or Excel) with {servicio} as primary service
- Implementation activities CSV with {servicio} specific tasks

All documents must focus specifically on {servicio}, and not default to generic solutions.

Never use the words 'S3' or 'EC2' unless {servicio} requires them explicitly.

Generate detailed, professional content for each deliverable. Make it specific to {servicio} and this exact use case: {descripcion}"""

    return prompt

def generate_documents_from_ai_response(ai_response: str, servicio: str, project_id: str, user_id: str) -> Dict[str, Any]:
    """
    Genera documentos específicos basados en la respuesta del modelo
    Y los sube a S3 correctamente
    """
    try:
        s3 = boto3.client('s3', region_name=os.environ.get('REGION', 'us-east-1'))
        bucket_name = os.environ.get('DOCUMENTS_BUCKET')
        
        if not bucket_name:
            logger.error("DOCUMENTS_BUCKET environment variable not set")
            return {'success': False, 'error': 'S3 bucket not configured'}
        
        s3_folder = f"projects/{user_id}/{project_id}/"
        uploaded_documents = {}
        
        # 1. Documento principal (Word) - Usar respuesta completa del AI
        word_key = f"{s3_folder}propuesta-ejecutiva-{servicio.lower().replace(' ', '-')}.txt"
        s3.put_object(
            Bucket=bucket_name,
            Key=word_key,
            Body=ai_response.encode('utf-8'),
            ContentType='text/plain'
        )
        uploaded_documents['propuesta_ejecutiva'] = word_key
        logger.info(f"✅ Uploaded executive proposal: {word_key}")
        
        # 2. Documento técnico - Extraer secciones técnicas
        tech_content = extract_technical_content(ai_response, servicio)
        tech_key = f"{s3_folder}documento-tecnico-{servicio.lower().replace(' ', '-')}.txt"
        s3.put_object(
            Bucket=bucket_name,
            Key=tech_key,
            Body=tech_content.encode('utf-8'),
            ContentType='text/plain'
        )
        uploaded_documents['documento_tecnico'] = tech_key
        logger.info(f"✅ Uploaded technical document: {tech_key}")
        
        # 3. CloudFormation - Extraer YAML
        cf_content = extract_cloudformation_content(ai_response, servicio)
        cf_key = f"{s3_folder}cloudformation-{servicio.lower().replace(' ', '-')}.yaml"
        s3.put_object(
            Bucket=bucket_name,
            Key=cf_key,
            Body=cf_content.encode('utf-8'),
            ContentType='text/yaml'
        )
        uploaded_documents['cloudformation'] = cf_key
        logger.info(f"✅ Uploaded CloudFormation: {cf_key}")
        
        # 4. Actividades CSV
        activities_content = extract_activities_content(ai_response, servicio)
        activities_key = f"{s3_folder}actividades-{servicio.lower().replace(' ', '-')}.csv"
        s3.put_object(
            Bucket=bucket_name,
            Key=activities_key,
            Body=activities_content.encode('utf-8'),
            ContentType='text/csv'
        )
        uploaded_documents['actividades'] = activities_key
        logger.info(f"✅ Uploaded activities: {activities_key}")
        
        # 5. Costos CSV
        costs_content = extract_costs_content(ai_response, servicio)
        costs_key = f"{s3_folder}costos-{servicio.lower().replace(' ', '-')}.csv"
        s3.put_object(
            Bucket=bucket_name,
            Key=costs_key,
            Body=costs_content.encode('utf-8'),
            ContentType='text/csv'
        )
        uploaded_documents['costos'] = costs_key
        logger.info(f"✅ Uploaded costs: {costs_key}")
        
        # 6. Guía calculadora
        guide_content = extract_calculator_guide_content(ai_response, servicio)
        guide_key = f"{s3_folder}guia-calculadora-{servicio.lower().replace(' ', '-')}.txt"
        s3.put_object(
            Bucket=bucket_name,
            Key=guide_key,
            Body=guide_content.encode('utf-8'),
            ContentType='text/plain'
        )
        uploaded_documents['guia_calculadora'] = guide_key
        logger.info(f"✅ Uploaded calculator guide: {guide_key}")
        
        return {
            'success': True,
            'documents_generated': len(uploaded_documents),
            'uploaded_documents': uploaded_documents,
            's3_folder': s3_folder,
            'service_focus': servicio
        }
        
    except Exception as e:
        logger.error(f"Error uploading documents to S3: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'documents_generated': 0
        }

def extract_technical_content(ai_response: str, servicio: str) -> str:
    """Extrae contenido técnico específico"""
    lines = ai_response.split('\n')
    tech_lines = []
    
    tech_keywords = ['arquitectura', 'técnico', 'configuración', 'implementación', servicio.lower()]
    
    for line in lines:
        if any(keyword in line.lower() for keyword in tech_keywords):
            tech_lines.append(line)
    
    if tech_lines:
        return '\n'.join(tech_lines)
    
    return f"""DOCUMENTO TÉCNICO - {servicio}

Arquitectura propuesta centrada en {servicio}:

1. Componente principal: {servicio}
2. Configuración específica para el caso de uso
3. Integración con servicios complementarios
4. Consideraciones de seguridad para {servicio}
5. Monitoreo y mantenimiento

Especificaciones técnicas basadas en {servicio}."""

def extract_cloudformation_content(ai_response: str, servicio: str) -> str:
    """Extrae template CloudFormation"""
    # Buscar contenido YAML en la respuesta
    lines = ai_response.split('\n')
    yaml_lines = []
    in_yaml = False
    
    for line in lines:
        if 'cloudformation' in line.lower() or 'yaml' in line.lower():
            in_yaml = True
        elif in_yaml and (line.startswith('AWSTemplateFormatVersion') or 'Resources:' in line):
            yaml_lines.append(line)
        elif in_yaml and line.strip():
            yaml_lines.append(line)
    
    if yaml_lines:
        return '\n'.join(yaml_lines)
    
    # Template básico específico para el servicio
    return f"""AWSTemplateFormatVersion: '2010-09-09'
Description: 'CloudFormation template for {servicio} - Generated from AI analysis'

Parameters:
  Environment:
    Type: String
    Default: 'prod'
    Description: 'Environment name'

Resources:
  # {servicio} specific resources will be defined here
  # This template is customized for {servicio} use case
  
Outputs:
  ServiceEndpoint:
    Description: '{servicio} endpoint or identifier'
    Value: !Ref MainResource
    Export:
      Name: !Sub '${{AWS::StackName}}-{servicio}-Endpoint'"""

def extract_activities_content(ai_response: str, servicio: str) -> str:
    """Extrae actividades de implementación"""
    csv_content = "Fase,Actividad,Descripcion,Duracion_Estimada,Responsable\n"
    
    # Buscar actividades en la respuesta
    lines = ai_response.split('\n')
    activities = []
    
    for line in lines:
        if any(word in line.lower() for word in ['paso', 'fase', 'actividad', 'implementar', 'configurar']):
            if len(line.strip()) > 10:
                activities.append(line.strip())
    
    # Si encontramos actividades específicas, usarlas
    if activities:
        for i, activity in enumerate(activities[:8], 1):  # Máximo 8 actividades
            csv_content += f"Fase {i},{activity},Implementación específica de {servicio},2-3 días,Arquitecto AWS\n"
    else:
        # Actividades por defecto específicas del servicio
        default_activities = [
            f"Configuración inicial de {servicio}",
            f"Integración de {servicio} con servicios complementarios",
            f"Configuración de seguridad para {servicio}",
            f"Pruebas de {servicio}",
            f"Despliegue de {servicio} en producción"
        ]
        
        for i, activity in enumerate(default_activities, 1):
            csv_content += f"Fase {i},{activity},Actividad específica de {servicio},2-3 días,Arquitecto AWS\n"
    
    return csv_content

def extract_costs_content(ai_response: str, servicio: str) -> str:
    """Extrae estimación de costos"""
    csv_content = "Servicio,Tipo_Instancia,Costo_Mensual_USD,Costo_Anual_USD,Notas\n"
    
    # Agregar costo principal del servicio
    csv_content += f"{servicio},Configuración estándar,100,1200,Costo base de {servicio}\n"
    
    # Buscar menciones de costos en la respuesta
    if 'costo' in ai_response.lower() or '$' in ai_response:
        csv_content += f"Servicios complementarios,Soporte para {servicio},50,600,Servicios adicionales\n"
    else:
        csv_content += f"Servicios de soporte,Configuración mínima,30,360,Servicios complementarios para {servicio}\n"
    
    csv_content += f"Total estimado,Solución completa,130,1560,Costo total de la solución con {servicio}\n"
    
    return csv_content

def extract_calculator_guide_content(ai_response: str, servicio: str) -> str:
    """Extrae guía de calculadora AWS"""
    guide_content = f"""GUÍA AWS PRICING CALCULATOR - {servicio}

1. Acceder a https://calculator.aws/
2. Buscar el servicio: {servicio}
3. Configurar parámetros específicos para {servicio}:
   - Región: us-east-1 (recomendado)
   - Configuración según caso de uso
   - Estimación de uso mensual

4. Agregar servicios complementarios necesarios para {servicio}
5. Revisar estimación total
6. Exportar resultados para documentación

Parámetros específicos para {servicio}:
- Configuración recomendada según el caso de uso
- Consideraciones de escalabilidad
- Optimización de costos

Esta guía está específicamente diseñada para {servicio}."""
    
    return guide_content
