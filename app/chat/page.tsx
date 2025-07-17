'use client'

import React, { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import ModelSelector from '@/components/ModelSelector'
import { useChatStore } from '@/store/chatStore'
import { Message, AVAILABLE_MODELS } from '@/lib/types'
import { generateId, formatDate } from '@/lib/utils'
import { 
  ArrowLeft, 
  Send, 
  Bot, 
  User, 
  Loader2,
  MessageCircle,
  Sparkles,
  Zap,
  Lightbulb,
  Cpu
} from 'lucide-react'

export default function ChatPage() {
  const router = useRouter()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [input, setInput] = useState('')
  
  const {
    messages,
    isLoading,
    selectedModel,
    addMessage,
    setLoading,
    setSelectedModel,
    clearCurrentSession
  } = useChatStore()

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

    addMessage(userMessage)
    setInput('')
    setLoading(true)

    try {
      // Llamada al endpoint específico de chat libre (solo AWS)
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod'
      
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [...messages, userMessage].map(m => ({
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
        timestamp: new Date().toISOString()
      }

      addMessage(assistantMessage)
      
    } catch (error: any) {
      console.error('Error sending message:', error)
      
      const errorMessage: Message = {
        id: generateId(),
        role: 'assistant',
        content: `Error al procesar la solicitud: ${error?.message || 'Error desconocido'}`,
        timestamp: new Date().toISOString()
      }
      
      addMessage(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const clearChat = () => {
    clearCurrentSession()
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => router.push('/')}
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Volver
              </Button>
              <div className="flex items-center space-x-3">
                <MessageCircle className="w-6 h-6 text-blue-600" />
                <div>
                  <h1 className="text-xl font-bold text-gray-900">Chat Libre</h1>
                  <p className="text-sm text-gray-600">Conversa con IA sobre AWS</p>
                </div>
              </div>
            </div>
            
            <ModelSelector
              selectedModel={selectedModel}
              onModelChange={setSelectedModel}
              disabled={isLoading}
              compact={true}
            />
          </div>
        </div>
      </header>

      {/* Chat Container */}
      <div className="flex-1 flex flex-col max-w-5xl mx-auto w-full">
        {/* Model Comparison Card */}
        {messages.length === 0 && (
          <div className="px-4 pt-4">
            <Card className="mb-4">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Cpu className="h-5 w-5 text-blue-600" />
                  Modelos Disponibles
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="p-4 border rounded-lg bg-blue-50 border-blue-200">
                    <div className="flex items-center gap-2 mb-2">
                      <Zap className="h-5 w-5 text-blue-600" />
                      <h3 className="font-semibold text-blue-900">Amazon Nova Pro v1</h3>
                    </div>
                    <ul className="text-sm text-blue-700 space-y-1">
                      <li>• Ideal para análisis multimodal y diagramas</li>
                      <li>• Excelente para explicaciones técnicas</li>
                      <li>• Optimizado para servicios AWS</li>
                      <li>• Respuestas directas sobre AWS</li>
                    </ul>
                  </div>
                  
                  <div className="p-4 border rounded-lg bg-purple-50 border-purple-200">
                    <div className="flex items-center gap-2 mb-2">
                      <Lightbulb className="h-5 w-5 text-purple-600" />
                      <h3 className="font-semibold text-purple-900">Claude 3.5 Sonnet v2</h3>
                    </div>
                    <ul className="text-sm text-purple-700 space-y-1">
                      <li>• Perfecto para análisis técnico profundo</li>
                      <li>• Excelente para código y soluciones complejas</li>
                      <li>• Razonamiento detallado y estructurado</li>
                      <li>• Respuestas precisas y bien fundamentadas</li>
                    </ul>
                  </div>
                </div>
                
                <div className="mt-4 text-sm text-gray-600">
                  <p>Selecciona el modelo que mejor se adapte a tu consulta. Puedes cambiar de modelo en cualquier momento.</p>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <WelcomeMessage model={currentModel} />
          ) : (
            messages.map((message: Message) => (
              <MessageBubble key={message.id} message={message} />
            ))
          )}
          
          {isLoading && <LoadingMessage model={currentModel} />}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t bg-white p-4">
          <div className="flex space-x-4">
            <div className="flex-1">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={`Pregunta algo sobre AWS usando ${currentModel.name}...`}
                className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                rows={3}
                disabled={isLoading}
              />
            </div>
            <Button
              onClick={sendMessage}
              disabled={!input.trim() || isLoading}
              size="lg"
              className="px-6"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </Button>
          </div>
          
          <div className="mt-2 text-xs text-gray-500 flex items-center justify-between">
            <span>Presiona Enter para enviar, Shift+Enter para nueva línea</span>
            <span>Modelo: {currentModel.name} • ${currentModel.costPer1kTokens}/1k tokens</span>
          </div>
        </div>
      </div>
    </div>
  )
}

interface MessageBubbleProps {
  message: Message
}

function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex space-x-3 max-w-3xl ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? 'bg-blue-600' : 'bg-gray-600'
        }`}>
          {isUser ? (
            <User className="w-4 h-4 text-white" />
          ) : (
            <Bot className="w-4 h-4 text-white" />
          )}
        </div>
        
        <Card className={`${isUser ? 'bg-blue-50 border-blue-200' : 'bg-white'}`}>
          <CardContent className="p-4">
            <div className="prose prose-sm max-w-none">
              <div className="whitespace-pre-wrap">{message.content}</div>
            </div>
            
            <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
              <span>{message.timestamp ? formatDate(message.timestamp) : ''}</span>
              <div className="flex items-center gap-2">
                {message.usage && (
                  <span>
                    {message.usage.inputTokens}→{message.usage.outputTokens} tokens
                  </span>
                )}
              </div>
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
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center">
          <Bot className="w-4 h-4 text-white" />
        </div>
        
        <Card className="bg-white">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
              <span className="text-sm text-gray-600">
                {model.name} está pensando...
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
      <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-6">
        <Sparkles className="w-8 h-8 text-blue-600" />
      </div>
      
      <h2 className="text-2xl font-bold text-gray-900 mb-4">
        ¡Bienvenido al Chat Libre!
      </h2>
      
      <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
        Conversa con <strong>{model.name}</strong> sobre cualquier tema relacionado con AWS. 
        Puedes hacer preguntas técnicas, solicitar arquitecturas, mejores prácticas y más.
      </p>
      
      <div className="grid md:grid-cols-3 gap-4 max-w-3xl mx-auto text-sm">
        <div className="p-4 bg-blue-50 rounded-lg">
          <h3 className="font-semibold text-blue-900 mb-2">💡 Ejemplos de preguntas</h3>
          <ul className="text-blue-700 space-y-1">
            <li>• ¿Cómo diseñar una arquitectura serverless?</li>
            <li>• Diferencias entre RDS y DynamoDB</li>
            <li>• Mejores prácticas de seguridad en AWS</li>
          </ul>
        </div>
        
        <div className="p-4 bg-green-50 rounded-lg">
          <h3 className="font-semibold text-green-900 mb-2">🚀 Capacidades</h3>
          <ul className="text-green-700 space-y-1">
            <li>• Análisis técnico profundo</li>
            <li>• Recomendaciones personalizadas</li>
            <li>• Explicaciones paso a paso</li>
          </ul>
        </div>
        
        <div className="p-4 bg-purple-50 rounded-lg">
          <h3 className="font-semibold text-purple-900 mb-2">⚡ Modelo actual</h3>
          <ul className="text-purple-700 space-y-1">
            <li>• {model.name} ({model.provider})</li>
            <li>• ${model.costPer1kTokens}/1k tokens</li>
            <li>• Max {model.maxTokens.toLocaleString()} tokens</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
