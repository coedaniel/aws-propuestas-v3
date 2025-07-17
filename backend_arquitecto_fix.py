import json
import boto3
import os
from datetime import datetime
import uuid

# Cliente Bedrock
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')

# Prompt maestro completo
PROMPT_MAESTRO = """
Actua como arquitecto de soluciones AWS y consultor experto. Vamos a dimensionar, documentar y entregar una solucion profesional en AWS, siguiendo mejores practicas y generando todos los archivos necesarios para una propuesta ejecutiva. No uses acentos ni caracteres especiales en ningun texto, archivo, script ni documento.

IMPORTANTE: Sigue este flujo paso a paso:

1. Primero pregunta: Cual es el nombre del proyecto

2. Despues pregunta: El proyecto es una solucion integral (como migracion, aplicacion nueva, modernizacion, analitica, seguridad, IA, IoT, data lake, networking, DRP, VDI, integracion, etc.) o es un servicio rapido especifico (implementacion de instancias EC2, RDS, SES, VPN, ELB, S3, VPC, CloudFront, SSO, backup, etc.)

3. Haz MUCHAS preguntas detalladas una por una para capturar toda la informacion necesaria

4. SOLO al final, cuando tengas TODA la informacion, genera los documentos:
- Tabla de actividades de implementacion (CSV)
- Script CloudFormation para desplegar
- Diagrama de arquitectura
- Documento Word con descripcion completa
- Archivo de costos estimados (CSV)
- Guia para calculadora AWS

NO generes documentos hasta tener toda la informacion completa del proyecto.
Pregunta una cosa a la vez. Se detallado y minucioso.
"""

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
        
        # Detectar MCP services
        response_lower = ai_response.lower()
        mcp_services_used = []
        
        if any(keyword in response_lower for keyword in ['diagrama', 'arquitectura']):
            mcp_services_used.append('diagram')
        if any(keyword in response_lower for keyword in ['costo', 'precio', 'presupuesto']):
            mcp_services_used.append('pricing')
        if any(keyword in response_lower for keyword in ['documento', 'archivo']):
            mcp_services_used.append('documents')
        
        # SOLO generar documentos si dice explícitamente que los está generando
        documents_generated = None
        project_id = None
        project_name = None
        
        # Palabras clave MUY específicas para detectar generación real
        generation_phrases = [
            'genero los siguientes documentos',
            'he generado los documentos',
            'documentos generados exitosamente',
            'archivos creados',
            'tabla de actividades generada',
            'script cloudformation creado'
        ]
        
        if any(phrase in response_lower for phrase in generation_phrases):
            documents_generated = [
                'CloudFormation Template', 
                'Tabla de Actividades', 
                'Diagrama de Arquitectura',
                'Documento de Proyecto', 
                'Analisis de Costos', 
                'Guia Calculadora AWS'
            ]
            project_id = str(uuid.uuid4())
            project_name = 'Proyecto AWS'
        
        # Respuesta estructurada
        result = {
            'response': ai_response,
            'modelId': selected_model,
            'mode': 'arquitecto-maestro',
            'timestamp': datetime.now().isoformat(),
            'mcpServicesUsed': mcp_services_used,
            'documentsGenerated': documents_generated,
            'projectId': project_id,
            'projectName': project_name
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
