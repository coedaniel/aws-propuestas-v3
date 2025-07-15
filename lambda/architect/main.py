"""
AWS Propuestas V3 - Professional Solutions Architect
Implements the Master Prompt for AWS Solutions Architecture with MCP Integration
"""

import json
import boto3
import uuid
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError

# Import the new intelligent architect
from intelligent_architect import IntelligentArchitect

def lambda_handler(event, context):
    """
    Main Lambda handler for the Architect functionality
    Routes requests to the appropriate handler based on the request type
    """
    
    try:
        # Handle CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                },
                'body': ''
            }
        
        # Parse request body
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event
        
        # Extract parameters
        messages = body.get('messages', [])
        session_id = body.get('session_id')
        model_id = body.get('modelId', 'anthropic.claude-3-5-sonnet-20241022-v2:0')
        
        print(f"Architect request - Session: {session_id}, Messages: {len(messages)}")
        
        # Get the last user message
        user_input = ""
        if messages:
            for msg in reversed(messages):
                if msg.get('role') == 'user':
                    user_input = msg.get('content', '')
                    break
        
        # Create intelligent architect instance and process request
        architect = IntelligentArchitect()
        result = architect.process_request(user_input, session_id)
        
        # Format response for frontend compatibility
        response = {
            'response': result.get('response', ''),
            'modelId': model_id,
            'projectId': result.get('session_id'),
            'currentStep': result.get('state', 'initial'),
            'isComplete': result.get('state') == 'completed',
            'usage': {
                'inputTokens': len(user_input) // 4,  # Rough estimate
                'outputTokens': len(result.get('response', '')) // 4,
                'totalTokens': (len(user_input) + len(result.get('response', ''))) // 4
            }
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Content-Type': 'application/json'
            },
            'body': json.dumps(response)
        }
        
    except Exception as e:
        print(f"Error in architect lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e),
                'response': 'Lo siento, hubo un error interno. Por favor, intenta de nuevo.',
                'modelId': 'error',
                'projectId': None,
                'currentStep': 'error',
                'isComplete': False
            })
        }
            
            # Process user input through the Master Prompt flow
            response = self._process_master_prompt(user_input, session_id)
            
            # Save session state
            self._save_session(session_id)
            
            return {
                'statusCode': 200,
                'headers': self._get_cors_headers(),
                'body': json.dumps({
                    'response': response,
                    'session_id': session_id,
                    'conversation_state': self.conversation_state,
                    'project_info': self.project_info,
                    'timestamp': datetime.utcnow().isoformat()
                })
            }
            
        except Exception as e:
            print(f"Error in lambda_handler: {str(e)}")
            return {
                'statusCode': 500,
                'headers': self._get_cors_headers(),
                'body': json.dumps({
                    'error': f'Error interno del servidor: {str(e)}',
                    'session_id': session_id if 'session_id' in locals() else None
                })
            }
    
    def _process_master_prompt(self, user_input: str, session_id: str) -> str:
        """
        Implements the Master Prompt logic:
        1. Project name
        2. Solution type (integral vs rapid service)
        3. Guided interview
        4. Document generation
        5. S3 upload
        """
        
        # Detect user intent and adapt flow dynamically
        intent = self._analyze_user_intent(user_input)
        
        if self.conversation_state == "initial" or intent.get('restart'):
            return self._start_conversation()
        
        elif self.conversation_state == "asking_project_name":
            return self._handle_project_name(user_input)
        
        elif self.conversation_state == "asking_solution_type":
            return self._handle_solution_type(user_input)
        
        elif self.conversation_state == "rapid_service_flow":
            return self._handle_rapid_service_flow(user_input, session_id)
        
        elif self.conversation_state == "integral_solution_flow":
            return self._handle_integral_solution_flow(user_input, session_id)
        
        elif self.conversation_state == "generating_documents":
            return self._handle_document_generation(user_input, session_id)
        
        elif self.conversation_state == "asking_s3_bucket":
            return self._handle_s3_upload(user_input, session_id)
        
        elif self.conversation_state == "final_comments":
            return self._handle_final_comments(user_input, session_id)
        
        else:
            # Adaptive response - understand what user wants
            return self._adaptive_response(user_input, session_id)
    
    def _start_conversation(self) -> str:
        """Start the conversation following the Master Prompt"""
        self.conversation_state = "asking_project_name"
        return """¡Hola! Soy tu arquitecto de soluciones AWS experto. 

Vamos a dimensionar, documentar y entregar una solucion profesional en AWS, siguiendo mejores practicas y generando todos los archivos necesarios para una propuesta ejecutiva.

**Pregunta 1:**
¿Cual es el nombre del proyecto?"""
    
    def _handle_project_name(self, user_input: str) -> str:
        """Handle project name input"""
        project_name = user_input.strip()
        if not project_name:
            return "Por favor, proporciona un nombre para el proyecto."
        
        self.project_info['name'] = project_name
        self.conversation_state = "asking_solution_type"
        
        return f"""Perfecto, el proyecto se llama: **{project_name}**

**Pregunta 2:**
¿El proyecto es una solucion integral o un servicio rapido especifico?

**Opciones:**
- **Solucion integral**: migracion, aplicacion nueva, modernizacion, analitica, seguridad, IA, IoT, data lake, networking, DRP, VDI, integracion, etc.
- **Servicio rapido especifico**: implementacion de instancias EC2, RDS, SES, VPN, ELB, S3, VPC, CloudFront, SSO, backup, etc.

Responde "integral" o "rapido" (o describe tu necesidad)."""
    
    def _handle_solution_type(self, user_input: str) -> str:
        """Handle solution type selection"""
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ['rapido', 'rapid', 'especifico', 'specific']):
            self.project_info['solution_type'] = 'rapid_service'
            self.conversation_state = "rapid_service_flow"
            return self._show_rapid_services_catalog()
        
        elif any(word in user_input_lower for word in ['integral', 'complejo', 'complex', 'migracion', 'aplicacion', 'modernizacion']):
            self.project_info['solution_type'] = 'integral_solution'
            self.conversation_state = "integral_solution_flow"
            return self._start_integral_interview()
        
        else:
            # Try to understand what they want
            return """No estoy seguro del tipo de solucion que necesitas.

Por favor, especifica:
- **"integral"** para proyectos complejos (migraciones, aplicaciones nuevas, modernizacion, etc.)
- **"rapido"** para servicios especificos (EC2, RDS, S3, VPN, etc.)

¿Cual prefieres?"""
    
    def _show_rapid_services_catalog(self) -> str:
        """Show catalog of rapid services"""
        return """**Catalogo de Servicios Rapidos AWS:**

**Compute & Storage:**
1. Instancias EC2 (servidores virtuales)
2. Amazon RDS (bases de datos)
3. Amazon S3 (almacenamiento de objetos)
4. EBS (almacenamiento de bloques)

**Networking & Security:**
5. VPC (red privada virtual)
6. VPN (conexion segura)
7. ELB (balanceador de carga)
8. CloudFront (CDN)
9. Route 53 (DNS)

**Management & Security:**
10. AWS SSO (inicio de sesion unico)
11. AWS Backup (respaldos)
12. CloudWatch (monitoreo)
13. SES (servicio de email)

**Escribe el numero del servicio que necesitas, o describe tu requerimiento especifico.**"""
    
    def _start_integral_interview(self) -> str:
        """Start guided interview for integral solutions"""
        self.project_info['interview_step'] = 1
        return f"""Perfecto, vamos a hacer una entrevista guiada para **{self.project_info['name']}**.

**Pregunta 1 de 15:**
¿Que tipo de solucion integral necesitas?

**Opciones comunes:**
- Migracion a la nube
- Aplicacion web nueva
- Modernizacion de aplicaciones
- Plataforma de analitica/BI
- Solucion de seguridad
- Implementacion de IA/ML
- Plataforma IoT
- Data Lake
- Networking empresarial
- Plan de recuperacion ante desastres (DRP)
- Infraestructura de escritorios virtuales (VDI)
- Integracion de sistemas

Describe tu necesidad o elige una opcion."""
    
    def _handle_rapid_service_flow(self, user_input: str, session_id: str) -> str:
        """Handle rapid service flow"""
        # Parse service selection
        selected_services = self._parse_service_selection(user_input)
        self.project_info['selected_services'] = selected_services
        
        # Ask minimal questions for selected services
        if not hasattr(self, 'service_questions_asked'):
            self.service_questions_asked = []
        
        # Generate questions based on selected services
        questions = self._generate_service_questions(selected_services)
        
        if len(self.service_questions_asked) < len(questions):
            current_question = questions[len(self.service_questions_asked)]
            self.service_questions_asked.append(current_question)
            return current_question
        else:
            # All questions answered, generate documents
            return self._initiate_document_generation(session_id, 'rapid')
    
    def _handle_integral_solution_flow(self, user_input: str, session_id: str) -> str:
        """Handle integral solution guided interview"""
        step = self.project_info.get('interview_step', 1)
        
        # Store answer from previous step
        if step > 1:
            self.project_info[f'answer_{step-1}'] = user_input
        
        # Define interview questions
        questions = [
            "¿Que tipo de solucion integral necesitas?",
            "¿Cual es el objetivo principal del proyecto?",
            "Proporciona una descripcion detallada del proyecto:",
            "¿Cuales son las caracteristicas clave requeridas?",
            "¿Que componentes o servicios AWS deseas incluir?",
            "¿Cantidad y tipo de recursos principales?",
            "¿Que integraciones necesitas? (on-premises, SaaS, APIs, IoT, etc.)",
            "¿Requisitos de seguridad y compliance?",
            "¿Alta disponibilidad y DRP? (multi-AZ, multi-region, RTO, RPO, backups)",
            "¿Estimacion de usuarios, trafico, cargas?",
            "¿Presupuesto disponible? (opcional)",
            "¿Fechas de inicio y entrega deseadas?",
            "¿Restricciones tecnicas, negocio o preferencias tecnologicas?",
            "¿Comentarios o necesidades adicionales? (opcional)"
        ]
        
        if step <= len(questions):
            if step == 1:
                # Store the solution type from user input
                self.project_info['solution_type_detail'] = user_input
            
            self.project_info['interview_step'] = step + 1
            
            if step < len(questions):
                return f"**Pregunta {step + 1} de {len(questions)}:**\n{questions[step]}"
            else:
                # Interview complete, generate documents
                return self._initiate_document_generation(session_id, 'integral')
        else:
            return self._initiate_document_generation(session_id, 'integral')
    
    def _initiate_document_generation(self, session_id: str, solution_type: str) -> str:
        """Initiate document generation process"""
        self.conversation_state = "generating_documents"
        
        # Choose the appropriate agent based on solution type
        if solution_type == 'rapid':
            agent_id = NOVA_AGENT_ID
            agent_alias_id = NOVA_AGENT_ALIAS_ID
            agent_name = "Nova Pro"
        else:
            agent_id = CLAUDE_AGENT_ID
            agent_alias_id = CLAUDE_AGENT_ALIAS_ID
            agent_name = "Claude 3.5 Sonnet"
        
        try:
            # Generate documents using the selected agent
            documents = self._generate_all_documents(agent_id, agent_alias_id, session_id)
            
            self.project_info['generated_documents'] = documents
            self.conversation_state = "asking_s3_bucket"
            
            return f"""¡Excelente! He generado todos los documentos profesionales usando {agent_name}:

**Documentos generados:**
- ✅ Documento Word con objetivo y descripcion del proyecto
- ✅ Tabla de actividades de implementacion (CSV)
- ✅ Script CloudFormation para desplegar la solucion
- ✅ Diagramas de arquitectura (SVG, PNG, Draw.io)
- ✅ Archivo de costos estimados (CSV)
- ✅ Guia para la calculadora oficial de AWS

**Pregunta final:**
¿En que bucket S3 deseas subir la carpeta con todos los documentos generados?

Proporciona el nombre del bucket S3 (debe existir y tener permisos de escritura)."""
            
        except Exception as e:
            print(f"Error generating documents: {str(e)}")
            return f"Error generando documentos: {str(e)}. Por favor, intenta nuevamente."
    
    def _generate_all_documents(self, agent_id: str, agent_alias_id: str, session_id: str) -> Dict[str, Any]:
        """Generate all required documents using Bedrock agents and MCP servers"""
        
        # Prepare comprehensive prompt for the agent
        project_prompt = self._build_comprehensive_prompt()
        
        try:
            # Invoke Bedrock agent
            response = bedrock_agent_runtime.invoke_agent(
                agentId=agent_id,
                agentAliasId=agent_alias_id,
                sessionId=session_id,
                inputText=project_prompt,
                enableTrace=True
            )
            
            # Process streaming response
            agent_response = ""
            event_stream = response['completion']
            
            for event in event_stream:
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        chunk_data = json.loads(chunk['bytes'].decode('utf-8'))
                        if 'completion' in chunk_data:
                            agent_response += chunk_data['completion']
            
            # Generate individual documents using MCP servers
            documents = {
                'word_document': self._invoke_mcp_server('document_generator', {
                    'project_info': self.project_info,
                    'agent_response': agent_response,
                    'document_type': 'word'
                }),
                'activities_csv': self._invoke_mcp_server('document_generator', {
                    'project_info': self.project_info,
                    'agent_response': agent_response,
                    'document_type': 'activities_csv'
                }),
                'cloudformation_template': self._invoke_mcp_server('cloudformation_generator', {
                    'project_info': self.project_info,
                    'agent_response': agent_response
                }),
                'architecture_diagrams': self._invoke_mcp_server('diagram_generator', {
                    'project_info': self.project_info,
                    'agent_response': agent_response
                }),
                'cost_analysis': self._invoke_mcp_server('cost_analysis', {
                    'project_info': self.project_info,
                    'agent_response': agent_response
                })
            }
            
            return documents
            
        except Exception as e:
            print(f"Error in _generate_all_documents: {str(e)}")
            raise e
    
    def _invoke_mcp_server(self, server_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke MCP server Lambda function"""
        function_name = f"aws-propuestas-{server_name.replace('_', '-')}-{ENVIRONMENT}"
        
        try:
            response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            result = json.loads(response['Payload'].read())
            return result
            
        except Exception as e:
            print(f"Error invoking MCP server {server_name}: {str(e)}")
            return {'error': str(e)}
    
    def _build_comprehensive_prompt(self) -> str:
        """Build comprehensive prompt for the Bedrock agent"""
        project_name = self.project_info.get('name', 'Proyecto AWS')
        solution_type = self.project_info.get('solution_type', 'integral')
        
        prompt = f"""Actua como arquitecto de soluciones AWS y consultor experto. 

PROYECTO: {project_name}
TIPO: {solution_type}

INFORMACION DEL PROYECTO:
"""
        
        # Add all collected information
        for key, value in self.project_info.items():
            if key.startswith('answer_') or key in ['solution_type_detail', 'selected_services']:
                prompt += f"- {key}: {value}\n"
        
        prompt += """
GENERAR:
1. Propuesta ejecutiva profesional
2. Arquitectura AWS detallada
3. Lista de actividades de implementacion
4. Template CloudFormation funcional
5. Diagramas de arquitectura
6. Analisis de costos detallado
7. Guia para calculadora AWS

IMPORTANTE: 
- No uses acentos ni caracteres especiales
- Genera contenido profesional y detallado
- Incluye mejores practicas de AWS
- Asegura compatibilidad de archivos
"""
        
        return prompt
    
    def _handle_s3_upload(self, user_input: str, session_id: str) -> str:
        """Handle S3 bucket specification and upload"""
        bucket_name = user_input.strip()
        
        if not bucket_name:
            return "Por favor, proporciona el nombre del bucket S3."
        
        try:
            # Upload documents to S3
            upload_result = self._invoke_mcp_server('s3_upload', {
                'bucket_name': bucket_name,
                'project_name': self.project_info['name'],
                'documents': self.project_info.get('generated_documents', {}),
                'session_id': session_id
            })
            
            if 'error' in upload_result:
                return f"Error subiendo archivos a S3: {upload_result['error']}\n\nVerifica que el bucket existe y tienes permisos de escritura."
            
            self.conversation_state = "final_comments"
            
            return f"""¡Perfecto! Todos los documentos han sido subidos exitosamente a S3.

**Ubicacion:** s3://{bucket_name}/{self.project_info['name']}/

**Archivos subidos:**
- 📄 Propuesta ejecutiva (Word)
- 📊 Actividades de implementacion (CSV)
- ⚙️ Template CloudFormation (YAML)
- 🎨 Diagramas de arquitectura (SVG, PNG, Draw.io)
- 💰 Analisis de costos (CSV)
- 📋 Guia calculadora AWS (PDF)

**Pregunta final:**
¿Deseas agregar algun comentario o ajuste final antes de terminar?

Responde "no" para finalizar o describe cualquier ajuste necesario."""
            
        except Exception as e:
            return f"Error procesando la subida a S3: {str(e)}"
    
    def _handle_final_comments(self, user_input: str, session_id: str) -> str:
        """Handle final comments and close the session"""
        if user_input.lower().strip() in ['no', 'ninguno', 'nada', 'finalizar']:
            return self._finalize_session()
        else:
            # Process final adjustments
            self.project_info['final_comments'] = user_input
            return f"""Comentarios registrados: {user_input}

¡Perfecto! La propuesta para **{self.project_info['name']}** ha sido completada exitosamente.

**Resumen final:**
- ✅ Proyecto analizado y documentado
- ✅ Documentos profesionales generados
- ✅ Archivos subidos a S3
- ✅ Propuesta lista para presentacion

¡Gracias por usar el sistema de arquitectura AWS! 🚀"""
    
    def _finalize_session(self) -> str:
        """Finalize the session"""
        return f"""¡Perfecto! La propuesta para **{self.project_info['name']}** ha sido completada exitosamente.

**Resumen final:**
- ✅ Proyecto analizado y documentado
- ✅ Documentos profesionales generados
- ✅ Archivos subidos a S3
- ✅ Propuesta lista para presentacion

**Proximos pasos:**
1. Revisa los documentos en S3
2. Presenta la propuesta ejecutiva
3. Implementa usando el template CloudFormation
4. Utiliza la guia para estimar costos en la calculadora AWS

¡Gracias por usar el sistema de arquitectura AWS! 🚀

Para iniciar un nuevo proyecto, simplemente envia un mensaje."""
    
    def _analyze_user_intent(self, user_input: str) -> Dict[str, Any]:
        """Analyze user intent to adapt the conversation flow"""
        user_input_lower = user_input.lower()
        
        intent = {
            'restart': any(word in user_input_lower for word in ['nuevo', 'reiniciar', 'empezar', 'comenzar']),
            'project_info': any(word in user_input_lower for word in ['proyecto', 'nombre', 'llamar']),
            'solution_type': any(word in user_input_lower for word in ['integral', 'rapido', 'servicio', 'solucion']),
            'help': any(word in user_input_lower for word in ['ayuda', 'help', 'como', 'que']),
        }
        
        return intent
    
    def _adaptive_response(self, user_input: str, session_id: str) -> str:
        """Provide adaptive response when conversation flow is unclear"""
        intent = self._analyze_user_intent(user_input)
        
        if intent['help']:
            return """Soy tu arquitecto de soluciones AWS. Puedo ayudarte a:

1. **Crear propuestas profesionales** para proyectos AWS
2. **Generar documentacion completa** (Word, CSV, CloudFormation, diagramas)
3. **Analizar costos** y crear guias de implementacion
4. **Subir todo a S3** organizado por proyecto

Para empezar, dime: **¿Cual es el nombre de tu proyecto?**"""
        
        elif intent['restart']:
            self.conversation_state = "initial"
            self.project_info = {}
            return self._start_conversation()
        
        else:
            # Try to understand what they want and guide them
            return f"""Entiendo que mencionas: "{user_input}"

Para ayudarte mejor, necesito saber:
1. **¿Cual es el nombre del proyecto?**
2. **¿Es una solucion integral o un servicio rapido?**

Por favor, proporciona esta informacion para continuar."""
    
    # Utility methods
    def _parse_body(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Parse request body"""
        body = event.get('body', '{}')
        if isinstance(body, str):
            return json.loads(body)
        return body
    
    def _load_session(self, session_id: str):
        """Load session data (simplified - in production use DynamoDB)"""
        # In production, load from DynamoDB
        pass
    
    def _save_session(self, session_id: str):
        """Save session data (simplified - in production use DynamoDB)"""
        # In production, save to DynamoDB
        pass
    
    def _parse_service_selection(self, user_input: str) -> List[str]:
        """Parse selected services from user input"""
        # Simplified parsing - in production, use more sophisticated NLP
        services = []
        user_input_lower = user_input.lower()
        
        service_map = {
            '1': 'EC2', 'ec2': 'EC2', 'instancia': 'EC2',
            '2': 'RDS', 'rds': 'RDS', 'base de datos': 'RDS',
            '3': 'S3', 's3': 'S3', 'almacenamiento': 'S3',
            '4': 'EBS', 'ebs': 'EBS',
            '5': 'VPC', 'vpc': 'VPC', 'red': 'VPC',
            '6': 'VPN', 'vpn': 'VPN',
            '7': 'ELB', 'elb': 'ELB', 'balanceador': 'ELB',
            '8': 'CloudFront', 'cloudfront': 'CloudFront', 'cdn': 'CloudFront',
            '9': 'Route53', 'route53': 'Route53', 'dns': 'Route53',
            '10': 'SSO', 'sso': 'SSO',
            '11': 'Backup', 'backup': 'Backup', 'respaldo': 'Backup',
            '12': 'CloudWatch', 'cloudwatch': 'CloudWatch', 'monitoreo': 'CloudWatch',
            '13': 'SES', 'ses': 'SES', 'email': 'SES'
        }
        
        for key, service in service_map.items():
            if key in user_input_lower:
                services.append(service)
        
        return services if services else ['General']
    
    def _generate_service_questions(self, services: List[str]) -> List[str]:
        """Generate minimal questions for selected services"""
        questions = []
        
        for service in services:
            if service == 'EC2':
                questions.extend([
                    "¿Cuantas instancias EC2 necesitas?",
                    "¿Que tipo de instancia prefieres? (t3.micro, t3.small, m5.large, etc.)"
                ])
            elif service == 'RDS':
                questions.extend([
                    "¿Que motor de base de datos necesitas? (MySQL, PostgreSQL, SQL Server, etc.)",
                    "¿Tamaño estimado de la base de datos?"
                ])
            elif service == 'S3':
                questions.extend([
                    "¿Para que usaras S3? (backup, hosting web, data lake, etc.)",
                    "¿Volumen estimado de datos?"
                ])
            # Add more service-specific questions as needed
        
        if not questions:
            questions = [
                "Describe los requerimientos especificos del servicio:",
                "¿Hay alguna configuracion particular que necesites?"
            ]
        
        return questions
    
    def _cors_response(self) -> Dict[str, Any]:
        """Return CORS preflight response"""
        return {
            'statusCode': 200,
            'headers': self._get_cors_headers(),
            'body': ''
        }
    
    def _get_cors_headers(self) -> Dict[str, str]:
        """Get CORS headers"""
        return {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
            'Content-Type': 'application/json'
        }

# Initialize the architect
architect = AWSArchitect()

def lambda_handler(event, context):
    """Lambda entry point"""
    return architect.lambda_handler(event, context)
