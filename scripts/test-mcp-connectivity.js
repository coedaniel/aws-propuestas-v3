#!/usr/bin/env node

// Test script to verify MCP servers connectivity
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

async function testEndpoint(name, url) {
  return new Promise((resolve) => {
    const urlObj = new URL(url)
    const client = urlObj.protocol === 'https:' ? https : http
    
    const req = client.request({
      hostname: urlObj.hostname,
      port: urlObj.port,
      path: urlObj.pathname + '/health',
      method: 'GET',
      timeout: 5000
    }, (res) => {
      let data = ''
      res.on('data', chunk => data += chunk)
      res.on('end', () => {
        resolve({
          name,
          url,
          status: res.statusCode,
          healthy: res.statusCode >= 200 && res.statusCode < 300,
          response: data
        })
      })
    })

    req.on('error', (error) => {
      resolve({
        name,
        url,
        status: 0,
        healthy: false,
        error: error.message
      })
    })

    req.on('timeout', () => {
      req.destroy()
      resolve({
        name,
        url,
        status: 0,
        healthy: false,
        error: 'Timeout'
      })
    })

    req.end()
  })
}

async function testAllEndpoints() {
  console.log('🔍 Testing MCP Server Connectivity...\n')
  
  const results = []
  
  for (const [name, url] of Object.entries(MCP_ENDPOINTS)) {
    process.stdout.write(`Testing ${name}... `)
    const result = await testEndpoint(name, url)
    results.push(result)
    
    if (result.healthy) {
      console.log('✅ Healthy')
    } else {
      console.log(`❌ Failed (${result.error || `HTTP ${result.status}`})`)
    }
  }
  
  console.log('\n📊 Summary:')
  console.log('=' * 50)
  
  const healthy = results.filter(r => r.healthy).length
  const total = results.length
  
  console.log(`Healthy servers: ${healthy}/${total}`)
  console.log(`Overall status: ${healthy === total ? '✅ All systems operational' : '⚠️  Some systems degraded'}`)
  
  if (healthy < total) {
    console.log('\n❌ Failed servers:')
    results.filter(r => !r.healthy).forEach(r => {
      console.log(`  - ${r.name}: ${r.error || `HTTP ${r.status}`}`)
    })
  }
  
  console.log('\n🔗 Endpoints:')
  results.forEach(r => {
    console.log(`  ${r.healthy ? '✅' : '❌'} ${r.name}: ${r.url}`)
  })
}

// Test MCP connectivity with sample request
async function testMCPRequest() {
  console.log('\n🧪 Testing MCP Request...')
  
  const testRequest = {
    method: 'tools/list',
    params: {}
  }
  
  try {
    const response = await fetch(MCP_ENDPOINTS['Core MCP'], {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(testRequest),
    })
    
    if (response.ok) {
      const data = await response.json()
      console.log('✅ MCP Request successful')
      console.log('Sample response:', JSON.stringify(data, null, 2).substring(0, 200) + '...')
    } else {
      console.log(`❌ MCP Request failed: HTTP ${response.status}`)
    }
  } catch (error) {
    console.log(`❌ MCP Request failed: ${error.message}`)
  }
}

// Main execution
async function main() {
  await testAllEndpoints()
  
  // Only test MCP request if at least one server is healthy
  const coreHealthy = await testEndpoint('Core MCP', MCP_ENDPOINTS['Core MCP'])
  if (coreHealthy.healthy) {
    await testMCPRequest()
  }
  
  console.log('\n✨ Test completed!')
}

main().catch(console.error)
