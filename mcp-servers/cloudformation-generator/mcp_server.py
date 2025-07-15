"""
MCP Server - CloudFormation Template Generation
Real MCP server for generating CloudFormation templates
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
import yaml

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
server = Server("aws-cloudformation-generator")

class ProjectInfo(BaseModel):
    name: str
    solution_type: str
    solution_type_detail: Optional[str] = None
    selected_services: List[str] = []
    requirements: Optional[str] = None

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available CloudFormation generation tools"""
    return [
        Tool(
            name="generate_cloudformation_template",
            description="Generate CloudFormation template for AWS infrastructure",
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
    """Handle tool calls for CloudFormation generation"""
    
    try:
        if name == "generate_cloudformation_template":
            result = await generate_cloudformation_template(arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}")
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

async def generate_cloudformation_template(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Generate CloudFormation template based on project requirements"""
    
    project_info = ProjectInfo(**arguments["project_info"])
    agent_response = arguments.get("agent_response", "")
    
    logger.info(f"Generating CloudFormation template for: {project_info.name}")
    
    # Generate template based on solution type
    if project_info.solution_type == 'rapid_service':
        template = _generate_rapid_service_template(project_info)
    else:
        template = _generate_integral_solution_template(project_info)
    
    # Convert to YAML
    yaml_content = yaml.dump(template, default_flow_style=False, indent=2)
    
    filename = f"{project_info.name.replace(' ', '_')}_CloudFormation_Template.yaml"
    
    return {
        "filename": filename,
        "content": yaml_content,
        "template_dict": template,
        "generated_at": datetime.now().isoformat(),
        "description": f"CloudFormation template for {project_info.name}"
    }

def _generate_rapid_service_template(project_info: ProjectInfo) -> Dict[str, Any]:
    """Generate template for rapid services"""
    
    project_name = project_info.name.replace(' ', '')
    
    template = {
        'AWSTemplateFormatVersion': '2010-09-09',
        'Description': f'CloudFormation template for {project_name} - Rapid Service',
        'Parameters': {
            'Environment': {
                'Type': 'String',
                'Default': 'prod',
                'AllowedValues': ['dev', 'staging', 'prod'],
                'Description': 'Environment name'
            },
            'ProjectName': {
                'Type': 'String',
                'Default': project_name,
                'Description': 'Name of the project'
            }
        },
        'Resources': {},
        'Outputs': {}
    }
    
    # Add VPC resources (always needed)
    template['Resources'].update(_generate_vpc_resources(project_name))
    
    # Add service-specific resources
    for service in project_info.selected_services:
        if service == 'EC2':
            template['Resources'].update(_generate_ec2_resources(project_name))
        elif service == 'RDS':
            template['Resources'].update(_generate_rds_resources(project_name))
        elif service == 'S3':
            template['Resources'].update(_generate_s3_resources(project_name))
        elif service == 'ELB':
            template['Resources'].update(_generate_elb_resources(project_name))
        elif service == 'CloudFront':
            template['Resources'].update(_generate_cloudfront_resources(project_name))
    
    # Generate outputs
    template['Outputs'] = _generate_outputs(template['Resources'], project_name)
    
    return template

def _generate_integral_solution_template(project_info: ProjectInfo) -> Dict[str, Any]:
    """Generate template for integral solutions"""
    
    project_name = project_info.name.replace(' ', '')
    
    template = {
        'AWSTemplateFormatVersion': '2010-09-09',
        'Description': f'CloudFormation template for {project_name} - Integral Solution',
        'Parameters': {
            'Environment': {
                'Type': 'String',
                'Default': 'prod',
                'AllowedValues': ['dev', 'staging', 'prod'],
                'Description': 'Environment name'
            },
            'ProjectName': {
                'Type': 'String',
                'Default': project_name,
                'Description': 'Name of the project'
            }
        },
        'Resources': {},
        'Outputs': {}
    }
    
    # Add VPC resources
    template['Resources'].update(_generate_vpc_resources(project_name))
    
    # Add solution-specific resources based on detail
    solution_detail = project_info.solution_type_detail or ""
    
    if 'web' in solution_detail.lower() or 'aplicacion' in solution_detail.lower():
        template['Resources'].update(_generate_web_application_resources(project_name))
    elif 'data' in solution_detail.lower() or 'analitica' in solution_detail.lower():
        template['Resources'].update(_generate_data_analytics_resources(project_name))
    elif 'iot' in solution_detail.lower():
        template['Resources'].update(_generate_iot_resources(project_name))
    else:
        template['Resources'].update(_generate_general_enterprise_resources(project_name))
    
    # Generate outputs
    template['Outputs'] = _generate_outputs(template['Resources'], project_name)
    
    return template

def _generate_vpc_resources(project_name: str) -> Dict[str, Any]:
    """Generate VPC and networking resources"""
    return {
        f'{project_name}VPC': {
            'Type': 'AWS::EC2::VPC',
            'Properties': {
                'CidrBlock': '10.0.0.0/16',
                'EnableDnsHostnames': True,
                'EnableDnsSupport': True,
                'Tags': [
                    {'Key': 'Name', 'Value': {'Fn::Sub': '${ProjectName}-VPC'}}
                ]
            }
        },
        f'{project_name}InternetGateway': {
            'Type': 'AWS::EC2::InternetGateway',
            'Properties': {
                'Tags': [
                    {'Key': 'Name', 'Value': {'Fn::Sub': '${ProjectName}-IGW'}}
                ]
            }
        },
        f'{project_name}AttachGateway': {
            'Type': 'AWS::EC2::VPCGatewayAttachment',
            'Properties': {
                'VpcId': {'Ref': f'{project_name}VPC'},
                'InternetGatewayId': {'Ref': f'{project_name}InternetGateway'}
            }
        },
        f'{project_name}PublicSubnet1': {
            'Type': 'AWS::EC2::Subnet',
            'Properties': {
                'VpcId': {'Ref': f'{project_name}VPC'},
                'CidrBlock': '10.0.1.0/24',
                'AvailabilityZone': {'Fn::Select': [0, {'Fn::GetAZs': ''}]},
                'MapPublicIpOnLaunch': True,
                'Tags': [
                    {'Key': 'Name', 'Value': {'Fn::Sub': '${ProjectName}-Public-Subnet-1'}}
                ]
            }
        },
        f'{project_name}PublicSubnet2': {
            'Type': 'AWS::EC2::Subnet',
            'Properties': {
                'VpcId': {'Ref': f'{project_name}VPC'},
                'CidrBlock': '10.0.2.0/24',
                'AvailabilityZone': {'Fn::Select': [1, {'Fn::GetAZs': ''}]},
                'MapPublicIpOnLaunch': True,
                'Tags': [
                    {'Key': 'Name', 'Value': {'Fn::Sub': '${ProjectName}-Public-Subnet-2'}}
                ]
            }
        }
    }

def _generate_ec2_resources(project_name: str) -> Dict[str, Any]:
    """Generate EC2 resources"""
    return {
        f'{project_name}SecurityGroup': {
            'Type': 'AWS::EC2::SecurityGroup',
            'Properties': {
                'GroupDescription': f'Security group for {project_name} EC2 instances',
                'VpcId': {'Ref': f'{project_name}VPC'},
                'SecurityGroupIngress': [
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 80,
                        'ToPort': 80,
                        'CidrIp': '0.0.0.0/0'
                    },
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 443,
                        'ToPort': 443,
                        'CidrIp': '0.0.0.0/0'
                    }
                ],
                'Tags': [
                    {'Key': 'Name', 'Value': {'Fn::Sub': '${ProjectName}-SG'}}
                ]
            }
        },
        f'{project_name}LaunchTemplate': {
            'Type': 'AWS::EC2::LaunchTemplate',
            'Properties': {
                'LaunchTemplateName': {'Fn::Sub': '${ProjectName}-LaunchTemplate'},
                'LaunchTemplateData': {
                    'ImageId': 'ami-0c02fb55956c7d316',  # Amazon Linux 2
                    'InstanceType': 't3.micro',
                    'SecurityGroupIds': [{'Ref': f'{project_name}SecurityGroup'}],
                    'UserData': {
                        'Fn::Base64': {
                            'Fn::Sub': '''#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
echo "<h1>Welcome to ${ProjectName}</h1>" > /var/www/html/index.html
'''
                        }
                    }
                }
            }
        }
    }

def _generate_rds_resources(project_name: str) -> Dict[str, Any]:
    """Generate RDS resources"""
    return {
        f'{project_name}DBSubnetGroup': {
            'Type': 'AWS::RDS::DBSubnetGroup',
            'Properties': {
                'DBSubnetGroupDescription': f'Subnet group for {project_name} database',
                'SubnetIds': [
                    {'Ref': f'{project_name}PublicSubnet1'},
                    {'Ref': f'{project_name}PublicSubnet2'}
                ]
            }
        },
        f'{project_name}Database': {
            'Type': 'AWS::RDS::DBInstance',
            'Properties': {
                'DBInstanceIdentifier': {'Fn::Sub': '${ProjectName}-database'},
                'DBInstanceClass': 'db.t3.micro',
                'Engine': 'mysql',
                'AllocatedStorage': 20,
                'DBSubnetGroupName': {'Ref': f'{project_name}DBSubnetGroup'},
                'MasterUsername': 'admin',
                'MasterUserPassword': {'Fn::Sub': '${ProjectName}Password123!'}
            }
        }
    }

def _generate_s3_resources(project_name: str) -> Dict[str, Any]:
    """Generate S3 resources"""
    return {
        f'{project_name}S3Bucket': {
            'Type': 'AWS::S3::Bucket',
            'Properties': {
                'BucketName': {'Fn::Sub': '${ProjectName}-${Environment}-${AWS::AccountId}'},
                'VersioningConfiguration': {
                    'Status': 'Enabled'
                },
                'BucketEncryption': {
                    'ServerSideEncryptionConfiguration': [
                        {
                            'ServerSideEncryptionByDefault': {
                                'SSEAlgorithm': 'AES256'
                            }
                        }
                    ]
                }
            }
        }
    }

def _generate_elb_resources(project_name: str) -> Dict[str, Any]:
    """Generate ELB resources"""
    return {
        f'{project_name}ALB': {
            'Type': 'AWS::ElasticLoadBalancingV2::LoadBalancer',
            'Properties': {
                'Name': {'Fn::Sub': '${ProjectName}-ALB'},
                'Scheme': 'internet-facing',
                'Type': 'application',
                'Subnets': [
                    {'Ref': f'{project_name}PublicSubnet1'},
                    {'Ref': f'{project_name}PublicSubnet2'}
                ]
            }
        }
    }

def _generate_cloudfront_resources(project_name: str) -> Dict[str, Any]:
    """Generate CloudFront resources"""
    return {
        f'{project_name}CloudFrontDistribution': {
            'Type': 'AWS::CloudFront::Distribution',
            'Properties': {
                'DistributionConfig': {
                    'Origins': [
                        {
                            'Id': 'S3Origin',
                            'DomainName': {'Fn::GetAtt': [f'{project_name}S3Bucket', 'DomainName']},
                            'S3OriginConfig': {
                                'OriginAccessIdentity': ''
                            }
                        }
                    ],
                    'DefaultCacheBehavior': {
                        'TargetOriginId': 'S3Origin',
                        'ViewerProtocolPolicy': 'redirect-to-https'
                    },
                    'Enabled': True
                }
            }
        }
    }

def _generate_web_application_resources(project_name: str) -> Dict[str, Any]:
    """Generate resources for web applications"""
    resources = {}
    resources.update(_generate_ec2_resources(project_name))
    resources.update(_generate_rds_resources(project_name))
    resources.update(_generate_s3_resources(project_name))
    resources.update(_generate_elb_resources(project_name))
    return resources

def _generate_data_analytics_resources(project_name: str) -> Dict[str, Any]:
    """Generate resources for data analytics"""
    return {
        f'{project_name}DataLakeS3': {
            'Type': 'AWS::S3::Bucket',
            'Properties': {
                'BucketName': {'Fn::Sub': '${ProjectName}-datalake-${Environment}-${AWS::AccountId}'},
                'VersioningConfiguration': {'Status': 'Enabled'}
            }
        }
    }

def _generate_iot_resources(project_name: str) -> Dict[str, Any]:
    """Generate resources for IoT solutions"""
    return {
        f'{project_name}IoTThing': {
            'Type': 'AWS::IoT::Thing',
            'Properties': {
                'ThingName': {'Fn::Sub': '${ProjectName}-IoT-Device'}
            }
        }
    }

def _generate_general_enterprise_resources(project_name: str) -> Dict[str, Any]:
    """Generate general enterprise resources"""
    resources = {}
    resources.update(_generate_ec2_resources(project_name))
    resources.update(_generate_rds_resources(project_name))
    resources.update(_generate_s3_resources(project_name))
    return resources

def _generate_outputs(resources: Dict[str, Any], project_name: str) -> Dict[str, Any]:
    """Generate CloudFormation outputs"""
    outputs = {}
    
    if f'{project_name}VPC' in resources:
        outputs['VPCId'] = {
            'Description': 'VPC ID',
            'Value': {'Ref': f'{project_name}VPC'}
        }
    
    if f'{project_name}S3Bucket' in resources:
        outputs['S3BucketName'] = {
            'Description': 'S3 bucket name',
            'Value': {'Ref': f'{project_name}S3Bucket'}
        }
    
    return outputs

async def main():
    """Main function to run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="aws-cloudformation-generator",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
