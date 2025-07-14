'use client'

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import AppLayout from '@/components/AppLayout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { 
  Plus, 
  Search,
  Calendar,
  DollarSign,
  FileText,
  Loader2,
  Download,
  Eye,
  Trash2,
  CheckCircle,
  Clock,
  Filter,
  MoreVertical,
  ExternalLink
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

interface TypewriterViewerProps {
  content: string
}

function TypewriterViewer({ content }: TypewriterViewerProps) {
  return (
    <div className="space-y-4">
      {/* Content Display - Show complete content immediately */}
      <div className="bg-black text-green-400 p-6 rounded-lg font-mono text-sm max-h-[500px] overflow-y-auto">
        <div className="whitespace-pre-wrap">
          {content}
        </div>
      </div>
    </div>
  )
}

export default function ProjectsPage() {
  const router = useRouter()
  const [projects, setProjects] = useState<Project[]>([])
  const [filteredProjects, setFilteredProjects] = useState<Project[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  const [generatingDocs, setGeneratingDocs] = useState<string | null>(null)
  const [deletingProject, setDeletingProject] = useState<string | null>(null)
  const [previewProject, setPreviewProject] = useState<Project | null>(null)

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    requirements: ['']
  })

  useEffect(() => {
    loadProjects()
  }, [])

  useEffect(() => {
    filterProjects()
  }, [projects, searchTerm, statusFilter])

  const loadProjects = async () => {
    try {
      setIsLoading(true)
      const data = await getProjects()
      setProjects(data)
    } catch (error) {
      console.error('Error loading projects:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const filterProjects = () => {
    let filtered = projects

    if (searchTerm.trim()) {
      const searchLower = searchTerm.toLowerCase()
      filtered = filtered.filter(project => {
        // Search in project name
        const nameMatch = project.projectName?.toLowerCase().includes(searchLower)
        
        // Search in project info
        const infoMatch = project.projectInfo?.description?.toLowerCase().includes(searchLower) ||
                         project.projectInfo?.name?.toLowerCase().includes(searchLower) ||
                         project.projectInfo?.service_focus?.toLowerCase().includes(searchLower)
        
        // Search in project ID
        const idMatch = project.projectId?.toLowerCase().includes(searchLower)
        
        // Search in status
        const statusMatch = project.status?.toLowerCase().includes(searchLower)
        
        return nameMatch || infoMatch || idMatch || statusMatch
      })
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter(project => project.status === statusFilter)
    }

    setFilteredProjects(filtered)
  }

  // Helper function to format dates safely
  const formatDate = (dateString: string | number) => {
    try {
      if (!dateString) return 'Fecha no disponible'
      
      // Handle timestamp (number) or ISO string
      const date = typeof dateString === 'number' 
        ? new Date(dateString * 1000) // Convert from Unix timestamp
        : new Date(dateString)
      
      if (isNaN(date.getTime())) {
        return 'Fecha inválida'
      }
      
      return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch (error) {
      console.error('Error formatting date:', error)
      return 'Fecha inválida'
    }
  }
    if (!formData.name.trim()) return

    setIsCreating(true)
    try {
      const newProject = await createProject({
        name: formData.name.trim(),
        description: formData.description.trim(),
        requirements: formData.requirements.filter(req => req.trim())
      })

      setProjects(prev => [newProject, ...prev])
      setShowCreateForm(false)
      setFormData({ name: '', description: '', requirements: [''] })
      
      // Redirect to architect page with the new project
      router.push(`/arquitecto?projectId=${newProject.projectId}`)
    } catch (error) {
      console.error('Error creating project:', error)
      alert('Error al crear proyecto')
    } finally {
      setIsCreating(false)
    }
  }

  const handleDeleteProject = async (projectId: string) => {
    if (!confirm('¿Estás seguro de que deseas eliminar este proyecto? Esta acción eliminará el proyecto de DynamoDB y todos sus documentos de S3. No se puede deshacer.')) return
    
    setDeletingProject(projectId)
    try {
      const result = await deleteProject(projectId)
      if (result.success) {
        setProjects(prev => prev.filter(p => p.projectId !== projectId))
        alert(`Proyecto eliminado exitosamente. Se eliminaron ${result.deletedFiles} archivos de S3.`)
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

  const handleGenerateDocuments = async (project: Project) => {
    setGeneratingDocs(project.projectId)
    try {
      await generateDocuments(project.projectId)
      alert('Documentos generados exitosamente')
      loadProjects() // Reload to get updated document count
    } catch (error) {
      console.error('Error generating documents:', error)
      alert('Error al generar documentos')
    } finally {
      setGeneratingDocs(null)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED': return 'bg-green-100 text-green-800'
      case 'IN_PROGRESS': return 'bg-blue-100 text-blue-800'
      case 'ARCHIVED': return 'bg-gray-100 text-gray-800'
      case 'DRAFT': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-yellow-100 text-yellow-800'
    }
  }

  const getPreviewContent = (project: Project) => {
    const info = project.projectInfo || {}
    return `# Proyecto: ${project.projectName}

## Información General
- ID: ${project.projectId}
- Estado: ${project.status}
- Paso Actual: ${project.currentStep}
- Creado: ${formatDate(project.createdAt)}
- Actualizado: ${formatDate(project.updatedAt)}

## Detalles del Proyecto
${info.description ? `Descripción: ${info.description}` : ''}
${info.objective ? `Objetivo: ${info.objective}` : ''}
${info.timeline ? `Timeline: ${info.timeline}` : ''}
${info.budget ? `Presupuesto: ${info.budget}` : ''}

## Servicios AWS Detectados
${info.services ? info.services.map((service: string) => `- ${service}`).join('\n') : 'No hay servicios detectados aún'}

## Arquitectura
${info.architecture ? Object.entries(info.architecture).map(([key, value]) => 
  `${key}: ${Array.isArray(value) ? (value as string[]).join(', ') : value}`
).join('\n') : 'Arquitectura no definida'}

## Documentos Generados
- Total de documentos: ${project.documentCount}
- Documentos disponibles: ${project.hasDocuments ? 'Sí' : 'No'}

## Último Mensaje
${project.lastMessage || 'No hay mensajes disponibles'}

---
Fin del resumen del proyecto
`
  }

  return (
    <AppLayout>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Proyectos</h1>
            <p className="text-gray-600">Gestiona tus propuestas AWS y documentos generados</p>
          </div>
          <Dialog open={showCreateForm} onOpenChange={setShowCreateForm}>
            <DialogTrigger asChild>
              <Button className="flex items-center space-x-2">
                <Plus className="h-4 w-4" />
                <span>Nuevo Proyecto</span>
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-md">
              <DialogHeader>
                <DialogTitle>Crear Nuevo Proyecto</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <Input
                  placeholder="Nombre del proyecto"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                />
                <Input
                  placeholder="Descripción (opcional)"
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                />
                <div className="flex space-x-2">
                  <Button
                    onClick={handleCreateProject}
                    disabled={isCreating || !formData.name.trim()}
                    className="flex-1"
                  >
                    {isCreating ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Creando...
                      </>
                    ) : (
                      'Crear Proyecto'
                    )}
                  </Button>
                  <Button variant="outline" onClick={() => setShowCreateForm(false)}>
                    Cancelar
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {/* Filters */}
        <div className="flex items-center space-x-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Buscar proyectos..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md bg-white"
          >
            <option value="all">Todos los estados</option>
            <option value="DRAFT">Borrador</option>
            <option value="IN_PROGRESS">En Progreso</option>
            <option value="COMPLETED">Completados</option>
            <option value="ARCHIVED">Archivados</option>
          </select>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Proyectos</p>
                  <p className="text-2xl font-bold">{projects.length}</p>
                </div>
                <FileText className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Completados</p>
                  <p className="text-2xl font-bold text-green-600">
                    {projects.filter(p => p.status === 'COMPLETED').length}
                  </p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">En Progreso</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {projects.filter(p => p.status === 'IN_PROGRESS').length}
                  </p>
                </div>
                <Clock className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Con Documentos</p>
                  <p className="text-2xl font-bold text-purple-600">
                    {projects.filter(p => p.hasDocuments).length}
                  </p>
                </div>
                <Download className="h-8 w-8 text-purple-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Projects Grid */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin" />
          </div>
        ) : filteredProjects.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {searchTerm || statusFilter !== 'all' ? 'No se encontraron proyectos' : 'No hay proyectos'}
            </h3>
            <p className="text-gray-600 mb-4">
              {searchTerm || statusFilter !== 'all' 
                ? 'Intenta ajustar los filtros de búsqueda'
                : 'Comienza creando tu primer proyecto AWS'
              }
            </p>
            {!searchTerm && statusFilter === 'all' && (
              <Button onClick={() => setShowCreateForm(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Crear Primer Proyecto
              </Button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {filteredProjects.map((project) => (
              <Card key={project.projectId} className="hover:shadow-lg transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg mb-2">{project.projectName}</CardTitle>
                      <div className="flex items-center space-x-2">
                        <Badge className={getStatusColor(project.status)}>
                          {project.status}
                        </Badge>
                        <span className="text-sm text-gray-500">
                          Paso {project.currentStep}
                        </span>
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="text-sm text-gray-600">
                    <div className="flex items-center space-x-2 mb-1">
                      <Calendar className="h-4 w-4" />
                      <span>Creado: {formatDate(project.createdAt)}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <FileText className="h-4 w-4" />
                      <span>{project.documentCount} documentos</span>
                    </div>
                  </div>

                  <div className="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg">
                    <p className="font-medium mb-1">Último mensaje:</p>
                    <p className="line-clamp-2">{project.lastMessage || 'Sin mensajes'}</p>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setPreviewProject(project)}
                          className="flex-1"
                        >
                          <Eye className="h-4 w-4 mr-2" />
                          Vista Previa
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="max-w-6xl max-h-[90vh] overflow-hidden">
                        <DialogHeader>
                          <DialogTitle className="flex items-center justify-between">
                            <span>Vista Previa: {project.projectName}</span>
                            <div className="flex items-center space-x-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => router.push(`/arquitecto?projectId=${project.projectId}`)}
                              >
                                <ExternalLink className="h-4 w-4 mr-2" />
                                Abrir Proyecto
                              </Button>
                            </div>
                          </DialogTitle>
                        </DialogHeader>
                        <div className="overflow-y-auto max-h-[70vh]">
                          <TypewriterViewer
                            content={getPreviewContent(project)}
                          />
                        </div>
                      </DialogContent>
                    </Dialog>

                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => router.push(`/arquitecto?projectId=${project.projectId}`)}
                    >
                      Continuar
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
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  )
}
