import json
import urllib3
import os
from urllib.parse import urlencode

# Configurar urllib3
http = urllib3.PoolManager()

# URLs base de los MCP servers
MCP_BASE_URL = os.environ.get('MCP_BASE_URL', 'https://mcp.danielingram.shop')

def lambda_handler(event, context):
    """
    Proxy CORS para MCP servers
    """
    
    # Headers CORS
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
        'Access-Control-Max-Age': '86400'
    }
    
    try:
        # Manejar preflight OPTIONS request
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': ''
            }
        
        # Extraer información de la request
        path = event.get('path', '')
        method = event.get('httpMethod', 'GET')
        query_params = event.get('queryStringParameters') or {}
        headers = event.get('headers') or {}
        body = event.get('body')
        
        # Construir URL del MCP server
        # Remover /cors-proxy del path si existe
        if path.startswith('/cors-proxy'):
            path = path[11:]  # Remover '/cors-proxy'
        
        target_url = f"{MCP_BASE_URL}{path}"
        if query_params:
            target_url += '?' + urlencode(query_params)
        
        print(f"Proxying {method} request to: {target_url}")
        
        # Preparar headers para la request upstream
        upstream_headers = {}
        for key, value in headers.items():
            # Filtrar headers que no deben ser enviados upstream
            if key.lower() not in ['host', 'x-forwarded-for', 'x-forwarded-proto', 'x-forwarded-port']:
                upstream_headers[key] = value
        
        # Hacer request al MCP server
        if method == 'GET':
            response = http.request('GET', target_url, headers=upstream_headers)
        elif method == 'POST':
            response = http.request('POST', target_url, body=body, headers=upstream_headers)
        elif method == 'PUT':
            response = http.request('PUT', target_url, body=body, headers=upstream_headers)
        elif method == 'DELETE':
            response = http.request('DELETE', target_url, headers=upstream_headers)
        else:
            return {
                'statusCode': 405,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Method not allowed'})
            }
        
        # Preparar response
        response_headers = cors_headers.copy()
        
        # Copiar algunos headers de la response upstream
        for key, value in response.headers.items():
            if key.lower() in ['content-type', 'cache-control']:
                response_headers[key] = value
        
        return {
            'statusCode': response.status,
            'headers': response_headers,
            'body': response.data.decode('utf-8') if response.data else ''
        }
        
    except Exception as e:
        print(f"Error in CORS proxy: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
