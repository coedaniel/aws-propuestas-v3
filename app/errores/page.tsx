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
  AlertTriangle, 
  XCircle, 
  AlertCircle,
  Search, 
  Filter, 
  Download,
  RefreshCw,
  Eye,
  Trash2,
  Calendar,
  Clock,
  Server,
  Database,
  Network,
  Zap,
  Globe,
  ChevronDown,
  ChevronRight,
  Copy,
  ExternalLink
} from 'lucide-react'

interface LogEntry {
  id: string
  timestamp: string
  level: 'error' | 'warning' | 'info'
  category: 'connection' | 'mcp' | 'model' | 's3' | 'api' | 'system'
  service: string
  message: string
  details?: string
  stackTrace?: string
  userId?: string
  requestId?: string
  resolved: boolean
}

// Mock data - En producción esto vendría de CloudWatch Logs o tu sistema de logging
const mockLogs: LogEntry[] = [
  {
    id: '1',
    timestamp: '2025-01-19T18:45:23Z',
    level: 'error',
    category: 'mcp',
    service: 'CFN MCP',
    message: 'Timeout al generar template CloudFormation',
    details: 'El servicio MCP de CloudFormation tardó más de 30 segundos en responder',
    stackTrace: 'TimeoutError: Request timeout after 30000ms\n  at MCPClient.call(mcp-client.js:45)\n  at CFNGenerator.generate(cfn-generator.js:123)',
    requestId: 'req_abc123',
    resolved: false
  },
  {
    id: '2',
    timestamp: '2025-01-19T18:30:15Z',
    level: 'warning',
    category: 'model',
    service: 'Bedrock Runtime',
    message: 'Latencia alta en modelo Nova Pro',
    details: 'El modelo Nova Pro está respondiendo con latencia superior a 5 segundos',
    requestId: 'req_def456',
    resolved: true
  },
  {
    id: '3',
    timestamp: '2025-01-19T18:15:42Z',
    level: 'error',
    category: 's3',
    service: 'S3 Storage',
    message: 'Error al subir archivo de proyecto',
    details: 'No se pudo subir el archivo diagram.png al bucket aws-propuestas-files',
    stackTrace: 'S3Error: Access Denied\n  at S3Client.upload(s3-client.js:78)\n  at ProjectManager.saveFiles(project-manager.js:234)',
    userId: 'user_789',
    requestId: 'req_ghi789',
    resolved: false
  },
  {
    id: '4',
    timestamp: '2025-01-19T17:58:33Z',
    level: 'warning',
    category: 'connection',
    service: 'Diagram MCP',
    message: 'Conexión intermitente detectada',
    details: 'El servicio MCP de diagramas ha tenido 3 fallos de conexión en los últimos 10 minutos',
    resolved: true
  },
  {
    id: '5',
    timestamp: '2025-01-19T17:45:18Z',
    level: 'error',
    category: 'api',
    service: 'API Gateway',
    message: 'Rate limit excedido',
    details: 'Se ha excedido el límite de 1000 requests por minuto en el endpoint /chat',
    requestId: 'req_jkl012',
    resolved: true
  },
  {
    id: '6',
    timestamp: '2025-01-19T17:30:05Z',
    level: 'info',
    category: 'system',
    service: 'Health Check',
    message: 'Verificación de servicios completada',
    details: 'Todos los servicios están operativos. Tiempo total de verificación: 2.3s',
    resolved: true
  },
  {
    id: '7',
    timestamp: '2025-01-19T17:15:27Z',
    level: 'error',
    category: 'mcp',
    service: 'Pricing MCP',
    message: 'Error al calcular costos',
    details: 'No se pudo obtener precios actualizados de la API de AWS Pricing',
    stackTrace: 'PricingError: API rate limit exceeded\n  at PricingClient.getPrice(pricing-client.js:156)\n  at CostCalculator.calculate(cost-calculator.js:89)',
    requestId: 'req_mno345',
    resolved: false
  }
]

export default function ErroresPage() {
  const [logs, setLogs] = useState<LogEntry[]>(mockLogs)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterLevel, setFilterLevel] = useState<'all' | 'error' | 'warning' | 'info'>('all')
  const [filterCategory, setFilterCategory] = useState<'all' | 'connection' | 'mcp' | 'model' | 's3' | 'api' | 'system'>('all')
  const [filterResolved, setFilterResolved] = useState<'all' | 'resolved' | 'unresolved'>('all')
  const [expandedLog, setExpandedLog] = useState<string | null>(null)
  const [isRefreshing, setIsRefreshing] = useState(false)

  const filteredLogs = logs.filter(log => {
    const matchesSearch = log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         log.service.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         log.details?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesLevel = filterLevel === 'all' || log.level === filterLevel
    const matchesCategory = filterCategory === 'all' || log.category === filterCategory
    const matchesResolved = filterResolved === 'all' || 
                           (filterResolved === 'resolved' && log.resolved) ||
                           (filterResolved === 'unresolved' && !log.resolved)
    
    return matchesSearch && matchesLevel && matchesCategory && matchesResolved
  })

  const refreshLogs = async () => {
    setIsRefreshing(true)
    // Simular carga de logs
    await new Promise(resolve => setTimeout(resolve, 1000))
    setIsRefreshing(false)
  }

  const exportLogs = () => {
    const csvContent = [
      ['Timestamp', 'Level', 'Category', 'Service', 'Message', 'Details', 'Resolved'],
      ...filteredLogs.map(log => [
        log.timestamp,
        log.level,
        log.category,
        log.service,
        log.message,
        log.details || '',
        log.resolved ? 'Yes' : 'No'
      ])
    ].map(row => row.map(cell => `"${cell}"`).join(',')).join('\n')
    
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `error-logs-${new Date().toISOString().split('T')[0]}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const toggleResolved = (logId: string) => {
    setLogs(prev => prev.map(log => 
      log.id === logId ? { ...log, resolved: !log.resolved } : log
    ))
  }

  const deleteLog = (logId: string) => {
    setLogs(prev => prev.filter(log => log.id !== logId))
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const getLevelIcon = (level: LogEntry['level']) => {
    switch (level) {
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" />
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />
      case 'info':
        return <AlertCircle className="w-4 h-4 text-blue-500" />
    }
  }

  const getLevelBadge = (level: LogEntry['level']) => {
    switch (level) {
      case 'error':
        return <Badge className="bg-red-500/10 text-red-500 border-red-500/20">Error</Badge>
      case 'warning':
        return <Badge className="bg-yellow-500/10 text-yellow-500 border-yellow-500/20">Warning</Badge>
      case 'info':
        return <Badge className="bg-blue-500/10 text-blue-500 border-blue-500/20">Info</Badge>
    }
  }

  const getCategoryIcon = (category: LogEntry['category']) => {
    switch (category) {
      case 'connection':
        return <Network className="w-4 h-4 text-cyan-500" />
      case 'mcp':
        return <Server className="w-4 h-4 text-blue-500" />
      case 'model':
        return <Zap className="w-4 h-4 text-purple-500" />
      case 's3':
        return <Database className="w-4 h-4 text-orange-500" />
      case 'api':
        return <Globe className="w-4 h-4 text-green-500" />
      case 'system':
        return <AlertCircle className="w-4 h-4 text-gray-500" />
    }
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  const errorCount = logs.filter(l => l.level === 'error' && !l.resolved).length
  const warningCount = logs.filter(l => l.level === 'warning' && !l.resolved).length
  const totalUnresolved = logs.filter(l => !l.resolved).length

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-foreground">Logs y Errores</h1>
          <p className="text-lg text-muted-foreground">
            Monitoreo y diagnóstico de errores del sistema
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={refreshLogs} disabled={isRefreshing}>
            <RefreshCw className={`w-4 h-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
            Actualizar
          </Button>
          <Button variant="outline" onClick={exportLogs}>
            <Download className="w-4 h-4 mr-2" />
            Exportar CSV
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-red-500/10 rounded-lg">
                <XCircle className="w-5 h-5 text-red-500" />
              </div>
              <div>
                <div className="text-2xl font-bold text-red-500">{errorCount}</div>
                <div className="text-sm text-muted-foreground">Errores Activos</div>
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
                <div className="text-2xl font-bold text-yellow-500">{warningCount}</div>
                <div className="text-sm text-muted-foreground">Advertencias</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-orange-500/10 rounded-lg">
                <AlertCircle className="w-5 h-5 text-orange-500" />
              </div>
              <div>
                <div className="text-2xl font-bold text-orange-500">{totalUnresolved}</div>
                <div className="text-sm text-muted-foreground">Sin Resolver</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-500/10 rounded-lg">
                <Clock className="w-5 h-5 text-blue-500" />
              </div>
              <div>
                <div className="text-2xl font-bold text-blue-500">{logs.length}</div>
                <div className="text-sm text-muted-foreground">Total Logs</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Filter className="w-5 h-5" />
            <span>Filtros</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <div>
              <label className="text-sm font-medium text-muted-foreground mb-2 block">
                Buscar
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar en logs..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div>
              <label className="text-sm font-medium text-muted-foreground mb-2 block">
                Nivel
              </label>
              <select
                value={filterLevel}
                onChange={(e) => setFilterLevel(e.target.value as any)}
                className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground"
              >
                <option value="all">Todos los niveles</option>
                <option value="error">Error</option>
                <option value="warning">Warning</option>
                <option value="info">Info</option>
              </select>
            </div>
            
            <div>
              <label className="text-sm font-medium text-muted-foreground mb-2 block">
                Categoría
              </label>
              <select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value as any)}
                className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground"
              >
                <option value="all">Todas las categorías</option>
                <option value="connection">Conexión</option>
                <option value="mcp">MCP</option>
                <option value="model">Modelo</option>
                <option value="s3">S3</option>
                <option value="api">API</option>
                <option value="system">Sistema</option>
              </select>
            </div>
            
            <div>
              <label className="text-sm font-medium text-muted-foreground mb-2 block">
                Estado
              </label>
              <select
                value={filterResolved}
                onChange={(e) => setFilterResolved(e.target.value as any)}
                className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground"
              >
                <option value="all">Todos</option>
                <option value="unresolved">Sin resolver</option>
                <option value="resolved">Resueltos</option>
              </select>
            </div>
            
            <div className="flex items-end">
              <Button 
                variant="outline" 
                onClick={() => {
                  setSearchTerm('')
                  setFilterLevel('all')
                  setFilterCategory('all')
                  setFilterResolved('all')
                }}
                className="w-full"
              >
                Limpiar Filtros
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Logs Table */}
      <Card>
        <CardHeader>
          <CardTitle>Registro de Logs</CardTitle>
          <CardDescription>
            {filteredLogs.length} de {logs.length} entradas
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {filteredLogs.map((log) => (
              <div key={log.id} className="border border-border rounded-lg">
                <div 
                  className="p-4 cursor-pointer hover:bg-muted/30 transition-colors"
                  onClick={() => setExpandedLog(expandedLog === log.id ? null : log.id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4 flex-1">
                      <div className="flex items-center space-x-2">
                        {expandedLog === log.id ? (
                          <ChevronDown className="w-4 h-4 text-muted-foreground" />
                        ) : (
                          <ChevronRight className="w-4 h-4 text-muted-foreground" />
                        )}
                        {getLevelIcon(log.level)}
                      </div>
                      
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <span className="font-medium text-foreground">{log.message}</span>
                          {getLevelBadge(log.level)}
                          {log.resolved && (
                            <Badge variant="outline" className="bg-green-500/10 text-green-500">
                              Resuelto
                            </Badge>
                          )}
                        </div>
                        <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                          <div className="flex items-center space-x-1">
                            {getCategoryIcon(log.category)}
                            <span>{log.service}</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <Clock className="w-3 h-3" />
                            <span>{formatTimestamp(log.timestamp)}</span>
                          </div>
                          {log.requestId && (
                            <div className="flex items-center space-x-1">
                              <span>ID: {log.requestId}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation()
                          toggleResolved(log.id)
                        }}
                      >
                        {log.resolved ? 'Marcar pendiente' : 'Marcar resuelto'}
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation()
                          deleteLog(log.id)
                        }}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </div>
                
                {expandedLog === log.id && (
                  <div className="border-t border-border p-4 bg-muted/20">
                    {log.details && (
                      <div className="mb-4">
                        <h4 className="font-medium text-foreground mb-2">Detalles</h4>
                        <p className="text-sm text-muted-foreground">{log.details}</p>
                      </div>
                    )}
                    
                    {log.stackTrace && (
                      <div className="mb-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-foreground">Stack Trace</h4>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => copyToClipboard(log.stackTrace!)}
                          >
                            <Copy className="w-4 h-4" />
                          </Button>
                        </div>
                        <pre className="text-xs bg-muted p-3 rounded border overflow-x-auto">
                          {log.stackTrace}
                        </pre>
                      </div>
                    )}
                    
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Timestamp:</span>
                        <span className="ml-2 font-mono">{log.timestamp}</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Categoría:</span>
                        <span className="ml-2">{log.category}</span>
                      </div>
                      {log.userId && (
                        <div>
                          <span className="text-muted-foreground">Usuario:</span>
                          <span className="ml-2">{log.userId}</span>
                        </div>
                      )}
                      {log.requestId && (
                        <div>
                          <span className="text-muted-foreground">Request ID:</span>
                          <span className="ml-2 font-mono">{log.requestId}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
          
          {filteredLogs.length === 0 && (
            <div className="text-center py-8">
              <AlertCircle className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium text-foreground mb-2">No se encontraron logs</h3>
              <p className="text-muted-foreground">
                {searchTerm || filterLevel !== 'all' || filterCategory !== 'all' || filterResolved !== 'all'
                  ? 'Intenta ajustar los filtros de búsqueda'
                  : 'No hay logs disponibles en este momento'}
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
