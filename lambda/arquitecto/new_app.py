import json
import boto3
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any
import logging

# Import simple intelligent generator with validation
from generators.simple_intelligent_generator import (
    extract_project_parameters,
    create_intelligent_messages,
    process_intelligent_response_with_validation,
    generate_specific_documents
)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ.get('REGION', 'us-east-1'))
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('REGION', 'us-east-1'))
s3 = boto3.client('s3', region_name=os.environ.get('REGION', 'us-east-1'))

# Get table and bucket names from environment
PROJECTS_TABLE = os.environ.get('PROJECTS_TABLE')
DOCUMENTS_BUCKET = os.environ.get('DOCUMENTS_BUCKET')

projects_table = dynamodb.Table(PROJECTS_TABLE) if PROJECTS_TABLE else None

def lambda_handler(event, context):
    """
    AWS Lambda handler for arquitecto functionality - AWS Propuestas v3
    SIMPLE INTELLIGENT SYSTEM - No generic content
    """
    try:
        # Handle CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return create_response(200, {})
        
        # Parse the request
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event
        
        # Extract parameters
        action = body.get('action', 'chat')
        project_id = body.get('projectId', str(uuid.uuid4()))
        user_id = body.get('userId', 'anonymous')
        
        logger.info(f"🎯 SIMPLE INTELLIGENT ARQUITECTO V3 - Action: {action}, Project: {project_id}")
        
        # Default chat functionality with intelligent system
        return process_intelligent_arquitecto_chat(body, context)
        
    except Exception as e:
        logger.error(f"Error in arquitecto handler: {str(e)}")
        return create_response(500, {
            'error': 'Internal server error',
            'details': str(e)
        })

def process_intelligent_arquitecto_chat(body: Dict, context) -> Dict:
    """Process chat with simple intelligent system - No generic content"""
    
    try:
        messages = body.get('messages', [])
        model_id = body.get('modelId', 'anthropic.claude-3-haiku-20240307-v1:0')
        project_id = body.get('projectId', str(uuid.uuid4()))
        user_id = body.get('userId', 'anonymous')
        project_info = body.get('projectInfo', {})
        
        if not messages:
            return create_response(400, {'error': 'Messages are required'})
        
        logger.info(f"🎯 SIMPLE INTELLIGENT ARCHITECT - Project: {project_id}")
        logger.info(f"Messages count: {len(messages)}")
        
        # Extract specific parameters from conversation
        project_params = extract_project_parameters(messages, "", project_info)
        servicio = project_params['servicio']
        descripcion = project_params['descripcion'] 
        objetivo = project_params['objetivo']
        
        logger.info(f"🔍 EXTRACTED PARAMS - Service: {servicio}, Description: {descripcion[:50]}...")
        
        # Check if we have enough information to generate documents
        has_enough_info = len(descripcion) > 30 and servicio != "AWS"
        
        if has_enough_info:
            # Generate documents immediately with specific parameters
            logger.info(f"✅ SUFFICIENT INFO - Generating documents for {servicio}")
            
            # Create intelligent messages for document generation
            intelligent_messages = create_intelligent_messages(servicio, descripcion, objetivo)
            
            # Prepare prompt for Bedrock
            prompt_body = prepare_prompt_for_model(model_id, "", intelligent_messages)
            
            # Call Bedrock for document generation
            response = bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(prompt_body),
                contentType='application/json'
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            ai_response, usage = extract_response(model_id, response_body)
            
            if not ai_response:
                logger.error(f"Empty response from model {model_id}")
                return create_response(500, {
                    'error': 'Empty response from AI model',
                    'modelId': model_id
                })
            
            # Process intelligent response with validation
            document_results = process_intelligent_response_with_validation(
                ai_response, servicio, descripcion, objetivo
            )
            
            # Generate and upload documents to S3
            document_generation_results = generate_specific_documents(
                document_results, 
                project_id, 
                user_id, 
                servicio
            )
            
            # Create final response with document generation confirmation
            quality_score = document_results.get('quality_score', 0)
            validation_info = document_results.get('validation', {})
            
            final_response = f"""✅ **PROPUESTA COMPLETADA PARA {servicio.upper()}**

He analizado tu proyecto: "{descripcion}"

**Objetivo identificado:** {objetivo}

**Calidad de la respuesta:** {quality_score}/100 puntos

**Documentos generados específicamente para {servicio}:**

📄 **Propuesta Ejecutiva** - Documento profesional con análisis específico de {servicio}
🔧 **Documento Técnico** - Arquitectura detallada centrada en {servicio}  
📊 **Plan de Implementación** - Actividades específicas para {servicio}
💰 **Estimación de Costos** - Costos reales de {servicio} y servicios complementarios
🏗️ **CloudFormation Template** - Infraestructura como código para {servicio}
📈 **Guía de Calculadora AWS** - Pasos específicos para estimar costos de {servicio}

**Todos los documentos están adaptados específicamente a tu caso de uso, no son genéricos.**

Los documentos están disponibles en la sección de **Proyectos** para descarga."""
            
            if validation_info.get('issues'):
                final_response += f"\n\n⚠️ **Nota de calidad:** {', '.join(validation_info['issues'][:2])}"
            
            final_response += f"\n\n¿Te gustaría que ajuste algún aspecto específico de la solución con {servicio}?"
            
            # Save project data
            project_info.update({
                'name': f"Proyecto {servicio}",
                'service_focus': servicio,
                'description': descripcion,
                'objective': objetivo,
                'status': 'COMPLETED',
                'quality_score': quality_score
            })
            
            save_conversation_data(project_id, user_id, messages, final_response, project_info)
            
            return create_response(200, {
                'response': final_response,
                'projectId': project_id,
                'projectInfo': project_info,
                'isComplete': True,
                'usage': usage,
                'modelId': model_id,
                'documentGeneration': document_generation_results,
                'specificService': servicio,
                'qualityScore': quality_score
            })
        
        else:
            # Continue conversation to gather more specific information
            logger.info(f"❓ NEED MORE INFO - Current service: {servicio}")
            
            # Create conversational prompt to gather specific information
            conversation_prompt = f"""Eres un Arquitecto de Soluciones AWS experto. Tu objetivo es entender exactamente qué necesita el cliente para generar una propuesta específica y profesional.

INFORMACIÓN ACTUAL:
- Servicio detectado: {servicio}
- Descripción: {descripcion}
- Objetivo: {objetivo}

INSTRUCCIONES:
1. Si la información es muy general, haz preguntas específicas para entender:
   - ¿Qué servicio AWS específico necesita?
   - ¿Cuál es el caso de uso exacto?
   - ¿Cuál es el objetivo de negocio?

2. Una vez que tengas información específica, confirma que procederás a generar los documentos.

3. Mantén un tono profesional y conversacional.

Responde al último mensaje del usuario de manera natural y específica."""
            
            # Prepare messages for conversation
            conversation_messages = [
                {"role": "system", "content": conversation_prompt}
            ] + messages
            
            # Prepare prompt for Bedrock
            prompt_body = prepare_prompt_for_model(model_id, "", conversation_messages)
            
            # Call Bedrock
            response = bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(prompt_body),
                contentType='application/json'
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            ai_response, usage = extract_response(model_id, response_body)
            
            if not ai_response:
                logger.error(f"Empty response from model {model_id}")
                return create_response(500, {
                    'error': 'Empty response from AI model',
                    'modelId': model_id
                })
            
            # Update project info with current parameters
            project_info.update({
                'service_focus': servicio,
                'description': descripcion,
                'objective': objetivo,
                'status': 'IN_PROGRESS'
            })
            
            save_conversation_data(project_id, user_id, messages, ai_response, project_info)
            
            return create_response(200, {
                'response': ai_response,
                'projectId': project_id,
                'projectInfo': project_info,
                'isComplete': False,
                'usage': usage,
                'modelId': model_id,
                'detectedService': servicio
            })
        
    except Exception as e:
        logger.error(f"Error in simple intelligent arquitecto: {str(e)}")
        return create_response(500, {
            'error': 'Failed to process chat',
            'details': str(e)
        })

def prepare_prompt_for_model(model_id: str, system_prompt: str, messages: List[Dict]) -> Dict:
    """
    Prepara el prompt para diferentes modelos de Bedrock
    """
    if model_id.startswith('anthropic.claude'):
        # Claude format
        formatted_messages = []
        
        # Add system message if provided
        if system_prompt:
            formatted_messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # Add conversation messages
        for msg in messages:
            if msg.get('content'):
                formatted_messages.append({
                    "role": msg.get('role', 'user'),
                    "content": msg.get('content')
                })
        
        return {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "messages": formatted_messages
        }
    
    elif model_id.startswith('amazon.nova'):
        # Nova format
        formatted_messages = []
        
        # Add system message if provided
        if system_prompt:
            formatted_messages.append({
                "role": "system",
                "content": [{"text": system_prompt}]
            })
        
        # Add conversation messages
        for msg in messages:
            if msg.get('content'):
                formatted_messages.append({
                    "role": msg.get('role', 'user'),
                    "content": [{"text": msg.get('content')}]
                })
        
        return {
            "messages": formatted_messages,
            "inferenceConfig": {
                "maxTokens": 4000,
                "temperature": 0.7
            }
        }
    
    else:
        # Default format
        return {
            "messages": messages,
            "max_tokens": 4000
        }

def extract_response(model_id: str, response_body: Dict) -> tuple:
    """Extract AI response and usage from response body"""
    
    ai_response = ""
    usage = {}
    
    if model_id.startswith('anthropic.claude'):
        ai_response = response_body.get('content', [{}])[0].get('text', '')
        usage = {
            'inputTokens': response_body.get('usage', {}).get('input_tokens'),
            'outputTokens': response_body.get('usage', {}).get('output_tokens'),
            'totalTokens': response_body.get('usage', {}).get('input_tokens', 0) + response_body.get('usage', {}).get('output_tokens', 0)
        }
    elif model_id.startswith('amazon.nova'):
        ai_response = response_body.get('output', {}).get('message', {}).get('content', [{}])[0].get('text', '')
        usage = {
            'inputTokens': response_body.get('usage', {}).get('inputTokens'),
            'outputTokens': response_body.get('usage', {}).get('outputTokens'),
            'totalTokens': response_body.get('usage', {}).get('totalTokens')
        }
    else:
        ai_response = response_body.get('content', '')
    
    return ai_response, usage

def save_conversation_data(project_id: str, user_id: str, messages: List[Dict], ai_response: str, project_info: Dict):
    """
    Guarda los datos de la conversación en DynamoDB
    """
    try:
        if not projects_table:
            logger.warning("Projects table not configured")
            return
        
        # Update project in DynamoDB
        projects_table.put_item(
            Item={
                'projectId': project_id,
                'userId': user_id,
                'projectInfo': project_info,
                'lastMessage': ai_response[:500],  # Truncate for storage
                'messageCount': len(messages),
                'lastUpdated': datetime.utcnow().isoformat(),
                'status': project_info.get('status', 'IN_PROGRESS')
            }
        )
        
        logger.info(f"💾 Saved conversation data for project: {project_id}")
        
    except Exception as e:
        logger.error(f"Error saving conversation data: {str(e)}")

def create_response(status_code: int, body: Dict) -> Dict:
    """
    Crea respuesta HTTP con headers CORS
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With'
        },
        'body': json.dumps(body, ensure_ascii=False, default=str)
    }
