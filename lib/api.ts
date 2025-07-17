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
  documentsGenerated?: boolean
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
  api_status?: boolean
}> {
  const timestamp = new Date().toISOString()
  let apiStatus = false

  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
    })
    apiStatus = response.ok
  } catch (error) {
    console.warn('API health check failed:', error)
  }

  return {
    status: apiStatus ? 'healthy' : 'unhealthy',
    timestamp,
    api_status: apiStatus
  }
}
