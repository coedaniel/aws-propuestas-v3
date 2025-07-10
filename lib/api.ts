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
  name: string
  description: string
  requirements: string[]
  budget?: number
  createdAt: string
}

// API functions
export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
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

  return response.json()
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

// Health check
export async function checkHealth(): Promise<{ status: string; timestamp: string }> {
  const response = await fetch(`${API_BASE_URL}/health`, {
    method: 'GET',
  })

  if (!response.ok) {
    throw new Error(`Health check failed: ${response.status} ${response.statusText}`)
  }

  return response.json()
}
