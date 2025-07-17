// MCP Client for AWS Propuestas v3
// This client handles communication with the MCP servers deployed on ECS

interface MCPResponse {
  result?: any
  error?: {
    code: number
    message: string
    data?: any
  }
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

export interface ChatRequest {
  messages: ChatMessage[]
  modelId?: string
  mode?: string
  selected_model?: string
}

export interface ChatResponse {
  response: string
  modelId: string
  mode: string
  usage?: {
    inputTokens?: number
    outputTokens?: number
    totalTokens?: number
  }
}

// MCP Server URLs - Using HTTPS for secure connections
const MCP_URLS = {
  core: process.env.NEXT_PUBLIC_CORE_MCP_URL || 'https://mcp.danielingram.shop/core',
  pricing: process.env.NEXT_PUBLIC_PRICING_MCP_URL || 'https://mcp.danielingram.shop/pricing',
  awsdocs: process.env.NEXT_PUBLIC_AWSDOCS_MCP_URL || 'https://mcp.danielingram.shop/awsdocs',
  cfn: process.env.NEXT_PUBLIC_CFN_MCP_URL || 'https://mcp.danielingram.shop/cfn',
  diagram: process.env.NEXT_PUBLIC_DIAGRAM_MCP_URL || 'https://mcp.danielingram.shop/diagram',
  docgen: process.env.NEXT_PUBLIC_DOCGEN_MCP_URL || 'https://mcp.danielingram.shop/docgen',
}

class MCPClient {

  // Core MCP Server - Main chat functionality
  async sendChatMessage(messages: ChatMessage[], modelId?: string): Promise<ChatResponse> {
    const request = {
      tool: 'chat',
      arguments: {
        messages,
        modelId: modelId || 'anthropic.claude-3-5-sonnet-20240620-v1:0',
      }
    }

    const response = await fetch(`${MCP_URLS.core}?endpoint=call-tool`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      throw new Error(`Core MCP Error: HTTP ${response.status}`)
    }

    const result = await response.json()
    
    if (!result.success) {
      throw new Error(`Core MCP Error: ${result.error}`)
    }

    return result.result
  }

  // Pricing MCP Server - AWS pricing calculations
  async calculatePricing(services: any[]): Promise<any> {
    const request = {
      tool: 'calculate_pricing',
      arguments: { services }
    }

    const response = await fetch(`${MCP_URLS.pricing}?endpoint=call-tool`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      throw new Error(`Pricing MCP Error: HTTP ${response.status}`)
    }

    const result = await response.json()
    
    if (!result.success) {
      throw new Error(`Pricing MCP Error: ${result.error}`)
    }

    return result.result
  }

  // AWS Docs MCP Server - Documentation search
  async searchDocumentation(query: string): Promise<any> {
    const request = {
      tool: 'search_documentation',
      arguments: { query }
    }

    const response = await fetch(`${MCP_URLS.awsdocs}/call-tool`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      throw new Error(`AWS Docs MCP Error: HTTP ${response.status}`)
    }

    const result = await response.json()
    
    if (!result.success) {
      throw new Error(`AWS Docs MCP Error: ${result.error}`)
    }

    return result.result
  }

  // CloudFormation MCP Server - Infrastructure templates
  async generateCloudFormation(requirements: any): Promise<any> {
    const request = {
      tool: 'generate_template',
      arguments: requirements
    }

    const response = await fetch(`${MCP_URLS.cfn}/call-tool`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      throw new Error(`CloudFormation MCP Error: HTTP ${response.status}`)
    }

    const result = await response.json()
    
    if (!result.success) {
      throw new Error(`CloudFormation MCP Error: ${result.error}`)
    }

    return result.result
  }

  // Diagram MCP Server - Architecture diagrams
  async generateDiagram(architecture: any): Promise<any> {
    const request = {
      tool: 'generate_diagram',
      arguments: architecture
    }

    const response = await fetch(`${MCP_URLS.diagram}/call-tool`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      throw new Error(`Diagram MCP Error: HTTP ${response.status}`)
    }

    const result = await response.json()
    
    if (!result.success) {
      throw new Error(`Diagram MCP Error: ${result.error}`)
    }

    return result.result
  }

  // Document Generator MCP Server - Custom documents
  async generateDocument(projectData: any, documentType: string): Promise<any> {
    const request = {
      tool: 'generate_document',
      arguments: {
        projectData,
        documentType
      }
    }

    const response = await fetch(`${MCP_URLS.docgen}/call-tool`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      throw new Error(`Document Generator MCP Error: HTTP ${response.status}`)
    }

    const result = await response.json()
    
    if (!result.success) {
      throw new Error(`Document Generator MCP Error: ${result.error}`)
    }

    return result.result
  }

  // Health check for all MCP servers
  async checkHealth(): Promise<{ [key: string]: boolean }> {
    const healthChecks: { [key: string]: boolean } = {}

    for (const [name, url] of Object.entries(MCP_URLS)) {
      try {
        const response = await fetch(`${url}?endpoint=health`, {
          method: 'GET',
          signal: AbortSignal.timeout(5000),
        })
        healthChecks[name] = response.ok
      } catch (error) {
        console.warn(`Health check failed for ${name}:`, error)
        healthChecks[name] = false
      }
    }

    return healthChecks
  }

  // Get available tools from a specific MCP server
  async getAvailableTools(serverName: keyof typeof MCP_URLS): Promise<any> {
    const response = await fetch(`${MCP_URLS[serverName]}/tools`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`Tools list error for ${serverName}: HTTP ${response.status}`)
    }

    const result = await response.json()
    
    if (!result.success) {
      throw new Error(`Tools list error for ${serverName}: ${result.error}`)
    }

    return result.tools
  }

  // Execute a specific tool on a MCP server
  async executeTool(serverName: keyof typeof MCP_URLS, toolName: string, params: any): Promise<any> {
    const request = {
      tool: toolName,
      arguments: params
    }

    const response = await fetch(`${MCP_URLS[serverName]}/call-tool`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      throw new Error(`Tool execution error: HTTP ${response.status}`)
    }

    const result = await response.json()
    
    if (!result.success) {
      throw new Error(`Tool execution error: ${result.error}`)
    }

    return result.result
  }
}

// Export singleton instance
export const mcpClient = new MCPClient()

// Export utilities
export { MCP_URLS }
