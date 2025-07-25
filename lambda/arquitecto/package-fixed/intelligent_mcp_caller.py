"""
Intelligent MCP Caller - Como Amazon Q CLI
Activa MCP services automáticamente según el contexto
"""
import json
import logging
import requests
from typing import Dict, Any, List

logger = logging.getLogger()

class IntelligentMCPCaller:
    def __init__(self):
        self.mcp_endpoints = {
            'core': 'https://mcp.danielingram.shop/core',
            'diagram': 'https://mcp.danielingram.shop/diagram', 
            'pricing': 'https://mcp.danielingram.shop/pricing',
            'cfn': 'https://mcp.danielingram.shop/cfn',
            'awsdocs': 'https://mcp.danielingram.shop/awsdocs',
            'docgen': 'https://mcp.danielingram.shop/docgen'
        }
        
    def should_activate_mcps(self, project_data: Dict[str, Any]) -> bool:
        """Detecta si debe activar MCP services"""
        required_fields = ['name', 'type', 'services', 'requirements']
        return all(field in project_data and project_data[field] for field in required_fields)
    
    def get_intelligent_context(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera contexto inteligente para MCP calls"""
        return {
            "project_name": project_data.get('name', ''),
            "solution_type": project_data.get('type', ''),
            "aws_services": project_data.get('services', []),
            "requirements": project_data.get('requirements', ''),
            "user_intent": self._analyze_user_intent(project_data),
            "complexity_level": self._assess_complexity(project_data)
        }
    
    def _analyze_user_intent(self, project_data: Dict[str, Any]) -> str:
        """Analiza la intención del usuario"""
        solution_type = project_data.get('type', '').lower()
        requirements = project_data.get('requirements', '').lower()
        
        if 'integral' in solution_type:
            if any(keyword in requirements for keyword in ['migracion', 'migration', 'modernizacion']):
                return 'enterprise_migration'
            elif any(keyword in requirements for keyword in ['analitica', 'analytics', 'data']):
                return 'data_analytics'
            elif any(keyword in requirements for keyword in ['ia', 'ai', 'machine learning']):
                return 'ai_ml_solution'
            else:
                return 'enterprise_architecture'
        else:
            return 'quick_service'
    
    def _assess_complexity(self, project_data: Dict[str, Any]) -> str:
        """Evalúa la complejidad del proyecto"""
        services = project_data.get('services', [])
        requirements = project_data.get('requirements', '')
        
        if len(services) > 5 or len(requirements) > 200:
            return 'high'
        elif len(services) > 2 or len(requirements) > 100:
            return 'medium'
        else:
            return 'low'
    
    async def orchestrate_intelligent_generation(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Orquesta la generación inteligente como Amazon Q CLI"""
        if not self.should_activate_mcps(project_data):
            return {"error": "Datos insuficientes para activar MCP"}
        
        context = self.get_intelligent_context(project_data)
        results = {}
        
        try:
            # 1. SIEMPRE: Core MCP para prompt understanding
            logger.info("🧠 Activando Core MCP para prompt understanding...")
            core_result = await self._call_core_mcp_intelligent(context)
            results['core_analysis'] = core_result
            
            # 2. INTELIGENTE: Diagram MCP según servicios detectados
            logger.info("🎨 Activando Diagram MCP inteligentemente...")
            diagram_result = await self._call_diagram_mcp_intelligent(context, core_result)
            results['architecture_diagram'] = diagram_result
            
            # 3. INTELIGENTE: Pricing MCP con contexto específico
            logger.info("💰 Activando Pricing MCP con contexto...")
            pricing_result = await self._call_pricing_mcp_intelligent(context, core_result)
            results['cost_estimation'] = pricing_result
            
            # 4. INTELIGENTE: CloudFormation MCP
            logger.info("☁️ Activando CloudFormation MCP...")
            cfn_result = await self._call_cfn_mcp_intelligent(context, core_result)
            results['infrastructure_code'] = cfn_result
            
            # 5. CONDICIONAL: AWS Docs MCP si necesita documentación específica
            if self._needs_aws_documentation(context):
                logger.info("📚 Activando AWS Docs MCP...")
                docs_result = await self._call_awsdocs_mcp_intelligent(context)
                results['aws_documentation'] = docs_result
            
            # 6. SIEMPRE: Document Generator para archivos finales
            logger.info("📄 Activando Document Generator...")
            docgen_result = await self._call_docgen_intelligent(context, results)
            results['generated_documents'] = docgen_result
            
            return {
                "success": True,
                "project_name": project_data['name'],
                "mcp_services_used": list(results.keys()),
                "results": results,
                "generation_summary": self._create_generation_summary(results)
            }
            
        except Exception as e:
            logger.error(f"Error en orquestación MCP: {str(e)}")
            return {"error": f"Error generando documentos: {str(e)}"}
    
    async def _call_core_mcp_intelligent(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Llama Core MCP con prompt understanding"""
        payload = {
            "action": "prompt_understanding",
            "context": context,
            "request": f"Analiza este proyecto: {context['project_name']} - {context['solution_type']} con servicios {context['aws_services']}"
        }
        
        response = requests.post(
            self.mcp_endpoints['core'],
            json=payload,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"Core MCP falló: {response.status_code}")
            return {"analysis": "Análisis básico del proyecto", "recommendations": []}
    
    async def _call_diagram_mcp_intelligent(self, context: Dict[str, Any], core_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Llama Diagram MCP con contexto inteligente"""
        payload = {
            "project_name": context['project_name'],
            "services": context['aws_services'],
            "architecture_type": context['user_intent'],
            "complexity": context['complexity_level'],
            "core_recommendations": core_analysis.get('recommendations', [])
        }
        
        response = requests.post(
            self.mcp_endpoints['diagram'],
            json=payload,
            timeout=45,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"Diagram MCP falló: {response.status_code}")
            return {"diagram_url": None, "message": "Diagrama no generado"}
    
    async def _call_pricing_mcp_intelligent(self, context: Dict[str, Any], core_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Llama Pricing MCP con estimación inteligente"""
        payload = {
            "services": context['aws_services'],
            "usage_pattern": context['complexity_level'],
            "region": "us-east-1",
            "project_type": context['solution_type'],
            "estimated_users": self._extract_user_count(context['requirements'])
        }
        
        response = requests.post(
            self.mcp_endpoints['pricing'],
            json=payload,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"Pricing MCP falló: {response.status_code}")
            return {"monthly_cost": "No calculado", "breakdown": []}
    
    async def _call_cfn_mcp_intelligent(self, context: Dict[str, Any], core_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Llama CloudFormation MCP con template inteligente"""
        payload = {
            "project_name": context['project_name'],
            "services": context['aws_services'],
            "architecture_pattern": context['user_intent'],
            "best_practices": True,
            "security_enabled": True
        }
        
        response = requests.post(
            self.mcp_endpoints['cfn'],
            json=payload,
            timeout=60,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"CloudFormation MCP falló: {response.status_code}")
            return {"template": None, "message": "Template no generado"}
    
    async def _call_docgen_intelligent(self, context: Dict[str, Any], mcp_results: Dict[str, Any]) -> Dict[str, Any]:
        """Llama Document Generator con todos los resultados"""
        payload = {
            "project_name": context['project_name'],
            "project_type": context['solution_type'],
            "architecture_diagram": mcp_results.get('architecture_diagram', {}),
            "cost_estimation": mcp_results.get('cost_estimation', {}),
            "infrastructure_code": mcp_results.get('infrastructure_code', {}),
            "core_analysis": mcp_results.get('core_analysis', {}),
            "generate_formats": ["csv", "xlsx", "docx", "pdf", "txt"]
        }
        
        response = requests.post(
            self.mcp_endpoints['docgen'],
            json=payload,
            timeout=90,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"Document Generator falló: {response.status_code}")
            return {"documents": [], "message": "Documentos no generados"}
    
    async def _call_awsdocs_mcp_intelligent(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Llama AWS Docs MCP solo cuando es necesario"""
        services_needing_docs = [s for s in context['aws_services'] if s.upper() in ['LAMBDA', 'DYNAMODB', 'API GATEWAY']]
        
        if not services_needing_docs:
            return {"documentation": "No se requiere documentación específica"}
        
        payload = {
            "services": services_needing_docs,
            "documentation_type": "best_practices"
        }
        
        response = requests.post(
            self.mcp_endpoints['awsdocs'],
            json=payload,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"documentation": "Documentación no disponible"}
    
    def _needs_aws_documentation(self, context: Dict[str, Any]) -> bool:
        """Determina si necesita documentación AWS específica"""
        complex_services = ['LAMBDA', 'DYNAMODB', 'API GATEWAY', 'EKS', 'ECS']
        return any(service.upper() in complex_services for service in context['aws_services'])
    
    def _extract_user_count(self, requirements: str) -> int:
        """Extrae número de usuarios de los requerimientos"""
        import re
        numbers = re.findall(r'\d+', requirements)
        if numbers:
            return int(numbers[0])
        return 100  # Default
    
    def _create_generation_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Crea resumen de generación"""
        return {
            "documents_generated": len(results.get('generated_documents', {}).get('documents', [])),
            "diagram_created": bool(results.get('architecture_diagram', {}).get('diagram_url')),
            "cost_calculated": bool(results.get('cost_estimation', {}).get('monthly_cost')),
            "infrastructure_ready": bool(results.get('infrastructure_code', {}).get('template')),
            "status": "completed"
        }
