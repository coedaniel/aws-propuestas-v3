'use client'

import React from 'react'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  MessageCircle, 
  Bot, 
  FolderOpen, 
  BarChart3,
  Zap,
  ArrowRight,
  Cpu,
  Network,
  CheckCircle,
  AlertCircle,
  Clock,
  TrendingUp,
  Users,
  FileText,
  Sparkles
} from 'lucide-react'

export default function HomePage() {
  return (
    <div className="p-6 space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-foreground">
          Bienvenido a AWS Propuestas v3
        </h1>
        <p className="text-lg text-muted-foreground">
          Plataforma inteligente para generar propuestas arquitectónicas profesionales con IA
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Link href="/chat">
          <Card className="hover-lift cursor-pointer transition-all duration-200 hover:border-primary/50">
            <CardHeader className="pb-3">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-blue-500/10 rounded-lg">
                  <MessageCircle className="w-6 h-6 text-blue-500" />
                </div>
                <div>
                  <CardTitle className="text-lg">Chat Libre</CardTitle>
                  <CardDescription>Conversa con IA</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-3">
                Interactúa libremente con modelos de Bedrock para consultas técnicas
              </p>
              <div className="flex items-center text-primary text-sm font-medium">
                Iniciar chat <ArrowRight className="w-4 h-4 ml-1" />
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/arquitecto">
          <Card className="hover-lift cursor-pointer transition-all duration-200 hover:border-primary/50">
            <CardHeader className="pb-3">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-purple-500/10 rounded-lg">
                  <Bot className="w-6 h-6 text-purple-500" />
                </div>
                <div>
                  <CardTitle className="text-lg">Arquitecto IA</CardTitle>
                  <CardDescription>Genera propuestas</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-3">
                Crea propuestas arquitectónicas profesionales paso a paso
              </p>
              <div className="flex items-center text-primary text-sm font-medium">
                Crear propuesta <ArrowRight className="w-4 h-4 ml-1" />
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/proyectos">
          <Card className="hover-lift cursor-pointer transition-all duration-200 hover:border-primary/50">
            <CardHeader className="pb-3">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-green-500/10 rounded-lg">
                  <FolderOpen className="w-6 h-6 text-green-500" />
                </div>
                <div>
                  <CardTitle className="text-lg">Proyectos</CardTitle>
                  <CardDescription>Gestiona trabajos</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-3">
                Administra y descarga todos tus proyectos generados
              </p>
              <div className="flex items-center text-primary text-sm font-medium">
                Ver proyectos <ArrowRight className="w-4 h-4 ml-1" />
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/analitica">
          <Card className="hover-lift cursor-pointer transition-all duration-200 hover:border-primary/50">
            <CardHeader className="pb-3">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-orange-500/10 rounded-lg">
                  <BarChart3 className="w-6 h-6 text-orange-500" />
                </div>
                <div>
                  <CardTitle className="text-lg">Analítica</CardTitle>
                  <CardDescription>Métricas y datos</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-3">
                Visualiza estadísticas de uso y rendimiento del sistema
              </p>
              <div className="flex items-center text-primary text-sm font-medium">
                Ver métricas <ArrowRight className="w-4 h-4 ml-1" />
              </div>
            </CardContent>
          </Card>
        </Link>
      </div>

      {/* System Status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Cpu className="w-5 h-5 text-primary" />
              <span>Estado del Sistema</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span className="text-sm">Bedrock Runtime</span>
              </div>
              <Badge variant="secondary" className="bg-green-500/10 text-green-500">
                Activo
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span className="text-sm">Servicios MCP</span>
              </div>
              <Badge variant="secondary" className="bg-green-500/10 text-green-500">
                6/6 Online
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span className="text-sm">API Gateway</span>
              </div>
              <Badge variant="secondary" className="bg-green-500/10 text-green-500">
                Operativo
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 text-yellow-500" />
                <span className="text-sm">Almacenamiento S3</span>
              </div>
              <Badge variant="secondary" className="bg-yellow-500/10 text-yellow-500">
                Monitoreando
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-primary" />
              <span>Estadísticas Rápidas</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <FileText className="w-4 h-4 text-blue-500" />
                <span className="text-sm">Proyectos Creados</span>
              </div>
              <span className="text-lg font-semibold">24</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <MessageCircle className="w-4 h-4 text-purple-500" />
                <span className="text-sm">Conversaciones</span>
              </div>
              <span className="text-lg font-semibold">156</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Zap className="w-4 h-4 text-orange-500" />
                <span className="text-sm">MCPs Ejecutados</span>
              </div>
              <span className="text-lg font-semibold">89</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4 text-green-500" />
                <span className="text-sm">Tiempo Promedio</span>
              </div>
              <span className="text-lg font-semibold">2.3s</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-primary" />
              <span>Modelos Disponibles</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium">Nova Pro v1.0</div>
                  <div className="text-xs text-muted-foreground">Multimodal</div>
                </div>
                <Badge variant="secondary" className="bg-blue-500/10 text-blue-500">
                  Activo
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium">Claude 3.5 Sonnet v2</div>
                  <div className="text-xs text-muted-foreground">Análisis profundo</div>
                </div>
                <Badge variant="secondary" className="bg-purple-500/10 text-purple-500">
                  Activo
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium">Claude Sonnet 4</div>
                  <div className="text-xs text-muted-foreground">Cross-region</div>
                </div>
                <Badge variant="secondary" className="bg-green-500/10 text-green-500">
                  Disponible
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Actividad Reciente</CardTitle>
          <CardDescription>
            Últimas acciones realizadas en la plataforma
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center space-x-4 p-3 bg-muted/30 rounded-lg">
              <div className="p-2 bg-green-500/10 rounded-lg">
                <CheckCircle className="w-4 h-4 text-green-500" />
              </div>
              <div className="flex-1">
                <div className="text-sm font-medium">Proyecto "Migración Cloud" completado</div>
                <div className="text-xs text-muted-foreground">Hace 2 horas • Arquitecto IA</div>
              </div>
            </div>
            <div className="flex items-center space-x-4 p-3 bg-muted/30 rounded-lg">
              <div className="p-2 bg-blue-500/10 rounded-lg">
                <MessageCircle className="w-4 h-4 text-blue-500" />
              </div>
              <div className="flex-1">
                <div className="text-sm font-medium">Nueva conversación iniciada</div>
                <div className="text-xs text-muted-foreground">Hace 4 horas • Chat Libre</div>
              </div>
            </div>
            <div className="flex items-center space-x-4 p-3 bg-muted/30 rounded-lg">
              <div className="p-2 bg-purple-500/10 rounded-lg">
                <Zap className="w-4 h-4 text-purple-500" />
              </div>
              <div className="flex-1">
                <div className="text-sm font-medium">MCP Diagram ejecutado exitosamente</div>
                <div className="text-xs text-muted-foreground">Hace 6 horas • Sistema</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
