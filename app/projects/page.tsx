'use client'

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { 
  ArrowLeft, 
  Plus, 
  FolderOpen, 
  Calendar,
  DollarSign,
  FileText,
  Loader2,
  Download,
  Eye,
  Trash2,
  CheckCircle,
  Clock
} from 'lucide-react'
import { getProjects, createProject, generateDocuments, deleteProject } from '@/lib/api'

interface Project {
  projectId: string
  projectName: string
  status: string
  currentStep: string
  createdAt: string
  updatedAt: string
  documentCount: number
  hasDocuments: boolean
  projectInfo: any
  lastMessage: string
}

export default function ProjectsPage() {
  const router = useRouter()
  const [projects, setProjects] = useState<Project[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  const [generatingDocs, setGeneratingDocs] = useState<string | null>(null)
  const [deletingProject, setDeletingProject] = useState<string | null>(null)
  const [previewProject, setPreviewProject] = useState<Project | null>(null)

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    requirements: '',
    budget: ''
  })

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      const data = await getProjects()
      setProjects(data)
    } catch (error) {
      console.error('Error loading projects:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateProject = async () => {
    if (!formData.name.trim() || !formData.description.trim()) return

    setIsCreating(true)
    try {
      const requirements = formData.requirements
        .split('\n')
        .map(req => req.trim())
        .filter(req => req.length > 0)

      const newProject = await createProject({
        name: formData.name.trim(),
        description: formData.description.trim(),
        requirements,
        budget: formData.budget ? parseFloat(formData.budget) : undefined
      })

      setProjects([newProject, ...projects])
      setFormData({ name: '', description: '', requirements: '', budget: '' })
      setShowCreateForm(false)
    } catch (error) {
      console.error('Error creating project:', error)
    } finally {
      setIsCreating(false)
    }
  }

  const handleGenerateDocuments = async (projectId: string) => {
    setGeneratingDocs(projectId)
    try {
      await generateDocuments(projectId)
      alert('Documentos generados exitosamente')
      // Reload projects to update document count
      await loadProjects()
    } catch (error) {
      console.error('Error generating documents:', error)
      alert('Error al generar documentos')
    } finally {
      setGeneratingDocs(null)
    }
  }

  const handleDeleteProject = async (projectId: string) => {
    if (!confirm('¿Estás seguro de que deseas eliminar este proyecto? Esta acción eliminará el proyecto de DynamoDB y todos sus documentos de S3. No se puede deshacer.')) return
    
    setDeletingProject(projectId)
    try {
      const result = await deleteProject(projectId)
      if (result.success) {
        // Remove project from local state
        setProjects(prev => prev.filter(p => p.projectId !== projectId))
        alert('Proyecto eliminado exitosamente')
      } else {
        alert(`Error al eliminar proyecto: ${result.message}`)
      }
    } catch (error) {
      console.error('Error deleting project:', error)
      alert('Error al eliminar proyecto. Por favor intenta de nuevo.')
    } finally {
      setDeletingProject(null)
    }
  }

  const handleDownloadDocuments = async (project: Project) => {
    try {
      // TODO: Implement download functionality
      console.log('Download documents for:', project.projectName)
      alert('Funcionalidad de descarga pendiente de implementar')
    } catch (error) {
      console.error('Error downloading documents:', error)
      alert('Error al descargar documentos')
    }
  }

  const formatDate = (timestamp: string) => {
    // Handle both timestamp formats (Unix timestamp and ISO string)
    const date = timestamp.includes('-') ? new Date(timestamp) : new Date(parseInt(timestamp) * 1000)
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const getStatusIcon = (status: string) => {
    return status === 'completed' ? (
      <CheckCircle className="h-4 w-4 text-green-600" />
    ) : (
      <Clock className="h-4 w-4 text-yellow-600" />
    )
  }

  const getStatusColor = (status: string) => {
    return status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 p-4">
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
              <FolderOpen className="h-6 w-6 text-green-600" />
              <h1 className="text-2xl font-bold text-gray-900">Mis Proyectos</h1>
            </div>
          </div>
          <Button
            onClick={() => router.push('/arquitecto')}
            className="flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Nuevo Proyecto
          </Button>
        </div>

        {/* Projects List */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-green-600" />
              <p className="text-gray-600">Cargando proyectos...</p>
            </div>
          </div>
        ) : projects.length === 0 ? (
          <Card>
            <CardContent className="text-center py-12">
              <FolderOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No hay proyectos</h3>
              <p className="text-gray-600 mb-4">Crea tu primer proyecto para comenzar</p>
              <Button onClick={() => router.push('/arquitecto')}>
                <Plus className="h-4 w-4 mr-2" />
                Crear Proyecto
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <Card key={project.projectId} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <CardTitle className="flex items-start justify-between">
                    <span className="line-clamp-2">{project.projectName}</span>
                    <div className="flex flex-col gap-1 ml-2">
                      <Badge className={`flex items-center gap-1 ${getStatusColor(project.status)}`}>
                        {getStatusIcon(project.status)}
                        {project.status === 'completed' ? 'Completado' : 'En Progreso'}
                      </Badge>
                      <Badge variant="outline" className="text-xs">
                        <Calendar className="h-3 w-3 mr-1" />
                        {formatDate(project.createdAt)}
                      </Badge>
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="text-gray-600 text-sm line-clamp-3 font-mono bg-gray-50 p-2 rounded">
                    {project.lastMessage || 'Sin mensajes recientes'}
                  </div>
                  
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4 text-blue-600" />
                      <span>{project.documentCount} documentos</span>
                    </div>
                    <Badge variant={project.hasDocuments ? 'default' : 'secondary'}>
                      {project.hasDocuments ? 'Con documentos' : 'Sin documentos'}
                    </Badge>
                  </div>

                  <div className="flex flex-col gap-2">
                    <div className="flex gap-2">
                      <Button
                        onClick={() => router.push(`/arquitecto?projectId=${project.projectId}`)}
                        variant="outline"
                        size="sm"
                        className="flex-1"
                      >
                        Continuar Chat
                      </Button>
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setPreviewProject(project)}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                        </DialogTrigger>
                        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
                          <DialogHeader>
                            <DialogTitle>Vista Previa - {project.projectName}</DialogTitle>
                          </DialogHeader>
                          <div className="space-y-4">
                            <div>
                              <h4 className="font-semibold mb-2">Estado del Proyecto:</h4>
                              <Badge className={getStatusColor(project.status)}>
                                {project.status === 'completed' ? 'Completado' : 'En Progreso'}
                              </Badge>
                            </div>
                            <div>
                              <h4 className="font-semibold mb-2">Información del Proyecto:</h4>
                              <pre className="bg-gray-100 p-3 rounded text-sm font-mono whitespace-pre-wrap">
                                {JSON.stringify(project.projectInfo, null, 2)}
                              </pre>
                            </div>
                            <div>
                              <h4 className="font-semibold mb-2">Último Mensaje:</h4>
                              <div className="bg-gray-50 p-3 rounded text-sm font-mono whitespace-pre-wrap">
                                {project.lastMessage}
                              </div>
                            </div>
                            <div>
                              <h4 className="font-semibold mb-2">Documentos:</h4>
                              <p>{project.documentCount} documentos generados</p>
                            </div>
                          </div>
                        </DialogContent>
                      </Dialog>
                    </div>
                    
                    <div className="flex gap-2">
                      {project.hasDocuments && (
                        <Button
                          onClick={() => handleDownloadDocuments(project)}
                          variant="outline"
                          size="sm"
                          className="flex-1"
                        >
                          <Download className="h-4 w-4 mr-1" />
                          Descargar
                        </Button>
                      )}
                      <Button
                        onClick={() => handleGenerateDocuments(project.projectId)}
                        disabled={generatingDocs === project.projectId}
                        size="sm"
                        className="flex-1"
                      >
                        {generatingDocs === project.projectId ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <FileText className="h-4 w-4" />
                        )}
                        {generatingDocs === project.projectId ? 'Generando...' : 'Documentos'}
                      </Button>
                      <Button
                        onClick={() => handleDeleteProject(project.projectId)}
                        disabled={deletingProject === project.projectId}
                        variant="destructive"
                        size="sm"
                      >
                        {deletingProject === project.projectId ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <Trash2 className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
