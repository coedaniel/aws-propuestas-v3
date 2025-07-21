'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
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
  Wrench
} from 'lucide-react'

export default function ArquitectoPage() {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [input, setInput] = useState('')
  // Usar el store global en lugar de estado local
  const [localLoading, setLocalLoading] = useState(false)
  const [showPromptUnderstanding, setShowPromptUnderstanding] = useState(true)
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null)
  const [currentProject, setCurrentProject] = useState<any>(null)
  const [projectPhase, setProjectPhase] = useState<'inicio' | 'recopilacion' | 'generacion' | 'completado'>('inicio')
  
  const {
    selectedModel,
    setSelectedModel,
    messages,
    addMessage,
    setLoading,
    isLoading: globalLoading
  } = useChatStore()

  const isLoading = localLoading || globalLoading
  const currentModel = AVAILABLE_MODELS.find(m => m.id === selectedModel) || AVAILABLE_MODELS[0]

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: generateId(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString()
    }

    // Usar el store global
    addMessage(userMessage)
    const currentMessages = [...messages, userMessage]
    
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
        projectPhase: projectPhase,
        currentProject: currentProject
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
          projectPhase: projectPhase,
          currentProject: currentProject
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

      // Usar el store global
      addMessage(assistantMessage)
      
      // Actualizar estado del proyecto si se proporciona
      if (data.projectUpdate) {
        setCurrentProject(data.projectUpdate)
      }
      
      // Actualizar fase del proyecto si se proporciona
      if (data.projectPhase) {
        setProjectPhase(data.projectPhase)
      }
      
    } catch (error: any) {
      console.error('❌ Error completo:', error)
      const errorMessage: Message = {
        id: generateId(),
        role: 'assistant',
        content: `Error al procesar la solicitud: ${error?.message || 'Error desconocido'}`,
        timestamp: new Date().toISOString()
      }
      
      addMessage(errorMessage)
    } finally {
      setLocalLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      e.stopPropagation()
      sendMessage()
    }
  }

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (input.trim() && !isLoading) {
      sendMessage()
    }
  }

  const clearChat = () => {
    // Usar el store global
    const { clearCurrentSession } = useChatStore.getState()
    clearCurrentSession()
    setCurrentProject(null)
    setProjectPhase('inicio')
  }

  const exportChat = () => {
    const chatData = {
      timestamp: new Date().toISOString(),
      model: currentModel.name,
      project: currentProject,
      phase: projectPhase,
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

  const getPhaseIcon = (phase: typeof projectPhase) => {
    switch (phase) {
      case 'inicio':
        return <Sparkles className="w-4 h-4 text-blue-500" />
      case 'recopilacion':
        return <Target className="w-4 h-4 text-yellow-500" />
      case 'generacion':
        return <Wrench className="w-4 h-4 text-purple-500" />
      case 'completado':
        return <CheckCircle className="w-4 h-4 text-green-500" />
    }
  }

  const getPhaseText = (phase: typeof projectPhase) => {
    switch (phase) {
      case 'inicio':
        return 'Inicio de Proyecto'
      case 'recopilacion':
        return 'Recopilación de Requisitos'
      case 'generacion':
        return 'Generación de Documentos'
      case 'completado':
        return 'Proyecto Completado'
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
                  <Bot className="w-6 h-6 text-purple-500" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-foreground">Arquitecto IA</h1>
                  <div className="flex items-center space-x-2">
                    {getPhaseIcon(projectPhase)}
                    <p className="text-sm text-muted-foreground">
                      {getPhaseText(projectPhase)} • {currentModel.name}
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
                onClick={() => setShowPromptUnderstanding(!showPromptUnderstanding)}
              >
                {showPromptUnderstanding ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                {showPromptUnderstanding ? 'Ocultar' : 'Mostrar'} Análisis
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
          {currentProject && (
            <div className="mt-4 p-3 bg-muted/30 rounded-lg">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Building className="w-4 h-4 text-primary" />
                  <div>
                    <div className="font-medium text-foreground">{currentProject.name || 'Proyecto Sin Nombre'}</div>
                    <div className="text-sm text-muted-foreground">
                      {currentProject.type === 'servicio-rapido' ? 'Servicio Rápido' : 'Solución Integral'}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant="outline" className="bg-blue-500/10 text-blue-500">
                    Fase {projectPhase === 'inicio' ? '1' : projectPhase === 'recopilacion' ? '2' : projectPhase === 'generacion' ? '3' : '4'}/4
                  </Badge>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <WelcomeMessage model={currentModel} />
          ) : (
            messages.map((message: Message) => (
              <MessageBubble 
                key={message.id} 
                message={message} 
                onCopy={copyMessage}
                copiedMessageId={copiedMessageId}
              />
            ))
          )}
          
          {isLoading && <LoadingMessage model={currentModel} />}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-border bg-card/50 backdrop-blur-sm p-4">
          <form onSubmit={handleFormSubmit} className="flex space-x-4">
            <div className="flex-1">
              <Textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={getInputPlaceholder(projectPhase)}
                className="min-h-[80px] resize-none focus-ring"
                disabled={isLoading}
              />
            </div>
            <Button
              type="submit"
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
          </form>
          
          <div className="mt-2 text-xs text-muted-foreground flex items-center justify-between">
            <span>Presiona Enter para enviar, Shift+Enter para nueva línea</span>
            <span>Arquitecto IA • Generación guiada de propuestas</span>
          </div>
        </div>
      </div>

      {/* Prompt Understanding Sidebar */}
      {showPromptUnderstanding && (
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
      return 'Describe tu proyecto o necesidad de arquitectura AWS...'
    case 'recopilacion':
      return 'Proporciona más detalles sobre los requisitos...'
    case 'generacion':
      return 'Confirma los detalles o solicita ajustes...'
    case 'completado':
      return 'Proyecto completado. ¿Necesitas algún ajuste?'
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
            <Bot className="w-4 h-4 text-white" />
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
          <Bot className="w-4 h-4 text-white" />
        </div>
        
        <Card className="message-assistant">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Loader2 className="w-4 h-4 animate-spin text-purple-500" />
              <span className="text-sm text-muted-foreground">
                El Arquitecto IA está analizando tu solicitud...
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

function WelcomeMessage({ model }: { model: any }) {
  return (
    <div className="text-center py-12">
      <div className="inline-flex items-center justify-center w-16 h-16 bg-purple-500/10 rounded-full mb-6">
        <Bot className="w-8 h-8 text-purple-500" />
      </div>
      
      <h2 className="text-2xl font-bold text-foreground mb-4">
        ¡Bienvenido al Arquitecto IA!
      </h2>
      
      <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
        Soy tu asistente especializado en generar propuestas arquitectónicas profesionales para AWS. 
        Te guiaré paso a paso para crear documentación completa y personalizada.
      </p>
      
      <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto text-sm mb-8">
        <Card className="p-4 bg-blue-500/5 border-blue-500/20">
          <div className="flex items-center space-x-2 mb-3">
            <Zap className="w-5 h-5 text-blue-500" />
            <h3 className="font-semibold text-blue-900 dark:text-blue-100">Servicios Rápidos</h3>
          </div>
          <ul className="text-blue-700 dark:text-blue-300 space-y-1 text-left">
            <li>• Configuración de EC2, RDS, S3</li>
            <li>• Setup de VPN, ELB, CloudFront</li>
            <li>• Implementación de servicios específicos</li>
            <li>• Documentación y scripts automáticos</li>
          </ul>
        </Card>
        
        <Card className="p-4 bg-purple-500/5 border-purple-500/20">
          <div className="flex items-center space-x-2 mb-3">
            <Building className="w-5 h-5 text-purple-500" />
            <h3 className="font-semibold text-purple-900 dark:text-purple-100">Soluciones Integrales</h3>
          </div>
          <ul className="text-purple-700 dark:text-purple-300 space-y-1 text-left">
            <li>• Migraciones completas a la nube</li>
            <li>• Arquitecturas serverless y microservicios</li>
            <li>• Soluciones de IA, IoT y analytics</li>
            <li>• Propuestas ejecutivas profesionales</li>
          </ul>
        </Card>
      </div>
      
      <div className="grid md:grid-cols-3 gap-4 max-w-3xl mx-auto text-sm">
        <Card className="p-4 bg-green-500/5 border-green-500/20">
          <div className="flex items-center space-x-2 mb-2">
            <CheckCircle className="w-4 h-4 text-green-500" />
            <h3 className="font-semibold text-green-900 dark:text-green-100">Proceso Guiado</h3>
          </div>
          <ul className="text-green-700 dark:text-green-300 space-y-1 text-left">
            <li>• Entrevista paso a paso</li>
            <li>• Recopilación de requisitos</li>
            <li>• Validación de información</li>
          </ul>
        </Card>
        
        <Card className="p-4 bg-orange-500/5 border-orange-500/20">
          <div className="flex items-center space-x-2 mb-2">
            <FileText className="w-4 h-4 text-orange-500" />
            <h3 className="font-semibold text-orange-900 dark:text-orange-100">Documentos Generados</h3>
          </div>
          <ul className="text-orange-700 dark:text-orange-300 space-y-1 text-left">
            <li>• Propuesta ejecutiva (Word)</li>
            <li>• Plan de actividades (CSV)</li>
            <li>• Scripts CloudFormation (YAML)</li>
            <li>• Diagramas de arquitectura</li>
          </ul>
        </Card>
        
        <Card className="p-4 bg-cyan-500/5 border-cyan-500/20">
          <div className="flex items-center space-x-2 mb-2">
            <Cpu className="w-4 h-4 text-cyan-500" />
            <h3 className="font-semibold text-cyan-900 dark:text-cyan-100">MCPs Integrados</h3>
          </div>
          <ul className="text-cyan-700 dark:text-cyan-300 space-y-1 text-left">
            <li>• Cálculo automático de costos</li>
            <li>• Generación de diagramas</li>
            <li>• Consulta de documentación AWS</li>
          </ul>
        </Card>
      </div>
      
      <div className="mt-8">
        <p className="text-sm text-muted-foreground mb-4">
          Para comenzar, simplemente describe tu proyecto o necesidad:
        </p>
        <div className="flex flex-wrap justify-center gap-2">
          <Badge variant="outline" className="bg-muted/30">
            "Necesito migrar mi aplicación a AWS"
          </Badge>
          <Badge variant="outline" className="bg-muted/30">
            "Quiero implementar una arquitectura serverless"
          </Badge>
          <Badge variant="outline" className="bg-muted/30">
            "Configurar una base de datos RDS"
          </Badge>
        </div>
      </div>
    </div>
  )
}
