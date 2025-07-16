// ============================================================================
// TYPES DEFINITIONS - AWS PROPUESTAS V3
// ============================================================================

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  modelId?: string
  usage?: {
    inputTokens?: number
    outputTokens?: number
    totalTokens?: number
  }
}

export interface ChatSession {
  id: string
  userId: string
  title: string
  messages: Message[]
  modelId: string
  mode: 'chat-libre' | 'arquitecto'
  createdAt: Date
  updatedAt: Date
}

// ============================================================================
// ARQUITECTO TYPES
// ============================================================================

export interface ProjectInfo {
  id: string
  userId: string
  sessionId: string
  name: string
  type: 'integral' | 'rapido'
  status: 'IN_PROGRESS' | 'COMPLETED' | 'ARCHIVED'
  
  // Basic Info
  description?: string
  objective?: string
  timeline?: string
  budget?: string
  
  // Technical Requirements
  services?: string[]
  regions?: string[]
  highAvailability?: boolean
  disasterRecovery?: boolean
  rto?: string // Recovery Time Objective
  rpo?: string // Recovery Point Objective
  
  // Architecture Details
  architecture?: {
    compute?: string[]
    storage?: string[]
    database?: string[]
    networking?: string[]
    security?: string[]
    monitoring?: string[]
  }
  
  // Generated Documents
  documents?: {
    wordDoc?: string // S3 URL
    activitiesCSV?: string // S3 URL
    costsCSV?: string // S3 URL
    cloudFormationYAML?: string // S3 URL
    diagramSVG?: string // S3 URL
    diagramPNG?: string // S3 URL
    diagramDrawio?: string // S3 URL
    calculatorGuide?: string // S3 URL
  }
  
  // Metadata
  estimatedCost?: number
  complexity?: 'LOW' | 'MEDIUM' | 'HIGH'
  createdAt: Date
  updatedAt: Date
  completedAt?: Date
}

export interface ArquitectoStep {
  id: number
  question: string
  answer?: string
  required: boolean
  type: 'text' | 'select' | 'multiselect' | 'boolean'
  options?: string[]
  completed: boolean
}

export interface ArquitectoFlow {
  currentStep: number
  steps: ArquitectoStep[]
  projectInfo: Partial<ProjectInfo>
  isComplete: boolean
}

// ============================================================================
// AI MODELS
// ============================================================================

export interface AIModel {
  id: string
  name: string
  description: string
  icon: string
  color: string
  provider: 'amazon' | 'anthropic' | 'meta'
  capabilities: string[]
  maxTokens: number
  costPer1kTokens: number
}

export const AVAILABLE_MODELS: AIModel[] = [
  {
    id: 'nova',
    name: 'Nova Pro',
    description: 'Ideal para diagramas, análisis visual y contenido multimodal',
    icon: '🎨',
    color: 'text-orange-600',
    provider: 'amazon',
    capabilities: ['text', 'image', 'video', 'multimodal', 'diagrams'],
    maxTokens: 4000,
    costPer1kTokens: 0.008
  },
  {
    id: 'claude',
    name: 'Claude 3.5 Sonnet',
    description: 'Ideal para análisis técnico profundo y documentación detallada',
    icon: '🧠',
    color: 'text-purple-600',
    provider: 'anthropic',
    capabilities: ['text', 'advanced-reasoning', 'technical-analysis', 'documentation'],
    maxTokens: 8000,
    costPer1kTokens: 0.003
  }
]

// ============================================================================
// API RESPONSES
// ============================================================================

export interface ChatResponse {
  response: string
  modelId: string
  mode: string
  usage?: {
    inputTokens?: number
    outputTokens?: number
    totalTokens?: number
  }
  sessionId?: string
}

export interface ArquitectoResponse extends ChatResponse {
  projectInfo?: Partial<ProjectInfo>
  currentStep?: number
  isComplete?: boolean
  documentsGenerated?: boolean
  s3Folder?: string
  // MCP Integration properties
  mcpServicesUsed?: string[]
  mcpResults?: any
  transparency?: {
    message: string
    services: string[]
  }
  promptUnderstanding?: any
}

export interface ProjectsResponse {
  projects: ProjectInfo[]
  total: number
  page: number
  limit: number
}

// ============================================================================
// DOCUMENT GENERATION
// ============================================================================

export interface DocumentTemplate {
  type: 'word' | 'csv' | 'yaml' | 'svg' | 'png' | 'drawio' | 'guide'
  name: string
  description: string
  generator: string
}

export interface GeneratedDocument {
  type: DocumentTemplate['type']
  filename: string
  s3Key: string
  s3Url: string
  size: number
  createdAt: Date
}

// ============================================================================
// AWS SERVICES CATALOG
// ============================================================================

export interface AWSService {
  id: string
  name: string
  category: 'compute' | 'storage' | 'database' | 'networking' | 'security' | 'ai' | 'analytics' | 'devops'
  description: string
  icon: string
  pricing: 'pay-per-use' | 'reserved' | 'on-demand' | 'free-tier'
  complexity: 'LOW' | 'MEDIUM' | 'HIGH'
  commonUse: string[]
}

export const AWS_SERVICES_CATALOG: AWSService[] = [
  // Compute
  {
    id: 'lambda',
    name: 'AWS Lambda',
    category: 'compute',
    description: 'Ejecuta código sin servidores',
    icon: '⚡',
    pricing: 'pay-per-use',
    complexity: 'LOW',
    commonUse: ['APIs', 'Procesamiento de eventos', 'Microservicios']
  },
  {
    id: 'ec2',
    name: 'Amazon EC2',
    category: 'compute',
    description: 'Servidores virtuales escalables',
    icon: '🖥️',
    pricing: 'on-demand',
    complexity: 'MEDIUM',
    commonUse: ['Aplicaciones web', 'Bases de datos', 'Procesamiento']
  },
  // Storage
  {
    id: 's3',
    name: 'Amazon S3',
    category: 'storage',
    description: 'Almacenamiento de objetos escalable',
    icon: '🗄️',
    pricing: 'pay-per-use',
    complexity: 'LOW',
    commonUse: ['Backup', 'Archivos estáticos', 'Data lake']
  },
  // Database
  {
    id: 'dynamodb',
    name: 'Amazon DynamoDB',
    category: 'database',
    description: 'Base de datos NoSQL serverless',
    icon: '🗃️',
    pricing: 'pay-per-use',
    complexity: 'MEDIUM',
    commonUse: ['Aplicaciones web', 'Gaming', 'IoT']
  },
  {
    id: 'rds',
    name: 'Amazon RDS',
    category: 'database',
    description: 'Base de datos relacional administrada',
    icon: '🏛️',
    pricing: 'reserved',
    complexity: 'MEDIUM',
    commonUse: ['Aplicaciones empresariales', 'E-commerce', 'CRM']
  }
]

// ============================================================================
// STORE TYPES
// ============================================================================

export interface ChatStore {
  // Current session
  currentSession: ChatSession | null
  messages: Message[]
  isLoading: boolean
  selectedModel: string
  
  // Actions
  setCurrentSession: (session: ChatSession | null) => void
  addMessage: (message: Message) => void
  setMessages: (messages: Message[]) => void
  setIsLoading: (loading: boolean) => void
  setSelectedModel: (modelId: string) => void
  clearMessages: () => void
}

export interface ArquitectoStore {
  // Current project
  currentProject: ProjectInfo | null
  flow: ArquitectoFlow | null
  isGeneratingDocuments: boolean
  
  // Actions
  setCurrentProject: (project: ProjectInfo | null) => void
  setFlow: (flow: ArquitectoFlow | null) => void
  updateProjectInfo: (info: Partial<ProjectInfo>) => void
  setIsGeneratingDocuments: (generating: boolean) => void
  completeProject: () => void
}

export interface ProjectsStore {
  projects: ProjectInfo[]
  isLoading: boolean
  currentPage: number
  totalPages: number
  
  // Actions
  setProjects: (projects: ProjectInfo[]) => void
  addProject: (project: ProjectInfo) => void
  updateProject: (id: string, updates: Partial<ProjectInfo>) => void
  setIsLoading: (loading: boolean) => void
  setCurrentPage: (page: number) => void
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}

export type ApiResponse<T = any> = {
  success: boolean
  data?: T
  error?: string
  message?: string
}

export type PaginatedResponse<T> = {
  items: T[]
  total: number
  page: number
  limit: number
  totalPages: number
}
