'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import ModelSelector from '@/components/ModelSelector'
import { ArrowLeft, Send, Loader2, Building2, Lightbulb } from 'lucide-react'
import { sendArquitectoRequest } from '@/lib/api'
import { AVAILABLE_MODELS } from '@/lib/types'

export default function ArquitectoPage() {
  const router = useRouter()
  const [messages, setMessages] = useState<Array<{role: 'user' | 'assistant', content: string}>>([])
  const [currentInput, setCurrentInput] = useState('')
  const [response, setResponse] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [selectedModel, setSelectedModel] = useState('amazon.nova-pro-v1:0')
  const [projectId, setProjectId] = useState<string | null>(null)
  const [currentStep, setCurrentStep] = useState(0)
  const [isComplete, setIsComplete] = useState(false)

  const currentModel = AVAILABLE_MODELS.find(m => m.id === selectedModel) || AVAILABLE_MODELS[0]

  const handleSubmit = async () => {
    if (!currentInput.trim() || isLoading) return

    setIsLoading(true)
    
    // Add user message to conversation
    const newMessages = [...messages, { role: 'user' as const, content: currentInput.trim() }]
    setMessages(newMessages)
    setCurrentInput('')

    try {
      const data = await sendArquitectoRequest({
        messages: newMessages,
        modelId: selectedModel,
        projectId: projectId || undefined
      })

      // Add assistant response
      setMessages([...newMessages, { role: 'assistant' as const, content: data.response }])
      setResponse(data.response)
      
      // Update project state
      if (data.projectId) setProjectId(data.projectId)
      if (data.currentStep) setCurrentStep(data.currentStep)
      if (data.isComplete !== undefined) setIsComplete(data.isComplete)
      
    } catch (error) {
      console.error('Error calling arquitecto:', error)
      const errorMessage = 'Lo siento, hubo un error al procesar tu solicitud. Por favor, inténtalo de nuevo.'
      setMessages([...newMessages, { role: 'assistant' as const, content: errorMessage }])
      setResponse(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push('/')}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Volver
          </Button>
          <div className="flex items-center gap-2">
            <Building2 className="h-6 w-6 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900">Arquitecto AWS</h1>
          </div>
        </div>

        {/* Model Selector */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="h-5 w-5" />
              Configuración del Modelo
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ModelSelector
              selectedModel={selectedModel}
              onModelChange={setSelectedModel}
            />
          </CardContent>
        </Card>

        {/* Conversation History */}
        {messages.length > 0 && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building2 className="h-5 w-5" />
                Conversación con el Arquitecto
                {projectId && (
                  <span className="text-sm font-normal text-gray-500">
                    (Proyecto: {projectId.slice(0, 8)}... - Paso {currentStep})
                  </span>
                )}
                {isComplete && (
                  <span className="text-sm font-normal text-green-600">
                    ✅ Completado
                  </span>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`p-4 rounded-lg ${
                      message.role === 'user'
                        ? 'bg-blue-50 border-l-4 border-blue-500 ml-8'
                        : 'bg-gray-50 border-l-4 border-gray-500 mr-8'
                    }`}
                  >
                    <div className="text-sm font-medium mb-2">
                      {message.role === 'user' ? '👤 Tú' : '🏗️ Arquitecto AWS'}
                    </div>
                    <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">
                      {message.content}
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="bg-gray-50 border-l-4 border-gray-500 mr-8 p-4 rounded-lg">
                    <div className="text-sm font-medium mb-2">🏗️ Arquitecto AWS</div>
                    <div className="flex items-center gap-2">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span className="text-gray-600">Analizando tu proyecto...</span>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Auto-start welcome message */}
        {messages.length === 0 && !isLoading && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building2 className="h-5 w-5" />
                Arquitecto AWS - Consultor Experto
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-lg mr-8">
                <div className="text-sm font-medium mb-2">🏗️ Arquitecto AWS</div>
                <div className="text-gray-800 leading-relaxed">
                  ¡Hola! Soy tu Arquitecto AWS especializado. Te ayudaré a diseñar una solución profesional completa paso a paso.
                  
                  Puedo ayudarte con dos tipos de proyectos:
                  
                  **🔧 Solución Integral**: Proyecto completo desde cero con arquitectura, documentación y estimaciones detalladas.
                  
                  **⚡ Servicio Rápido**: Consulta específica sobre un tema puntual de AWS.
                  
                  Para comenzar, simplemente describe tu proyecto o necesidad en el campo de abajo.
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Input Section - Always at bottom */}
        <Card className="mb-6">
          <CardContent className="space-y-4 pt-6">
            <Textarea
              value={currentInput}
              onChange={(e) => setCurrentInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={messages.length === 0 ? 
                "Describe tu proyecto o necesidad (ej: 'Necesito un e-commerce que maneje 10,000 productos')" : 
                "Continúa la conversación..."
              }
              className="min-h-[100px] resize-none"
              disabled={isLoading}
            />
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">
                Presiona Enter para enviar, Shift+Enter para nueva línea
              </span>
              <div className="flex gap-2">
                {messages.length > 0 && !isComplete && (
                  <Button
                    variant="outline"
                    onClick={() => {
                      setMessages([])
                      setCurrentInput('')
                      setProjectId(null)
                      setCurrentStep(0)
                      setIsComplete(false)
                      setResponse('')
                    }}
                    className="flex items-center gap-2"
                  >
                    🔄 Nuevo Proyecto
                  </Button>
                )}
                <Button
                  onClick={handleSubmit}
                  disabled={!currentInput.trim() || isLoading}
                  className="flex items-center gap-2"
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                  {isLoading ? 'Consultando...' : messages.length === 0 ? 'Iniciar Consultoría' : 'Enviar'}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Examples - Only show when no conversation */}
        {messages.length === 0 && !isLoading && (
          <Card>
            <CardHeader>
              <CardTitle>Ejemplos de Proyectos</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-semibold mb-2">E-commerce Escalable</h4>
                  <p className="text-sm text-gray-600">
                    "Necesito una plataforma de e-commerce que maneje 50,000 productos, 10,000 usuarios concurrentes, con pagos, inventario y análisis."
                  </p>
                </div>
                <div className="p-4 bg-green-50 rounded-lg">
                  <h4 className="font-semibold mb-2">API Microservicios</h4>
                  <p className="text-sm text-gray-600">
                    "Quiero migrar mi aplicación monolítica a microservicios con alta disponibilidad y auto-escalado."
                  </p>
                </div>
                <div className="p-4 bg-purple-50 rounded-lg">
                  <h4 className="font-semibold mb-2">Data Analytics</h4>
                  <p className="text-sm text-gray-600">
                    "Necesito procesar 1TB de datos diarios, crear dashboards en tiempo real y machine learning."
                  </p>
                </div>
                <div className="p-4 bg-orange-50 rounded-lg">
                  <h4 className="font-semibold mb-2">App Móvil Backend</h4>
                  <p className="text-sm text-gray-600">
                    "Backend para app móvil con autenticación, notificaciones push, chat en tiempo real y geolocalización."
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
