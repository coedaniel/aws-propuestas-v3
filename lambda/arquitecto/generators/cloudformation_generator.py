"""
Legacy CloudFormation generator - DEPRECATED
Use dynamic_generator.py instead for intelligent document generation
"""

def generate_cloudformation_template(service_type, project_info):
    """
    DEPRECATED: Use generate_dynamic_cloudformation from dynamic_generator.py
    This function is kept for backward compatibility only
    """
    return """
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Legacy template - use dynamic generator instead'
Resources:
  PlaceholderResource:
    Type: AWS::CloudFormation::WaitConditionHandle
    Properties: {}
Outputs:
  Message:
    Description: 'Use dynamic generator for intelligent templates'
    Value: 'This is a placeholder template'
"""
