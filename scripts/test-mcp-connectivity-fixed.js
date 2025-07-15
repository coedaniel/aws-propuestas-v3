#!/usr/bin/env node

// Test script to verify MCP servers connectivity with correct paths
const https = require('https')
const http = require('http')

const MCP_ENDPOINTS = {
  'Core MCP': 'http://aws-propuestas-v3-alb-prod-297472567.us-east-1.elb.amazonaws.com/core',
  'Pricing MCP': 'http://aws-propuestas-v3-alb-prod-297472567.us-east-1.elb.amazonaws.com/pricing',
  'AWS Docs MCP': 'http://aws-propuestas-v3-alb-prod-297472567.us-east-1.elb.amazonaws.com/awsdocs',
  'CloudFormation MCP': 'http://aws-propuestas-v3-alb-prod-297472567.us-east-1.elb.amazonaws.com/cfn',
  'Diagram MCP': 'http://aws-propuestas-v3-alb-prod-297472567.us-east-1.elb.amazonaws.com/diagram',
  'Document Generator MCP': 'http://aws-propuestas-v3-alb-prod-297472567.us-east-1.elb.amazonaws.com/docgen'
}

async function testEndpoint(name, url, path = '/health') {
  return new Promise((resolve) => {
    const urlObj = new URL(url + path)
    const client = urlObj.protocol === 'https:' ? https : http
    
    const req = client.request({
      hostname: urlObj.hostname,
      port: urlObj.port,
      path: urlObj.pathname,
      method: 'GET',
      timeout: 10000
    }, (res) => {
      let data = ''
      res.on('data', chunk => data += chunk)
      res.on('end', () => {
        resolve({
          name,
          url: url + path,
          status: res.statusCode,
          healthy: res.statusCode >= 200 && res.statusCode < 300,
          response: data.substring(0, 200) // Limit response length
        })
      })
    })

    req.on('error', (error) => {
      resolve({
        name,
        url: url + path,
        status: 0,
        healthy: false,
        error: error.message
      })
    })

    req.on('timeout', () => {
      req.destroy()
      resolve({
        name,
        url: url + path,
        status: 0,
        healthy: false,
        error: 'Timeout'
      })
    })

    req.end()
  })
}

async function testAllEndpoints() {
  console.log('🔍 Testing MCP Server Connectivity (Updated Wrappers)...\n')
  
  const results = []
  
  // Test health endpoints
  console.log('📋 Testing Health Endpoints:')
  for (const [name, url] of Object.entries(MCP_ENDPOINTS)) {
    process.stdout.write(`  ${name}... `)
    const result = await testEndpoint(name, url, '/health')
    results.push(result)
    
    if (result.healthy) {
      console.log('✅ Healthy')
    } else {
      console.log(`❌ Failed (${result.error || `HTTP ${result.status}`})`)
    }
  }
  
  console.log('\n📋 Testing Root Endpoints:')
  for (const [name, url] of Object.entries(MCP_ENDPOINTS)) {
    process.stdout.write(`  ${name} root... `)
    const result = await testEndpoint(name + ' Root', url, '/')
    
    if (result.healthy) {
      console.log('✅ Healthy')
    } else {
      console.log(`❌ Failed (${result.error || `HTTP ${result.status}`})`)
    }
  }
  
  console.log('\n📊 Summary:')
  console.log('='.repeat(50))
  
  const healthy = results.filter(r => r.healthy).length
  const total = results.length
  
  console.log(`Healthy endpoints: ${healthy}/${total}`)
  console.log(`Overall status: ${healthy === total ? '✅ All systems operational' : healthy > 0 ? '⚠️  Some systems healthy' : '❌ All systems down'}`)
  
  if (healthy < total) {
    console.log('\n❌ Failed endpoints:')
    results.filter(r => !r.healthy).forEach(r => {
      console.log(`  - ${r.name}: ${r.error || `HTTP ${r.status}`}`)
    })
  }
  
  if (healthy > 0) {
    console.log('\n✅ Working endpoints:')
    results.filter(r => r.healthy).forEach(r => {
      console.log(`  - ${r.name}: ${r.url}`)
    })
  }
}

// Test MCP functionality
async function testMCPFunctionality() {
  console.log('\n🧪 Testing MCP Functionality...')
  
  // Test tools endpoint
  const coreUrl = MCP_ENDPOINTS['Core MCP']
  
  try {
    console.log('Testing /tools endpoint...')
    const toolsResult = await testEndpoint('Core MCP Tools', coreUrl, '/tools')
    
    if (toolsResult.healthy) {
      console.log('✅ Tools endpoint working')
      console.log('Response preview:', toolsResult.response.substring(0, 100) + '...')
    } else {
      console.log('❌ Tools endpoint failed')
    }
  } catch (error) {
    console.log(`❌ Tools test failed: ${error.message}`)
  }
}

// Main execution
async function main() {
  await testAllEndpoints()
  await testMCPFunctionality()
  
  console.log('\n✨ Test completed!')
  console.log('\n📝 Next steps if services are healthy:')
  console.log('1. Update frontend to use these endpoints')
  console.log('2. Test integration with Amplify')
  console.log('3. Deploy frontend updates')
}

main().catch(console.error)
