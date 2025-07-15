"""
MCP Server - Cost Analysis Generation
Real MCP server for generating cost analysis and pricing estimates
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("aws-cost-analysis")

class ProjectInfo(BaseModel):
    name: str
    solution_type: str
    solution_type_detail: Optional[str] = None
    selected_services: List[str] = []
    requirements: Optional[str] = None

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available cost analysis tools"""
    return [
        Tool(
            name="generate_cost_analysis",
            description="Generate detailed cost analysis for AWS project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_info": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "solution_type": {"type": "string"},
                            "solution_type_detail": {"type": "string"},
                            "selected_services": {"type": "array", "items": {"type": "string"}},
                            "requirements": {"type": "string"}
                        },
                        "required": ["name", "solution_type"]
                    },
                    "agent_response": {"type": "string"},
                },
                "required": ["project_info"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls for cost analysis"""
    
    try:
        if name == "generate_cost_analysis":
            result = await generate_cost_analysis(arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}")
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

async def generate_cost_analysis(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive cost analysis"""
    
    project_info = ProjectInfo(**arguments["project_info"])
    agent_response = arguments.get("agent_response", "")
    
    logger.info(f"Generating cost analysis for: {project_info.name}")
    
    # Calculate costs based on solution type
    if project_info.solution_type == 'rapid_service':
        cost_breakdown = _calculate_rapid_service_costs(project_info.selected_services)
    else:
        cost_breakdown = _calculate_integral_solution_costs(project_info)
    
    # Generate CSV content
    csv_content = _generate_cost_csv(cost_breakdown, project_info.name)
    
    filename = f"{project_info.name.replace(' ', '_')}_Cost_Analysis.csv"
    
    return {
        "filename": filename,
        "content": csv_content,
        "content_type": "text/csv",
        "size": len(csv_content.encode('utf-8')),
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_monthly_usd": cost_breakdown['total_monthly'],
            "total_annual_usd": cost_breakdown['total_annual'],
            "service_count": len(cost_breakdown['services']),
            "solution_type": cost_breakdown['solution_type']
        },
        "recommendations": _generate_cost_recommendations(cost_breakdown)
    }

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

def _calculate_integral_solution_costs(project_info: ProjectInfo) -> Dict[str, Any]:
    """Calculate costs for integral solutions"""
    
    solution_detail = project_info.solution_type_detail or ""
    
    if 'web' in solution_detail.lower() or 'aplicacion' in solution_detail.lower():
        return _calculate_web_application_costs()
    elif 'data' in solution_detail.lower() or 'analitica' in solution_detail.lower():
        return _calculate_data_analytics_costs()
    elif 'iot' in solution_detail.lower():
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

async def main():
    """Main function to run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="aws-cost-analysis",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
