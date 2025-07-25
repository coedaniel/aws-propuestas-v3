"""
AWS Propuestas v3 - Arquitecto Lambda MINIMAL for debugging
"""

import json
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """Minimal Lambda handler for debugging"""
    
    try:
        logger.info(f"Event received: {json.dumps(event)}")
        
        # Handle CORS preflight requests
        if event.get('httpMethod') == 'OPTIONS':
            logger.info("Handling OPTIONS preflight request")
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With, Accept, Origin',
                    'Access-Control-Max-Age': '86400',
                    'Content-Type': 'application/json'
                },
                'body': ''
            }
        
        # Parse request
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        messages = body.get('messages', [])
        
        if not messages:
            logger.error("No messages provided")
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'No messages provided'})
            }
        
        logger.info(f"Processing {len(messages)} messages")
        
        # Simple response
        response_data = {
            'content': 'Hola! Soy el arquitecto de AWS. Para comenzar, necesito que me digas: ¿Cual es el nombre del proyecto?',
            'projectState': {
                'phase': 'inicio',
                'data': {
                    'timestamp': datetime.now().isoformat()
                }
            },
            'debug': 'Minimal version working'
        }
        
        logger.info("Returning successful response")
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps(response_data)
        }
        
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }
