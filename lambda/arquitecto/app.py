"""
Amazon Q CLI Intelligent Architect - Lambda handler principal
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

def save_project_to_db(project_data, analysis_results):
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
            'name': project_data.get('name', 'Proyecto sin nombre'),
            'type': 'intelligent_analysis',
            'analysis_results': json.dumps(analysis_results),
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
    """Handler principal con análisis inteligente completo"""
    
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
        
        # Inicializar manejador de conversación inteligente
        conversation = ConversationState()
        
        # Restaurar estado desde projectState si existe
        if project_state:
            conversation.restore_from_project_state(project_state)
        
        # Verificar si debe activar análisis inteligente completo
        should_analyze = conversation.should_trigger_intelligent_analysis(messages, project_state)
        
        if should_analyze:
            logger.info("🧠 ACTIVANDO ANÁLISIS INTELIGENTE COMPLETO")
            
            # Mostrar prompt de análisis inteligente
            analysis_prompt = conversation.get_intelligent_analysis_prompt()
            
            # Activar MCP services inteligentemente como Amazon Q CLI
            mcp_caller = IntelligentMCPCaller()
            
            try:
                # Crear event loop si no existe
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # Ejecutar análisis inteligente completo
                intelligent_results = loop.run_until_complete(
                    mcp_caller.execute_intelligent_analysis(conversation.project_data, messages, project_state)
                )
                
                if intelligent_results:
                    # Marcar análisis como completo
                    conversation.analysis_complete = True
                    project_state['analysis_complete'] = True
                    project_state['system_analysis'] = intelligent_results
                    
                    # Guardar proyecto en DB
                    project_id = save_project_to_db(conversation.project_data, intelligent_results)
                    
                    return create_response(200, {
                        'message': intelligent_results.get('final_response', analysis_prompt),
                        'projectState': project_state,
                        'mcpActivated': True,
                        'mcpUsed': intelligent_results.get('mcp_services_used', []),
                        'conversationComplete': True,
                        'projectId': project_id,
                        'systemAnalysis': intelligent_results
                    })
                    
            except Exception as e:
                logger.error(f"❌ Error en análisis inteligente: {str(e)}")
                # Fallback: mostrar prompt de análisis
                return create_response(200, {
                    'message': analysis_prompt,
                    'projectState': project_state,
                    'mcpActivated': True,
                    'mcpUsed': [],
                    'conversationComplete': False,
                    'currentStep': 'intelligent_analysis'
                })
        
        # Si no necesita análisis inteligente, usar flujo básico
        if not conversation.is_ready_to_generate():
            return create_response(200, {
                'message': "¿Cuál es el nombre del proyecto?",
                'projectState': project_state,
                'mcpActivated': False,
                'mcpUsed': [],
                'conversationComplete': False,
                'currentStep': 'name'
            })
        
        # Si está completo, generar documentos finales
        project_data = conversation.project_data
        logger.info(f"🚀 Generando documentos finales para: {project_data.get('name', 'Proyecto')}")

        # Importar y usar el caller inteligente para generación final
        mcp_caller = IntelligentMCPCaller()
        
        try:
            # Crear event loop si no existe
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Ejecutar orquestación inteligente final
            results = loop.run_until_complete(
                mcp_caller.orchestrate_intelligent_generation(project_data)
            )
            
            # Guardar proyecto en DB
            project_id = save_project_to_db(project_data, results)
            
            return create_response(200, {
                'message': results.get('summary', 'Documentos generados exitosamente'),
                'projectState': project_state,
                'mcpActivated': True,
                'mcpUsed': results.get('mcp_services_used', []),
                'conversationComplete': True,
                'projectId': project_id,
                'results': results
            })
            
        except Exception as e:
            logger.error(f"❌ Error en generación final: {str(e)}")
            return create_response(500, {
                'message': f'Error generando documentos: {str(e)}',
                'projectState': project_state,
                'mcpActivated': False,
                'mcpUsed': [],
                'conversationComplete': False
            })
        
    except Exception as e:
        logger.error(f"❌ Error general: {str(e)}")
        return create_response(500, {
            'message': f'Error interno del servidor: {str(e)}',
            'mcpActivated': False,
            'mcpUsed': [],
            'conversationComplete': False
        })
