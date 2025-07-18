import json
import urllib3
from typing import Dict, List, Any, Optional
import re

class SmartMCPHandler:
    """
    Smart MCP Handler - Activates MCP services only when contextually needed
    Similar to Amazon Q CLI Developer approach
    """
    
    def __init__(self):
        # Use urllib3 instead of requests to avoid Lambda issues
        self.http = urllib3.PoolManager()
        
        # MCP service endpoints
        self.mcp_services = {
            'document_generator': "https://mcp.danielingram.shop/customdoc",
            'cloudformation': "https://mcp.danielingram.shop/cfn", 
            'pricing': "https://mcp.danielingram.shop/pricing",
            'diagram': "https://mcp.danielingram.shop/diagram"
        }
        
        # Context detection patterns
        self.context_patterns = {
            'document_generation': [
                r'\b(documento|documentación|propuesta|informe|reporte)\b',
                r'\b(generar|crear|elaborar).*(documento|propuesta)\b',
                r'\b(necesito|quiero).*(documento|documentación)\b'
            ],
            'cloudformation': [
                r'\b(cloudformation|template|infraestructura|despliegue)\b',
                r'\b(crear|generar).*(template|infraestructura)\b',
                r'\b(iac|infrastructure as code)\b'
            ],
            'pricing': [
                r'\b(precio|costo|presupuesto|estimación|coste)\b',
                r'\b(cuánto|cuanto).*(cuesta|costar)\b',
                r'\b(análisis de costos|estimación de precios)\b'
            ],
            'diagram': [
                r'\b(diagrama|arquitectura|esquema|diseño)\b',
                r'\b(mostrar|visualizar).*(arquitectura|diseño)\b',
                r'\b(crear|generar).*(diagrama|esquema)\b'
            ]
        }
    
    def detect_needed_services(self, conversation_context: str, project_data: Dict = None) -> List[str]:
        """
        Detect which MCP services are needed based on conversation context
        """
        needed_services = []
        context_lower = conversation_context.lower()
        
        for service_type, patterns in self.context_patterns.items():
            for pattern in patterns:
                if re.search(pattern, context_lower, re.IGNORECASE):
                    needed_services.append(service_type)
                    break
        
        # Additional logic based on project data
        if project_data:
            if project_data.get('services') and 'cloudformation' not in needed_services:
                # If we have services defined, likely need CloudFormation
                needed_services.append('cloudformation')
            
            if project_data.get('budget_required') and 'pricing' not in needed_services:
                needed_services.append('pricing')
        
        return list(set(needed_services))  # Remove duplicates
    
    def call_mcp_service(self, service_name: str, data: Dict) -> Dict:
        """
        Call a specific MCP service
        """
        if service_name not in self.mcp_services:
            return {"error": f"Unknown service: {service_name}"}
        
        url = self.mcp_services[service_name]
        
        try:
            response = self.http.request(
                'POST',
                url,
                body=json.dumps(data),
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status == 200:
                return json.loads(response.data.decode('utf-8'))
            else:
                return {"error": f"MCP service error: {response.status}"}
                
        except Exception as e:
            return {"error": f"Failed to call MCP service {service_name}: {str(e)}"}
    
    def generate_document(self, project_data: Dict) -> Dict:
        """Generate document using MCP document generator"""
        mcp_data = {
            "project_name": project_data.get('name', 'Proyecto AWS'),
            "description": project_data.get('description', ''),
            "requirements": project_data.get('requirements', []),
            "architecture": project_data.get('architecture', {}),
            "services": project_data.get('services', []),
            "budget": project_data.get('budget', 'No especificado'),
            "timeline": project_data.get('timeline', 'No especificado')
        }
        
        return self.call_mcp_service('document_generator', mcp_data)
    
    def generate_cloudformation(self, project_data: Dict) -> Dict:
        """Generate CloudFormation template using MCP"""
        mcp_data = {
            "project_name": project_data.get('name', 'Proyecto AWS'),
            "services": project_data.get('services', []),
            "architecture": project_data.get('architecture', {}),
            "requirements": project_data.get('requirements', []),
            "region": project_data.get('region', 'us-east-1')
        }
        
        return self.call_mcp_service('cloudformation', mcp_data)
    
    def analyze_pricing(self, project_data: Dict) -> Dict:
        """Analyze pricing using MCP pricing service"""
        mcp_data = {
            "services": project_data.get('services', []),
            "region": project_data.get('region', 'us-east-1'),
            "usage_patterns": project_data.get('usage_patterns', {}),
            "estimated_users": project_data.get('estimated_users', 1000),
            "data_transfer": project_data.get('data_transfer', '1TB')
        }
        
        return self.call_mcp_service('pricing', mcp_data)
    
    def generate_diagram(self, project_data: Dict) -> Dict:
        """Generate architecture diagram using MCP"""
        mcp_data = {
            "project_name": project_data.get('name', 'Proyecto AWS'),
            "architecture": project_data.get('architecture', {}),
            "services": project_data.get('services', []),
            "connections": project_data.get('connections', []),
            "diagram_type": "aws_architecture"
        }
        
        return self.call_mcp_service('diagram', mcp_data)
    
    def process_smart_request(self, user_message: str, project_data: Dict = None, conversation_history: List = None) -> Dict:
        """
        Main method - intelligently process request and activate needed MCP services
        """
        # Build conversation context
        context = user_message
        if conversation_history:
            context += " " + " ".join([msg.get('content', '') for msg in conversation_history[-3:]])
        
        # Detect needed services
        needed_services = self.detect_needed_services(context, project_data)
        
        results = {
            'services_activated': needed_services,
            'mcp_results': {},
            'artifacts_generated': []
        }
        
        # Activate needed services
        if project_data:
            if 'document_generation' in needed_services:
                doc_result = self.generate_document(project_data)
                if 'error' not in doc_result:
                    results['mcp_results']['document'] = doc_result
                    results['artifacts_generated'].append('document')
            
            if 'cloudformation' in needed_services:
                cfn_result = self.generate_cloudformation(project_data)
                if 'error' not in cfn_result:
                    results['mcp_results']['cloudformation'] = cfn_result
                    results['artifacts_generated'].append('cloudformation')
            
            if 'pricing' in needed_services:
                pricing_result = self.analyze_pricing(project_data)
                if 'error' not in pricing_result:
                    results['mcp_results']['pricing'] = pricing_result
                    results['artifacts_generated'].append('pricing')
            
            if 'diagram' in needed_services:
                diagram_result = self.generate_diagram(project_data)
                if 'error' not in diagram_result:
                    results['mcp_results']['diagram'] = diagram_result
                    results['artifacts_generated'].append('diagram')
        
        return results

# Global instance
smart_mcp = SmartMCPHandler()
