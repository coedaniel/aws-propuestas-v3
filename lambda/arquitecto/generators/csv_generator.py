"""
CSV generator for AWS proposals
"""
import io
import csv
from typing import Dict, Any, List

def generate_activities_csv(project_info: Dict[str, Any]) -> bytes:
    """
    Generate implementation activities CSV
    
    Args:
        project_info: Dictionary with project information
    
    Returns:
        bytes: CSV content
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow([
        'Fase',
        'Actividad',
        'Descripcion',
        'Duracion (dias)',
        'Recursos',
        'Entregables',
        'Dependencias'
    ])
    
    # Project type specific activities
    project_type = project_info.get('type', 'integral')
    
    if 'migracion' in project_type.lower():
        activities = get_migration_activities()
    elif 'analitica' in project_type.lower() or 'data' in project_type.lower():
        activities = get_analytics_activities()
    elif 'iot' in project_type.lower():
        activities = get_iot_activities()
    elif 'seguridad' in project_type.lower():
        activities = get_security_activities()
    else:
        activities = get_general_activities()
    
    # Write activities
    for activity in activities:
        writer.writerow(activity)
    
    # Convert to bytes
    output.seek(0)
    return output.getvalue().encode('utf-8')

def generate_costs_csv(project_info: Dict[str, Any]) -> bytes:
    """
    Generate cost estimation CSV
    
    Args:
        project_info: Dictionary with project information
    
    Returns:
        bytes: CSV content
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow([
        'Servicio AWS',
        'Tipo de Recurso',
        'Cantidad',
        'Costo Mensual (USD)',
        'Costo Anual (USD)',
        'Notas'
    ])
    
    # Generate cost estimates based on project type
    project_type = project_info.get('type', 'integral')
    aws_services = project_info.get('aws_services', [])
    
    costs = generate_cost_estimates(project_type, aws_services)
    
    total_monthly = 0
    for cost_item in costs:
        writer.writerow(cost_item)
        if len(cost_item) > 3 and cost_item[3]:
            try:
                total_monthly += float(cost_item[3])
            except (ValueError, TypeError):
                pass
    
    # Add total row
    writer.writerow(['', '', '', '', '', ''])
    writer.writerow(['TOTAL ESTIMADO', '', '', f'{total_monthly:.2f}', f'{total_monthly * 12:.2f}', 'Estimacion base'])
    
    # Convert to bytes
    output.seek(0)
    return output.getvalue().encode('utf-8')

def get_general_activities() -> List[List[str]]:
    """Get general implementation activities"""
    return [
        ['Planificacion', 'Analisis de requerimientos', 'Revision detallada de requerimientos y definicion de alcance', '3', 'Arquitecto de Soluciones', 'Documento de requerimientos', 'Aprobacion del proyecto'],
        ['Planificacion', 'Diseño de arquitectura', 'Diseño detallado de la arquitectura AWS', '5', 'Arquitecto de Soluciones', 'Diagramas de arquitectura', 'Documento de requerimientos'],
        ['Planificacion', 'Estimacion de costos', 'Calculo detallado de costos AWS', '2', 'Arquitecto de Soluciones', 'Estimacion de costos', 'Diseño de arquitectura'],
        ['Implementacion', 'Configuracion de red', 'Creacion de VPC, subnets y componentes de red', '3', 'Ingeniero DevOps', 'Infraestructura de red', 'Diseño de arquitectura'],
        ['Implementacion', 'Despliegue de servicios', 'Implementacion de servicios AWS principales', '7', 'Ingeniero DevOps', 'Servicios configurados', 'Infraestructura de red'],
        ['Implementacion', 'Configuracion de seguridad', 'Implementacion de politicas de seguridad', '4', 'Especialista en Seguridad', 'Configuracion de seguridad', 'Servicios configurados'],
        ['Implementacion', 'Configuracion de monitoreo', 'Implementacion de CloudWatch y alertas', '2', 'Ingeniero DevOps', 'Sistema de monitoreo', 'Servicios configurados'],
        ['Pruebas', 'Pruebas funcionales', 'Validacion de funcionalidad de la solucion', '5', 'QA Engineer', 'Reporte de pruebas', 'Sistema de monitoreo'],
        ['Pruebas', 'Pruebas de rendimiento', 'Validacion de rendimiento y escalabilidad', '3', 'QA Engineer', 'Reporte de rendimiento', 'Pruebas funcionales'],
        ['Entrega', 'Documentacion', 'Creacion de documentacion tecnica y de usuario', '3', 'Technical Writer', 'Documentacion completa', 'Pruebas de rendimiento'],
        ['Entrega', 'Capacitacion', 'Capacitacion al equipo del cliente', '2', 'Arquitecto de Soluciones', 'Equipo capacitado', 'Documentacion completa'],
        ['Entrega', 'Go-live', 'Puesta en produccion de la solucion', '1', 'Todo el equipo', 'Sistema en produccion', 'Equipo capacitado']
    ]

def get_migration_activities() -> List[List[str]]:
    """Get migration specific activities"""
    return [
        ['Evaluacion', 'Assessment de infraestructura actual', 'Analisis detallado de la infraestructura existente', '5', 'Arquitecto de Soluciones', 'Reporte de assessment', 'Acceso a infraestructura'],
        ['Evaluacion', 'Analisis de dependencias', 'Mapeo de dependencias entre aplicaciones', '3', 'Arquitecto de Soluciones', 'Mapa de dependencias', 'Reporte de assessment'],
        ['Planificacion', 'Estrategia de migracion', 'Definicion de estrategia y fases de migracion', '4', 'Arquitecto de Soluciones', 'Plan de migracion', 'Mapa de dependencias'],
        ['Planificacion', 'Diseño de arquitectura objetivo', 'Diseño de la arquitectura en AWS', '6', 'Arquitecto de Soluciones', 'Arquitectura objetivo', 'Plan de migracion'],
        ['Preparacion', 'Configuracion de entorno AWS', 'Setup inicial de cuentas y servicios AWS', '3', 'Ingeniero DevOps', 'Entorno AWS configurado', 'Arquitectura objetivo'],
        ['Preparacion', 'Configuracion de conectividad', 'Setup de VPN/Direct Connect', '4', 'Ingeniero de Redes', 'Conectividad establecida', 'Entorno AWS configurado'],
        ['Migracion', 'Migracion de datos', 'Transferencia de datos a AWS', '10', 'Ingeniero de Datos', 'Datos migrados', 'Conectividad establecida'],
        ['Migracion', 'Migracion de aplicaciones', 'Despliegue de aplicaciones en AWS', '8', 'Ingeniero DevOps', 'Aplicaciones migradas', 'Datos migrados'],
        ['Validacion', 'Pruebas de integracion', 'Validacion de integracion completa', '5', 'QA Engineer', 'Pruebas completadas', 'Aplicaciones migradas'],
        ['Validacion', 'Pruebas de rendimiento', 'Validacion de rendimiento en AWS', '3', 'QA Engineer', 'Rendimiento validado', 'Pruebas completadas'],
        ['Cutover', 'Switchover a produccion', 'Cambio definitivo a AWS', '2', 'Todo el equipo', 'Sistema en produccion', 'Rendimiento validado'],
        ['Post-migracion', 'Optimizacion', 'Optimizacion de costos y rendimiento', '4', 'Arquitecto de Soluciones', 'Sistema optimizado', 'Sistema en produccion']
    ]

def get_analytics_activities() -> List[List[str]]:
    """Get analytics specific activities"""
    return [
        ['Planificacion', 'Analisis de fuentes de datos', 'Identificacion y analisis de fuentes de datos', '4', 'Data Architect', 'Inventario de datos', 'Aprobacion del proyecto'],
        ['Planificacion', 'Diseño de data lake', 'Diseño de arquitectura de data lake en S3', '5', 'Data Architect', 'Arquitectura de data lake', 'Inventario de datos'],
        ['Planificacion', 'Diseño de pipelines ETL', 'Diseño de procesos de extraccion y transformacion', '4', 'Data Engineer', 'Diseño de ETL', 'Arquitectura de data lake'],
        ['Implementacion', 'Configuracion de S3', 'Setup de buckets y politicas de S3', '2', 'Data Engineer', 'S3 configurado', 'Diseño de ETL'],
        ['Implementacion', 'Implementacion de Glue', 'Configuracion de AWS Glue para ETL', '6', 'Data Engineer', 'Glue configurado', 'S3 configurado'],
        ['Implementacion', 'Configuracion de Redshift', 'Setup de cluster Redshift', '3', 'Data Engineer', 'Redshift configurado', 'Glue configurado'],
        ['Implementacion', 'Implementacion de QuickSight', 'Configuracion de dashboards', '4', 'BI Developer', 'Dashboards creados', 'Redshift configurado'],
        ['Integracion', 'Ingesta de datos', 'Configuracion de ingesta automatica', '5', 'Data Engineer', 'Ingesta configurada', 'Dashboards creados'],
        ['Validacion', 'Pruebas de calidad de datos', 'Validacion de calidad y consistencia', '4', 'Data Analyst', 'Datos validados', 'Ingesta configurada'],
        ['Validacion', 'Pruebas de dashboards', 'Validacion de reportes y visualizaciones', '3', 'BI Developer', 'Dashboards validados', 'Datos validados'],
        ['Entrega', 'Capacitacion en BI', 'Entrenamiento en uso de dashboards', '2', 'BI Developer', 'Usuarios capacitados', 'Dashboards validados'],
        ['Entrega', 'Go-live analytics', 'Puesta en produccion del sistema', '1', 'Todo el equipo', 'Sistema analitico activo', 'Usuarios capacitados']
    ]

def get_iot_activities() -> List[List[str]]:
    """Get IoT specific activities"""
    return [
        ['Planificacion', 'Analisis de dispositivos IoT', 'Inventario y analisis de dispositivos', '3', 'IoT Architect', 'Inventario de dispositivos', 'Aprobacion del proyecto'],
        ['Planificacion', 'Diseño de arquitectura IoT', 'Diseño de solucion IoT en AWS', '5', 'IoT Architect', 'Arquitectura IoT', 'Inventario de dispositivos'],
        ['Planificacion', 'Estrategia de conectividad', 'Definicion de protocolos y conectividad', '3', 'IoT Engineer', 'Plan de conectividad', 'Arquitectura IoT'],
        ['Implementacion', 'Configuracion de IoT Core', 'Setup de AWS IoT Core', '4', 'IoT Engineer', 'IoT Core configurado', 'Plan de conectividad'],
        ['Implementacion', 'Configuracion de certificados', 'Gestion de certificados y seguridad', '3', 'Security Engineer', 'Certificados configurados', 'IoT Core configurado'],
        ['Implementacion', 'Desarrollo de reglas IoT', 'Creacion de reglas de procesamiento', '5', 'IoT Developer', 'Reglas implementadas', 'Certificados configurados'],
        ['Implementacion', 'Integracion con Lambda', 'Conexion con funciones Lambda', '4', 'Backend Developer', 'Lambda integrado', 'Reglas implementadas'],
        ['Implementacion', 'Configuracion de almacenamiento', 'Setup de DynamoDB/S3 para datos IoT', '3', 'Data Engineer', 'Almacenamiento configurado', 'Lambda integrado'],
        ['Pruebas', 'Pruebas de conectividad', 'Validacion de conexion de dispositivos', '4', 'IoT Engineer', 'Conectividad validada', 'Almacenamiento configurado'],
        ['Pruebas', 'Pruebas de escalabilidad', 'Validacion con multiples dispositivos', '5', 'QA Engineer', 'Escalabilidad validada', 'Conectividad validada'],
        ['Despliegue', 'Despliegue de dispositivos', 'Instalacion y configuracion en campo', '7', 'Field Engineer', 'Dispositivos desplegados', 'Escalabilidad validada'],
        ['Monitoreo', 'Configuracion de monitoreo', 'Setup de alertas y dashboards', '3', 'DevOps Engineer', 'Monitoreo activo', 'Dispositivos desplegados']
    ]

def get_security_activities() -> List[List[str]]:
    """Get security specific activities"""
    return [
        ['Assessment', 'Auditoria de seguridad actual', 'Evaluacion del estado actual de seguridad', '5', 'Security Architect', 'Reporte de auditoria', 'Aprobacion del proyecto'],
        ['Planificacion', 'Diseño de arquitectura segura', 'Diseño de solucion con controles de seguridad', '6', 'Security Architect', 'Arquitectura segura', 'Reporte de auditoria'],
        ['Planificacion', 'Definicion de politicas', 'Creacion de politicas de seguridad', '4', 'Security Engineer', 'Politicas definidas', 'Arquitectura segura'],
        ['Implementacion', 'Configuracion de IAM', 'Setup de roles y politicas IAM', '5', 'Security Engineer', 'IAM configurado', 'Politicas definidas'],
        ['Implementacion', 'Configuracion de VPC Security', 'Setup de Security Groups y NACLs', '4', 'Network Security Engineer', 'VPC Security configurado', 'IAM configurado'],
        ['Implementacion', 'Implementacion de WAF', 'Configuracion de Web Application Firewall', '3', 'Security Engineer', 'WAF configurado', 'VPC Security configurado'],
        ['Implementacion', 'Configuracion de GuardDuty', 'Setup de deteccion de amenazas', '2', 'Security Engineer', 'GuardDuty activo', 'WAF configurado'],
        ['Implementacion', 'Configuracion de CloudTrail', 'Setup de auditoria y logging', '3', 'Security Engineer', 'CloudTrail configurado', 'GuardDuty activo'],
        ['Implementacion', 'Configuracion de Config', 'Setup de compliance y configuracion', '4', 'Compliance Engineer', 'Config configurado', 'CloudTrail configurado'],
        ['Validacion', 'Pruebas de penetracion', 'Testing de seguridad de la solucion', '6', 'Penetration Tester', 'Pentest completado', 'Config configurado'],
        ['Validacion', 'Auditoria de compliance', 'Validacion de cumplimiento normativo', '4', 'Compliance Engineer', 'Compliance validado', 'Pentest completado'],
        ['Entrega', 'Documentacion de seguridad', 'Creacion de runbooks de seguridad', '3', 'Security Engineer', 'Documentacion completa', 'Compliance validado']
    ]

def generate_cost_estimates(project_type: str, aws_services: List[str]) -> List[List[str]]:
    """Generate cost estimates based on project type and services"""
    costs = []
    
    # Base infrastructure costs
    costs.extend([
        ['EC2', 't3.medium instances', '2', '60.00', '720.00', 'Instancias para aplicacion'],
        ['VPC', 'NAT Gateway', '1', '45.00', '540.00', 'Conectividad saliente'],
        ['ELB', 'Application Load Balancer', '1', '22.00', '264.00', 'Balanceador de carga'],
        ['Route 53', 'Hosted Zone', '1', '0.50', '6.00', 'DNS management']
    ])
    
    # Add specific services based on project type
    if 'migracion' in project_type.lower():
        costs.extend([
            ['DMS', 'Database Migration Service', '1', '150.00', '1800.00', 'Migracion de base de datos'],
            ['DataSync', 'Data transfer service', '1', '100.00', '1200.00', 'Sincronizacion de datos'],
            ['Storage Gateway', 'Hybrid cloud storage', '1', '80.00', '960.00', 'Almacenamiento hibrido']
        ])
    
    if 'analitica' in project_type.lower() or 'data' in project_type.lower():
        costs.extend([
            ['S3', 'Data Lake storage', '1TB', '25.00', '300.00', 'Almacenamiento de datos'],
            ['Glue', 'ETL processing', '100 DPU-hours', '44.00', '528.00', 'Procesamiento ETL'],
            ['Redshift', 'dc2.large cluster', '2 nodes', '360.00', '4320.00', 'Data warehouse'],
            ['QuickSight', 'BI dashboards', '10 users', '180.00', '2160.00', 'Visualizacion de datos']
        ])
    
    if 'iot' in project_type.lower():
        costs.extend([
            ['IoT Core', 'Device connectivity', '1000 devices', '80.00', '960.00', 'Conectividad IoT'],
            ['IoT Analytics', 'Data processing', '1GB/month', '20.00', '240.00', 'Procesamiento de datos IoT'],
            ['DynamoDB', 'IoT data storage', '25GB', '6.25', '75.00', 'Almacenamiento de datos'],
            ['Lambda', 'IoT data processing', '1M invocations', '20.00', '240.00', 'Procesamiento serverless']
        ])
    
    if 'seguridad' in project_type.lower():
        costs.extend([
            ['GuardDuty', 'Threat detection', '1 account', '30.00', '360.00', 'Deteccion de amenazas'],
            ['WAF', 'Web Application Firewall', '1 web ACL', '60.00', '720.00', 'Proteccion web'],
            ['Config', 'Compliance monitoring', '1000 items', '20.00', '240.00', 'Monitoreo de compliance'],
            ['CloudTrail', 'Audit logging', '1 trail', '2.00', '24.00', 'Auditoria de eventos']
        ])
    
    # Add common monitoring and backup services
    costs.extend([
        ['CloudWatch', 'Monitoring and alerting', '1', '30.00', '360.00', 'Monitoreo de aplicacion'],
        ['Backup', 'Automated backups', '100GB', '5.00', '60.00', 'Respaldos automaticos'],
        ['KMS', 'Key management', '10 keys', '10.00', '120.00', 'Gestion de llaves de cifrado']
    ])
    
    return costs
