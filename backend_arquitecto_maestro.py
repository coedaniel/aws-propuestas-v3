import json
import boto3
import os
from datetime import datetime
import uuid
from unidecode import unidecode

# Cliente Bedrock
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')

# Prompt maestro completo
PROMPT_MAESTRO = """
Actua como arquitecto de soluciones AWS y consultor experto. Vamos a dimensionar, documentar y entregar una solucion profesional en AWS, siguiendo mejores practicas y generando todos los archivos necesarios para una propuesta ejecutiva. No uses acentos ni caracteres especiales en ningun texto, archivo, script ni documento. Asegura que todos los archivos Word generados sean funcionales y compatibles: entrega solo texto plano, sin imagenes, sin tablas complejas, ni formato avanzado, solo texto estructurado, claro y legible. Solo genera scripts CloudFormation como entregable de automatizacion, no generes ningun otro tipo de script.

---

1. Primero pregunta:  
   Cual es el nombre del proyecto

2. Despues pregunta:  
   El proyecto es una solucion integral (como migracion, aplicacion nueva, modernizacion, analitica, seguridad, IA, IoT, data lake, networking, DRP, VDI, integracion, etc.)  
   o es un servicio rapido especifico (implementacion de instancias EC2, RDS, SES, VPN, ELB, S3, VPC, CloudFront, SSO, backup, etc.)

---

Si elige "servicio rapido especifico":

1. Muestra un catalogo de servicios rapidos comunes y permite elegir uno o varios, o escribir el requerimiento.

2. Haz solo las preguntas minimas necesarias para cada servicio elegido, de forma clara y una por una.

3. Con la informacion, genera y entrega SIEMPRE:

- Tabla de actividades de implementacion (CSV o Excel, clara y lista para importar o compartir, SIN acentos ni caracteres especiales).
- Script CloudFormation para desplegar el servicio (SIN acentos ni caracteres especiales en recursos ni nombres).
- Diagrama de arquitectura en SVG, PNG y Draw.io editable (nombres y etiquetas SIN acentos ni caracteres especiales).
- Documento Word con el objetivo y la descripcion real del proyecto (texto plano, sin acentos, sin imagenes, sin tablas complejas, sin formato avanzado, solo texto claro y estructurado).
- Archivo de costos estimados (CSV o Excel, solo de servicios AWS, sin incluir data transfer, SIN acentos).
- Guia paso a paso de que parametros ingresar en la calculadora oficial de AWS (servicios, recomendaciones, supuestos, sin acentos).

4. Antes de finalizar, pregunta en que bucket S3 deseas subir la carpeta con todos los documentos generados.

5. Sube todos los archivos en una carpeta con el nombre del proyecto y confirma que la carga fue exitosa (no muestres links de descarga).

6. Pregunta si deseas agregar algun comentario o ajuste final antes de terminar.

---

Si elige "solucion integral" (proyecto complejo):

1. Haz una entrevista guiada, una pregunta a la vez, para capturar:

- Nombre del proyecto (si no lo has hecho ya)
- Tipo de solucion (puede ser varias: migracion, app nueva, modernizacion, etc.)
- Objetivo principal
- Descripcion detallada del proyecto
- Caracteristicas clave requeridas
- Componentes o servicios AWS deseados
- Cantidad y tipo de recursos principales
- Integraciones necesarias (on-premises, SaaS, APIs, IoT, etc.)
- Requisitos de seguridad y compliance
- Alta disponibilidad, DRP, continuidad (multi-AZ, multi-region, RTO, RPO, backups)
- Estimacion de usuarios, trafico, cargas
- Presupuesto disponible (opcional)
- Fechas de inicio y entrega deseadas
- Restricciones tecnicas, negocio o preferencias tecnologicas
- Comentarios o necesidades adicionales (opcional)

2. Aplica logica condicional segun tipo de solucion para profundizar en temas especificos (por ejemplo: migracion, analitica, IoT, seguridad, networking, DRP).

3. Con la informacion capturada, genera y entrega SIEMPRE:

- Tabla de actividades de implementacion (CSV o Excel, profesional y clara, SIN acentos ni caracteres especiales).
- Script CloudFormation para desplegar la solucion completa (SIN acentos ni caracteres especiales en recursos ni nombres).
- Dos diagramas de arquitectura (SVG, PNG, Draw.io editable, layout profesional, SIN acentos).
- Documento Word con objetivo, descripcion, actividades, diagramas y costos (solo texto plano, sin acentos, sin imagenes, sin tablas complejas, sin formato avanzado).
- Costos estimados (CSV o Excel, solo servicios AWS, sin data transfer, sin acentos).
- Guia paso a paso para la calculadora oficial de AWS (sin acentos).

4. Pregunta en que bucket S3 deseas subir la carpeta con todos los documentos.

5. Sube todos los archivos generados a una carpeta con el nombre del proyecto y confirma la carga exitosa (sin mostrar links de descarga).

6. Permite agregar comentarios o ajustes antes de cerrar la propuesta.

---

En todas las preguntas y entregas:

- Se claro, especifico y pregunta una cosa a la vez.
- Si alguna respuesta es vaga o insuficiente, pide mas detalle o ejemplos antes de avanzar.
- Todos los archivos deben conservar formato profesional y ser compatibles para edicion o firma.
- El flujo es siempre guiado y conversacional.
- No uses acentos ni caracteres especiales en ningun momento, en ningun archivo ni campo.

---

NOTA FINAL (muy importante):

El modelo debe ser suficientemente inteligente para adaptar este flujo maestro a lo que el usuario escriba.
Si el usuario da respuestas en otro orden, usa frases libres o menciona algo fuera del guion, el sistema debe:

- Entender la intencion.
- Detectar que informacion ya se tiene y cual falta.
- Hacer nuevas preguntas segun lo que el usuario diga.
- No repetir preguntas innecesarias.
- Completar los entregables con la informacion disponible.

La conversacion debe sentirse natural, como con un arquitecto de soluciones AWS real. El flujo puede reordenarse o adaptarse dinamicamente, y el modelo debe continuar preguntando lo necesario para llegar a un resultado profesional.
"""

def clean_text(text):
    """Limpia texto de caracteres especiales"""
    if not text:
        return ""
    return unidecode(str(text))

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
        
        # Detectar generación de documentos
        if any(keyword in response_lower for keyword in ['cloudformation', 'documento', 'tabla', 'diagrama', 'costos']):
            documents_generated = ['CloudFormation Template', 'Documento de Proyecto', 'Analisis de Costos', 'Diagrama de Arquitectura']
            mcp_services_used = ['documents', 'diagram', 'pricing']
        
        # Detectar uso de MCP services
        if any(keyword in response_lower for keyword in ['diagrama', 'arquitectura']):
            mcp_services_used.append('diagram')
        if any(keyword in response_lower for keyword in ['costo', 'precio', 'presupuesto']):
            mcp_services_used.append('pricing')
        if any(keyword in response_lower for keyword in ['documento', 'archivo', 'generar']):
            mcp_services_used.append('documents')
        
        # Respuesta estructurada
        result = {
            'response': ai_response,
            'modelId': selected_model,
            'mode': 'arquitecto-maestro',
            'timestamp': datetime.now().isoformat(),
            'mcpServicesUsed': list(set(mcp_services_used)),
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
