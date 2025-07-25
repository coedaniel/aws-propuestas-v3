"""
Manejo de conversación inteligente como Amazon Q CLI
Sigue el flujo exacto definido en el prompt del sistema
"""
import logging
import re

logger = logging.getLogger()

class ConversationState:
    def __init__(self):
        self.required_fields = {
            'name': False,
            'type': False,
            'services': False,
            'requirements': False
        }
        self.current_step = 'name'  # Empezar siempre pidiendo el nombre
        self.project_data = {}
        self.solution_type = None  # 'integral' o 'rapido'
        
    def validate_state(self, messages, project_state):
        """Valida el estado actual de la conversación de forma inteligente"""
        
        # Obtener mensajes del usuario solamente
        user_messages = [msg for msg in messages if msg.get('role') == 'user']
        if not user_messages:
            return False
            
        last_user_message = user_messages[-1].get('content', '').strip()
        conversation_text = ' '.join([msg.get('content', '') for msg in user_messages]).lower()
        
        logger.info(f"Procesando mensaje: {last_user_message}")
        logger.info(f"Paso actual: {self.current_step}")
        
        # PASO 1: Validar nombre del proyecto
        if self.current_step == 'name' and last_user_message:
            # Filtrar saludos comunes
            greetings = ['hola', 'hi', 'hello', 'que tal', 'buenas', 'buenos dias', 'buenas tardes']
            if not any(greeting in last_user_message.lower() for greeting in greetings) and len(last_user_message) > 2:
                self.required_fields['name'] = True
                self.project_data['name'] = last_user_message
                project_state['name'] = last_user_message
                project_state['phase'] = 'tipo'
                self.current_step = 'type'
                logger.info(f"Nombre del proyecto capturado: {last_user_message}")
                
        # PASO 2: Validar tipo de solución
        elif self.current_step == 'type' and last_user_message:
            # Detectar si es solución integral
            integral_keywords = [
                'integral', 'migracion', 'aplicacion nueva', 'modernizacion', 'analitica', 
                'seguridad', 'ia', 'iot', 'data lake', 'networking', 'drp', 'vdi', 'integracion',
                'completa', 'complejo', 'arquitectura', 'sistema completo'
            ]
            
            # Detectar si es servicio rápido
            rapido_keywords = [
                'rapido', 'especifico', 'ec2', 'rds', 'ses', 'vpn', 'elb', 's3', 'vpc', 
                'cloudfront', 'sso', 'backup', 'simple', 'basico', 'individual'
            ]
            
            message_lower = last_user_message.lower()
            
            if any(keyword in message_lower for keyword in integral_keywords):
                self.solution_type = 'integral'
                self.required_fields['type'] = True
                self.project_data['type'] = 'integral'
                project_state['type'] = 'integral'
                project_state['phase'] = 'recopilacion'
                self.current_step = 'integral_interview'
                logger.info("Tipo detectado: Solución Integral")
                
            elif any(keyword in message_lower for keyword in rapido_keywords):
                self.solution_type = 'rapido'
                self.required_fields['type'] = True
                self.project_data['type'] = 'rapido'
                project_state['type'] = 'rapido'
                project_state['phase'] = 'recopilacion'
                self.current_step = 'services'
                logger.info("Tipo detectado: Servicio Rápido")
                
        # PASO 3A: Para servicios rápidos - capturar servicios
        elif self.current_step == 'services' and self.solution_type == 'rapido' and last_user_message:
            # Extraer servicios AWS mencionados
            aws_services = self._extract_aws_services(last_user_message)
            
            if aws_services or len(last_user_message) > 5:
                self.required_fields['services'] = True
                self.project_data['services'] = aws_services if aws_services else [last_user_message]
                project_state['services'] = self.project_data['services']
                self.current_step = 'requirements_rapido'
                logger.info(f"Servicios capturados: {self.project_data['services']}")
                
        # PASO 3B: Para servicios rápidos - capturar requerimientos mínimos
        elif self.current_step == 'requirements_rapido' and last_user_message:
            if len(last_user_message) > 10:
                self.required_fields['requirements'] = True
                self.project_data['requirements'] = last_user_message
                project_state['requirements'] = last_user_message
                project_state['phase'] = 'generacion'
                self.current_step = 'generate_rapido'
                logger.info("Requerimientos rápidos capturados, listo para generar")
                
        # PASO 3C: Para soluciones integrales - entrevista guiada
        elif self.current_step == 'integral_interview':
            self._process_integral_interview(last_user_message, project_state)
            
        return self.is_ready_to_generate()
        
    def _extract_aws_services(self, text):
        """Extrae servicios AWS del texto del usuario"""
        aws_services = []
        service_patterns = {
            'EC2': ['ec2', 'instancia', 'servidor', 'virtual machine', 'vm'],
            'RDS': ['rds', 'base de datos', 'database', 'mysql', 'postgres', 'sql'],
            'S3': ['s3', 'almacenamiento', 'storage', 'bucket'],
            'Lambda': ['lambda', 'serverless', 'funcion'],
            'API Gateway': ['api gateway', 'api', 'rest api'],
            'DynamoDB': ['dynamodb', 'nosql', 'dynamo'],
            'CloudFront': ['cloudfront', 'cdn', 'distribucion'],
            'VPC': ['vpc', 'red', 'network', 'networking'],
            'ELB': ['elb', 'load balancer', 'balanceador'],
            'SES': ['ses', 'email', 'correo'],
            'SNS': ['sns', 'notificacion', 'notification'],
            'SQS': ['sqs', 'cola', 'queue']
        }
        
        text_lower = text.lower()
        for service, keywords in service_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                aws_services.append(service)
                
        return aws_services
        
    def _process_integral_interview(self, message, project_state):
        """Procesa la entrevista para soluciones integrales"""
        # Aquí implementarías la lógica de entrevista paso a paso
        # Por ahora, simplificamos para que funcione
        if len(message) > 20:
            self.required_fields['requirements'] = True
            self.project_data['requirements'] = message
            project_state['requirements'] = message
            project_state['phase'] = 'generacion'
            self.current_step = 'generate_integral'
            logger.info("Entrevista integral completada, listo para generar")
        
    def is_complete(self):
        """Verifica si tenemos toda la información necesaria"""
        return all(self.required_fields.values())
        
    def is_ready_to_generate(self):
        """Verifica si estamos listos para generar documentos"""
        return self.current_step in ['generate_rapido', 'generate_integral']
        
    def get_next_question(self):
        """Retorna la siguiente pregunta basada en el estado actual"""
        if self.current_step == 'name':
            return "¿Cual es el nombre del proyecto?"
            
        elif self.current_step == 'type':
            return """¿El proyecto es una solucion integral (como migracion, aplicacion nueva, modernizacion, analitica, seguridad, IA, IoT, data lake, networking, DRP, VDI, integracion, etc.)?

¿O es un servicio rapido especifico (como EC2, RDS, SES, VPN, ELB, S3, VPC, CloudFront, SSO, backup, etc.)?"""
            
        elif self.current_step == 'services' and self.solution_type == 'rapido':
            return """Perfecto! Para el servicio rapido, ¿que servicios AWS especificos necesitas?

Algunos servicios comunes:
• EC2 (instancias virtuales)
• RDS (bases de datos)
• S3 (almacenamiento)
• VPC (redes)
• ELB (balanceadores)
• CloudFront (CDN)
• SES (email)

Puedes escribir los que necesites o describir tu caso de uso."""
            
        elif self.current_step == 'requirements_rapido':
            services = ', '.join(self.project_data.get('services', []))
            return f"""Excelente! Para implementar {services}, necesito saber los requerimientos minimos:

• ¿Cuantos usuarios aproximadamente?
• ¿Que region de AWS prefieres?
• ¿Algun requerimiento especial de seguridad o rendimiento?

Con esta informacion generare todos los documentos automaticamente."""
            
        elif self.current_step == 'integral_interview':
            return """Perfecto! Para la solucion integral, necesito mas detalles:

• ¿Cual es el objetivo principal del proyecto?
• ¿Que sistemas o aplicaciones estan involucrados?
• ¿Tienes requisitos especificos de rendimiento, seguridad o cumplimiento?
• ¿Cuantos usuarios aproximadamente manejara?

Puedes responder todo junto o paso a paso."""
            
        elif self.current_step in ['generate_rapido', 'generate_integral']:
            return "Perfecto! Tengo toda la informacion necesaria. Voy a generar todos los documentos profesionales para tu proyecto. Esto incluira diagramas, scripts CloudFormation, costos estimados y documentacion completa."
            
        return "Continuemos con el siguiente paso..."
        
    def get_completion_percentage(self):
        """Calcula el porcentaje de completitud"""
        if self.solution_type == 'rapido':
            required_for_rapido = ['name', 'type', 'services', 'requirements']
            completed = sum(1 for field in required_for_rapido if self.required_fields.get(field, False))
            return (completed / len(required_for_rapido)) * 100
        else:
            completed = sum(1 for v in self.required_fields.values() if v)
            total = len(self.required_fields)
            return (completed / total) * 100
        
    def get_missing_fields(self):
        """Retorna lista de campos faltantes"""
        return [k for k, v in self.required_fields.items() if not v]
        
    def should_activate_mcp(self):
        """Determina si debe activar servicios MCP para generar documentos"""
        return self.is_ready_to_generate()
        
    def get_mcp_services_needed(self):
        """Retorna lista de servicios MCP necesarios"""
        if self.is_ready_to_generate():
            return ['diagram', 'cloudformation', 'pricing', 'documentation']
        return []
