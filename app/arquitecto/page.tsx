'use client'

import React, { useState, useRef, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import AppLayout from '@/components/AppLayout'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { ModelSelector } from '@/components/ModelSelector'
import { ArrowLeft, Send, Loader2, CheckCircle, FileText, Download, Bot, User } from 'lucide-react'
import { sendArquitectoRequest } from '@/lib/api'
import type { ArquitectoResponse, ProjectState, GeneratedProject } from './types'
import { generateId, formatDate } from '@/lib/utils'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  mcpServices?: string[]
}

export default function ArquitectoPage() {
  const router = useRouter()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<Message[]>([
    {
      id: generateId(),
      role: 'assistant',
      content: '¡Hola! Soy tu Arquitecto AWS experto. Vamos a crear una propuesta profesional paso a paso.\n\n**PASO 1:** Para comenzar, necesito que me digas únicamente el **nombre del proyecto**.\n\nEjemplos:\n• "E-commerce Platform"\n• "Sistema de Inventario" \n• "Portal de Clientes"\n• "App de Delivery"\n\n¿Cuál es el nombre de tu proyecto?',
      timestamp: new Date().toISOString()
    }
  ])
  const [isLoading, setIsLoading] = useState(false)
  const [selectedModel, setSelectedModel] = useState('amazon.nova-pro-v1:0')
  const [mcpServices, setMcpServices] = useState<string[]>([])
  const [showSuccessModal, setShowSuccessModal] = useState(false)
  const [generatedProject, setGeneratedProject] = useState<GeneratedProject | null>(null)
  const [projectState, setProjectState] = useState<ProjectState>({
    phase: 'inicio',
    data: {}
  })

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: generateId(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    const currentMessages = [...messages, userMessage]
    
    setInput('')
    setIsLoading(true)

    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod'
      
      console.log('🚀 Enviando mensaje a:', `${API_BASE_URL}/arquitecto`)
      
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
        content: data.content || data.response || 'Lo siento, no pude generar una respuesta.',
        timestamp: new Date().toISOString(),
        mcpServices: data.mcpUsed || []
      }

      setMessages(prev => [...prev, assistantMessage])
      
      // Actualizar estado del proyecto si se proporciona
      if (data.projectState) {
        setProjectState(prev => ({ ...prev, ...data.projectState }))
      }
      
      // Actualizar servicios MCP
      if (data.mcpUsed && data.mcpUsed.length > 0) {
        setMcpServices(data.mcpUsed)
      }

      // Verificar si se generaron documentos
      if (data.documentsGenerated && data.documentsGenerated.length > 0) {
        setGeneratedProject({
          projectId: generateId(),
          projectName: projectState.name || 'Proyecto',
          documentsGenerated: data.documentsGenerated
        })
        setShowSuccessModal(true)
      }
      
    } catch (error: any) {
      console.error('❌ Error completo:', error)
      const errorMessage: Message = {
        id: generateId(),
        role: 'assistant',
        content: `Error al procesar la solicitud: ${error?.message || 'Error desconocido'}`,
        timestamp: new Date().toISOString()
      }
      
      setMessages(prev => [...prev, errorMessage])
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

  const clearChat = () => {
    setMessages([
      {
        id: generateId(),
        role: 'assistant',
        content: '¡Hola! Soy tu Arquitecto AWS experto. Vamos a crear una propuesta profesional paso a paso.\n\n**PASO 1:** Para comenzar, necesito que me digas únicamente el **nombre del proyecto**.\n\nEjemplos:\n• "E-commerce Platform"\n• "Sistema de Inventario" \n• "Portal de Clientes"\n• "App de Delivery"\n\n¿Cuál es el nombre de tu proyecto?',
        timestamp: new Date().toISOString()
      }
    ])
    setProjectState({ phase: 'inicio', data: {} })
    setMcpServices([])
  }

  return (
    <AppLayout>
      <div className="flex h-full flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.push('/')}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Volver
            </Button>
            <div>
              <h1 className="text-xl font-semibold">Arquitecto AWS</h1>
              <p className="text-sm text-muted-foreground">
                Fase: {projectState.phase} {projectState.name ? `• ${projectState.name}` : ''}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <ModelSelector
              selectedModel={selectedModel}
              onModelChange={setSelectedModel}
            />
            <Button variant="outline" size="sm" onClick={clearChat}>
              Limpiar Chat
            </Button>
          </div>
        </div>

        {/* MCP Services Indicator */}
        {mcpServices.length > 0 && (
          <div className="bg-purple-50 border-b px-4 py-2">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-purple-700">
                🔧 MCP Services: {mcpServices.join(', ')}
              </span>
            </div>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`flex gap-3 max-w-[80%] ${message.role === 'user' ? 'flex-row-reverse' : ''}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  message.role === 'user' 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-purple-500 text-white'
                }`}>
                  {message.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                </div>
                
                <Card className={`${
                  message.role === 'user' 
                    ? 'bg-blue-50 border-blue-200' 
                    : 'bg-white border-gray-200'
                }`}>
                  <CardContent className="p-4">
                    <div className="whitespace-pre-wrap text-sm">{message.content}</div>
                    <div className="flex items-center justify-between mt-2 text-xs text-muted-foreground">
                      <span>{formatDate(message.timestamp)}</span>
                      {message.mcpServices && message.mcpServices.length > 0 && (
                        <span className="text-purple-600">MCP: {message.mcpServices.join(', ')}</span>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="flex gap-3 max-w-[80%]">
                <div className="w-8 h-8 rounded-full bg-purple-500 text-white flex items-center justify-center">
                  <Bot className="w-4 h-4" />
                </div>
                <Card className="bg-white border-gray-200">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span className="text-sm">Procesando...</span>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t p-4">
          <div className="flex gap-2">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Escribe tu mensaje aquí..."
              className="flex-1 min-h-[60px] resize-none"
              disabled={isLoading}
            />
            <Button
              onClick={sendMessage}
              disabled={!input.trim() || isLoading}
              size="lg"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </Button>
          </div>
        </div>
      </div>

      {/* Success Modal */}
      <Dialog open={showSuccessModal} onOpenChange={setShowSuccessModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-500" />
              ¡Proyecto Completado!
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Se han generado todos los documentos para tu proyecto.
            </p>
            {generatedProject && (
              <div className="space-y-2">
                <h4 className="font-medium">{generatedProject.projectName}</h4>
                <div className="space-y-1">
                  {generatedProject.documentsGenerated.map((doc, index) => (
                    <div key={index} className="flex items-center justify-between text-sm">
                      <span className="flex items-center gap-2">
                        <FileText className="w-4 h-4" />
                        {doc.name}
                      </span>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => window.open(doc.url, '_blank')}
                      >
                        <Download className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            )}
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => router.push('/projects')}
                className="flex-1"
              >
                Ver Proyectos
              </Button>
              <Button
                onClick={() => setShowSuccessModal(false)}
                className="flex-1"
              >
                Continuar
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </AppLayout>
  )
}
