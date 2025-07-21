"""
AWS Propuestas v3 - Arquitecto Lambda SIMPLIFIED for debugging
"""

import json
import boto3
import os
import logging
from datetime import datetime

# Import our CORS handler
from cors_handler import handle_preflight_request, create_response, create_error_response, create_success_response

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ.get('REGION', 'us-east-1'))

def lambda_handler(event, context):
    """Simplified Lambda handler for debugging"""
    
    try:
        logger.info(f"Event received: {json.dumps(event)}")
        
        # Handle CORS preflight requests
        if event.get('httpMethod') == 'OPTIONS':
            logger.info("Handling OPTIONS preflight request")
            return handle_preflight_request()
        
        # Parse request
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        messages = body.get('messages', [])
        model_id = body.get('modelId', 'anthropic.claude-3-5-sonnet-20241022-v2:0')
        
        if not messages:
            logger.error("No messages provided")
            return create_error_response(400, 'No messages provided')
        
        logger.info(f"Processing {len(messages)} messages")
        
        # Simple response without MCP for now
        response_data = {
            'content': 'Hola! Soy el arquitecto de AWS. Para comenzar, necesito que me digas: ¿Cual es el nombre del proyecto?',
            'projectState': {
                'phase': 'inicio',
                'data': {
                    'timestamp': datetime.now().isoformat()
                }
            },
            'mcpActivated': False,
            'debug': 'Simplified version - MCP disabled for debugging'
        }
        
        logger.info("Returning successful response")
        return create_success_response(response_data)
        
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}", exc_info=True)
        return create_error_response(500, f'Internal server error: {str(e)}')
