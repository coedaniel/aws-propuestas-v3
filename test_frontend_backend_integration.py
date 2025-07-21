"""
Test de integración Frontend-Backend para solucionar el problema del reseteo
"""

import json
import requests
import time
from datetime import datetime

def test_frontend_format():
    """Test con el formato exacto que envía el frontend"""
    
    print("🧪 Testing Frontend-Backend Integration")
    print("=" * 50)
    
    # URL de la API (la misma que usa el frontend)
    api_url = "https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod/arquitecto"
    
    # Payload exacto como lo envía el frontend
    frontend_payload = {
        "messages": [
            {
                "id": "test-msg-1",
                "role": "user",
                "content": "Hola, necesito crear una aplicación web en AWS con base de datos",
                "timestamp": datetime.now().isoformat()
            }
        ],
        "modelId": "anthropic.claude-3-haiku-20240307-v1:0",
        "projectPhase": "inicio",
        "currentProject": None
    }
    
    print("📤 Enviando request con formato del frontend...")
    print(f"URL: {api_url}")
    print(f"Payload keys: {list(frontend_payload.keys())}")
    
    try:
        start_time = time.time()
        
        response = requests.post(
            api_url,
            json=frontend_payload,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=30
        )
        
        execution_time = time.time() - start_time
        
        print(f"⏱️  Response time: {execution_time:.2f} seconds")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Request successful!")
            
            try:
                response_data = response.json()
                
                print("\n📋 Response Analysis:")
                print(f"  Response keys: {list(response_data.keys())}")
                
                # Check for expected frontend fields
                expected_fields = ['response', 'projectUpdate', 'projectPhase', 'mcpUsed', 'usage']
                missing_fields = []
                
                for field in expected_fields:
                    if field in response_data:
                        print(f"  ✅ {field}: Present")
                    else:
                        print(f"  ❌ {field}: Missing")
                        missing_fields.append(field)
                
                if not missing_fields:
                    print("\n🎉 All expected fields present! Frontend should work correctly.")
                else:
                    print(f"\n⚠️  Missing fields: {missing_fields}")
                
                # Show response preview
                ai_response = response_data.get('response', '')
                if ai_response:
                    print(f"\n💬 AI Response Preview:")
                    print(f"  {ai_response[:200]}...")
                
                # Show MCP usage
                mcp_used = response_data.get('mcpUsed', [])
                if mcp_used:
                    print(f"\n🔧 MCPs Used: {mcp_used}")
                
                return True
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {str(e)}")
                print(f"Raw response: {response.text[:500]}...")
                return False
                
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {str(e)}")
        return False

def test_conversation_flow():
    """Test a complete conversation flow"""
    
    print("\n🔄 Testing Conversation Flow")
    print("=" * 30)
    
    api_url = "https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod/arquitecto"
    
    # Simulate a conversation
    conversation_steps = [
        {
            "messages": [
                {
                    "id": "msg-1",
                    "role": "user", 
                    "content": "Hola, necesito ayuda con un proyecto AWS",
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "expected_phase": "inicio"
        },
        {
            "messages": [
                {
                    "id": "msg-1",
                    "role": "user",
                    "content": "Hola, necesito ayuda con un proyecto AWS",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "id": "msg-2", 
                    "role": "assistant",
                    "content": "¡Hola! Soy tu Arquitecto IA especializado en AWS. ¿Cuál es el nombre del proyecto que vamos a arquitectar?",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "id": "msg-3",
                    "role": "user",
                    "content": "El proyecto se llama 'Sistema de Gestión Empresarial'",
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "expected_phase": "recopilacion"
        }
    ]
    
    project_state = None
    
    for i, step in enumerate(conversation_steps, 1):
        print(f"\n📝 Step {i}: Testing conversation continuation...")
        
        payload = {
            "messages": step["messages"],
            "modelId": "anthropic.claude-3-haiku-20240307-v1:0",
            "projectPhase": "inicio" if i == 1 else "recopilacion",
            "currentProject": project_state
        }
        
        try:
            response = requests.post(api_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                project_state = data.get('projectUpdate')
                
                print(f"  ✅ Step {i} successful")
                print(f"  📊 Project state updated: {project_state is not None}")
                
                if data.get('response'):
                    print(f"  💬 Response length: {len(data['response'])} chars")
                
            else:
                print(f"  ❌ Step {i} failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ Step {i} error: {str(e)}")
            return False
    
    print("\n✅ Conversation flow test completed successfully!")
    return True

def main():
    """Run integration tests"""
    
    print("🧪 AWS Propuestas v3 - Frontend-Backend Integration Test")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Test 1: Frontend format compatibility
    test1_success = test_frontend_format()
    
    # Test 2: Conversation flow (only if test 1 passed)
    test2_success = True
    if test1_success:
        test2_success = test_conversation_flow()
    
    print("\n" + "=" * 60)
    print("🎯 Integration Test Results:")
    
    if test1_success and test2_success:
        print("✅ ALL TESTS PASSED!")
        print("🎉 The frontend reset issue should be resolved!")
        print("\n📋 Next steps:")
        print("  1. Deploy the updated Lambda")
        print("  2. Test the frontend in browser")
        print("  3. Verify MCP integration is working")
    else:
        print("❌ Some tests failed.")
        print("🔧 Please check the Lambda logs and fix any issues.")

if __name__ == "__main__":
    main()
