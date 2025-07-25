'use client'

import React, { useState, useRef, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import AppLayout from '@/components/AppLayout'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { ModelSelector } from '@/components/ModelSelector'
import { ArrowLeft, Send, Loader2, CheckCircle, FileText, Download } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
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
      content: 'Hola! Soy tu Arquitecto AWS experto. Vamos a crear una propuesta profesional paso a paso. Para comenzar, necesito que me digas únicamente el nombre del proyecto.',
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
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
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
    setInput('')
    setIsLoading(true)

    try {
      const response = await sendArquitectoRequest({
        messages: [...messages, userMessage].map(msg => ({
          role: msg.role,
          content: msg.content
        })),
        modelId: selectedModel
      })

      if (response.response) {
        const assistantMessage: Message = {
          id: generateId(),
          role: 'assistant',
          content: response.response,
          timestamp: new Date().toISOString()
        }

        setMessages(prev => [...prev, assistantMessage])
        
        // Handle project completion
        if (response.isComplete && response.documentsGenerated) {
          setGeneratedProject({
            projectId: response.projectId || 'proyecto-' + Date.now(),
            projectName: response.projectId || 'Proyecto',
            documentsGenerated: response.documentsGenerated
          })
          setShowSuccessModal(true)
        }
      } else {
        const errorMessage: Message = {
          id: generateId(),
          role: 'assistant',
          content: 'Lo siento, hubo un error al procesar tu mensaje. Por favor, intenta de nuevo.',
          timestamp: new Date().toISOString()
        }
        setMessages(prev => [...prev, errorMessage])
      }
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: Message = {
        id: generateId(),
        role: 'assistant',
        content: 'Lo siento, hubo un error de conexión. Por favor, intenta de nuevo.',
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
        content: 'Hola! Soy tu Arquitecto AWS experto. Vamos a crear una propuesta profesional paso a paso. Para comenzar, necesito que me digas únicamente el nombre del proyecto.',
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
              className="hover:bg-slate-100"
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
          
          <div className="flex items-center gap-3">
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
            <div
              key={message.id}
              className={`flex ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[80%] p-3 rounded-lg ${
                  message.role === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown>
                    {message.content}
                  </ReactMarkdown>
                </div>
                {message.mcpServices && message.mcpServices.length > 0 && (
                  <div className="text-xs mt-2 opacity-75">
                    MCP: {message.mcpServices.join(', ')}
                  </div>
                )}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 p-3 rounded-lg">
                <Loader2 className="w-4 h-4 animate-spin" />
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
