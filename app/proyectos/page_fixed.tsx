'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { 
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { 
  FolderOpen, 
  Search, 
  Download, 
  Eye, 
  Calendar,
  FileText,
  Image,
  FileSpreadsheet,
  Code,
  CheckCircle,
  XCircle,
  Clock,
  Filter,
  MoreHorizontal,
  ExternalLink,
  Trash2,
  Edit,
  RefreshCw,
  AlertCircle,
  Loader2
} from 'lucide-react'

interface Project {
  id: string
  name: string
  type: 'servicio-rapido' | 'solucion-integral'
  status: 'completado' | 'en-progreso' | 'error'
  createdAt: string
  updatedAt: string
  files: {
    word?: boolean
    csv?: boolean
    yaml?: boolean
    png?: boolean
    svg?: boolean
  }
  description: string
  s3Folder?: string
  s3Bucket?: string
}

interface ProjectStatistics {
  total_projects: number
  completed_projects: number
  in_progress_projects: number
  error_projects: number
  total_files: number
  by_type: {
    servicio_rapido: number
    solucion_integral: number
  }
}

export default function ProyectosPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const [statistics, setStatistics] = useState<ProjectStatistics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState<'all' | 'servicio-rapido' | 'solucion-integral'>('all')
  const [filterStatus, setFilterStatus] = useState<'all' | 'completado' | 'en-progreso' | 'error'>('all')
  const [downloadingFiles, setDownloadingFiles] = useState<Set<string>>(new Set())

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod'

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await fetch(`${API_BASE_URL}/projects`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      
      setProjects(data.projects || [])
      setStatistics(data.statistics || null)
      
    } catch (error: any) {
      console.error('Error loading projects:', error)
      setError(error.message || 'Error desconocido al cargar proyectos')
    } finally {
      setLoading(false)
    }
  }

  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         project.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = filterType === 'all' || project.type === filterType
    const matchesStatus = filterStatus === 'all' || project.status === filterStatus
    
    return matchesSearch && matchesType && matchesStatus
  })

  const getStatusIcon = (status: Project['status']) => {
    switch (status) {
      case 'completado':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'en-progreso':
        return <Clock className="w-4 h-4 text-yellow-500" />
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" />
    }
  }

  const getStatusBadge = (status: Project['status']) => {
    switch (status) {
      case 'completado':
        return <Badge className="bg-green-500/10 text-green-500 border-green-500/20">Completado</Badge>
      case 'en-progreso':
        return <Badge className="bg-yellow-500/10 text-yellow-500 border-yellow-500/20">En Progreso</Badge>
      case 'error':
        return <Badge className="bg-red-500/10 text-red-500 border-red-500/20">Error</Badge>
    }
  }

  const getTypeBadge = (type: Project['type']) => {
    switch (type) {
      case 'servicio-rapido':
        return <Badge variant="outline" className="bg-blue-500/10 text-blue-500">Servicio Rápido</Badge>
      case 'solucion-integral':
        return <Badge variant="outline" className="bg-purple-500/10 text-purple-500">Solución Integral</Badge>
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const downloadFile = async (projectId: string, fileType: string) => {
    try {
      setDownloadingFiles(prev => new Set(prev).add(`${projectId}-${fileType}`))

      const response = await fetch(`${API_BASE_URL}/projects/${projectId}/files`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      
      if (data.error) {
        throw new Error(data.error)
      }

      const fileInfo = data.files[fileType]
      if (!fileInfo) {
        throw new Error(`Archivo ${fileType} no encontrado`)
      }

      // Descargar archivo usando la URL firmada
      const downloadResponse = await fetch(fileInfo.url)
      if (!downloadResponse.ok) {
        throw new Error('Error al descargar el archivo')
      }

      const blob = await downloadResponse.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = fileInfo.filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)

    } catch (error: any) {
      console.error('Error downloading file:', error)
      alert(`Error al descargar archivo: ${error.message}`)
    } finally {
      setDownloadingFiles(prev => {
        const newSet = new Set(prev)
        newSet.delete(`${projectId}-${fileType}`)
        return newSet
      })
    }
  }

  const downloadAllFiles = async (projectId: string) => {
    try {
      setDownloadingFiles(prev => new Set(prev).add(`${projectId}-all`))

      const response = await fetch(`${API_BASE_URL}/projects/${projectId}/files`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      
      if (data.error) {
        throw new Error(data.error)
      }

      // Descargar todos los archivos disponibles
      const files = data.files
      for (const [fileType, fileInfo] of Object.entries(files)) {
        try {
          const downloadResponse = await fetch((fileInfo as any).url)
          if (downloadResponse.ok) {
            const blob = await downloadResponse.blob()
            const url = window.URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = (fileInfo as any).filename
            document.body.appendChild(a)
            a.click()
            document.body.removeChild(a)
            window.URL.revokeObjectURL(url)
          }
        } catch (fileError) {
          console.error(`Error downloading ${fileType}:`, fileError)
        }
      }

    } catch (error: any) {
      console.error('Error downloading files:', error)
      alert(`Error al descargar archivos: ${error.message}`)
    } finally {
      setDownloadingFiles(prev => {
        const newSet = new Set(prev)
        newSet.delete(`${projectId}-all`)
        return newSet
      })
    }
  }

  const deleteProject = async (projectId: string) => {
    if (!confirm('¿Estás seguro de que quieres eliminar este proyecto? Esta acción no se puede deshacer.')) {
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      
      if (data.error) {
        throw new Error(data.error)
      }

      // Recargar proyectos
      await loadProjects()
      alert('Proyecto eliminado exitosamente')

    } catch (error: any) {
      console.error('Error deleting project:', error)
      alert(`Error al eliminar proyecto: ${error.message}`)
    }
  }

  const viewProject = (projectId: string) => {
    // En el futuro, esto podría abrir un modal con detalles del proyecto
    const project = projects.find(p => p.id === projectId)
    if (project) {
      alert(`Proyecto: ${project.name}\nTipo: ${project.type}\nEstado: ${project.status}\nDescripción: ${project.description}`)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Cargando proyectos...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="w-full max-w-md">
          <CardContent className="p-6 text-center">
            <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Error al cargar proyectos</h3>
            <p className="text-muted-foreground mb-4">{error}</p>
            <Button onClick={loadProjects} className="w-full">
              <RefreshCw className="w-4 h-4 mr-2" />
              Reintentar
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-foreground">Proyectos</h1>
          <p className="text-lg text-muted-foreground">
            Gestiona y descarga todos tus proyectos generados
          </p>
        </div>
        <Button onClick={loadProjects} variant="outline">
          <RefreshCw className="w-4 h-4 mr-2" />
          Actualizar
        </Button>
      </div>

      {/* Stats Cards */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-blue-500/10 rounded-lg">
                  <FolderOpen className="w-5 h-5 text-blue-500" />
                </div>
                <div>
                  <div className="text-2xl font-bold">{statistics.total_projects}</div>
                  <div className="text-sm text-muted-foreground">Total Proyectos</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-green-500/10 rounded-lg">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                </div>
                <div>
                  <div className="text-2xl font-bold">{statistics.completed_projects}</div>
                  <div className="text-sm text-muted-foreground">Completados</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-yellow-500/10 rounded-lg">
                  <Clock className="w-5 h-5 text-yellow-500" />
                </div>
                <div>
                  <div className="text-2xl font-bold">{statistics.in_progress_projects}</div>
                  <div className="text-sm text-muted-foreground">En Progreso</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-purple-500/10 rounded-lg">
                  <FileText className="w-5 h-5 text-purple-500" />
                </div>
                <div>
                  <div className="text-2xl font-bold">{statistics.total_files}</div>
                  <div className="text-sm text-muted-foreground">Archivos Generados</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Filter className="w-5 h-5" />
            <span>Filtros y Búsqueda</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar proyectos..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div className="flex gap-2">
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value as any)}
                className="px-3 py-2 border border-border rounded-md bg-background text-foreground"
              >
                <option value="all">Todos los tipos</option>
                <option value="servicio-rapido">Servicio Rápido</option>
                <option value="solucion-integral">Solución Integral</option>
              </select>
              
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value as any)}
                className="px-3 py-2 border border-border rounded-md bg-background text-foreground"
              >
                <option value="all">Todos los estados</option>
                <option value="completado">Completado</option>
                <option value="en-progreso">En Progreso</option>
                <option value="error">Error</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Projects Table */}
      <Card>
        <CardHeader>
          <CardTitle>Lista de Proyectos</CardTitle>
          <CardDescription>
            {filteredProjects.length} de {projects.length} proyectos
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Proyecto</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Archivos</TableHead>
                  <TableHead>Fecha</TableHead>
                  <TableHead>Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredProjects.map((project) => (
                  <TableRow key={project.id}>
                    <TableCell>
                      <div>
                        <div className="font-medium text-foreground">{project.name}</div>
                        <div className="text-sm text-muted-foreground line-clamp-1">
                          {project.description}
                        </div>
                      </div>
                    </TableCell>
                    
                    <TableCell>
                      {getTypeBadge(project.type)}
                    </TableCell>
                    
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(project.status)}
                        {getStatusBadge(project.status)}
                      </div>
                    </TableCell>
                    
                    <TableCell>
                      <div className="flex space-x-1">
                        {project.files.word && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => downloadFile(project.id, 'word')}
                            className="p-1 h-8 w-8"
                            disabled={downloadingFiles.has(`${project.id}-word`)}
                          >
                            {downloadingFiles.has(`${project.id}-word`) ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <FileText className="w-4 h-4 text-blue-600" />
                            )}
                          </Button>
                        )}
                        {project.files.csv && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => downloadFile(project.id, 'csv')}
                            className="p-1 h-8 w-8"
                            disabled={downloadingFiles.has(`${project.id}-csv`)}
                          >
                            {downloadingFiles.has(`${project.id}-csv`) ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <FileSpreadsheet className="w-4 h-4 text-green-600" />
                            )}
                          </Button>
                        )}
                        {project.files.yaml && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => downloadFile(project.id, 'yaml')}
                            className="p-1 h-8 w-8"
                            disabled={downloadingFiles.has(`${project.id}-yaml`)}
                          >
                            {downloadingFiles.has(`${project.id}-yaml`) ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <Code className="w-4 h-4 text-purple-600" />
                            )}
                          </Button>
                        )}
                        {project.files.png && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => downloadFile(project.id, 'png')}
                            className="p-1 h-8 w-8"
                            disabled={downloadingFiles.has(`${project.id}-png`)}
                          >
                            {downloadingFiles.has(`${project.id}-png`) ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <Image className="w-4 h-4 text-orange-600" />
                            )}
                          </Button>
                        )}
                      </div>
                    </TableCell>
                    
                    <TableCell>
                      <div className="text-sm">
                        <div className="text-foreground">{formatDate(project.createdAt)}</div>
                        {project.updatedAt !== project.createdAt && (
                          <div className="text-muted-foreground">
                            Actualizado: {formatDate(project.updatedAt)}
                          </div>
                        )}
                      </div>
                    </TableCell>
                    
                    <TableCell>
                      <div className="flex space-x-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => viewProject(project.id)}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => downloadAllFiles(project.id)}
                          disabled={downloadingFiles.has(`${project.id}-all`)}
                        >
                          {downloadingFiles.has(`${project.id}-all`) ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <Download className="w-4 h-4" />
                          )}
                        </Button>
                        {project.s3Folder && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => window.open(`https://s3.console.aws.amazon.com/s3/buckets/${project.s3Bucket || 'aws-propuestas-v3-documents-prod-035385358261'}/${project.s3Folder}/`, '_blank')}
                          >
                            <ExternalLink className="w-4 h-4" />
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => deleteProject(project.id)}
                          className="text-red-500 hover:text-red-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          
          {filteredProjects.length === 0 && (
            <div className="text-center py-8">
              <FolderOpen className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium text-foreground mb-2">No se encontraron proyectos</h3>
              <p className="text-muted-foreground">
                {searchTerm || filterType !== 'all' || filterStatus !== 'all'
                  ? 'Intenta ajustar los filtros de búsqueda'
                  : 'Aún no has creado ningún proyecto. ¡Comienza creando uno nuevo en la sección Arquitecto!'}
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
