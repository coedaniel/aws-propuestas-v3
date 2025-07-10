import json
import os
from datetime import datetime

def lambda_handler(event, context):
    """
    Health check endpoint for AWS Propuestas v3
    """
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
        },
        'body': json.dumps({
            'status': 'healthy',
            'service': 'AWS Propuestas v3',
            'version': '3.0.0',
            'timestamp': datetime.utcnow().isoformat(),
            'environment': os.environ.get('ENVIRONMENT', 'unknown'),
            'region': os.environ.get('REGION', 'unknown'),
            'message': 'Sistema conversacional profesional funcionando correctamente'
        })
    }
