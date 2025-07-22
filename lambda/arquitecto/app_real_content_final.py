"""
Parte final del archivo app_real_content.py con lambda_handler
"""

def prepare_conversation(messages: List[Dict], project_state: Dict) -> List[Dict]:
    """Prepare conversation for Bedrock with correct format"""
    conversation = []
    
    # Add system message with correct format (as user message for Bedrock)
    conversation.append({
        "role": "user",
        "content": [{"text": PROMPT_MAESTRO}]
    })
    
    # Add project state context if available
    if project_state.get('data') and project_state['data']:
        context = f"CONTEXTO DEL PROYECTO: {json.dumps(project_state['data'], indent=2)}"
        conversation.append({
            "role": "user", 
            "content": [{"text": context}]
        })
    
    # Add conversation history with correct format
    for msg in messages:
        content = msg.get("content", "")
        if content.strip():
            conversation.append({
                "role": msg.get("role", "user"),
                "content": [{"text": content}]
            })
    
    return conversation

def call_bedrock_model(model_id: str, conversation: List[Dict]) -> Dict:
    """Call Bedrock model with correct format"""
    try:
        logger.info(f"Calling Bedrock model: {model_id}")
        
        response = bedrock_runtime.converse(
            modelId=model_id,
            messages=conversation,
            inferenceConfig={
                'maxTokens': 4000,
                'temperature': 0.7,
                'topP': 0.9
            }
        )
        
        content = response['output']['message']['content'][0]['text']
        logger.info(f"Bedrock response received, length: {len(content)}")
        
        return {
            'content': content,
            'usage': response.get('usage', {}),
            'modelUsed': model_id
        }
        
    except Exception as e:
        logger.error(f"Error calling Bedrock: {str(e)}", exc_info=True)
        return {'error': f'Error calling Bedrock: {str(e)}'}

def lambda_handler(event, context):
    """Main Lambda handler - CON GENERACIÓN DE CONTENIDO REAL"""
    
    try:
        logger.info(f"Event received: {json.dumps(event, default=str)}")
        
        # Handle CORS preflight requests
        if event.get('httpMethod') == 'OPTIONS':
            logger.info("Handling OPTIONS preflight request")
            return handle_preflight_request()
        
        # Parse request
        try:
            if isinstance(event.get('body'), str):
                body = json.loads(event['body'])
            else:
                body = event.get('body', {})
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return create_error_response(400, 'Invalid JSON in request body')
        
        messages = body.get('messages', [])
        model_id = body.get('modelId', 'anthropic.claude-3-5-sonnet-20240620-v1:0')
        project_state = body.get('projectState', {'phase': 'inicio', 'data': {}})
        
        if not messages:
            logger.error("No messages provided")
            return create_error_response(400, 'No messages provided')
        
        logger.info(f"Processing {len(messages)} messages with model: {model_id}")
        
        # === ACTIVACIÓN MCP CON CONTENIDO REAL ===
        
        # 1. MCP CORE - SIEMPRE ACTIVO
        core_mcp = activate_core_mcp_always(messages)
        
        # 2. MCP AWS DOCS - SOLO CUANDO SEA NECESARIO
        docs_mcp = check_docs_mcp_needed(messages)
        
        # 3. READINESS PARA GENERACIÓN
        generation_readiness = calculate_generation_readiness(messages)
        
        # 4. MCPs DE GENERACIÓN - Con contenido REAL + GUARDADO S3
        generation_mcps = {'activated_mcps': [], 'generated_content': {}, 'mcp_count': 0, 's3_folder': None}
        if generation_readiness['ready_for_generation']:
            generation_mcps = activate_generation_mcps_with_real_content(messages)
        
        # Prepare conversation for Bedrock
        conversation = prepare_conversation(messages, project_state)
        
        if not conversation:
            logger.error("Empty conversation after preparation")
            return create_error_response(400, 'No valid conversation content')
        
        # Call Bedrock model
        bedrock_response = call_bedrock_model(model_id, conversation)
        
        if 'error' in bedrock_response:
            logger.error(f"Bedrock error: {bedrock_response['error']}")
            return create_error_response(500, bedrock_response['error'])
        
        response_content = bedrock_response['content']
        
        if not response_content or not response_content.strip():
            logger.error("Empty response from Bedrock")
            return create_error_response(500, 'Empty response from AI model')
        
        # Si se generaron documentos REALES, agregarlos a la respuesta
        if generation_mcps['generated_content']:
            logger.info("📄 Adding REAL MCP-generated content to response")
            response_content += "\n\n--- DOCUMENTOS GENERADOS Y GUARDADOS EN S3 ---\n"
            response_content += f"📁 Carpeta: {generation_mcps['s3_folder']}\n"
            response_content += f"🪣 Bucket: {DOCUMENTS_BUCKET}\n"
            response_content += f"📄 Documentos: {generation_mcps['mcp_count']} archivos generados\n\n"
            
            # Mostrar resumen de documentos generados
            for content_type in generation_mcps['generated_content'].keys():
                response_content += f"✅ {content_type.title()}: Generado exitosamente\n"
            
            response_content += f"\n🎯 Los documentos han sido guardados en S3 y el proyecto registrado en la base de datos."
        
        # Compilar MCPs utilizados
        all_mcps_used = []
        if core_mcp['activated']:
            all_mcps_used.append('core-mcp-prompt-understanding')
        if docs_mcp['activated']:
            all_mcps_used.append('aws-docs-mcp')
        all_mcps_used.extend(generation_mcps['activated_mcps'])
        
        # Response data
        response_data = {
            'content': response_content,
            'projectState': project_state,
            'mcpActivated': len(all_mcps_used) > 0,
            'mcpStatus': f'real_content_phase_{1 if not generation_readiness["ready_for_generation"] else 3}',
            'mcpUsed': all_mcps_used,
            'mcpBreakdown': {
                'core_mcp': core_mcp,
                'docs_mcp': docs_mcp,
                'generation_readiness': generation_readiness,
                'generation_mcps': generation_mcps
            },
            's3Info': {
                'bucket': DOCUMENTS_BUCKET,
                'folder': generation_mcps.get('s3_folder'),
                'documents_saved': generation_mcps.get('s3_result', {}).get('documents_saved', []),
                'content_source': 'real_generation'
            } if generation_mcps.get('s3_folder') else None,
            'readinessScore': generation_readiness['readiness_score'],
            'modelUsed': bedrock_response.get('modelUsed', model_id),
            'usage': bedrock_response.get('usage', {}),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ REAL CONTENT Response: Core={core_mcp['activated']}, Docs={docs_mcp['activated']}, Generation={generation_readiness['ready_for_generation']}")
        if generation_mcps.get('s3_folder'):
            logger.info(f"📁 S3 Folder: {generation_mcps['s3_folder']}, Documents: {generation_mcps['mcp_count']}")
        
        return create_success_response(response_data)
        
    except Exception as e:
        logger.error(f"Unexpected error in lambda_handler: {str(e)}", exc_info=True)
        return create_error_response(500, f'Internal server error: {str(e)}')
