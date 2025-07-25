"""
Llamadas corregidas a MCPs con datos específicos del proyecto
"""

import json
import requests
import logging
from typing import Dict, List, Any

logger = logging.getLogger()

# URLs de los servicios MCP ECS
MCP_BASE_URL = "https://mcp.danielingram.shop"
MCP_SERVICES = {
    'core': f"{MCP_BASE_URL}",
    'pricing': f"{MCP_BASE_URL}/pricing", 
    'awsdocs': f"{MCP_BASE_URL}/awsdocs",
    'cfn': f"{MCP_BASE_URL}/cfn",
    'diagram': f"{MCP_BASE_URL}/diagram",
    'customdoc': f"{MCP_BASE_URL}/docgen"
}

def call_mcp_service_with_retry(service_name: str, action: str, data: Dict, retries: int = 2) -> Dict:
    """Llama a un servicio MCP con reintentos"""
    
    for attempt in range(retries + 1):
        try:
            url = MCP_SERVICES.get(service_name)
            if not url:
                return {"error": f"Unknown service: {service_name}"}
            
            # Construir URL completa
            if action == 'health':
                full_url = f"{url}/health"
            else:
                full_url = f"{url}/{action}"
            
            logger.info(f"Attempt {attempt + 1}: Calling MCP {service_name} at {full_url}")
            logger.info(f"Data sent: {json.dumps(data, indent=2)}")
            
            response = requests.post(full_url, json=data, timeout=45)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"MCP {service_name} response: {json.dumps(result, indent=2)}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Attempt {attempt + 1} failed for MCP {service_name}: {str(e)}")
            if attempt == retries:
                return {"error": f"MCP service error after {retries + 1} attempts: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error calling MCP {service_name}: {str(e)}")
            return {"error": f"Unexpected error: {str(e)}"}

def generate_architecture_diagram(project_data: Dict) -> Dict:
    """Genera diagrama de arquitectura específico del proyecto"""
    
    # Preparar datos específicos para el diagrama
    diagram_request = {
        "action": "generate_aws_diagram",
        "project_name": project_data.get("name", "Proyecto AWS"),
        "services": project_data.get("services", ["EC2", "VPC", "S3"]),
        "architecture_type": project_data.get("architecture_type", "standard"),
        "region": project_data.get("region", "us-east-1"),
        "description": project_data.get("description", "Arquitectura AWS"),
        "requirements": project_data.get("requirements", []),
        "diagram_format": "png",
        "use_aws_icons": True,
        "include_labels": True,
        "layout": "hierarchical"
    }
    
    logger.info(f"Generating diagram with specific data: {json.dumps(diagram_request, indent=2)}")
    
    result = call_mcp_service_with_retry("diagram", "generate", diagram_request)
    
    if "error" not in result:
        logger.info("✅ Diagram generated successfully with AWS icons")
    else:
        logger.error(f"❌ Diagram generation failed: {result.get('error')}")
    
    return result

def generate_cloudformation_template(project_data: Dict) -> Dict:
    """Genera template CloudFormation específico del proyecto"""
    
    cfn_request = {
        "action": "generate_cloudformation",
        "project_name": project_data.get("name", "Proyecto AWS"),
        "services": project_data.get("services", ["EC2", "VPC", "S3"]),
        "region": project_data.get("region", "us-east-1"),
        "architecture_type": project_data.get("architecture_type", "standard"),
        "requirements": project_data.get("requirements", []),
        "include_parameters": True,
        "include_outputs": True,
        "format": "yaml"
    }
    
    logger.info(f"Generating CloudFormation with specific data: {json.dumps(cfn_request, indent=2)}")
    
    result = call_mcp_service_with_retry("cfn", "generate", cfn_request)
    
    if "error" not in result:
        logger.info("✅ CloudFormation template generated successfully")
    else:
        logger.error(f"❌ CloudFormation generation failed: {result.get('error')}")
    
    return result

def generate_cost_estimation(project_data: Dict) -> Dict:
    """Genera estimación de costos específica del proyecto"""
    
    pricing_request = {
        "action": "estimate_costs",
        "project_name": project_data.get("name", "Proyecto AWS"),
        "services": project_data.get("services", ["EC2", "VPC", "S3"]),
        "region": project_data.get("region", "us-east-1"),
        "architecture_type": project_data.get("architecture_type", "standard"),
        "usage_pattern": "standard",
        "include_breakdown": True,
        "currency": "USD",
        "period": "monthly"
    }
    
    logger.info(f"Generating cost estimation with specific data: {json.dumps(pricing_request, indent=2)}")
    
    result = call_mcp_service_with_retry("pricing", "estimate", pricing_request)
    
    if "error" not in result:
        logger.info("✅ Cost estimation generated successfully")
    else:
        logger.error(f"❌ Cost estimation failed: {result.get('error')}")
    
    return result

def generate_custom_documents(project_data: Dict) -> Dict:
    """Genera documentos personalizados específicos del proyecto"""
    
    doc_request = {
        "action": "generate_documents",
        "project_name": project_data.get("name", "Proyecto AWS"),
        "project_type": project_data.get("type", "solucion-integral"),
        "services": project_data.get("services", ["EC2", "VPC", "S3"]),
        "description": project_data.get("description", "Proyecto AWS"),
        "requirements": project_data.get("requirements", []),
        "architecture_type": project_data.get("architecture_type", "standard"),
        "region": project_data.get("region", "us-east-1"),
        "documents_to_generate": [
            "executive_proposal",
            "technical_architecture", 
            "implementation_plan",
            "cost_analysis",
            "aws_calculator_guide"
        ],
        "format": "docx"
    }
    
    logger.info(f"Generating custom documents with specific data: {json.dumps(doc_request, indent=2)}")
    
    result = call_mcp_service_with_retry("customdoc", "generate", doc_request)
    
    if "error" not in result:
        logger.info("✅ Custom documents generated successfully")
    else:
        logger.error(f"❌ Custom documents generation failed: {result.get('error')}")
    
    return result

def get_aws_documentation(project_data: Dict) -> Dict:
    """Obtiene documentación específica de AWS para el proyecto"""
    
    # Obtener documentación para los servicios específicos del proyecto
    services_to_document = project_data.get("services", ["EC2"])[:3]  # Limitar a 3 servicios principales
    
    docs_request = {
        "action": "get_service_documentation",
        "services": services_to_document,
        "topics": [
            "getting_started",
            "best_practices", 
            "pricing",
            "security"
        ],
        "format": "markdown"
    }
    
    logger.info(f"Getting AWS documentation for services: {services_to_document}")
    
    result = call_mcp_service_with_retry("awsdocs", "search", docs_request)
    
    if "error" not in result:
        logger.info("✅ AWS documentation retrieved successfully")
    else:
        logger.error(f"❌ AWS documentation retrieval failed: {result.get('error')}")
    
    return result

def generate_all_documents_with_specific_data(project_data: Dict) -> Dict:
    """Genera todos los documentos con datos específicos del proyecto"""
    
    logger.info(f"🚀 Starting document generation for project: {project_data.get('name')}")
    logger.info(f"📋 Services: {project_data.get('services')}")
    logger.info(f"🏗️ Architecture: {project_data.get('architecture_type')}")
    
    generated_content = {}
    mcp_results = {}
    
    try:
        # 1. Generar diagrama de arquitectura con iconos AWS oficiales
        logger.info("1️⃣ Generating architecture diagram...")
        diagram_result = generate_architecture_diagram(project_data)
        mcp_results["diagram"] = diagram_result
        
        if "error" not in diagram_result:
            generated_content["diagram"] = diagram_result
        
        # 2. Generar CloudFormation template específico
        logger.info("2️⃣ Generating CloudFormation template...")
        cfn_result = generate_cloudformation_template(project_data)
        mcp_results["cloudformation"] = cfn_result
        
        if "error" not in cfn_result:
            generated_content["cloudformation"] = cfn_result
        
        # 3. Generar estimación de costos específica
        logger.info("3️⃣ Generating cost estimation...")
        pricing_result = generate_cost_estimation(project_data)
        mcp_results["pricing"] = pricing_result
        
        if "error" not in pricing_result:
            generated_content["pricing"] = pricing_result
        
        # 4. Generar documentos personalizados
        logger.info("4️⃣ Generating custom documents...")
        doc_result = generate_custom_documents(project_data)
        mcp_results["documents"] = doc_result
        
        if "error" not in doc_result:
            generated_content["documents"] = doc_result
        
        # 5. Obtener documentación AWS específica
        logger.info("5️⃣ Getting AWS documentation...")
        aws_docs_result = get_aws_documentation(project_data)
        mcp_results["aws_docs"] = aws_docs_result
        
        if "error" not in aws_docs_result:
            generated_content["aws_docs"] = aws_docs_result
        
        success_count = len(generated_content)
        total_count = 5
        
        logger.info(f"✅ Document generation completed: {success_count}/{total_count} successful")
        
        return {
            "success": success_count > 0,
            "generated_content": generated_content,
            "mcp_results": mcp_results,
            "files_generated": success_count,
            "total_attempted": total_count,
            "project_data_used": project_data
        }
        
    except Exception as e:
        logger.error(f"❌ Error in document generation: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "mcp_results": mcp_results,
            "project_data_used": project_data
        }
