'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown,
  Users,
  FileText,
  Zap,
  Clock,
  DollarSign,
  Activity,
  Calendar,
  Download,
  RefreshCw,
  Filter
} from 'lucide-react'

// Mock data para las gráficas
const mockData = {
  projectsOverTime: [
    { month: 'Ene', proyectos: 12, completados: 10 },
    { month: 'Feb', proyectos: 19, completados: 16 },
    { month: 'Mar', proyectos: 15, completados: 14 },
    { month: 'Abr', proyectos: 25, completados: 22 },
    { month: 'May', proyectos: 22, completados: 20 },
    { month: 'Jun', proyectos: 30, completados: 28 },
  ],
  mcpUsage: [
    { name: 'Core MCP', usage: 45, percentage: 25 },
    { name: 'Diagram MCP', usage: 38, percentage: 21 },
    { name: 'Pricing MCP', usage: 32, percentage: 18 },
    { name: 'AWS Docs MCP', usage: 28, percentage: 16 },
    { name: 'CFN MCP', usage: 22, percentage: 12 },
    { name: 'Custom Doc MCP', usage: 15, percentage: 8 },
  ],
  topSolutions: [
    { name: 'Migración a Cloud', count: 24, trend: 'up' },
    { name: 'Arquitectura Serverless', count: 18, trend: 'up' },
    { name: 'Setup RDS/DynamoDB', count: 15, trend: 'stable' },
    { name: 'Configuración VPC', count: 12, trend: 'down' },
    { name: 'Implementación CDN', count: 9, trend: 'up' },
  ],
  modelUsage: [
    { model: 'Nova Pro v1.0', requests: 156, tokens: 2340000, cost: 234.50 },
    { model: 'Claude 3.5 Sonnet v2', requests: 89, tokens: 1890000, cost: 189.30 },
    { model: 'Claude Sonnet 4', requests: 23, tokens: 450000, cost: 67.80 },
  ]
}

export default function AnaliticaPage() {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d' | '1y'>('30d')
  const [isLoading, setIsLoading] = useState(false)

  const refreshData = async () => {
    setIsLoading(true)
    // Simular carga de datos
    await new Promise(resolve => setTimeout(resolve, 1000))
    setIsLoading(false)
  }

  const exportData = () => {
    // En producción, esto exportaría los datos a CSV/Excel
    console.log('Exportando datos analíticos...')
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-foreground">Analítica</h1>
          <p className="text-lg text-muted-foreground">
            Métricas y estadísticas de uso de la plataforma
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value as any)}
            className="px-3 py-2 border border-border rounded-md bg-background text-foreground"
          >
            <option value="7d">Últimos 7 días</option>
            <option value="30d">Últimos 30 días</option>
            <option value="90d">Últimos 90 días</option>
            <option value="1y">Último año</option>
          </select>
          
          <Button variant="outline" onClick={refreshData} disabled={isLoading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Actualizar
          </Button>
          
          <Button variant="outline" onClick={exportData}>
            <Download className="w-4 h-4 mr-2" />
            Exportar
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Proyectos Totales</p>
                <p className="text-3xl font-bold text-foreground">142</p>
                <div className="flex items-center text-sm text-green-600 mt-1">
                  <TrendingUp className="w-4 h-4 mr-1" />
                  +12% vs mes anterior
                </div>
              </div>
              <div className="p-3 bg-blue-500/10 rounded-lg">
                <FileText className="w-6 h-6 text-blue-500" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">MCPs Ejecutados</p>
                <p className="text-3xl font-bold text-foreground">1,247</p>
                <div className="flex items-center text-sm text-green-600 mt-1">
                  <TrendingUp className="w-4 h-4 mr-1" />
                  +8% vs mes anterior
                </div>
              </div>
              <div className="p-3 bg-purple-500/10 rounded-lg">
                <Zap className="w-6 h-6 text-purple-500" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Tiempo Promedio</p>
                <p className="text-3xl font-bold text-foreground">2.3s</p>
                <div className="flex items-center text-sm text-green-600 mt-1">
                  <TrendingDown className="w-4 h-4 mr-1" />
                  -5% vs mes anterior
                </div>
              </div>
              <div className="p-3 bg-green-500/10 rounded-lg">
                <Clock className="w-6 h-6 text-green-500" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Costo Total</p>
                <p className="text-3xl font-bold text-foreground">$491</p>
                <div className="flex items-center text-sm text-red-600 mt-1">
                  <TrendingUp className="w-4 h-4 mr-1" />
                  +15% vs mes anterior
                </div>
              </div>
              <div className="p-3 bg-orange-500/10 rounded-lg">
                <DollarSign className="w-6 h-6 text-orange-500" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Proyectos por Mes */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="w-5 h-5" />
              <span>Proyectos por Mes</span>
            </CardTitle>
            <CardDescription>
              Evolución de proyectos creados y completados
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-end justify-between space-x-2">
              {mockData.projectsOverTime.map((data, index) => (
                <div key={index} className="flex-1 flex flex-col items-center space-y-2">
                  <div className="w-full flex flex-col space-y-1">
                    <div 
                      className="bg-primary rounded-t"
                      style={{ height: `${(data.completados / 30) * 200}px` }}
                    />
                    <div 
                      className="bg-primary/30 rounded-b"
                      style={{ height: `${((data.proyectos - data.completados) / 30) * 200}px` }}
                    />
                  </div>
                  <span className="text-xs text-muted-foreground">{data.month}</span>
                </div>
              ))}
            </div>
            <div className="flex items-center justify-center space-x-4 mt-4 text-sm">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-primary rounded"></div>
                <span>Completados</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-primary/30 rounded"></div>
                <span>En progreso</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Uso de MCPs */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Zap className="w-5 h-5" />
              <span>Uso de MCPs</span>
            </CardTitle>
            <CardDescription>
              Distribución de uso por servicio MCP
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {mockData.mcpUsage.map((mcp, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium">{mcp.name}</span>
                    <span className="text-muted-foreground">{mcp.usage} usos</span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div 
                      className="bg-primary h-2 rounded-full transition-all duration-300"
                      style={{ width: `${mcp.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top 5 Soluciones */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5" />
              <span>Top 5 Soluciones</span>
            </CardTitle>
            <CardDescription>
              Soluciones más solicitadas este mes
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {mockData.topSolutions.map((solution, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="text-lg font-bold text-muted-foreground">
                      #{index + 1}
                    </div>
                    <div>
                      <div className="font-medium text-foreground">{solution.name}</div>
                      <div className="text-sm text-muted-foreground">{solution.count} proyectos</div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {solution.trend === 'up' && (
                      <TrendingUp className="w-4 h-4 text-green-500" />
                    )}
                    {solution.trend === 'down' && (
                      <TrendingDown className="w-4 h-4 text-red-500" />
                    )}
                    {solution.trend === 'stable' && (
                      <Activity className="w-4 h-4 text-yellow-500" />
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Uso de Modelos */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Users className="w-5 h-5" />
              <span>Uso de Modelos IA</span>
            </CardTitle>
            <CardDescription>
              Estadísticas de uso y costos por modelo
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {mockData.modelUsage.map((model, index) => (
                <div key={index} className="p-4 border border-border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-foreground">{model.model}</h4>
                    <Badge variant="outline" className="bg-green-500/10 text-green-500">
                      ${model.cost.toFixed(2)}
                    </Badge>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Requests:</span>
                      <span className="ml-2 font-medium">{model.requests}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Tokens:</span>
                      <span className="ml-2 font-medium">{model.tokens.toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Performance Metrics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Activity className="w-5 h-5" />
            <span>Métricas de Rendimiento</span>
          </CardTitle>
          <CardDescription>
            Indicadores clave de rendimiento del sistema
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-4 bg-muted/30 rounded-lg">
              <div className="text-2xl font-bold text-green-500 mb-2">99.8%</div>
              <div className="text-sm text-muted-foreground">Disponibilidad</div>
              <div className="text-xs text-muted-foreground mt-1">Últimos 30 días</div>
            </div>
            
            <div className="text-center p-4 bg-muted/30 rounded-lg">
              <div className="text-2xl font-bold text-blue-500 mb-2">1.2s</div>
              <div className="text-sm text-muted-foreground">Latencia P95</div>
              <div className="text-xs text-muted-foreground mt-1">Tiempo de respuesta</div>
            </div>
            
            <div className="text-center p-4 bg-muted/30 rounded-lg">
              <div className="text-2xl font-bold text-purple-500 mb-2">0.02%</div>
              <div className="text-sm text-muted-foreground">Tasa de Error</div>
              <div className="text-xs text-muted-foreground mt-1">Requests fallidos</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
