"""
Word document generator for AWS proposals
"""
import io
from typing import Dict, Any
from docx import Document
from docx.shared import Inches

def generate_word_document(project_info: Dict[str, Any], document_type: str = "propuesta") -> bytes:
    """
    Generate a Word document for the project
    
    Args:
        project_info: Dictionary with project information
        document_type: Type of document (propuesta, tecnico, resumen)
    
    Returns:
        bytes: Word document content
    """
    doc = Document()
    
    # Get project details
    project_name = project_info.get('name', 'Proyecto AWS')
    project_type = project_info.get('type', 'general')
    service_type = project_info.get('service_type', 'general')
    description = project_info.get('description', f'Solución {service_type} en AWS')
    objective = project_info.get('objective', 'Implementar una solución robusta y escalable en AWS')
    
    # Title
    title = doc.add_heading(f'Propuesta Ejecutiva - {project_name}', 0)
    
    # Executive Summary
    doc.add_heading('Resumen Ejecutivo', level=1)
    doc.add_paragraph(
        f'Este documento presenta la propuesta técnica y comercial para el proyecto '
        f'"{project_name}", {description}. La solución propuesta cumple con '
        f'los requerimientos especificados y sigue las mejores prácticas de AWS.'
    )
    
    # Project Objective
    doc.add_heading('Objetivo del Proyecto', level=1)
    doc.add_paragraph(objective)
    
    # Project Description
    doc.add_heading('Descripción del Proyecto', level=1)
    doc.add_paragraph(description)
    
    # Project Type and Service Details
    doc.add_heading('Tipo de Proyecto', level=1)
    if project_type == 'servicio_rapido':
        doc.add_paragraph('Este es un proyecto de servicio rápido, enfocado en la implementación específica de servicios AWS.')
    elif project_type == 'solucion_integral':
        doc.add_paragraph('Este es un proyecto de solución integral que abarca múltiples servicios y componentes de AWS.')
    
    # Service-specific details
    if service_type == 'vpc':
        doc.add_heading('Configuración de VPC', level=1)
        doc.add_paragraph('La solución incluye la configuración de una Virtual Private Cloud (VPC) con las siguientes características:')
        
        vpc_details = doc.add_paragraph()
        vpc_details.add_run('• ').bold = True
        vpc_details.add_run('VPC principal con CIDR block configurable\n')
        vpc_details.add_run('• ').bold = True
        vpc_details.add_run('Subredes públicas y privadas en múltiples zonas de disponibilidad\n')
        vpc_details.add_run('• ').bold = True
        vpc_details.add_run('Internet Gateway para conectividad externa\n')
        vpc_details.add_run('• ').bold = True
        vpc_details.add_run('Tablas de rutas optimizadas\n')
        
        if project_info.get('architecture') == 'tres_capas':
            doc.add_paragraph('La arquitectura está diseñada para soportar un sistema de tres capas (presentación, lógica de negocio y datos).')
        
        # CIDR blocks if specified
        cidr_blocks = project_info.get('cidr_blocks')
        if cidr_blocks:
            doc.add_heading('Configuración de Red', level=2)
            doc.add_paragraph(f'VPC CIDR: {cidr_blocks.get("vpc", "10.0.0.0/16")}')
            if cidr_blocks.get('public_subnets'):
                doc.add_paragraph(f'Subredes Públicas: {", ".join(cidr_blocks["public_subnets"])}')
            if cidr_blocks.get('private_subnets'):
                doc.add_paragraph(f'Subredes Privadas: {", ".join(cidr_blocks["private_subnets"])}')
    
    elif service_type == 'ec2':
        doc.add_heading('Configuración de EC2', level=1)
        doc.add_paragraph('La solución incluye la configuración de instancias Amazon EC2 con las siguientes especificaciones:')
        
        ec2_details = doc.add_paragraph()
        instance_type = project_info.get('instance_type', 't2.micro')
        ec2_details.add_run('• ').bold = True
        ec2_details.add_run(f'Tipo de instancia: {instance_type}\n')
        ec2_details.add_run('• ').bold = True
        ec2_details.add_run('Sistema operativo optimizado\n')
        ec2_details.add_run('• ').bold = True
        ec2_details.add_run('Configuración de seguridad avanzada\n')
        ec2_details.add_run('• ').bold = True
        ec2_details.add_run('Monitoreo y alertas integradas\n')
        
        # Technical specs if available
        tech_specs = project_info.get('technical_specs', {})
        if tech_specs:
            doc.add_heading('Especificaciones Técnicas', level=2)
            for spec, value in tech_specs.items():
                doc.add_paragraph(f'{spec.title()}: {value}')
    
    elif service_type == 'rds':
        doc.add_heading('Configuración de RDS', level=1)
        doc.add_paragraph('La solución incluye una base de datos Amazon RDS con las siguientes características:')
        
        rds_details = doc.add_paragraph()
        rds_details.add_run('• ').bold = True
        rds_details.add_run('Base de datos relacional administrada\n')
        rds_details.add_run('• ').bold = True
        rds_details.add_run('Respaldos automáticos\n')
        rds_details.add_run('• ').bold = True
        rds_details.add_run('Alta disponibilidad con Multi-AZ\n')
        rds_details.add_run('• ').bold = True
        rds_details.add_run('Cifrado en reposo y en tránsito\n')
    
    # AWS Services
    aws_services = project_info.get('aws_services', [])
    if aws_services:
        doc.add_heading('Servicios AWS Utilizados', level=1)
        for service in aws_services:
            p = doc.add_paragraph(service, style='List Bullet')
    
    # Requirements
    requirements = project_info.get('requirements', [])
    if requirements:
        doc.add_heading('Requerimientos Cumplidos', level=1)
        for req in requirements:
            p = doc.add_paragraph(req, style='List Bullet')
    
    # Architecture Overview
    doc.add_heading('Visión General de la Arquitectura', level=1)
    if service_type == 'vpc':
        doc.add_paragraph(
            'La arquitectura de red propuesta utiliza las mejores prácticas de AWS para '
            'garantizar seguridad, escalabilidad y alta disponibilidad. La VPC está '
            'diseñada con subredes públicas y privadas distribuidas en múltiples zonas '
            'de disponibilidad para máxima resiliencia.'
        )
    elif service_type == 'ec2':
        doc.add_paragraph(
            'La arquitectura de cómputo propuesta utiliza instancias EC2 optimizadas '
            'para el caso de uso específico, con configuraciones de seguridad robustas '
            'y monitoreo continuo para garantizar el rendimiento óptimo.'
        )
    elif service_type == 'rds':
        doc.add_paragraph(
            'La arquitectura de base de datos propuesta utiliza Amazon RDS para '
            'proporcionar una solución de base de datos completamente administrada '
            'con alta disponibilidad, respaldos automáticos y seguridad avanzada.'
        )
    else:
        doc.add_paragraph(
            'La solución propuesta utiliza una arquitectura moderna y escalable que aprovecha '
            'los servicios nativos de AWS para garantizar alta disponibilidad, seguridad y '
            'rendimiento óptimo.'
        )
    
    # Implementation Timeline
    doc.add_heading('Cronograma de Implementación', level=1)
    doc.add_paragraph('La implementación se realizará en las siguientes fases:')
    
    timeline = doc.add_paragraph()
    timeline.add_run('Fase 1: ').bold = True
    timeline.add_run('Configuración inicial y preparación del entorno\n')
    timeline.add_run('Fase 2: ').bold = True
    timeline.add_run('Despliegue de la infraestructura principal\n')
    timeline.add_run('Fase 3: ').bold = True
    timeline.add_run('Configuración de seguridad y monitoreo\n')
    timeline.add_run('Fase 4: ').bold = True
    timeline.add_run('Pruebas y validación\n')
    timeline.add_run('Fase 5: ').bold = True
    timeline.add_run('Puesta en producción y documentación\n')
    
    # Next Steps
    doc.add_heading('Próximos Pasos', level=1)
    doc.add_paragraph(
        'Una vez aprobada esta propuesta, procederemos con la implementación '
        'siguiendo el cronograma establecido y manteniendo comunicación constante '
        'para asegurar el éxito del proyecto.'
    )
    
    # Save to bytes
    doc_io = io.BytesIO()
    doc.save(doc_io)
    doc_io.seek(0)
    
    return doc_io.getvalue()
    )
    
    # Implementation Timeline
    doc.add_heading('Cronograma de Implementacion', level=1)
    doc.add_paragraph(
        'El proyecto se ejecutara en fases bien definidas, con entregables claros '
        'y puntos de control para asegurar el exito de la implementacion.'
    )
    
    # Cost Estimation
    doc.add_heading('Estimacion de Costos', level=1)
    doc.add_paragraph(
        'Los costos estimados incluyen los servicios AWS necesarios para la solucion, '
        'calculados con base en el uso proyectado y las mejores practicas de optimizacion.'
    )
    
    # Next Steps
    doc.add_heading('Proximos Pasos', level=1)
    doc.add_paragraph('1. Revision y aprobacion de la propuesta')
    doc.add_paragraph('2. Definicion del cronograma detallado')
    doc.add_paragraph('3. Inicio de la fase de implementacion')
    doc.add_paragraph('4. Configuracion del entorno de desarrollo')
    doc.add_paragraph('5. Despliegue en ambiente de produccion')
    
    # Save to bytes
    doc_io = io.BytesIO()
    doc.save(doc_io)
    doc_io.seek(0)
    
    return doc_io.getvalue()

def generate_technical_document(project_info: Dict[str, Any]) -> bytes:
    """Generate detailed technical document"""
    doc = Document()
    
    # Title
    doc.add_heading(f'Documento Tecnico - {project_info.get("name", "Proyecto AWS")}', 0)
    
    # Technical Architecture
    doc.add_heading('Arquitectura Tecnica Detallada', level=1)
    doc.add_paragraph(
        'Esta seccion describe en detalle la arquitectura tecnica propuesta, '
        'incluyendo todos los componentes, servicios y configuraciones necesarias.'
    )
    
    # Security Considerations
    doc.add_heading('Consideraciones de Seguridad', level=1)
    doc.add_paragraph(
        'La solucion implementa las mejores practicas de seguridad de AWS, '
        'incluyendo cifrado en transito y en reposo, control de acceso granular '
        'y monitoreo continuo.'
    )
    
    # Scalability and Performance
    doc.add_heading('Escalabilidad y Rendimiento', level=1)
    doc.add_paragraph(
        'La arquitectura esta diseñada para escalar automaticamente segun la demanda, '
        'utilizando servicios nativos de AWS para garantizar rendimiento optimo.'
    )
    
    # Monitoring and Logging
    doc.add_heading('Monitoreo y Logging', level=1)
    doc.add_paragraph(
        'Se implementaran soluciones completas de monitoreo utilizando CloudWatch, '
        'X-Ray y otros servicios de observabilidad de AWS.'
    )
    
    # Save to bytes
    doc_io = io.BytesIO()
    doc.save(doc_io)
    doc_io.seek(0)
    
    return doc_io.getvalue()
