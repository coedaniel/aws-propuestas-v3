'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { ModelSelector } from '@/components/ModelSelector'
import { PromptUnderstanding } from '@/components/PromptUnderstanding'
import { useChatStore } from '@/store/chatStore'
import { Message, AVAILABLE_MODELS } from '@/lib/types'
import { generateId, formatDate } from '@/lib/utils'
import { 
  Send, 
  Bot, 
  User, 
  Loader2,
  Sparkles,
  Zap,
  FileText,
  Download,
  Copy,
  Check,
  Eye,
  EyeOff,
  RotateCcw,
  Settings,
  Lightbulb,
  Target,
  CheckCircle,
  AlertCircle,
  Clock,
  Cpu,
  Building,
  Wrench,
  Folder,
  Upload,
  Database,
  Cloud,
  Cog,
  Tool
} from 'lucide-react'

// Tipos específicos para el arquitecto
interface ProjectState {
  name?: string
  type?: 'integral' | 'rapido'
  phase: 'inicio' | 'tipo' | 'recopilacion' | 'generacion' | 'entrega'
  data: any
}

interface McpActivity {
  id: string
  tool: string
  status: 'running' | 'completed' | 'error'
  description: string
  timestamp: string
  duration?: number
}

export default function ArquitectoPage() {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [input, setInput] = useState('')
  const [localMessages, setLocalMessages] = useState<Message[]>([])
  const [localLoading, setLocalLoading] = useState(false)
  const [showPromptUnderstanding, setShowPromptUnderstanding] = useState(true)
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null)
  
  // Estados específicos del arquitecto
  const [projectState, setProjectState] = useState<ProjectState>({
    phase: 'inicio',
    data: {}
  })
  const [mcpActivities, setMcpActivities] = useState<McpActivity[]>([])
  const [showMcpPanel, setShowMcpPanel] = useState(true)
  
  const {
    selectedModel,
    setSelectedModel,
  } = useChatStore()

  const messages = localMessages
  const isLoading = localLoading
  const currentModel = AVAILABLE_MODELS.find(m => m.id === selectedModel) || AVAILABLE_MODELS[0]

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Inicializar con mensaje de bienvenida del arquitecto
    if (messages.length === 0) {
      const welcomeMessage: Message = {
        id: generateId(),
        role: 'assistant',
        content: getWelcomePrompt(),
        timestamp: new Date().toISOString()
      }
      setLocalMessages([welcomeMessage])
    }
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const getWelcomePrompt = () => {
    return `¡Hola! Soy tu Arquitecto de Soluciones AWS y consultor experto.

Vamos a dimensionar, documentar y entregar una solucion profesional en AWS, siguiendo mejores practicas y generando todos los archivos necesarios para una propuesta ejecutiva.

**Importante:**
- No usare acentos ni caracteres especiales en ningun texto, archivo, script ni documento
- Todos los archivos Word seran funcionales y compatibles: solo texto plano, sin imagenes, sin tablas complejas, ni formato avanzado
- Solo generare scripts CloudFormation como entregable de automatizacion

**Para comenzar, necesito saber:**

¿Cual es el nombre del proyecto?`
  }

  const addMcpActivity = (tool: string, description: string) => {
    const activity: McpActivity = {
      id: generateId(),
      tool,
      status: 'running',
      description,
      timestamp: new Date().toISOString()
    }
    setMcpActivities(prev => [...prev, activity])
    return activity.id
  }

  const updateMcpActivity = (id: string, status: 'completed' | 'error', duration?: number) => {
    setMcpActivities(prev => prev.map(activity => 
      activity.id === id 
        ? { ...activity, status, duration }
        : activity
    ))
  }

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: generateId(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString()
    }

    setLocalMessages(prev => [...prev, userMessage])
    const currentMessages = [...localMessages, userMessage]
    
    setInput('')
    setLocalLoading(true)

    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod'
      
      console.log('🚀 Enviando mensaje a:', `${API_BASE_URL}/arquitecto`)
      console.log('📤 Payload:', {
        messages: currentMessages.map(m => ({
          role: m.role,
          content: m.content
        })),
        modelId: selectedModel,
        projectState: projectState
      })
      
      const response = await fetch(`${API_BASE_URL}/arquitecto`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: currentMessages.map(m => ({
            role: m.role,
            content: m.content
          })),
          modelId: selectedModel,
          projectState: projectState
        }),
      })

      console.log('📊 Response status:', response.status)

      if (!response.ok) {
        const errorText = await response.text()
        console.error('❌ Response error:', errorText)
        throw new Error(`Error ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      console.log('✅ Response data:', data)

      const assistantMessage: Message = {
        id: generateId(),
        role: 'assistant',
        content: data.response || 'Lo siento, no pude generar una respuesta.',
        timestamp: new Date().toISOString(),
        usage: data.usage,
        mcpUsed: data.mcpUsed || []
      }

      setLocalMessages(prev => [...prev, assistantMessage])
      
      // Actualizar estado del proyecto si se proporciona
      if (data.projectUpdate) {
        setProjectState(prev => ({ ...prev, ...data.projectUpdate }))
      }
      
      // Simular actividades MCP basadas en la respuesta
      if (data.mcpUsed && data.mcpUsed.length > 0) {
        data.mcpUsed.forEach((mcp: string) => {
          const activityId = addMcpActivity(mcp, `Using ${mcp} (trusted)`)
          setTimeout(() => {
            updateMcpActivity(activityId, 'completed', Math.random() * 2000 + 500)
          }, Math.random() * 1000 + 500)
        })
      }
      
    } catch (error: any) {
      console.error('❌ Error completo:', error)
      const errorMessage: Message = {
        id: generateId(),
        role: 'assistant',
        content: `Error al procesar la solicitud: ${error?.message || 'Error desconocido'}`,
        timestamp: new Date().toISOString()
      }
      
      setLocalMessages(prev => [...prev, errorMessage])
    } finally {
      setLocalLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const clearChat = () => {
    setLocalMessages([])
    setProjectState({ phase: 'inicio', data: {} })
    setMcpActivities([])
    // Reinicializar con mensaje de bienvenida
    const welcomeMessage: Message = {
      id: generateId(),
      role: 'assistant',
      content: getWelcomePrompt(),
      timestamp: new Date().toISOString()
    }
    setLocalMessages([welcomeMessage])
  }

  const exportChat = () => {
    const chatData = {
      timestamp: new Date().toISOString(),
      model: currentModel.name,
      project: projectState,
      mcpActivities: mcpActivities,
      messages: messages.map(m => ({
        role: m.role,
        content: m.content,
        timestamp: m.timestamp,
        mcpUsed: m.mcpUsed
      }))
    }
    
    const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `arquitecto-session-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const copyMessage = async (content: string, messageId: string) => {
    try {
      await navigator.clipboard.writeText(content)
      setCopiedMessageId(messageId)
      setTimeout(() => setCopiedMessageId(null), 2000)
    } catch (err) {
      console.error('Failed to copy message:', err)
    }
  }

  const getPhaseIcon = (phase: string) => {
    switch (phase) {
      case 'inicio':
        return <Sparkles className="w-4 h-4 text-blue-500" />
      case 'tipo':
        return <Target className="w-4 h-4 text-yellow-500" />
      case 'recopilacion':
        return <Database className="w-4 h-4 text-orange-500" />
      case 'generacion':
        return <Wrench className="w-4 h-4 text-purple-500" />
      case 'entrega':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      default:
        return <Clock className="w-4 h-4 text-gray-500" />
    }
  }

  const getPhaseText = (phase: string) => {
    switch (phase) {
      case 'inicio':
        return 'Inicio de Proyecto'
      case 'tipo':
        return 'Definicion de Tipo'
      case 'recopilacion':
        return 'Recopilacion de Requisitos'
      case 'generacion':
        return 'Generacion de Documentos'
      case 'entrega':
        return 'Entrega Final'
      default:
        return 'En Proceso'
    }
  }

  return (
    <div className="flex h-screen">
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="border-b border-border bg-card/50 backdrop-blur-sm p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-purple-500/10 rounded-lg">
                  <Building className="w-6 h-6 text-purple-500" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-foreground">Arquitecto AWS</h1>
                  <div className="flex items-center space-x-2">
                    {getPhaseIcon(projectState.phase)}
                    <p className="text-sm text-muted-foreground">
                      {getPhaseText(projectState.phase)} • {currentModel.name}
                    </p>
                  </div>
                </div>
              </div>
              
              <Badge variant="secondary" className="bg-green-500/10 text-green-500">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                6 MCPs Activos
              </Badge>
            </div>
            
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowMcpPanel(!showMcpPanel)}
              >
                <Tool className="w-4 h-4 mr-2" />
                {showMcpPanel ? 'Ocultar' : 'Mostrar'} MCPs
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowPromptUnderstanding(!showPromptUnderstanding)}
              >
                {showPromptUnderstanding ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                {showPromptUnderstanding ? 'Ocultar' : 'Mostrar'} Analisis
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={exportChat}
                disabled={messages.length === 0}
              >
                <Download className="w-4 h-4 mr-2" />
                Exportar
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={clearChat}
                disabled={messages.length === 0}
              >
                <RotateCcw className="w-4 h-4 mr-2" />
                Nuevo Proyecto
              </Button>
              <ModelSelector
                selectedModel={selectedModel}
                onModelChange={setSelectedModel}
                disabled={isLoading}
                compact={true}
              />
            </div>
          </div>
          
          {/* Project Status Bar */}
          {projectState.name && (
            <div className="mt-4 p-3 bg-muted/30 rounded-lg">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Folder className="w-4 h-4 text-primary" />
                  <div>
                    <div className="font-medium text-foreground">{projectState.name}</div>
                    <div className="text-sm text-muted-foreground">
                      {projectState.type === 'rapido' ? 'Servicio Rapido' : 'Solucion Integral'}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant="outline" className="bg-blue-500/10 text-blue-500">
                    Fase {projectState.phase === 'inicio' ? '1' : projectState.phase === 'tipo' ? '2' : projectState.phase === 'recopilacion' ? '3' : projectState.phase === 'generacion' ? '4' : '5'}/5
                  </Badge>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message: Message) => (
            <MessageBubble 
              key={message.id} 
              message={message} 
              onCopy={copyMessage}
              copiedMessageId={copiedMessageId}
            />
          ))}
          
          {isLoading && <LoadingMessage model={currentModel} />}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-border bg-card/50 backdrop-blur-sm p-4">
          <div className="flex space-x-4">
            <div className="flex-1">
              <Textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={getInputPlaceholder(projectState.phase)}
                className="min-h-[80px] resize-none focus-ring"
                disabled={isLoading}
              />
            </div>
            <Button
              onClick={sendMessage}
              disabled={!input.trim() || isLoading}
              size="lg"
              className="px-6 self-end"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </Button>
          </div>
          
          <div className="mt-2 text-xs text-muted-foreground flex items-center justify-between">
            <span>Presiona Enter para enviar, Shift+Enter para nueva linea</span>
            <span>Arquitecto AWS • Generacion guiada de propuestas</span>
          </div>
        </div>
      </div>

      {/* MCP Activities Panel */}
      {showMcpPanel && (
        <div className="w-80 border-l border-border bg-card/30 backdrop-blur-sm">
          <McpPanel activities={mcpActivities} />
        </div>
      )}

      {/* Prompt Understanding Sidebar */}
      {showPromptUnderstanding && !showMcpPanel && (
        <div className="w-80 border-l border-border bg-card/30 backdrop-blur-sm">
          <PromptUnderstanding messages={messages} />
        </div>
      )}
    </div>
  )
}

function getInputPlaceholder(phase: string) {
  switch (phase) {
    case 'inicio':
      return 'Escribe el nombre del proyecto...'
    case 'tipo':
      return 'Especifica si es solucion integral o servicio rapido...'
    case 'recopilacion':
      return 'Proporciona mas detalles sobre los requisitos...'
    case 'generacion':
      return 'Confirma los detalles o solicita ajustes...'
    case 'entrega':
      return 'Proyecto completado. ¿Necesitas algun ajuste?'
    default:
      return 'Escribe tu mensaje...'
  }
}

interface MessageBubbleProps {
  message: Message
  onCopy: (content: string, messageId: string) => void
  copiedMessageId: string | null
}

function MessageBubble({ message, onCopy, copiedMessageId }: MessageBubbleProps) {
  const isUser = message.role === 'user'
  const isCopied = copiedMessageId === message.id
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex space-x-3 max-w-4xl ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? 'bg-primary' : 'bg-purple-500'
        }`}>
          {isUser ? (
            <User className="w-4 h-4 text-primary-foreground" />
          ) : (
            <Building className="w-4 h-4 text-white" />
          )}
        </div>
        
        <Card className={`${isUser ? 'message-user' : 'message-assistant'} group`}>
          <CardContent className="p-4">
            <div className="prose prose-sm max-w-none dark:prose-invert">
              <div className="whitespace-pre-wrap">{message.content}</div>
            </div>
            
            <div className="mt-3 flex items-center justify-between text-xs text-muted-foreground">
              <div className="flex items-center space-x-2">
                <span>{message.timestamp ? formatDate(message.timestamp) : ''}</span>
                {message.usage && (
                  <Badge variant="outline" className="text-xs">
                    {message.usage.inputTokens}→{message.usage.outputTokens} tokens
                  </Badge>
                )}
                {message.mcpUsed && message.mcpUsed.length > 0 && (
                  <Badge variant="outline" className="text-xs bg-purple-500/10 text-purple-500">
                    {message.mcpUsed.length} MCP
                  </Badge>
                )}
              </div>
              
              <Button
                variant="ghost"
                size="sm"
                className="opacity-0 group-hover:opacity-100 transition-opacity"
                onClick={() => onCopy(message.content, message.id)}
              >
                {isCopied ? (
                  <Check className="w-3 h-3 text-green-500" />
                ) : (
                  <Copy className="w-3 h-3" />
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

function LoadingMessage({ model }: { model: any }) {
  return (
    <div className="flex justify-start">
      <div className="flex space-x-3 max-w-4xl">
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-purple-500 flex items-center justify-center">
          <Building className="w-4 h-4 text-white" />
        </div>
        
        <Card className="message-assistant">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Loader2 className="w-4 h-4 animate-spin text-purple-500" />
              <span className="text-sm text-muted-foreground">
                El Arquitecto AWS esta analizando tu solicitud...
              </span>
            </div>
            <div className="mt-2 text-xs text-muted-foreground">
              Activando MCPs necesarios para generar la propuesta
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

interface McpPanelProps {
  activities: McpActivity[]
}

function McpPanel({ activities }: McpPanelProps) {
  const recentActivities = activities.slice(-10).reverse()
  
  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-border">
        <div className="flex items-center space-x-2">
          <Tool className="w-5 h-5 text-purple-500" />
          <h3 className="font-semibold text-foreground">Actividad MCP</h3>
        </div>
        <p className="text-xs text-muted-foreground mt-1">
          Herramientas utilizadas en tiempo real
        </p>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {recentActivities.length === 0 ? (
          <div className="text-center py-8">
            <Tool className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
            <p className="text-sm text-muted-foreground">
              No hay actividad MCP aun
            </p>
          </div>
        ) : (
          recentActivities.map((activity) => (
            <McpActivityItem key={activity.id} activity={activity} />
          ))
        )}
      </div>
      
      <div className="p-4 border-t border-border">
        <div className="text-xs text-muted-foreground">
          <div className="flex items-center justify-between">
            <span>MCPs Disponibles: 6</span>
            <span>Activos: {activities.filter(a => a.status === 'running').length}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

interface McpActivityItemProps {
  activity: McpActivity
}

function McpActivityItem({ activity }: McpActivityItemProps) {
  const getStatusIcon = () => {
    switch (activity.status) {
      case 'running':
        return <Loader2 className="w-3 h-3 animate-spin text-blue-500" />
      case 'completed':
        return <CheckCircle className="w-3 h-3 text-green-500" />
      case 'error':
        return <AlertCircle className="w-3 h-3 text-red-500" />
    }
  }
  
  const getStatusColor = () => {
    switch (activity.status) {
      case 'running':
        return 'border-blue-500/20 bg-blue-500/5'
      case 'completed':
        return 'border-green-500/20 bg-green-500/5'
      case 'error':
        return 'border-red-500/20 bg-red-500/5'
    }
  }
  
  return (
    <Card className={`p-3 ${getStatusColor()}`}>
      <div className="flex items-start space-x-2">
        {getStatusIcon()}
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono text-purple-600 dark:text-purple-400">
              🛠️ Using tool: {activity.tool}
            </span>
            <Badge variant="outline" className="text-xs">
              trusted
            </Badge>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            {activity.description}
          </p>
          {activity.duration && (
            <p className="text-xs text-muted-foreground mt-1">
              ● Completed in {(activity.duration / 1000).toFixed(1)}s
            </p>
          )}
        </div>
      </div>
    </Card>
  )
}
