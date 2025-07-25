"""
Amazon Q CLI Intelligent Architect - Análisis profundo de sistemas AWS
Usa todos los MCP servers disponibles para análisis completo
"""
import logging
import re

logger = logging.getLogger()

class ConversationState:
    def __init__(self):
        self.analysis_complete = False
        self.project_data = {}
        self.system_analysis = {}
        self.current_phase = 'initial_analysis'  # initial_analysis -> deep_analysis -> solution_design
        
    def restore_from_project_state(self, project_state):
        """Restaura el estado de la conversación desde projectState"""
        if not project_state:
            return
            
        # Restaurar datos del análisis
        if 'name' in project_state:
            self.project_data['name'] = project_state['name']
            
        if 'analysis_complete' in project_state:
            self.analysis_complete = project_state['analysis_complete']
            
        if 'system_analysis' in project_state:
            self.system_analysis = project_state['system_analysis']
            
        if 'phase' in project_state:
            self.current_phase = project_state['phase']
            
        logger.info(f"Estado restaurado - Fase: {self.current_phase}, Análisis: {self.analysis_complete}")
        
    def should_trigger_intelligent_analysis(self, messages, project_state):
        """
        Determina si debe activar el análisis inteligente completo
        Como Amazon Q CLI, debe analizar el contexto completo del usuario
        """
        
        # Obtener mensajes del usuario solamente
        user_messages = [msg for msg in messages if msg.get('role') == 'user']
        if not user_messages:
            return False
            
        last_user_message = user_messages[-1].get('content', '').strip()
        conversation_text = ' '.join([msg.get('content', '') for msg in user_messages]).lower()
        
        logger.info(f"Analizando mensaje para inteligencia: {last_user_message}")
        
        # ACTIVAR ANÁLISIS INTELIGENTE SIEMPRE que el usuario escriba algo sustancial
        # Como Amazon Q CLI, debe ser proactivo y analizar cualquier consulta
        
        # Filtrar saludos muy básicos
        basic_greetings = ['hola', 'hi', 'hello', 'hey']
        if len(last_user_message.strip()) <= 5 and any(greeting in last_user_message.lower() for greeting in basic_greetings):
            return False
            
        # Si el usuario escribió algo más que un saludo básico, activar análisis
        if len(last_user_message.strip()) > 2:
            logger.info("🧠 Activando análisis inteligente - Usuario proporcionó información")
            
            # Extraer nombre del proyecto si es posible
            if not self.project_data.get('name'):
                # Usar el primer mensaje sustancial como nombre del proyecto
                self.project_data['name'] = last_user_message.strip()
                project_state['name'] = last_user_message.strip()
            
            self.current_phase = 'intelligent_analysis'
            project_state['phase'] = 'intelligent_analysis'
            project_state['trigger_intelligent_analysis'] = True
            return True
            
        return False
        
    def get_intelligent_analysis_prompt(self):
        """
        Retorna el prompt para activar el análisis inteligente completo
        """
        project_name = self.project_data.get('name', 'tu proyecto')
        
        return f"""¡Perfecto! Como tu Arquitecto AWS experto, voy a hacer un análisis profundo y completo de {project_name}.

🧠 **ANÁLISIS INTELIGENTE ACTIVADO**

Voy a usar todos los MCP servers disponibles para:

✅ **Análisis de Sistema Actual:**
- Revisar tu arquitectura AWS existente
- Identificar servicios en uso (Lambda, ECS, RDS, etc.)
- Analizar configuraciones y dependencias
- Detectar problemas y cuellos de botella

✅ **Análisis de Código y Repositorios:**
- Examinar estructura de proyectos
- Identificar tecnologías y frameworks
- Revisar configuraciones SAM/CDK/Terraform
- Analizar pipelines CI/CD

✅ **Diagnóstico de Problemas:**
- Identificar qué está fallando
- Analizar logs y métricas
- Detectar configuraciones subóptimas
- Encontrar oportunidades de mejora

✅ **Diseño de Solución:**
- Proponer arquitectura optimizada
- Calcular costos y dimensionamiento
- Generar diagramas y documentación
- Crear scripts de implementación

Dame un momento mientras ejecuto el análisis completo usando mis herramientas MCP..."""

    def is_ready_to_generate(self):
        """Determina si está listo para generar documentos"""
        return self.analysis_complete
        
    def get_completion_percentage(self):
        """Calcula el porcentaje de completitud del análisis"""
        if self.current_phase == 'initial_analysis':
            return 10
        elif self.current_phase == 'intelligent_analysis':
            return 50
        elif self.analysis_complete:
            return 100
        return 0
        
    def get_missing_fields(self):
        """Retorna campos faltantes"""
        if not self.analysis_complete:
            return ['Análisis completo del sistema']
        return []
