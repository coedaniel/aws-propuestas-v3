'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { FileText, Download, FolderOpen, FileCode, FileSpreadsheet, FileImage, AlertCircle, Loader2 } from 'lucide-react'

interface Document {
  name: string
  path: string
  type: 'text' | 'code' | 'spreadsheet' | 'image' | 'other'
  size: number
  lastModified: string
}

interface DocumentViewerProps {
  projectName: string
  s3Folder: string
}

export function DocumentViewer({ projectName, s3Folder }: DocumentViewerProps) {
  const [documents, setDocuments] = useState<Document[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState('all')

  useEffect(() => {
    // Simular carga de documentos desde S3
    // En una implementación real, esto haría una llamada a la API para obtener los documentos
    const fetchDocuments = async () => {
      setIsLoading(true)
      setError(null)
      
      try {
        // Simulación de documentos - en producción, esto vendría de una API
        const mockDocuments: Document[] = [
          {
            name: `${projectName}-arquitectura.docx`,
            path: `${s3Folder}/${projectName}-arquitectura.docx`,
            type: 'text',
            size: 245000,
            lastModified: new Date().toISOString()
          },
          {
            name: `${projectName}-costos.xlsx`,
            path: `${s3Folder}/${projectName}-costos.xlsx`,
            type: 'spreadsheet',
            size: 125000,
            lastModified: new Date().toISOString()
          },
          {
            name: `${projectName}-cloudformation.yaml`,
            path: `${s3Folder}/${projectName}-cloudformation.yaml`,
            type: 'code',
            size: 35000,
            lastModified: new Date().toISOString()
          },
          {
            name: `${projectName}-diagrama.svg`,
            path: `${s3Folder}/${projectName}-diagrama.svg`,
            type: 'image',
            size: 85000,
            lastModified: new Date().toISOString()
          },
          {
            name: `${projectName}-diagrama.xml`,
            path: `${s3Folder}/${projectName}-diagrama.xml`,
            type: 'code',
            size: 92000,
            lastModified: new Date().toISOString()
          }
        ]
        
        // Simular retraso de red
        setTimeout(() => {
          setDocuments(mockDocuments)
          setIsLoading(false)
        }, 1000)
        
      } catch (err) {
        console.error('Error fetching documents:', err)
        setError('Error al cargar los documentos. Por favor, inténtalo de nuevo.')
        setIsLoading(false)
      }
    }
    
    if (projectName) {
      fetchDocuments()
    }
  }, [projectName, s3Folder])

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'text': return <FileText className="h-4 w-4 text-blue-600" />
      case 'code': return <FileCode className="h-4 w-4 text-purple-600" />
      case 'spreadsheet': return <FileSpreadsheet className="h-4 w-4 text-green-600" />
      case 'image': return <FileImage className="h-4 w-4 text-orange-600" />
      default: return <FileText className="h-4 w-4 text-gray-600" />
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const filteredDocuments = activeTab === 'all' 
    ? documents 
    : documents.filter(doc => doc.type === activeTab)

  const handleDownload = (document: Document) => {
    // En una implementación real, esto descargaría el archivo desde S3
    alert(`Descargando ${document.name} desde ${document.path}`)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FolderOpen className="h-5 w-5 text-blue-600" />
          Documentos del Proyecto
        </CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
              <p className="text-gray-600">Cargando documentos...</p>
            </div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <AlertCircle className="h-8 w-8 mx-auto mb-4 text-red-600" />
              <p className="text-red-600">{error}</p>
              <Button 
                variant="outline" 
                size="sm" 
                className="mt-4"
                onClick={() => window.location.reload()}
              >
                Reintentar
              </Button>
            </div>
          </div>
        ) : documents.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <FolderOpen className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p>No hay documentos disponibles todavía.</p>
            <p className="text-sm mt-2">Los documentos aparecerán aquí cuando se generen.</p>
          </div>
        ) : (
          <>
            <Tabs defaultValue="all" value={activeTab} onValueChange={setActiveTab} className="mb-4">
              <TabsList className="grid grid-cols-5 mb-4">
                <TabsTrigger value="all">Todos</TabsTrigger>
                <TabsTrigger value="text">Documentos</TabsTrigger>
                <TabsTrigger value="spreadsheet">Hojas</TabsTrigger>
                <TabsTrigger value="code">Código</TabsTrigger>
                <TabsTrigger value="image">Imágenes</TabsTrigger>
              </TabsList>
              
              <TabsContent value={activeTab} className="mt-0">
                <div className="border rounded-lg overflow-hidden">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nombre</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tamaño</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Modificado</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acción</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {filteredDocuments.map((doc, index) => (
                        <tr key={index} className="hover:bg-gray-50">
                          <td className="px-4 py-3">
                            <div className="flex items-center">
                              {getFileIcon(doc.type)}
                              <span className="ml-2 truncate max-w-[200px]">{doc.name}</span>
                            </div>
                          </td>
                          <td className="px-4 py-3 text-gray-600">{formatFileSize(doc.size)}</td>
                          <td className="px-4 py-3 text-gray-600">{formatDate(doc.lastModified)}</td>
                          <td className="px-4 py-3 text-right">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDownload(doc)}
                              className="text-blue-600 hover:text-blue-800"
                            >
                              <Download className="h-4 w-4" />
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </TabsContent>
            </Tabs>
            
            <div className="text-xs text-gray-500 mt-2">
              <p>Ruta de almacenamiento: {s3Folder}</p>
              <p>Total: {documents.length} documento(s)</p>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
}
