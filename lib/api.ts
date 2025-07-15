// API configuration for AWS Propuestas v3
import { mcpClient, type ChatMessage as MCPChatMessage } from './mcp-client'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod'
const USE_MCP_FALLBACK = true // Enable MCP fallback when legacy API fails

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

export interface ChatRequest {
  messages: ChatMessage[]
  modelId?: string
  mode?: string
  selected_model?: string  // Para el selector de modelos duales
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

export interface ArquitectoRequest {
  messages: ChatMessage[]
  modelId?: string
  projectId?: string
  selected_model?: string  // Para el selector de modelos duales
  project_info?: any  // Información del proyecto
  query?: string  // Query del usuario
  session_id?: string  // ID de sesión
}

export interface ArquitectoResponse {
  response: string
  modelId: string
  projectId?: string
  currentStep?: number
  isComplete?: boolean
  usage?: any
}

export interface ProjectRequest {
  name: string
  description: string
  requirements: string[]
  budget?: number
}

export interface ProjectResponse {
  projectId: string
  projectName: string  // API returns projectName, not name
  status: string
  currentStep: string
  createdAt: string
  updatedAt: string
  documentCount: number
  hasDocuments: boolean
  projectInfo: any
  lastMessage: string
}

// API functions
export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  try {
    // Try legacy API first
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
    console.warn('Legacy API failed, trying MCP fallback:', error)
    
    if (USE_MCP_FALLBACK) {
      try {
        // Convert to MCP format and use MCP client
        const mcpMessages: MCPChatMessage[] = request.messages.map(msg => ({
          role: msg.role,
          content: msg.content
        }))
        
        const mcpResponse = await mcpClient.sendChatMessage(mcpMessages, request.modelId)
        
        // Convert MCP response to legacy format
        return {
          response: mcpResponse.response,
          modelId: mcpResponse.modelId,
          mode: mcpResponse.mode || 'chat',
          usage: mcpResponse.usage
        }
      } catch (mcpError) {
        console.error('MCP fallback also failed:', mcpError)
        throw new Error('Both legacy API and MCP servers are unavailable')
      }
    }
    
    throw error
  }
}

export async function sendArquitectoRequest(request: ArquitectoRequest): Promise<ArquitectoResponse> {
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

  return response.json()
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
  
  // Handle the API response structure that includes projects array
  if (data.projects && Array.isArray(data.projects)) {
    return data.projects
  }
  
  // Fallback: if it's already an array, return it directly
  if (Array.isArray(data)) {
    return data
  }
  
  // If neither, return empty array to prevent errors
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
  let mcpServersStatus: { [key: string]: boolean } = {}

  // Check legacy API
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
    })
    legacyApiStatus = response.ok
  } catch (error) {
    console.warn('Legacy API health check failed:', error)
  }

  // Check MCP servers
  try {
    mcpServersStatus = await mcpClient.checkHealth()
  } catch (error) {
    console.warn('MCP servers health check failed:', error)
  }

  // Determine overall status
  const mcpHealthy = Object.values(mcpServersStatus).some(status => status)
  const overallStatus = legacyApiStatus || mcpHealthy ? 'healthy' : 'unhealthy'

  return {
    status: overallStatus,
    timestamp,
    legacy_api: legacyApiStatus,
    mcp_servers: mcpServersStatus
  }
}
