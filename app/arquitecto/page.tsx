'use client'

import React, { useState, useRef, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import ModelSelector from '@/components/ModelSelector'
import { ArrowLeft, Send, Loader2, CheckCircle, FileText, Download } from 'lucide-react'
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
  const [generatedProject, setGeneratedProject] = useState<any>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const detectMCPServices = (input: string): string[] => {
    const services: string[] = []
    const text = input.toLowerCase()
    
    if (text.includes('diagrama') || text.includes('arquitectura')) {
      services.push('diagram')
    }
    if (text.includes('costo') || text.includes('precio')) {
      services.push('pricing')
    }
    if (text.includes('documento') || text.includes('generar')) {
      services.push('documents')
    }
    
    return services
  }

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

    // Detectar MCP services
    const detectedServices = detectMCPServices(input)
    if (detectedServices.length > 0) {
      setMcpServices(detectedServices)
    }

    try {
      const response = await sendArquitectoRequest({
        messages: currentMessages.map(m => ({
          role: m.role,
          content: m.content
        })),
        selected_model: selectedModel
      })

      const assistantMessage: Message = {
        id: generateId(),
        role: 'assistant',
        content: response.response || 'Lo siento, no pude generar una respuesta.',
        timestamp: new Date().toISOString(),
        mcpServices: response.mcpServicesUsed || []
      }

      setMessages(prev => [...prev, assistantMessage])
      
      // Solo mostrar modal si REALMENTE se generaron documentos
      // Buscar palabras clave específicas que indiquen generación completa
      const responseText = response.response.toLowerCase()
      const hasGenerated = (responseText.includes('generado') && responseText.includes('documento')) ||
                          responseText.includes('cloudformation') ||
                          (responseText.includes('subir') && responseText.includes('s3')) ||
                          response.documentsGenerated ||
                          response.projectId
      
      if (hasGenerated) {
        setGeneratedProject({
          projectId: response.projectId || generateId(),
          projectName: response.projectName || 'Proyecto AWS',
          documentsGenerated: response.documentsGenerated || ['CloudFormation', 'Costos', 'Diagrama']
        })
        setShowSuccessModal(true)
      }
      
    } catch (error: any) {
      console.error('Error:', error)
      setMessages(prev => [...prev, {
        id: generateId(),
        role: 'assistant',
        content: `Error: ${error.message}`,
        timestamp: new Date().toISOString()
      }])
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
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="border-b bg-white sticky top-0 z-50 shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => router.push('/')}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Inicio
              </Button>
              <h1 className="text-xl font-semibold">Arquitecto AWS</h1>
            </div>
            <ModelSelector
              selectedModel={selectedModel}
              onModelChange={setSelectedModel}
            />
          </div>
        </div>
      </header>

      {/* Main Content - Full Height */}
      <div className="flex-1 flex flex-col">
        {/* MCP Services Indicator */}
        {mcpServices.length > 0 && (
          <div className="px-4 pt-4">
            <Card className="bg-blue-50 border-blue-200">
              <CardContent className="p-3">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                  <span className="text-sm text-blue-700">
                    🔧 Usando MCP: {mcpServices.join(', ')}
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Messages Container - Scrollable */}
        <div className="flex-1 overflow-y-auto px-4 py-4">
          <div className="max-w-4xl mx-auto space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <Card className={`max-w-[85%] ${
                  message.role === 'user' 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-white border shadow-sm'
                }`}>
                  <CardContent className="p-4">
                    <div className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</div>
                    <div className="flex items-center justify-between mt-3 text-xs opacity-70">
                      <span>{formatDate(message.timestamp)}</span>
                      {message.mcpServices && message.mcpServices.length > 0 && (
                        <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded">
                          MCP: {message.mcpServices.join(', ')}
                        </span>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area - Fixed Bottom */}
        <div className="border-t bg-white p-4 shadow-lg">
          <div className="max-w-4xl mx-auto">
            <div className="flex gap-3">
              <Textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Responde paso a paso las preguntas del arquitecto..."
                className="flex-1 min-h-[80px] resize-none text-sm"
                disabled={isLoading}
              />
              <Button
                onClick={sendMessage}
                disabled={!input.trim() || isLoading}
                size="lg"
                className="px-6"
              >
                {isLoading ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <Send className="h-5 w-5" />
                )}
              </Button>
            </div>
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
