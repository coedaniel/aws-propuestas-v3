// MCP Proxy API Route - Solves Mixed Content issues
// This proxy allows HTTPS frontend to communicate with HTTP MCP servers

import { NextRequest, NextResponse } from 'next/server'

const MCP_BASE_URL = 'https://mcp.danielingram.shop'

const MCP_ENDPOINTS = {
  core: `${MCP_BASE_URL}/core`,
  pricing: `${MCP_BASE_URL}/pricing`,
  awsdocs: `${MCP_BASE_URL}/awsdocs`,
  cfn: `${MCP_BASE_URL}/cfn`,
  diagram: `${MCP_BASE_URL}/diagram`,
  docgen: `${MCP_BASE_URL}/docgen`,
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const service = searchParams.get('service')
  const endpoint = searchParams.get('endpoint') || 'health'

  if (!service || !MCP_ENDPOINTS[service as keyof typeof MCP_ENDPOINTS]) {
    return NextResponse.json({ error: 'Invalid service' }, { status: 400 })
  }

  try {
    const mcpUrl = `${MCP_ENDPOINTS[service as keyof typeof MCP_ENDPOINTS]}/${endpoint}`
    const response = await fetch(mcpUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    const data = await response.json()
    
    return NextResponse.json(data, { 
      status: response.status,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
      }
    })
  } catch (error) {
    console.error(`MCP Proxy Error for ${service}:`, error)
    return NextResponse.json(
      { error: 'MCP service unavailable', service },
      { status: 503 }
    )
  }
}

export async function POST(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const service = searchParams.get('service')
  const endpoint = searchParams.get('endpoint') || 'call-tool'

  if (!service || !MCP_ENDPOINTS[service as keyof typeof MCP_ENDPOINTS]) {
    return NextResponse.json({ error: 'Invalid service' }, { status: 400 })
  }

  try {
    const body = await request.json()
    const mcpUrl = `${MCP_ENDPOINTS[service as keyof typeof MCP_ENDPOINTS]}/${endpoint}`
    
    const response = await fetch(mcpUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })

    const data = await response.json()
    
    return NextResponse.json(data, { 
      status: response.status,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
      }
    })
  } catch (error) {
    console.error(`MCP Proxy Error for ${service}:`, error)
    return NextResponse.json(
      { error: 'MCP service unavailable', service },
      { status: 503 }
    )
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  })
}
