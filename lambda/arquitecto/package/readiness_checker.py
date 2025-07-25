"""
Verificador de preparación para generación de documentos
"""

from typing import Dict, List, Any

def check_conversation_readiness(messages: List[Dict], project_data: Dict) -> Dict:
    """
    Verifica si la conversación está lista para generar documentos
    """
    # Extraer contenido de todos los mensajes
    full_conversation = " ".join([msg.get("content", "") for msg in messages])
    full_conversation_lower = full_conversation.lower()
    
    readiness = {
        "ready_for_generation": False,
        "readiness_score": 0.0,
        "missing_info": [],
        "project_type_determined": False,
        "requirements_gathered": False,
        "services_identified": False,
        "conversation_complete": False
    }
    
    # 1. Verificar nombre del proyecto
    if project_data.get("name") and project_data["name"] != "Proyecto AWS":
        readiness["readiness_score"] += 0.2
    else:
        readiness["missing_info"].append("Nombre del proyecto no definido")
    
    # 2. Verificar tipo de proyecto
    if "solucion integral" in full_conversation_lower or "servicio rapido" in full_conversation_lower:
        readiness["project_type_determined"] = True
        readiness["readiness_score"] += 0.2
    else:
        readiness["missing_info"].append("Tipo de proyecto no especificado (integral o rápido)")
    
    # 3. Verificar servicios AWS
    if project_data.get("services") and len(project_data["services"]) > 0:
        readiness["services_identified"] = True
        readiness["readiness_score"] += 0.2
    else:
        readiness["missing_info"].append("Servicios AWS no identificados")
    
    # 4. Verificar requerimientos mínimos
    if project_data.get("requirements") and len(project_data["requirements"]) > 0:
        readiness["requirements_gathered"] = True
        readiness["readiness_score"] += 0.2
    else:
        readiness["missing_info"].append("Requerimientos no recopilados")
    
    # 5. Verificar profundidad de conversación
    min_messages = 4  # Mínimo: nombre, tipo, detalles, confirmación
    if len(messages) >= min_messages:
        readiness["conversation_complete"] = True
        readiness["readiness_score"] += 0.2
    else:
        readiness["missing_info"].append(f"Conversación incompleta ({len(messages)}/{min_messages} mensajes)")
    
    # Determinar si está listo para generación
    readiness["ready_for_generation"] = readiness["readiness_score"] >= 0.8
    
    # Agregar mensaje específico según el estado
    if readiness["ready_for_generation"]:
        readiness["status_message"] = "✅ Listo para generar documentos"
    else:
        missing = ", ".join(readiness["missing_info"])
        readiness["status_message"] = f"⚠️ Falta información: {missing}"
    
    return readiness

def get_next_question(readiness: Dict) -> str:
    """
    Determina la siguiente pregunta basada en el estado de preparación
    """
    if not readiness["project_type_determined"]:
        return """¿El proyecto es una solucion integral (como migracion, aplicacion nueva, modernizacion, analitica, seguridad, IA, IoT, data lake, networking, DRP, VDI, integracion, etc.)?
¿O es un servicio rapido especifico (como EC2, RDS, SES, VPN, ELB, S3, VPC, CloudFront, SSO, backup, etc.)?"""
    
    elif not readiness["services_identified"]:
        return "¿Qué servicios AWS específicos necesitas para este proyecto?"
    
    elif not readiness["requirements_gathered"]:
        return """Por favor, cuéntame más sobre los requerimientos específicos:
- ¿Necesitas alta disponibilidad?
- ¿Cuál es el nivel de seguridad requerido?
- ¿Tienes requisitos de rendimiento específicos?
- ¿Hay integraciones con otros sistemas?"""
    
    else:
        return "¿Hay algún otro requerimiento o detalle importante que debamos considerar antes de generar la documentación?"
