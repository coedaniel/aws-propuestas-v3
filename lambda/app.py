import json
import boto3
import uuid
from botocore.exceptions import ClientError

# Configuración del cliente Bedrock Agent Runtime
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

# Configuración de agentes duales
AGENTS_CONFIG = {
    'nova': {
        'agent_id': 'WUGHP2HGH9',
        'agent_alias_id': 'ZNZ3SYTP5L',
        'model': 'amazon.nova-pro-v1:0',
        'name': 'Nova Pro',
        'specialization': 'multimodal',
        'description': 'Ideal para diagramas, análisis visual y contenido multimodal'
    },
    'claude': {
        'agent_id': 'W3YRJXXIRE',
        'agent_alias_id': 'ULPAGJS0VW',
        'model': 'anthropic.claude-3-5-sonnet-20240620-v1:0',
        'name': 'Claude 3.5 Sonnet',
        'specialization': 'analysis',
        'description': 'Ideal para análisis técnico profundo y documentación detallada'
    }
}

def lambda_handler(event, context):
    """
    Función Lambda principal que maneja las solicitudes usando agentes duales
    """
    try:
        # Manejar CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return handle_options()
        
        # Parsear el cuerpo de la solicitud
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        # Extraer información del proyecto y modelo seleccionado
        project_info = body.get('project_info', {})
        user_query = body.get('query', '')
        selected_model = body.get('selected_model', 'nova')  # Default: Nova Pro
        session_id = body.get('session_id', str(uuid.uuid4()))
        
        print(f"Procesando solicitud para proyecto: {project_info.get('name', 'Sin nombre')}")
        print(f"Query del usuario: {user_query}")
        print(f"Modelo seleccionado: {selected_model}")
        print(f"Session ID: {session_id}")
        
        # Validar modelo seleccionado
        if selected_model not in AGENTS_CONFIG:
            selected_model = 'nova'  # Fallback a Nova Pro
        
        # Obtener configuración del agente
        agent_config = AGENTS_CONFIG[selected_model]
        
        # Preparar el mensaje para el agente
        if project_info:
            input_text = f"""Necesito generar una propuesta profesional para el siguiente proyecto AWS:

Información del proyecto:
- Nombre: {project_info.get('name', 'No especificado')}
- Descripción: {project_info.get('description', 'No especificada')}
- Servicios AWS requeridos: {', '.join(project_info.get('services', []))}
- Objetivo: {project_info.get('objective', 'No especificado')}
- Requerimientos: {project_info.get('requirements', 'No especificados')}

Por favor genera:
1. Una propuesta ejecutiva profesional
2. Un diagrama de arquitectura AWS
3. Un template CloudFormation
4. Una estimación de costos

{user_query}"""
        else:
            input_text = user_query
        
        # Invocar el agente seleccionado
        response = invoke_bedrock_agent(
            agent_id=agent_config['agent_id'],
            agent_alias_id=agent_config['agent_alias_id'],
            session_id=session_id,
            input_text=input_text,
            model_info=agent_config
        )
        
        # Procesar la respuesta
        result = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({
                'message': 'Propuesta generada exitosamente',
                'session_id': session_id,
                'selected_model': selected_model,
                'model_info': agent_config,
                'response': response,
                'project_id': project_info.get('name', 'proyecto-' + str(uuid.uuid4())[:8]),
                'hasDocuments': True
            })
        }
        
        return result
        
    except Exception as e:
        print(f"Error en lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': f'Error interno del servidor: {str(e)}',
                'hasDocuments': False
            })
        }

def invoke_bedrock_agent(agent_id, agent_alias_id, session_id, input_text, model_info):
    """
    Invocar el agente de Bedrock usando la API InvokeAgent
    """
    try:
        print(f"Invocando agente {model_info['name']} ({agent_id}) con alias {agent_alias_id}")
        print(f"Especialización: {model_info['specialization']}")
        print(f"Texto de entrada: {input_text[:200]}...")
        
        # Llamar a la API InvokeAgent
        response = bedrock_agent_runtime.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=session_id,
            inputText=input_text,
            enableTrace=True  # Habilitar trazas para debugging
        )
        
        print("Respuesta recibida del agente")
        
        # Procesar la respuesta streaming
        agent_response = ""
        trace_data = []
        
        # La respuesta es un stream, necesitamos procesarla
        event_stream = response['completion']
        
        for event in event_stream:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    # Decodificar los bytes de la respuesta
                    chunk_data = json.loads(chunk['bytes'].decode('utf-8'))
                    if 'completion' in chunk_data:
                        agent_response += chunk_data['completion']
                    
            elif 'trace' in event:
                # Capturar información de trazas para debugging
                trace_data.append(event['trace'])
        
        return {
            'agent_response': agent_response,
            'model_used': model_info['name'],
            'model_specialization': model_info['specialization'],
            'trace_data': trace_data if trace_data else None,
            'session_id': session_id
        }
        
    except Exception as e:
        print(f"Error invocando agente {model_info['name']}: {str(e)}")
        raise e

def get_available_models():
    """
    Obtener información de los modelos disponibles
    """
    return {
        'models': AGENTS_CONFIG,
        'default': 'nova'
    }

# Función para manejar OPTIONS (CORS)
def handle_options():
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': ''
    }

# Endpoint adicional para obtener información de modelos
def get_models_info(event, context):
    """
    Endpoint para obtener información de los modelos disponibles
    """
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(get_available_models())
    }
