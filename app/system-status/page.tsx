'use client'

import React from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { MCPStatusDetailed } from '@/components/mcp-status'
import { ArrowLeft, RefreshCw } from 'lucide-react'

export default function SystemStatusPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <Link href="/">
              <Button variant="outline" size="sm">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Volver
              </Button>
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Estado del Sistema</h1>
              <p className="text-gray-600">Monitoreo en tiempo real de los servicios</p>
            </div>
          </div>
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => window.location.reload()}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Actualizar
          </Button>
        </div>

        {/* System Status */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <MCPStatusDetailed />
        </div>

        {/* Additional Information */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-semibold mb-4">Servidores MCP</h3>
            <div className="space-y-3 text-sm">
              <div>
                <strong>Core MCP:</strong> Funcionalidad principal de chat y conversación
              </div>
              <div>
                <strong>Pricing MCP:</strong> Cálculos de precios y costos de AWS
              </div>
              <div>
                <strong>AWS Docs MCP:</strong> Búsqueda en documentación oficial de AWS
              </div>
              <div>
                <strong>CloudFormation MCP:</strong> Generación de plantillas de infraestructura
              </div>
              <div>
                <strong>Diagram MCP:</strong> Creación de diagramas de arquitectura
              </div>
              <div>
                <strong>Document Generator MCP:</strong> Generación de documentos personalizados
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-semibold mb-4">Información Técnica</h3>
            <div className="space-y-3 text-sm">
              <div>
                <strong>Infraestructura:</strong> Amazon ECS con Fargate
              </div>
              <div>
                <strong>Load Balancer:</strong> Application Load Balancer
              </div>
              <div>
                <strong>Región:</strong> us-east-1 (N. Virginia)
              </div>
              <div>
                <strong>Protocolo:</strong> HTTP/HTTPS
              </div>
              <div>
                <strong>Monitoreo:</strong> Automático cada 30 segundos
              </div>
            </div>
          </div>
        </div>

        {/* Troubleshooting */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-4">Solución de Problemas</h3>
          <div className="space-y-2 text-sm text-blue-800">
            <p>• Si algunos servicios aparecen como no disponibles, espera unos minutos y actualiza la página</p>
            <p>• Los servicios MCP pueden tardar hasta 2 minutos en iniciarse después de un despliegue</p>
            <p>• Si persisten los problemas, verifica la configuración de red y security groups</p>
            <p>• El sistema tiene fallback automático entre API legacy y servidores MCP</p>
          </div>
        </div>
      </div>
    </div>
  )
}
