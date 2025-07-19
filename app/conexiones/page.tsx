'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Network, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  RefreshCw,
  Zap,
  Database,
  Cloud,
  Server,
  Globe,
  Activity,
  Clock,
  Wifi,
  WifiOff,
  Settings,
  ExternalLink,
  Info
} from 'lucide-react'

interface ServiceStatus {
  id: string
  name: string
  type: 'bedrock' | 'mcp' | 'api' | 'storage' | 'network'
  status: 'online' | 'offline' | 'warning' | 'checking'
  url?: string
  port?: number
  responseTime?: number
  lastCheck: string
  description: string
  version?: string
  region?: string
}

// Mock data - En producción esto vendría de health checks reales
const mockServices: ServiceStatus[] = [
  {
    id: 'bedrock-runtime',
    name: 'Bedrock Runtime',
    type: 'bedrock',
    status: 'online',
    responseTime: 245,
    lastCheck: new Date().toISOString(),
    description: 'Servicio principal de Amazon Bedrock para modelos de IA',
    region: 'us-east-1'
  },
  {
    id: 'core-mcp',
    name: 'Core MCP',
    type: 'mcp',
    status: 'online',
    url: 'https://mcp.danielingram.shop/core',
    port: 8000,
    responseTime: 156,
    lastCheck: new Date().toISOString(),
    description: 'Servicio MCP principal para coordinación',
    version: 'v1.2.0'
  },
  {
    id: 'pricing-mcp',
    name: 'Pricing MCP',
    type: 'mcp',
    status: 'online',
    url: 'https://mcp.danielingram.shop/pricing',
    port: 8001,
    responseTime: 189,
    lastCheck: new Date().toISOString(),
    description: 'Cálculos de costos y estimaciones AWS',
    version: 'v1.1.5'
  },
  {
    id: 'awsdocs-mcp',
    name: 'AWS Docs MCP',
    type: 'mcp',
    status: 'online',
    url: 'https://mcp.danielingram.shop/awsdocs',
    port: 8002,
    responseTime: 203,
    lastCheck: new Date().toISOString(),
    description: 'Acceso a documentación oficial de AWS',
    version: 'v1.0.8'
  },
  {
    id: 'cfn-mcp',
    name: 'CloudFormation MCP',
    type: 'mcp',
    status: 'warning',
    url: 'https://mcp.danielingram.shop/cfn',
    port: 8003,
    responseTime: 1250,
    lastCheck: new Date().toISOString(),
    description: 'Generación de templates CloudFormation',
    version: 'v1.0.3'
  },
  {
    id: 'diagram-mcp',
    name: 'Diagram MCP',
    type: 'mcp',
    status: 'online',
    url: 'https://mcp.danielingram.shop/diagram',
    port: 8004,
    responseTime: 312,
    lastCheck: new Date().toISOString(),
    description: 'Generación de diagramas de arquitectura',
    version: 'v2.1.0'
  },
  {
    id: 'customdoc-mcp',
    name: 'Custom Doc MCP',
    type: 'mcp',
    status: 'online',
    url: 'https://mcp.danielingram.shop/docgen',
    port: 8005,
    responseTime: 278,
    lastCheck: new Date().toISOString(),
    description: 'Generación de documentos personalizados',
    version: 'v1.3.2'
  },
  {
    id: 'api-gateway',
    name: 'API Gateway',
    type: 'api',
    status: 'online',
    url: 'https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod',
    responseTime: 89,
    lastCheck: new Date().toISOString(),
    description: 'Gateway principal para APIs REST',
    region: 'us-east-1'
  },
  {
    id: 's3-storage',
    name: 'S3 Storage',
    type: 'storage',
    status: 'online',
    responseTime: 67,
    lastCheck: new Date().toISOString(),
    description: 'Almacenamiento de archivos generados',
    region: 'us-east-1'
  },
  {
    id: 'dynamodb',
    name: 'DynamoDB',
    type: 'storage',
    status: 'online',
    responseTime: 45,
    lastCheck: new Date().toISOString(),
    description: 'Base de datos para proyectos y metadatos',
    region: 'us-east-1'
  },
  {
    id: 'amplify',
    name: 'Amplify Hosting',
    type: 'network',
    status: 'online',
    url: 'https://main.d2xsphsjdxlk24.amplifyapp.com',
    responseTime: 123,
    lastCheck: new Date().toISOString(),
    description: 'Hosting del frontend Next.js',
    region: 'us-east-1'
  }
]

export default function ConexionesPage() {
  const [services, setServices] = useState<ServiceStatus[]>(mockServices)
  const [isChecking, setIsChecking] = useState(false)
  const [lastGlobalCheck, setLastGlobalCheck] = useState(new Date())

  const checkAllServices = async () => {
    setIsChecking(true)
    
    // Simular verificación de servicios
    const updatedServices = services.map(service => ({
      ...service,
      status: 'checking' as const,
      lastCheck: new Date().toISOString()
    }))
    setServices(updatedServices)
    
    // Simular delay de verificación
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Restaurar estados (en producción aquí harías health checks reales)
    const finalServices = updatedServices.map(service => ({
      ...service,
      status: Math.random() > 0.1 ? 'online' as const : 'warning' as const,
      responseTime: Math.floor(Math.random() * 500) + 50,
      lastCheck: new Date().toISOString()
    }))
    
    setServices(finalServices)
    setLastGlobalCheck(new Date())
    setIsChecking(false)
  }

  const checkSingleService = async (serviceId: string) => {
    setServices(prev => prev.map(service => 
      service.id === serviceId 
        ? { ...service, status: 'checking', lastCheck: new Date().toISOString() }
        : service
    ))
    
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    setServices(prev => prev.map(service => 
      service.id === serviceId 
        ? { 
            ...service, 
            status: Math.random() > 0.1 ? 'online' : 'warning',
            responseTime: Math.floor(Math.random() * 500) + 50,
            lastCheck: new Date().toISOString()
          }
        : service
    ))
  }

  const getStatusIcon = (status: ServiceStatus['status']) => {
    switch (status) {
      case 'online':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'offline':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />
      case 'checking':
        return <RefreshCw className="w-5 h-5 text-blue-500 animate-spin" />
    }
  }

  const getStatusBadge = (status: ServiceStatus['status']) => {
    switch (status) {
      case 'online':
        return <Badge className="bg-green-500/10 text-green-500 border-green-500/20">Online</Badge>
      case 'offline':
        return <Badge className="bg-red-500/10 text-red-500 border-red-500/20">Offline</Badge>
      case 'warning':
        return <Badge className="bg-yellow-500/10 text-yellow-500 border-yellow-500/20">Advertencia</Badge>
      case 'checking':
        return <Badge className="bg-blue-500/10 text-blue-500 border-blue-500/20">Verificando</Badge>
    }
  }

  const getTypeIcon = (type: ServiceStatus['type']) => {
    switch (type) {
      case 'bedrock':
        return <Zap className="w-5 h-5 text-purple-500" />
      case 'mcp':
        return <Server className="w-5 h-5 text-blue-500" />
      case 'api':
        return <Globe className="w-5 h-5 text-green-500" />
      case 'storage':
        return <Database className="w-5 h-5 text-orange-500" />
      case 'network':
        return <Network className="w-5 h-5 text-cyan-500" />
    }
  }

  const formatResponseTime = (time?: number) => {
    if (!time) return 'N/A'
    if (time < 100) return `${time}ms`
    if (time < 1000) return `${time}ms`
    return `${(time / 1000).toFixed(1)}s`
  }

  const formatLastCheck = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    
    if (diff < 60000) return 'Hace menos de 1 min'
    if (diff < 3600000) return `Hace ${Math.floor(diff / 60000)} min`
    return date.toLocaleTimeString()
  }

  const onlineServices = services.filter(s => s.status === 'online').length
  const warningServices = services.filter(s => s.status === 'warning').length
  const offlineServices = services.filter(s => s.status === 'offline').length

  const ServiceCard = ({ service, onCheck }: { service: ServiceStatus, onCheck: (serviceId: string) => void }) => (
    <div className="p-4 border border-border rounded-lg bg-card hover:bg-muted/30 transition-colors">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-3">
          {getTypeIcon(service.type)}
          <div>
            <h4 className="font-medium text-foreground">{service.name}</h4>
            <p className="text-sm text-muted-foreground">{service.description}</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {getStatusBadge(service.status)}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onCheck(service.id)}
            disabled={service.status === 'checking'}
          >
            <RefreshCw className={`w-4 h-4 ${service.status === 'checking' ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <span className="text-muted-foreground">Respuesta:</span>
          <span className="ml-2 font-medium">{formatResponseTime(service.responseTime)}</span>
        </div>
        <div>
          <span className="text-muted-foreground">Verificado:</span>
          <span className="ml-2 font-medium">{formatLastCheck(service.lastCheck)}</span>
        </div>
        {service.version && (
          <div>
            <span className="text-muted-foreground">Versión:</span>
            <span className="ml-2 font-medium">{service.version}</span>
          </div>
        )}
        {service.region && (
          <div>
            <span className="text-muted-foreground">Región:</span>
            <span className="ml-2 font-medium">{service.region}</span>
          </div>
        )}
      </div>
      
      {service.url && (
        <div className="mt-3 pt-3 border-t border-border">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground font-mono">{service.url}</span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => window.open(service.url, '_blank')}
            >
              <ExternalLink className="w-3 h-3" />
            </Button>
          </div>
        </div>
      )}
    </div>
  )

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-foreground">Estado de Conexiones</h1>
          <p className="text-lg text-muted-foreground">
            Monitoreo en tiempo real de todos los servicios
          </p>
        </div>
        
        <Button onClick={checkAllServices} disabled={isChecking}>
          <RefreshCw className={`w-4 h-4 mr-2 ${isChecking ? 'animate-spin' : ''}`} />
          {isChecking ? 'Verificando...' : 'Verificar Todo'}
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-green-500/10 rounded-lg">
                <CheckCircle className="w-5 h-5 text-green-500" />
              </div>
              <div>
                <div className="text-2xl font-bold text-green-500">{onlineServices}</div>
                <div className="text-sm text-muted-foreground">Servicios Online</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-yellow-500/10 rounded-lg">
                <AlertTriangle className="w-5 h-5 text-yellow-500" />
              </div>
              <div>
                <div className="text-2xl font-bold text-yellow-500">{warningServices}</div>
                <div className="text-sm text-muted-foreground">Con Advertencias</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-red-500/10 rounded-lg">
                <XCircle className="w-5 h-5 text-red-500" />
              </div>
              <div>
                <div className="text-2xl font-bold text-red-500">{offlineServices}</div>
                <div className="text-sm text-muted-foreground">Servicios Offline</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-500/10 rounded-lg">
                <Activity className="w-5 h-5 text-blue-500" />
              </div>
              <div>
                <div className="text-2xl font-bold text-blue-500">
                  {Math.round(services.reduce((acc, s) => acc + (s.responseTime || 0), 0) / services.length)}ms
                </div>
                <div className="text-sm text-muted-foreground">Latencia Promedio</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Services by Category */}
      <div className="space-y-6">
        {/* Bedrock Services */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Zap className="w-5 h-5 text-purple-500" />
              <span>Servicios Bedrock</span>
            </CardTitle>
            <CardDescription>
              Modelos de IA y servicios de Amazon Bedrock
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 gap-4">
              {services.filter(s => s.type === 'bedrock').map((service) => (
                <ServiceCard key={service.id} service={service} onCheck={checkSingleService} />
              ))}
            </div>
          </CardContent>
        </Card>

        {/* MCP Services */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Server className="w-5 h-5 text-blue-500" />
              <span>Servicios MCP</span>
            </CardTitle>
            <CardDescription>
              Model Context Protocol servers desplegados en ECS
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {services.filter(s => s.type === 'mcp').map((service) => (
                <ServiceCard key={service.id} service={service} onCheck={checkSingleService} />
              ))}
            </div>
          </CardContent>
        </Card>

        {/* API & Network Services */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Globe className="w-5 h-5 text-green-500" />
              <span>APIs y Red</span>
            </CardTitle>
            <CardDescription>
              Servicios de API Gateway, hosting y conectividad
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {services.filter(s => s.type === 'api' || s.type === 'network').map((service) => (
                <ServiceCard key={service.id} service={service} onCheck={checkSingleService} />
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Storage Services */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Database className="w-5 h-5 text-orange-500" />
              <span>Almacenamiento</span>
            </CardTitle>
            <CardDescription>
              Servicios de base de datos y almacenamiento
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {services.filter(s => s.type === 'storage').map((service) => (
                <ServiceCard key={service.id} service={service} onCheck={checkSingleService} />
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Last Check Info */}
      <Card className="bg-muted/30">
        <CardContent className="p-4">
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <div className="flex items-center space-x-2">
              <Clock className="w-4 h-4" />
              <span>Última verificación global: {lastGlobalCheck.toLocaleTimeString()}</span>
            </div>
            <div className="flex items-center space-x-2">
              <Info className="w-4 h-4" />
              <span>Verificación automática cada 5 minutos</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
