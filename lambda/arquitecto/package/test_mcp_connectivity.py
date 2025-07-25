"""
Test MCP Connectivity - Standalone script to test MCP services
"""

import json
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp_orchestrator import MCPOrchestrator

def test_mcp_services():
    """Test all MCP services connectivity"""
    
    print("🔍 Testing MCP Services Connectivity...")
    print("=" * 50)
    
    # Initialize orchestrator
    orchestrator = MCPOrchestrator()
    
    # Get MCP status
    print("\n📊 MCP Services Status:")
    status = orchestrator.get_mcp_status()
    
    print(f"Total Services: {status['summary']['total']}")
    print(f"Real ECS Services: {status['summary']['real_services']}")
    print(f"Fallback Services: {status['summary']['fallback_services']}")
    print(f"Active Services: {status['summary']['active']}")
    
    print("\n🔧 Service Details:")
    for service_name, service_info in status['services'].items():
        if service_info['type'] == 'real_ecs_service':
            print(f"  ✅ {service_name}: Port {service_info['port']} - {service_info['target_group']}")
        else:
            print(f"  🔄 {service_name}: Fallback - {service_info['server']}")
    
    # Test connectivity
    print("\n🌐 Testing Connectivity...")
    connectivity = orchestrator.test_mcp_connectivity()
    
    print(f"Healthy Services: {connectivity['healthy_services']}/{connectivity['total_services']}")
    
    for service_name, result in connectivity['results'].items():
        status_icon = "✅" if result['status'] == 'healthy' else "❌"
        print(f"  {status_icon} {service_name}: {result['status']}")
        if result.get('endpoint'):
            print(f"      Endpoint: {result['endpoint']}")
        if result.get('error'):
            print(f"      Error: {result['error']}")
        if result.get('response_time'):
            print(f"      Response Time: {result['response_time']:.3f}s")
    
    # Test a sample MCP call
    print("\n🧪 Testing Sample MCP Calls...")
    
    # Test Core MCP
    print("\n  Testing Core MCP...")
    core_result = orchestrator._call_real_mcp_service('core', 'analyze', {
        'text': 'Generate architecture documentation for AWS project'
    })
    
    if core_result['success']:
        print("    ✅ Core MCP responded successfully")
        if core_result.get('simulated'):
            print("    ⚠️  Using simulated response")
    else:
        print(f"    ❌ Core MCP failed: {core_result.get('error')}")
    
    # Test Pricing MCP
    print("\n  Testing Pricing MCP...")
    pricing_result = orchestrator._call_real_mcp_service('aws_pricing', 'estimate', {
        'services': ['EC2', 'S3', 'RDS']
    })
    
    if pricing_result['success']:
        print("    ✅ Pricing MCP responded successfully")
        if pricing_result.get('simulated'):
            print("    ⚠️  Using simulated response")
    else:
        print(f"    ❌ Pricing MCP failed: {pricing_result.get('error')}")
    
    print("\n" + "=" * 50)
    print("🎯 MCP Connectivity Test Complete!")
    
    return {
        'status': status,
        'connectivity': connectivity,
        'sample_calls': {
            'core': core_result,
            'pricing': pricing_result
        }
    }

if __name__ == "__main__":
    try:
        results = test_mcp_services()
        
        # Save results to file
        with open('/tmp/mcp_test_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📄 Results saved to: /tmp/mcp_test_results.json")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
