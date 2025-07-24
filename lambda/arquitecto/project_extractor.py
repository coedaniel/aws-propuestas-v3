"""
Extractor inteligente de datos del proyecto desde la conversación
"""

import re
import json
from typing import Dict, List, Any

def extract_project_data_from_conversation(messages: List[Dict]) -> Dict:
    """Extrae datos específicos del proyecto desde la conversación"""
    
    # Combinar todo el contenido de la conversación
    full_conversation = " ".join([msg.get("content", "") for msg in messages])
    full_conversation_lower = full_conversation.lower()
    
    project_data = {
        "name": "Proyecto AWS",
        "type": "solucion-integral",
        "description": "Proyecto AWS profesional",
        "services": [],
        "region": "us-east-1",
        "requirements": [],
        "architecture_type": "standard"
    }
    
    # 1. EXTRAER NOMBRE DEL PROYECTO
    name_patterns = [
        r"proyecto\s+(?:es\s+|se\s+llama\s+)?([^.!?\n]+)",
        r"nombre\s+(?:del\s+proyecto\s+)?(?:es\s+)?([^.!?\n]+)",
        r"sistema\s+(?:de\s+)?([^.!?\n]+)",
        r"aplicacion\s+(?:de\s+)?([^.!?\n]+)",
        r"plataforma\s+(?:de\s+)?([^.!?\n]+)"
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, full_conversation_lower)
        if match:
            project_name = match.group(1).strip()
            if len(project_name) > 3:  # Evitar nombres muy cortos
                project_data["name"] = project_name.title()
                break
    
    # 2. DETECTAR SERVICIOS AWS ESPECÍFICOS
    aws_services_map = {
        # Compute
        "ec2": ["EC2", "instancia", "servidor", "virtual machine", "vm"],
        "lambda": ["Lambda", "serverless", "funcion", "function"],
        "ecs": ["ECS", "container", "contenedor", "docker"],
        "fargate": ["Fargate", "fargate"],
        
        # Storage
        "s3": ["S3", "bucket", "almacenamiento", "storage", "archivos", "files"],
        "efs": ["EFS", "file system", "sistema de archivos"],
        "ebs": ["EBS", "volumen", "volume", "disco"],
        
        # Database
        "rds": ["RDS", "base de datos", "database", "mysql", "postgres", "sql server"],
        "dynamodb": ["DynamoDB", "dynamo", "nosql", "documento"],
        "redshift": ["Redshift", "data warehouse", "analitica"],
        "aurora": ["Aurora", "aurora"],
        
        # Networking
        "vpc": ["VPC", "red", "network", "networking"],
        "cloudfront": ["CloudFront", "cdn", "distribucion", "distribution"],
        "route53": ["Route53", "dns", "dominio", "domain"],
        "elb": ["ELB", "load balancer", "balanceador", "alb", "nlb"],
        "api-gateway": ["API Gateway", "api", "rest", "graphql"],
        
        # Security
        "iam": ["IAM", "permisos", "roles", "usuarios", "identidad"],
        "cognito": ["Cognito", "autenticacion", "authentication", "login"],
        "waf": ["WAF", "firewall", "seguridad web"],
        
        # Analytics
        "kinesis": ["Kinesis", "streaming", "tiempo real", "real time"],
        "glue": ["Glue", "etl", "transformacion"],
        "athena": ["Athena", "consultas", "queries", "sql"],
        
        # Monitoring
        "cloudwatch": ["CloudWatch", "monitoreo", "monitoring", "logs", "metricas"],
        "x-ray": ["X-Ray", "tracing", "trazabilidad"]
    }
    
    detected_services = []
    for service_key, keywords in aws_services_map.items():
        for keyword in keywords:
            if keyword.lower() in full_conversation_lower:
                service_name = service_key.upper().replace("-", " ")
                if service_name not in detected_services:
                    detected_services.append(service_name)
                break
    
    # Si no se detectan servicios específicos, usar servicios por defecto según el tipo
    if not detected_services:
        if "web" in full_conversation_lower or "website" in full_conversation_lower:
            detected_services = ["S3", "CloudFront", "Route53", "Certificate Manager"]
        elif "api" in full_conversation_lower:
            detected_services = ["API Gateway", "Lambda", "DynamoDB", "CloudWatch"]
        elif "base de datos" in full_conversation_lower or "database" in full_conversation_lower:
            detected_services = ["RDS", "VPC", "CloudWatch", "IAM"]
        else:
            detected_services = ["EC2", "VPC", "S3", "CloudWatch"]
    
    project_data["services"] = detected_services
    
    # 3. DETECTAR TIPO DE PROYECTO
    integral_keywords = ["migracion", "aplicacion nueva", "modernizacion", "analitica", "seguridad", "ia", "iot", "data lake", "networking", "drp", "vdi", "integracion", "sistema completo", "plataforma"]
    rapido_keywords = ["servicio rapido", "configuracion", "setup", "instalacion"]
    
    if any(keyword in full_conversation_lower for keyword in integral_keywords):
        project_data["type"] = "solucion-integral"
    elif any(keyword in full_conversation_lower for keyword in rapido_keywords):
        project_data["type"] = "servicio-rapido"
    
    # 4. DETECTAR ARQUITECTURA ESPECÍFICA
    if "serverless" in full_conversation_lower:
        project_data["architecture_type"] = "serverless"
        project_data["services"] = ["Lambda", "API Gateway", "DynamoDB", "S3", "CloudWatch"]
    elif "microservicios" in full_conversation_lower or "microservices" in full_conversation_lower:
        project_data["architecture_type"] = "microservices"
        project_data["services"] = ["ECS", "ALB", "RDS", "ElastiCache", "CloudWatch"]
    elif "cdn" in full_conversation_lower or "cloudfront" in full_conversation_lower:
        project_data["architecture_type"] = "cdn"
        project_data["services"] = ["S3", "CloudFront", "Route53", "Certificate Manager"]
    elif "data" in full_conversation_lower and ("lake" in full_conversation_lower or "warehouse" in full_conversation_lower):
        project_data["architecture_type"] = "data"
        project_data["services"] = ["S3", "Glue", "Athena", "Redshift", "Kinesis"]
    
    # 5. EXTRAER REQUISITOS ESPECÍFICOS
    requirements = []
    
    # Disponibilidad
    if "alta disponibilidad" in full_conversation_lower or "high availability" in full_conversation_lower:
        requirements.append("Alta disponibilidad multi-AZ")
    
    # Escalabilidad
    if "escalable" in full_conversation_lower or "scalable" in full_conversation_lower:
        requirements.append("Auto-scaling configurado")
    
    # Seguridad
    if "seguro" in full_conversation_lower or "security" in full_conversation_lower:
        requirements.append("Configuracion de seguridad avanzada")
    
    # Performance
    if "rapido" in full_conversation_lower or "performance" in full_conversation_lower:
        requirements.append("Optimizacion de performance")
    
    # Backup
    if "backup" in full_conversation_lower or "respaldo" in full_conversation_lower:
        requirements.append("Estrategia de backup automatizada")
    
    project_data["requirements"] = requirements
    
    # 6. DETECTAR REGIÓN
    region_patterns = {
        "us-east-1": ["virginia", "us-east-1", "norte de virginia"],
        "us-west-2": ["oregon", "us-west-2"],
        "eu-west-1": ["irlanda", "ireland", "eu-west-1", "europa"],
        "ap-southeast-1": ["singapur", "singapore", "ap-southeast-1", "asia"],
        "sa-east-1": ["brasil", "brazil", "sa-east-1", "sao paulo"]
    }
    
    for region, keywords in region_patterns.items():
        if any(keyword in full_conversation_lower for keyword in keywords):
            project_data["region"] = region
            break
    
    # 7. GENERAR DESCRIPCIÓN ESPECÍFICA
    if project_data["name"] != "Proyecto AWS":
        project_data["description"] = f"Implementacion de {project_data['name']} utilizando {', '.join(project_data['services'][:3])} en AWS"
    
    return project_data

def validate_project_data(project_data: Dict) -> Dict:
    """Valida y enriquece los datos del proyecto"""
    
    # Asegurar que hay al menos un servicio
    if not project_data.get("services"):
        project_data["services"] = ["EC2", "VPC", "S3"]
    
    # Asegurar que el nombre no esté vacío
    if not project_data.get("name") or project_data["name"] == "Proyecto AWS":
        project_data["name"] = f"Proyecto {project_data['services'][0]}"
    
    # Asegurar descripción
    if not project_data.get("description"):
        project_data["description"] = f"Implementacion de {project_data['name']} en AWS"
    
    # Limpiar nombre para S3 (sin acentos ni caracteres especiales)
    project_data["s3_folder_name"] = clean_name_for_s3(project_data["name"])
    
    return project_data

def clean_name_for_s3(name: str) -> str:
    """Limpia el nombre para usar como carpeta S3"""
    # Convertir a minúsculas
    clean_name = name.lower()
    
    # Reemplazar espacios y caracteres especiales
    clean_name = re.sub(r'[^a-z0-9\-]', '-', clean_name)
    
    # Remover guiones múltiples
    clean_name = re.sub(r'-+', '-', clean_name)
    
    # Remover guiones al inicio y final
    clean_name = clean_name.strip('-')
    
    return clean_name

# Función principal para usar en el Lambda
def extract_and_validate_project_data(messages: List[Dict]) -> Dict:
    """Función principal para extraer y validar datos del proyecto"""
    project_data = extract_project_data_from_conversation(messages)
    validated_data = validate_project_data(project_data)
    
    return validated_data
