"""
CloudFormation template generator for AWS proposals
"""
import yaml
from typing import Dict, Any, List

def generate_cloudformation_template(project_info: Dict[str, Any]) -> str:
    """
    Generate CloudFormation template based on project information
    
    Args:
        project_info: Dictionary with project information
    
    Returns:
        str: CloudFormation template in YAML format
    """
    project_name = project_info.get('name', 'aws-project').lower().replace(' ', '-')
    service_type = project_info.get('service_type', 'general')
    
    template = {
        'AWSTemplateFormatVersion': '2010-09-09',
        'Description': f'CloudFormation template for {project_info.get("name", "AWS Project")} - {service_type.upper()} service',
        'Parameters': get_parameters_by_service(service_type, project_info),
        'Resources': get_resources_by_service(service_type, project_name, project_info),
        'Outputs': get_outputs_by_service(service_type, project_name)
    }
    
    # Add mappings for EC2 if needed
    if service_type == 'ec2':
        template['Mappings'] = {
            'RegionMap': {
                'us-east-1': {'AMI': 'ami-0c02fb55956c7d316'},
                'us-west-2': {'AMI': 'ami-0c2d3e23f757b5d84'},
                'eu-west-1': {'AMI': 'ami-0c9c942bd7bf113a2'},
                'ap-southeast-1': {'AMI': 'ami-0c802847a7dd848c0'}
            }
        }
    
    # Add additional parameters for EFS if needed
    if service_type == 'efs':
        template['Parameters'].update({
            'VpcId': {
                'Type': 'AWS::EC2::VPC::Id',
                'Description': 'VPC ID where EFS will be created'
            },
            'SubnetId': {
                'Type': 'AWS::EC2::Subnet::Id',
                'Description': 'Subnet ID for EFS mount target'
            }
        })
    
    return yaml.dump(template, default_flow_style=False, allow_unicode=True)

def get_parameters_by_service(service_type: str, project_info: Dict[str, Any]) -> Dict[str, Any]:
    """Get CloudFormation parameters based on specific service type"""
    
    if service_type == 's3':
        return {
            'BucketName': {
                'Type': 'String',
                'Default': project_info.get('bucket_name', f'{project_info.get("name", "project").lower().replace(" ", "-")}-bucket'),
                'Description': 'Name of the S3 bucket'
            },
            'StorageClass': {
                'Type': 'String',
                'Default': project_info.get('storage_type', 'STANDARD'),
                'AllowedValues': ['STANDARD', 'STANDARD_IA', 'GLACIER', 'DEEP_ARCHIVE'],
                'Description': 'S3 storage class'
            },
            'VersioningEnabled': {
                'Type': 'String',
                'Default': 'Enabled' if project_info.get('versioning') == 'enabled' else 'Suspended',
                'AllowedValues': ['Enabled', 'Suspended'],
                'Description': 'Enable versioning for S3 bucket'
            }
        }
    
    elif service_type == 'efs':
        return {
            'PerformanceMode': {
                'Type': 'String',
                'Default': project_info.get('performance_mode', 'generalPurpose'),
                'AllowedValues': ['generalPurpose', 'maxIO'],
                'Description': 'EFS performance mode'
            },
            'ThroughputMode': {
                'Type': 'String',
                'Default': project_info.get('throughput_mode', 'bursting').lower(),
                'AllowedValues': ['bursting', 'provisioned'],
                'Description': 'EFS throughput mode'
            },
            'Encrypted': {
                'Type': 'String',
                'Default': 'true',
                'AllowedValues': ['true', 'false'],
                'Description': 'Enable encryption for EFS'
            }
        }
    
    elif service_type == 'ec2':
        return {
            'InstanceType': {
                'Type': 'String',
                'Default': project_info.get('instance_type', 't2.micro'),
                'Description': 'EC2 instance type'
            },
            'KeyPairName': {
                'Type': 'AWS::EC2::KeyPair::KeyName',
                'Description': 'Name of an existing EC2 KeyPair'
            },
            'VpcId': {
                'Type': 'AWS::EC2::VPC::Id',
                'Description': 'VPC ID where EC2 instance will be launched'
            },
            'SubnetId': {
                'Type': 'AWS::EC2::Subnet::Id',
                'Description': 'Subnet ID where EC2 instance will be launched'
            }
        }
    
    elif service_type == 'lambda':
        return {
            'Runtime': {
                'Type': 'String',
                'Default': project_info.get('runtime', 'python3.9'),
                'Description': 'Lambda function runtime'
            },
            'MemorySize': {
                'Type': 'Number',
                'Default': 128,
                'MinValue': 128,
                'MaxValue': 10240,
                'Description': 'Lambda function memory size'
            },
            'Timeout': {
                'Type': 'Number',
                'Default': 30,
                'MinValue': 1,
                'MaxValue': 900,
                'Description': 'Lambda function timeout'
            }
        }
    
    else:
        # Generic parameters
        return {
            'Environment': {
                'Type': 'String',
                'Default': 'prod',
                'AllowedValues': ['dev', 'staging', 'prod'],
                'Description': 'Environment name'
            }
        }
                'AllowedValues': ['t3.micro', 't3.small', 't3.medium', 't3.large'],
                'Description': 'EC2 instance type'
            },
            'KeyPairName': {
                'Type': 'AWS::EC2::KeyPair::KeyName',
                'Description': 'EC2 Key Pair for SSH access'
            }
        })
    
    if 'data' in project_type.lower() or 'analitica' in project_type.lower():
        base_params.update({
            'RedshiftNodeType': {
                'Type': 'String',
                'Default': 'dc2.large',
                'AllowedValues': ['dc2.large', 'dc2.8xlarge', 'ra3.xlplus', 'ra3.4xlarge'],
                'Description': 'Redshift node type'
            }
        })
    
    return base_params

def get_resources_by_service(service_type: str, project_name: str, project_info: Dict[str, Any]) -> Dict[str, Any]:
    """Get CloudFormation resources based on specific service type"""
    
    if service_type == 's3':
        bucket_name = project_info.get('bucket_name', f'{project_name}-bucket')
        return {
            'S3Bucket': {
                'Type': 'AWS::S3::Bucket',
                'Properties': {
                    'BucketName': {'Ref': 'BucketName'},
                    'VersioningConfiguration': {
                        'Status': {'Ref': 'VersioningEnabled'}
                    },
                    'BucketEncryption': {
                        'ServerSideEncryptionConfiguration': [
                            {
                                'ServerSideEncryptionByDefault': {
                                    'SSEAlgorithm': 'AES256'
                                }
                            }
                        ]
                    },
                    'PublicAccessBlockConfiguration': {
                        'BlockPublicAcls': True,
                        'BlockPublicPolicy': True,
                        'IgnorePublicAcls': True,
                        'RestrictPublicBuckets': True
                    },
                    'Tags': [
                        {'Key': 'Name', 'Value': f'{project_name}-s3-bucket'},
                        {'Key': 'Project', 'Value': project_name}
                    ]
                }
            }
        }
    
    elif service_type == 'efs':
        return {
            'EFSFileSystem': {
                'Type': 'AWS::EFS::FileSystem',
                'Properties': {
                    'PerformanceMode': {'Ref': 'PerformanceMode'},
                    'ThroughputMode': {'Ref': 'ThroughputMode'},
                    'Encrypted': {'Ref': 'Encrypted'},
                    'FileSystemTags': [
                        {'Key': 'Name', 'Value': f'{project_name}-efs'},
                        {'Key': 'Project', 'Value': project_name}
                    ]
                }
            },
            'EFSMountTarget1': {
                'Type': 'AWS::EFS::MountTarget',
                'Properties': {
                    'FileSystemId': {'Ref': 'EFSFileSystem'},
                    'SubnetId': {'Ref': 'SubnetId'},
                    'SecurityGroups': [{'Ref': 'EFSSecurityGroup'}]
                }
            },
            'EFSSecurityGroup': {
                'Type': 'AWS::EC2::SecurityGroup',
                'Properties': {
                    'GroupDescription': f'Security group for {project_name} EFS',
                    'VpcId': {'Ref': 'VpcId'},
                    'SecurityGroupIngress': [
                        {
                            'IpProtocol': 'tcp',
                            'FromPort': 2049,
                            'ToPort': 2049,
                            'CidrIp': '10.0.0.0/16',
                            'Description': 'NFS access from VPC'
                        }
                    ],
                    'Tags': [
                        {'Key': 'Name', 'Value': f'{project_name}-efs-sg'},
                        {'Key': 'Project', 'Value': project_name}
                    ]
                }
            }
        }
    
    elif service_type == 'ec2':
        return {
            'EC2Instance': {
                'Type': 'AWS::EC2::Instance',
                'Properties': {
                    'InstanceType': {'Ref': 'InstanceType'},
                    'KeyName': {'Ref': 'KeyPairName'},
                    'SubnetId': {'Ref': 'SubnetId'},
                    'SecurityGroupIds': [{'Ref': 'EC2SecurityGroup'}],
                    'ImageId': {'Fn::FindInMap': ['RegionMap', {'Ref': 'AWS::Region'}, 'AMI']},
                    'Tags': [
                        {'Key': 'Name', 'Value': f'{project_name}-ec2'},
                        {'Key': 'Project', 'Value': project_name}
                    ]
                }
            },
            'EC2SecurityGroup': {
                'Type': 'AWS::EC2::SecurityGroup',
                'Properties': {
                    'GroupDescription': f'Security group for {project_name} EC2',
                    'VpcId': {'Ref': 'VpcId'},
                    'SecurityGroupIngress': [
                        {
                            'IpProtocol': 'tcp',
                            'FromPort': 22,
                            'ToPort': 22,
                            'CidrIp': '0.0.0.0/0',
                            'Description': 'SSH access'
                        },
                        {
                            'IpProtocol': 'tcp',
                            'FromPort': 80,
                            'ToPort': 80,
                            'CidrIp': '0.0.0.0/0',
                            'Description': 'HTTP access'
                        }
                    ],
                    'Tags': [
                        {'Key': 'Name', 'Value': f'{project_name}-ec2-sg'},
                        {'Key': 'Project', 'Value': project_name}
                    ]
                }
            }
        }
    
    elif service_type == 'lambda':
        return {
            'LambdaFunction': {
                'Type': 'AWS::Lambda::Function',
                'Properties': {
                    'FunctionName': f'{project_name}-function',
                    'Runtime': {'Ref': 'Runtime'},
                    'Handler': 'index.handler',
                    'MemorySize': {'Ref': 'MemorySize'},
                    'Timeout': {'Ref': 'Timeout'},
                    'Role': {'Fn::GetAtt': ['LambdaExecutionRole', 'Arn']},
                    'Code': {
                        'ZipFile': '''
def handler(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }
                        '''
                    },
                    'Tags': [
                        {'Key': 'Name', 'Value': f'{project_name}-lambda'},
                        {'Key': 'Project', 'Value': project_name}
                    ]
                }
            },
            'LambdaExecutionRole': {
                'Type': 'AWS::IAM::Role',
                'Properties': {
                    'AssumeRolePolicyDocument': {
                        'Version': '2012-10-17',
                        'Statement': [
                            {
                                'Effect': 'Allow',
                                'Principal': {'Service': 'lambda.amazonaws.com'},
                                'Action': 'sts:AssumeRole'
                            }
                        ]
                    },
                    'ManagedPolicyArns': [
                        'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
                    ],
                    'Tags': [
                        {'Key': 'Name', 'Value': f'{project_name}-lambda-role'},
                        {'Key': 'Project', 'Value': project_name}
                    ]
                }
            }
        }
    
    else:
        # Generic resources
        return {
            'GenericResource': {
                'Type': 'AWS::CloudFormation::WaitConditionHandle',
                'Properties': {}
            }
        }

def get_outputs_by_service(service_type: str, project_name: str) -> Dict[str, Any]:
    """Get CloudFormation outputs based on specific service type"""
    
    if service_type == 's3':
        return {
            'BucketName': {
                'Description': 'Name of the created S3 bucket',
                'Value': {'Ref': 'S3Bucket'},
                'Export': {'Name': f'{project_name}-bucket-name'}
            },
            'BucketArn': {
                'Description': 'ARN of the created S3 bucket',
                'Value': {'Fn::GetAtt': ['S3Bucket', 'Arn']},
                'Export': {'Name': f'{project_name}-bucket-arn'}
            }
        }
    
    elif service_type == 'efs':
        return {
            'FileSystemId': {
                'Description': 'ID of the created EFS file system',
                'Value': {'Ref': 'EFSFileSystem'},
                'Export': {'Name': f'{project_name}-efs-id'}
            },
            'FileSystemArn': {
                'Description': 'ARN of the created EFS file system',
                'Value': {'Fn::GetAtt': ['EFSFileSystem', 'Arn']},
                'Export': {'Name': f'{project_name}-efs-arn'}
            }
        }
    
    elif service_type == 'ec2':
        return {
            'InstanceId': {
                'Description': 'ID of the created EC2 instance',
                'Value': {'Ref': 'EC2Instance'},
                'Export': {'Name': f'{project_name}-instance-id'}
            },
            'PublicIP': {
                'Description': 'Public IP of the EC2 instance',
                'Value': {'Fn::GetAtt': ['EC2Instance', 'PublicIp']},
                'Export': {'Name': f'{project_name}-public-ip'}
            }
        }
    
    elif service_type == 'lambda':
        return {
            'FunctionName': {
                'Description': 'Name of the created Lambda function',
                'Value': {'Ref': 'LambdaFunction'},
                'Export': {'Name': f'{project_name}-function-name'}
            },
            'FunctionArn': {
                'Description': 'ARN of the created Lambda function',
                'Value': {'Fn::GetAtt': ['LambdaFunction', 'Arn']},
                'Export': {'Name': f'{project_name}-function-arn'}
            }
        }
    
    else:
        return {
            'ProjectName': {
                'Description': 'Name of the project',
                'Value': project_name
            }
        }

def get_vpc_resources(project_name: str) -> Dict[str, Any]:
    """Get VPC and networking resources"""
    return {
        'VPC': {
            'Type': 'AWS::EC2::VPC',
            'Properties': {
                'CidrBlock': {'Ref': 'VpcCidr'},
                'EnableDnsHostnames': True,
                'EnableDnsSupport': True,
                'Tags': [
                    {'Key': 'Name', 'Value': f'{project_name}-vpc'},
                    {'Key': 'Project', 'Value': project_name}
                ]
            }
        },
        'PublicSubnet1': {
            'Type': 'AWS::EC2::Subnet',
            'Properties': {
                'VpcId': {'Ref': 'VPC'},
                'CidrBlock': '10.0.1.0/24',
                'AvailabilityZone': {'Fn::Select': [0, {'Fn::GetAZs': ''}]},
                'MapPublicIpOnLaunch': True,
                'Tags': [
                    {'Key': 'Name', 'Value': f'{project_name}-public-subnet-1'},
                    {'Key': 'Type', 'Value': 'Public'}
                ]
            }
        },
        'PublicSubnet2': {
            'Type': 'AWS::EC2::Subnet',
            'Properties': {
                'VpcId': {'Ref': 'VPC'},
                'CidrBlock': '10.0.2.0/24',
                'AvailabilityZone': {'Fn::Select': [1, {'Fn::GetAZs': ''}]},
                'MapPublicIpOnLaunch': True,
                'Tags': [
                    {'Key': 'Name', 'Value': f'{project_name}-public-subnet-2'},
                    {'Key': 'Type', 'Value': 'Public'}
                ]
            }
        },
        'PrivateSubnet1': {
            'Type': 'AWS::EC2::Subnet',
            'Properties': {
                'VpcId': {'Ref': 'VPC'},
                'CidrBlock': '10.0.3.0/24',
                'AvailabilityZone': {'Fn::Select': [0, {'Fn::GetAZs': ''}]},
                'Tags': [
                    {'Key': 'Name', 'Value': f'{project_name}-private-subnet-1'},
                    {'Key': 'Type', 'Value': 'Private'}
                ]
            }
        },
        'PrivateSubnet2': {
            'Type': 'AWS::EC2::Subnet',
            'Properties': {
                'VpcId': {'Ref': 'VPC'},
                'CidrBlock': '10.0.4.0/24',
                'AvailabilityZone': {'Fn::Select': [1, {'Fn::GetAZs': ''}]},
                'Tags': [
                    {'Key': 'Name', 'Value': f'{project_name}-private-subnet-2'},
                    {'Key': 'Type', 'Value': 'Private'}
                ]
            }
        },
        'InternetGateway': {
            'Type': 'AWS::EC2::InternetGateway',
            'Properties': {
                'Tags': [
                    {'Key': 'Name', 'Value': f'{project_name}-igw'}
                ]
            }
        },
        'AttachGateway': {
            'Type': 'AWS::EC2::VPCGatewayAttachment',
            'Properties': {
                'VpcId': {'Ref': 'VPC'},
                'InternetGatewayId': {'Ref': 'InternetGateway'}
            }
        },
        'PublicRouteTable': {
            'Type': 'AWS::EC2::RouteTable',
            'Properties': {
                'VpcId': {'Ref': 'VPC'},
                'Tags': [
                    {'Key': 'Name', 'Value': f'{project_name}-public-rt'}
                ]
            }
        },
        'PublicRoute': {
            'Type': 'AWS::EC2::Route',
            'DependsOn': 'AttachGateway',
            'Properties': {
                'RouteTableId': {'Ref': 'PublicRouteTable'},
                'DestinationCidrBlock': '0.0.0.0/0',
                'GatewayId': {'Ref': 'InternetGateway'}
            }
        },
        'PublicSubnetRouteTableAssociation1': {
            'Type': 'AWS::EC2::SubnetRouteTableAssociation',
            'Properties': {
                'SubnetId': {'Ref': 'PublicSubnet1'},
                'RouteTableId': {'Ref': 'PublicRouteTable'}
            }
        },
        'PublicSubnetRouteTableAssociation2': {
            'Type': 'AWS::EC2::SubnetRouteTableAssociation',
            'Properties': {
                'SubnetId': {'Ref': 'PublicSubnet2'},
                'RouteTableId': {'Ref': 'PublicRouteTable'}
            }
        }
    }

def get_web_app_resources(project_name: str) -> Dict[str, Any]:
    """Get web application resources"""
    return {
        'WebServerSecurityGroup': {
            'Type': 'AWS::EC2::SecurityGroup',
            'Properties': {
                'GroupDescription': 'Security group for web servers',
                'VpcId': {'Ref': 'VPC'},
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
                    },
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'CidrIp': '10.0.0.0/16'
                    }
                ],
                'Tags': [
                    {'Key': 'Name', 'Value': f'{project_name}-web-sg'}
                ]
            }
        },
        'ApplicationLoadBalancer': {
            'Type': 'AWS::ElasticLoadBalancingV2::LoadBalancer',
            'Properties': {
                'Name': f'{project_name}-alb',
                'Scheme': 'internet-facing',
                'Type': 'application',
                'Subnets': [
                    {'Ref': 'PublicSubnet1'},
                    {'Ref': 'PublicSubnet2'}
                ],
                'SecurityGroups': [{'Ref': 'WebServerSecurityGroup'}],
                'Tags': [
                    {'Key': 'Name', 'Value': f'{project_name}-alb'}
                ]
            }
        },
        'LaunchTemplate': {
            'Type': 'AWS::EC2::LaunchTemplate',
            'Properties': {
                'LaunchTemplateName': f'{project_name}-launch-template',
                'LaunchTemplateData': {
                    'ImageId': 'ami-0c02fb55956c7d316',  # Amazon Linux 2
                    'InstanceType': {'Ref': 'InstanceType'},
                    'KeyName': {'Ref': 'KeyPairName'},
                    'SecurityGroupIds': [{'Ref': 'WebServerSecurityGroup'}],
                    'UserData': {
                        'Fn::Base64': {
                            'Fn::Sub': '''#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
echo "<h1>Welcome to ${AWS::StackName}</h1>" > /var/www/html/index.html
'''
                        }
                    },
                    'TagSpecifications': [
                        {
                            'ResourceType': 'instance',
                            'Tags': [
                                {'Key': 'Name', 'Value': f'{project_name}-web-server'},
                                {'Key': 'Project', 'Value': project_name}
                            ]
                        }
                    ]
                }
            }
        },
        'AutoScalingGroup': {
            'Type': 'AWS::AutoScaling::AutoScalingGroup',
            'Properties': {
                'AutoScalingGroupName': f'{project_name}-asg',
                'LaunchTemplate': {
                    'LaunchTemplateId': {'Ref': 'LaunchTemplate'},
                    'Version': {'Fn::GetAtt': ['LaunchTemplate', 'LatestVersionNumber']}
                },
                'MinSize': '1',
                'MaxSize': '3',
                'DesiredCapacity': '2',
                'VPCZoneIdentifier': [
                    {'Ref': 'PrivateSubnet1'},
                    {'Ref': 'PrivateSubnet2'}
                ],
                'HealthCheckType': 'ELB',
                'HealthCheckGracePeriod': 300,
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': f'{project_name}-asg',
                        'PropagateAtLaunch': False
                    }
                ]
            }
        }
    }

def get_analytics_resources(project_name: str) -> Dict[str, Any]:
    """Get analytics and data resources"""
    return {
        'DataLakeBucket': {
            'Type': 'AWS::S3::Bucket',
            'Properties': {
                'BucketName': f'{project_name}-data-lake-{{"Ref": "AWS::AccountId"}}',
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
                },
                'PublicAccessBlockConfiguration': {
                    'BlockPublicAcls': True,
                    'BlockPublicPolicy': True,
                    'IgnorePublicAcls': True,
                    'RestrictPublicBuckets': True
                }
            }
        },
        'GlueDatabase': {
            'Type': 'AWS::Glue::Database',
            'Properties': {
                'CatalogId': {'Ref': 'AWS::AccountId'},
                'DatabaseInput': {
                    'Name': f'{project_name}_database',
                    'Description': f'Glue database for {project_name} project'
                }
            }
        },
        'RedshiftSubnetGroup': {
            'Type': 'AWS::Redshift::SubnetGroup',
            'Properties': {
                'Description': 'Subnet group for Redshift cluster',
                'SubnetIds': [
                    {'Ref': 'PrivateSubnet1'},
                    {'Ref': 'PrivateSubnet2'}
                ]
            }
        },
        'RedshiftSecurityGroup': {
            'Type': 'AWS::EC2::SecurityGroup',
            'Properties': {
                'GroupDescription': 'Security group for Redshift cluster',
                'VpcId': {'Ref': 'VPC'},
                'SecurityGroupIngress': [
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 5439,
                        'ToPort': 5439,
                        'CidrIp': '10.0.0.0/16'
                    }
                ]
            }
        },
        'RedshiftCluster': {
            'Type': 'AWS::Redshift::Cluster',
            'Properties': {
                'ClusterIdentifier': f'{project_name}-redshift',
                'NodeType': {'Ref': 'RedshiftNodeType'},
                'NumberOfNodes': 2,
                'DBName': 'analytics',
                'MasterUsername': 'admin',
                'MasterUserPassword': 'TempPassword123!',  # Should be parameterized
                'VpcSecurityGroupIds': [{'Ref': 'RedshiftSecurityGroup'}],
                'ClusterSubnetGroupName': {'Ref': 'RedshiftSubnetGroup'},
                'PubliclyAccessible': False,
                'Encrypted': True
            }
        }
    }

def get_iot_resources(project_name: str) -> Dict[str, Any]:
    """Get IoT specific resources"""
    return {
        'IoTPolicy': {
            'Type': 'AWS::IoT::Policy',
            'Properties': {
                'PolicyName': f'{project_name}-iot-policy',
                'PolicyDocument': {
                    'Version': '2012-10-17',
                    'Statement': [
                        {
                            'Effect': 'Allow',
                            'Action': [
                                'iot:Connect',
                                'iot:Publish',
                                'iot:Subscribe',
                                'iot:Receive'
                            ],
                            'Resource': '*'
                        }
                    ]
                }
            }
        },
        'IoTThing': {
            'Type': 'AWS::IoT::Thing',
            'Properties': {
                'ThingName': f'{project_name}-device'
            }
        },
        'IoTTopicRule': {
            'Type': 'AWS::IoT::TopicRule',
            'Properties': {
                'RuleName': f'{project_name.replace("-", "_")}_rule',
                'TopicRulePayload': {
                    'Sql': f"SELECT * FROM 'topic/{project_name}'",
                    'Actions': [
                        {
                            'DynamoDBv2': {
                                'RoleArn': {'Fn::GetAtt': ['IoTRole', 'Arn']},
                                'PutItem': {
                                    'TableName': {'Ref': 'IoTDataTable'}
                                }
                            }
                        }
                    ]
                }
            }
        },
        'IoTDataTable': {
            'Type': 'AWS::DynamoDB::Table',
            'Properties': {
                'TableName': f'{project_name}-iot-data',
                'BillingMode': 'PAY_PER_REQUEST',
                'AttributeDefinitions': [
                    {
                        'AttributeName': 'deviceId',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'timestamp',
                        'AttributeType': 'N'
                    }
                ],
                'KeySchema': [
                    {
                        'AttributeName': 'deviceId',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'timestamp',
                        'KeyType': 'RANGE'
                    }
                ]
            }
        },
        'IoTRole': {
            'Type': 'AWS::IAM::Role',
            'Properties': {
                'AssumeRolePolicyDocument': {
                    'Version': '2012-10-17',
                    'Statement': [
                        {
                            'Effect': 'Allow',
                            'Principal': {
                                'Service': 'iot.amazonaws.com'
                            },
                            'Action': 'sts:AssumeRole'
                        }
                    ]
                },
                'Policies': [
                    {
                        'PolicyName': 'IoTDynamoDBPolicy',
                        'PolicyDocument': {
                            'Version': '2012-10-17',
                            'Statement': [
                                {
                                    'Effect': 'Allow',
                                    'Action': [
                                        'dynamodb:PutItem'
                                    ],
                                    'Resource': {'Fn::GetAtt': ['IoTDataTable', 'Arn']}
                                }
                            ]
                        }
                    }
                ]
            }
        }
    }

def get_migration_resources(project_name: str) -> Dict[str, Any]:
    """Get migration specific resources"""
    return {
        'DMSReplicationInstance': {
            'Type': 'AWS::DMS::ReplicationInstance',
            'Properties': {
                'ReplicationInstanceIdentifier': f'{project_name}-dms',
                'ReplicationInstanceClass': 'dms.t3.micro',
                'AllocatedStorage': 20,
                'VpcSecurityGroupIds': [{'Ref': 'DMSSecurityGroup'}],
                'ReplicationSubnetGroupIdentifier': {'Ref': 'DMSSubnetGroup'}
            }
        },
        'DMSSubnetGroup': {
            'Type': 'AWS::DMS::ReplicationSubnetGroup',
            'Properties': {
                'ReplicationSubnetGroupDescription': 'Subnet group for DMS',
                'SubnetIds': [
                    {'Ref': 'PrivateSubnet1'},
                    {'Ref': 'PrivateSubnet2'}
                ]
            }
        },
        'DMSSecurityGroup': {
            'Type': 'AWS::EC2::SecurityGroup',
            'Properties': {
                'GroupDescription': 'Security group for DMS',
                'VpcId': {'Ref': 'VPC'},
                'SecurityGroupIngress': [
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 3306,
                        'ToPort': 3306,
                        'CidrIp': '10.0.0.0/16'
                    },
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 5432,
                        'ToPort': 5432,
                        'CidrIp': '10.0.0.0/16'
                    }
                ]
            }
        }
    }

def get_security_resources(project_name: str) -> Dict[str, Any]:
    """Get security resources"""
    return {
        'CloudTrail': {
            'Type': 'AWS::CloudTrail::Trail',
            'Properties': {
                'TrailName': f'{project_name}-cloudtrail',
                'S3BucketName': {'Ref': 'CloudTrailBucket'},
                'IncludeGlobalServiceEvents': True,
                'IsMultiRegionTrail': True,
                'EnableLogFileValidation': True
            }
        },
        'CloudTrailBucket': {
            'Type': 'AWS::S3::Bucket',
            'Properties': {
                'BucketName': f'{project_name}-cloudtrail-{{"Ref": "AWS::AccountId"}}',
                'PublicAccessBlockConfiguration': {
                    'BlockPublicAcls': True,
                    'BlockPublicPolicy': True,
                    'IgnorePublicAcls': True,
                    'RestrictPublicBuckets': True
                }
            }
        },
        'GuardDutyDetector': {
            'Type': 'AWS::GuardDuty::Detector',
            'Properties': {
                'Enable': True,
                'FindingPublishingFrequency': 'FIFTEEN_MINUTES'
            }
        }
    }

def get_monitoring_resources(project_name: str) -> Dict[str, Any]:
    """Get monitoring resources"""
    return {
        'SNSAlarmTopic': {
            'Type': 'AWS::SNS::Topic',
            'Properties': {
                'TopicName': f'{project_name}-alarms',
                'DisplayName': f'Alarms for {project_name}'
            }
        },
        'HighCPUAlarm': {
            'Type': 'AWS::CloudWatch::Alarm',
            'Properties': {
                'AlarmName': f'{project_name}-high-cpu',
                'AlarmDescription': 'Alarm for high CPU utilization',
                'MetricName': 'CPUUtilization',
                'Namespace': 'AWS/EC2',
                'Statistic': 'Average',
                'Period': 300,
                'EvaluationPeriods': 2,
                'Threshold': 80,
                'ComparisonOperator': 'GreaterThanThreshold',
                'AlarmActions': [{'Ref': 'SNSAlarmTopic'}]
            }
        }
    }

def get_outputs(project_type: str, project_name: str) -> Dict[str, Any]:
    """Get CloudFormation outputs"""
    outputs = {
        'VPCId': {
            'Description': 'VPC ID',
            'Value': {'Ref': 'VPC'},
            'Export': {
                'Name': f'{project_name}-vpc-id'
            }
        },
        'PublicSubnet1Id': {
            'Description': 'Public Subnet 1 ID',
            'Value': {'Ref': 'PublicSubnet1'},
            'Export': {
                'Name': f'{project_name}-public-subnet-1'
            }
        },
        'PublicSubnet2Id': {
            'Description': 'Public Subnet 2 ID',
            'Value': {'Ref': 'PublicSubnet2'},
            'Export': {
                'Name': f'{project_name}-public-subnet-2'
            }
        }
    }
    
    if 'web' in project_type.lower() or 'app' in project_type.lower():
        outputs.update({
            'LoadBalancerDNS': {
                'Description': 'Application Load Balancer DNS name',
                'Value': {'Fn::GetAtt': ['ApplicationLoadBalancer', 'DNSName']},
                'Export': {
                    'Name': f'{project_name}-alb-dns'
                }
            }
        })
    
    if 'data' in project_type.lower() or 'analitica' in project_type.lower():
        outputs.update({
            'DataLakeBucket': {
                'Description': 'Data Lake S3 Bucket',
                'Value': {'Ref': 'DataLakeBucket'},
                'Export': {
                    'Name': f'{project_name}-data-lake-bucket'
                }
            },
            'RedshiftEndpoint': {
                'Description': 'Redshift cluster endpoint',
                'Value': {'Fn::GetAtt': ['RedshiftCluster', 'Endpoint.Address']},
                'Export': {
                    'Name': f'{project_name}-redshift-endpoint'
                }
            }
        })
    
    return outputs
