"""
Sistema de Validación Avanzado para AWS Propuestas v3.2.1
Validación de calidad de documentos y respuestas de IA
"""

import re
import json
import logging
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class DocumentValidator:
    def __init__(self):
        """Initialize document validator with enhanced rules"""
        self.aws_services = {
            'LEX', 'LAMBDA', 'API_GATEWAY', 'DYNAMODB', 'RDS', 'S3', 'EC2', 
            'ECS', 'EKS', 'SAGEMAKER', 'BEDROCK', 'CLOUDFRONT', 'ROUTE53',
            'COGNITO', 'SNS', 'SQS', 'EVENTBRIDGE', 'STEP_FUNCTIONS', 
            'CLOUDWATCH', 'VPC', 'IAM', 'ELB', 'KINESIS', 'GLUE', 'REDSHIFT',
            'ELASTICSEARCH', 'FARGATE', 'AMPLIFY', 'APPSYNC'
        }
        
        self.generic_indicators = [
            'ejemplo genérico', 'plantilla estándar', 'contenido por defecto',
            'lorem ipsum', 'placeholder', 'template', 'generic example',
            'sample content', 'default text', 'boilerplate'
        ]
        
        self.quality_keywords = [
            'específico', 'personalizado', 'detallado', 'implementación',
            'arquitectura', 'solución', 'estrategia', 'optimización',
            'escalabilidad', 'seguridad', 'rendimiento', 'costos'
        ]
    
    def validate_document_quality(self, content: str, service: str, document_type: str) -> Dict[str, Any]:
        """
        Comprehensive document quality validation
        """
        try:
            logger.info(f"🔍 VALIDATING {document_type} FOR {service}")
            
            validation_result = {
                'document_type': document_type,
                'service': service,
                'timestamp': datetime.now().isoformat(),
                'scores': {},
                'issues': [],
                'recommendations': [],
                'overall_score': 0,
                'quality_level': 'unknown'
            }
            
            # Run all validation checks
            validation_result['scores']['service_relevance'] = self._check_service_relevance(content, service)
            validation_result['scores']['content_depth'] = self._check_content_depth(content)
            validation_result['scores']['technical_accuracy'] = self._check_technical_accuracy(content, service)
            validation_result['scores']['structure_quality'] = self._check_structure_quality(content, document_type)
            validation_result['scores']['generic_content'] = self._check_generic_content(content)
            validation_result['scores']['completeness'] = self._check_completeness(content, document_type)
            
            # Calculate overall score
            scores = validation_result['scores']
            weights = {
                'service_relevance': 0.25,
                'content_depth': 0.20,
                'technical_accuracy': 0.20,
                'structure_quality': 0.15,
                'generic_content': 0.10,
                'completeness': 0.10
            }
            
            overall_score = sum(scores[key] * weights[key] for key in scores.keys())
            validation_result['overall_score'] = round(overall_score, 2)
            
            # Determine quality level
            if overall_score >= 85:
                validation_result['quality_level'] = 'excellent'
            elif overall_score >= 70:
                validation_result['quality_level'] = 'good'
            elif overall_score >= 50:
                validation_result['quality_level'] = 'acceptable'
            else:
                validation_result['quality_level'] = 'poor'
            
            # Generate recommendations
            validation_result['recommendations'] = self._generate_recommendations(scores, service, document_type)
            
            logger.info(f"✅ VALIDATION COMPLETE: {overall_score:.1f}/100 ({validation_result['quality_level']})")
            return validation_result
            
        except Exception as e:
            logger.error(f"❌ VALIDATION ERROR: {str(e)}")
            return {
                'error': str(e),
                'overall_score': 0,
                'quality_level': 'error'
            }
    
    def _check_service_relevance(self, content: str, service: str) -> float:
        """Check how relevant the content is to the specified service"""
        try:
            content_lower = content.lower()
            service_lower = service.lower()
            
            # Direct service mentions
            direct_mentions = content_lower.count(service_lower)
            
            # Related terms based on service
            service_terms = self._get_service_related_terms(service)
            related_mentions = sum(content_lower.count(term.lower()) for term in service_terms)
            
            # AWS-specific terminology
            aws_terms = ['aws', 'amazon', 'cloud', 'serverless', 'managed service']
            aws_mentions = sum(content_lower.count(term) for term in aws_terms)
            
            # Calculate score
            total_mentions = direct_mentions * 3 + related_mentions * 2 + aws_mentions
            content_length = len(content.split())
            
            if content_length == 0:
                return 0
            
            relevance_ratio = total_mentions / (content_length / 100)  # Per 100 words
            score = min(100, relevance_ratio * 20)  # Scale to 0-100
            
            return max(0, score)
            
        except Exception as e:
            logger.error(f"❌ SERVICE RELEVANCE CHECK ERROR: {str(e)}")
            return 0
    
    def _check_content_depth(self, content: str) -> float:
        """Check the depth and detail level of content"""
        try:
            # Length indicators
            word_count = len(content.split())
            sentence_count = len(re.split(r'[.!?]+', content))
            paragraph_count = len(content.split('\n\n'))
            
            # Technical depth indicators
            technical_terms = [
                'arquitectura', 'implementación', 'configuración', 'integración',
                'escalabilidad', 'rendimiento', 'seguridad', 'monitoreo',
                'deployment', 'infrastructure', 'pipeline', 'workflow'
            ]
            
            technical_score = sum(1 for term in technical_terms if term.lower() in content.lower())
            
            # Structure indicators
            has_sections = bool(re.search(r'#+\s+|^\d+\.|^-\s+|^\*\s+', content, re.MULTILINE))
            has_code_blocks = bool(re.search(r'```|`[^`]+`', content))
            has_lists = bool(re.search(r'^\s*[-*+]\s+|^\s*\d+\.\s+', content, re.MULTILINE))
            
            # Calculate score
            length_score = min(40, word_count / 25)  # Up to 40 points for length
            technical_score = min(30, technical_score * 3)  # Up to 30 points for technical terms
            structure_score = (has_sections * 10) + (has_code_blocks * 10) + (has_lists * 10)  # Up to 30 points
            
            total_score = length_score + technical_score + structure_score
            return min(100, total_score)
            
        except Exception as e:
            logger.error(f"❌ CONTENT DEPTH CHECK ERROR: {str(e)}")
            return 0
    
    def _check_technical_accuracy(self, content: str, service: str) -> float:
        """Check technical accuracy and AWS best practices"""
        try:
            content_lower = content.lower()
            
            # AWS best practices terms
            best_practices = [
                'alta disponibilidad', 'fault tolerance', 'disaster recovery',
                'security', 'encryption', 'iam', 'vpc', 'monitoring',
                'logging', 'backup', 'scalability', 'cost optimization'
            ]
            
            best_practices_score = sum(2 for term in best_practices if term in content_lower)
            
            # Service-specific technical terms
            service_technical_terms = self._get_service_technical_terms(service)
            technical_accuracy = sum(1 for term in service_technical_terms if term.lower() in content_lower)
            
            # Avoid common mistakes
            mistake_penalties = 0
            common_mistakes = [
                'free tier forever', 'unlimited storage', 'zero cost',
                'no limits', 'infinite scalability', 'perfect security'
            ]
            
            for mistake in common_mistakes:
                if mistake in content_lower:
                    mistake_penalties += 10
            
            # Calculate score
            total_score = min(70, best_practices_score * 2) + min(30, technical_accuracy * 2) - mistake_penalties
            return max(0, min(100, total_score))
            
        except Exception as e:
            logger.error(f"❌ TECHNICAL ACCURACY CHECK ERROR: {str(e)}")
            return 0
    
    def _check_structure_quality(self, content: str, document_type: str) -> float:
        """Check document structure quality"""
        try:
            # Basic structure elements
            has_title = bool(re.search(r'^#\s+|^[A-Z][^.]*$', content, re.MULTILINE))
            has_sections = len(re.findall(r'^#+\s+', content, re.MULTILINE))
            has_paragraphs = len(content.split('\n\n'))
            
            # Document type specific requirements
            type_score = 0
            if document_type.lower() in ['propuesta ejecutiva', 'executive proposal']:
                # Should have executive summary, objectives, benefits
                executive_terms = ['resumen ejecutivo', 'objetivos', 'beneficios', 'roi']
                type_score = sum(10 for term in executive_terms if term.lower() in content.lower())
            
            elif document_type.lower() in ['documento técnico', 'technical document']:
                # Should have architecture, implementation details
                technical_terms = ['arquitectura', 'implementación', 'configuración', 'diagrama']
                type_score = sum(10 for term in technical_terms if term.lower() in content.lower())
            
            # Calculate score
            structure_score = (has_title * 20) + min(40, has_sections * 8) + min(20, has_paragraphs * 2)
            total_score = structure_score + min(20, type_score)
            
            return min(100, total_score)
            
        except Exception as e:
            logger.error(f"❌ STRUCTURE QUALITY CHECK ERROR: {str(e)}")
            return 0
    
    def _check_generic_content(self, content: str) -> float:
        """Check for generic/template content (higher score = less generic)"""
        try:
            content_lower = content.lower()
            
            # Count generic indicators
            generic_count = sum(1 for indicator in self.generic_indicators if indicator in content_lower)
            
            # Check for placeholder patterns
            placeholder_patterns = [
                r'\[.*?\]', r'\{.*?\}', r'<.*?>', r'xxx+', r'todo', r'tbd'
            ]
            
            placeholder_count = sum(len(re.findall(pattern, content_lower)) for pattern in placeholder_patterns)
            
            # Check for repetitive content
            sentences = re.split(r'[.!?]+', content)
            unique_sentences = len(set(sentence.strip().lower() for sentence in sentences if sentence.strip()))
            total_sentences = len([s for s in sentences if s.strip()])
            
            uniqueness_ratio = unique_sentences / max(1, total_sentences)
            
            # Calculate score (100 = not generic, 0 = very generic)
            generic_penalty = generic_count * 15 + placeholder_count * 10
            uniqueness_score = uniqueness_ratio * 50
            
            total_score = 100 - generic_penalty + uniqueness_score
            return max(0, min(100, total_score))
            
        except Exception as e:
            logger.error(f"❌ GENERIC CONTENT CHECK ERROR: {str(e)}")
            return 50  # Neutral score on error
    
    def _check_completeness(self, content: str, document_type: str) -> float:
        """Check document completeness"""
        try:
            word_count = len(content.split())
            
            # Minimum word count by document type
            min_words = {
                'propuesta ejecutiva': 300,
                'documento técnico': 400,
                'cloudformation': 50,
                'actividades csv': 100,
                'costos csv': 50,
                'guía calculadora': 200
            }
            
            expected_words = min_words.get(document_type.lower(), 200)
            completeness_ratio = min(1.0, word_count / expected_words)
            
            # Check for key sections based on document type
            section_score = 0
            if document_type.lower() in ['propuesta ejecutiva']:
                required_sections = ['objetivo', 'beneficio', 'implementación', 'costo']
                section_score = sum(20 for section in required_sections if section in content.lower())
            
            total_score = (completeness_ratio * 60) + min(40, section_score)
            return min(100, total_score)
            
        except Exception as e:
            logger.error(f"❌ COMPLETENESS CHECK ERROR: {str(e)}")
            return 0
    
    def _get_service_related_terms(self, service: str) -> List[str]:
        """Get related terms for a specific AWS service"""
        service_terms = {
            'LEX': ['chatbot', 'bot', 'conversational', 'nlp', 'intent', 'slot'],
            'LAMBDA': ['serverless', 'function', 'event-driven', 'trigger', 'runtime'],
            'API_GATEWAY': ['rest api', 'http api', 'endpoint', 'integration', 'stage'],
            'DYNAMODB': ['nosql', 'table', 'item', 'partition key', 'gsi'],
            'S3': ['bucket', 'object', 'storage', 'lifecycle', 'versioning'],
            'EC2': ['instance', 'ami', 'security group', 'key pair', 'ebs'],
            'RDS': ['database', 'mysql', 'postgresql', 'aurora', 'backup'],
            'CLOUDFRONT': ['cdn', 'distribution', 'edge location', 'cache'],
            'ROUTE53': ['dns', 'hosted zone', 'record', 'health check'],
            'COGNITO': ['user pool', 'identity pool', 'authentication', 'jwt']
        }
        
        return service_terms.get(service, [])
    
    def _get_service_technical_terms(self, service: str) -> List[str]:
        """Get technical terms specific to a service"""
        technical_terms = {
            'LEX': ['intent recognition', 'slot filling', 'fulfillment', 'context'],
            'LAMBDA': ['cold start', 'concurrency', 'layers', 'environment variables'],
            'API_GATEWAY': ['throttling', 'caching', 'cors', 'authorizer'],
            'DYNAMODB': ['read capacity', 'write capacity', 'eventual consistency', 'streams'],
            'S3': ['cross-region replication', 'transfer acceleration', 'multipart upload'],
            'EC2': ['auto scaling', 'load balancing', 'placement groups', 'spot instances'],
            'RDS': ['multi-az', 'read replica', 'parameter group', 'subnet group'],
            'CLOUDFRONT': ['origin', 'behavior', 'invalidation', 'signed urls'],
            'ROUTE53': ['alias record', 'weighted routing', 'geolocation', 'failover'],
            'COGNITO': ['federated identity', 'saml', 'oauth', 'mfa']
        }
        
        return technical_terms.get(service, [])
    
    def _generate_recommendations(self, scores: Dict[str, float], service: str, document_type: str) -> List[str]:
        """Generate improvement recommendations based on scores"""
        recommendations = []
        
        if scores.get('service_relevance', 0) < 70:
            recommendations.append(f"Incluir más referencias específicas a {service} y sus características únicas")
        
        if scores.get('content_depth', 0) < 60:
            recommendations.append("Agregar más detalles técnicos y ejemplos específicos de implementación")
        
        if scores.get('technical_accuracy', 0) < 70:
            recommendations.append("Incluir más mejores prácticas de AWS y consideraciones de seguridad")
        
        if scores.get('structure_quality', 0) < 60:
            recommendations.append("Mejorar la estructura del documento con secciones claras y títulos")
        
        if scores.get('generic_content', 0) < 70:
            recommendations.append("Reducir contenido genérico y agregar información más específica al caso de uso")
        
        if scores.get('completeness', 0) < 70:
            recommendations.append("Expandir el contenido para cubrir todos los aspectos importantes del tema")
        
        return recommendations

# Global validator instance
validator = DocumentValidator()

def validate_ai_response(content: str, service: str, document_type: str = "general") -> Dict[str, Any]:
    """
    Main function to validate AI-generated content
    """
    try:
        logger.info(f"🔍 VALIDATING AI RESPONSE FOR {service}")
        return validator.validate_document_quality(content, service, document_type)
    except Exception as e:
        logger.error(f"❌ VALIDATION FAILED: {str(e)}")
        return {
            'error': str(e),
            'overall_score': 0,
            'quality_level': 'error'
        }

def is_response_acceptable(validation_result: Dict[str, Any], min_score: float = 60.0) -> bool:
    """
    Check if response meets minimum quality standards
    """
    try:
        overall_score = validation_result.get('overall_score', 0)
        quality_level = validation_result.get('quality_level', 'poor')
        
        return overall_score >= min_score and quality_level != 'poor'
    except Exception as e:
        logger.error(f"❌ ACCEPTABILITY CHECK ERROR: {str(e)}")
        return False
