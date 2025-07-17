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
}

export const AVAILABLE_MODELS: Model[] = [
  {
    id: 'amazon.nova-pro-v1:0',
    name: 'Amazon Nova Pro',
    provider: 'Amazon',
    description: 'Modelo de lenguaje de alta capacidad para tareas complejas',
    maxTokens: 4096,
    contextWindow: 32000,
    capabilities: ['chat', 'arquitecto', 'documentacion']
  },
  {
    id: 'anthropic.claude-3-5-sonnet-20241022-v2:0',
    name: 'Claude 3.5 Sonnet',
    provider: 'Anthropic',
    description: 'Modelo de lenguaje avanzado con excelente razonamiento',
    maxTokens: 4096,
    contextWindow: 200000,
    capabilities: ['chat', 'arquitecto', 'documentacion']
  }
]

// Tipos para mensajes
export interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
  mcpServicesUsed?: string[]
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
