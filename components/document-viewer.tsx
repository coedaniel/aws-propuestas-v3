'use client'

import { useState, useEffect } from 'react'

interface DocumentFile {
  name: string
  type: 'word' | 'excel' | 'yaml' | 'svg' | 'xml' | 'pdf' | 'other'
  size: string
  url: string
  lastModified: string
}

interface DocumentViewerProps {
  projectName: string
  s3Folder: string
}

export function DocumentViewer({ projectName, s3Folder }: DocumentViewerProps) {
  const [documents, setDocuments] = useState<DocumentFile[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadDocuments()
  }, [projectName, s3Folder])

  const loadDocuments = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Simular carga de documentos desde S3
      // En producción, esto haría una llamada real a la API
      const mockDocuments: DocumentFile[] = [
        {
          name: 'Arquitectura_AWS.docx',
          type: 'word',
          size: '2.3 MB',
          url: `${s3Folder}/Arquitectura_AWS.docx`,
          lastModified: '2024-12-16 10:30'
        },
        {
          name: 'Estimacion_Costos.xlsx',
          type: 'excel',
          size: '1.8 MB',
          url: `${s3Folder}/Estimacion_Costos.xlsx`,
          lastModified: '2024-12-16 10:25'
        },
        {
          name: 'CloudFormation_Template.yaml',
          type: 'yaml',
          size: '45 KB',
          url: `${s3Folder}/CloudFormation_Template.yaml`,
          lastModified: '2024-12-16 10:20'
        },
        {
          name: 'Diagrama_Arquitectura.svg',
          type: 'svg',
          size: '156 KB',
          url: `${s3Folder}/Diagrama_Arquitectura.svg`,
          lastModified: '2024-12-16 10:15'
        }
      ]
      
      setDocuments(mockDocuments)
    } catch (err) {
      setError('Error al cargar los documentos')
      console.error('Error loading documents:', err)
    } finally {
      setLoading(false)
    }
  }

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'word': return '📄'
      case 'excel': return '📊'
      case 'yaml': return '⚙️'
      case 'svg': return '🎨'
      case 'xml': return '📋'
      case 'pdf': return '📕'
      default: return '📁'
    }
  }

  const getFileTypeColor = (type: string) => {
    switch (type) {
      case 'word': return 'bg-blue-100 text-blue-800'
      case 'excel': return 'bg-green-100 text-green-800'
      case 'yaml': return 'bg-purple-100 text-purple-800'
      case 'svg': return 'bg-pink-100 text-pink-800'
      case 'xml': return 'bg-orange-100 text-orange-800'
      case 'pdf': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const handleDownload = (doc: DocumentFile) => {
    // En producción, esto descargaría desde S3
    console.log(`Descargando: ${doc.name} desde ${doc.url}`)
    
    // Simular descarga
    const link = window.document.createElement('a')
    link.href = doc.url
    link.download = doc.name
    link.click()
  }

  if (loading) {
    return (
      <div className="bg-white border rounded-lg p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gray-200 rounded"></div>
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-1"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white border rounded-lg p-6">
        <div className="text-center text-red-600">
          <span className="text-2xl">❌</span>
          <p className="mt-2">{error}</p>
          <button 
            onClick={loadDocuments}
            className="mt-3 px-4 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200"
          >
            Reintentar
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white border rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-900">📁 Documentos Generados</h3>
        <span className="text-sm text-gray-500">
          Proyecto: {projectName}
        </span>
      </div>

      {documents.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <span className="text-4xl">📄</span>
          <p className="mt-2">No hay documentos generados aún</p>
          <p className="text-sm">Los documentos aparecerán aquí cuando se generen</p>
        </div>
      ) : (
        <div className="space-y-3">
          {documents.map((doc, index) => (
            <div 
              key={index}
              className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
            >
              <div className="flex items-center space-x-3">
                <span className="text-2xl">{getFileIcon(doc.type)}</span>
                <div>
                  <h4 className="font-medium text-gray-900">{doc.name}</h4>
                  <div className="flex items-center space-x-2 text-sm text-gray-500">
                    <span className={`px-2 py-1 rounded-full text-xs ${getFileTypeColor(doc.type)}`}>
                      {doc.type.toUpperCase()}
                    </span>
                    <span>{doc.size}</span>
                    <span>•</span>
                    <span>{doc.lastModified}</span>
                  </div>
                </div>
              </div>
              
              <button
                onClick={() => handleDownload(doc)}
                className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
              >
                📥 Descargar
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="mt-4 pt-4 border-t">
        <p className="text-xs text-gray-500">
          📂 Ubicación: <code>proyectos/{projectName}/</code>
        </p>
      </div>
    </div>
  )
}
