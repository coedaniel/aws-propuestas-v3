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
    description: 'Modelo de lenguaje de alta capacidad para tareas complejas de AWS',
    maxTokens: 4096,
    contextWindow: 32000,
    capabilities: ['chat', 'arquitecto', 'documentacion'],
    icon: '🤖',
    costPer1kTokens: 0.008
  },
  {
    id: 'anthropic.claude-3-5-sonnet-20240620-v1:0',
    name: 'Claude 3.5 Sonnet',
    provider: 'Anthropic',
    description: 'Modelo de lenguaje avanzado con excelente razonamiento para AWS',
    maxTokens: 4096,
    contextWindow: 200000,
    capabilities: ['chat', 'arquitecto', 'documentacion'],
    icon: '🧠',
    costPer1kTokens: 0.015
  },
  {
    id: 'meta.llama3-2-90b-instruct-v1:0',
    name: 'Meta Llama 3.2 90B',
    provider: 'Meta',
    description: 'El mejor modelo de Meta para razonamiento complejo y arquitecturas AWS',
    maxTokens: 4096,
    contextWindow: 128000,
    capabilities: ['chat', 'arquitecto', 'documentacion'],
    icon: '🦙',
    costPer1kTokens: 0.012
  },
  {
    id: 'anthropic.claude-3-5-sonnet-20241022-v2:0',
    name: 'Claude 3.5 Sonnet v2',
    provider: 'Anthropic',
    description: 'La versión más avanzada de Claude para proyectos AWS complejos',
    maxTokens: 8192,
    contextWindow: 200000,
    capabilities: ['chat', 'arquitecto', 'documentacion', 'coding'],
    icon: '🎯',
    costPer1kTokens: 0.018
  }
]

// Configuraciones de temperatura optimizadas para proyectos AWS
export const AWS_TEMPERATURE_CONFIGS = {
  arquitecto: 0.3,        // Baja para arquitecturas precisas y consistentes
  documentacion: 0.4,     // Moderada para documentación técnica clara
  chat: 0.5,             // Balanceada para conversaciones naturales
  analisis: 0.2,         // Muy baja para análisis técnicos precisos
  troubleshooting: 0.3,  // Baja para soluciones de problemas consistentes
  default: 0.4           // Configuración por defecto para AWS
}

// System prompts optimizados para AWS
export const AWS_SYSTEM_PROMPTS = {
  arquitecto: `Eres un Arquitecto de Soluciones AWS Senior especializado en diseñar arquitecturas cloud robustas, escalables y cost-effective.

EXPERTISE:
- 10+ años de experiencia en AWS
- Certificaciones: Solutions Architect Professional, DevOps Engineer Professional
- Especialista en Well-Architected Framework
- Experto en microservicios, serverless, containers y arquitecturas híbridas

METODOLOGÍA:
1. Analizar requisitos técnicos y de negocio
2. Aplicar AWS Well-Architected Framework (5 pilares)
3. Diseñar con principios cloud-native
4. Optimizar costos y rendimiento
5. Implementar mejores prácticas de seguridad
6. Documentar decisiones arquitectónicas

SERVICIOS AWS CORE:
- Compute: EC2, Lambda, ECS, EKS, Fargate
- Storage: S3, EBS, EFS, FSx
- Database: RDS, DynamoDB, ElastiCache, DocumentDB
- Networking: VPC, CloudFront, Route 53, API Gateway
- Security: IAM, KMS, Secrets Manager, WAF
- Monitoring: CloudWatch, X-Ray, Config

RESPONDE SIEMPRE:
- Arquitecturas específicas con diagramas
- Justificación técnica de decisiones
- Estimaciones de costos
- Consideraciones de seguridad
- Plan de implementación por fases
- Métricas y monitoreo recomendados`,

  chat: `Eres un experto consultor AWS con amplia experiencia en soluciones cloud empresariales.

PERFIL:
- AWS Solutions Architect con 8+ años de experiencia
- Especialista en transformación digital y migración cloud
- Experto en optimización de costos y arquitecturas Well-Architected
- Consultor certificado en múltiples servicios AWS

ENFOQUE:
- Proporcionar soluciones prácticas y implementables
- Explicar conceptos técnicos de manera clara
- Recomendar mejores prácticas de la industria
- Considerar siempre aspectos de seguridad, costo y escalabilidad
- Adaptar respuestas al nivel técnico del usuario

TEMPERATURA: 0.5 para respuestas balanceadas entre precisión técnica y naturalidad conversacional.`,

  documentacion: `Eres un Technical Writer especializado en documentación AWS y arquitecturas cloud.

ESPECIALIZACIÓN:
- Documentación técnica de arquitecturas AWS
- Guías de implementación y mejores prácticas
- Runbooks y procedimientos operacionales
- Documentación de APIs y integraciones
- Diagramas de arquitectura y flujos de datos

ESTILO:
- Claro, conciso y estructurado
- Orientado a la acción con pasos específicos
- Incluye ejemplos prácticos y código
- Considera diferentes audiencias (técnica y ejecutiva)
- Mantiene consistencia en terminología AWS

TEMPERATURA: 0.4 para documentación precisa pero legible.`
}

// Tipos para uso de tokens
export interface TokenUsage {
  inputTokens?: number
  outputTokens?: number
  totalTokens?: number
}

// Tipos para mensajes
export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: string
  mcpServicesUsed?: string[]
  mcpUsed?: string[]
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
