import json
import requests
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger()

# MCP URLs - USING HTTPS WITH CUSTOM DOMAIN
MCP_BASE_URL = "https://mcp.danielingram.shop"
CORE_MCP_URL = f"{MCP_BASE_URL}/core"
DIAGRAM_MCP_URL = f"{MCP_BASE_URL}/diagram"
CFN_MCP_URL = f"{MCP_BASE_URL}/cfn"
PRICING_MCP_URL = f"{MCP_BASE_URL}/pricing"
DOCGEN_MCP_URL = f"{MCP_BASE_URL}/docgen"
AWSDOCS_MCP_URL = f"{MCP_BASE_URL}/awsdocs"

class MCPConnector:
    """Connector to interact with MCP services"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def activate_core_mcp(self, conversation_context: Dict) -> Dict:
        """
        Activate MCP Core to supercharge the model with all MCP tools
        This should be called FIRST to give the model access to all capabilities
        """
        try:
            payload = {
                "action": "activate_tools",
                "context": conversation_context,
                "available_mcps": [
                    "diagram", "cloudformation", "pricing", "documentation", "aws-docs"
                ]
            }
            
            response = self.session.post(
                f"{CORE_MCP_URL}/activate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info("✅ MCP Core activated successfully")
                return response.json()
            else:
                logger.error(f"❌ MCP Core activation failed: {response.status_code}")
                return {"error": f"Core MCP activation failed: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Error activating MCP Core: {str(e)}")
            return {"error": f"Core MCP activation error: {str(e)}"}
    
    def process_with_core_mcp(self, messages: List[Dict], project_info: Dict) -> Dict:
        """
        Process conversation through MCP Core which will orchestrate other MCPs as needed
        """
        try:
            payload = {
                "messages": messages,
                "project_info": project_info,
                "mode": "arquitecto-master-prompt",
                "available_tools": [
                    "diagram_generator",
                    "cloudformation_generator", 
                    "pricing_calculator",
                    "document_generator",
                    "aws_documentation"
                ]
            }
            
            response = self.session.post(
                f"{CORE_MCP_URL}/process",
                json=payload,
                timeout=120  # Longer timeout for complex processing
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ MCP Core processing successful")
                return result
            else:
                logger.error(f"❌ MCP Core processing failed: {response.status_code}")
                return {"error": f"Core MCP processing failed: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Error processing with MCP Core: {str(e)}")
            return {"error": f"Core MCP processing error: {str(e)}"}
    
    def generate_diagram(self, architecture_description: str, project_name: str) -> Dict:
        """Generate architecture diagram using Diagram MCP"""
        try:
            payload = {
                "description": architecture_description,
                "project_name": project_name,
                "output_formats": ["svg", "png", "drawio"]
            }
            
            response = self.session.post(
                f"{DIAGRAM_MCP_URL}/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                logger.info("✅ Diagram generated successfully")
                return response.json()
            else:
                logger.error(f"❌ Diagram generation failed: {response.status_code}")
                return {"error": f"Diagram generation failed: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Error generating diagram: {str(e)}")
            return {"error": f"Diagram generation error: {str(e)}"}
    
    def generate_cloudformation(self, requirements: Dict) -> Dict:
        """Generate CloudFormation template using CFN MCP"""
        try:
            payload = {
                "requirements": requirements,
                "template_type": "complete",
                "include_outputs": True
            }
            
            response = self.session.post(
                f"{CFN_MCP_URL}/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                logger.info("✅ CloudFormation template generated successfully")
                return response.json()
            else:
                logger.error(f"❌ CloudFormation generation failed: {response.status_code}")
                return {"error": f"CloudFormation generation failed: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Error generating CloudFormation: {str(e)}")
            return {"error": f"CloudFormation generation error: {str(e)}"}
    
    def calculate_pricing(self, services: List[Dict]) -> Dict:
        """Calculate pricing using Pricing MCP"""
        try:
            payload = {
                "services": services,
                "region": "us-east-1",
                "include_calculator_guide": True
            }
            
            response = self.session.post(
                f"{PRICING_MCP_URL}/calculate",
                json=payload,
                timeout=45
            )
            
            if response.status_code == 200:
                logger.info("✅ Pricing calculated successfully")
                return response.json()
            else:
                logger.error(f"❌ Pricing calculation failed: {response.status_code}")
                return {"error": f"Pricing calculation failed: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Error calculating pricing: {str(e)}")
            return {"error": f"Pricing calculation error: {str(e)}"}
    
    def generate_documents(self, project_data: Dict) -> Dict:
        """Generate all project documents using Document Generator MCP"""
        try:
            payload = {
                "project_data": project_data,
                "document_types": [
                    "implementation_plan",
                    "technical_documentation", 
                    "cost_analysis",
                    "aws_calculator_guide"
                ],
                "format": "plain_text_only"  # No accents, no complex formatting
            }
            
            response = self.session.post(
                f"{DOCGEN_MCP_URL}/generate",
                json=payload,
                timeout=90
            )
            
            if response.status_code == 200:
                logger.info("✅ Documents generated successfully")
                return response.json()
            else:
                logger.error(f"❌ Document generation failed: {response.status_code}")
                return {"error": f"Document generation failed: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Error generating documents: {str(e)}")
            return {"error": f"Document generation error: {str(e)}"}

# Global instance
mcp_connector = MCPConnector()
