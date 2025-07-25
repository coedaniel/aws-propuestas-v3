import json
import requests
import logging
import re
from typing import Dict, List, Any, Optional

logger = logging.getLogger()

# MCP URLs
MCP_BASE_URL = "https://mcp.danielingram.shop"

class SmartMCPHandler:
    """
    Smart MCP handler that activates MCPs only when needed, like Amazon Q CLI Developer
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.mcp_services_used = []
    
    def detect_mcp_needs(self, text: str, conversation_context: Dict) -> List[str]:
        """
        Detect which MCPs are needed based on conversation content
        Like Amazon Q CLI Developer - smart detection
        """
        needed_mcps = []
        text_lower = text.lower()
        
        # Detect diagram needs
        diagram_keywords = [
            'diagrama', 'diagram', 'arquitectura', 'architecture', 'visual', 
            'grafico', 'esquema', 'draw.io', 'drawio', 'svg', 'png'
        ]
        if any(keyword in text_lower for keyword in diagram_keywords):
            needed_mcps.append('diagram')
        
        # Detect CloudFormation needs
        cfn_keywords = [
            'cloudformation', 'template', 'script', 'automatizacion', 
            'automation', 'infraestructura como codigo', 'iac'
        ]
        if any(keyword in text_lower for keyword in cfn_keywords):
            needed_mcps.append('cfn')
        
        # Detect pricing needs
        pricing_keywords = [
            'costo', 'cost', 'precio', 'price', 'calculadora', 'calculator',
            'presupuesto', 'budget', 'estimacion', 'estimate'
        ]
        if any(keyword in text_lower for keyword in pricing_keywords):
            needed_mcps.append('pricing')
        
        # Detect document generation needs
        doc_keywords = [
            'generar documentos', 'generate documents', 'archivos', 'files',
            'entregables', 'deliverables', 'propuesta', 'proposal'
        ]
        if any(keyword in text_lower for keyword in doc_keywords):
            needed_mcps.append('docgen')
        
        # Check if we're at document generation phase
        if self._is_document_generation_phase(text_lower, conversation_context):
            # Add all needed MCPs for final document generation
            needed_mcps.extend(['diagram', 'cfn', 'pricing', 'docgen'])
            needed_mcps = list(set(needed_mcps))  # Remove duplicates
        
        return needed_mcps
    
    def _is_document_generation_phase(self, text: str, context: Dict) -> bool:
        """Check if we're in the document generation phase"""
        generation_phrases = [
            'procederé a generar', 'voy a generar', 'generando documentos',
            'creating documents', 'generating files', 'entregables listos'
        ]
        return any(phrase in text for phrase in generation_phrases)
    
    def call_mcp_service(self, service: str, payload: Dict) -> Dict:
        """Call specific MCP service when needed"""
        try:
            url_map = {
                'diagram': f"{MCP_BASE_URL}/diagram/generate",
                'cfn': f"{MCP_BASE_URL}/cfn/generate", 
                'pricing': f"{MCP_BASE_URL}/pricing/calculate",
                'docgen': f"{MCP_BASE_URL}/docgen/generate",
                'core': f"{MCP_BASE_URL}/core/process"
            }
            
            if service not in url_map:
                return {"error": f"Unknown MCP service: {service}"}
            
            response = self.session.post(
                url_map[service],
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                logger.info(f"✅ MCP {service} called successfully")
                if service not in self.mcp_services_used:
                    self.mcp_services_used.append(service)
                return response.json()
            else:
                logger.error(f"❌ MCP {service} failed: {response.status_code}")
                return {"error": f"MCP {service} failed: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Error calling MCP {service}: {str(e)}")
            return {"error": f"MCP {service} error: {str(e)}"}
    
    def process_with_smart_mcps(self, ai_response: str, conversation_context: Dict, project_info: Dict) -> Dict:
        """
        Process AI response and activate MCPs only when needed
        Like Amazon Q CLI Developer
        """
        results = {
            "enhanced_response": ai_response,
            "mcp_results": {},
            "files_generated": [],
            "services_used": []
        }
        
        # Detect what MCPs we need
        needed_mcps = self.detect_mcp_needs(ai_response, conversation_context)
        
        if not needed_mcps:
            logger.info("No MCPs needed for this response")
            return results
        
        logger.info(f"🎯 Smart MCP activation needed: {needed_mcps}")
        
        # Call each needed MCP
        for mcp_service in needed_mcps:
            mcp_result = self._call_specific_mcp(mcp_service, ai_response, project_info)
            if mcp_result and "error" not in mcp_result:
                results["mcp_results"][mcp_service] = mcp_result
                results["services_used"].append(mcp_service)
                
                # Extract generated files
                if "files" in mcp_result:
                    results["files_generated"].extend(mcp_result["files"])
        
        # Update response with MCP enhancements
        if results["mcp_results"]:
            results["enhanced_response"] = self._enhance_response_with_mcp_results(
                ai_response, results["mcp_results"]
            )
        
        return results
    
    def _call_specific_mcp(self, service: str, context: str, project_info: Dict) -> Dict:
        """Call specific MCP with appropriate payload"""
        
        if service == 'diagram':
            return self.call_mcp_service('diagram', {
                "description": context,
                "project_name": project_info.get('name', 'proyecto'),
                "output_formats": ["svg", "png", "drawio"]
            })
        
        elif service == 'cfn':
            return self.call_mcp_service('cfn', {
                "requirements": project_info,
                "context": context,
                "template_type": "complete"
            })
        
        elif service == 'pricing':
            return self.call_mcp_service('pricing', {
                "project_info": project_info,
                "context": context,
                "region": "us-east-1"
            })
        
        elif service == 'docgen':
            return self.call_mcp_service('docgen', {
                "project_data": project_info,
                "context": context,
                "document_types": ["all"],
                "format": "plain_text_only"
            })
        
        return {}
    
    def _enhance_response_with_mcp_results(self, original_response: str, mcp_results: Dict) -> str:
        """Enhance the AI response with MCP results"""
        enhanced = original_response
        
        # Add information about generated files
        if mcp_results:
            enhanced += "\n\n**Archivos generados con herramientas especializadas:**\n"
            
            for service, result in mcp_results.items():
                if "files" in result:
                    enhanced += f"\n- {service.upper()}: {len(result['files'])} archivos generados\n"
                    for file_info in result["files"]:
                        enhanced += f"  • {file_info.get('name', 'archivo')}\n"
        
        return enhanced
    
    def get_services_used(self) -> List[str]:
        """Get list of MCP services used in this session"""
        return self.mcp_services_used.copy()

# Global instance
smart_mcp = SmartMCPHandler()
