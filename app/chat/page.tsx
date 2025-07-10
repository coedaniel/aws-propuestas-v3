'use client'

import React, { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
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
  Sparkles
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
    setIsLoading,
    setSelectedModel
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
      timestamp: new Date(),
      modelId: selectedModel
    }

    addMessage(userMessage)
    setInput('')
    setIsLoading(true)

    try {
      const { sendChatMessage } = await import('@/lib/api')
      const data = await sendChatMessage({
        messages: [...messages, userMessage].map(m => ({
          role: m.role,
          content: m.content
        })),
        modelId: selectedModel,
        mode: 'chat-libre'
      })

      const assistantMessage: Message = {
        id: generateId(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
        modelId: selectedModel,
        usage: data.usage
      }

      addMessage(assistantMessage)
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: Message = {
        id: generateId(),
        role: 'assistant',
        content: 'Lo siento, hubo un error al procesar tu mensaje. Por favor, inténtalo de nuevo.',
        timestamp: new Date(),
        modelId: selectedModel
      }
      addMessage(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
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
      <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <WelcomeMessage model={currentModel} />
          ) : (
            messages.map((message) => (
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
              <span>{formatDate(message.timestamp)}</span>
              {message.usage && (
                <span>
                  {message.usage.inputTokens}→{message.usage.outputTokens} tokens
                </span>
              )}
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
