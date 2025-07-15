"""
MCP Server - Professional Document Generation
Generates Word documents, CSV files, and other professional documents
"""

import json
import boto3
import os
import uuid
from datetime import datetime
from typing import Dict, Any, List
import csv
from io import StringIO, BytesIO

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """Generate professional documents based on project information"""
    try:
        project_info = event.get('project_info', {})
        agent_response = event.get('agent_response', '')
        document_type = event.get('document_type', 'word')
        
        print(f"Generating document type: {document_type}")
        
        if document_type == 'word':
            return generate_word_document(project_info, agent_response)
        elif document_type == 'activities_csv':
            return generate_activities_csv(project_info, agent_response)
        else:
            return {'error': f'Unsupported document type: {document_type}'}
            
    except Exception as e:
        print(f"Error in document generator: {str(e)}")
        return {'error': str(e)}

def generate_word_document(project_info: Dict[str, Any], agent_response: str) -> Dict[str, Any]:
    """Generate professional Word document (as plain text)"""
    
    project_name = project_info.get('name', 'Proyecto AWS')
    solution_type = project_info.get('solution_type', 'integral')
    
    # Generate comprehensive Word document content
    word_content = f"""PROPUESTA EJECUTIVA - {project_name.upper()}

RESUMEN EJECUTIVO
================

Proyecto: {project_name}
Tipo de Solucion: {solution_type.title()}
Fecha: {datetime.now().strftime('%d/%m/%Y')}
Preparado por: Arquitecto AWS Certificado

OBJETIVO DEL PROYECTO
====================

{project_info.get('solution_type_detail', 'Implementacion de solucion AWS profesional')}

DESCRIPCION DETALLADA
====================

{_extract_project_description(project_info)}

ARQUITECTURA PROPUESTA
=====================

La solucion propuesta utiliza los siguientes servicios AWS:

{_generate_architecture_description(project_info, agent_response)}

BENEFICIOS DE LA SOLUCION
=========================

1. ESCALABILIDAD
   - Capacidad de crecimiento automatico segun demanda
   - Recursos elasticos que se ajustan a las necesidades

2. SEGURIDAD
   - Implementacion de mejores practicas de seguridad AWS
   - Cifrado en transito y en reposo
   - Control de acceso granular con IAM

3. DISPONIBILIDAD
   - Arquitectura multi-AZ para alta disponibilidad
   - Respaldos automaticos y recuperacion ante desastres

4. COSTO-EFECTIVIDAD
   - Modelo de pago por uso
   - Optimizacion automatica de recursos
   - Reduccion de costos operativos

IMPLEMENTACION
==============

FASE 1: PREPARACION (Semana 1-2)
- Configuracion de cuenta AWS
- Configuracion de redes y seguridad base
- Preparacion de entornos

FASE 2: DESPLIEGUE CORE (Semana 3-4)
- Implementacion de servicios principales
- Configuracion de monitoreo
- Pruebas iniciales

FASE 3: INTEGRACION (Semana 5-6)
- Integracion con sistemas existentes
- Configuracion de respaldos
- Pruebas de integracion

FASE 4: PRODUCCION (Semana 7-8)
- Despliegue a produccion
- Monitoreo y optimizacion
- Documentacion final y transferencia

ESTIMACION DE COSTOS
===================

{_generate_cost_summary(project_info)}

PROXIMOS PASOS
==============

1. Aprobacion de la propuesta
2. Configuracion de cuenta AWS
3. Inicio de implementacion segun cronograma
4. Reuniones de seguimiento semanales

CONTACTO
========

Para consultas sobre esta propuesta:
- Arquitecto AWS Certificado
- Email: arquitecto@empresa.com
- Telefono: +1-XXX-XXX-XXXX

---
Documento generado automaticamente por AWS Propuestas V3
{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
    
    return {
        'document_type': 'word',
        'filename': f"{project_name.replace(' ', '_')}_Propuesta_Ejecutiva.txt",
        'content': word_content,
        'size': len(word_content.encode('utf-8')),
        'generated_at': datetime.now().isoformat()
    }

def generate_activities_csv(project_info: Dict[str, Any], agent_response: str) -> Dict[str, Any]:
    """Generate implementation activities CSV"""
    
    project_name = project_info.get('name', 'Proyecto AWS')
    solution_type = project_info.get('solution_type', 'integral')
    
    # Generate activities based on solution type
    if solution_type == 'rapid_service':
        activities = _generate_rapid_service_activities(project_info)
    else:
        activities = _generate_integral_solution_activities(project_info)
    
    # Create CSV content
    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer)
    
    # Headers
    writer.writerow([
        'ID',
        'Actividad',
        'Descripcion',
        'Responsable',
        'Duracion (dias)',
        'Dependencias',
        'Fase',
        'Estado'
    ])
    
    # Write activities
    for i, activity in enumerate(activities, 1):
        writer.writerow([
            f"ACT-{i:03d}",
            activity['name'],
            activity['description'],
            activity['responsible'],
            activity['duration'],
            activity['dependencies'],
            activity['phase'],
            'Pendiente'
        ])
    
    csv_content = csv_buffer.getvalue()
    csv_buffer.close()
    
    return {
        'document_type': 'activities_csv',
        'filename': f"{project_name.replace(' ', '_')}_Actividades_Implementacion.csv",
        'content': csv_content,
        'size': len(csv_content.encode('utf-8')),
        'generated_at': datetime.now().isoformat()
    }

def _extract_project_description(project_info: Dict[str, Any]) -> str:
    """Extract and format project description from collected information"""
    description_parts = []
    
    # Add answers from interview
    for key, value in project_info.items():
        if key.startswith('answer_') and value:
            description_parts.append(f"- {value}")
    
    if project_info.get('selected_services'):
        services = ', '.join(project_info['selected_services'])
        description_parts.append(f"- Servicios requeridos: {services}")
    
    return '\n'.join(description_parts) if description_parts else "Proyecto de implementacion AWS profesional"

def _generate_architecture_description(project_info: Dict[str, Any], agent_response: str) -> str:
    """Generate architecture description based on project info"""
    
    # Extract services mentioned in the project
    services = project_info.get('selected_services', [])
    
    if not services:
        # Try to extract from agent response or use defaults
        services = ['EC2', 'VPC', 'S3', 'CloudWatch']
    
    architecture_desc = []
    
    for service in services:
        if service == 'EC2':
            architecture_desc.append("- Amazon EC2: Instancias virtuales para procesamiento")
        elif service == 'RDS':
            architecture_desc.append("- Amazon RDS: Base de datos relacional administrada")
        elif service == 'S3':
            architecture_desc.append("- Amazon S3: Almacenamiento de objetos escalable")
        elif service == 'VPC':
            architecture_desc.append("- Amazon VPC: Red privada virtual segura")
        elif service == 'ELB':
            architecture_desc.append("- Elastic Load Balancer: Distribucion de carga")
        elif service == 'CloudFront':
            architecture_desc.append("- Amazon CloudFront: Red de distribucion de contenido")
        else:
            architecture_desc.append(f"- {service}: Servicio AWS especializado")
    
    # Add standard components
    architecture_desc.extend([
        "- AWS IAM: Gestion de identidades y accesos",
        "- Amazon CloudWatch: Monitoreo y alertas",
        "- AWS CloudTrail: Auditoria y compliance"
    ])
    
    return '\n'.join(architecture_desc)

def _generate_cost_summary(project_info: Dict[str, Any]) -> str:
    """Generate cost summary based on project requirements"""
    
    solution_type = project_info.get('solution_type', 'integral')
    services = project_info.get('selected_services', [])
    
    if solution_type == 'rapid_service':
        base_cost = 50 * len(services) if services else 100
        return f"""
Estimacion mensual aproximada: ${base_cost}-${base_cost * 3} USD

Componentes principales:
- Servicios AWS seleccionados: ${base_cost * 0.7:.0f} USD
- Monitoreo y seguridad: ${base_cost * 0.2:.0f} USD
- Soporte y mantenimiento: ${base_cost * 0.1:.0f} USD

Nota: Los costos pueden variar segun uso real y configuracion final.
Se recomienda usar la calculadora oficial de AWS para estimaciones precisas.
"""
    else:
        base_cost = 500
        return f"""
Estimacion mensual aproximada: ${base_cost}-${base_cost * 5} USD

Componentes principales:
- Infraestructura base: ${base_cost * 0.4:.0f} USD
- Servicios aplicacion: ${base_cost * 0.3:.0f} USD
- Almacenamiento y datos: ${base_cost * 0.2:.0f} USD
- Monitoreo y seguridad: ${base_cost * 0.1:.0f} USD

Nota: Los costos pueden variar significativamente segun:
- Volumen de datos procesados
- Numero de usuarios concurrentes
- Nivel de alta disponibilidad requerido
- Integraciones adicionales necesarias

Se recomienda usar la calculadora oficial de AWS para estimaciones precisas.
"""

def _generate_rapid_service_activities(project_info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate activities for rapid service implementation"""
    
    services = project_info.get('selected_services', ['General'])
    
    activities = [
        {
            'name': 'Configuracion inicial de cuenta AWS',
            'description': 'Configurar cuenta, IAM, y permisos basicos',
            'responsible': 'Arquitecto AWS',
            'duration': 1,
            'dependencies': 'Ninguna',
            'phase': 'Preparacion'
        },
        {
            'name': 'Configuracion de red y seguridad',
            'description': 'Crear VPC, subnets, security groups',
            'responsible': 'Arquitecto AWS',
            'duration': 2,
            'dependencies': 'ACT-001',
            'phase': 'Preparacion'
        }
    ]
    
    # Add service-specific activities
    for service in services:
        if service == 'EC2':
            activities.extend([
                {
                    'name': 'Despliegue de instancias EC2',
                    'description': 'Crear y configurar instancias EC2 segun especificaciones',
                    'responsible': 'Ingeniero AWS',
                    'duration': 2,
                    'dependencies': 'ACT-002',
                    'phase': 'Implementacion'
                },
                {
                    'name': 'Configuracion de monitoreo EC2',
                    'description': 'Configurar CloudWatch para instancias',
                    'responsible': 'Ingeniero AWS',
                    'duration': 1,
                    'dependencies': f'ACT-{len(activities)+1:03d}',
                    'phase': 'Implementacion'
                }
            ])
        elif service == 'RDS':
            activities.extend([
                {
                    'name': 'Despliegue de base de datos RDS',
                    'description': 'Crear instancia RDS con configuracion optima',
                    'responsible': 'DBA/Ingeniero AWS',
                    'duration': 3,
                    'dependencies': 'ACT-002',
                    'phase': 'Implementacion'
                },
                {
                    'name': 'Configuracion de respaldos RDS',
                    'description': 'Configurar respaldos automaticos y snapshots',
                    'responsible': 'DBA/Ingeniero AWS',
                    'duration': 1,
                    'dependencies': f'ACT-{len(activities)+1:03d}',
                    'phase': 'Implementacion'
                }
            ])
    
    # Add final activities
    activities.extend([
        {
            'name': 'Pruebas de integracion',
            'description': 'Ejecutar pruebas completas del sistema',
            'responsible': 'Equipo QA',
            'duration': 2,
            'dependencies': 'Todas las implementaciones',
            'phase': 'Validacion'
        },
        {
            'name': 'Documentacion y transferencia',
            'description': 'Documentar configuracion y transferir conocimiento',
            'responsible': 'Arquitecto AWS',
            'duration': 2,
            'dependencies': f'ACT-{len(activities)+1:03d}',
            'phase': 'Cierre'
        }
    ])
    
    return activities

def _generate_integral_solution_activities(project_info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate activities for integral solution implementation"""
    
    return [
        {
            'name': 'Analisis de requerimientos detallado',
            'description': 'Analizar y documentar todos los requerimientos del proyecto',
            'responsible': 'Arquitecto de Soluciones',
            'duration': 5,
            'dependencies': 'Ninguna',
            'phase': 'Analisis'
        },
        {
            'name': 'Diseno de arquitectura detallada',
            'description': 'Crear diseno tecnico detallado de la solucion',
            'responsible': 'Arquitecto de Soluciones',
            'duration': 7,
            'dependencies': 'ACT-001',
            'phase': 'Diseno'
        },
        {
            'name': 'Configuracion de cuenta y organizacion AWS',
            'description': 'Configurar estructura organizacional en AWS',
            'responsible': 'Arquitecto AWS',
            'duration': 3,
            'dependencies': 'ACT-002',
            'phase': 'Preparacion'
        },
        {
            'name': 'Implementacion de red y seguridad base',
            'description': 'Implementar VPC, subnets, security groups, NACLs',
            'responsible': 'Ingeniero de Redes',
            'duration': 5,
            'dependencies': 'ACT-003',
            'phase': 'Infraestructura'
        },
        {
            'name': 'Despliegue de servicios principales',
            'description': 'Implementar servicios core de la aplicacion',
            'responsible': 'Equipo de Desarrollo',
            'duration': 10,
            'dependencies': 'ACT-004',
            'phase': 'Implementacion'
        },
        {
            'name': 'Configuracion de monitoreo y alertas',
            'description': 'Implementar CloudWatch, alertas y dashboards',
            'responsible': 'Ingeniero DevOps',
            'duration': 3,
            'dependencies': 'ACT-005',
            'phase': 'Implementacion'
        },
        {
            'name': 'Implementacion de respaldos y DR',
            'description': 'Configurar estrategia de respaldos y recuperacion',
            'responsible': 'Ingeniero AWS',
            'duration': 4,
            'dependencies': 'ACT-005',
            'phase': 'Implementacion'
        },
        {
            'name': 'Integracion con sistemas existentes',
            'description': 'Integrar con sistemas on-premises o terceros',
            'responsible': 'Ingeniero de Integracion',
            'duration': 7,
            'dependencies': 'ACT-005',
            'phase': 'Integracion'
        },
        {
            'name': 'Pruebas de sistema completas',
            'description': 'Ejecutar pruebas funcionales, rendimiento y seguridad',
            'responsible': 'Equipo QA',
            'duration': 5,
            'dependencies': 'ACT-008',
            'phase': 'Validacion'
        },
        {
            'name': 'Capacitacion y transferencia',
            'description': 'Capacitar equipo cliente y transferir conocimiento',
            'responsible': 'Arquitecto de Soluciones',
            'duration': 3,
            'dependencies': 'ACT-009',
            'phase': 'Cierre'
        },
        {
            'name': 'Go-live y soporte inicial',
            'description': 'Puesta en produccion y soporte post-implementacion',
            'responsible': 'Equipo Completo',
            'duration': 2,
            'dependencies': 'ACT-010',
            'phase': 'Produccion'
        }
    ]
