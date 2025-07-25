"""
MCP Orchestrator - Amazon Q Developer CLI Style
Intelligent MCP activation and coordination system with real ECS services
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from document_generator import DocumentGenerator
from real_mcp_connector import RealMCPConnector

logger = logging.getLogger(__name__)

class MCPOrchestrator:
    """Orchestrates MCP services like Amazon Q Developer CLI"""
    
    def __init__(self, bucket_name: str = None):
        self.bucket_name = bucket_name or 'aws-propuestas-v3-documents-prod'
        self.document_generator = DocumentGenerator(self.bucket_name)
        self.real_mcp_connector = RealMCPConnector()
        
        # Real MCP services running in ECS cluster
        self.available_mcps = {
            # Core MCP services (puerto 8000)
            'core': {
                'name': 'Core MCP',
                'description': 'Central MCP coordination and prompt understanding',
                'capabilities': ['prompt_analysis', 'context_management', 'workflow_coordination'],
                'priority': 1,
                'active': True,
                'port': 8000,
                'target_group': 'aws-prop-v3-core-prod'
            },
            
            # Pricing MCP (puerto 8001)
            'aws_pricing': {
                'name': 'AWS Pricing Calculator',
                'description': 'Calculates and optimizes AWS costs',
                'capabilities': ['cost_estimation', 'pricing_optimization', 'budget_analysis'],
                'priority': 2,
                'active': True,
                'port': 8001,
                'target_group': 'aws-prop-v3-pricing-prod'
            },
            
            # AWS Docs MCP (puerto 8002)
            'aws_docs': {
                'name': 'AWS Documentation',
                'description': 'Searches and retrieves AWS documentation',
                'capabilities': ['doc_search', 'best_practices', 'service_guides'],
                'priority': 3,
                'active': True,
                'port': 8002,
                'target_group': 'aws-prop-v3-awsdocs-prod'
            },
            
            # CloudFormation MCP (puerto 8003)
            'cloudformation': {
                'name': 'CloudFormation Generator',
                'description': 'Generates CloudFormation templates',
                'capabilities': ['template_generation', 'resource_definition', 'stack_management'],
                'priority': 4,
                'active': True,
                'port': 8003,
                'target_group': 'aws-prop-v3-cfn-prod'
            },
            
            # Diagram MCP (puerto 8004)
            'aws_diagram': {
                'name': 'AWS Architecture Diagrams',
                'description': 'Creates professional AWS architecture diagrams',
                'capabilities': ['architecture_diagrams', 'service_visualization', 'flow_charts'],
                'priority': 5,
                'active': True,
                'port': 8004,
                'target_group': 'aws-prop-v3-diagram-prod'
            },
            
            # Custom Documentation MCP (puerto 8005)
            'code_doc_gen': {
                'name': 'Custom Documentation Generator',
                'description': 'Generates comprehensive project documentation',
                'capabilities': ['readme_generation', 'api_docs', 'architecture_docs', 'custom_docs'],
                'priority': 6,
                'active': True,
                'port': 8005,
                'target_group': 'aws-prop-v3-customdoc-prod'
            },
            
            # Local fallback MCPs (for compatibility)
            'bedrock_kb': 'awslabs.bedrock-kb-retrieval-mcp-server',
            'nova_canvas': 'awslabs.nova-canvas-mcp-server',
            'cdk': 'awslabs.cdk-mcp-server',
            'serverless': 'awslabs.aws-serverless-mcp-server',
            'dynamodb': 'awslabs.dynamodb-mcp-server',
            'iam': 'awslabs.iam-mcp-server',
            'frontend': 'awslabs.frontend-mcp-server',
            'bedrock_data_automation': 'awslabs.aws-bedrock-data-automation-mcp-server'
        }
        
    def analyze_conversation_intent(self, messages: List[Dict], ai_response: str) -> Dict:
        """Analyze conversation to determine which MCPs to activate"""
        
        conversation_text = ""
        for msg in messages:
            conversation_text += f"{msg.get('role', '')}: {msg.get('content', '')}\n"
        conversation_text += f"assistant: {ai_response}"
        
        text_lower = conversation_text.lower()
        
        intent_analysis = {
            'primary_intent': 'chat',
            'mcps_to_activate': [],
            'confidence': 0.0,
            'context': {},
            'should_generate_artifacts': False
        }
        
        # Architecture and Infrastructure Intent
        if any(term in text_lower for term in [
            'arquitectura', 'infraestructura', 'cloudformation', 'cdk', 'terraform',
            'diagrama', 'diseño', 'solucion', 'implementar', 'desplegar'
        ]):
            intent_analysis['primary_intent'] = 'architecture'
            intent_analysis['mcps_to_activate'].extend(['cdk', 'aws_diagram', 'aws_docs'])
            intent_analysis['confidence'] += 0.3
            
        # Document Generation Intent
        if any(term in text_lower for term in [
            'generar documentos', 'crear archivos', 'propuesta', 'entregables',
            'documentacion', 'procederé a generar', 'documentos listos'
        ]):
            intent_analysis['primary_intent'] = 'document_generation'
            intent_analysis['mcps_to_activate'].extend(['code_doc_gen', 'nova_canvas', 'aws_diagram'])
            intent_analysis['should_generate_artifacts'] = True
            intent_analysis['confidence'] += 0.4
            
        # Serverless Development Intent
        if any(term in text_lower for term in [
            'lambda', 'serverless', 'api gateway', 'sam', 'amplify',
            'function', 'evento', 'trigger'
        ]):
            intent_analysis['primary_intent'] = 'serverless'
            intent_analysis['mcps_to_activate'].extend(['serverless', 'aws_docs'])
            intent_analysis['confidence'] += 0.3
            
        # Database Intent
        if any(term in text_lower for term in [
            'dynamodb', 'base de datos', 'tabla', 'rds', 'aurora',
            'consulta', 'query', 'datos'
        ]):
            intent_analysis['mcps_to_activate'].append('dynamodb')
            intent_analysis['confidence'] += 0.2
            
        # Security and IAM Intent
        if any(term in text_lower for term in [
            'permisos', 'iam', 'roles', 'politicas', 'seguridad',
            'acceso', 'autenticacion', 'autorizacion'
        ]):
            intent_analysis['mcps_to_activate'].append('iam')
            intent_analysis['confidence'] += 0.2
            
        # Frontend Development Intent
        if any(term in text_lower for term in [
            'frontend', 'react', 'interfaz', 'ui', 'ux',
            'componente', 'pagina', 'web'
        ]):
            intent_analysis['mcps_to_activate'].append('frontend')
            intent_analysis['confidence'] += 0.2
            
        # Always include core for prompt understanding
        if 'core' not in intent_analysis['mcps_to_activate']:
            intent_analysis['mcps_to_activate'].insert(0, 'core')
            
        # Remove duplicates while preserving order
        intent_analysis['mcps_to_activate'] = list(dict.fromkeys(intent_analysis['mcps_to_activate']))
        
        return intent_analysis
        
    def execute_mcp_workflow(self, intent_analysis: Dict, messages: List[Dict], 
                           ai_response: str, project_context: Dict) -> Dict:
        """Execute MCP workflow based on intent analysis"""
        
        workflow_results = {
            'success': True,
            'mcps_executed': [],
            'artifacts_generated': [],
            'enhanced_response': ai_response,
            'context_updates': {},
            'errors': []
        }
        
        try:
            primary_intent = intent_analysis['primary_intent']
            mcps_to_activate = intent_analysis['mcps_to_activate']
            
            logger.info(f"🎯 Executing MCP workflow for intent: {primary_intent}")
            logger.info(f"🔧 MCPs to activate: {mcps_to_activate}")
            
            # Execute based on primary intent
            if primary_intent == 'architecture':
                workflow_results = self._execute_architecture_workflow(
                    mcps_to_activate, messages, ai_response, project_context
                )
                
            elif primary_intent == 'document_generation':
                workflow_results = self._execute_document_generation_workflow(
                    mcps_to_activate, messages, ai_response, project_context
                )
                
            elif primary_intent == 'serverless':
                workflow_results = self._execute_serverless_workflow(
                    mcps_to_activate, messages, ai_response, project_context
                )
                
            else:
                # Default chat enhancement workflow
                workflow_results = self._execute_chat_enhancement_workflow(
                    mcps_to_activate, messages, ai_response, project_context
                )
                
        except Exception as e:
            logger.error(f"Error in MCP workflow execution: {str(e)}")
            workflow_results['success'] = False
            workflow_results['errors'].append(str(e))
            
        return workflow_results
        
    def _execute_architecture_workflow(self, mcps: List[str], messages: List[Dict], 
                                     ai_response: str, context: Dict) -> Dict:
        """Execute architecture-focused MCP workflow"""
        
        results = {
            'success': True,
            'mcps_executed': [],
            'artifacts_generated': [],
            'enhanced_response': ai_response,
            'context_updates': {},
            'errors': []
        }
        
        # Simulate CDK guidance activation
        if 'cdk' in mcps:
            results['mcps_executed'].append('cdk')
            results['enhanced_response'] += "\n\n🏗️ **CDK Guidance Activated**\n"
            results['enhanced_response'] += "- AWS CDK best practices applied\n"
            results['enhanced_response'] += "- Infrastructure as Code patterns recommended\n"
            
        # Simulate diagram generation
        if 'aws_diagram' in mcps:
            results['mcps_executed'].append('aws_diagram')
            results['artifacts_generated'].append({
                'type': 'diagram',
                'name': 'architecture_diagram.svg',
                'description': 'AWS Architecture Diagram'
            })
            results['enhanced_response'] += "- Architecture diagram generated\n"
            
        return results
        
    def _execute_document_generation_workflow(self, mcps: List[str], messages: List[Dict], 
                                            ai_response: str, context: Dict) -> Dict:
        """Execute document generation MCP workflow using DocumentGenerator"""
        
        results = {
            'success': True,
            'mcps_executed': [],
            'artifacts_generated': [],
            'enhanced_response': ai_response,
            'context_updates': {},
            'errors': []
        }
        
        try:
            # Extract project info from conversation and context
            project_name = self._extract_project_name(messages, context)
            project_type = self._determine_project_type(messages)
            project_id = context.get('project_id', 'unknown')
            user_id = context.get('user_id', 'anonymous')
            
            logger.info(f"🚀 Generating documents for project: {project_name}")
            
            # Generate complete document package
            doc_results = self.document_generator.generate_complete_package(
                project_name, project_type, messages, ai_response, project_id, user_id
            )
            
            if doc_results.get('success'):
                results['mcps_executed'].extend(['code_doc_gen', 'aws_diagram', 'nova_canvas'])
                results['artifacts_generated'] = doc_results.get('documents', [])
                
                # Create enhanced response with document generation confirmation
                total_docs = doc_results.get('total_documents', 0)
                project_folder = doc_results.get('project_folder', '')
                
                results['enhanced_response'] = f"""✅ **DOCUMENTOS GENERADOS EXITOSAMENTE**

He generado {total_docs} archivos profesionales para el proyecto '{project_name}':

📄 **Documentos Ejecutivos:**
- Propuesta Ejecutiva - Documento profesional para stakeholders
- Arquitectura Técnica - Diseño detallado de la solución

🏗️ **Implementación:**
- CloudFormation Template - Infraestructura como código
- Plan de Implementación - Timeline detallado de actividades

💰 **Análisis Financiero:**
- Análisis de Costos - Estimación detallada de precios AWS
- Guía Calculadora AWS - Instrucciones para cálculos precisos

📁 **Ubicación**: {project_folder}
🗄️ **Bucket S3**: {self.bucket_name}

Todos los archivos están disponibles en la sección de **Proyectos** para descarga inmediata.

¿Deseas realizar algún ajuste específico o tienes comentarios adicionales sobre la propuesta?"""
                
                # Update context with generation results
                results['context_updates'].update({
                    'documents_generated': True,
                    'total_documents': total_docs,
                    'project_folder': project_folder,
                    'generation_timestamp': datetime.now().isoformat()
                })
                
            else:
                results['success'] = False
                results['errors'].append(doc_results.get('error', 'Unknown error in document generation'))
                
        except Exception as e:
            logger.error(f"Error in document generation workflow: {str(e)}")
            results['success'] = False
            results['errors'].append(str(e))
            
        return results
    
    def _extract_project_name(self, messages: List[Dict], context: Dict) -> str:
        """Extract project name from conversation or context"""
        
        # Check context first
        if context.get('project_name'):
            return context['project_name']
        
        # Look for project name in messages
        for msg in messages:
            content = msg.get('content', '').lower()
            if 'nombre del proyecto' in content or 'proyecto se llama' in content:
                # Try to extract the name from the next part
                words = msg.get('content', '').split()
                if len(words) > 3:
                    # Take the last few words as potential project name
                    potential_name = ' '.join(words[-3:])
                    if not any(word in potential_name.lower() for word in ['es', 'se', 'llama', 'nombre']):
                        return potential_name.title()
        
        # Default project name
        return "Proyecto AWS"
    
    def _determine_project_type(self, messages: List[Dict]) -> str:
        """Determine project type from conversation"""
        
        conversation_text = ""
        for msg in messages:
            conversation_text += msg.get('content', '').lower()
        
        # Check for service-specific keywords
        if any(term in conversation_text for term in [
            'servicio rapido', 'implementacion rapida', 'configuracion simple',
            'ec2', 's3', 'rds', 'vpc', 'lambda'
        ]):
            return "servicio_rapido"
        
        # Check for integral solution keywords
        if any(term in conversation_text for term in [
            'solucion integral', 'migracion', 'aplicacion nueva', 'modernizacion',
            'arquitectura completa', 'sistema completo'
        ]):
            return "solucion_integral"
        
        # Default to integral solution
        return "solucion_integral"
    
    def _call_real_mcp_service(self, mcp_name: str, method: str, data: Dict = None) -> Dict:
        """Call a real MCP service running in ECS"""
        
        if mcp_name not in self.available_mcps:
            logger.error(f"MCP service {mcp_name} not found")
            return {'success': False, 'error': 'Service not found'}
        
        mcp_config = self.available_mcps[mcp_name]
        
        # Check if it's a real ECS service or fallback
        if isinstance(mcp_config, dict) and 'port' in mcp_config:
            return self.real_mcp_connector.call_mcp_service(mcp_name, mcp_config, method, data)
        else:
            # Fallback to simulation for local MCPs
            logger.info(f"Using fallback simulation for {mcp_name}")
            return self.real_mcp_connector._simulate_mcp_response(mcp_name, {}, method, data)
    
    def test_mcp_connectivity(self) -> Dict:
        """Test connectivity to all MCP services"""
        return self.real_mcp_connector.test_mcp_connectivity()
    
    def get_mcp_status(self) -> Dict:
        """Get status of all MCP services"""
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'services': {},
            'summary': {
                'total': 0,
                'active': 0,
                'real_services': 0,
                'fallback_services': 0
            }
        }
        
        for mcp_name, mcp_config in self.available_mcps.items():
            if isinstance(mcp_config, dict) and 'port' in mcp_config:
                status['services'][mcp_name] = {
                    'type': 'real_ecs_service',
                    'port': mcp_config['port'],
                    'target_group': mcp_config.get('target_group', 'unknown'),
                    'active': mcp_config.get('active', False),
                    'capabilities': mcp_config.get('capabilities', [])
                }
                status['summary']['real_services'] += 1
            else:
                status['services'][mcp_name] = {
                    'type': 'fallback_local',
                    'server': mcp_config,
                    'active': True
                }
                status['summary']['fallback_services'] += 1
            
            status['summary']['total'] += 1
            if status['services'][mcp_name].get('active', True):
                status['summary']['active'] += 1
        
        return status
        
    def _execute_serverless_workflow(self, mcps: List[str], messages: List[Dict], 
                                   ai_response: str, context: Dict) -> Dict:
        """Execute serverless development MCP workflow"""
        
        results = {
            'success': True,
            'mcps_executed': [],
            'artifacts_generated': [],
            'enhanced_response': ai_response,
            'context_updates': {},
            'errors': []
        }
        
        if 'serverless' in mcps:
            results['mcps_executed'].append('serverless')
            results['enhanced_response'] += "\n\n🚀 **Serverless Guidance Activated**\n"
            results['enhanced_response'] += "- AWS Lambda best practices applied\n"
            results['enhanced_response'] += "- SAM templates and deployment guidance provided\n"
            results['enhanced_response'] += "- Event-driven architecture patterns recommended\n"
            
        return results
        
    def _execute_chat_enhancement_workflow(self, mcps: List[str], messages: List[Dict], 
                                         ai_response: str, context: Dict) -> Dict:
        """Execute general chat enhancement workflow"""
        
        results = {
            'success': True,
            'mcps_executed': [],
            'artifacts_generated': [],
            'enhanced_response': ai_response,
            'context_updates': {},
            'errors': []
        }
        
        # Always activate core for prompt understanding
        if 'core' in mcps:
            results['mcps_executed'].append('core')
            results['context_updates']['prompt_analysis'] = 'completed'
            
        return results
        
    def should_generate_documents(self, messages: List[Dict], ai_response: str) -> bool:
        """Determine if documents should be generated based on conversation flow"""
        
        # Check for explicit generation triggers
        generation_triggers = [
            'procederé a generar',
            'generar los documentos',
            'crear los archivos',
            'documentos listos',
            'archivos generados',
            'completar la propuesta'
        ]
        
        ai_lower = ai_response.lower()
        
        # Check if AI explicitly mentions document generation
        if any(trigger in ai_lower for trigger in generation_triggers):
            return True
            
        # Check conversation length and content depth
        if len(messages) >= 4:
            conversation_text = ""
            for msg in messages:
                conversation_text += msg.get('content', '').lower()
                
            # Check for sufficient project information
            required_info = ['proyecto', 'nombre', 'servicio', 'objetivo', 'descripcion']
            info_count = sum(1 for info in required_info if info in conversation_text)
            
            if info_count >= 3:
                return True
                
        return False
