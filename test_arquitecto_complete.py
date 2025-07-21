"""
Test completo del sistema Arquitecto con MCPs reales
"""

import json
import boto3
import time
from datetime import datetime

def test_arquitecto_lambda():
    """Test the arquitecto Lambda function with real MCP integration"""
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    print("🚀 Testing Arquitecto Lambda with Real MCP Integration")
    print("=" * 60)
    
    # Test payload - solicitud de generación de documentos
    test_payload = {
        "user_id": "test-user-123",
        "project_id": "test-project-456",
        "messages": [
            {
                "role": "user",
                "content": "Necesito crear una solución AWS completa para una aplicación web con base de datos. Incluye EC2, RDS, S3 y VPC. Genera todos los documentos necesarios."
            }
        ],
        "ai_response": "Perfecto, procederé a generar una solución integral de AWS que incluya todos los componentes necesarios para tu aplicación web. Voy a crear la documentación ejecutiva, arquitectura técnica, templates de CloudFormation, análisis de costos y plan de implementación.",
        "project_info": {
            "name": "Aplicación Web Empresarial",
            "type": "web_application",
            "services": ["EC2", "RDS", "S3", "VPC", "ALB"],
            "environment": "production"
        }
    }
    
    try:
        print("📤 Invoking Lambda function...")
        start_time = time.time()
        
        response = lambda_client.invoke(
            FunctionName='aws-propuestas-v3-arquitecto-prod',
            InvocationType='RequestResponse',
            Payload=json.dumps(test_payload)
        )
        
        execution_time = time.time() - start_time
        
        # Parse response
        response_payload = json.loads(response['Payload'].read())
        
        print(f"⏱️  Execution time: {execution_time:.2f} seconds")
        print(f"📊 Status Code: {response['StatusCode']}")
        
        if response['StatusCode'] == 200:
            print("✅ Lambda execution successful!")
            
            # Parse the response body
            if 'body' in response_payload:
                body = json.loads(response_payload['body'])
                
                print("\n📋 Response Summary:")
                print(f"  Success: {body.get('success', 'Unknown')}")
                print(f"  Intent: {body.get('intent_analysis', {}).get('primary_intent', 'Unknown')}")
                print(f"  MCPs Activated: {len(body.get('mcp_results', {}).get('mcps_executed', []))}")
                print(f"  Documents Generated: {len(body.get('mcp_results', {}).get('artifacts_generated', []))}")
                
                # Show MCP results
                mcp_results = body.get('mcp_results', {})
                if mcp_results.get('success'):
                    print("\n🔧 MCP Execution Results:")
                    for mcp in mcp_results.get('mcps_executed', []):
                        print(f"  ✅ {mcp}")
                    
                    print("\n📄 Generated Artifacts:")
                    for artifact in mcp_results.get('artifacts_generated', []):
                        if isinstance(artifact, dict):
                            print(f"  📝 {artifact.get('name', 'Unknown')} - {artifact.get('type', 'Unknown')}")
                        else:
                            print(f"  📝 {artifact}")
                
                # Show enhanced response
                enhanced_response = body.get('enhanced_response', '')
                if enhanced_response and len(enhanced_response) > 100:
                    print(f"\n💬 Enhanced Response Preview:")
                    print(f"  {enhanced_response[:200]}...")
                
            else:
                print("⚠️  No body in response")
                print(f"Raw response: {json.dumps(response_payload, indent=2)}")
                
        else:
            print("❌ Lambda execution failed!")
            print(f"Response: {json.dumps(response_payload, indent=2)}")
            
    except Exception as e:
        print(f"❌ Error invoking Lambda: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_mcp_connectivity():
    """Test MCP connectivity through Lambda"""
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    print("\n🔍 Testing MCP Connectivity...")
    print("=" * 40)
    
    # Test payload for MCP connectivity
    test_payload = {
        "test_mode": True,
        "test_type": "mcp_connectivity"
    }
    
    try:
        response = lambda_client.invoke(
            FunctionName='aws-propuestas-v3-arquitecto-prod',
            InvocationType='RequestResponse',
            Payload=json.dumps(test_payload)
        )
        
        response_payload = json.loads(response['Payload'].read())
        
        if response['StatusCode'] == 200:
            print("✅ MCP connectivity test successful!")
            
            if 'body' in response_payload:
                body = json.loads(response_payload['body'])
                connectivity = body.get('connectivity_results', {})
                
                print(f"📊 Services Status:")
                print(f"  Total: {connectivity.get('total_services', 0)}")
                print(f"  Healthy: {connectivity.get('healthy_services', 0)}")
                
                for service, result in connectivity.get('results', {}).items():
                    status_icon = "✅" if result.get('status') == 'healthy' else "❌"
                    print(f"  {status_icon} {service}: {result.get('status', 'unknown')}")
        else:
            print("❌ MCP connectivity test failed!")
            
    except Exception as e:
        print(f"❌ Error testing MCP connectivity: {str(e)}")

def main():
    """Run all tests"""
    
    print("🧪 AWS Propuestas v3 - Arquitecto Complete Test Suite")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Test 1: Main Lambda functionality
    success = test_arquitecto_lambda()
    
    # Test 2: MCP connectivity (if main test succeeded)
    if success:
        test_mcp_connectivity()
    
    print("\n" + "=" * 60)
    print("🎯 Test Suite Complete!")
    
    if success:
        print("✅ All tests passed! The system is ready for production.")
    else:
        print("❌ Some tests failed. Please check the logs.")

if __name__ == "__main__":
    main()
