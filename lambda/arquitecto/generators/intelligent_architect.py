"""
Sistema de Arquitecto Inteligente para AWS Propuestas v3
Maneja conversaciones dinámicas y genera documentos reales basados en respuestas del modelo
"""

import json
import re
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger()

class IntelligentArchitect:
    """
    Arquitecto inteligente que maneja conversaciones dinámicas y extrae información real
    """
    
    def __init__(self):
        self.required_info = {
            'business_context': {
                'company_info': None,
                'industry': None,
                'business_goals': None,
                'current_challenges': None
            },
            'technical_requirements': {
                'current_infrastructure': None,
                'expected_load': None,
                'performance_requirements': None,
                'security_requirements': None,
                'compliance_needs': None
            },
            'solution_scope': {
                'project_type': None,
                'aws_services_needed': [],
                'integration_requirements': None,
                'data_requirements': None
            },
            'project_constraints': {
                'budget_range': None,
                'timeline': None,
                'team_expertise': None,
                'maintenance_preferences': None
            }
        }
    
    def analyze_conversation_intent(self, user_message: str, conversation_history: List[Dict]) -> Dict[str, Any]:
        """
        Analiza la intención del usuario y determina qué información se puede extraer
        """
        intent_analysis = {
            'detected_intents': [],
            'extracted_info': {},
            'missing_critical_info': [],
            'suggested_questions': [],
            'conversation_stage': 'discovery'
        }
        
        # Detectar intenciones comunes
        user_lower = user_message.lower()
        
        # Intención de inicio de proyecto
        if any(keyword in user_lower for keyword in ['quiero', 'necesito', 'proyecto', 'implementar', 'migrar']):
            intent_analysis['detected_intents'].append('project_initiation')
        
        # Intención técnica
        if any(keyword in user_lower for keyword in ['servidor', 'base de datos', 'aplicación', 'api', 'web']):
            intent_analysis['detected_intents'].append('technical_specification')
        
        # Intención de negocio
        if any(keyword in user_lower for keyword in ['empresa', 'negocio', 'clientes', 'ventas', 'crecimiento']):
            intent_analysis['detected_intents'].append('business_context')
        
        # Intención de costos
        if any(keyword in user_lower for keyword in ['costo', 'precio', 'presupuesto', 'barato', 'económico']):
            intent_analysis['detected_intents'].append('cost_concern')
        
        # Extraer información específica del mensaje
        extracted_info = self.extract_specific_information(user_message)
        intent_analysis['extracted_info'] = extracted_info
        
        # Determinar qué información falta
        missing_info = self.identify_missing_information(extracted_info, conversation_history)
        intent_analysis['missing_critical_info'] = missing_info
        
        # Generar preguntas inteligentes
        questions = self.generate_intelligent_questions(missing_info, intent_analysis['detected_intents'])
        intent_analysis['suggested_questions'] = questions
        
        # Determinar etapa de conversación
        stage = self.determine_conversation_stage(conversation_history, extracted_info)
        intent_analysis['conversation_stage'] = stage
        
        return intent_analysis
    
    def extract_specific_information(self, message: str) -> Dict[str, Any]:
        """
        Extrae información específica del mensaje del usuario usando NLP básico
        """
        extracted = {}
        message_lower = message.lower()
        
        # Extraer tipo de empresa/industria
        industry_patterns = {
            'ecommerce': ['tienda', 'ecommerce', 'e-commerce', 'venta online', 'marketplace'],
            'fintech': ['banco', 'fintech', 'financiero', 'pagos', 'transacciones'],
            'healthcare': ['salud', 'hospital', 'médico', 'pacientes', 'clínica'],
            'education': ['educación', 'universidad', 'escuela', 'estudiantes', 'cursos'],
            'manufacturing': ['manufactura', 'fábrica', 'producción', 'industrial'],
            'retail': ['retail', 'tienda física', 'sucursales', 'inventario'],
            'logistics': ['logística', 'transporte', 'envíos', 'almacén', 'distribución']
        }
        
        for industry, keywords in industry_patterns.items():
            if any(keyword in message_lower for keyword in keywords):
                extracted['industry'] = industry
                break
        
        # Extraer servicios AWS mencionados
        aws_services = []
        service_patterns = {
            'ec2': ['servidor', 'máquina virtual', 'vm', 'instancia', 'ec2'],
            'rds': ['base de datos', 'mysql', 'postgresql', 'sql', 'rds'],
            's3': ['almacenamiento', 'archivos', 'documentos', 's3', 'bucket'],
            'lambda': ['función', 'serverless', 'lambda', 'sin servidor'],
            'api_gateway': ['api', 'rest', 'endpoint', 'gateway'],
            'cloudfront': ['cdn', 'distribución', 'cache', 'cloudfront'],
            'route53': ['dns', 'dominio', 'route53'],
            'elb': ['balanceador', 'load balancer', 'elb', 'alb'],
            'ecs': ['contenedor', 'docker', 'ecs', 'fargate'],
            'eks': ['kubernetes', 'k8s', 'eks']
        }
        
        for service, keywords in service_patterns.items():
            if any(keyword in message_lower for keyword in keywords):
                aws_services.append(service)
        
        if aws_services:
            extracted['aws_services'] = aws_services
        
        # Extraer información de escala/carga
        scale_patterns = {
            'small': ['pequeño', 'pocos usuarios', 'startup', 'comenzando'],
            'medium': ['mediano', 'creciendo', 'miles de usuarios'],
            'large': ['grande', 'millones', 'alta demanda', 'enterprise']
        }
        
        for scale, keywords in scale_patterns.items():
            if any(keyword in message_lower for keyword in keywords):
                extracted['expected_scale'] = scale
                break
        
        # Extraer información de presupuesto
        budget_patterns = {
            'low': ['barato', 'económico', 'poco presupuesto', 'startup'],
            'medium': ['moderado', 'razonable', 'medio'],
            'high': ['sin límite', 'enterprise', 'gran presupuesto']
        }
        
        for budget, keywords in budget_patterns.items():
            if any(keyword in message_lower for keyword in keywords):
                extracted['budget_indication'] = budget
                break
        
        # Extraer timeline
        if 'urgente' in message_lower or 'rápido' in message_lower:
            extracted['timeline'] = 'urgent'
        elif 'meses' in message_lower:
            extracted['timeline'] = 'months'
        elif 'semanas' in message_lower:
            extracted['timeline'] = 'weeks'
        
        return extracted
    
    def identify_missing_information(self, extracted_info: Dict, conversation_history: List[Dict]) -> List[str]:
        """
        Identifica qué información crítica falta para completar la propuesta
        """
        missing = []
        
        # Información de negocio crítica
        if not extracted_info.get('industry') and not self._has_business_context(conversation_history):
            missing.append('business_context')
        
        # Servicios AWS específicos
        if not extracted_info.get('aws_services') and not self._has_technical_requirements(conversation_history):
            missing.append('technical_requirements')
        
        # Escala del proyecto
        if not extracted_info.get('expected_scale') and not self._has_scale_info(conversation_history):
            missing.append('project_scale')
        
        # Presupuesto o restricciones
        if not extracted_info.get('budget_indication') and not self._has_budget_info(conversation_history):
            missing.append('budget_constraints')
        
        return missing
    
    def generate_intelligent_questions(self, missing_info: List[str], detected_intents: List[str]) -> List[str]:
        """
        Genera preguntas inteligentes basadas en lo que falta y las intenciones detectadas
        """
        questions = []
        
        if 'business_context' in missing_info:
            if 'project_initiation' in detected_intents:
                questions.append("¿Podrías contarme más sobre tu empresa y el sector en el que operan?")
            else:
                questions.append("¿Cuál es el contexto de negocio de este proyecto?")
        
        if 'technical_requirements' in missing_info:
            if 'technical_specification' in detected_intents:
                questions.append("¿Qué tipo de aplicación o sistema necesitas implementar específicamente?")
            else:
                questions.append("¿Cuáles son los requerimientos técnicos principales del proyecto?")
        
        if 'project_scale' in missing_info:
            questions.append("¿Cuántos usuarios o qué volumen de datos esperas manejar?")
        
        if 'budget_constraints' in missing_info:
            questions.append("¿Tienes alguna restricción de presupuesto o preferencias de costos?")
        
        return questions
    
    def determine_conversation_stage(self, conversation_history: List[Dict], extracted_info: Dict) -> str:
        """
        Determina en qué etapa está la conversación
        """
        if len(conversation_history) <= 2:
            return 'initial_discovery'
        
        info_completeness = len(extracted_info)
        
        if info_completeness < 2:
            return 'discovery'
        elif info_completeness < 4:
            return 'requirements_gathering'
        else:
            return 'solution_design'
    
    def generate_dynamic_prompt(self, user_message: str, conversation_history: List[Dict], 
                              project_info: Dict) -> str:
        """
        Genera un prompt dinámico basado en el análisis de la conversación
        """
        intent_analysis = self.analyze_conversation_intent(user_message, conversation_history)
        
        # Construir contexto dinámico
        context_parts = []
        
        # Información ya conocida
        if project_info:
            context_parts.append(f"INFORMACIÓN CONOCIDA DEL PROYECTO:\n{json.dumps(project_info, indent=2, ensure_ascii=False)}")
        
        # Información extraída del mensaje actual
        if intent_analysis['extracted_info']:
            context_parts.append(f"NUEVA INFORMACIÓN DETECTADA:\n{json.dumps(intent_analysis['extracted_info'], indent=2, ensure_ascii=False)}")
        
        # Etapa de conversación
        context_parts.append(f"ETAPA DE CONVERSACIÓN: {intent_analysis['conversation_stage']}")
        
        # Información faltante crítica
        if intent_analysis['missing_critical_info']:
            context_parts.append(f"INFORMACIÓN FALTANTE CRÍTICA: {', '.join(intent_analysis['missing_critical_info'])}")
        
        context = "\n\n".join(context_parts)
        
        # Prompt principal adaptativo
        base_prompt = f"""Eres un Arquitecto de Soluciones AWS experto y consultor senior. Tu objetivo es mantener una conversación natural y profesional para diseñar la mejor solución AWS para el cliente.

CONTEXTO ACTUAL:
{context}

INSTRUCCIONES DINÁMICAS:
1. **Conversación Natural**: Responde de manera conversacional, como un arquitecto real
2. **Adaptabilidad**: No sigas un guion rígido - adapta tu respuesta a lo que el usuario dice
3. **Extracción Inteligente**: Identifica y confirma información técnica y de negocio
4. **Preguntas Estratégicas**: Haz preguntas específicas solo cuando sea necesario
5. **Propuesta Progresiva**: Ve construyendo la solución gradualmente

MENSAJE DEL USUARIO: {user_message}

RESPUESTA ESPERADA:
- Si es el inicio: Saluda profesionalmente y haz 1-2 preguntas clave
- Si hay información técnica: Confirma y profundiza en aspectos específicos
- Si falta información crítica: Pregunta de manera natural
- Si tienes suficiente información: Comienza a proponer soluciones específicas
- Si el proyecto está completo: Indica que procederás a generar los documentos

Mantén un tono profesional pero cercano, como un consultor experimentado."""
        
        return base_prompt
    
    def _has_business_context(self, conversation_history: List[Dict]) -> bool:
        """Verifica si ya se tiene contexto de negocio"""
        for msg in conversation_history:
            content = msg.get('content', '').lower()
            if any(word in content for word in ['empresa', 'negocio', 'industria', 'sector']):
                return True
        return False
    
    def _has_technical_requirements(self, conversation_history: List[Dict]) -> bool:
        """Verifica si ya se tienen requerimientos técnicos"""
        for msg in conversation_history:
            content = msg.get('content', '').lower()
            if any(word in content for word in ['servidor', 'base de datos', 'aplicación', 'api']):
                return True
        return False
    
    def _has_scale_info(self, conversation_history: List[Dict]) -> bool:
        """Verifica si ya se tiene información de escala"""
        for msg in conversation_history:
            content = msg.get('content', '').lower()
            if any(word in content for word in ['usuarios', 'carga', 'volumen', 'escala']):
                return True
        return False
    
    def _has_budget_info(self, conversation_history: List[Dict]) -> bool:
        """Verifica si ya se tiene información de presupuesto"""
        for msg in conversation_history:
            content = msg.get('content', '').lower()
            if any(word in content for word in ['presupuesto', 'costo', 'precio', 'barato']):
                return True
        return False
