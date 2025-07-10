"""
Diagram generator for AWS proposals
"""
import xml.etree.ElementTree as ET
from typing import Dict, Any
import base64

def generate_drawio_diagram(project_info: Dict[str, Any]) -> str:
    """
    Generate Draw.io diagram XML for the project
    
    Args:
        project_info: Dictionary with project information
    
    Returns:
        str: Draw.io XML content
    """
    project_name = project_info.get('name', 'AWS Project')
    project_type = project_info.get('type', 'general')
    
    # Create basic Draw.io structure
    mxfile = ET.Element('mxfile', host="app.diagrams.net", modified="2024-01-01T00:00:00.000Z", agent="AWS Propuestas v3", version="22.1.11")
    diagram = ET.SubElement(mxfile, 'diagram', name=f"{project_name} Architecture", id="architecture")
    
    # Create mxGraphModel
    mxGraphModel = ET.SubElement(diagram, 'mxGraphModel', dx="1422", dy="794", grid="1", gridSize="10", guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1", pageWidth="827", pageHeight="1169", math="0", shadow="0")
    root = ET.SubElement(mxGraphModel, 'root')
    
    # Add default cells
    ET.SubElement(root, 'mxCell', id="0")
    ET.SubElement(root, 'mxCell', id="1", parent="0")
    
    # Add title
    title_cell = ET.SubElement(root, 'mxCell', id="title", value=f"{project_name} - AWS Architecture", style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=16;fontStyle=1", vertex="1", parent="1")
    ET.SubElement(title_cell, 'mxGeometry', x="300", y="30", width="200", height="30", **{"as": "geometry"})
    
    # Add AWS Cloud container
    cloud_cell = ET.SubElement(root, 'mxCell', id="aws-cloud", value="AWS Cloud", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;verticalAlign=top;fontSize=14;fontStyle=1", vertex="1", parent="1")
    ET.SubElement(cloud_cell, 'mxGeometry', x="50", y="80", width="700", height="500", **{"as": "geometry"})
    
    # Add components based on project type
    if 'web' in project_type.lower() or 'app' in project_type.lower():
        add_web_components(root)
    elif 'data' in project_type.lower() or 'analitica' in project_type.lower():
        add_analytics_components(root)
    elif 'iot' in project_type.lower():
        add_iot_components(root)
    else:
        add_general_components(root)
    
    # Convert to string
    return ET.tostring(mxfile, encoding='unicode')

def add_web_components(root):
    """Add web application components to diagram"""
    # Internet Gateway
    igw_cell = ET.SubElement(root, 'mxCell', id="igw", value="Internet Gateway", style="outlineConnect=0;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;shape=mxgraph.aws3.internet_gateway;fillColor=#F58534;gradientColor=none;", vertex="1", parent="1")
    ET.SubElement(igw_cell, 'mxGeometry', x="380", y="120", width="40", height="42", **{"as": "geometry"})
    
    # Application Load Balancer
    alb_cell = ET.SubElement(root, 'mxCell', id="alb", value="Application Load Balancer", style="outlineConnect=0;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;shape=mxgraph.aws3.application_load_balancer;fillColor=#F58534;gradientColor=none;", vertex="1", parent="1")
    ET.SubElement(alb_cell, 'mxGeometry', x="380", y="200", width="40", height="42", **{"as": "geometry"})
    
    # EC2 Instances
    ec2_1_cell = ET.SubElement(root, 'mxCell', id="ec2-1", value="Web Server 1", style="outlineConnect=0;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;shape=mxgraph.aws3.ec2;fillColor=#F58534;gradientColor=none;", vertex="1", parent="1")
    ET.SubElement(ec2_1_cell, 'mxGeometry', x="280", y="300", width="40", height="48", **{"as": "geometry"})
    
    ec2_2_cell = ET.SubElement(root, 'mxCell', id="ec2-2", value="Web Server 2", style="outlineConnect=0;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;shape=mxgraph.aws3.ec2;fillColor=#F58534;gradientColor=none;", vertex="1", parent="1")
    ET.SubElement(ec2_2_cell, 'mxGeometry', x="480", y="300", width="40", height="48", **{"as": "geometry"})
    
    # RDS Database
    rds_cell = ET.SubElement(root, 'mxCell', id="rds", value="RDS Database", style="outlineConnect=0;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;shape=mxgraph.aws3.rds;fillColor=#2E73B8;gradientColor=none;", vertex="1", parent="1")
    ET.SubElement(rds_cell, 'mxGeometry', x="380", y="450", width="40", height="48", **{"as": "geometry"})
    
    # Add connections
    add_connection(root, "igw-alb", "igw", "alb")
    add_connection(root, "alb-ec2-1", "alb", "ec2-1")
    add_connection(root, "alb-ec2-2", "alb", "ec2-2")
    add_connection(root, "ec2-1-rds", "ec2-1", "rds")
    add_connection(root, "ec2-2-rds", "ec2-2", "rds")

def add_analytics_components(root):
    """Add analytics components to diagram"""
    # S3 Data Lake
    s3_cell = ET.SubElement(root, 'mxCell', id="s3", value="S3 Data Lake", style="outlineConnect=0;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;shape=mxgraph.aws3.s3;fillColor=#E05243;gradientColor=none;", vertex="1", parent="1")
    ET.SubElement(s3_cell, 'mxGeometry', x="150", y="200", width="40", height="48", **{"as": "geometry"})
    
    # Glue ETL
    glue_cell = ET.SubElement(root, 'mxCell', id="glue", value="AWS Glue ETL", style="outlineConnect=0;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;shape=mxgraph.aws3.glue;fillColor=#F58534;gradientColor=none;", vertex="1", parent="1")
    ET.SubElement(glue_cell, 'mxGeometry', x="300", y="200", width="40", height="48", **{"as": "geometry"})
    
    # Redshift
    redshift_cell = ET.SubElement(root, 'mxCell', id="redshift", value="Redshift Cluster", style="outlineConnect=0;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;shape=mxgraph.aws3.redshift;fillColor=#2E73B8;gradientColor=none;", vertex="1", parent="1")
    ET.SubElement(redshift_cell, 'mxGeometry', x="450", y="200", width="40", height="48", **{"as": "geometry"})
    
    # QuickSight
    quicksight_cell = ET.SubElement(root, 'mxCell', id="quicksight", value="QuickSight", style="outlineConnect=0;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;shape=mxgraph.aws3.quicksight;fillColor=#F58534;gradientColor=none;", vertex="1", parent="1")
    ET.SubElement(quicksight_cell, 'mxGeometry', x="600", y="200", width="40", height="48", **{"as": "geometry"})
    
    # Add connections
    add_connection(root, "s3-glue", "s3", "glue")
    add_connection(root, "glue-redshift", "glue", "redshift")
    add_connection(root, "redshift-quicksight", "redshift", "quicksight")

def add_iot_components(root):
    """Add IoT components to diagram"""
    # IoT Device
    device_cell = ET.SubElement(root, 'mxCell', id="device", value="IoT Devices", style="outlineConnect=0;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;shape=mxgraph.aws3.iot_thing;fillColor=#F58534;gradientColor=none;", vertex="1", parent="1")
    ET.SubElement(device_cell, 'mxGeometry', x="100", y="200", width="40", height="48", **{"as": "geometry"})
    
    # IoT Core
    iot_core_cell = ET.SubElement(root, 'mxCell', id="iot-core", value="IoT Core", style="outlineConnect=0;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;shape=mxgraph.aws3.iot_core;fillColor=#F58534;gradientColor=none;", vertex="1", parent="1")
    ET.SubElement(iot_core_cell, 'mxGeometry', x="250", y="200", width="40", height="48", **{"as": "geometry"})
    
    # Lambda
    lambda_cell = ET.SubElement(root, 'mxCell', id="lambda", value="Lambda Functions", style="outlineConnect=0;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;shape=mxgraph.aws3.lambda;fillColor=#F58534;gradientColor=none;", vertex="1", parent="1")
    ET.SubElement(lambda_cell, 'mxGeometry', x="400", y="200", width="40", height="48", **{"as": "geometry"})
    
    # DynamoDB
    dynamodb_cell = ET.SubElement(root, 'mxCell', id="dynamodb", value="DynamoDB", style="outlineConnect=0;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;shape=mxgraph.aws3.dynamodb;fillColor=#2E73B8;gradientColor=none;", vertex="1", parent="1")
    ET.SubElement(dynamodb_cell, 'mxGeometry', x="550", y="200", width="40", height="48", **{"as": "geometry"})
    
    # Add connections
    add_connection(root, "device-iot-core", "device", "iot-core")
    add_connection(root, "iot-core-lambda", "iot-core", "lambda")
    add_connection(root, "lambda-dynamodb", "lambda", "dynamodb")

def add_general_components(root):
    """Add general components to diagram"""
    # VPC
    vpc_cell = ET.SubElement(root, 'mxCell', id="vpc", value="VPC", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;verticalAlign=top;fontSize=12;fontStyle=1", vertex="1", parent="1")
    ET.SubElement(vpc_cell, 'mxGeometry', x="100", y="150", width="600", height="350", **{"as": "geometry"})
    
    # Public Subnet
    public_subnet_cell = ET.SubElement(root, 'mxCell', id="public-subnet", value="Public Subnet", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;verticalAlign=top;fontSize=10", vertex="1", parent="1")
    ET.SubElement(public_subnet_cell, 'mxGeometry', x="150", y="200", width="250", height="100", **{"as": "geometry"})
    
    # Private Subnet
    private_subnet_cell = ET.SubElement(root, 'mxCell', id="private-subnet", value="Private Subnet", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;verticalAlign=top;fontSize=10", vertex="1", parent="1")
    ET.SubElement(private_subnet_cell, 'mxGeometry', x="450", y="200", width="200", height="250", **{"as": "geometry"})
    
    # EC2 Instance
    ec2_cell = ET.SubElement(root, 'mxCell', id="ec2", value="EC2 Instance", style="outlineConnect=0;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;shape=mxgraph.aws3.ec2;fillColor=#F58534;gradientColor=none;", vertex="1", parent="1")
    ET.SubElement(ec2_cell, 'mxGeometry', x="500", y="250", width="40", height="48", **{"as": "geometry"})

def add_connection(root, connection_id, source_id, target_id):
    """Add connection between two components"""
    connection_cell = ET.SubElement(root, 'mxCell', id=connection_id, value="", style="endArrow=classic;html=1;rounded=0;", edge="1", parent="1", source=source_id, target=target_id)
    ET.SubElement(connection_cell, 'mxGeometry', width="50", height="50", relative="1", **{"as": "geometry"})

def generate_svg_diagram(project_info: Dict[str, Any]) -> str:
    """
    Generate SVG diagram for the project
    
    Args:
        project_info: Dictionary with project information
    
    Returns:
        str: SVG content
    """
    project_name = project_info.get('name', 'AWS Project')
    project_type = project_info.get('type', 'general')
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .title {{ font-family: Arial, sans-serif; font-size: 18px; font-weight: bold; text-anchor: middle; }}
      .component {{ font-family: Arial, sans-serif; font-size: 12px; text-anchor: middle; }}
      .aws-service {{ fill: #FF9900; stroke: #232F3E; stroke-width: 2; }}
      .container {{ fill: none; stroke: #232F3E; stroke-width: 2; stroke-dasharray: 5,5; }}
      .connection {{ stroke: #232F3E; stroke-width: 2; marker-end: url(#arrowhead); }}
    </style>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#232F3E" />
    </marker>
  </defs>
  
  <!-- Title -->
  <text x="400" y="30" class="title">{project_name} - AWS Architecture</text>
  
  <!-- AWS Cloud Container -->
  <rect x="50" y="60" width="700" height="500" class="container" />
  <text x="400" y="80" class="component">AWS Cloud</text>
'''
    
    if 'web' in project_type.lower() or 'app' in project_type.lower():
        svg_content += get_web_svg_components()
    elif 'data' in project_type.lower() or 'analitica' in project_type.lower():
        svg_content += get_analytics_svg_components()
    elif 'iot' in project_type.lower():
        svg_content += get_iot_svg_components()
    else:
        svg_content += get_general_svg_components()
    
    svg_content += '</svg>'
    return svg_content

def get_web_svg_components() -> str:
    """Get web application SVG components"""
    return '''
  <!-- Internet Gateway -->
  <rect x="380" y="120" width="40" height="30" class="aws-service" />
  <text x="400" y="140" class="component">IGW</text>
  
  <!-- Application Load Balancer -->
  <rect x="380" y="200" width="40" height="30" class="aws-service" />
  <text x="400" y="220" class="component">ALB</text>
  
  <!-- EC2 Instances -->
  <rect x="280" y="300" width="40" height="30" class="aws-service" />
  <text x="300" y="320" class="component">EC2-1</text>
  
  <rect x="480" y="300" width="40" height="30" class="aws-service" />
  <text x="500" y="320" class="component">EC2-2</text>
  
  <!-- RDS Database -->
  <rect x="380" y="450" width="40" height="30" class="aws-service" />
  <text x="400" y="470" class="component">RDS</text>
  
  <!-- Connections -->
  <line x1="400" y1="150" x2="400" y2="200" class="connection" />
  <line x1="400" y1="230" x2="300" y2="300" class="connection" />
  <line x1="400" y1="230" x2="500" y2="300" class="connection" />
  <line x1="300" y1="330" x2="400" y2="450" class="connection" />
  <line x1="500" y1="330" x2="400" y2="450" class="connection" />
'''

def get_analytics_svg_components() -> str:
    """Get analytics SVG components"""
    return '''
  <!-- S3 Data Lake -->
  <rect x="150" y="200" width="40" height="30" class="aws-service" />
  <text x="170" y="220" class="component">S3</text>
  
  <!-- Glue ETL -->
  <rect x="300" y="200" width="40" height="30" class="aws-service" />
  <text x="320" y="220" class="component">Glue</text>
  
  <!-- Redshift -->
  <rect x="450" y="200" width="40" height="30" class="aws-service" />
  <text x="470" y="220" class="component">Redshift</text>
  
  <!-- QuickSight -->
  <rect x="600" y="200" width="40" height="30" class="aws-service" />
  <text x="620" y="220" class="component">QuickSight</text>
  
  <!-- Connections -->
  <line x1="190" y1="215" x2="300" y2="215" class="connection" />
  <line x1="340" y1="215" x2="450" y2="215" class="connection" />
  <line x1="490" y1="215" x2="600" y2="215" class="connection" />
'''

def get_iot_svg_components() -> str:
    """Get IoT SVG components"""
    return '''
  <!-- IoT Devices -->
  <rect x="100" y="200" width="40" height="30" class="aws-service" />
  <text x="120" y="220" class="component">Devices</text>
  
  <!-- IoT Core -->
  <rect x="250" y="200" width="40" height="30" class="aws-service" />
  <text x="270" y="220" class="component">IoT Core</text>
  
  <!-- Lambda -->
  <rect x="400" y="200" width="40" height="30" class="aws-service" />
  <text x="420" y="220" class="component">Lambda</text>
  
  <!-- DynamoDB -->
  <rect x="550" y="200" width="40" height="30" class="aws-service" />
  <text x="570" y="220" class="component">DynamoDB</text>
  
  <!-- Connections -->
  <line x1="140" y1="215" x2="250" y2="215" class="connection" />
  <line x1="290" y1="215" x2="400" y2="215" class="connection" />
  <line x1="440" y1="215" x2="550" y2="215" class="connection" />
'''

def get_general_svg_components() -> str:
    """Get general SVG components"""
    return '''
  <!-- VPC -->
  <rect x="100" y="150" width="600" height="350" class="container" />
  <text x="400" y="170" class="component">VPC (10.0.0.0/16)</text>
  
  <!-- Public Subnet -->
  <rect x="150" y="200" width="250" height="100" class="container" />
  <text x="275" y="220" class="component">Public Subnet</text>
  
  <!-- Private Subnet -->
  <rect x="450" y="200" width="200" height="250" class="container" />
  <text x="550" y="220" class="component">Private Subnet</text>
  
  <!-- EC2 Instance -->
  <rect x="500" y="250" width="40" height="30" class="aws-service" />
  <text x="520" y="270" class="component">EC2</text>
'''
