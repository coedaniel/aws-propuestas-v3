'use client'

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
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
  ExternalLink,
  FolderOpen
} from 'lucide-react'
import { getProjects, deleteProject } from '@/lib/api'

interface Project {
  projectId: string
  projectName: string
  projectType: string
  status: 'completed' | 'in_progress' | 'draft'
  createdAt: string
  updatedAt: string
  estimatedCost?: number
  description?: string
  documentsGenerated?: string[]
  s3Folder?: string
}

export default function ProjectsPage() {
  const router = useRouter()
  const [projects, setProjects] = useState<Project[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedProject, setSelectedProject] = useState<Project | null>(null)
  const [showPreview, setShowPreview] = useState(false)

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      setIsLoading(true)
      const response = await getProjects()
      console.log('Projects loaded:', response)
      setProjects(response.projects || [])
    } catch (error) {
      console.error('Error loading projects:', error)
      setProjects([])
    } finally {
      setIsLoading(false)
    }
  }

  const filteredProjects = projects.filter(project =>
    project.projectName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    project.projectType.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800'
      case 'in_progress': return 'bg-blue-100 text-blue-800'
      case 'draft': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-4 w-4" />
      case 'in_progress': return <Clock className="h-4 w-4" />
      default: return <FileText className="h-4 w-4" />
    }
  }

  const handlePreview = (project: Project) => {
    setSelectedProject(project)
    setShowPreview(true)
  }

  const handleDownload = (project: Project) => {
    // Abrir S3 bucket folder
    const s3Url = `https://aws-propuestas-v3-documents-prod-035385358261.s3.amazonaws.com/${project.s3Folder}/`
    window.open(s3Url, '_blank')
  }

  const handleDelete = async (projectId: string) => {
    if (confirm('¿Estás seguro de eliminar este proyecto?')) {
      try {
        await deleteProject(projectId)
        setProjects(prev => prev.filter(p => p.projectId !== projectId))
      } catch (error) {
        console.error('Error deleting project:', error)
      }
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p>Cargando proyectos...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">Proyectos AWS</h1>
              <p className="text-gray-600">Gestiona tus propuestas y documentos generados</p>
            </div>
            <Button onClick={() => router.push('/arquitecto')}>
              <Plus className="h-4 w-4 mr-2" />
              Nuevo Proyecto
            </Button>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="container mx-auto px-4 py-6">
        {/* Search */}
        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              placeholder="Buscar proyectos..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Proyectos</p>
                  <p className="text-2xl font-bold">{projects.length}</p>
                </div>
                <FolderOpen className="h-8 w-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Completados</p>
                  <p className="text-2xl font-bold text-green-600">
                    {projects.filter(p => p.status === 'completed').length}
                  </p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-500" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">En Progreso</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {projects.filter(p => p.status === 'in_progress').length}
                  </p>
                </div>
                <Clock className="h-8 w-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Projects Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.map((project) => (
            <Card key={project.projectId} className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg mb-1">{project.projectName}</CardTitle>
                    <p className="text-sm text-gray-600">{project.projectType}</p>
                  </div>
                  <Badge className={getStatusColor(project.status)}>
                    <div className="flex items-center gap-1">
                      {getStatusIcon(project.status)}
                      {project.status}
                    </div>
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-gray-700 line-clamp-2">
                  {project.description || 'Proyecto generado por el Arquitecto AWS'}
                </p>
                
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <div className="flex items-center gap-1">
                    <Calendar className="h-4 w-4" />
                    {new Date(project.createdAt).toLocaleDateString()}
                  </div>
                  {project.estimatedCost && (
                    <div className="flex items-center gap-1">
                      <DollarSign className="h-4 w-4" />
                      ${project.estimatedCost}
                    </div>
                  )}
                </div>

                <div className="space-y-2">
                  <p className="text-xs font-medium text-gray-700">Documentos:</p>
                  <div className="flex flex-wrap gap-1">
                    {project.documentsGenerated?.slice(0, 2).map((doc, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {doc.replace(/\.(json|csv|md)$/, '')}
                      </Badge>
                    ))}
                    {project.documentsGenerated && project.documentsGenerated.length > 2 && (
                      <Badge variant="outline" className="text-xs">
                        +{project.documentsGenerated.length - 2} más
                      </Badge>
                    )}
                  </div>
                </div>

                <div className="flex gap-2 pt-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handlePreview(project)}
                    className="flex-1"
                  >
                    <Eye className="h-4 w-4 mr-1" />
                    Vista Previa
                  </Button>
                  <Button
                    size="sm"
                    onClick={() => handleDownload(project)}
                    className="flex-1"
                  >
                    <Download className="h-4 w-4 mr-1" />
                    Descargar
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleDelete(project.projectId)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {filteredProjects.length === 0 && !isLoading && (
          <div className="text-center py-12">
            <FolderOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {projects.length === 0 ? 'No hay proyectos' : 'No se encontraron proyectos'}
            </h3>
            <p className="text-gray-600 mb-4">
              {projects.length === 0 
                ? 'Comienza creando tu primer proyecto AWS' 
                : 'Intenta con otros términos de búsqueda'
              }
            </p>
            {projects.length === 0 && (
              <Button onClick={() => router.push('/arquitecto')}>
                <Plus className="h-4 w-4 mr-2" />
                Crear Proyecto
              </Button>
            )}
          </div>
        )}
      </div>

      {/* Preview Modal */}
      <Dialog open={showPreview} onOpenChange={setShowPreview}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              {selectedProject?.projectName}
            </DialogTitle>
          </DialogHeader>
          {selectedProject && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium text-gray-700">Tipo</p>
                  <p className="text-sm">{selectedProject.projectType}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-700">Estado</p>
                  <Badge className={getStatusColor(selectedProject.status)}>
                    {selectedProject.status}
                  </Badge>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-700">Creado</p>
                  <p className="text-sm">{new Date(selectedProject.createdAt).toLocaleDateString()}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-700">Costo Estimado</p>
                  <p className="text-sm">${selectedProject.estimatedCost}</p>
                </div>
              </div>

              <div>
                <p className="text-sm font-medium text-gray-700 mb-2">Descripción</p>
                <p className="text-sm text-gray-600">{selectedProject.description}</p>
              </div>

              <div>
                <p className="text-sm font-medium text-gray-700 mb-3">Documentos Generados</p>
                <div className="space-y-2">
                  {selectedProject.documentsGenerated?.map((doc, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4 text-blue-500" />
                        <span className="text-sm">{doc}</span>
                      </div>
                      <Button size="sm" variant="ghost">
                        <ExternalLink className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex gap-2">
                <Button onClick={() => handleDownload(selectedProject)} className="flex-1">
                  <Download className="h-4 w-4 mr-2" />
                  Descargar Todo
                </Button>
                <Button variant="outline" onClick={() => setShowPreview(false)}>
                  Cerrar
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
