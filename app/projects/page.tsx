'use client'

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { 
  ArrowLeft, 
  Plus, 
  FolderOpen, 
  Calendar,
  DollarSign,
  FileText,
  Loader2
} from 'lucide-react'
import { getProjects, createProject, generateDocuments } from '@/lib/api'

interface Project {
  projectId: string
  name: string
  description: string
  requirements: string[]
  budget?: number
  createdAt: string
}

export default function ProjectsPage() {
  const router = useRouter()
  const [projects, setProjects] = useState<Project[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  const [generatingDocs, setGeneratingDocs] = useState<string | null>(null)

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
      // Aquí podrías mostrar un mensaje de éxito o descargar los documentos
      alert('Documentos generados exitosamente')
    } catch (error) {
      console.error('Error generating documents:', error)
      alert('Error al generar documentos')
    } finally {
      setGeneratingDocs(null)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
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
            onClick={() => setShowCreateForm(true)}
            className="flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Nuevo Proyecto
          </Button>
        </div>

        {/* Create Project Form */}
        {showCreateForm && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Crear Nuevo Proyecto</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Nombre del Proyecto</label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Ej: Sistema de E-commerce"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Descripción</label>
                <Textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Describe brevemente el proyecto..."
                  className="min-h-[80px]"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Requisitos (uno por línea)</label>
                <Textarea
                  value={formData.requirements}
                  onChange={(e) => setFormData({ ...formData, requirements: e.target.value })}
                  placeholder="Alta disponibilidad&#10;Escalabilidad automática&#10;Seguridad avanzada"
                  className="min-h-[100px]"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Presupuesto (USD) - Opcional</label>
                <Input
                  type="number"
                  value={formData.budget}
                  onChange={(e) => setFormData({ ...formData, budget: e.target.value })}
                  placeholder="10000"
                />
              </div>
              <div className="flex gap-2">
                <Button
                  onClick={handleCreateProject}
                  disabled={isCreating || !formData.name.trim() || !formData.description.trim()}
                  className="flex items-center gap-2"
                >
                  {isCreating ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Plus className="h-4 w-4" />
                  )}
                  {isCreating ? 'Creando...' : 'Crear Proyecto'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setShowCreateForm(false)}
                  disabled={isCreating}
                >
                  Cancelar
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

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
              <Button onClick={() => setShowCreateForm(true)}>
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
                    <span className="line-clamp-2">{project.name}</span>
                    <Badge variant="secondary" className="ml-2">
                      <Calendar className="h-3 w-3 mr-1" />
                      {formatDate(project.createdAt)}
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-gray-600 text-sm line-clamp-3">
                    {project.description}
                  </p>
                  
                  {project.requirements.length > 0 && (
                    <div>
                      <h4 className="font-medium text-sm mb-2">Requisitos:</h4>
                      <div className="flex flex-wrap gap-1">
                        {project.requirements.slice(0, 3).map((req, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {req}
                          </Badge>
                        ))}
                        {project.requirements.length > 3 && (
                          <Badge variant="outline" className="text-xs">
                            +{project.requirements.length - 3} más
                          </Badge>
                        )}
                      </div>
                    </div>
                  )}

                  {project.budget && (
                    <div className="flex items-center gap-2 text-sm">
                      <DollarSign className="h-4 w-4 text-green-600" />
                      <span className="font-medium">
                        ${project.budget.toLocaleString()} USD
                      </span>
                    </div>
                  )}

                  <Button
                    onClick={() => handleGenerateDocuments(project.projectId)}
                    disabled={generatingDocs === project.projectId}
                    className="w-full flex items-center gap-2"
                    size="sm"
                  >
                    {generatingDocs === project.projectId ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <FileText className="h-4 w-4" />
                    )}
                    {generatingDocs === project.projectId ? 'Generando...' : 'Generar Documentos'}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
