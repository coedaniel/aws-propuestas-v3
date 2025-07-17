'use client'

import React, { useState, useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import ModelSelector from '@/components/ModelSelector'
import { MCPTransparency, MCPServiceIndicator, MCPNotification } from '@/components/mcp-transparency'
import { ProjectStatus } from '@/components/project-status'
import { DocumentViewer } from '@/components/document-viewer'
import { ArrowLeft, Send, Loader2, Building2, Lightbulb, FolderOpen, CheckCircle, AlertTriangle, Settings } from 'lucide-react'
import { sendArquitectoRequest, ArquitectoResponse } from '@/lib/api'
import { AVAILABLE_MODELS } from '@/lib/types'
import { detectMCPServices, validateProjectInfo, updateProjectStatus } from '@/lib/mcpIntegration'

function ArquitectoContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const existingProjectId = searchParams.get('projectId')
  
  // Estado local simple como en chat
  const [localMessages, setLocalMessages] = useState<Array<{role: 'user' | 'assistant', content: string, mcpInfo?: any}>>([])
  const [currentInput, setCurrentInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [selectedModel, setSelectedModel] = useState('amazon.nova-pro-v1:0')
  const [mcpServices, setMcpServices] = useState<string[]>([])
  const [showSuccessModal, setShowSuccessModal] = useState(false)
  const [generatedProject, setGeneratedProject] = useState<any>(null)
  const [currentStep, setCurrentStep] = useState(0)
  const [isComplete, setIsComplete] = useState(false)
  const [lastMcpInfo, setLastMcpInfo] = useState<any>(null)
  const [projectCompleted, setProjectCompleted] = useState(false)
  
  // Enhanced project state with professional features
  const [projectInfo, setProjectInfo] = useState({
    name: '',
    type: 'standard' as 'basic' | 'standard' | 'premium',
    services: [] as string[],
    status: 'in_progress' as 'in_progress' | 'completed',
    id: existingProjectId || ''
  })
  const [mcpServices, setMcpServices] = useState<string[]>([])
  const [mcpNotification, setMcpNotification] = useState<{
    message: string
    type: 'info' | 'success' | 'warning' | 'error'
  } | null>(null)
  
  // Project tracking
  const [currentPhase, setCurrentPhase] = useState<'planning' | 'architecture' | 'documentation' | 'costing' | 'completed'>('planning')
  const [documentsGenerated, setDocumentsGenerated] = useState(0)
  const [totalDocuments] = useState(5)
  const [completedTasks, setCompletedTasks] = useState<string[]>([])
  const [pendingTasks, setPendingTasks] = useState<string[]>([
    'Definir arquitectura',
    'Generar diagrama',
    'Crear documentación',
    'Calcular costos',
    'Finalizar proyecto'
  ])
  const [mcpTransparency, setMcpTransparency] = useState<{
    service: string
    action: string
    status: 'preparing' | 'executing' | 'completed' | 'error'
    details?: string
  } | null>(null)

  const currentModel = AVAILABLE_MODELS.find(m => m.id === selectedModel) || AVAILABLE_MODELS[0]

  // Helper functions
  const extractProjectNameFromInput = (input: string): string | null => {
    // Simple extraction - in production this would be more sophisticated
    const patterns = [
      /proyecto\s+([a-zA-Z0-9áéíóúñü\s_-]+)/i,
      /llamado\s+([a-zA-Z0-9áéíóúñü\s_-]+)/i,
      /nombre\s+([a-zA-Z0-9áéíóúñü\s_-]+)/i,
      /"([^"]+)"/g
    ]
    
    for (const pattern of patterns) {
      const match = input.match(pattern)
      if (match && match[1]) {
        return match[1].trim()
      }
    }
    
    // Fallback: look for capitalized words
    const words = input.split(' ')
    for (const word of words) {
      if (word.length > 3 && /^[A-Z]/.test(word) && !/^(Proyecto|Sistema|Aplicacion|Plataforma)$/i.test(word)) {
        return word
      }
    }
    
    return null
  }

  const updateTaskProgress = (taskName: string, completed: boolean) => {
    if (completed) {
      setCompletedTasks(prev => [...prev.filter(t => t !== taskName), taskName])
      setPendingTasks(prev => prev.filter(t => t !== taskName))
    } else {
      setPendingTasks(prev => [...prev.filter(t => t !== taskName), taskName])
      setCompletedTasks(prev => prev.filter(t => t !== taskName))
    }
  }

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

  const handleProjectComplete = async () => {
    try {
      setMcpNotification({
        message: '✅ Voy a usar el MCP `dynamodb` para actualizar el estado del proyecto...',
        type: 'info'
      })
      
      // Actualizar estado en DynamoDB
      const success = await updateProjectStatus(projectInfo.id, 'completed')
      
      if (success) {
        setProjectInfo(prev => ({
          ...prev,
          status: 'completed'
        }))
        
        setMcpNotification({
          message: '✅ Proyecto finalizado exitosamente. Todos los documentos están disponibles para descarga.',
          type: 'success'
        })
        
        setCurrentPhase('completed')
        setIsComplete(true)
        setProjectCompleted(true)
        
        // Marcar todas las tareas como completadas
        setCompletedTasks([
          'Definir arquitectura',
          'Generar diagrama',
          'Crear documentación',
          'Calcular costos',
          'Finalizar proyecto'
        ])
        setPendingTasks([])
        setDocumentsGenerated(totalDocuments)
      } else {
        setMcpNotification({
          message: '❌ Error al actualizar el estado del proyecto en DynamoDB.',
          type: 'error'
        })
      }
      
    } catch (error: any) {
      console.error('Error al finalizar el proyecto:', error)
      setMcpNotification({
        message: `❌ Error al finalizar el proyecto: ${error?.message || 'Error desconocido'}`,
        type: 'error'
      })
    }
  }

  const handleSubmit = async () => {
    if (!currentInput.trim() || isLoading) return

    // Validar información del proyecto
    if (!projectInfo.name) {
      setMcpNotification({
        message: 'Por favor, define un nombre para el proyecto antes de continuar.',
        type: 'warning'
      })
      return
    }

    // Detectar servicios MCP necesarios
    const detectedServices = detectMCPServices(currentInput, messages.map((m: { content: string }) => m.content))
    if (detectedServices.length > 0) {
      setMcpNotification({
        message: `✅ Voy a usar los MCP ${detectedServices.join(', ')} para procesar tu solicitud...`,
        type: 'info'
      })
    }

    setIsLoading(true)
    
    try {
      const userMessage = { role: 'user' as const, content: currentInput.trim() }
      setMessages(prev => [...prev, userMessage])
      setCurrentInput('')
      
      const response = await sendArquitectoRequest({
        messages: [...messages, userMessage],
        projectId: projectInfo.id,
        project_info: projectInfo,
        query: currentInput,
        selected_model: selectedModel
      })
      
      setMessages(prev => [...prev, { role: 'assistant', content: response.response }])
      
      // Actualizar información del proyecto
      if (response.projectInfo) {
        setProjectInfo(prev => ({
          ...prev,
          ...response.projectInfo,
          id: response.projectId || prev.id
        }))
      }
      
      // Actualizar servicios MCP utilizados
      if (response.mcpServicesUsed && response.mcpServicesUsed.length > 0) {
        setMcpServices(response.mcpServicesUsed)
      }
      
      // Si se generaron documentos, mostrar notificación
      if (response.documentsGenerated) {
        setMcpNotification({
          message: '✅ Documentos generados exitosamente. Puedes descargarlos desde el panel de documentos.',
          type: 'success'
        })
        setDocumentsGenerated(prev => prev + 1)
      }
      
    } catch (error: any) {
      console.error('Error en la solicitud:', error)
      setMcpNotification({
        message: `❌ Error: ${error?.message || 'Error desconocido'}`,
        type: 'error'
      })
    } finally {
      setIsLoading(false)
      
      // Limpiar notificación después de 5 segundos
      setTimeout(() => {
        setMcpNotification(null)
      }, 5000)
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
      <div className="max-w-6xl mx-auto">
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

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Panel principal */}
          <div className="lg:col-span-2">
            {/* Notificaciones MCP */}
            {mcpNotification && (
              <MCPNotification 
                message={mcpNotification.message} 
                type={mcpNotification.type} 
              />
            )}
            
            {/* Mensajes */}
            <Card className="mb-4">
              <CardHeader>
                <CardTitle>Conversación con el Arquitecto</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4 mb-4 max-h-96 overflow-y-auto">
                  {messages.length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      <Building2 className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                      <p>¡Hola! Soy tu Arquitecto AWS.</p>
                      <p className="text-sm mt-2">Describe tu arquitectura AWS para comenzar...</p>
                    </div>
                  )}
                  
                  {messages.map((message, index) => (
                    <div key={index}>
                      <div
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
                      
                      {/* MCP Service Indicator */}
                      {message.role === 'assistant' && message.mcpInfo && message.mcpInfo.mcpServicesUsed.length > 0 && (
                        <div className="mr-8 mt-2">
                          <MCPServiceIndicator services={message.mcpInfo.mcpServicesUsed} />
                        </div>
                      )}
                    </div>
                  ))}
                  
                  {isLoading && (
                    <div className="bg-gray-100 mr-8 p-3 rounded-lg">
                      <div className="text-sm font-medium mb-1">Arquitecto AWS</div>
                      <div className="flex items-center gap-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span>Analizando consulta y preparando servicios MCP...</span>
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
                    placeholder="Describe tu arquitectura AWS..."
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
            
            {/* Servicios MCP utilizados */}
            {mcpServices.length > 0 && (
              <div className="mb-4">
                <MCPServiceIndicator services={mcpServices} />
              </div>
            )}
          </div>
          
          {/* Panel lateral */}
          <div className="space-y-6">
            {/* Información del proyecto */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5" />
                  Información del Proyecto
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Nombre del Proyecto</label>
                  <Input
                    type="text"
                    value={projectInfo.name}
                    onChange={(e) => setProjectInfo(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="Ej: ecommerce-aws"
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Tipo de Solución</label>
                  <Select
                    value={projectInfo.type}
                    onValueChange={(value: 'basic' | 'standard' | 'premium') => 
                      setProjectInfo(prev => ({ ...prev, type: value }))
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="basic">Básica</SelectItem>
                      <SelectItem value="standard">Estándar</SelectItem>
                      <SelectItem value="premium">Premium</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                {/* Selector de modelo */}
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Modelo de IA</label>
                  <ModelSelector
                    selectedModel={selectedModel}
                    onModelChange={setSelectedModel}
                    disabled={isLoading}
                  />
                </div>
                
                {/* Botón para finalizar proyecto */}
                {projectInfo.id && (
                  <Button
                    onClick={handleProjectComplete}
                    disabled={projectInfo.status === 'completed'}
                    className="w-full"
                    variant={projectInfo.status === 'completed' ? 'outline' : 'default'}
                  >
                    {projectInfo.status === 'completed' ? (
                      <>
                        <CheckCircle className="h-4 w-4 mr-2" />
                        Proyecto Finalizado
                      </>
                    ) : (
                      <>
                        <CheckCircle className="h-4 w-4 mr-2" />
                        Finalizar Proyecto
                      </>
                    )}
                  </Button>
                )}
              </CardContent>
            </Card>
            
            {/* Estado del proyecto */}
            {projectInfo.id && (
              <ProjectStatus
                projectName={projectInfo.name}
                documentsGenerated={documentsGenerated}
                totalDocuments={totalDocuments}
                pendingTasks={pendingTasks}
                completedTasks={completedTasks}
                currentPhase={currentPhase}
              />
            )}
            
            {/* Visor de documentos */}
            {projectInfo.id && (
              <DocumentViewer
                projectName={projectInfo.name}
                s3Folder={`proyectos/${projectInfo.name}`}
              />
            )}
          </div>
        </div>
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
