'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Loader2, CheckCircle, XCircle, Activity } from 'lucide-react'

interface MCPService {
  name: string
  url: string
  status: 'healthy' | 'unhealthy' | 'checking'
  description: string
  capabilities: string[]
}

const MCP_SERVICES: MCPService[] = [
  {
    name: 'Core MCP',
    url: '/api/mcp-proxy/core',
    status: 'checking',
    description: 'Servicios principales de análisis y procesamiento',
    capabilities: ['Análisis de texto', 'Extracción de entidades', 'Clasificación']
  },
  {
    name: 'Diagram MCP',
    url: '/api/mcp-proxy/diagram',
    status: 'checking',
    description: 'Generación de diagramas de arquitectura',
    capabilities: ['Diagramas AWS', 'Visualización', 'Exportación SVG']
  },
  {
    name: 'AWS Docs MCP',
    url: '/api/mcp-proxy/awsdocs',
    status: 'checking',
    description: 'Búsqueda y análisis de documentación AWS',
    capabilities: ['Búsqueda docs', 'Recomendaciones', 'Análisis técnico']
  },
  {
    name: 'CloudFormation MCP',
    url: '/api/mcp-proxy/cfn',
    status: 'checking',
    description: 'Generación de templates CloudFormation',
    capabilities: ['Templates IaC', 'Validación', 'Optimización']
  },
  {
    name: 'Pricing MCP',
    url: '/api/mcp-proxy/pricing',
    status: 'checking',
    description: 'Análisis de costos y pricing AWS',
    capabilities: ['Estimación costos', 'Comparación precios', 'Optimización']
  },
  {
    name: 'Custom Doc MCP',
    url: '/api/mcp-proxy/customdoc',
    status: 'checking',
    description: 'Generación de documentación personalizada',
    capabilities: ['Docs técnicos', 'Propuestas', 'Reportes']
  }
]

export function MCPIntegration() {
  const [services, setServices] = useState<MCPService[]>(MCP_SERVICES)
  const [isChecking, setIsChecking] = useState(false)

  const checkServiceHealth = async (service: MCPService): Promise<'healthy' | 'unhealthy'> => {
    try {
      const response = await fetch(`${service.url}/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(5000) // 5 second timeout
      })
      
      return response.ok ? 'healthy' : 'unhealthy'
    } catch (error) {
      console.error(`Health check failed for ${service.name}:`, error)
      return 'unhealthy'
    }
  }

  const checkAllServices = async () => {
    setIsChecking(true)
    
    const updatedServices = await Promise.all(
      services.map(async (service) => {
        const status = await checkServiceHealth(service)
        return { ...service, status }
      })
    )
    
    setServices(updatedServices)
    setIsChecking(false)
  }

  useEffect(() => {
    checkAllServices()
    
    // Check services every 30 seconds
    const interval = setInterval(checkAllServices, 30000)
    return () => clearInterval(interval)
  }, [])

  const getStatusIcon = (status: MCPService['status']) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'unhealthy':
        return <XCircle className="h-4 w-4 text-red-500" />
      case 'checking':
        return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />
    }
  }

  const getStatusColor = (status: MCPService['status']) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-100 text-green-800'
      case 'unhealthy':
        return 'bg-red-100 text-red-800'
      case 'checking':
        return 'bg-blue-100 text-blue-800'
    }
  }

  const healthyCount = services.filter(s => s.status === 'healthy').length
  const totalCount = services.length

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">MCP Services Status</h2>
          <p className="text-gray-600">
            Estado de los servicios MCP ({healthyCount}/{totalCount} activos)
          </p>
        </div>
        <Button 
          onClick={checkAllServices} 
          disabled={isChecking}
          variant="outline"
        >
          {isChecking ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Verificando...
            </>
          ) : (
            <>
              <Activity className="mr-2 h-4 w-4" />
              Verificar Estado
            </>
          )}
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {services.map((service) => (
          <Card key={service.name} className="relative">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{service.name}</CardTitle>
                <div className="flex items-center space-x-2">
                  {getStatusIcon(service.status)}
                  <Badge className={getStatusColor(service.status)}>
                    {service.status === 'healthy' ? 'Activo' : 
                     service.status === 'unhealthy' ? 'Inactivo' : 'Verificando'}
                  </Badge>
                </div>
              </div>
              <CardDescription>{service.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-gray-900">Capacidades:</h4>
                <div className="flex flex-wrap gap-1">
                  {service.capabilities.map((capability) => (
                    <Badge key={capability} variant="secondary" className="text-xs">
                      {capability}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Overall Health Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Activity className="h-5 w-5" />
            <span>Resumen del Sistema</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{healthyCount}</div>
              <div className="text-sm text-gray-600">Servicios Activos</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {services.filter(s => s.status === 'unhealthy').length}
              </div>
              <div className="text-sm text-gray-600">Servicios Inactivos</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {Math.round((healthyCount / totalCount) * 100)}%
              </div>
              <div className="text-sm text-gray-600">Disponibilidad</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
