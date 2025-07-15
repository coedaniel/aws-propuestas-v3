"""
MCP Server - Cost Analysis Generation
Generates detailed cost analysis and pricing estimates for AWS projects
"""

import json
import boto3
import os
from datetime import datetime
from typing import Dict, Any, List

def lambda_handler(event, context):
    """Generate cost analysis based on project information"""
    try:
        project_info = event.get('project_info', {})
        agent_response = event.get('agent_response', '')
        
        print(f"Generating cost analysis for: {project_info.get('name', 'Unknown')}")
        
        # Generate cost analysis
        cost_analysis = generate_cost_analysis(project_info, agent_response)
        
        return {
            'cost_analysis': cost_analysis,
            'generated_at': datetime.now().isoformat(),
            'project_name': project_info.get('name', 'AWS Project')
        }
        
    except Exception as e:
        print(f"Error in cost analysis generator: {str(e)}")
        return {'error': str(e)}

def generate_cost_analysis(project_info: Dict[str, Any], agent_response: str) -> Dict[str, Any]:
    """Generate comprehensive cost analysis"""
    
    project_name = project_info.get('name', 'AWS Project')
    solution_type = project_info.get('solution_type', 'integral')
    services = project_info.get('selected_services', [])
    
    # Calculate costs based on solution type
    if solution_type == 'rapid_service':
        cost_breakdown = _calculate_rapid_service_costs(services)
    else:
        cost_breakdown = _calculate_integral_solution_costs(project_info)
    
    # Generate cost analysis document
    analysis = {
        'filename': f"{project_name.replace(' ', '_')}_Cost_Analysis.csv",
        'content': _generate_cost_csv(cost_breakdown, project_name),
        'summary': _generate_cost_summary(cost_breakdown),
        'recommendations': _generate_cost_recommendations(cost_breakdown),
        'total_monthly_estimate': cost_breakdown['total_monthly'],
        'total_annual_estimate': cost_breakdown['total_annual']
    }
    
    return analysis

def _calculate_rapid_service_costs(services: List[str]) -> Dict[str, Any]:
    """Calculate costs for rapid services"""
    
    service_costs = {
        'EC2': {
            'monthly': 8.50,  # t3.micro
            'description': 't3.micro instance (1 vCPU, 1 GB RAM)',
            'assumptions': '24/7 operation, On-Demand pricing'
        },
        'RDS': {
            'monthly': 15.84,  # db.t3.micro MySQL
            'description': 'db.t3.micro MySQL (1 vCPU, 1 GB RAM, 20 GB storage)',
            'assumptions': '24/7 operation, Single-AZ deployment'
        },
        'S3': {
            'monthly': 2.30,  # 100 GB standard storage
            'description': 'Standard storage (100 GB) + requests',
            'assumptions': '100 GB storage, 10,000 requests/month'
        },
        'ELB': {
            'monthly': 22.50,  # Application Load Balancer
            'description': 'Application Load Balancer',
            'assumptions': '1 ALB, 1 GB/hour data processing'
        },
        'CloudFront': {
            'monthly': 8.50,  # 100 GB data transfer
            'description': 'CloudFront distribution (100 GB transfer)',
            'assumptions': '100 GB data transfer, 1M requests'
        },
        'VPC': {
            'monthly': 0.00,  # VPC is free
            'description': 'VPC and basic networking',
            'assumptions': 'Standard VPC features (free tier)'
        }
    }
    
    total_monthly = 0
    selected_services = {}
    
    # Always include VPC for networking
    selected_services['VPC'] = service_costs['VPC']
    
    for service in services:
        if service in service_costs:
            selected_services[service] = service_costs[service]
            total_monthly += service_costs[service]['monthly']
    
    # Add data transfer costs (estimated)
    data_transfer_cost = len(services) * 2.0  # $2 per service for data transfer
    selected_services['Data Transfer'] = {
        'monthly': data_transfer_cost,
        'description': 'Inter-service and internet data transfer',
        'assumptions': 'Estimated based on service count'
    }
    total_monthly += data_transfer_cost
    
    return {
        'services': selected_services,
        'total_monthly': round(total_monthly, 2),
        'total_annual': round(total_monthly * 12, 2),
        'solution_type': 'rapid_service'
    }

def _calculate_integral_solution_costs(project_info: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate costs for integral solutions"""
    
    solution_detail = project_info.get('solution_type_detail', '').lower()
    
    if 'web' in solution_detail or 'aplicacion' in solution_detail:
        return _calculate_web_application_costs()
    elif 'data' in solution_detail or 'analitica' in solution_detail:
        return _calculate_data_analytics_costs()
    elif 'iot' in solution_detail:
        return _calculate_iot_costs()
    else:
        return _calculate_general_enterprise_costs()

def _calculate_web_application_costs() -> Dict[str, Any]:
    """Calculate costs for web application solution"""
    
    services = {
        'EC2 Instances': {
            'monthly': 34.00,  # 2x t3.small for high availability
            'description': '2x t3.small instances (2 vCPU, 2 GB RAM each)',
            'assumptions': '24/7 operation, Multi-AZ deployment'
        },
        'Application Load Balancer': {
            'monthly': 22.50,
            'description': 'Application Load Balancer with health checks',
            'assumptions': '1 ALB, 5 GB/hour data processing'
        },
        'RDS Database': {
            'monthly': 31.68,  # db.t3.small Multi-AZ
            'description': 'db.t3.small MySQL Multi-AZ (2 vCPU, 2 GB RAM, 100 GB)',
            'assumptions': 'Multi-AZ for high availability, automated backups'
        },
        'S3 Storage': {
            'monthly': 11.50,  # 500 GB + requests
            'description': 'S3 Standard storage for static assets and backups',
            'assumptions': '500 GB storage, 50,000 requests/month'
        },
        'CloudFront CDN': {
            'monthly': 17.00,  # 200 GB data transfer
            'description': 'CloudFront distribution for global content delivery',
            'assumptions': '200 GB data transfer, 2M requests'
        },
        'Route 53 DNS': {
            'monthly': 1.00,
            'description': 'Hosted zone and DNS queries',
            'assumptions': '1 hosted zone, 1M queries/month'
        },
        'CloudWatch Monitoring': {
            'monthly': 5.00,
            'description': 'Enhanced monitoring and custom metrics',
            'assumptions': 'Custom metrics, log retention, alarms'
        },
        'VPC & Networking': {
            'monthly': 3.00,
            'description': 'NAT Gateway and data transfer',
            'assumptions': '1 NAT Gateway, moderate data transfer'
        }
    }
    
    total_monthly = sum(service['monthly'] for service in services.values())
    
    return {
        'services': services,
        'total_monthly': round(total_monthly, 2),
        'total_annual': round(total_monthly * 12, 2),
        'solution_type': 'web_application'
    }

def _calculate_data_analytics_costs() -> Dict[str, Any]:
    """Calculate costs for data analytics solution"""
    
    services = {
        'S3 Data Lake': {
            'monthly': 46.00,  # 2 TB storage + requests
            'description': 'S3 Standard and IA storage for data lake',
            'assumptions': '2 TB total storage, mixed storage classes'
        },
        'Amazon Redshift': {
            'monthly': 180.00,  # dc2.large single node
            'description': 'Redshift dc2.large cluster for data warehousing',
            'assumptions': 'Single node cluster, 160 GB SSD storage'
        },
        'AWS Glue': {
            'monthly': 44.00,  # ETL jobs
            'description': 'Glue ETL jobs for data processing',
            'assumptions': '10 DPU-hours/day for ETL processing'
        },
        'Amazon Athena': {
            'monthly': 25.00,  # Query processing
            'description': 'Athena for ad-hoc queries on S3 data',
            'assumptions': '5 TB data scanned per month'
        },
        'QuickSight': {
            'monthly': 24.00,  # 4 users
            'description': 'QuickSight for business intelligence dashboards',
            'assumptions': '4 standard users, basic dashboards'
        },
        'Lambda Functions': {
            'monthly': 8.00,
            'description': 'Lambda functions for data processing triggers',
            'assumptions': '1M invocations, 512 MB memory, 30s duration'
        },
        'CloudWatch & Monitoring': {
            'monthly': 12.00,
            'description': 'Enhanced monitoring for data pipeline',
            'assumptions': 'Custom metrics, log retention, alarms'
        }
    }
    
    total_monthly = sum(service['monthly'] for service in services.values())
    
    return {
        'services': services,
        'total_monthly': round(total_monthly, 2),
        'total_annual': round(total_monthly * 12, 2),
        'solution_type': 'data_analytics'
    }

def _calculate_iot_costs() -> Dict[str, Any]:
    """Calculate costs for IoT solution"""
    
    services = {
        'AWS IoT Core': {
            'monthly': 15.00,  # Device connectivity and messaging
            'description': 'IoT Core for device connectivity and messaging',
            'assumptions': '100 devices, 1M messages/month'
        },
        'IoT Device Management': {
            'monthly': 5.00,
            'description': 'Device registry and fleet management',
            'assumptions': '100 devices registered and managed'
        },
        'Lambda Functions': {
            'monthly': 12.00,
            'description': 'Lambda for IoT data processing',
            'assumptions': '2M invocations, 256 MB memory, 10s duration'
        },
        'DynamoDB': {
            'monthly': 25.00,
            'description': 'DynamoDB for IoT data storage',
            'assumptions': 'On-demand billing, 1M read/write requests'
        },
        'Kinesis Data Streams': {
            'monthly': 36.00,
            'description': 'Kinesis for real-time data streaming',
            'assumptions': '2 shards, 1M records/month'
        },
        'S3 Storage': {
            'monthly': 23.00,
            'description': 'S3 for long-term IoT data storage',
            'assumptions': '1 TB storage, mixed storage classes'
        },
        'CloudWatch': {
            'monthly': 8.00,
            'description': 'Monitoring and alerting for IoT devices',
            'assumptions': 'Custom metrics, device health monitoring'
        }
    }
    
    total_monthly = sum(service['monthly'] for service in services.values())
    
    return {
        'services': services,
        'total_monthly': round(total_monthly, 2),
        'total_annual': round(total_monthly * 12, 2),
        'solution_type': 'iot_solution'
    }

def _calculate_general_enterprise_costs() -> Dict[str, Any]:
    """Calculate costs for general enterprise solution"""
    
    services = {
        'EC2 Instances': {
            'monthly': 68.00,  # 2x t3.medium
            'description': '2x t3.medium instances for application servers',
            'assumptions': '24/7 operation, Multi-AZ deployment'
        },
        'RDS Database': {
            'monthly': 63.36,  # db.t3.medium Multi-AZ
            'description': 'db.t3.medium PostgreSQL Multi-AZ',
            'assumptions': 'Multi-AZ, automated backups, 200 GB storage'
        },
        'Application Load Balancer': {
            'monthly': 22.50,
            'description': 'Application Load Balancer',
            'assumptions': '1 ALB, moderate traffic'
        },
        'S3 Storage': {
            'monthly': 23.00,
            'description': 'S3 for application data and backups',
            'assumptions': '1 TB storage, mixed access patterns'
        },
        'ElastiCache': {
            'monthly': 15.84,  # cache.t3.micro
            'description': 'ElastiCache Redis for session management',
            'assumptions': 'Single node, cache.t3.micro'
        },
        'CloudWatch & Monitoring': {
            'monthly': 10.00,
            'description': 'Comprehensive monitoring and logging',
            'assumptions': 'Custom metrics, log retention, alarms'
        },
        'VPC & Networking': {
            'monthly': 45.00,
            'description': 'NAT Gateway and VPN connectivity',
            'assumptions': '1 NAT Gateway, VPN connection'
        }
    }
    
    total_monthly = sum(service['monthly'] for service in services.values())
    
    return {
        'services': services,
        'total_monthly': round(total_monthly, 2),
        'total_annual': round(total_monthly * 12, 2),
        'solution_type': 'general_enterprise'
    }

def _generate_cost_csv(cost_breakdown: Dict[str, Any], project_name: str) -> str:
    """Generate CSV content for cost analysis"""
    
    csv_lines = [
        f"AWS Cost Analysis - {project_name}",
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "Service,Monthly Cost (USD),Annual Cost (USD),Description,Assumptions",
    ]
    
    for service_name, service_data in cost_breakdown['services'].items():
        monthly_cost = service_data['monthly']
        annual_cost = monthly_cost * 12
        description = service_data['description'].replace(',', ';')
        assumptions = service_data['assumptions'].replace(',', ';')
        
        csv_lines.append(f'"{service_name}",{monthly_cost},{annual_cost:.2f},"{description}","{assumptions}"')
    
    csv_lines.extend([
        "",
        f"TOTAL MONTHLY,{cost_breakdown['total_monthly']},{cost_breakdown['total_annual']:.2f},Total estimated costs,Based on current assumptions",
        "",
        "COST OPTIMIZATION RECOMMENDATIONS:",
        "1. Consider Reserved Instances for EC2 (up to 75% savings)",
        "2. Use S3 Intelligent Tiering for automatic cost optimization",
        "3. Implement CloudWatch cost monitoring and budgets",
        "4. Review and optimize data transfer costs",
        "5. Consider Spot Instances for non-critical workloads",
        "",
        "IMPORTANT NOTES:",
        "- Costs are estimates based on typical usage patterns",
        "- Actual costs may vary based on usage and region",
        "- Data transfer costs may apply between services",
        "- Consider AWS Free Tier eligibility for new accounts",
        "- Prices are subject to change - verify current pricing"
    ])
    
    return '\n'.join(csv_lines)

def _generate_cost_summary(cost_breakdown: Dict[str, Any]) -> Dict[str, Any]:
    """Generate cost summary"""
    
    return {
        'total_monthly_usd': cost_breakdown['total_monthly'],
        'total_annual_usd': cost_breakdown['total_annual'],
        'service_count': len(cost_breakdown['services']),
        'highest_cost_service': max(
            cost_breakdown['services'].items(),
            key=lambda x: x[1]['monthly']
        )[0],
        'solution_type': cost_breakdown['solution_type']
    }

def _generate_cost_recommendations(cost_breakdown: Dict[str, Any]) -> List[str]:
    """Generate cost optimization recommendations"""
    
    recommendations = [
        "Consider AWS Reserved Instances for predictable workloads (up to 75% savings)",
        "Implement S3 Intelligent Tiering for automatic storage cost optimization",
        "Use AWS Cost Explorer and Budgets for ongoing cost monitoring",
        "Review data transfer patterns and optimize cross-AZ communication",
        "Consider Spot Instances for fault-tolerant, flexible workloads"
    ]
    
    # Add specific recommendations based on solution type
    if cost_breakdown['solution_type'] == 'web_application':
        recommendations.extend([
            "Implement CloudFront caching to reduce origin server load",
            "Use Auto Scaling to match capacity with demand",
            "Consider Aurora Serverless for variable database workloads"
        ])
    elif cost_breakdown['solution_type'] == 'data_analytics':
        recommendations.extend([
            "Use S3 lifecycle policies to transition old data to cheaper storage classes",
            "Consider Redshift Spectrum for infrequent query workloads",
            "Optimize Glue job scheduling to reduce idle time"
        ])
    elif cost_breakdown['solution_type'] == 'iot_solution':
        recommendations.extend([
            "Implement device-side filtering to reduce message volume",
            "Use DynamoDB on-demand billing for unpredictable workloads",
            "Consider IoT Device Defender for security cost optimization"
        ])
    
    return recommendations
