// Definiciones de tipos para AWS Propuestas v3

// Modelos disponibles
export interface Model {
  id: string
  name: string
  provider: string
  description: string
  maxTokens: number
  contextWindow: number
  capabilities: string[]
  icon?: string
  costPer1kTokens?: number
}

// Alias para compatibilidad
export type AIModel = Model

export const AVAILABLE_MODELS: Model[] = [
  {
    id: 'amazon.nova-pro-v1:0',
    name: 'Amazon Nova Pro',
    provider: 'Amazon',
    description: 'Modelo de lenguaje de alta capacidad para tareas complejas',
    maxTokens: 4096,
    contextWindow: 32000,
    capabilities: ['chat', 'arquitecto', 'documentacion'],
    icon: '🤖',
    costPer1kTokens: 0.008
  },
  {
    id: 'anthropic.claude-3-5-sonnet-20241022-v1:0',
    name: 'Claude 3.5 Sonnet',
    provider: 'Anthropic',
    description: 'Modelo de lenguaje avanzado con excelente razonamiento',
    maxTokens: 4096,
    contextWindow: 200000,
    capabilities: ['chat', 'arquitecto', 'documentacion'],
    icon: '🧠',
    costPer1kTokens: 0.015
  }
]

// Tipos para uso de tokens
export interface TokenUsage {
  inputTokens?: number
  outputTokens?: number
  totalTokens?: number
}

// Tipos para mensajes
export interface Message {
  id?: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: string
  mcpServicesUsed?: string[]
  usage?: TokenUsage
  mcpInfo?: {
    mcpServicesUsed: string[]
    transparency?: {
      message: string
      services: string[]
    }
  }
}

// Tipos para proyectos
export interface Project {
  id: string
  name: string
  description: string
  status: 'in_progress' | 'completed'
  type: 'basic' | 'standard' | 'premium'
  createdAt: string
  updatedAt: string
  documentCount: number
  hasDocuments: boolean
  lastMessage?: string
}

// Alias para compatibilidad
export type ProjectInfo = Project

// Tipos para documentos
export interface Document {
  id: string
  projectId: string
  name: string
  type: string
  url: string
  createdAt: string
  size: number
}

// Tipos para servicios MCP
export interface MCPService {
  name: string
  description: string
  capabilities: string[]
  status: 'active' | 'inactive'
}

export const MCP_SERVICES: MCPService[] = [
  {
    name: 'core',
    description: 'Servicios principales de MCP',
    capabilities: ['chat', 'prompt_understanding'],
    status: 'active'
  },
  {
    name: 'diagram',
    description: 'Generación de diagramas de arquitectura',
    capabilities: ['generate_diagram', 'list_icons'],
    status: 'active'
  },
  {
    name: 'docgen',
    description: 'Generación de documentación',
    capabilities: ['generate_document', 'prepare_repository'],
    status: 'active'
  },
  {
    name: 'pricing',
    description: 'Cálculo de precios de AWS',
    capabilities: ['calculate_pricing'],
    status: 'active'
  },
  {
    name: 'awsdocs',
    description: 'Búsqueda en documentación de AWS',
    capabilities: ['search_documentation', 'read_documentation'],
    status: 'active'
  },
  {
    name: 'cfn',
    description: 'Generación de plantillas CloudFormation',
    capabilities: ['generate_template'],
    status: 'active'
  }
]

// Tipos para stores de Zustand
export interface ChatSession {
  id: string
  name: string
  messages: Message[]
  createdAt: string
  updatedAt: string
  modelId: string
}

export interface ChatStore {
  sessions: ChatSession[]
  currentSessionId: string | null
  isLoading: boolean
  selectedModel: string
  messages: Message[] // Computed property for current session messages
  addSession: (session: ChatSession) => void
  setCurrentSession: (sessionId: string) => void
  addMessage: (message: Message) => void
  updateMessage: (sessionId: string, messageIndex: number, updates: Partial<Message>) => void
  clearCurrentSession: () => void
  setMessages: (messages: Message[]) => void
  deleteSession: (sessionId: string) => void
  setLoading: (loading: boolean) => void
  setSelectedModel: (modelId: string) => void
}

export interface ArquitectoFlow {
  currentStep: number
  totalSteps: number
  stepName: string
  isComplete: boolean
  canProceed: boolean
}

export interface ArquitectoStore {
  currentProject: ProjectInfo | null
  flow: ArquitectoFlow
  isGeneratingDocuments: boolean
  setCurrentProject: (project: ProjectInfo) => void
  updateFlow: (flow: Partial<ArquitectoFlow>) => void
  setProjectInfo: (info: Partial<ProjectInfo>) => void
  nextStep: () => void
  previousStep: () => void
  resetFlow: () => void
  completeFlow: () => void
  setGeneratingDocuments: (generating: boolean) => void
}

export interface ProjectsStore {
  projects: ProjectInfo[]
  isLoading: boolean
  currentPage: number
  totalPages: number
  setProjects: (projects: ProjectInfo[]) => void
  addProject: (project: ProjectInfo) => void
  updateProject: (id: string, updates: Partial<ProjectInfo>) => void
  deleteProject: (id: string) => void
  setLoading: (loading: boolean) => void
  setCurrentPage: (page: number) => void
}
