"""
MCP Caller inteligente optimizado para Amazon Q Developer CLI
"""
import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Any

logger = logging.getLogger()

class IntelligentMCPCaller:
    def __init__(self):
        self.mcp_endpoints = {
            'core': 'https://mcp.danielingram.shop/core',
            'diagram': 'https://mcp.danielingram.shop/diagram',
            'pricing': 'https://mcp.danielingram.shop/pricing',
            'cfn': 'https://mcp.danielingram.shop/cfn',
            'docgen': 'https://mcp.danielingram.shop/docgen'
        }
    async def generate_intelligent_questions(self, project_data: Dict[str, Any], messages: List[Dict]) -> str:
        """
        Genera preguntas inteligentes específicas basadas en los servicios AWS mencionados
        Usa MCP Core para obtener contexto y mejores prácticas
        """
        try:
            services = project_data.get('services', [])
            project_name = project_data.get('name', 'el proyecto')
            
            # Construir contexto para MCP Core
            context = {
                'project_name': project_name,
                'services': services,
                'conversation_history': messages[-3:] if len(messages) > 3 else messages,  # Últimos 3 mensajes
                'task': 'generate_intelligent_requirements_questions'
            }
            
            # Llamar a MCP Core para obtener preguntas inteligentes
            core_response = await self._call_mcp_endpoint('core', {
                'action': 'generate_service_questions',
                'context': context
            })
            
            if core_response and 'questions' in core_response:
                return core_response['questions']
            
            # Fallback: usar lógica inteligente local
            return self._generate_fallback_questions(services, project_name)
            
        except Exception as e:
            logger.error(f"❌ Error generando preguntas inteligentes: {str(e)}")
            return self._generate_fallback_questions(project_data.get('services', []), project_data.get('name', 'el proyecto'))
    
    def _generate_fallback_questions(self, services: List[str], project_name: str) -> str:
        """
        Genera preguntas inteligentes como fallback cuando MCP no está disponible
        """
        services_text = ', '.join(services) if services else 'los servicios mencionados'
        
        # Detectar servicios específicos y hacer preguntas relevantes
        questions = []
        
        # Análisis inteligente de servicios
        service_context = ' '.join(services).lower()
        
        if any(term in service_context for term in ['vpc', 'red', 'network']):
            questions.extend([
                "• ¿Necesitas conectividad híbrida con tu datacenter on-premises?",
                "• ¿Qué rangos de IP prefieres para las subnets?",
                "• ¿Requieres NAT Gateway para subnets privadas?"
            ])
        
        if any(term in service_context for term in ['cloudfront', 'cdn', 'distribucion']):
            questions.extend([
                "• ¿Qué tipo de contenido vas a distribuir (estático, dinámico, streaming)?",
                "• ¿Necesitas certificado SSL/TLS personalizado?",
                "• ¿Qué origins usarás (S3, ALB, EC2, custom)?"
            ])
        
        if any(term in service_context for term in ['elb', 'alb', 'balanceador', 'load balancer']):
            questions.extend([
                "• ¿Qué tipo de tráfico balancearás (HTTP/HTTPS, TCP, UDP)?",
                "• ¿Necesitas SSL termination en el balanceador?",
                "• ¿Cuántas instancias backend aproximadamente?"
            ])
        
        if any(term in service_context for term in ['rds', 'database', 'base de datos']):
            questions.extend([
                "• ¿Qué engine de base de datos prefieres (MySQL, PostgreSQL, Oracle)?",
                "• ¿Necesitas Multi-AZ para alta disponibilidad?",
                "• ¿Cuál es el tamaño estimado de datos?"
            ])
        
        if any(term in service_context for term in ['s3', 'storage', 'almacenamiento']):
            questions.extend([
                "• ¿Qué tipo de datos almacenarás (documentos, imágenes, backups)?",
                "• ¿Necesitas versionado o lifecycle policies?",
                "• ¿Requieres encriptación específica?"
            ])
        
        # Si no hay preguntas específicas, usar preguntas generales inteligentes
        if not questions:
            questions = [
                f"• ¿Cuál es el volumen de tráfico esperado para {services_text}?",
                "• ¿Qué región de AWS prefieres y por qué?",
                "• ¿Tienes requisitos específicos de compliance o seguridad?",
                "• ¿Necesitas alta disponibilidad multi-AZ?"
            ]
        
        # Agregar siempre preguntas de contexto
        questions.extend([
            "• ¿Qué región de AWS prefieres?",
            "• ¿Tienes algún requisito especial de seguridad o compliance?"
        ])
        
        return f"""Excelente! Para implementar {services_text} de manera óptima, necesito entender mejor tu caso específico:

{chr(10).join(questions)}

Como arquitecto AWS, estas preguntas me ayudan a diseñar la solución más eficiente y siguiendo las mejores prácticas."""

        """
        Orquesta la generación inteligente de documentos usando MCPs
        Simula el comportamiento de Amazon Q Developer CLI
        """
        try:
            logger.info(f"🧠 Iniciando generación inteligente para: {project_data['name']}")
            
            # Resultados que se generarán
            results = {}
            mcp_services_used = []
            
            # 1. Core Analysis (siempre se ejecuta)
            core_result = await self._call_core_analysis(project_data)
            if core_result:
                results['core_analysis'] = core_result
                mcp_services_used.append('core_analysis')
                logger.info("✅ Core analysis completado")
            
            # 2. Architecture Diagram (para todos los proyectos)
            diagram_result = await self._call_diagram_generation(project_data)
            if diagram_result:
                results['architecture_diagram'] = diagram_result
                mcp_services_used.append('architecture_diagram')
                logger.info("✅ Diagrama de arquitectura generado")
            
            # 3. Cost Estimation (para todos los proyectos)
            cost_result = await self._call_cost_estimation(project_data)
            if cost_result:
                results['cost_estimation'] = cost_result
                mcp_services_used.append('cost_estimation')
                logger.info("✅ Estimación de costos completada")
            
            # 4. Infrastructure Code (CloudFormation)
            cfn_result = await self._call_cloudformation_generation(project_data)
            if cfn_result:
                results['infrastructure_code'] = cfn_result
                mcp_services_used.append('infrastructure_code')
                logger.info("✅ Código de infraestructura generado")
            
            # 5. Documentation Generation
            doc_result = await self._call_documentation_generation(project_data)
            if doc_result:
                results['generated_documents'] = doc_result
                mcp_services_used.append('generated_documents')
                logger.info("✅ Documentación generada")
            
            return {
                'success': True,
                'results': results,
                'mcp_services_used': mcp_services_used,
                'total_services': len(mcp_services_used)
            }
            
        except Exception as e:
            logger.error(f"❌ Error en generación inteligente: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'results': {},
                'mcp_services_used': []
            }
    
    async def _call_core_analysis(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Llama al MCP Core para análisis de prompt"""
        try:
            # Simular llamada al MCP Core
            await asyncio.sleep(0.1)  # Simular latencia de red
            
            return {
                'service': 'core_analysis',
                'analysis': f"Análisis completo del proyecto {project_data['name']}",
                'recommendations': [
                    'Implementar alta disponibilidad',
                    'Configurar monitoreo y alertas',
                    'Aplicar mejores prácticas de seguridad'
                ],
                'status': 'completed'
            }
        except Exception as e:
            logger.error(f"Error en core analysis: {str(e)}")
            return None
    
    async def _call_diagram_generation(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera diagrama de arquitectura AWS"""
        try:
            await asyncio.sleep(0.2)
            
            # Generar código de diagrama basado en servicios
            services = project_data.get('services', [])
            diagram_code = self._generate_diagram_code(project_data['name'], services)
            
            return {
                'service': 'architecture_diagram',
                'filename': f"{project_data['name']}_architecture.png",
                'diagram_code': diagram_code,
                'services_included': services,
                'status': 'completed'
            }
        except Exception as e:
            logger.error(f"Error en diagram generation: {str(e)}")
            return None
    
    async def _call_cost_estimation(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Estima costos AWS"""
        try:
            await asyncio.sleep(0.15)
            
            services = project_data.get('services', [])
            cost_breakdown = self._calculate_costs(services)
            
            return {
                'service': 'cost_estimation',
                'filename': f"{project_data['name']}_costs.xlsx",
                'monthly_cost': cost_breakdown['total'],
                'breakdown': cost_breakdown['details'],
                'region': 'us-east-1',
                'status': 'completed'
            }
        except Exception as e:
            logger.error(f"Error en cost estimation: {str(e)}")
            return None
    
    async def _call_cloudformation_generation(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera template CloudFormation"""
        try:
            await asyncio.sleep(0.25)
            
            services = project_data.get('services', [])
            cfn_template = self._generate_cloudformation_template(project_data['name'], services)
            
            return {
                'service': 'infrastructure_code',
                'filename': f"{project_data['name']}_infrastructure.yaml",
                'template': cfn_template,
                'resources_count': len(cfn_template.get('Resources', {})),
                'status': 'completed'
            }
        except Exception as e:
            logger.error(f"Error en CloudFormation generation: {str(e)}")
            return None
    
    async def _call_documentation_generation(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera documentación técnica"""
        try:
            await asyncio.sleep(0.3)
            
            documents = self._generate_documentation_structure(project_data)
            
            return {
                'service': 'generated_documents',
                'documents': documents,
                'total_documents': len(documents),
                'status': 'completed'
            }
        except Exception as e:
            logger.error(f"Error en documentation generation: {str(e)}")
            return None
    
    def _generate_diagram_code(self, project_name: str, services: List[str]) -> str:
        """Genera código de diagrama AWS"""
        code = f'''from diagrams import Diagram, Cluster
from diagrams.aws.general import Users
from diagrams.aws.compute import Lambda
from diagrams.aws.network import ELB, ALB
from diagrams.aws.storage import S3

with Diagram("{project_name}", show=False, filename="{project_name}_architecture"):
    users = Users("Usuarios")
    
    with Cluster("AWS Cloud"):
'''
        
        for service in services:
            if 'ELB' in service or 'ALB' in service:
                code += f'        lb = ALB("Load Balancer")\n'
                code += f'        users >> lb\n'
        
        code += '''
    # Configuración adicional basada en servicios
'''
        
        return code
    
    def _calculate_costs(self, services: List[str]) -> Dict[str, Any]:
        """Calcula costos estimados"""
        base_cost = 25.0
        service_costs = {
            'ELB': 22.0,
            'ALB': 22.0,
            'EC2': 75.0,
            'RDS': 120.0,
            'S3': 8.0,
            'VPC': 5.0
        }
        
        total = base_cost
        details = [{'service': 'Base AWS', 'monthly_cost': base_cost}]
        
        for service in services:
            for service_name, cost in service_costs.items():
                if service_name in service:
                    total += cost
                    details.append({
                        'service': service_name,
                        'monthly_cost': cost,
                        'description': f'Costo mensual estimado para {service_name}'
                    })
        
        return {'total': total, 'details': details}
    
    def _generate_cloudformation_template(self, project_name: str, services: List[str]) -> Dict[str, Any]:
        """Genera template CloudFormation"""
        template = {
            'AWSTemplateFormatVersion': '2010-09-09',
            'Description': f'Infrastructure template for {project_name}',
            'Parameters': {
                'Environment': {
                    'Type': 'String',
                    'Default': 'prod',
                    'Description': 'Environment name'
                }
            },
            'Resources': {}
        }
        
        # Agregar recursos basados en servicios
        for service in services:
            if 'ELB' in service or 'ALB' in service:
                template['Resources']['ApplicationLoadBalancer'] = {
                    'Type': 'AWS::ElasticLoadBalancingV2::LoadBalancer',
                    'Properties': {
                        'Name': f'{project_name}-alb',
                        'Scheme': 'internet-facing',
                        'Type': 'application',
                        'IpAddressType': 'ipv4'
                    }
                }
                
                template['Resources']['ALBSecurityGroup'] = {
                    'Type': 'AWS::EC2::SecurityGroup',
                    'Properties': {
                        'GroupDescription': f'Security group for {project_name} ALB',
                        'SecurityGroupIngress': [
                            {
                                'IpProtocol': 'tcp',
                                'FromPort': 80,
                                'ToPort': 80,
                                'CidrIp': '0.0.0.0/0'
                            },
                            {
                                'IpProtocol': 'tcp',
                                'FromPort': 443,
                                'ToPort': 443,
                                'CidrIp': '0.0.0.0/0'
                            }
                        ]
                    }
                }
        
        return template
    
    def _generate_documentation_structure(self, project_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Genera estructura de documentación"""
        return [
            {
                'name': 'Resumen Ejecutivo',
                'filename': f"{project_data['name']}_executive_summary.docx",
                'type': 'executive',
                'sections': ['Objetivo', 'Alcance', 'Beneficios', 'Inversión']
            },
            {
                'name': 'Documentación Técnica',
                'filename': f"{project_data['name']}_technical_docs.docx",
                'type': 'technical',
                'sections': ['Arquitectura', 'Servicios AWS', 'Configuración', 'Seguridad']
            },
            {
                'name': 'Plan de Implementación',
                'filename': f"{project_data['name']}_implementation_plan.xlsx",
                'type': 'planning',
                'sections': ['Fases', 'Actividades', 'Cronograma', 'Recursos']
            }
        ]
    
    async def _call_mcp_endpoint(self, service: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Llama a un endpoint MCP específico
        """
        try:
            endpoint = self.mcp_endpoints.get(service)
            if not endpoint:
                logger.warning(f"⚠️ Endpoint MCP no encontrado para: {service}")
                return {}
            
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(endpoint, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"✅ MCP {service} respondió exitosamente")
                        return result
                    else:
                        logger.warning(f"⚠️ MCP {service} respondió con status {response.status}")
                        return {}
                        
        except Exception as e:
            logger.error(f"❌ Error llamando MCP {service}: {str(e)}")
            return {}
