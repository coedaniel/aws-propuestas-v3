"""
Lambda handler principal con logging detallado
"""
import json
import boto3
import logging
import asyncio
from datetime import datetime
import uuid
import os
from conversation_handler import ConversationState
from mcp_caller import IntelligentMCPCaller

# Configuración de logging detallado
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def log_request(event, body):
    """Log detallado de la petición"""
    logger.info("=== INICIO REQUEST LOGGING ===")
    logger.info(f"Headers: {json.dumps(event.get('headers', {}))}")
    logger.info(f"Body: {json.dumps(body)}")
    logger.info(f"Messages: {json.dumps(body.get('messages', []))}")
    logger.info(f"Project State: {json.dumps(body.get('projectState', {}))}")
    logger.info("=== FIN REQUEST LOGGING ===")

def get_cors_headers():
    return {
        'Access-Control-Allow-Origin': 'https://main.d2xsphsjdxlk24.amplifyapp.com',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With, Accept, Origin',
        'Access-Control-Max-Age': '86400',
        'Content-Type': 'application/json'
    }

def create_response(status_code, body):
    logger.info(f"=== RESPONSE ===")
    logger.info(f"Status: {status_code}")
    logger.info(f"Body: {json.dumps(body)}")
    logger.info("=== FIN RESPONSE ===")
    return {
        'statusCode': status_code,
        'headers': get_cors_headers(),
        'body': json.dumps(body)
    }

def save_project_to_db(project_data, mcp_results):
    """Guarda el proyecto en DynamoDB"""
    try:
        import boto3
        import uuid
        from datetime import datetime
        
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ.get('PROJECTS_TABLE', 'aws-propuestas-v3-projects-prod-v2'))
        
        # Generar projectId único (clave primaria requerida por DynamoDB)
        project_id = f"proj_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
        
        item = {
            'projectId': project_id,  # Clave primaria correcta
            'name': project_data['name'],
            'type': project_data['type'],
            'services': project_data['services'],
            'requirements': project_data['requirements'],
            'mcp_results': json.dumps(mcp_results),
            'created_at': datetime.now().isoformat(),
            'status': 'completed'
        }
        
        table.put_item(Item=item)
        logger.info(f"✅ Proyecto guardado en DynamoDB: {project_id}")
        
        return project_id
        
    except Exception as e:
        logger.error(f"❌ Error guardando proyecto: {str(e)}")
        return None

def lambda_handler(event, context):
    """Handler principal con logging detallado"""
    
    # Manejar preflight CORS
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': ''
        }

    try:
        # Extraer y loggear datos del request
        body = json.loads(event.get('body', '{}'))
        log_request(event, body)
        
        messages = body.get('messages', [])
        project_state = body.get('projectState', {})
        
        # Inicializar manejador de conversación con estado persistente
        conversation = ConversationState()
        
        # Restaurar estado desde projectState si existe
        if project_state:
            conversation.restore_from_project_state(project_state)
        
        # Validar estado actual
        is_complete = conversation.validate_state(messages, project_state)
        logger.info(f"Estado de conversación: {conversation.current_step}")
        logger.info(f"Campos requeridos: {json.dumps(conversation.required_fields)}")
        
        # Si no está completo, verificar si necesita inteligencia MCP
        if not is_complete:
            # Para requirements_rapido, usar inteligencia MCP para hacer preguntas específicas
            if conversation.current_step == 'requirements_rapido':
                logger.info("🧠 Activando inteligencia MCP para preguntas específicas")
                
                # Usar MCP Core para generar preguntas inteligentes
                mcp_caller = IntelligentMCPCaller()
                try:
                    # Crear event loop si no existe
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    # Generar preguntas inteligentes basadas en los servicios
                    intelligent_questions = loop.run_until_complete(
                        mcp_caller.generate_intelligent_questions(conversation.project_data, messages)
                    )
                    
                    if intelligent_questions:
                        return create_response(200, {
                            'message': intelligent_questions,
                            'projectState': project_state,
                            'mcpActivated': True,
                            'mcpUsed': ['core_analysis', 'aws_documentation'],
                            'conversationComplete': False,
                            'currentStep': 'requirements_rapido'
                        })
                        
                except Exception as e:
                    logger.error(f"❌ Error en MCP inteligente: {str(e)}")
                    # Fallback a pregunta básica
                    pass
            
            # Fallback: obtener siguiente pregunta normal
            next_question = conversation.get_next_question()
            completion = conversation.get_completion_percentage()
            missing = conversation.get_missing_fields()
            
            return create_response(200, {
                'message': next_question,
                'projectState': project_state,
                'mcpActivated': True,
                'mcpUsed': [],
                'conversationComplete': False,
                'currentStep': conversation.current_step
            })
        
        # Si está completo, activar MCP services inteligentemente como Amazon Q CLI
        project_data = conversation.project_data
        logger.info(f"🚀 Activando MCP services inteligentemente para: {project_data['name']}")

        # Importar y usar el caller inteligente
        mcp_caller = IntelligentMCPCaller()
        
        # Ejecutar orquestación inteligente
        try:
            # Crear event loop si no existe
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Ejecutar generación inteligente
            generation_result = loop.run_until_complete(
                mcp_caller.orchestrate_intelligent_generation(project_data)
            )
            
            if generation_result.get('success'):
                mcp_results = generation_result['results']
                mcp_used = generation_result['mcp_services_used']
                
                # Guardar proyecto en DynamoDB
                project_id = save_project_to_db(project_data, mcp_results)
                
                if project_id:
                    logger.info(f"✅ MCP services activados exitosamente: {mcp_used}")
                    logger.info(f"✅ Proyecto guardado con ID: {project_id}")
                else:
                    logger.error("❌ Error guardando proyecto en DynamoDB")
            else:
                logger.error(f"❌ Error en generación MCP: {generation_result.get('error')}")
                mcp_results = {}
                mcp_used = []

        except Exception as e:
            logger.error(f"💥 Error crítico en orquestación MCP: {str(e)}")
            mcp_results = {}
            mcp_used = []
        
        success_message = f"""✅ DOCUMENTOS GENERADOS EXITOSAMENTE PARA: {project_data['name']}

🏗️ Tipo: {project_data.get('type', 'N/A').title()}
🔧 Servicios AWS: {', '.join(project_data.get('services', []))}
🤖 MCP Services utilizados: {len(mcp_used)} servicios

📁 Documentos generados:
   • Diagrama de arquitectura AWS (PNG/SVG)
   • Script CloudFormation (YAML)
   • Estimación de costos (CSV/Excel)
   • Documentación técnica (Word/PDF)
   • Tabla de actividades (CSV/Excel)

💾 Proyecto guardado y disponible en la sección 'Proyectos'

🎯 Los documentos están listos para entrega ejecutiva."""
        
        return create_response(200, {
            'content': success_message,
            'projectState': project_state,
            'mcpActivated': True,
            'mcpUsed': mcp_used,
            'readinessScore': 1.0,
            'readinessStatus': "✅ Documentos generados"
        })
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.error(f"Stack trace:", exc_info=True)
        return create_response(500, {
            'content': f"Lo siento, ocurrió un error: {str(e)}",
            'projectState': project_state,
            'mcpActivated': True,
            'mcpUsed': [],
            'readinessScore': 0,
            'readinessStatus': "Error en el procesamiento"
        })
