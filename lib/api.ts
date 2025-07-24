// API configuration for AWS Propuestas v3
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod'

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
  mcpServicesUsed?: string[]
}

export interface ArquitectoRequest {
  messages: ChatMessage[]
  modelId?: string
  projectId?: string
  selected_model?: string
  project_info?: any
  query?: string
  session_id?: string
}

export interface ArquitectoResponse {
  response: string
  modelId: string
  mode: string
  projectId?: string
  currentStep?: number
  isComplete?: boolean
  documentsGenerated?: Array<{
    name: string
    url: string
    type: string
    size?: number
  }>
  s3Folder?: string
  usage?: {
    inputTokens?: number
    outputTokens?: number
    totalTokens?: number
  }
  mcpServicesUsed?: string[]
  mcpResults?: any
  transparency?: {
    message: string
    services: string[]
  }
  promptUnderstanding?: any
  projectInfo?: any
  projectState?: {
    name?: string
    type?: 'integral' | 'rapido'
    phase: 'inicio' | 'tipo' | 'recopilacion' | 'generacion' | 'entrega'
    data: any
  }
}

export interface ProjectRequest {
  name: string
  description: string
  requirements: string[]
  budget?: number
}

export interface ProjectResponse {
  projectId: string
  projectName: string
  status: string
  currentStep: string
  createdAt: string
  updatedAt: string
  documentCount: number
  hasDocuments: boolean
  projectInfo: any
  lastMessage: string
}

// API functions - usando únicamente la API externa
export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      throw new Error(`Chat API error: ${response.status} ${response.statusText}`)
    }

    return response.json()
  } catch (error) {
    console.error('Error sending chat message:', error)
    throw error
  }
}

export async function sendArquitectoRequest(request: ArquitectoRequest): Promise<ArquitectoResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/arquitecto`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      throw new Error(`Arquitecto API error: ${response.status}`)
    }

    const data = await response.json()
    
    return {
      ...data,
      mode: data.mode || 'arquitecto',
      mcpServicesUsed: data.mcpServicesUsed || [],
      mcpResults: data.mcpResults || {},
      transparency: data.transparency || null,
      promptUnderstanding: data.promptUnderstanding || null
    }
  } catch (error) {
    console.error('Error sending arquitecto request:', error)
    throw error
  }
}

export async function createProject(request: ProjectRequest): Promise<ProjectResponse> {
  const response = await fetch(`${API_BASE_URL}/projects`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    throw new Error(`Projects API error: ${response.status} ${response.statusText}`)
  }

  return response.json()
}

export async function getProjects(): Promise<ProjectResponse[]> {
  const response = await fetch(`${API_BASE_URL}/projects`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error(`Projects API error: ${response.status} ${response.statusText}`)
  }

  const data = await response.json()
  
  if (data.projects && Array.isArray(data.projects)) {
    return data.projects
  }
  
  if (Array.isArray(data)) {
    return data
  }
  
  console.warn('Unexpected API response structure:', data)
  return []
}

export async function generateDocuments(projectId: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/documents`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ projectId }),
  })

  if (!response.ok) {
    throw new Error(`Documents API error: ${response.status} ${response.statusText}`)
  }

  return response.json()
}

export async function deleteProject(projectId: string): Promise<{ success: boolean; message: string; deletedFiles?: number; projectId?: string }> {
  const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error(`Delete project API error: ${response.status} ${response.statusText}`)
  }

  return response.json()
}

// Health check
export async function checkHealth(): Promise<{ 
  status: string
  timestamp: string
  legacy_api?: boolean
  mcp_servers?: { [key: string]: boolean }
}> {
  const timestamp = new Date().toISOString()
  let legacyApiStatus = false
  const mcpServers: { [key: string]: boolean } = {}

  // Check legacy API
  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 5000)
    
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      signal: controller.signal
    })
    
    clearTimeout(timeoutId)
    legacyApiStatus = response.ok
  } catch (error) {
    console.warn('Legacy API health check failed:', error)
  }

  // Check MCP servers
  const mcpServices = [
    { name: 'core', url: process.env.NEXT_PUBLIC_CORE_MCP_URL },
    { name: 'pricing', url: process.env.NEXT_PUBLIC_PRICING_MCP_URL },
    { name: 'awsdocs', url: process.env.NEXT_PUBLIC_AWSDOCS_MCP_URL },
    { name: 'diagram', url: process.env.NEXT_PUBLIC_DIAGRAM_MCP_URL },
    { name: 'cfn', url: process.env.NEXT_PUBLIC_CFN_MCP_URL },
    { name: 'docgen', url: process.env.NEXT_PUBLIC_DOCGEN_MCP_URL }
  ]

  // Check each MCP service
  await Promise.allSettled(
    mcpServices.map(async (service) => {
      if (!service.url) {
        mcpServers[service.name] = false
        return
      }

      try {
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 3000)
        
        const response = await fetch(`${service.url}/health`, {
          method: 'GET',
          signal: controller.signal
        })
        
        clearTimeout(timeoutId)
        mcpServers[service.name] = response.ok
      } catch (error) {
        console.warn(`MCP ${service.name} health check failed:`, error)
        mcpServers[service.name] = false
      }
    })
  )

  // Determine overall status
  const mcpHealthy = Object.values(mcpServers).some(status => status)
  const overallStatus = legacyApiStatus || mcpHealthy ? 'healthy' : 'unhealthy'

  return {
    status: overallStatus,
    timestamp,
    legacy_api: legacyApiStatus,
    mcp_servers: mcpServers
  }
}
