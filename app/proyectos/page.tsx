'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Download, FileText, Image, Code } from 'lucide-react'
import { useToast } from '@/components/ui/use-toast'

interface Document {
  filename: string
  title: string
  type: string
  url: string
}

interface Project {
  projectId: string
  projectName: string
  projectType: string
  status: string
  createdAt: number
  description: string
  s3Folder: string
  s3Bucket: string
  documentsGenerated: Document[]
  totalDocuments: number
  estimatedCost: number
  services?: string[]
  requirements?: string[]
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const { toast } = useToast()

  useEffect(() => {
    fetchProjects()
  }, [])

  const fetchProjects = async () => {
    try {
      const response = await fetch('https://75bl52azoi.execute-api.us-east-1.amazonaws.com/prod/projects')
      const data = await response.json()
      setProjects(data.projects || [])
      setLoading(false)
    } catch (error) {
      console.error('Error fetching projects:', error)
      toast({
        title: 'Error',
        description: 'No se pudieron cargar los proyectos. Por favor intenta nuevamente.',
        variant: 'destructive'
      })
      setLoading(false)
    }
  }

  const getDocumentIcon = (type: string | undefined) => {
    if (!type) return <FileText className="w-4 h-4" />
    
    switch (type.toLowerCase()) {
      case 'diagram':
        return <Image className="w-4 h-4" />
      case 'cloudformation':
        return <Code className="w-4 h-4" />
      default:
        return <FileText className="w-4 h-4" />
    }
  }

  const downloadDocument = async (project: Project, doc: Document) => {
    try {
      const response = await fetch(`https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod/download?bucket=${project.s3Bucket}&key=${doc.url}`)
      if (!response.ok) throw new Error('Error downloading file')
      
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = doc.filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      toast({
        title: 'Descarga exitosa',
        description: `Se descargó ${doc.filename} correctamente.`
      })
    } catch (error) {
      console.error('Error downloading document:', error)
      toast({
        title: 'Error',
        description: 'No se pudo descargar el documento. Por favor intenta nuevamente.',
        variant: 'destructive'
      })
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Proyectos</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="w-full">
              <CardHeader>
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-3 w-1/2" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-20 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Proyectos</h1>
      {projects.length === 0 ? (
        <Card>
          <CardContent className="p-8 text-center">
            <p className="text-muted-foreground">No hay proyectos disponibles.</p>
            <p className="text-sm text-muted-foreground mt-2">
              Los proyectos aparecerán aquí cuando uses el Arquitecto AWS.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((project) => (
            <Card key={project.projectId} className="w-full">
              <CardHeader>
                <CardTitle>{project.projectName || 'Sin nombre'}</CardTitle>
                <CardDescription>
                  <Badge variant={project.status === 'COMPLETED' ? 'default' : 'secondary'}>
                    {project.status}
                  </Badge>
                  {project.projectType && (
                    <Badge variant="outline" className="ml-2">
                      {project.projectType}
                    </Badge>
                  )}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground mb-4">
                  {project.description || 'Sin descripción'}
                </p>
                {project.services && project.services.length > 0 && (
                  <div className="mb-4">
                    <p className="text-sm font-medium mb-2">Servicios AWS:</p>
                    <div className="flex flex-wrap gap-2">
                      {project.services.map((service) => (
                        <Badge key={service} variant="secondary">
                          {service}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
                {project.documentsGenerated && project.documentsGenerated.length > 0 && (
                  <div>
                    <p className="text-sm font-medium mb-2">Documentos:</p>
                    <div className="flex flex-col gap-2">
                      {project.documentsGenerated.map((doc) => (
                        <Button
                          key={doc.url}
                          variant="outline"
                          size="sm"
                          className="w-full justify-start"
                          onClick={() => downloadDocument(project, doc)}
                        >
                          {getDocumentIcon(doc.type)}
                          <span className="ml-2">{doc.title}</span>
                          <Download className="w-4 h-4 ml-auto" />
                        </Button>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
              <CardFooter className="text-sm text-muted-foreground">
                Creado: {new Date(project.createdAt * 1000).toLocaleDateString()}
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
