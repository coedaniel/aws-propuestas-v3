"""
MCP Client for AWS Propuestas V3
Handles communication with MCP servers running on ECS
"""

import json
import os
import logging
import requests
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class MCPClient:
    """Client for communicating with MCP servers"""
    
    def __init__(self):
        # Get MCP server endpoints from environment variables
        self.document_generator_endpoint = os.environ.get('DOCUMENT_GENERATOR_ENDPOINT')
        self.cloudformation_generator_endpoint = os.environ.get('CLOUDFORMATION_GENERATOR_ENDPOINT')
        self.cost_analysis_endpoint = os.environ.get('COST_ANALYSIS_ENDPOINT')
        
        # Default timeout for requests
        self.timeout = 30
        
        logger.info(f"MCP Client initialized with endpoints:")
        logger.info(f"  Document Generator: {self.document_generator_endpoint}")
        logger.info(f"  CloudFormation Generator: {self.cloudformation_generator_endpoint}")
        logger.info(f"  Cost Analysis: {self.cost_analysis_endpoint}")
    
    def generate_word_document(self, project_info: Dict[str, Any], agent_response: str = "") -> Dict[str, Any]:
        """Generate Word document using MCP server"""
        
        if not self.document_generator_endpoint:
            raise ValueError("Document generator endpoint not configured")
        
        try:
            payload = {
                "tool": "generate_word_document",
                "arguments": {
                    "project_info": project_info,
                    "agent_response": agent_response
                }
            }
            
            response = requests.post(
                f"{self.document_generator_endpoint}/call-tool",
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Word document generated successfully for project: {project_info.get('name', 'Unknown')}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling document generator MCP server: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in generate_word_document: {str(e)}")
            raise
    
    def generate_csv_activities(self, project_info: Dict[str, Any], agent_response: str = "") -> Dict[str, Any]:
        """Generate CSV activities using MCP server"""
        
        if not self.document_generator_endpoint:
            raise ValueError("Document generator endpoint not configured")
        
        try:
            payload = {
                "tool": "generate_csv_activities",
                "arguments": {
                    "project_info": project_info,
                    "agent_response": agent_response
                }
            }
            
            response = requests.post(
                f"{self.document_generator_endpoint}/call-tool",
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"CSV activities generated successfully for project: {project_info.get('name', 'Unknown')}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling document generator MCP server: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in generate_csv_activities: {str(e)}")
            raise
    
    def generate_complete_proposal(self, project_info: Dict[str, Any], agent_response: str = "") -> Dict[str, Any]:
        """Generate complete proposal package using MCP server"""
        
        if not self.document_generator_endpoint:
            raise ValueError("Document generator endpoint not configured")
        
        try:
            payload = {
                "tool": "generate_complete_proposal",
                "arguments": {
                    "project_info": project_info,
                    "agent_response": agent_response
                }
            }
            
            response = requests.post(
                f"{self.document_generator_endpoint}/call-tool",
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Complete proposal generated successfully for project: {project_info.get('name', 'Unknown')}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling document generator MCP server: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in generate_complete_proposal: {str(e)}")
            raise
    
    def generate_cloudformation_template(self, project_info: Dict[str, Any], agent_response: str = "") -> Dict[str, Any]:
        """Generate CloudFormation template using MCP server"""
        
        if not self.cloudformation_generator_endpoint:
            raise ValueError("CloudFormation generator endpoint not configured")
        
        try:
            payload = {
                "tool": "generate_cloudformation_template",
                "arguments": {
                    "project_info": project_info,
                    "agent_response": agent_response
                }
            }
            
            response = requests.post(
                f"{self.cloudformation_generator_endpoint}/call-tool",
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"CloudFormation template generated successfully for project: {project_info.get('name', 'Unknown')}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling CloudFormation generator MCP server: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in generate_cloudformation_template: {str(e)}")
            raise
    
    def generate_cost_analysis(self, project_info: Dict[str, Any], agent_response: str = "") -> Dict[str, Any]:
        """Generate cost analysis using MCP server"""
        
        if not self.cost_analysis_endpoint:
            raise ValueError("Cost analysis endpoint not configured")
        
        try:
            payload = {
                "tool": "generate_cost_analysis",
                "arguments": {
                    "project_info": project_info,
                    "agent_response": agent_response
                }
            }
            
            response = requests.post(
                f"{self.cost_analysis_endpoint}/call-tool",
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Cost analysis generated successfully for project: {project_info.get('name', 'Unknown')}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling cost analysis MCP server: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in generate_cost_analysis: {str(e)}")
            raise
    
    def generate_all_documents(self, project_info: Dict[str, Any], agent_response: str = "") -> Dict[str, Any]:
        """Generate all documents for a complete proposal"""
        
        logger.info(f"Generating all documents for project: {project_info.get('name', 'Unknown')}")
        
        results = {
            'project_info': project_info,
            'generated_at': datetime.now().isoformat(),
            'documents': {},
            'errors': []
        }
        
        # Generate Word document and CSV activities
        try:
            proposal_result = self.generate_complete_proposal(project_info, agent_response)
            results['documents']['word_document'] = proposal_result.get('word_document', {})
            results['documents']['csv_activities'] = proposal_result.get('csv_activities', {})
        except Exception as e:
            error_msg = f"Error generating proposal documents: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
        
        # Generate CloudFormation template
        try:
            cfn_result = self.generate_cloudformation_template(project_info, agent_response)
            results['documents']['cloudformation_template'] = cfn_result
        except Exception as e:
            error_msg = f"Error generating CloudFormation template: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
        
        # Generate cost analysis
        try:
            cost_result = self.generate_cost_analysis(project_info, agent_response)
            results['documents']['cost_analysis'] = cost_result
        except Exception as e:
            error_msg = f"Error generating cost analysis: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
        
        logger.info(f"Document generation completed. Generated {len(results['documents'])} document types with {len(results['errors'])} errors")
        
        return results
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of all MCP servers"""
        
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'services': {}
        }
        
        services = [
            ('document_generator', self.document_generator_endpoint),
            ('cloudformation_generator', self.cloudformation_generator_endpoint),
            ('cost_analysis', self.cost_analysis_endpoint)
        ]
        
        for service_name, endpoint in services:
            if not endpoint:
                health_status['services'][service_name] = {
                    'status': 'not_configured',
                    'endpoint': None
                }
                continue
            
            try:
                response = requests.get(f"{endpoint}/health", timeout=5)
                health_status['services'][service_name] = {
                    'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                    'endpoint': endpoint,
                    'response_time_ms': response.elapsed.total_seconds() * 1000
                }
            except Exception as e:
                health_status['services'][service_name] = {
                    'status': 'error',
                    'endpoint': endpoint,
                    'error': str(e)
                }
        
        return health_status
