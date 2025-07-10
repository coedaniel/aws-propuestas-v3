"""
Helper functions for dynamic document generation
"""
import csv
import io
from typing import Dict, Any, List
from datetime import datetime

# Import the centralized service extraction function
from .dynamic_generator import extract_services_from_analysis

def generate_simple_costs_csv(project_info: Dict[str, Any], ai_analysis: str) -> bytes:
    """Generate a simple costs CSV based on AI analysis"""
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Servicio', 'Tipo_Recurso', 'Cantidad', 'Costo_Mensual_USD', 'Descripcion'])
    
    # Extract services and generate cost estimates
    services = extract_services_from_analysis(ai_analysis)
    
    for service in services:
        if 'EC2' in service:
            writer.writerow(['Amazon EC2', 'Instancia t3.micro', '1', '8.50', 'Instancia de computo basica'])
            writer.writerow(['Amazon EC2', 'EBS Storage', '20 GB', '2.00', 'Almacenamiento de disco'])
        elif 'S3' in service:
            writer.writerow(['Amazon S3', 'Standard Storage', '100 GB', '2.30', 'Almacenamiento de objetos'])
            writer.writerow(['Amazon S3', 'Requests', '10,000', '0.40', 'Solicitudes GET/PUT'])
        elif 'GuardDuty' in service:
            writer.writerow(['Amazon GuardDuty', 'Threat Detection', '1 account', '4.50', 'Deteccion de amenazas por cuenta'])
            writer.writerow(['Amazon GuardDuty', 'VPC Flow Logs', '1 GB', '1.00', 'Analisis de logs de VPC'])
            writer.writerow(['Amazon GuardDuty', 'DNS Logs', '1 million queries', '0.40', 'Analisis de consultas DNS'])
        elif 'EFS' in service:
            writer.writerow(['Amazon EFS', 'Standard Storage', '100 GB', '30.00', 'Sistema de archivos elastico'])
            writer.writerow(['Amazon EFS', 'Throughput', 'Provisioned', '6.00', 'Throughput provisionado'])
        elif 'RDS' in service:
            writer.writerow(['Amazon RDS', 'db.t3.micro', '1', '15.00', 'Base de datos MySQL'])
            writer.writerow(['Amazon RDS', 'Storage', '20 GB', '2.30', 'Almacenamiento SSD'])
        elif 'Lambda' in service:
            writer.writerow(['AWS Lambda', 'Requests', '1,000,000', '0.20', 'Invocaciones de funciones'])
            writer.writerow(['AWS Lambda', 'Duration', '100 GB-seconds', '1.67', 'Tiempo de ejecucion'])
        elif 'Inspector' in service:
            writer.writerow(['Amazon Inspector', 'EC2 Assessment', '1 instance', '1.30', 'Evaluacion de seguridad EC2'])
            writer.writerow(['Amazon Inspector', 'Container Assessment', '1 image', '0.09', 'Evaluacion de contenedores'])
        elif 'Config' in service:
            writer.writerow(['AWS Config', 'Configuration Items', '1,000', '0.003', 'Items de configuracion'])
            writer.writerow(['AWS Config', 'Rules Evaluations', '1,000', '0.001', 'Evaluaciones de reglas'])
        elif 'CloudTrail' in service:
            writer.writerow(['AWS CloudTrail', 'Management Events', 'First copy', '0.00', 'Eventos de gestion gratuitos'])
            writer.writerow(['AWS CloudTrail', 'Data Events', '100,000', '0.10', 'Eventos de datos'])
        elif 'WAF' in service:
            writer.writerow(['AWS WAF', 'Web ACL', '1', '1.00', 'Lista de control de acceso web'])
            writer.writerow(['AWS WAF', 'Rules', '10', '1.00', 'Reglas de firewall'])
        elif 'Shield' in service:
            writer.writerow(['AWS Shield', 'Standard', '1', '0.00', 'Proteccion DDoS basica'])
            writer.writerow(['AWS Shield', 'Advanced', '1', '3000.00', 'Proteccion DDoS avanzada'])
        elif 'Secrets Manager' in service:
            writer.writerow(['AWS Secrets Manager', 'Secrets', '1', '0.40', 'Gestion de secretos'])
            writer.writerow(['AWS Secrets Manager', 'API Calls', '10,000', '0.05', 'Llamadas a la API'])
        elif 'KMS' in service:
            writer.writerow(['AWS KMS', 'Customer Managed Keys', '1', '1.00', 'Claves administradas por cliente'])
            writer.writerow(['AWS KMS', 'API Requests', '20,000', '0.03', 'Solicitudes de API'])
        elif 'Certificate Manager' in service:
            writer.writerow(['AWS Certificate Manager', 'Public Certificates', '1', '0.00', 'Certificados publicos gratuitos'])
            writer.writerow(['AWS Certificate Manager', 'Private Certificates', '1', '0.75', 'Certificados privados'])
    
    # Add base costs
    writer.writerow(['AWS Support', 'Basic', '1', '0.00', 'Soporte basico incluido'])
    writer.writerow(['Data Transfer', 'Internet', '10 GB', '0.90', 'Transferencia de datos'])
    
    # Convert to bytes
    csv_content = output.getvalue()
    output.close()
    
    return csv_content.encode('utf-8')

def generate_simple_svg_diagram(project_info: Dict[str, Any], ai_analysis: str) -> str:
    """Generate a simple SVG architecture diagram"""
    
    services = extract_services_from_analysis(ai_analysis)
    project_name = project_info.get('name', 'AWS Project')
    
    # Basic SVG structure
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .title {{ font-family: Arial, sans-serif; font-size: 24px; font-weight: bold; }}
      .service {{ font-family: Arial, sans-serif; font-size: 14px; }}
      .aws-orange {{ fill: #FF9900; }}
      .aws-blue {{ fill: #232F3E; }}
      .service-box {{ fill: #E8F4FD; stroke: #1976D2; stroke-width: 2; }}
    </style>
  </defs>
  
  <!-- Background -->
  <rect width="800" height="600" fill="#F5F5F5"/>
  
  <!-- Title -->
  <text x="400" y="40" text-anchor="middle" class="title aws-blue">
    Arquitectura: {project_name}
  </text>
  
  <!-- AWS Cloud boundary -->
  <rect x="50" y="80" width="700" height="480" fill="none" stroke="#FF9900" stroke-width="3" stroke-dasharray="10,5"/>
  <text x="70" y="100" class="service aws-orange">AWS Cloud</text>
'''
    
    # Add services dynamically
    y_pos = 150
    x_pos = 100
    
    for i, service in enumerate(services[:6]):  # Limit to 6 services for layout
        if i % 2 == 0 and i > 0:
            y_pos += 120
            x_pos = 100
        elif i % 2 == 1:
            x_pos = 450
            
        svg_content += f'''
  <!-- {service} -->
  <rect x="{x_pos}" y="{y_pos}" width="200" height="80" class="service-box"/>
  <text x="{x_pos + 100}" y="{y_pos + 45}" text-anchor="middle" class="service aws-blue">
    {service}
  </text>
'''
    
    # Add connections
    if len(services) > 1:
        svg_content += '''
  <!-- Connections -->
  <line x1="200" y1="190" x2="450" y2="190" stroke="#1976D2" stroke-width="2"/>
'''
    
    svg_content += '''
  <!-- Footer -->
  <text x="400" y="580" text-anchor="middle" class="service" fill="#666">
    Generado dinámicamente basado en análisis de IA
  </text>
</svg>'''
    
    return svg_content

def generate_simple_drawio_diagram(project_info: Dict[str, Any], ai_analysis: str) -> str:
    """Generate a simple Draw.io XML diagram"""
    
    services = extract_services_from_analysis(ai_analysis)
    project_name = project_info.get('name', 'AWS Project')
    
    drawio_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="2025-07-10T21:00:00.000Z" agent="Dynamic Generator" etag="generated" version="21.0.0">
  <diagram name="Architecture" id="architecture">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        
        <!-- Title -->
        <mxCell id="title" value="{project_name}" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=20;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="300" y="20" width="200" height="30" as="geometry" />
        </mxCell>
        
        <!-- AWS Cloud -->
        <mxCell id="aws-cloud" value="AWS Cloud" style="sketch=0;outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=0;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_aws_cloud;strokeColor=#FF9900;fillColor=none;verticalAlign=top;align=left;spacingLeft=30;fontColor=#FF9900;dashed=0;" vertex="1" parent="1">
          <mxGeometry x="50" y="80" width="700" height="400" as="geometry" />
        </mxCell>
'''
    
    # Add services
    y_pos = 150
    x_pos = 100
    
    for i, service in enumerate(services[:4]):  # Limit for layout
        if i % 2 == 0 and i > 0:
            y_pos += 120
            x_pos = 100
        elif i % 2 == 1:
            x_pos = 450
            
        service_id = f"service-{i}"
        drawio_content += f'''
        <!-- {service} -->
        <mxCell id="{service_id}" value="{service}" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;fillColor=#E8F4FD;strokeColor=#1976D2;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;pointerEvents=1;" vertex="1" parent="1">
          <mxGeometry x="{x_pos}" y="{y_pos}" width="120" height="60" as="geometry" />
        </mxCell>
'''
    
    drawio_content += '''
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''
    
    return drawio_content

def generate_dynamic_calculator_guide(project_info: Dict[str, Any], ai_analysis: str) -> str:
    """Generate AWS Calculator guide based on AI analysis"""
    
    services = extract_services_from_analysis(ai_analysis)
    project_name = project_info.get('name', 'AWS Project')
    
    guide = f"""GUÍA PARA CALCULADORA AWS - {project_name.upper()}
{'=' * 60}

Esta guía te ayudará a estimar los costos de tu proyecto usando la Calculadora AWS.

URL: https://calculator.aws

SERVICIOS IDENTIFICADOS:
{'-' * 25}
"""
    
    for service in services:
        guide += f"• {service}\n"
    
    guide += f"""

PASOS PARA USAR LA CALCULADORA:
{'-' * 35}

1. Accede a https://calculator.aws
2. Haz clic en "Create estimate"
3. Selecciona la región: us-east-1 (recomendado)

"""
    
    # Add service-specific guidance
    for service in services:
        if 'EC2' in service:
            guide += """
CONFIGURACIÓN AMAZON EC2:
• Busca "EC2" en la calculadora
• Selecciona "Amazon EC2"
• Configuración recomendada:
  - Instance type: t3.micro (para pruebas) o t3.small (producción)
  - Operating system: Linux
  - Tenancy: Shared
  - Storage: 20 GB EBS General Purpose SSD (gp3)
"""
        elif 'S3' in service:
            guide += """
CONFIGURACIÓN AMAZON S3:
• Busca "S3" en la calculadora
• Selecciona "Amazon S3"
• Configuración recomendada:
  - Storage class: S3 Standard
  - Storage amount: Estima según tus necesidades
  - Requests: GET (10,000/mes), PUT (1,000/mes)
"""
        elif 'GuardDuty' in service:
            guide += """
CONFIGURACIÓN AMAZON GUARDDUTY:
• Busca "GuardDuty" en la calculadora
• Selecciona "Amazon GuardDuty"
• Configuración recomendada:
  - Threat Detection: Habilitado por cuenta
  - VPC Flow Logs analysis: Estima GB procesados por mes
  - DNS Logs analysis: Estima millones de consultas por mes
  - S3 Protection: Si tienes buckets S3 críticos
  - EKS Protection: Si usas Kubernetes
"""
        elif 'Inspector' in service:
            guide += """
CONFIGURACIÓN AMAZON INSPECTOR:
• Busca "Inspector" en la calculadora
• Selecciona "Amazon Inspector"
• Configuración recomendada:
  - EC2 instance assessments: Número de instancias
  - Container image assessments: Número de imágenes
  - Lambda function assessments: Número de funciones
"""
        elif 'Config' in service:
            guide += """
CONFIGURACIÓN AWS CONFIG:
• Busca "Config" en la calculadora
• Selecciona "AWS Config"
• Configuración recomendada:
  - Configuration items: Estima recursos monitoreados
  - Config rules evaluations: Número de evaluaciones
  - Conformance packs: Si usas paquetes de conformidad
"""
        elif 'CloudTrail' in service:
            guide += """
CONFIGURACIÓN AWS CLOUDTRAIL:
• Busca "CloudTrail" en la calculadora
• Selecciona "AWS CloudTrail"
• Configuración recomendada:
  - Management events: Primera copia gratuita
  - Data events: Estima eventos de S3/Lambda por mes
  - Insights events: Si necesitas análisis de patrones
"""
        elif 'EFS' in service:
            guide += """
CONFIGURACIÓN AMAZON EFS:
• Busca "EFS" en la calculadora
• Selecciona "Amazon Elastic File System (EFS)"
• Configuración recomendada:
  - Storage class: Standard
  - Average storage: Estima según tus archivos
  - Throughput mode: Provisioned (si necesitas alto rendimiento)
"""
        elif 'RDS' in service:
            guide += """
CONFIGURACIÓN AMAZON RDS:
• Busca "RDS" en la calculadora
• Selecciona "Amazon RDS for MySQL"
• Configuración recomendada:
  - Instance class: db.t3.micro (desarrollo) o db.t3.small (producción)
  - Multi-AZ deployment: Sí (para producción)
  - Storage: 20 GB General Purpose SSD
"""
    
    guide += f"""

CONSIDERACIONES ADICIONALES:
{'-' * 30}
• Data Transfer: Incluye 10 GB/mes de transferencia a Internet
• Support: Basic (gratuito) o Developer ($29/mes)
• Backup: Considera costos de respaldos automáticos
• Monitoring: CloudWatch básico incluido

ESTIMACIÓN MENSUAL APROXIMADA:
{'-' * 35}
Basándose en los servicios identificados, el costo mensual estimado
podría estar entre $50-200 USD, dependiendo del uso real.

PRÓXIMOS PASOS:
{'-' * 15}
1. Usa esta guía para configurar la calculadora
2. Ajusta los valores según tus necesidades específicas
3. Guarda la estimación para referencia futura
4. Revisa mensualmente los costos reales vs estimados

Generado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return guide
