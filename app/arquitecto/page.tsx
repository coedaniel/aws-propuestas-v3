'use client'

import React, { useState, useRef, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import ModelSelector from '@/components/ModelSelector'
import { ArrowLeft, Send, Loader2, CheckCircle, FileText, Download, Building2 } from 'lucide-react'
import { sendArquitectoRequest } from '@/lib/api'
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
  const [localMessages, setLocalMessages] = useState<Message[]>([
    {
      id: generateId(),
      role: 'assistant',
      content: '¡Hola! Soy tu Arquitecto AWS experto. Vamos a crear una propuesta profesional paso a paso.\n\n**PASO 1:** Para comenzar, necesito que me digas únicamente el **nombre del proyecto**.\n\nEjemplos:\n• "E-commerce Platform"\n• "Sistema de Inventario" \n• "Portal de Clientes"\n• "App de Delivery"\n\n¿Cuál es el nombre de tu proyecto?',
      timestamp: new Date().toISOString()
    }
  ])
  const [localLoading, setLocalLoading] = useState(false)
  const [selectedModel, setSelectedModel] = useState('amazon.nova-pro-v1:0')
  const [mcpServices, setMcpServices] = useState<string[]>([])
  const [showSuccessModal, setShowSuccessModal] = useState(false)
  const [generatedProject, setGeneratedProject] = useState<any>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [localMessages])

  const sendMessage = async () => {
    if (!input.trim() || localLoading) return

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
      const response = await sendArquitectoRequest({
        messages: currentMessages.map(m => ({
          role: m.role,
          content: m.content
        })),
        selected_model: selectedModel
      })

      console.log('Arquitecto response:', response)

      const assistantMessage: Message = {
        id: generateId(),
        role: 'assistant',
        content: response.response || 'Lo siento, no pude generar una respuesta.',
        timestamp: new Date().toISOString(),
        mcpServices: response.mcpServicesUsed || []
      }

      setLocalMessages(prev => [...prev, assistantMessage])
      
      // Actualizar MCP services si los hay
      if (response.mcpServicesUsed && response.mcpServicesUsed.length > 0) {
        setMcpServices(response.mcpServicesUsed)
      }
      
      // Modal solo si REALMENTE generó documentos
      if (response.documentsGenerated && response.documentsGenerated.length > 0) {
        console.log('Documents generated:', response.documentsGenerated)
        setGeneratedProject({
          projectId: response.projectId || generateId(),
          projectName: response.projectName || 'Proyecto AWS',
          documentsGenerated: response.documentsGenerated
        })
        setShowSuccessModal(true)
      }
      
    } catch (error: any) {
      console.error('Error:', error)
      setLocalMessages(prev => [...prev, {
        id: generateId(),
        role: 'assistant',
        content: `Error: ${error.message}`,
        timestamp: new Date().toISOString()
      }])
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

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header - EXACTAMENTE IGUAL QUE CHAT */}
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
                <Building2 className="w-6 h-6 text-blue-600" />
                <div>
                  <h1 className="text-xl font-bold text-gray-900">Arquitecto AWS</h1>
                  <p className="text-sm text-gray-600">Genera propuestas profesionales</p>
                </div>
              </div>
            </div>
            
            <ModelSelector
              selectedModel={selectedModel}
              onModelChange={setSelectedModel}
              disabled={localLoading}
              compact={true}
            />
          </div>
        </div>
      </header>

      {/* Chat Container - EXACTAMENTE IGUAL QUE CHAT */}
      <div className="flex-1 flex flex-col max-w-5xl mx-auto w-full">
        {/* MCP Indicator */}
        {mcpServices.length > 0 && (
          <div className="px-4 pt-4">
            <Card className="mb-4 bg-blue-50 border-blue-200">
              <CardContent className="p-3">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                  <span className="text-sm text-blue-700 font-medium">
                    🔧 MCP Services Activos: {mcpServices.join(', ')}
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Messages - EXACTAMENTE IGUAL QUE CHAT */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="space-y-4">
            {localMessages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <Card className={`max-w-[80%] ${
                  message.role === 'user' 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-white border'
                }`}>
                  <CardContent className="p-4">
                    <div className="whitespace-pre-wrap">{message.content}</div>
                    <div className="flex items-center justify-between mt-2 text-xs opacity-70">
                      <span>{formatDate(message.timestamp)}</span>
                      {message.mcpServices && message.mcpServices.length > 0 && (
                        <span>MCP: {message.mcpServices.join(', ')}</span>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area - EXACTAMENTE IGUAL QUE CHAT */}
        <div className="border-t bg-white p-4">
          <div className="flex gap-2">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Responde las preguntas del arquitecto..."
              className="flex-1 min-h-[60px] resize-none"
              disabled={localLoading}
            />
            <Button
              onClick={sendMessage}
              disabled={!input.trim() || localLoading}
              size="lg"
            >
              {localLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
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
              <CheckCircle className="h-5 w-5 text-green-500" />
              ¡Proyecto Generado!
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              Se ha generado exitosamente el proyecto: <strong>{generatedProject?.projectName}</strong>
            </p>
            <div className="space-y-2">
              <p className="text-sm font-medium">Documentos generados:</p>
              <ul className="text-sm space-y-1">
                {generatedProject?.documentsGenerated?.map((doc: string, index: number) => (
                  <li key={index} className="flex items-center gap-2">
                    <FileText className="h-4 w-4 text-blue-500" />
                    {doc}
                  </li>
                ))}
              </ul>
            </div>
            <div className="flex gap-2">
              <Button
                onClick={() => router.push('/projects')}
                className="flex-1"
              >
                <Download className="h-4 w-4 mr-2" />
                Ver en Proyectos
              </Button>
              <Button
                variant="outline"
                onClick={() => setShowSuccessModal(false)}
              >
                Continuar
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
