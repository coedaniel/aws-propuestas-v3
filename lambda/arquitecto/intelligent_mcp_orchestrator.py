"""
Intelligent MCP Orchestrator
Amazon Q Developer CLI Style - Phase-based MCP activation with intelligent triggers
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class IntelligentTriggerSystem:
    """Intelligent trigger system for MCP activation"""
    
    def __init__(self):
        self.technical_keywords = [
            'ec2', 'rds', 'lambda', 'vpc', 's3', 'cloudfront', 'elb', 'ses',
            'dynamodb', 'api gateway', 'ecs', 'eks', 'fargate', 'aurora'
        ]
        
        self.project_type_keywords = {
            'servicio_rapido': ['servicio rapido', 'quick service', 'simple deployment'],
            'solucion_integral': ['solucion integral', 'complete solution', 'full architecture', 'enterprise'],
            'migracion': ['migracion', 'migration', 'move to cloud'],
            'modernizacion': ['modernizacion', 'modernization', 'refactor', 'containerize']
        }
    
    def analyze_conversation_readiness(self, messages: List[Dict], project_state: Dict) -> Dict:
        """Analyze if conversation is ready for document generation"""
        
        readiness_indicators = {
            'project_name_identified': False,
            'project_type_clarified': False,
            'technical_requirements_gathered': False,
            'scope_boundaries_defined': False,
            'sufficient_context_depth': False
        }
        
        conversation_text = ' '.join([msg.get('content', '') for msg in messages])
        conversation_lower = conversation_text.lower()
        
        # 1. Project name identification
        project_name = self.extract_project_name(messages)
        if project_name and len(project_name) > 2:
            readiness_indicators['project_name_identified'] = True
        
        # 2. Project type clarification
        for project_type, keywords in self.project_type_keywords.items():
            if any(keyword in conversation_lower for keyword in keywords):
                readiness_indicators['project_type_clarified'] = True
                break
        
        # 3. Technical requirements gathering
        technical_mentions = sum(1 for keyword in self.technical_keywords 
                               if keyword in conversation_lower)
        if technical_mentions >= 2:
            readiness_indicators['technical_requirements_gathered'] = True
        
        # 4. Scope boundaries definition
        scope_indicators = ['region', 'environment', 'users', 'budget', 'timeline']
        scope_mentions = sum(1 for indicator in scope_indicators 
                           if indicator in conversation_lower)
        if scope_mentions >= 1:
            readiness_indicators['scope_boundaries_defined'] = True
        
        # 5. Sufficient context depth
        if len(messages) >= 6:  # Minimum exchanges for context
            readiness_indicators['sufficient_context_depth'] = True
        
        readiness_score = sum(readiness_indicators.values()) / len(readiness_indicators)
        
        return {
            'readiness_score': readiness_score,
            'indicators': readiness_indicators,
            'recommendation': self.get_recommendation(readiness_score),
            'missing_context': self.identify_missing_context(readiness_indicators),
            'project_name': project_name,
            'detected_services': self.extract_services(conversation_text),
            'project_type': self.detect_project_type(conversation_lower)
        }
    
    def extract_project_name(self, messages: List[Dict]) -> Optional[str]:
        """Extract project name from conversation"""
        for msg in messages:
            if msg.get('role') == 'user':
                content = msg.get('content', '').strip()
                # Look for single word responses (likely project names)
                if len(content.split()) == 1 and len(content) > 2 and content.isalnum():
                    return content.lower()
        return None
    
    def extract_services(self, conversation_text: str) -> List[str]:
        """Extract AWS services mentioned in conversation"""
        detected_services = []
        conversation_lower = conversation_text.lower()
        
        for service in self.technical_keywords:
            if service in conversation_lower:
                detected_services.append(service)
        
        return detected_services
    
    def detect_project_type(self, conversation_lower: str) -> Optional[str]:
        """Detect project type from conversation"""
        for project_type, keywords in self.project_type_keywords.items():
            if any(keyword in conversation_lower for keyword in keywords):
                return project_type
        return None
    
    def get_recommendation(self, score: float) -> str:
        """Get recommendation based on readiness score"""
        if score >= 0.8:
            return 'READY_FOR_GENERATION'
        elif score >= 0.6:
            return 'NEEDS_CLARIFICATION'
        else:
            return 'INSUFFICIENT_CONTEXT'
    
    def identify_missing_context(self, indicators: Dict) -> List[str]:
        """Identify what context is missing"""
        missing = []
        
        if not indicators['project_name_identified']:
            missing.append('project_name')
        if not indicators['project_type_clarified']:
            missing.append('project_type')
        if not indicators['technical_requirements_gathered']:
            missing.append('technical_requirements')
        if not indicators['scope_boundaries_defined']:
            missing.append('scope_definition')
        if not indicators['sufficient_context_depth']:
            missing.append('more_conversation')
        
        return missing
    
    def generate_clarifying_questions(self, readiness_analysis: Dict) -> List[str]:
        """Generate clarifying questions based on missing context"""
        questions = []
        missing = readiness_analysis['missing_context']
        
        if 'project_name' in missing:
            questions.append("¿Cual es el nombre del proyecto?")
        
        if 'project_type' in missing:
            questions.append("¿Es una solucion integral o un servicio rapido especifico?")
        
        if 'technical_requirements' in missing:
            questions.append("¿Que servicios AWS necesitas? (EC2, RDS, Lambda, etc.)")
        
        if 'scope_definition' in missing:
            questions.append("¿En que region de AWS? ¿Cuantos usuarios aproximadamente?")
        
        return questions


class IntelligentMCPOrchestrator:
    """Intelligent MCP Orchestrator with phase-based execution"""
    
    def __init__(self):
        self.mcp_endpoints = {
            'core': 'https://mcp.danielingram.shop/core',
            'pricing': 'https://mcp.danielingram.shop/pricing',
            'awsdocs': 'https://mcp.danielingram.shop/awsdocs',
            'cfn': 'https://mcp.danielingram.shop/cfn',
            'diagram': 'https://mcp.danielingram.shop/diagram',
            'docgen': 'https://mcp.danielingram.shop/docgen'
        }
        
        self.trigger_system = IntelligentTriggerSystem()
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60))
    
    async def call_mcp_tool(self, mcp_name: str, tool_name: str, arguments: Dict) -> Dict:
        """Call a specific MCP tool"""
        try:
            endpoint = self.mcp_endpoints.get(mcp_name)
            if not endpoint:
                return {"error": f"MCP {mcp_name} not found"}
            
            payload = {
                "tool": tool_name,
                "arguments": arguments
            }
            
            async with self.session.post(
                f"{endpoint}/call-tool",
                json=payload,
                headers={'Content-Type': 'application/json'}
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ MCP {mcp_name} tool {tool_name} executed successfully")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"❌ MCP {mcp_name} tool {tool_name} failed: {response.status} - {error_text}")
                    return {"error": f"MCP call failed: {response.status}"}
                    
        except Exception as e:
            logger.error(f"❌ Error calling MCP {mcp_name}: {str(e)}")
            return {"error": f"MCP call error: {str(e)}"}
    
    async def phase_1_analysis(self, conversation_context: Dict) -> Dict:
        """PHASE 1: Analysis and Understanding (MANDATORY)"""
        
        logger.info("🔍 Starting Phase 1: Analysis and Understanding")
        
        # 1.1 Core MCP - Context analysis (CRITICAL)
        core_analysis = await self.call_mcp_tool('core', 'prompt_understanding', {
            'conversation': conversation_context['messages'],
            'project_state': conversation_context['project_state']
        })
        
        if core_analysis.get('error'):
            logger.warning(f"Core MCP failed: {core_analysis['error']}")
            # Fallback to local analysis
            core_analysis = self.fallback_analysis(conversation_context)
        
        # 1.2 AWS Docs MCP - Official information (CRITICAL)
        services_detected = core_analysis.get('services_detected', [])
        docs_context = {}
        
        for service in services_detected[:3]:  # Limit to top 3 services
            docs_result = await self.call_mcp_tool('awsdocs', 'search_documentation', {
                'service': service,
                'query': f'{service} best practices architecture',
                'context': 'solution_design'
            })
            
            if not docs_result.get('error'):
                docs_context[service] = docs_result
        
        readiness_score = self.calculate_readiness_score(core_analysis, docs_context)
        
        return {
            'core_analysis': core_analysis,
            'official_docs': docs_context,
            'readiness_score': readiness_score,
            'next_phase_requirements': self.determine_next_phase_requirements(core_analysis),
            'mcps_used': ['awslabscore_mcp_server___prompt_understanding', 'awslabsaws_documentation_mcp_server___search_documentation']
        }
    
    async def phase_2_validation(self, phase_1_results: Dict) -> Dict:
        """PHASE 2: Validation and Enrichment (CONDITIONAL)"""
        
        logger.info("💰 Starting Phase 2: Validation and Enrichment")
        
        if phase_1_results['readiness_score'] < 0.7:
            return {
                'status': 'insufficient_context',
                'action': 'request_more_info',
                'missing_elements': phase_1_results.get('missing_context', [])
            }
        
        core_analysis = phase_1_results['core_analysis']
        
        # 2.1 Pricing MCP - Real costs
        pricing_analysis = await self.call_mcp_tool('pricing', 'calculate_costs', {
            'services': core_analysis.get('services_detected', []),
            'region': core_analysis.get('region', 'us-east-1'),
            'usage_patterns': core_analysis.get('usage_patterns', {}),
            'context': phase_1_results['official_docs']
        })
        
        return {
            'status': 'validated',
            'pricing_validated': pricing_analysis,
            'cost_optimization_suggestions': pricing_analysis.get('optimizations', []),
            'mcps_used': ['awslabspricing_mcp_server___calculate_costs']
        }
    
    async def phase_3_generation(self, phase_1_results: Dict, phase_2_results: Dict) -> Dict:
        """PHASE 3: Specialized Generation (PARALLEL)"""
        
        logger.info("🚀 Starting Phase 3: Specialized Generation")
        
        # Prepare enriched context
        enriched_context = {
            **phase_1_results['core_analysis'],
            'official_guidance': phase_1_results['official_docs'],
            'cost_constraints': phase_2_results.get('pricing_validated', {})
        }
        
        # Execute in parallel for efficiency
        tasks = []
        mcps_used = []
        
        # 3.1 CloudFormation MCP
        if enriched_context.get('requires_infrastructure', True):
            tasks.append(
                self.call_mcp_tool('cfn', 'generate_template', {
                    'architecture_pattern': enriched_context.get('architecture_pattern', 'basic'),
                    'services': enriched_context.get('services_detected', []),
                    'best_practices': phase_1_results['official_docs'],
                    'cost_optimization': True
                })
            )
            mcps_used.append('awslabscloudformation_mcp_server___generate_template')
        
        # 3.2 Diagram MCP
        if enriched_context.get('requires_visualization', True):
            tasks.append(
                self.call_mcp_tool('diagram', 'generate_diagram', {
                    'architecture': enriched_context.get('architecture_pattern', 'basic'),
                    'services': enriched_context.get('services_detected', []),
                    'official_icons': True,
                    'include_costs': phase_2_results.get('pricing_validated', {})
                })
            )
            mcps_used.append('awslabsaws_diagram_mcp_server___generate_diagram')
        
        # 3.3 Custom Document Generation (Not an MCP, but executed here)
        tasks.append(
            self.generate_custom_documents(enriched_context, phase_2_results)
        )
        mcps_used.append('awslabsfile_operations___create_document')
        
        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            'status': 'completed',
            'artifacts': self.process_generation_results(results),
            'mcps_used': mcps_used
        }
    
    async def intelligent_mcp_activation(self, messages: List[Dict], project_state: Dict, model_response: str) -> Dict:
        """Main intelligent MCP activation system"""
        
        logger.info("🧠 Starting Intelligent MCP Activation")
        
        # 1. Analyze conversation readiness
        readiness = self.trigger_system.analyze_conversation_readiness(messages, project_state)
        
        logger.info(f"Readiness Score: {readiness['readiness_score']:.2f}")
        logger.info(f"Recommendation: {readiness['recommendation']}")
        
        # 2. Intelligent decision based on context
        if readiness['recommendation'] == 'READY_FOR_GENERATION':
            
            try:
                # PHASE 1: ALWAYS - Fundamental analysis
                phase_1 = await self.phase_1_analysis({
                    'messages': messages,
                    'project_state': project_state,
                    'model_response': model_response
                })
                
                # Verify Phase 1 success
                if phase_1['readiness_score'] >= 0.7:
                    
                    # PHASE 2: CONDITIONAL - Validation
                    phase_2 = await self.phase_2_validation(phase_1)
                    
                    if phase_2['status'] != 'insufficient_context':
                        
                        # PHASE 3: PARALLEL - Generation
                        phase_3 = await self.phase_3_generation(phase_1, phase_2)
                        
                        return {
                            'status': 'SUCCESS',
                            'documents_generated': phase_3['artifacts'],
                            'mcp_execution_log': {
                                'phase_1': phase_1,
                                'phase_2': phase_2,
                                'phase_3': phase_3
                            },
                            'total_mcps_used': (
                                phase_1.get('mcps_used', []) +
                                phase_2.get('mcps_used', []) +
                                phase_3.get('mcps_used', [])
                            )
                        }
                
                # If not ready, request more information
                return {
                    'status': 'NEEDS_MORE_CONTEXT',
                    'missing_elements': phase_1.get('missing_context', []),
                    'suggested_questions': self.trigger_system.generate_clarifying_questions(readiness)
                }
                
            except Exception as e:
                logger.error(f"Error in MCP activation: {str(e)}")
                return {
                    'status': 'ERROR',
                    'error': str(e),
                    'fallback_action': 'continue_conversation'
                }
        
        elif readiness['recommendation'] == 'NEEDS_CLARIFICATION':
            return {
                'status': 'CLARIFICATION_NEEDED',
                'missing_context': readiness['missing_context'],
                'suggested_questions': self.trigger_system.generate_clarifying_questions(readiness)
            }
        
        else:
            return {
                'status': 'CONTINUE_CONVERSATION',
                'guidance': 'Necesito más información sobre el proyecto',
                'readiness_score': readiness['readiness_score']
            }
    
    def fallback_analysis(self, conversation_context: Dict) -> Dict:
        """Fallback analysis when Core MCP fails"""
        messages = conversation_context['messages']
        conversation_text = ' '.join([msg.get('content', '') for msg in messages])
        
        return {
            'services_detected': self.trigger_system.extract_services(conversation_text),
            'project_type': self.trigger_system.detect_project_type(conversation_text.lower()),
            'architecture_pattern': 'basic',
            'region': 'us-east-1',
            'fallback_used': True
        }
    
    def calculate_readiness_score(self, core_analysis: Dict, docs_context: Dict) -> float:
        """Calculate readiness score based on analysis results"""
        score = 0.5  # Base score
        
        if core_analysis.get('services_detected'):
            score += 0.2
        
        if core_analysis.get('project_type'):
            score += 0.2
        
        if docs_context:
            score += 0.1
        
        return min(score, 1.0)
    
    def determine_next_phase_requirements(self, core_analysis: Dict) -> Dict:
        """Determine what's needed for next phase"""
        return {
            'requires_pricing': bool(core_analysis.get('services_detected')),
            'requires_infrastructure': True,
            'requires_visualization': True
        }
    
    async def generate_custom_documents(self, context: Dict, pricing_results: Dict) -> Dict:
        """Generate custom documents (CSV, Word, etc.)"""
        # This would call your custom document generator
        # Not an MCP, but part of the generation process
        return {
            'csv_activities': 'Generated CSV content',
            'word_document': 'Generated Word content',
            'calculator_guide': 'Generated calculator guide'
        }
    
    def process_generation_results(self, results: List) -> List[str]:
        """Process the results from parallel generation"""
        artifacts = []
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Generation error: {result}")
                continue
            
            if isinstance(result, dict) and not result.get('error'):
                if 'template' in result:
                    artifacts.append('CloudFormation Template')
                if 'diagram' in result:
                    artifacts.append('Architecture Diagram')
                if 'csv_activities' in result:
                    artifacts.append('Activities CSV')
        
        return artifacts
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()
