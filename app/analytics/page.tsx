'use client'

import React, { useState, useEffect } from 'react'
import AppLayout from '@/components/AppLayout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { 
  BarChart3, 
  TrendingUp, 
  PieChart, 
  Activity,
  DollarSign,
  Users,
  Calendar,
  Award,
  Target,
  Zap,
  Cloud,
  Database,
  Server,
  Globe,
  Shield,
  Cpu,
  HardDrive,
  Network,
  RefreshCw,
  Clock
} from 'lucide-react'
import { getProjects } from '@/lib/api'

interface Project {
  projectId: string
  projectName: string
  status: string
  currentStep: string
  createdAt: string
  updatedAt: string
  documentCount: number
  hasDocuments: boolean
  projectInfo: any
  lastMessage: string
}

interface AnalyticsData {
  totalProjects: number
  completedProjects: number
  inProgressProjects: number
  archivedProjects: number
  totalDocuments: number
  avgProjectDuration: number
  successRate: number
  monthlyGrowth: number
  topServices: Array<{ name: string; count: number; icon: React.ReactNode }>
  projectsByMonth: Array<{ month: string; count: number }>
  statusDistribution: Array<{ status: string; count: number; color: string }>
  recentActivity: Array<{ date: string; action: string; project: string }>
}

export default function AnalyticsPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    loadAnalytics()
  }, [])

  const loadAnalytics = async () => {
    try {
      setIsLoading(true)
      const projectsData = await getProjects()
      setProjects(projectsData)
      
      // Calculate analytics
      const analyticsData = calculateAnalytics(projectsData)
      setAnalytics(analyticsData)
    } catch (error) {
      console.error('Error loading analytics:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    await loadAnalytics()
    setRefreshing(false)
  }

  const calculateAnalytics = (projects: Project[]): AnalyticsData => {
    const totalProjects = projects.length
    const completedProjects = projects.filter(p => p.status === 'COMPLETED').length
    const inProgressProjects = projects.filter(p => p.status === 'IN_PROGRESS').length
    const archivedProjects = projects.filter(p => p.status === 'ARCHIVED').length
    const totalDocuments = projects.reduce((sum, p) => sum + p.documentCount, 0)

    // Calculate average project duration (mock data for now)
    const avgProjectDuration = 7.5 // days

    // Calculate success rate
    const successRate = totalProjects > 0 ? (completedProjects / totalProjects) * 100 : 0

    // Mock monthly growth
    const monthlyGrowth = 15.3

    // Top AWS services (mock data based on common usage)
    const topServices = [
      { name: 'Lambda', count: Math.floor(totalProjects * 0.8), icon: <Zap className="h-5 w-5" /> },
      { name: 'DynamoDB', count: Math.floor(totalProjects * 0.7), icon: <Database className="h-5 w-5" /> },
      { name: 'API Gateway', count: Math.floor(totalProjects * 0.6), icon: <Globe className="h-5 w-5" /> },
      { name: 'S3', count: Math.floor(totalProjects * 0.9), icon: <HardDrive className="h-5 w-5" /> },
      { name: 'CloudFront', count: Math.floor(totalProjects * 0.4), icon: <Network className="h-5 w-5" /> },
      { name: 'EC2', count: Math.floor(totalProjects * 0.3), icon: <Server className="h-5 w-5" /> },
      { name: 'RDS', count: Math.floor(totalProjects * 0.25), icon: <Cpu className="h-5 w-5" /> },
      { name: 'IAM', count: Math.floor(totalProjects * 0.95), icon: <Shield className="h-5 w-5" /> }
    ].sort((a, b) => b.count - a.count)

    // Projects by month (last 6 months)
    const projectsByMonth = generateMonthlyData(projects)

    // Status distribution
    const statusDistribution = [
      { status: 'Completados', count: completedProjects, color: '#10B981' },
      { status: 'En Progreso', count: inProgressProjects, color: '#3B82F6' },
      { status: 'Archivados', count: archivedProjects, color: '#6B7280' }
    ]

    // Recent activity (mock data)
    const recentActivity = [
      { date: '2025-07-13', action: 'Proyecto completado', project: 'Sistema E-commerce' },
      { date: '2025-07-13', action: 'Documentos generados', project: 'API Microservicios' },
      { date: '2025-07-12', action: 'Nuevo proyecto creado', project: 'Dashboard Analytics' },
      { date: '2025-07-12', action: 'Arquitectura actualizada', project: 'Sistema IoT' },
      { date: '2025-07-11', action: 'Proyecto completado', project: 'Portal Clientes' }
    ]

    return {
      totalProjects,
      completedProjects,
      inProgressProjects,
      archivedProjects,
      totalDocuments,
      avgProjectDuration,
      successRate,
      monthlyGrowth,
      topServices,
      projectsByMonth,
      statusDistribution,
      recentActivity
    }
  }

  const generateMonthlyData = (projects: Project[]) => {
    const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']
    const data = months.map(month => ({
      month,
      count: Math.floor(Math.random() * 10) + 1
    }))
    return data
  }

  if (isLoading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
            <p>Cargando analytics...</p>
          </div>
        </div>
      </AppLayout>
    )
  }

  if (!analytics) {
    return (
      <AppLayout>
        <div className="p-6">
          <div className="text-center py-12">
            <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Error al cargar analytics</h3>
            <Button onClick={loadAnalytics}>Reintentar</Button>
          </div>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Analytics & Insights</h1>
            <p className="text-gray-600">Análisis detallado de tus proyectos AWS y métricas de rendimiento</p>
          </div>
          <Button onClick={handleRefresh} disabled={refreshing} variant="outline">
            <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Actualizar
          </Button>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-100">Total Proyectos</p>
                  <p className="text-3xl font-bold">{analytics.totalProjects}</p>
                  <p className="text-sm text-blue-100">+{analytics.monthlyGrowth}% este mes</p>
                </div>
                <BarChart3 className="h-12 w-12 text-blue-200" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-r from-green-500 to-green-600 text-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-100">Tasa de Éxito</p>
                  <p className="text-3xl font-bold">{analytics.successRate.toFixed(1)}%</p>
                  <p className="text-sm text-green-100">{analytics.completedProjects} completados</p>
                </div>
                <Target className="h-12 w-12 text-green-200" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-r from-purple-500 to-purple-600 text-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-purple-100">Documentos</p>
                  <p className="text-3xl font-bold">{analytics.totalDocuments}</p>
                  <p className="text-sm text-purple-100">Generados automáticamente</p>
                </div>
                <Award className="h-12 w-12 text-purple-200" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-r from-orange-500 to-orange-600 text-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-orange-100">Tiempo Promedio</p>
                  <p className="text-3xl font-bold">{analytics.avgProjectDuration}</p>
                  <p className="text-sm text-orange-100">días por proyecto</p>
                </div>
                <Clock className="h-12 w-12 text-orange-200" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Projects by Month */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <TrendingUp className="h-5 w-5 mr-2" />
                Proyectos por Mes
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {analytics.projectsByMonth.map((item, index) => (
                  <div key={item.month} className="flex items-center justify-between">
                    <span className="text-sm font-medium">{item.month}</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-32 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                          style={{ width: `${(item.count / Math.max(...analytics.projectsByMonth.map(p => p.count))) * 100}%` }}
                        />
                      </div>
                      <span className="text-sm text-gray-600 w-8">{item.count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Status Distribution */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <PieChart className="h-5 w-5 mr-2" />
                Distribución por Estado
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {analytics.statusDistribution.map((item, index) => (
                  <div key={item.status} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div 
                        className="w-4 h-4 rounded-full"
                        style={{ backgroundColor: item.color }}
                      />
                      <span className="text-sm font-medium">{item.status}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-gray-200 rounded-full h-2">
                        <div 
                          className="h-2 rounded-full transition-all duration-500"
                          style={{ 
                            width: `${(item.count / analytics.totalProjects) * 100}%`,
                            backgroundColor: item.color
                          }}
                        />
                      </div>
                      <span className="text-sm text-gray-600 w-8">{item.count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Services and Activity Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top AWS Services */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Cloud className="h-5 w-5 mr-2" />
                Servicios AWS Más Utilizados
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {analytics.topServices.slice(0, 6).map((service, index) => (
                  <div key={service.name} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="text-blue-600">
                        {service.icon}
                      </div>
                      <span className="font-medium">{service.name}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-20 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                          style={{ width: `${(service.count / Math.max(...analytics.topServices.map(s => s.count))) * 100}%` }}
                        />
                      </div>
                      <span className="text-sm text-gray-600 w-6">{service.count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Activity className="h-5 w-5 mr-2" />
                Actividad Reciente
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {analytics.recentActivity.map((activity, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                    <div className="w-2 h-2 bg-blue-600 rounded-full mt-2" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">{activity.action}</p>
                      <p className="text-sm text-gray-600">{activity.project}</p>
                      <p className="text-xs text-gray-400">{activity.date}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Performance Insights */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <TrendingUp className="h-5 w-5 mr-2" />
              Insights de Rendimiento
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600 mb-2">
                  {analytics.successRate > 80 ? '🚀' : analytics.successRate > 60 ? '📈' : '⚠️'}
                </div>
                <h3 className="font-semibold text-green-800">Rendimiento Excelente</h3>
                <p className="text-sm text-green-600">
                  Tu tasa de éxito del {analytics.successRate.toFixed(1)}% está por encima del promedio
                </p>
              </div>
              
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600 mb-2">⚡</div>
                <h3 className="font-semibold text-blue-800">Automatización Efectiva</h3>
                <p className="text-sm text-blue-600">
                  {analytics.totalDocuments} documentos generados automáticamente
                </p>
              </div>
              
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600 mb-2">🎯</div>
                <h3 className="font-semibold text-purple-800">Crecimiento Sostenido</h3>
                <p className="text-sm text-purple-600">
                  +{analytics.monthlyGrowth}% de crecimiento mensual en proyectos
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}
