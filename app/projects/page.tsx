'use client'

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import AppLayout from '@/components/AppLayout'
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
  FolderOpen,
  AlertCircle,
  RefreshCw
} from 'lucide-react'

interface ProjectDocument {
  fileName: string
  contentType: string
  s3Key: string
  downloadUrl?: string
  error?: string
}

interface Project {
  projectId: string
  projectName: string
  projectType: string
  status: 'completed' | 'in_progress' | 'draft' | 'error'
  createdAt: string
  updatedAt: string
  estimatedCost?: number
  description?: string
  documentsGenerated?: any[]
  s3Folder?: string
  s3Bucket?: string
  totalDocuments?: number
  documentUrls?: ProjectDocument[]
}

interface ProjectStatistics {
  totalProjects: number
  completedProjects: number
  inProgressProjects: number
  totalDocuments: number
}

interface ProjectsResponse {
  projects: Project[]
  statistics: ProjectStatistics
  total: number
  timestamp: string
}

export default function ProjectsPage() {
  const router = useRouter()
  const [projects, setProjects] = useState<Project[]>([])
  const [statistics, setStatistics] = useState<ProjectStatistics>({
    totalProjects: 0,
    completedProjects: 0,
    inProgressProjects: 0,
    totalDocuments: 0
  })
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [typeFilter, setTypeFilter] = useState('all')
  const [statusFilter, setStatusFilter] = useState('all')
  const [selectedProject, setSelectedProject] = useState<Project | null>(null)
  const [showPreview, setShowPreview] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://75bl52azoi.execute-api.us-east-1.amazonaws.com/prod'
      const response = await fetch(`${API_BASE_URL}/projects`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data: ProjectsResponse = await response.json()
      console.log('✅ Projects loaded:', data)
      
      setProjects(data.projects || [])
      setStatistics(data.statistics || {
        totalProjects: 0,
        completedProjects: 0,
        inProgressProjects: 0,
        totalDocuments: 0
      })
      
    } catch (error: any) {
      console.error('❌ Error loading projects:', error)
      setError(error.message || 'Error al cargar proyectos')
      setProjects([])
    } finally {
      setIsLoading(false)
    }
  }

  const loadProjectDetails = async (projectId: string) => {
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://75bl52azoi.execute-api.us-east-1.amazonaws.com/prod'
      const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const project: Project = await response.json()
      console.log('✅ Project details loaded:', project)
      
      setSelectedProject(project)
      setShowPreview(true)
      
    } catch (error: any) {
      console.error('❌ Error loading project details:', error)
      alert(`Error al cargar detalles del proyecto: ${error.message}`)
    }
  }

  const downloadDocument = async (documentUrl: string, fileName: string) => {
    try {
      console.log(`📥 Downloading document: ${fileName}`)
      
      const response = await fetch(documentUrl)
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = fileName
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
      
      console.log(`✅ Document downloaded: ${fileName}`)
      
    } catch (error: any) {
      console.error('❌ Error downloading document:', error)
      alert(`Error al descargar documento: ${error.message}`)
    }
  }

  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.projectName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         project.projectType.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (project.description || '').toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesType = typeFilter === 'all' || project.projectType.toLowerCase().includes(typeFilter.toLowerCase())
    const matchesStatus = statusFilter === 'all' || project.status === statusFilter
    
    return matchesSearch && matchesType && matchesStatus
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      case 'in_progress': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
      case 'draft': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
      case 'error': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed': return 'Completado'
      case 'in_progress': return 'En Progreso'
      case 'draft': return 'Borrador'
      case 'error': return 'Error'
      default: return status
    }
  }

  const getTypeText = (type: string) => {
    if (type.toLowerCase().includes('integral')) return 'Solución Integral'
    if (type.toLowerCase().includes('rapido') || type.toLowerCase().includes('ec2') || type.toLowerCase().includes('rds')) return 'Servicio Rápido'
    return type
  }

  const formatDate = (dateString: string) => {
    if (!dateString) return 'Fecha no disponible'
    try {
      return new Date(dateString).toLocaleDateString('es-ES', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return 'Fecha inválida'
    }
  }

  if (isLoading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4" />
            <p className="text-muted-foreground">Cargando proyectos...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Proyectos</h1>
            <p className="text-muted-foreground">Gestiona y descarga todos tus proyectos generados</p>
          </div>
          
          <div className="flex flex-wrap items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={loadProjects}
              disabled={isLoading}
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Actualizar
            </Button>
            <Button onClick={() => router.push('/arquitecto')}>
              <Plus className="w-4 h-4 mr-2" />
              Nuevo Proyecto
            </Button>
          </div>
        </div>

      {/* Error Message */}
      {error && (
        <Card className="border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950">
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-red-500" />
              <p className="text-red-700 dark:text-red-300">{error}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Proyectos</p>
                <p className="text-2xl font-bold">{statistics.totalProjects}</p>
              </div>
              <FolderOpen className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Completados</p>
                <p className="text-2xl font-bold">{statistics.completedProjects}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">En Progreso</p>
                <p className="text-2xl font-bold">{statistics.inProgressProjects}</p>
              </div>
              <Clock className="w-8 h-8 text-yellow-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Archivos Generados</p>
                <p className="text-2xl font-bold">{statistics.totalDocuments}</p>
              </div>
              <FileText className="w-8 h-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <CardTitle>Filtros y Búsqueda</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
                <Input
                  placeholder="Buscar proyectos..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="px-3 py-2 border border-input bg-background rounded-md"
            >
              <option value="all">Todos los tipos</option>
              <option value="integral">Solución Integral</option>
              <option value="rapido">Servicio Rápido</option>
            </select>
            
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-2 border border-input bg-background rounded-md"
            >
              <option value="all">Todos los estados</option>
              <option value="completed">Completado</option>
              <option value="in_progress">En Progreso</option>
              <option value="draft">Borrador</option>
              <option value="error">Error</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Projects List */}
      <Card>
        <CardHeader>
          <CardTitle>Lista de Proyectos</CardTitle>
          <p className="text-sm text-muted-foreground">
            {filteredProjects.length} de {projects.length} proyectos
          </p>
        </CardHeader>
        <CardContent>
          {filteredProjects.length === 0 ? (
            <div className="text-center py-8">
              <FolderOpen className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">
                {projects.length === 0 ? 'No hay proyectos disponibles' : 'No se encontraron proyectos con los filtros aplicados'}
              </p>
              {projects.length === 0 && (
                <Button 
                  className="mt-4" 
                  onClick={() => router.push('/arquitecto')}
                >
                  Crear Primer Proyecto
                </Button>
              )}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-4 font-medium">Proyecto</th>
                    <th className="text-left p-4 font-medium">Tipo</th>
                    <th className="text-left p-4 font-medium">Estado</th>
                    <th className="text-left p-4 font-medium">Archivos</th>
                    <th className="text-left p-4 font-medium">Fecha</th>
                    <th className="text-left p-4 font-medium">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredProjects.map((project) => (
                    <tr key={project.projectId} className="border-b hover:bg-muted/50">
                      <td className="p-4">
                        <div>
                          <h3 className="font-medium">{project.projectName}</h3>
                          {project.description && (
                            <p className="text-sm text-muted-foreground mt-1">
                              {project.description}
                            </p>
                          )}
                        </div>
                      </td>
                      <td className="p-4">
                        <Badge variant="outline">
                          {getTypeText(project.projectType)}
                        </Badge>
                      </td>
                      <td className="p-4">
                        <Badge className={getStatusColor(project.status)}>
                          {getStatusText(project.status)}
                        </Badge>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <FileText className="w-4 h-4" />
                          <span>{project.totalDocuments || 0}</span>
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="text-sm">
                          <div>{formatDate(project.createdAt)}</div>
                          {project.updatedAt && project.updatedAt !== project.createdAt && (
                            <div className="text-muted-foreground">
                              Actualizado: {formatDate(project.updatedAt)}
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => loadProjectDetails(project.projectId)}
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                          {project.s3Folder && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => loadProjectDetails(project.projectId)}
                            >
                              <Download className="w-4 h-4" />
                            </Button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Project Preview Dialog */}
      <Dialog open={showPreview} onOpenChange={setShowPreview}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{selectedProject?.projectName}</DialogTitle>
          </DialogHeader>
          
          {selectedProject && (
            <div className="space-y-6">
              {/* Project Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium mb-2">Información del Proyecto</h4>
                  <div className="space-y-2 text-sm">
                    <div><strong>Tipo:</strong> {getTypeText(selectedProject.projectType)}</div>
                    <div><strong>Estado:</strong> {getStatusText(selectedProject.status)}</div>
                    <div><strong>Creado:</strong> {formatDate(selectedProject.createdAt)}</div>
                    {selectedProject.updatedAt && (
                      <div><strong>Actualizado:</strong> {formatDate(selectedProject.updatedAt)}</div>
                    )}
                    {selectedProject.estimatedCost && (
                      <div><strong>Costo Estimado:</strong> ${selectedProject.estimatedCost}</div>
                    )}
                  </div>
                </div>
                
                <div>
                  <h4 className="font-medium mb-2">Almacenamiento</h4>
                  <div className="space-y-2 text-sm">
                    <div><strong>Bucket S3:</strong> {selectedProject.s3Bucket}</div>
                    <div><strong>Carpeta:</strong> {selectedProject.s3Folder}</div>
                    <div><strong>Total Documentos:</strong> {selectedProject.totalDocuments || 0}</div>
                  </div>
                </div>
              </div>

              {/* Description */}
              {selectedProject.description && (
                <div>
                  <h4 className="font-medium mb-2">Descripción</h4>
                  <p className="text-sm text-muted-foreground">{selectedProject.description}</p>
                </div>
              )}

              {/* Documents */}
              {selectedProject.documentUrls && selectedProject.documentUrls.length > 0 && (
                <div>
                  <h4 className="font-medium mb-2">Documentos Generados</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {selectedProject.documentUrls.map((doc, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center gap-2">
                          <FileText className="w-4 h-4" />
                          <span className="text-sm">{doc.fileName}</span>
                        </div>
                        {doc.downloadUrl ? (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => downloadDocument(doc.downloadUrl!, doc.fileName)}
                          >
                            <Download className="w-4 h-4" />
                          </Button>
                        ) : (
                          <Badge variant="destructive" className="text-xs">
                            Error
                          </Badge>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
      </div>
    </AppLayout>
  )
}
