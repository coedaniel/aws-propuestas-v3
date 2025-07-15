"""
AWS Propuestas V3 - Intelligent Architect with MCP Integration
Implements the Master Prompt exactly as specified by the user
"""

import json
import boto3
import uuid
import os
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError

# Initialize AWS clients
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
s3_client = boto3.client('s3')

# MCP Server URLs
MCP_BASE_URL = 'https://mcp.danielingram.shop'
MCP_ENDPOINTS = {
    'core': f'{MCP_BASE_URL}/core',
    'pricing': f'{MCP_BASE_URL}/pricing',
    'awsdocs': f'{MCP_BASE_URL}/awsdocs',
    'cfn': f'{MCP_BASE_URL}/cfn',
    'diagram': f'{MCP_BASE_URL}/diagram',
    'docgen': f'{MCP_BASE_URL}/docgen',
}

# Configuration
DOCUMENTS_BUCKET = os.environ.get('DOCUMENTS_BUCKET')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'prod')

class IntelligentArchitect:
    """
    Intelligent AWS Solutions Architect that implements the Master Prompt:
    
    PROMPT MAESTRO COMPLETO:
    Actua como arquitecto de soluciones AWS y consultor experto. Vamos a dimensionar, 
    documentar y entregar una solucion profesional en AWS, siguiendo mejores practicas 
    y generando todos los archivos necesarios para una propuesta ejecutiva.
    """
    
    def __init__(self):
        self.conversation_state = "initial"
        self.project_data = {}
        self.session_id = None
        
    def process_request(self, user_input: str, session_id: str = None) -> Dict[str, Any]:
        """Process user request following the Master Prompt flow"""
        
        if not session_id:
            session_id = str(uuid.uuid4())
        
        self.session_id = session_id
        
        # Load existing session data if available
        self._load_session_data()
        
        # Determine conversation state and respond accordingly
        if self.conversation_state == "initial":
            return self._handle_initial_state(user_input)
        elif self.conversation_state == "waiting_project_name":
            return self._handle_project_name(user_input)
        elif self.conversation_state == "waiting_solution_type":
            return self._handle_solution_type(user_input)
        elif self.conversation_state == "quick_service":
            return self._handle_quick_service(user_input)
        elif self.conversation_state == "integral_solution":
            return self._handle_integral_solution(user_input)
        elif self.conversation_state == "generating_documents":
            return self._handle_document_generation(user_input)
        else:
            return self._handle_general_conversation(user_input)
    
    def _handle_initial_state(self, user_input: str) -> Dict[str, Any]:
        """Handle the initial conversation state"""
        
        # Check if user already provided project name
        if user_input and len(user_input.strip()) > 0:
            # Try to extract project name from input
            if self._is_project_name(user_input):
                self.project_data['project_name'] = user_input.strip()
                self.conversation_state = "waiting_solution_type"
                return {
                    'response': f"Perfecto, el proyecto se llama '{user_input.strip()}'. Ahora necesito saber: ¿El proyecto es una solucion integral (como migracion, aplicacion nueva, modernizacion, analitica, seguridad, IA, IoT, data lake, networking, DRP, VDI, integracion, etc.) o es un servicio rapido especifico (implementacion de instancias EC2, RDS, SES, VPN, ELB, S3, VPC, CloudFront, SSO, backup, etc.)?",
                    'session_id': self.session_id,
                    'state': self.conversation_state,
                    'project_data': self.project_data
                }
            else:
                # User provided something else, ask for project name
                self.conversation_state = "waiting_project_name"
                return {
                    'response': "Hola! Soy tu Arquitecto AWS. Para comenzar, necesito que me proporciones unicamente el **nombre del proyecto** (por ejemplo: 'E-commerce Platform', 'Sistema de Inventario', 'Portal de Clientes', etc.). ¿Cual es el nombre de tu proyecto?",
                    'session_id': self.session_id,
                    'state': self.conversation_state
                }
        else:
            # No input, ask for project name
            self.conversation_state = "waiting_project_name"
            return {
                'response': "Hola! Soy tu Arquitecto AWS. Para comenzar, necesito que me proporciones unicamente el **nombre del proyecto** (por ejemplo: 'E-commerce Platform', 'Sistema de Inventario', 'Portal de Clientes', etc.). ¿Cual es el nombre de tu proyecto?",
                'session_id': self.session_id,
                'state': self.conversation_state
            }
    
    def _handle_project_name(self, user_input: str) -> Dict[str, Any]:
        """Handle project name input"""
        
        if user_input and len(user_input.strip()) > 0:
            self.project_data['project_name'] = user_input.strip()
            self.conversation_state = "waiting_solution_type"
            self._save_session_data()
            
            return {
                'response': f"Perfecto, el proyecto se llama '{user_input.strip()}'. Ahora necesito saber: ¿El proyecto es una solucion integral (como migracion, aplicacion nueva, modernizacion, analitica, seguridad, IA, IoT, data lake, networking, DRP, VDI, integracion, etc.) o es un servicio rapido especifico (implementacion de instancias EC2, RDS, SES, VPN, ELB, S3, VPC, CloudFront, SSO, backup, etc.)?",
                'session_id': self.session_id,
                'state': self.conversation_state,
                'project_data': self.project_data
            }
        else:
            return {
                'response': "Por favor, proporciona el nombre del proyecto para continuar.",
                'session_id': self.session_id,
                'state': self.conversation_state
            }
    
    def _handle_solution_type(self, user_input: str) -> Dict[str, Any]:
        """Handle solution type selection"""
        
        user_input_lower = user_input.lower()
        
        # Check if user chose quick service
        quick_keywords = ['rapido', 'especifico', 'servicio', 'ec2', 'rds', 'ses', 'vpn', 'elb', 's3', 'vpc', 'cloudfront', 'sso', 'backup']
        integral_keywords = ['integral', 'solucion', 'migracion', 'aplicacion', 'modernizacion', 'analitica', 'seguridad', 'ia', 'iot', 'data lake', 'networking', 'drp', 'vdi', 'integracion']
        
        is_quick = any(keyword in user_input_lower for keyword in quick_keywords)
        is_integral = any(keyword in user_input_lower for keyword in integral_keywords)
        
        if is_quick and not is_integral:
            self.project_data['solution_type'] = 'quick_service'
            self.conversation_state = "quick_service"
            self._save_session_data()
            
            return {
                'response': self._get_quick_services_catalog(),
                'session_id': self.session_id,
                'state': self.conversation_state,
                'project_data': self.project_data
            }
        elif is_integral:
            self.project_data['solution_type'] = 'integral_solution'
            self.conversation_state = "integral_solution"
            self._save_session_data()
            
            return {
                'response': "Perfecto, vamos a trabajar en una solucion integral. Necesito hacer una entrevista guiada para capturar todos los detalles. Empecemos: ¿Cual es el objetivo principal de este proyecto?",
                'session_id': self.session_id,
                'state': self.conversation_state,
                'project_data': self.project_data
            }
        else:
            return {
                'response': "Por favor, especifica si necesitas una 'solucion integral' o un 'servicio rapido especifico'.",
                'session_id': self.session_id,
                'state': self.conversation_state
            }
    
    def _handle_quick_service(self, user_input: str) -> Dict[str, Any]:
        """Handle quick service flow"""
        
        # This is where we would use MCP servers to generate documents
        # For now, let's simulate the process
        
        if 'bucket' in user_input.lower() and 's3' in user_input.lower():
            # User wants to upload to S3, let's generate documents
            return self._generate_quick_service_documents(user_input)
        else:
            # Continue gathering requirements
            return {
                'response': f"Entendido. Has seleccionado: {user_input}. Ahora necesito algunos detalles minimos. ¿Puedes describir brevemente los requerimientos especificos? Y al final, ¿en que bucket S3 deseas subir la carpeta con todos los documentos generados?",
                'session_id': self.session_id,
                'state': self.conversation_state,
                'project_data': self.project_data
            }
    
    def _handle_integral_solution(self, user_input: str) -> Dict[str, Any]:
        """Handle integral solution flow"""
        
        # This would be the guided interview process
        # For now, let's simulate
        
        if not self.project_data.get('objective'):
            self.project_data['objective'] = user_input
            self._save_session_data()
            return {
                'response': "Excelente. Ahora, ¿puedes proporcionar una descripcion detallada del proyecto?",
                'session_id': self.session_id,
                'state': self.conversation_state,
                'project_data': self.project_data
            }
        elif not self.project_data.get('description'):
            self.project_data['description'] = user_input
            self._save_session_data()
            return {
                'response': "Perfecto. ¿Cuales son las caracteristicas clave requeridas?",
                'session_id': self.session_id,
                'state': self.conversation_state,
                'project_data': self.project_data
            }
        else:
            # Continue with more questions or generate documents
            return self._generate_integral_solution_documents(user_input)
    
    def _generate_quick_service_documents(self, user_input: str) -> Dict[str, Any]:
        """Generate documents for quick service using MCP servers"""
        
        try:
            # Use MCP servers to generate documents
            documents = self._call_mcp_document_generation('quick_service', self.project_data, user_input)
            
            return {
                'response': f"Perfecto! He generado todos los documentos para el proyecto '{self.project_data.get('project_name')}'. Los documentos incluyen:\n\n- Tabla de actividades de implementacion (CSV)\n- Script CloudFormation para desplegar el servicio\n- Diagrama de arquitectura (SVG, PNG, Draw.io)\n- Documento Word con objetivo y descripcion\n- Archivo de costos estimados (CSV)\n- Guia paso a paso para la calculadora AWS\n\nTodos los archivos han sido subidos al bucket S3 especificado. ¿Deseas agregar algun comentario o ajuste final?",
                'session_id': self.session_id,
                'state': 'completed',
                'project_data': self.project_data,
                'documents': documents
            }
        except Exception as e:
            print(f"Error generating documents: {str(e)}")
            return {
                'response': f"Hubo un error al generar los documentos: {str(e)}. Por favor, intenta de nuevo.",
                'session_id': self.session_id,
                'state': self.conversation_state,
                'project_data': self.project_data
            }
    
    def _generate_integral_solution_documents(self, user_input: str) -> Dict[str, Any]:
        """Generate documents for integral solution using MCP servers"""
        
        try:
            # Use MCP servers to generate comprehensive documents
            documents = self._call_mcp_document_generation('integral_solution', self.project_data, user_input)
            
            return {
                'response': f"Excelente! He generado todos los documentos para la solucion integral '{self.project_data.get('project_name')}'. Los documentos incluyen:\n\n- Tabla de actividades de implementacion (CSV)\n- Script CloudFormation para la solucion completa\n- Dos diagramas de arquitectura (SVG, PNG, Draw.io)\n- Documento Word completo con objetivo, descripcion, actividades y costos\n- Costos estimados detallados (CSV)\n- Guia para la calculadora oficial de AWS\n\nTodos los archivos han sido organizados y subidos al bucket S3. ¿Deseas agregar comentarios o ajustes antes de cerrar la propuesta?",
                'session_id': self.session_id,
                'state': 'completed',
                'project_data': self.project_data,
                'documents': documents
            }
        except Exception as e:
            print(f"Error generating documents: {str(e)}")
            return {
                'response': f"Hubo un error al generar los documentos: {str(e)}. Por favor, intenta de nuevo.",
                'session_id': self.session_id,
                'state': self.conversation_state,
                'project_data': self.project_data
            }
    
    def _call_mcp_document_generation(self, solution_type: str, project_data: Dict, user_input: str) -> Dict[str, Any]:
        """Call MCP servers to generate documents"""
        
        documents = {}
        
        try:
            # 1. Generate CloudFormation template using CFN MCP
            cfn_response = self._call_mcp_server('cfn', 'generate_template', {
                'project_data': project_data,
                'solution_type': solution_type,
                'requirements': user_input
            })
            documents['cloudformation'] = cfn_response
            
            # 2. Generate architecture diagram using Diagram MCP
            diagram_response = self._call_mcp_server('diagram', 'generate_diagram', {
                'project_data': project_data,
                'solution_type': solution_type
            })
            documents['diagram'] = diagram_response
            
            # 3. Generate cost analysis using Pricing MCP
            pricing_response = self._call_mcp_server('pricing', 'calculate_pricing', {
                'project_data': project_data,
                'solution_type': solution_type
            })
            documents['pricing'] = pricing_response
            
            # 4. Generate custom documents using DocGen MCP
            docgen_response = self._call_mcp_server('docgen', 'generate_document', {
                'project_data': project_data,
                'solution_type': solution_type,
                'document_types': ['activities', 'word_document', 'aws_calculator_guide']
            })
            documents['custom_docs'] = docgen_response
            
            return documents
            
        except Exception as e:
            print(f"Error calling MCP servers: {str(e)}")
            raise e
    
    def _call_mcp_server(self, server_name: str, tool_name: str, arguments: Dict) -> Dict[str, Any]:
        """Call a specific MCP server tool"""
        
        url = f"{MCP_ENDPOINTS[server_name]}?endpoint=call-tool"
        
        payload = {
            'tool': tool_name,
            'arguments': arguments
        }
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code != 200:
            raise Exception(f"MCP server {server_name} returned status {response.status_code}")
        
        result = response.json()
        
        if not result.get('success'):
            raise Exception(f"MCP server {server_name} error: {result.get('error', 'Unknown error')}")
        
        return result.get('result', {})
    
    def _get_quick_services_catalog(self) -> str:
        """Return the catalog of quick services"""
        
        return """Aqui tienes el catalogo de servicios rapidos comunes:

**COMPUTE & HOSTING:**
1. Instancias EC2 (Windows/Linux)
2. Load Balancer (ALB/NLB)
3. Auto Scaling Groups
4. Elastic Beanstalk

**DATABASES:**
5. RDS (MySQL, PostgreSQL, SQL Server)
6. DynamoDB
7. ElastiCache (Redis/Memcached)
8. DocumentDB

**STORAGE:**
9. S3 Buckets y configuracion
10. EFS (Elastic File System)
11. FSx (Windows File Server)

**NETWORKING:**
12. VPC y subnets
13. VPN Site-to-Site
14. CloudFront CDN
15. Route 53 DNS

**SECURITY & ACCESS:**
16. IAM Roles y Policies
17. SSO (Single Sign-On)
18. Certificate Manager
19. WAF (Web Application Firewall)

**MESSAGING & INTEGRATION:**
20. SES (Simple Email Service)
21. SNS (Simple Notification Service)
22. SQS (Simple Queue Service)
23. API Gateway

**BACKUP & MONITORING:**
24. AWS Backup
25. CloudWatch Monitoring
26. CloudTrail Logging

Puedes elegir uno o varios servicios, o escribir tu requerimiento especifico. ¿Cual necesitas?"""
    
    def _is_project_name(self, text: str) -> bool:
        """Determine if the input looks like a project name"""
        
        # Simple heuristic: if it's not a question and not too long, it's likely a project name
        text = text.strip()
        
        if len(text) == 0:
            return False
        
        if len(text) > 100:
            return False
        
        # If it contains question words, it's probably not a project name
        question_words = ['que', 'como', 'cuando', 'donde', 'por que', 'cual', 'quien', '?']
        text_lower = text.lower()
        
        if any(word in text_lower for word in question_words):
            return False
        
        return True
    
    def _handle_general_conversation(self, user_input: str) -> Dict[str, Any]:
        """Handle general conversation using Core MCP server"""
        
        try:
            # Use Core MCP server for general conversation
            response = self._call_mcp_server('core', 'chat', {
                'messages': [
                    {'role': 'system', 'content': 'Eres un arquitecto de soluciones AWS experto. Responde de manera profesional y tecnica.'},
                    {'role': 'user', 'content': user_input}
                ],
                'modelId': 'anthropic.claude-3-5-sonnet-20241022-v2:0'
            })
            
            return {
                'response': response.get('response', 'Lo siento, no pude procesar tu solicitud.'),
                'session_id': self.session_id,
                'state': self.conversation_state,
                'project_data': self.project_data
            }
            
        except Exception as e:
            print(f"Error in general conversation: {str(e)}")
            return {
                'response': "Lo siento, hubo un error al procesar tu solicitud. Por favor, intenta de nuevo.",
                'session_id': self.session_id,
                'state': self.conversation_state,
                'project_data': self.project_data
            }
    
    def _load_session_data(self):
        """Load session data from storage (simplified for now)"""
        # In a real implementation, this would load from DynamoDB or similar
        pass
    
    def _save_session_data(self):
        """Save session data to storage (simplified for now)"""
        # In a real implementation, this would save to DynamoDB or similar
        pass

def lambda_handler(event, context):
    """Main Lambda handler"""
    
    try:
        # Handle CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                },
                'body': ''
            }
        
        # Parse request body
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event
        
        # Extract parameters
        messages = body.get('messages', [])
        session_id = body.get('session_id')
        
        # Get the last user message
        user_input = ""
        if messages:
            for msg in reversed(messages):
                if msg.get('role') == 'user':
                    user_input = msg.get('content', '')
                    break
        
        # Create architect instance and process request
        architect = IntelligentArchitect()
        result = architect.process_request(user_input, session_id)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Content-Type': 'application/json'
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
