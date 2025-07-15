"""
MCP Server - AWS Architecture Diagrams Generation
Uses the AWS Diagram MCP Server to generate professional architecture diagrams
"""

import json
import boto3
import os
import uuid
from datetime import datetime
from typing import Dict, Any, List

def lambda_handler(event, context):
    """Generate AWS architecture diagrams based on project information"""
    try:
        project_info = event.get('project_info', {})
        agent_response = event.get('agent_response', '')
        
        print(f"Generating diagrams for project: {project_info.get('name', 'Unknown')}")
        
        # Generate different types of diagrams
        diagrams = {
            'basic_architecture': generate_basic_architecture_diagram(project_info),
            'detailed_architecture': generate_detailed_architecture_diagram(project_info),
            'network_diagram': generate_network_diagram(project_info)
        }
        
        return {
            'diagrams': diagrams,
            'generated_at': datetime.now().isoformat(),
            'project_name': project_info.get('name', 'AWS Project')
        }
        
    except Exception as e:
        print(f"Error in diagram generator: {str(e)}")
        return {'error': str(e)}

def generate_basic_architecture_diagram(project_info: Dict[str, Any]) -> Dict[str, Any]:
    """Generate basic architecture diagram"""
    
    project_name = project_info.get('name', 'AWS Architecture')
    services = project_info.get('selected_services', [])
    solution_type = project_info.get('solution_type', 'integral')
    
    # Generate diagram code based on services
    if solution_type == 'rapid_service':
        diagram_code = _generate_rapid_service_diagram_code(project_name, services)
    else:
        diagram_code = _generate_integral_solution_diagram_code(project_name, project_info)
    
    return {
        'type': 'basic_architecture',
        'filename': f"{project_name.replace(' ', '_')}_Basic_Architecture",
        'diagram_code': diagram_code,
        'description': 'Basic architecture overview showing main components'
    }

def generate_detailed_architecture_diagram(project_info: Dict[str, Any]) -> Dict[str, Any]:
    """Generate detailed architecture diagram with clusters"""
    
    project_name = project_info.get('name', 'AWS Architecture')
    
    # Generate more detailed diagram with clusters
    diagram_code = f'''with Diagram("{project_name} - Detailed Architecture", show=False, direction="TB"):
    # Users and External Access
    users = Users("Users")
    
    with Cluster("AWS Cloud"):
        with Cluster("Public Subnet"):
            alb = ALB("Application\\nLoad Balancer")
            nat = NATGateway("NAT Gateway")
        
        with Cluster("Private Subnet - Application Tier"):
            app_servers = [
                EC2("App Server 1"),
                EC2("App Server 2"),
                EC2("App Server 3")
            ]
        
        with Cluster("Private Subnet - Database Tier"):
            db_primary = RDS("Primary DB")
            db_replica = RDS("Read Replica")
        
        with Cluster("Storage & Cache"):
            s3 = S3("Object Storage")
            cache = ElastiCache("Redis Cache")
        
        with Cluster("Monitoring & Security"):
            cloudwatch = CloudWatch("Monitoring")
            waf = WAF("Web Application\\nFirewall")
    
    # Connections
    users >> waf >> alb
    alb >> app_servers
    app_servers >> db_primary
    db_primary >> db_replica
    app_servers >> cache
    app_servers >> s3
    cloudwatch >> app_servers
    cloudwatch >> db_primary
'''
    
    return {
        'type': 'detailed_architecture',
        'filename': f"{project_name.replace(' ', '_')}_Detailed_Architecture",
        'diagram_code': diagram_code,
        'description': 'Detailed architecture with security and monitoring components'
    }

def generate_network_diagram(project_info: Dict[str, Any]) -> Dict[str, Any]:
    """Generate network architecture diagram"""
    
    project_name = project_info.get('name', 'AWS Network')
    
    diagram_code = f'''with Diagram("{project_name} - Network Architecture", show=False, direction="LR"):
    # On-premises
    onprem = OnPremises("Corporate\\nData Center")
    
    with Cluster("AWS VPC (10.0.0.0/16)"):
        igw = InternetGateway("Internet Gateway")
        
        with Cluster("Availability Zone A"):
            with Cluster("Public Subnet A (10.0.1.0/24)"):
                nat_a = NATGateway("NAT Gateway A")
                alb_a = ALB("ALB A")
            
            with Cluster("Private Subnet A (10.0.10.0/24)"):
                app_a = EC2("App Server A")
                db_a = RDS("Database A")
        
        with Cluster("Availability Zone B"):
            with Cluster("Public Subnet B (10.0.2.0/24)"):
                nat_b = NATGateway("NAT Gateway B")
                alb_b = ALB("ALB B")
            
            with Cluster("Private Subnet B (10.0.20.0/24)"):
                app_b = EC2("App Server B")
                db_b = RDS("Database B")
        
        # VPN Connection
        vpn = VPN("VPN Connection")
        vgw = VPNGateway("Virtual Private\\nGateway")
    
    # External connections
    internet = Internet("Internet")
    
    # Network flow
    internet >> igw >> [alb_a, alb_b]
    alb_a >> app_a >> db_a
    alb_b >> app_b >> db_b
    db_a - Edge(style="dashed") - db_b
    
    # Private connectivity
    onprem >> vpn >> vgw
    vgw >> [app_a, app_b]
    
    # NAT for outbound
    app_a >> nat_a >> igw
    app_b >> nat_b >> igw
'''
    
    return {
        'type': 'network_diagram',
        'filename': f"{project_name.replace(' ', '_')}_Network_Architecture",
        'diagram_code': diagram_code,
        'description': 'Network architecture showing VPC, subnets, and connectivity'
    }

def _generate_rapid_service_diagram_code(project_name: str, services: List[str]) -> str:
    """Generate diagram code for rapid services"""
    
    # Start with basic structure
    diagram_code = f'with Diagram("{project_name} - Service Architecture", show=False):\n'
    diagram_code += '    user = Users("Users")\n'
    
    # Add services based on selection
    service_components = []
    
    if 'EC2' in services:
        service_components.append('ec2 = EC2("EC2 Instance")')
    if 'RDS' in services:
        service_components.append('rds = RDS("Database")')
    if 'S3' in services:
        service_components.append('s3 = S3("Storage")')
    if 'ELB' in services:
        service_components.append('elb = ELB("Load Balancer")')
    if 'VPC' in services:
        service_components.append('vpc = VPC("Virtual Network")')
    if 'CloudFront' in services:
        service_components.append('cdn = CloudFront("CDN")')
    
    # Add default components if none specified
    if not service_components:
        service_components = [
            'ec2 = EC2("Application Server")',
            'rds = RDS("Database")',
            's3 = S3("Storage")'
        ]
    
    # Add components to diagram
    for component in service_components:
        diagram_code += f'    {component}\n'
    
    # Add monitoring
    diagram_code += '    monitoring = CloudWatch("Monitoring")\n'
    
    # Create connections
    diagram_code += '\n    # Connections\n'
    
    if 'CloudFront' in services:
        diagram_code += '    user >> cdn\n'
        if 'ELB' in services:
            diagram_code += '    cdn >> elb\n'
        elif 'EC2' in services:
            diagram_code += '    cdn >> ec2\n'
    elif 'ELB' in services:
        diagram_code += '    user >> elb\n'
        if 'EC2' in services:
            diagram_code += '    elb >> ec2\n'
    elif 'EC2' in services:
        diagram_code += '    user >> ec2\n'
    
    if 'EC2' in services and 'RDS' in services:
        diagram_code += '    ec2 >> rds\n'
    if 'EC2' in services and 'S3' in services:
        diagram_code += '    ec2 >> s3\n'
    
    # Add monitoring connections
    if 'EC2' in services:
        diagram_code += '    monitoring >> ec2\n'
    if 'RDS' in services:
        diagram_code += '    monitoring >> rds\n'
    
    return diagram_code

def _generate_integral_solution_diagram_code(project_name: str, project_info: Dict[str, Any]) -> str:
    """Generate diagram code for integral solutions"""
    
    # Analyze project info to determine architecture pattern
    solution_detail = project_info.get('solution_type_detail', '').lower()
    
    if 'web' in solution_detail or 'aplicacion' in solution_detail:
        return _generate_web_application_diagram(project_name)
    elif 'data' in solution_detail or 'analitica' in solution_detail:
        return _generate_data_analytics_diagram(project_name)
    elif 'iot' in solution_detail:
        return _generate_iot_diagram(project_name)
    elif 'migracion' in solution_detail:
        return _generate_migration_diagram(project_name)
    else:
        return _generate_general_enterprise_diagram(project_name)

def _generate_web_application_diagram(project_name: str) -> str:
    """Generate web application architecture diagram"""
    return f'''with Diagram("{project_name} - Web Application", show=False):
    users = Users("Users")
    
    with Cluster("AWS Cloud"):
        cdn = CloudFront("CloudFront CDN")
        waf = WAF("Web Application Firewall")
        
        with Cluster("Load Balancing"):
            alb = ALB("Application Load Balancer")
        
        with Cluster("Application Tier"):
            app_servers = [
                ECS("Web App 1"),
                ECS("Web App 2"),
                ECS("Web App 3")
            ]
        
        with Cluster("Database Tier"):
            db_primary = RDS("Primary Database")
            db_replica = RDS("Read Replica")
        
        with Cluster("Storage & Cache"):
            s3 = S3("Static Assets")
            cache = ElastiCache("Redis Cache")
        
        monitoring = CloudWatch("CloudWatch")
    
    # Flow
    users >> cdn >> waf >> alb >> app_servers
    app_servers >> db_primary
    db_primary >> db_replica
    app_servers >> cache
    app_servers >> s3
    monitoring >> app_servers
    monitoring >> db_primary
'''

def _generate_data_analytics_diagram(project_name: str) -> str:
    """Generate data analytics architecture diagram"""
    return f'''with Diagram("{project_name} - Data Analytics Platform", show=False, direction="LR"):
    # Data Sources
    sources = [
        OnPremises("On-Premises DB"),
        SaaS("SaaS Applications"),
        API("External APIs")
    ]
    
    with Cluster("Data Ingestion"):
        kinesis = Kinesis("Kinesis Data Streams")
        glue = Glue("AWS Glue ETL")
    
    with Cluster("Data Lake"):
        s3_raw = S3("Raw Data")
        s3_processed = S3("Processed Data")
        s3_curated = S3("Curated Data")
    
    with Cluster("Analytics & ML"):
        athena = Athena("Athena")
        redshift = Redshift("Redshift")
        sagemaker = Sagemaker("SageMaker")
    
    with Cluster("Visualization"):
        quicksight = Quicksight("QuickSight")
        
    # Data flow
    sources >> kinesis >> glue
    glue >> s3_raw >> s3_processed >> s3_curated
    s3_curated >> athena
    s3_curated >> redshift
    s3_curated >> sagemaker
    [athena, redshift, sagemaker] >> quicksight
'''

def _generate_iot_diagram(project_name: str) -> str:
    """Generate IoT architecture diagram"""
    return f'''with Diagram("{project_name} - IoT Platform", show=False, direction="TB"):
    # IoT Devices
    devices = [
        IoT("Sensor 1"),
        IoT("Sensor 2"),
        IoT("Gateway")
    ]
    
    with Cluster("AWS IoT Core"):
        iot_core = IoTCore("IoT Core")
        iot_rules = IoTRules("IoT Rules Engine")
    
    with Cluster("Data Processing"):
        kinesis = Kinesis("Kinesis")
        lambda_func = Lambda("Data Processor")
    
    with Cluster("Storage"):
        dynamodb = DynamoDB("Device Data")
        s3 = S3("Historical Data")
    
    with Cluster("Analytics"):
        timestream = Timestream("Time Series DB")
        quicksight = Quicksight("Analytics Dashboard")
    
    # Data flow
    devices >> iot_core >> iot_rules
    iot_rules >> kinesis >> lambda_func
    lambda_func >> dynamodb
    lambda_func >> s3
    lambda_func >> timestream
    timestream >> quicksight
'''

def _generate_migration_diagram(project_name: str) -> str:
    """Generate migration architecture diagram"""
    return f'''with Diagram("{project_name} - Migration Architecture", show=False, direction="LR"):
    # Source Environment
    with Cluster("On-Premises"):
        onprem_app = OnPremises("Legacy Application")
        onprem_db = Database("Legacy Database")
        onprem_files = Storage("File Storage")
    
    # Migration Tools
    with Cluster("Migration Services"):
        dms = DMS("Database Migration Service")
        datasync = DataSync("DataSync")
        app_migration = ApplicationMigration("Application Migration")
    
    # Target Environment
    with Cluster("AWS Cloud"):
        with Cluster("Compute"):
            ec2 = EC2("Migrated Application")
            
        with Cluster("Database"):
            rds = RDS("Amazon RDS")
            
        with Cluster("Storage"):
            s3 = S3("Amazon S3")
            efs = EFS("Amazon EFS")
    
    # Migration paths
    onprem_app >> app_migration >> ec2
    onprem_db >> dms >> rds
    onprem_files >> datasync >> s3
    onprem_files >> datasync >> efs
'''

def _generate_general_enterprise_diagram(project_name: str) -> str:
    """Generate general enterprise architecture diagram"""
    return f'''with Diagram("{project_name} - Enterprise Architecture", show=False):
    users = Users("Enterprise Users")
    
    with Cluster("AWS Cloud"):
        with Cluster("Security & Access"):
            waf = WAF("WAF")
            cognito = Cognito("User Authentication")
        
        with Cluster("Application Layer"):
            api_gw = APIGateway("API Gateway")
            lambda_funcs = [
                Lambda("Business Logic 1"),
                Lambda("Business Logic 2"),
                Lambda("Business Logic 3")
            ]
        
        with Cluster("Data Layer"):
            dynamodb = DynamoDB("NoSQL Database")
            rds = RDS("Relational Database")
            s3 = S3("Object Storage")
        
        with Cluster("Integration"):
            sqs = SQS("Message Queue")
            sns = SNS("Notifications")
            eventbridge = EventBridge("Event Bus")
        
        with Cluster("Monitoring"):
            cloudwatch = CloudWatch("Monitoring")
            xray = XRay("Distributed Tracing")
    
    # Connections
    users >> cognito >> waf >> api_gw >> lambda_funcs
    lambda_funcs >> [dynamodb, rds, s3]
    lambda_funcs >> sqs >> lambda_funcs
    lambda_funcs >> sns
    lambda_funcs >> eventbridge
    [cloudwatch, xray] >> lambda_funcs
'''
