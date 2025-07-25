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
  MessageCircle,
  Sparkles,
  Zap,
  Lightbulb,
  Cpu,
  RotateCcw,
  Download,
  Copy,
  Check,
  Settings,
  Eye,
  EyeOff
} from 'lucide-react'

export default function ChatPage() {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [input, setInput] = useState('')
  const [localMessages, setLocalMessages] = useState<Message[]>([])
  const [localLoading, setLocalLoading] = useState(false)
  const [showPromptUnderstanding, setShowPromptUnderstanding] = useState(true)
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null)
  
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

    setLocalMessages(prev => [...prev, userMessage])
    const currentMessages = [...localMessages, userMessage]
    
    setInput('')
    setLocalLoading(true)

    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://75bl52azoi.execute-api.us-east-1.amazonaws.com/prod'
      
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: currentMessages.map(m => ({
            role: m.role,
            content: m.content
          })),
          modelId: selectedModel
        }),
      })

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()

      const assistantMessage: Message = {
        id: generateId(),
        role: 'assistant',
        content: data.response || 'Lo siento, no pude generar una respuesta.',
        timestamp: new Date().toISOString(),
        usage: data.usage,
        mcpUsed: data.mcpUsed || []
      }

      setLocalMessages(prev => [...prev, assistantMessage])
      
    } catch (error: any) {
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
  }

  const exportChat = () => {
    const chatData = {
      timestamp: new Date().toISOString(),
      model: currentModel.name,
      messages: messages.map(m => ({
        role: m.role,
        content: m.content,
        timestamp: m.timestamp
      }))
    }
    
    const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `chat-export-${new Date().toISOString().split('T')[0]}.json`
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

  return (
    <div className="flex h-screen">
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="border-b border-border bg-card/50 backdrop-blur-sm p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <MessageCircle className="w-6 h-6 text-primary" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-foreground">Chat Libre</h1>
                  <p className="text-sm text-muted-foreground">
                    Conversación con {currentModel.name}
                  </p>
                </div>
              </div>
              
              <Badge variant="secondary" className="bg-green-500/10 text-green-500">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                Conectado
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
                Limpiar
              </Button>
              <ModelSelector
                selectedModel={selectedModel}
                onModelChange={setSelectedModel}
                disabled={isLoading}
                compact={true}
              />
            </div>
          </div>
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
          <div className="flex space-x-4">
            <div className="flex-1">
              <Textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={`Pregunta algo sobre AWS usando ${currentModel.name}...`}
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
            <span>Presiona Enter para enviar, Shift+Enter para nueva línea</span>
            <span>Modelo: {currentModel.name} • ${currentModel.costPer1kTokens}/1k tokens</span>
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
      <div className={`flex space-x-3 max-w-3xl ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? 'bg-primary' : 'bg-muted'
        }`}>
          {isUser ? (
            <User className="w-4 h-4 text-primary-foreground" />
          ) : (
            <Bot className="w-4 h-4 text-muted-foreground" />
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
      <div className="flex space-x-3 max-w-3xl">
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-muted flex items-center justify-center">
          <Bot className="w-4 h-4 text-muted-foreground" />
        </div>
        
        <Card className="message-assistant">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Loader2 className="w-4 h-4 animate-spin text-primary" />
              <span className="text-sm text-muted-foreground">
                {model.name} está procesando tu solicitud...
              </span>
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
      <div className="inline-flex items-center justify-center w-16 h-16 bg-primary/10 rounded-full mb-6">
        <Sparkles className="w-8 h-8 text-primary" />
      </div>
      
      <h2 className="text-2xl font-bold text-foreground mb-4">
        ¡Bienvenido al Chat Libre!
      </h2>
      
      <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
        Conversa con <strong>{model.name}</strong> sobre cualquier tema relacionado con AWS. 
        Puedes hacer preguntas técnicas, solicitar arquitecturas, mejores prácticas y más.
      </p>
      
      <div className="grid md:grid-cols-3 gap-4 max-w-3xl mx-auto text-sm">
        <Card className="p-4 bg-blue-500/5 border-blue-500/20">
          <div className="flex items-center space-x-2 mb-2">
            <Lightbulb className="w-4 h-4 text-blue-500" />
            <h3 className="font-semibold text-blue-900 dark:text-blue-100">Ejemplos de preguntas</h3>
          </div>
          <ul className="text-blue-700 dark:text-blue-300 space-y-1 text-left">
            <li>• ¿Cómo diseñar una arquitectura serverless?</li>
            <li>• Diferencias entre RDS y DynamoDB</li>
            <li>• Mejores prácticas de seguridad en AWS</li>
          </ul>
        </Card>
        
        <Card className="p-4 bg-green-500/5 border-green-500/20">
          <div className="flex items-center space-x-2 mb-2">
            <Zap className="w-4 h-4 text-green-500" />
            <h3 className="font-semibold text-green-900 dark:text-green-100">Capacidades</h3>
          </div>
          <ul className="text-green-700 dark:text-green-300 space-y-1 text-left">
            <li>• Análisis técnico profundo</li>
            <li>• Recomendaciones personalizadas</li>
            <li>• Explicaciones paso a paso</li>
          </ul>
        </Card>
        
        <Card className="p-4 bg-purple-500/5 border-purple-500/20">
          <div className="flex items-center space-x-2 mb-2">
            <Cpu className="w-4 h-4 text-purple-500" />
            <h3 className="font-semibold text-purple-900 dark:text-purple-100">Modelo actual</h3>
          </div>
          <ul className="text-purple-700 dark:text-purple-300 space-y-1 text-left">
            <li>• {model.name} ({model.provider})</li>
            <li>• ${model.costPer1kTokens}/1k tokens</li>
            <li>• Max {model.maxTokens.toLocaleString()} tokens</li>
          </ul>
        </Card>
      </div>
    </div>
  )
}
