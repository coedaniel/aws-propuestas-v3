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

// API functions
export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  try {
    // Intentar con la API local primero
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    if (response.ok) {
      return response.json()
    }

    // Si falla, intentar con la API externa
    const externalResponse = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    if (!externalResponse.ok) {
      throw new Error(`Chat API error: ${externalResponse.status} ${externalResponse.statusText}`)
    }

    return externalResponse.json()
  } catch (error) {
    console.error('Error sending chat message:', error)
    throw error
  }
}

export async function sendArquitectoRequest(request: ArquitectoRequest): Promise<ArquitectoResponse> {
  try {
    // Intentar con la API local primero
    const response = await fetch('/api/arquitecto', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: request.query || '',
        conversationHistory: request.messages || [],
        selectedModel: request.modelId || request.selected_model || 'amazon.nova-pro-v1:0',
        projectData: request.project_info
      }),
    })

    if (response.ok) {
      const data = await response.json()
      
      // Convertir a formato esperado
      return {
        response: data.response,
        modelId: data.selectedModel || request.modelId || request.selected_model || 'amazon.nova-pro-v1:0',
        mode: 'arquitecto',
        projectId: request.projectId,
        currentStep: 0,
        isComplete: false,
        usage: data.usage,
        mcpServicesUsed: data.mcpServicesUsed || [],
        mcpResults: data.mcpResults || {},
        transparency: data.transparency || null,
        promptUnderstanding: data.promptUnderstanding || null,
        projectInfo: data.projectInfo || null,
        documentsGenerated: data.documentsGenerated || false,
        s3Folder: data.s3Folder || null
      }
    }

    // Si falla, intentar con la API externa
    const externalResponse = await fetch(`${API_BASE_URL}/arquitecto`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    if (!externalResponse.ok) {
      throw new Error(`Arquitecto API error: ${externalResponse.status}`)
    }

    const data = await externalResponse.json()
    
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
  local_api?: boolean
}> {
  const timestamp = new Date().toISOString()
  let legacyApiStatus = false
  let localApiStatus = false

  // Check local API
  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages: [{ role: 'user', content: 'test' }],
        modelId: 'amazon.nova-pro-v1:0'
      }),
    })
    localApiStatus = response.ok
  } catch (error) {
    console.warn('Local API health check failed:', error)
  }

  // Check legacy API
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
    })
    legacyApiStatus = response.ok
  } catch (error) {
    console.warn('Legacy API health check failed:', error)
  }

  const overallStatus = localApiStatus || legacyApiStatus ? 'healthy' : 'unhealthy'

  return {
    status: overallStatus,
    timestamp,
    legacy_api: legacyApiStatus,
    local_api: localApiStatus
  }
}
