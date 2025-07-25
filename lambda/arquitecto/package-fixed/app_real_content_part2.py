"""
Continuación del archivo app_real_content.py
"""

def activate_core_mcp_always(messages: List[Dict]) -> Dict:
    """
    MCP CORE - SIEMPRE ACTIVO (como Amazon Q CLI)
    Se ejecuta en CADA mensaje para prompt understanding
    """
    logger.info("🧠 ACTIVATING CORE MCP - ALWAYS ACTIVE")
    
    conversation_text = " ".join([msg.get("content", "") for msg in messages])
    
    core_result = call_mcp_service('core', 'analyze', {
        'conversation': conversation_text,
        'action': 'prompt_understanding',
        'timestamp': datetime.now().isoformat()
    })
    
    return {
        'activated': True,
        'result': core_result,
        'reason': 'Core MCP always active for prompt understanding'
    }

def check_docs_mcp_needed(messages: List[Dict]) -> Dict:
    """
    MCP AWS DOCS - ACTIVACIÓN CONDICIONAL CORREGIDA
    SOLO se activa cuando hay triggers específicos
    """
    conversation_text = " ".join([msg.get("content", "") for msg in messages]).lower()
    
    # Triggers específicos para documentación (MÁS RESTRICTIVOS)
    explicit_docs_triggers = [
        'documentacion', 'busca documentacion', 'buscar documentacion',
        'mejores practicas', 'como hacer', 'que es lambda', 'que es ec2',
        'aws docs', 'documentacion oficial', 'guia oficial',
        'tutorial', 'ejemplo oficial', 'referencia aws'
    ]
    
    # Preguntas específicas que requieren docs oficiales
    specific_questions = [
        'como configurar', 'como implementar', 'como usar',
        'cual es la diferencia', 'que diferencia hay',
        'limites de', 'restricciones de', 'pricing de'
    ]
    
    needs_docs = (
        any(trigger in conversation_text for trigger in explicit_docs_triggers) or
        any(question in conversation_text for question in specific_questions)
    )
    
    if needs_docs:
        logger.info("📚 ACTIVATING AWS DOCS MCP - Explicit documentation request detected")
        
        docs_result = call_mcp_service('awsdocs', 'search', {
            'query': conversation_text,
            'action': 'get_official_docs',
            'timestamp': datetime.now().isoformat()
        })
        
        return {
            'activated': True,
            'result': docs_result,
            'reason': 'Explicit documentation request detected'
        }
    else:
        logger.info("📚 AWS Docs MCP NOT NEEDED - No explicit documentation triggers")
        return {
            'activated': False,
            'result': None,
            'reason': 'No explicit documentation triggers detected'
        }

def calculate_generation_readiness(messages: List[Dict]) -> Dict:
    """
    Calcula readiness SOLO para MCPs de generación
    """
    conversation_text = " ".join([msg.get("content", "") for msg in messages]).lower()
    
    score = 0.0
    criteria = {}
    
    # 1. Nombre del proyecto (25%)
    if any(word in conversation_text for word in ['proyecto', 'sistema', 'aplicacion', 'plataforma']):
        criteria['project_name'] = True
        score += 0.25
    else:
        criteria['project_name'] = False
    
    # 2. Tipo de proyecto (25%)
    if any(word in conversation_text for word in ['integral', 'rapido', 'servicio', 'ec2', 'rds', 's3', 'lambda']):
        criteria['project_type'] = True
        score += 0.25
    else:
        criteria['project_type'] = False
    
    # 3. Detalles técnicos (25%)
    technical_indicators = ['instancia', 'tipo', 'region', 'volumen', 'vpc', 'security', 'key', 'tamaño', 'gb']
    if sum(1 for indicator in technical_indicators if indicator in conversation_text) >= 3:
        criteria['technical_details'] = True
        score += 0.25
    else:
        criteria['technical_details'] = False
    
    # 4. Contexto suficiente (25%)
    user_messages = [msg for msg in messages if msg.get('role') == 'user']
    if len(user_messages) >= 4:
        criteria['sufficient_context'] = True
        score += 0.25
    else:
        criteria['sufficient_context'] = False
    
    return {
        'readiness_score': score,
        'criteria': criteria,
        'ready_for_generation': score >= 0.8
    }

def activate_generation_mcps_with_real_content(messages: List[Dict]) -> Dict:
    """
    MCPs DE GENERACIÓN - Con contenido REAL cuando MCPs devuelven mock
    """
    logger.info("🎯 ACTIVATING GENERATION MCPs - With REAL content generation")
    
    conversation_text = " ".join([msg.get("content", "") for msg in messages])
    project_info = extract_project_info(messages)
    
    activated_mcps = []
    generated_content = {}
    
    # 1. Diagram MCP - Con fallback a contenido real
    diagram_result = call_mcp_service('diagram', 'generate', {
        'project_name': project_info['name'],
        'project_type': project_info['type'],
        'services': ['EC2', 'VPC'] if 'ec2' in conversation_text else ['Lambda', 'API Gateway']
    })
    
    if is_mock_response(diagram_result):
        logger.info("🔄 Diagram MCP returned mock - generating REAL content")
        diagram_content = generate_real_diagram(project_info, conversation_text)
    else:
        diagram_content = diagram_result
    
    activated_mcps.append('diagram-mcp')
    generated_content['diagram'] = diagram_content
    
    # 2. CloudFormation MCP - Con fallback a contenido real
    cfn_result = call_mcp_service('cfn', 'generate', {
        'project_name': project_info['name'],
        'services': ['EC2'] if 'ec2' in conversation_text else ['Lambda'],
        'environment': 'prod'
    })
    
    if is_mock_response(cfn_result):
        logger.info("🔄 CloudFormation MCP returned mock - generating REAL content")
        cfn_content = generate_real_cloudformation(project_info, conversation_text)
    else:
        cfn_content = cfn_result
    
    activated_mcps.append('cloudformation-mcp')
    generated_content['cloudformation'] = cfn_content
    
    # 3. Document Generator MCP - Con fallback a contenido real
    doc_result = call_mcp_service('customdoc', 'generate', {
        'project_name': project_info['name'],
        'project_type': project_info['type'],
        'format': ['csv', 'docx', 'xlsx']
    })
    
    if is_mock_response(doc_result):
        logger.info("🔄 Document MCP returned mock - generating REAL content")
        doc_content = generate_real_documentation(project_info, conversation_text)
    else:
        doc_content = doc_result
    
    activated_mcps.append('document-generator-mcp')
    generated_content['documentation'] = doc_content
    
    # 4. Pricing MCP - Con fallback a contenido real
    pricing_result = call_mcp_service('pricing', 'calculate', {
        'services': ['EC2'] if 'ec2' in conversation_text else ['Lambda'],
        'usage_estimates': {'hours_per_month': 730}
    })
    
    if is_mock_response(pricing_result):
        logger.info("🔄 Pricing MCP returned mock - generating REAL content")
        pricing_content = generate_real_pricing(project_info, conversation_text)
    else:
        pricing_content = pricing_result
    
    activated_mcps.append('pricing-mcp')
    generated_content['pricing'] = pricing_content
    
    # 5. GUARDAR EN S3 - Con contenido REAL
    s3_result = save_documents_to_s3(project_info, generated_content)
    
    return {
        'activated_mcps': activated_mcps,
        'generated_content': generated_content,
        'mcp_count': len(activated_mcps),
        's3_folder': f"{project_info['name'].lower().replace(' ', '-')}-{project_info['id'][:8]}" if generated_content else None,
        's3_result': s3_result
    }

def save_documents_to_s3(project_info: Dict, generated_content: Dict) -> Dict:
    """
    GUARDA DOCUMENTOS REALES EN S3 EN CARPETA POR PROYECTO
    """
    try:
        folder_name = f"{project_info['name'].lower().replace(' ', '-')}-{project_info['id'][:8]}"
        
        logger.info(f"📁 Saving REAL documents to S3 folder: {folder_name}")
        
        documents_saved = []
        
        for content_type, content_data in generated_content.items():
            # Determinar extensión del archivo
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
                file_extension = 'json'
                content_type_s3 = 'application/json'
            else:
                file_extension = 'txt'
                content_type_s3 = 'text/plain'
            
            file_name = f"{content_type}.{file_extension}"
            s3_key = f"{folder_name}/{file_name}"
            
            # Convertir contenido a string si es necesario
            if isinstance(content_data, dict):
                content_str = json.dumps(content_data, indent=2)
            else:
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
                    'content_source': 'real_generation'
                }
            )
            
            documents_saved.append({
                'file_name': file_name,
                's3_key': s3_key,
                'content_type': content_type,
                'size_bytes': len(content_str.encode('utf-8'))
            })
            
            logger.info(f"✅ Saved REAL content {file_name} to S3: {s3_key} ({len(content_str)} chars)")
        
        # Guardar proyecto en DynamoDB
        save_project_to_dynamodb(project_info, documents_saved, folder_name)
        
        return {
            'folder_name': folder_name,
            'documents_saved': documents_saved,
            'bucket': DOCUMENTS_BUCKET,
            'total_files': len(documents_saved),
            'content_source': 'real_generation'
        }
        
    except Exception as e:
        logger.error(f"❌ Error saving to S3: {str(e)}")
        return None

def save_project_to_dynamodb(project_info: Dict, documents_saved: List[Dict], folder_name: str):
    """Guarda el proyecto en DynamoDB"""
    try:
        table = dynamodb.Table(PROJECTS_TABLE)
        
        project_item = {
            'projectId': project_info['id'],
            'projectName': project_info['name'],
            'projectType': project_info.get('type', 'Solucion AWS'),
            'status': 'completed',
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat(),
            'description': project_info.get('description', f'Proyecto {project_info["name"]} generado automaticamente'),
            's3Folder': folder_name,
            's3Bucket': DOCUMENTS_BUCKET,
            'documentsGenerated': documents_saved,
            'totalDocuments': len(documents_saved),
            'contentSource': 'real_generation'
        }
        
        table.put_item(Item=project_item)
        logger.info(f"✅ Project saved to DynamoDB: {project_info['id']}")
        return True
    except Exception as e:
        logger.error(f"❌ Error saving to DynamoDB: {str(e)}")
        return False

def extract_project_info(messages: List[Dict]) -> Dict:
    """Extrae información del proyecto de la conversación"""
    conversation_text = " ".join([msg.get("content", "") for msg in messages]).lower()
    
    project_info = {
        'id': str(uuid.uuid4())[:8],
        'name': 'AWS Project',
        'type': 'Solucion AWS'
    }
    
    # Extraer nombre del proyecto
    user_messages = [msg.get("content", "") for msg in messages if msg.get('role') == 'user']
    if user_messages:
        first_response = user_messages[0].strip()
        if len(first_response.split()) <= 5:  # Probablemente es el nombre
            project_info['name'] = first_response
    
    # Determinar tipo
    if 'ec2' in conversation_text:
        project_info['type'] = 'Implementacion EC2'
    elif 'rds' in conversation_text:
        project_info['type'] = 'Base de Datos RDS'
    elif 'integral' in conversation_text:
        project_info['type'] = 'Solucion Integral'
    elif 'rapido' in conversation_text:
        project_info['type'] = 'Servicio Rapido'
    
    return project_info
