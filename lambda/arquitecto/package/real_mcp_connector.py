"""
Real MCP Connector - Connects to actual MCP services running in ECS
"""

import json
import logging
import requests
import boto3
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class RealMCPConnector:
    """Connector for real MCP services running in ECS"""
    
    def __init__(self):
        self.elbv2_client = boto3.client('elbv2')
        self.session = requests.Session()
        self.session.timeout = 30
        
        # MCP service endpoints (will be resolved dynamically)
        self.mcp_endpoints = {}
        
    def _get_load_balancer_dns(self, target_group_name: str) -> Optional[str]:
        """Get the DNS name of the load balancer for a target group"""
        try:
            # Get target groups
            response = self.elbv2_client.describe_target_groups(
                Names=[target_group_name]
            )
            
            if not response['TargetGroups']:
                logger.error(f"Target group {target_group_name} not found")
                return None
                
            target_group_arn = response['TargetGroups'][0]['TargetGroupArn']
            
            # Get load balancers for this target group
            lb_response = self.elbv2_client.describe_load_balancers()
            
            for lb in lb_response['LoadBalancers']:
                # Check if this LB has our target group
                listeners_response = self.elbv2_client.describe_listeners(
                    LoadBalancerArn=lb['LoadBalancerArn']
                )
                
                for listener in listeners_response['Listeners']:
                    rules_response = self.elbv2_client.describe_rules(
                        ListenerArn=listener['ListenerArn']
                    )
                    
                    for rule in rules_response['Rules']:
                        for action in rule.get('Actions', []):
                            if (action.get('Type') == 'forward' and 
                                action.get('TargetGroupArn') == target_group_arn):
                                return lb['DNSName']
                                
        except Exception as e:
            logger.error(f"Error getting load balancer DNS for {target_group_name}: {str(e)}")
            
        return None
    
    def _resolve_mcp_endpoint(self, mcp_config: Dict) -> str:
        """Resolve the actual endpoint for an MCP service"""
        
        if 'target_group' not in mcp_config:
            return None
            
        target_group = mcp_config['target_group']
        port = mcp_config['port']
        
        # Check cache first
        cache_key = f"{target_group}:{port}"
        if cache_key in self.mcp_endpoints:
            return self.mcp_endpoints[cache_key]
        
        # Get load balancer DNS
        lb_dns = self._get_load_balancer_dns(target_group)
        if not lb_dns:
            logger.error(f"Could not resolve endpoint for {target_group}")
            return None
            
        endpoint = f"http://{lb_dns}:{port}"
        self.mcp_endpoints[cache_key] = endpoint
        
        logger.info(f"Resolved MCP endpoint: {target_group} -> {endpoint}")
        return endpoint
    
    def call_mcp_service(self, mcp_name: str, mcp_config: Dict, 
                        method: str, data: Dict = None) -> Dict:
        """Call a real MCP service"""
        
        try:
            # Resolve endpoint
            endpoint = self._resolve_mcp_endpoint(mcp_config)
            if not endpoint:
                return {
                    'success': False,
                    'error': f'Could not resolve endpoint for {mcp_name}',
                    'simulated': True
                }
            
            # Prepare request
            url = f"{endpoint}/mcp/{method}"
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'AWS-Propuestas-v3-Arquitecto/1.0'
            }
            
            # Make request
            if data:
                response = self.session.post(url, json=data, headers=headers)
            else:
                response = self.session.get(url, headers=headers)
            
            response.raise_for_status()
            
            return {
                'success': True,
                'data': response.json(),
                'status_code': response.status_code,
                'endpoint': endpoint
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling MCP service {mcp_name}: {str(e)}")
            
            # Return simulated response as fallback
            return self._simulate_mcp_response(mcp_name, mcp_config, method, data)
            
        except Exception as e:
            logger.error(f"Unexpected error calling MCP {mcp_name}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'simulated': True
            }
    
    def _simulate_mcp_response(self, mcp_name: str, mcp_config: Dict, 
                              method: str, data: Dict = None) -> Dict:
        """Simulate MCP response when real service is unavailable"""
        
        logger.info(f"Simulating response for {mcp_name}.{method}")
        
        # Core MCP simulation
        if mcp_name == 'core':
            return {
                'success': True,
                'data': {
                    'analysis': 'Conversation analyzed successfully',
                    'intent': 'document_generation',
                    'confidence': 0.85,
                    'recommendations': ['Generate comprehensive documentation']
                },
                'simulated': True
            }
        
        # Pricing MCP simulation
        elif mcp_name == 'aws_pricing':
            return {
                'success': True,
                'data': {
                    'estimated_cost': {
                        'monthly': 150.00,
                        'annual': 1800.00
                    },
                    'breakdown': {
                        'EC2': 50.00,
                        'S3': 25.00,
                        'RDS': 75.00
                    },
                    'recommendations': ['Consider Reserved Instances for 20% savings']
                },
                'simulated': True
            }
        
        # Documentation MCP simulation
        elif mcp_name == 'aws_docs':
            return {
                'success': True,
                'data': {
                    'documentation': 'AWS best practices documentation retrieved',
                    'links': [
                        'https://docs.aws.amazon.com/wellarchitected/',
                        'https://docs.aws.amazon.com/architecture-center/'
                    ]
                },
                'simulated': True
            }
        
        # CloudFormation MCP simulation
        elif mcp_name == 'cloudformation':
            return {
                'success': True,
                'data': {
                    'template': 'AWSTemplateFormatVersion: "2010-09-09"...',
                    'resources': ['VPC', 'EC2', 'RDS', 'S3'],
                    'estimated_cost': 120.00
                },
                'simulated': True
            }
        
        # Diagram MCP simulation
        elif mcp_name == 'aws_diagram':
            return {
                'success': True,
                'data': {
                    'diagram_url': 'https://example.com/diagram.png',
                    'diagram_type': 'architecture',
                    'components': ['VPC', 'EC2', 'RDS', 'S3', 'ALB']
                },
                'simulated': True
            }
        
        # Custom Documentation MCP simulation
        elif mcp_name == 'code_doc_gen':
            return {
                'success': True,
                'data': {
                    'documents_generated': 5,
                    'types': ['README', 'Architecture', 'API', 'Deployment'],
                    'total_size': '45KB'
                },
                'simulated': True
            }
        
        # Default simulation
        return {
            'success': True,
            'data': {
                'message': f'Simulated response from {mcp_name}',
                'method': method,
                'timestamp': datetime.now().isoformat()
            },
            'simulated': True
        }
    
    def test_mcp_connectivity(self) -> Dict:
        """Test connectivity to all MCP services"""
        
        results = {}
        
        # Test each MCP service
        test_mcps = {
            'core': {'port': 8000, 'target_group': 'aws-prop-v3-core-prod'},
            'aws_pricing': {'port': 8001, 'target_group': 'aws-prop-v3-pricing-prod'},
            'aws_docs': {'port': 8002, 'target_group': 'aws-prop-v3-awsdocs-prod'},
            'cloudformation': {'port': 8003, 'target_group': 'aws-prop-v3-cfn-prod'},
            'aws_diagram': {'port': 8004, 'target_group': 'aws-prop-v3-diagram-prod'},
            'code_doc_gen': {'port': 8005, 'target_group': 'aws-prop-v3-customdoc-prod'}
        }
        
        for mcp_name, config in test_mcps.items():
            try:
                endpoint = self._resolve_mcp_endpoint(config)
                if endpoint:
                    # Try a simple health check
                    response = self.session.get(f"{endpoint}/health", timeout=5)
                    results[mcp_name] = {
                        'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                        'endpoint': endpoint,
                        'response_time': response.elapsed.total_seconds()
                    }
                else:
                    results[mcp_name] = {
                        'status': 'unreachable',
                        'endpoint': None,
                        'error': 'Could not resolve endpoint'
                    }
                    
            except Exception as e:
                results[mcp_name] = {
                    'status': 'error',
                    'endpoint': endpoint if 'endpoint' in locals() else None,
                    'error': str(e)
                }
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_services': len(test_mcps),
            'healthy_services': len([r for r in results.values() if r['status'] == 'healthy']),
            'results': results
        }
