"""
Manejo de conversación y validación de estado
"""
import logging

logger = logging.getLogger()

class ConversationState:
    def __init__(self):
        self.required_fields = {
            'name': False,
            'type': False,
            'services': False,
            'requirements': False
        }
        self.current_step = 'initial'
        self.project_data = {}
        
    def validate_state(self, messages, project_state):
        """Valida el estado actual de la conversación"""
        conversation = ' '.join([msg.get('content', '').lower() for msg in messages])
        
        # Validar nombre del proyecto
        if project_state.get('name'):
            self.required_fields['name'] = True
            self.project_data['name'] = project_state['name']
            
        # Validar tipo de proyecto
        if 'solucion integral' in conversation or 'servicio rapido' in conversation:
            self.required_fields['type'] = True
            self.project_data['type'] = 'integral' if 'solucion integral' in conversation else 'rapido'
            
        # Validar servicios
        if project_state.get('services') and len(project_state['services']) > 0:
            self.required_fields['services'] = True
            self.project_data['services'] = project_state['services']
            
        # Validar requerimientos
        if project_state.get('requirements') and len(project_state['requirements']) > 0:
            self.required_fields['requirements'] = True
            self.project_data['requirements'] = project_state['requirements']
            
        # Determinar paso actual
        if not self.required_fields['name']:
            self.current_step = 'name'
        elif not self.required_fields['type']:
            self.current_step = 'type'
        elif not self.required_fields['services']:
            self.current_step = 'services'
        elif not self.required_fields['requirements']:
            self.current_step = 'requirements'
        else:
            self.current_step = 'complete'
            
        return self.is_complete()
        
    def is_complete(self):
        """Verifica si tenemos toda la información necesaria"""
        return all(self.required_fields.values())
        
    def get_next_question(self):
        """Retorna la siguiente pregunta basada en el estado actual"""
        if self.current_step == 'name':
            return "¿Cuál es el nombre del proyecto?"
            
        elif self.current_step == 'type':
            return """¿El proyecto es una solucion integral (como migracion, aplicacion nueva, modernizacion, analitica, seguridad, IA, IoT, data lake, networking, DRP, VDI, integracion, etc.)?
¿O es un servicio rapido especifico (como EC2, RDS, SES, VPN, ELB, S3, VPC, CloudFront, SSO, backup, etc.)?"""
            
        elif self.current_step == 'services':
            return "¿Qué servicios AWS específicos necesitas para este proyecto?"
            
        elif self.current_step == 'requirements':
            if self.project_data.get('type') == 'rapido':
                services = ', '.join(self.project_data.get('services', []))
                return f"Para implementar {services}, necesito saber los requerimientos específicos:"
            else:
                return """Para diseñar la solución integral, necesito saber:
- ¿Cuáles son los objetivos principales del proyecto?
- ¿Qué sistemas o aplicaciones están involucrados?
- ¿Tienes requisitos específicos de rendimiento o escalabilidad?
- ¿Hay consideraciones especiales de seguridad o cumplimiento?"""
                
        return None
        
    def get_completion_percentage(self):
        """Calcula el porcentaje de completitud"""
        completed = sum(1 for v in self.required_fields.values() if v)
        total = len(self.required_fields)
        return (completed / total) * 100
        
    def get_missing_fields(self):
        """Retorna lista de campos faltantes"""
        return [k for k, v in self.required_fields.items() if not v]
