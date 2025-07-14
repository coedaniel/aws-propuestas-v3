'use client'

import React, { useState, useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import ModelSelector from '@/components/ModelSelector'
import { ArrowLeft, Send, Loader2, Building2, Lightbulb, FolderOpen } from 'lucide-react'
import { sendArquitectoRequest } from '@/lib/api'
import { AVAILABLE_MODELS } from '@/lib/types'

function ArquitectoContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const existingProjectId = searchParams.get('projectId')
  
  const [messages, setMessages] = useState<Array<{role: 'user' | 'assistant', content: string}>>([])
  const [currentInput, setCurrentInput] = useState('')
  const [response, setResponse] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingProject, setIsLoadingProject] = useState(false)
  const [selectedModel, setSelectedModel] = useState('amazon.nova-pro-v1:0')
  const [projectId, setProjectId] = useState<string | null>(existingProjectId)
  const [currentStep, setCurrentStep] = useState(0)
  const [isComplete, setIsComplete] = useState(false)

  const currentModel = AVAILABLE_MODELS.find(m => m.id === selectedModel) || AVAILABLE_MODELS[0]

  // Load existing project if projectId is provided
  useEffect(() => {
    if (existingProjectId) {
      loadExistingProject(existingProjectId)
    } else {
      // Initialize with welcome message for new projects
      setMessages([{
        role: 'assistant',
        content: '¡Hola! Soy tu Arquitecto AWS. Para comenzar, necesito que me proporciones únicamente el **nombre del proyecto** (por ejemplo: "E-commerce Platform", "Sistema de Inventario", "Portal de Clientes", etc.). ¿Cuál es el nombre de tu proyecto?'
      }])
    }
  }, [existingProjectId])

  const loadExistingProject = async (projectId: string) => {
    setIsLoadingProject(true)
    try {
      // TODO: Implement API call to get project details
      // For now, we'll just set the projectId and let the user continue
      setProjectId(projectId)
      
      // Add a system message to indicate continuation
      setMessages([{
        role: 'assistant',
        content: 'Continuando con el proyecto existente. ¿En qué puedo ayudarte?'
      }])
    } catch (error) {
      console.error('Error loading project:', error)
      // If loading fails, start fresh but keep the projectId
      setMessages([{
        role: 'assistant',
        content: '¡Hola! Soy tu Arquitecto AWS. Para comenzar, necesito que me proporciones únicamente el **nombre del proyecto** (por ejemplo: "E-commerce Platform", "Sistema de Inventario", "Portal de Clientes", etc.). ¿Cuál es el nombre de tu proyecto?'
      }])
    } finally {
      setIsLoadingProject(false)
    }
  }

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
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
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
              <h1 className="text-2xl font-bold text-gray-900">
                Arquitecto AWS
                {existingProjectId && (
                  <span className="text-sm font-normal text-gray-600 ml-2">
                    (Continuando proyecto)
                  </span>
                )}
              </h1>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => router.push('/projects')}
            className="flex items-center gap-2"
          >
            <FolderOpen className="h-4 w-4" />
            Ver Proyectos
          </Button>
        </div>

        {/* Loading Project State */}
        {isLoadingProject && (
          <Card className="mb-6">
            <CardContent className="flex items-center justify-center py-8">
              <div className="text-center">
                <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
                <p className="text-gray-600">Cargando proyecto existente...</p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Model Selector - Compact */}
        <div className="mb-4">
          <div className="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
            <ModelSelector
              selectedModel={selectedModel}
              onModelChange={setSelectedModel}
              disabled={isLoading}
              compact={true}
            />
          </div>
        </div>

        {/* Chat Interface */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Conversación con el Arquitecto</CardTitle>
          </CardHeader>
          <CardContent>
            {/* Messages */}
            <div className="space-y-4 mb-4 max-h-96 overflow-y-auto">
              {messages.length === 0 && !existingProjectId && (
                <div className="text-center py-8 text-gray-500">
                  <Building2 className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <p>¡Hola! Soy tu Arquitecto AWS.</p>
                  <p className="text-sm mt-2">¿Cuál es el nombre del proyecto?</p>
                </div>
              )}
              
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`p-3 rounded-lg ${
                    message.role === 'user'
                      ? 'bg-blue-100 ml-8'
                      : 'bg-gray-100 mr-8'
                  }`}
                >
                  <div className="text-sm font-medium mb-1">
                    {message.role === 'user' ? 'Tú' : 'Arquitecto AWS'}
                  </div>
                  <div className="whitespace-pre-wrap">{message.content}</div>
                </div>
              ))}
              
              {isLoading && (
                <div className="bg-gray-100 mr-8 p-3 rounded-lg">
                  <div className="text-sm font-medium mb-1">Arquitecto AWS</div>
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Pensando...</span>
                  </div>
                </div>
              )}
            </div>

            {/* Input */}
            <div className="flex gap-2">
              <Textarea
                value={currentInput}
                onChange={(e) => setCurrentInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Escribe tu mensaje aquí..."
                className="flex-1"
                disabled={isLoading}
                rows={3}
              />
              <Button
                onClick={handleSubmit}
                disabled={!currentInput.trim() || isLoading}
                className="px-6"
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Project Status */}
        {projectId && (
          <Card>
            <CardHeader>
              <CardTitle>Estado del Proyecto</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <div className="font-medium text-gray-600">ID del Proyecto</div>
                  <div className="font-mono text-xs">{projectId}</div>
                </div>
                <div>
                  <div className="font-medium text-gray-600">Paso Actual</div>
                  <div>{currentStep}</div>
                </div>
                <div>
                  <div className="font-medium text-gray-600">Estado</div>
                  <div className={isComplete ? 'text-green-600' : 'text-yellow-600'}>
                    {isComplete ? 'Completado' : 'En Progreso'}
                  </div>
                </div>
                <div>
                  <div className="font-medium text-gray-600">Modelo</div>
                  <div className="text-xs">{currentModel.name}</div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}

export default function ArquitectoPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600">Cargando...</p>
        </div>
      </div>
    }>
      <ArquitectoContent />
    </Suspense>
  )
}
