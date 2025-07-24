"""
Continuacion del archivo app_fixed.py - Parte 3: Funciones principales
"""

def save_documents_to_s3_fixed(project_info: Dict, generated_content: Dict) -> Dict:
    """Guarda documentos REALES en S3 con contenido profesional"""
    try:
        folder_name = f"{project_info['name'].lower().replace(' ', '-')}-{project_info['id'][:8]}"
        
        logger.info(f"📁 Saving PROFESSIONAL documents to S3 folder: {folder_name}")
        
        documents_saved = []
        
        for content_type, content_data in generated_content.items():
            # Determinar extension y tipo de contenido
            if content_type == 'diagram':
                file_extension = 'svg'
                content_type_s3 = 'image/svg+xml'
            elif content_type == 'cloudformation':
                file_extension = 'yaml'
                content_type_s3 = 'text/yaml'
            elif content_type == 'documentation':
                file_extension = 'txt'
                content_type_s3 = 'text/plain'
            elif content_type == 'pricing':
                file_extension = 'txt'
                content_type_s3 = 'text/plain'
            elif content_type == 'activities':
                file_extension = 'csv'
                content_type_s3 = 'text/csv'
            else:
                file_extension = 'txt'
                content_type_s3 = 'text/plain'
            
            file_name = f"{content_type}.{file_extension}"
            s3_key = f"{folder_name}/{file_name}"
            
            # Convertir contenido a string
            content_str = str(content_data)
            
            # Subir a S3
            s3_client.put_object(
                Bucket=DOCUMENTS_BUCKET,
                Key=s3_key,
                Body=content_str,
                ContentType=content_type_s3,
                Metadata={
                    'project_name': project_info['name'],
                    'project_type': project_info['type'],
                    'generated_at': datetime.now().isoformat(),
                    'content_source': 'professional_generation'
                }
            )
            
            documents_saved.append({
                'file_name': file_name,
                's3_key': s3_key,
                'content_type': content_type,
                'size_bytes': len(content_str.encode('utf-8'))
            })
            
            logger.info(f"✅ Saved PROFESSIONAL {file_name} to S3: {s3_key}")
        
        # Guardar proyecto en DynamoDB
        save_project_to_dynamodb_fixed(project_info, documents_saved, folder_name)
        
        return {
            'folder_name': folder_name,
            'documents_saved': documents_saved,
            'bucket': DOCUMENTS_BUCKET,
            'total_files': len(documents_saved),
            'content_source': 'professional_generation'
        }
        
    except Exception as e:
        logger.error(f"❌ Error saving to S3: {str(e)}")
        return None

def save_project_to_dynamodb_fixed(project_info: Dict, documents_saved: List[Dict], folder_name: str):
    """Guarda informacion del proyecto en DynamoDB"""
    try:
        table = dynamodb.Table(PROJECTS_TABLE)
        
        # Convertir Decimal para DynamoDB
        def convert_decimals(obj):
            if isinstance(obj, list):
                return [convert_decimals(i) for i in obj]
            elif isinstance(obj, dict):
                return {k: convert_decimals(v) for k, v in obj.items()}
            elif isinstance(obj, float):
                return Decimal(str(obj))
            else:
                return obj
        
        item = {
            'project_id': project_info['id'],
            'project_name': project_info['name'],
            'project_type': project_info['type'],
            'status': 'completed',
            'created_at': project_info['created_at'],
            'updated_at': datetime.now().isoformat(),
            's3_folder': folder_name,
            'documents': convert_decimals(documents_saved),
            'total_files': len(documents_saved)
        }
        
        table.put_item(Item=item)
        logger.info(f"✅ Project saved to DynamoDB: {project_info['id']}")
        
    except Exception as e:
        logger.error(f"❌ Error saving to DynamoDB: {str(e)}")

def generate_all_documents_fixed(project_info: Dict, conversation_text: str) -> Dict:
    """Genera TODOS los documentos profesionales"""
    
    logger.info("📄 Generating ALL professional documents")
    
    generated_content = {}
    
    # 1. Diagrama AWS con iconos reales
    logger.info("🎨 Generating AWS diagram with real icons")
    diagram_content = generate_aws_diagram_with_mcp(project_info, conversation_text)
    generated_content['diagram'] = diagram_content
    
    # 2. CloudFormation profesional
    logger.info("🏗️ Generating professional CloudFormation")
    cf_content = generate_professional_cloudformation(project_info, conversation_text)
    generated_content['cloudformation'] = cf_content
    
    # 3. Documentacion tecnica completa
    logger.info("📋 Generating professional documentation")
    doc_content = generate_professional_documentation(project_info, conversation_text)
    generated_content['documentation'] = doc_content
    
    # 4. Pricing detallado
    logger.info("💰 Generating detailed pricing")
    pricing_content = generate_detailed_pricing(project_info, conversation_text)
    generated_content['pricing'] = pricing_content
    
    # 5. Actividades del proyecto
    logger.info("📅 Generating project activities")
    activities_content = generate_project_activities(project_info, conversation_text)
    generated_content['activities'] = activities_content
    
    # 6. Guardar en S3
    s3_result = save_documents_to_s3_fixed(project_info, generated_content)
    
    return {
        'generated_content': generated_content,
        's3_result': s3_result,
        'total_documents': len(generated_content)
    }

def prepare_conversation_fixed(messages: List[Dict], project_state: Dict) -> List[Dict]:
    """Prepara conversacion para Bedrock con prompt maestro corregido"""
    
    conversation = []
    
    # Agregar prompt maestro como primer mensaje del sistema
    conversation.append({
        "role": "user",
        "content": PROMPT_MAESTRO_CORREGIDO
    })
    
    # Agregar contexto del estado del proyecto si existe
    if project_state.get('phase') != 'inicio':
        context_msg = f"Contexto del proyecto: Fase actual: {project_state.get('phase', 'inicio')}"
        if project_state.get('data'):
            context_msg += f", Datos recopilados: {json.dumps(project_state['data'])}"
        
        conversation.append({
            "role": "user", 
            "content": context_msg
        })
    
    # Agregar mensajes de la conversacion
    for msg in messages:
        if msg.get('content') and msg.get('content').strip():
            conversation.append({
                "role": msg.get('role', 'user'),
                "content": msg['content'].strip()
            })
    
    return conversation

def call_bedrock_model_fixed(model_id: str, conversation: List[Dict]) -> Dict:
    """Llama al modelo Bedrock con manejo mejorado"""
    try:
        logger.info(f"🤖 Calling Bedrock model: {model_id}")
        
        # Preparar mensajes para Bedrock
        messages = []
        for msg in conversation:
            messages.append({
                "role": msg["role"],
                "content": [{"text": msg["content"]}]
            })
        
        response = bedrock_runtime.converse(
            modelId=model_id,
            messages=messages,
            inferenceConfig={
                'maxTokens': 4000,
                'temperature': 0.7,
                'topP': 0.9
            }
        )
        
        content = response['output']['message']['content'][0]['text']
        logger.info(f"✅ Bedrock response received, length: {len(content)}")
        
        return {
            'content': content,
            'usage': response.get('usage', {}),
            'modelUsed': model_id
        }
        
    except Exception as e:
        logger.error(f"❌ Error calling Bedrock: {str(e)}")
        return {'error': f'Error calling Bedrock: {str(e)}'}

def create_cors_response(status_code: int, body: Dict) -> Dict:
    """Crea respuesta con headers CORS"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, X-Amz-Date, Authorization, X-Api-Key, X-Amz-Security-Token',
            'Access-Control-Max-Age': '86400'
        },
        'body': json.dumps(body, default=str)
    }

def lambda_handler_fixed(event, context):
    """Lambda handler CORREGIDO con consultoria completa"""
    
    try:
        logger.info(f"📥 Event received: {json.dumps(event, default=str)}")
        
        # Handle CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return create_cors_response(200, {'message': 'CORS preflight successful'})
        
        # Parse request body
        try:
            if isinstance(event.get('body'), str):
                body = json.loads(event['body'])
            else:
                body = event.get('body', {})
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode error: {str(e)}")
            return create_cors_response(400, {'error': 'Invalid JSON in request body'})
        
        messages = body.get('messages', [])
        model_id = body.get('modelId', 'anthropic.claude-3-5-sonnet-20240620-v1:0')
        project_state = body.get('projectState', {'phase': 'inicio', 'data': {}})
        
        if not messages:
            return create_cors_response(400, {'error': 'No messages provided'})
        
        logger.info(f"🔄 Processing {len(messages)} messages with model: {model_id}")
        
        # === LOGICA PRINCIPAL CORREGIDA ===
        
        # 1. Extraer informacion del proyecto
        project_info = extract_project_info(messages)
        
        # 2. Verificar si esta listo para generar documentos
        ready_for_generation = is_ready_for_generation(messages)
        
        # 3. Generar documentos si esta listo
        generation_result = None
        if ready_for_generation:
            logger.info("✅ Ready for document generation")
            conversation_text = " ".join([msg.get("content", "") for msg in messages])
            generation_result = generate_all_documents_fixed(project_info, conversation_text)
        
        # 4. Preparar conversacion para Bedrock
        conversation = prepare_conversation_fixed(messages, project_state)
        
        if not conversation:
            return create_cors_response(400, {'error': 'No valid conversation content'})
        
        # 5. Llamar a Bedrock
        bedrock_response = call_bedrock_model_fixed(model_id, conversation)
        
        if 'error' in bedrock_response:
            return create_cors_response(500, {'error': bedrock_response['error']})
        
        response_content = bedrock_response['content']
        
        # 6. Agregar informacion de documentos generados si aplica
        if generation_result and generation_result['s3_result']:
            response_content += "\n\n--- DOCUMENTOS GENERADOS Y GUARDADOS EN S3 ---\n"
            response_content += f"📁 Carpeta: {generation_result['s3_result']['folder_name']}\n"
            response_content += f"🪣 Bucket: {DOCUMENTS_BUCKET}\n"
            response_content += f"📄 Documentos: {generation_result['total_documents']} archivos generados\n\n"
            
            for doc_type in generation_result['generated_content'].keys():
                response_content += f"✅ {doc_type.title()}: Generado exitosamente\n"
            
            response_content += f"\n🎯 Los documentos han sido guardados en S3 y el proyecto registrado en la base de datos."
        
        # 7. Preparar respuesta final
        response_data = {
            'content': response_content,
            'usage': bedrock_response.get('usage', {}),
            'modelUsed': bedrock_response.get('modelUsed', model_id),
            'mcpUsed': ['core-mcp'] if generation_result else [],
            'projectUpdate': {
                'phase': 'generacion' if ready_for_generation else project_state.get('phase', 'inicio'),
                'data': project_info
            } if ready_for_generation else None
        }
        
        logger.info("✅ Request processed successfully")
        return create_cors_response(200, response_data)
        
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}", exc_info=True)
        return create_cors_response(500, {'error': f'Internal server error: {str(e)}'})

# Alias para compatibilidad
lambda_handler = lambda_handler_fixed
