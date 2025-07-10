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
    
    # Title
    title = doc.add_heading(f'Propuesta Ejecutiva - {project_info.get("name", "Proyecto AWS")}', 0)
    
    # Executive Summary
    doc.add_heading('Resumen Ejecutivo', level=1)
    doc.add_paragraph(
        f'Este documento presenta la propuesta tecnica y comercial para el proyecto '
        f'{project_info.get("name", "")}, una solucion integral en AWS que cumple con '
        f'los requerimientos especificados y las mejores practicas de la industria.'
    )
    
    # Project Objective
    doc.add_heading('Objetivo del Proyecto', level=1)
    objective = project_info.get('objective', 'Implementar una solucion robusta y escalable en AWS')
    doc.add_paragraph(objective)
    
    # Project Description
    doc.add_heading('Descripcion del Proyecto', level=1)
    description = project_info.get('description', 'Solucion empresarial basada en servicios AWS')
    doc.add_paragraph(description)
    
    # Key Features
    if project_info.get('features'):
        doc.add_heading('Caracteristicas Principales', level=1)
        for feature in project_info.get('features', []):
            p = doc.add_paragraph(feature, style='List Bullet')
    
    # AWS Services
    if project_info.get('aws_services'):
        doc.add_heading('Servicios AWS Utilizados', level=1)
        for service in project_info.get('aws_services', []):
            p = doc.add_paragraph(service, style='List Bullet')
    
    # Architecture Overview
    doc.add_heading('Vision General de la Arquitectura', level=1)
    doc.add_paragraph(
        'La solucion propuesta utiliza una arquitectura moderna y escalable que aprovecha '
        'los servicios nativos de AWS para garantizar alta disponibilidad, seguridad y '
        'rendimiento optimo.'
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
