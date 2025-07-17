import json
import boto3
import os
from datetime import datetime
import uuid
import re

# Cliente Bedrock
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')

# Prompt maestro completo
PROMPT_MAESTRO = """
Actua como arquitecto de soluciones AWS y consultor experto. Vamos a dimensionar, documentar y entregar una solucion profesional en AWS, siguiendo mejores practicas y generando todos los archivos necesarios para una propuesta ejecutiva. No uses acentos ni caracteres especiales en ningun texto, archivo, script ni documento.

IMPORTANTE: Sigue este flujo paso a paso:

1. Primero pregunta: Cual es el nombre del proyecto

2. Despues pregunta: El proyecto es una solucion integral (como migracion, aplicacion nueva, modernizacion, analitica, seguridad, IA, IoT, data lake, networking, DRP, VDI, integracion, etc.) o es un servicio rapido especifico (implementacion de instancias EC2, RDS, SES, VPN, ELB, S3, VPC, CloudFront, SSO, backup, etc.)

Si elige "servicio rapido especifico":
- Muestra un catalogo de servicios rapidos comunes
- Haz solo las preguntas minimas necesarias
- Genera todos los documentos: CloudFormation, costos, diagramas, guia

Si elige "solucion integral":
- Haz una entrevista guiada, una pregunta a la vez
- Captura: objetivo, descripcion, servicios AWS, integraciones, seguridad, alta disponibilidad, usuarios, presupuesto, fechas
- Genera todos los documentos completos

SIEMPRE genera al final:
- Tabla de actividades de implementacion (CSV)
- Script CloudFormation para desplegar
- Diagrama de arquitectura
- Documento Word con descripcion completa
- Archivo de costos estimados (CSV)
- Guia para calculadora AWS

Pregunta una cosa a la vez. Se claro y especifico. El flujo debe ser guiado y conversacional como un arquitecto AWS real.
"""

def clean_text(text):
    """Limpia texto de caracteres especiales usando regex"""
    if not text:
        return ""
    # Remover acentos y caracteres especiales básicos
    text = str(text)
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'ñ': 'n', 'Ñ': 'N', 'ü': 'u', 'Ü': 'U'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def lambda_handler(event, context):
    try:
        # Parsear el cuerpo de la solicitud
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        messages = body.get('messages', [])
        selected_model = body.get('selected_model', 'amazon.nova-pro-v1:0')
        
        if not messages:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({'error': 'No messages provided'})
            }
        
        # Construir el prompt con el contexto maestro
        conversation_history = ""
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            conversation_history += f"\n{role.upper()}: {content}"
        
        # Prompt completo con contexto maestro
        full_prompt = f"{PROMPT_MAESTRO}\n\n--- CONVERSACION ACTUAL ---{conversation_history}\n\nARQUITECTO AWS:"
        
        # Preparar mensajes para Bedrock
        bedrock_messages = [
            {
                "role": "user",
                "content": [{"text": full_prompt}]
            }
        ]
        
        # Llamar a Bedrock
        if 'nova' in selected_model.lower():
            # Nova Pro
            payload = {
                "messages": bedrock_messages,
                "inferenceConfig": {
                    "maxTokens": 4000,
                    "temperature": 0.7
                }
            }
            
            response = bedrock_runtime.invoke_model(
                modelId=selected_model,
                body=json.dumps(payload),
                contentType='application/json',
                accept='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            ai_response = response_body['output']['message']['content'][0]['text']
            
        else:
            # Claude
            response = bedrock_runtime.converse(
                modelId=selected_model,
                messages=bedrock_messages,
                inferenceConfig={
                    'maxTokens': 4000,
                    'temperature': 0.7
                }
            )
            
            ai_response = response['output']['message']['content'][0]['text']
        
        # Limpiar respuesta
        ai_response = clean_text(ai_response)
        
        # Detectar si se están generando documentos
        response_lower = ai_response.lower()
        documents_generated = []
        mcp_services_used = []
        
        # Detectar generación de documentos (palabras clave específicas)
        generation_keywords = [
            'cloudformation', 'tabla de actividades', 'diagrama de arquitectura',
            'documento word', 'costos estimados', 'calculadora aws',
            'script cloudformation', 'archivo csv', 'genero los siguientes'
        ]
        
        if any(keyword in response_lower for keyword in generation_keywords):
            documents_generated = [
                'CloudFormation Template', 
                'Tabla de Actividades', 
                'Diagrama de Arquitectura',
                'Documento de Proyecto', 
                'Analisis de Costos', 
                'Guia Calculadora AWS'
            ]
            mcp_services_used = ['documents', 'diagram', 'pricing']
        
        # Detectar uso de MCP services
        if any(keyword in response_lower for keyword in ['diagrama', 'arquitectura']):
            if 'diagram' not in mcp_services_used:
                mcp_services_used.append('diagram')
        if any(keyword in response_lower for keyword in ['costo', 'precio', 'presupuesto']):
            if 'pricing' not in mcp_services_used:
                mcp_services_used.append('pricing')
        if any(keyword in response_lower for keyword in ['documento', 'archivo', 'generar']):
            if 'documents' not in mcp_services_used:
                mcp_services_used.append('documents')
        
        # Respuesta estructurada
        result = {
            'response': ai_response,
            'modelId': selected_model,
            'mode': 'arquitecto-maestro',
            'timestamp': datetime.now().isoformat(),
            'mcpServicesUsed': mcp_services_used,
            'documentsGenerated': documents_generated if documents_generated else None,
            'projectId': str(uuid.uuid4()) if documents_generated else None,
            'projectName': 'Proyecto AWS' if documents_generated else None
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({'error': str(e)})
        }
