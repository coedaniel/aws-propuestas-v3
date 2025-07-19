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
  Edit
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
}

// Mock data - En producción esto vendría de tu API
const mockProjects: Project[] = [
  {
    id: '1',
    name: 'Migracion Cloud Empresa ABC',
    type: 'solucion-integral',
    status: 'completado',
    createdAt: '2025-01-15T10:30:00Z',
    updatedAt: '2025-01-15T11:45:00Z',
    files: {
      word: true,
      csv: true,
      yaml: true,
      png: true,
      svg: true
    },
    description: 'Migración completa de infraestructura on-premises a AWS con alta disponibilidad',
    s3Folder: 'migracion-cloud-empresa-abc'
  },
  {
    id: '2',
    name: 'Setup RDS MySQL',
    type: 'servicio-rapido',
    status: 'completado',
    createdAt: '2025-01-14T14:20:00Z',
    updatedAt: '2025-01-14T14:35:00Z',
    files: {
      word: true,
      csv: true,
      yaml: true,
      png: true
    },
    description: 'Configuración de base de datos RDS MySQL con Multi-AZ',
    s3Folder: 'setup-rds-mysql'
  },
  {
    id: '3',
    name: 'Arquitectura Serverless E-commerce',
    type: 'solucion-integral',
    status: 'en-progreso',
    createdAt: '2025-01-16T09:15:00Z',
    updatedAt: '2025-01-16T09:15:00Z',
    files: {
      word: true,
      csv: false,
      yaml: false,
      png: false
    },
    description: 'Plataforma de e-commerce completamente serverless con Lambda y DynamoDB',
    s3Folder: 'arquitectura-serverless-ecommerce'
  },
  {
    id: '4',
    name: 'VPN Site-to-Site',
    type: 'servicio-rapido',
    status: 'error',
    createdAt: '2025-01-13T16:45:00Z',
    updatedAt: '2025-01-13T16:50:00Z',
    files: {
      word: false,
      csv: false,
      yaml: false,
      png: false
    },
    description: 'Conexión VPN entre oficina central y VPC de AWS',
    s3Folder: 'vpn-site-to-site'
  }
]

export default function ProyectosPage() {
  const [projects, setProjects] = useState<Project[]>(mockProjects)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState<'all' | 'servicio-rapido' | 'solucion-integral'>('all')
  const [filterStatus, setFilterStatus] = useState<'all' | 'completado' | 'en-progreso' | 'error'>('all')

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

  const downloadFile = (projectId: string, fileType: string) => {
    // En producción, esto haría una llamada a tu API para obtener la URL firmada de S3
    console.log(`Descargando ${fileType} del proyecto ${projectId}`)
  }

  const viewProject = (projectId: string) => {
    // En producción, esto abriría un modal o navegaría a una página de detalles
    console.log(`Viendo detalles del proyecto ${projectId}`)
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-foreground">Proyectos</h1>
        <p className="text-lg text-muted-foreground">
          Gestiona y descarga todos tus proyectos generados
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-500/10 rounded-lg">
                <FolderOpen className="w-5 h-5 text-blue-500" />
              </div>
              <div>
                <div className="text-2xl font-bold">{projects.length}</div>
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
                <div className="text-2xl font-bold">
                  {projects.filter(p => p.status === 'completado').length}
                </div>
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
                <div className="text-2xl font-bold">
                  {projects.filter(p => p.status === 'en-progreso').length}
                </div>
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
                <div className="text-2xl font-bold">
                  {projects.reduce((acc, p) => acc + Object.values(p.files).filter(Boolean).length, 0)}
                </div>
                <div className="text-sm text-muted-foreground">Archivos Generados</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

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
                          >
                            <FileText className="w-4 h-4 text-blue-600" />
                          </Button>
                        )}
                        {project.files.csv && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => downloadFile(project.id, 'csv')}
                            className="p-1 h-8 w-8"
                          >
                            <FileSpreadsheet className="w-4 h-4 text-green-600" />
                          </Button>
                        )}
                        {project.files.yaml && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => downloadFile(project.id, 'yaml')}
                            className="p-1 h-8 w-8"
                          >
                            <Code className="w-4 h-4 text-purple-600" />
                          </Button>
                        )}
                        {project.files.png && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => downloadFile(project.id, 'png')}
                            className="p-1 h-8 w-8"
                          >
                            <Image className="w-4 h-4 text-orange-600" />
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
                          onClick={() => downloadFile(project.id, 'all')}
                        >
                          <Download className="w-4 h-4" />
                        </Button>
                        {project.s3Folder && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => window.open(`https://s3.console.aws.amazon.com/s3/buckets/your-bucket/${project.s3Folder}/`, '_blank')}
                          >
                            <ExternalLink className="w-4 h-4" />
                          </Button>
                        )}
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
                  : 'Aún no has creado ningún proyecto. ¡Comienza creando uno nuevo!'}
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
