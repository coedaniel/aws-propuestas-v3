'use client'

import React, { useState } from 'react'
import { usePathname } from 'next/navigation'
import Link from 'next/link'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { 
  MessageCircle, 
  BarChart3, 
  FolderOpen, 
  AlertTriangle, 
  Settings,
  Menu,
  X,
  Zap,
  Bot,
  Cpu,
  Network,
  Home
} from 'lucide-react'

const navigation = [
  {
    name: 'Inicio',
    href: '/',
    icon: Home,
    description: 'Panel principal'
  },
  {
    name: 'Chat Libre',
    href: '/chat',
    icon: MessageCircle,
    description: 'Conversación libre con IA'
  },
  {
    name: 'Arquitecto',
    href: '/arquitecto',
    icon: Bot,
    description: 'Generación de propuestas'
  },
  {
    name: 'Proyectos',
    href: '/proyectos',
    icon: FolderOpen,
    description: 'Gestión de proyectos'
  },
  {
    name: 'Analítica',
    href: '/analitica',
    icon: BarChart3,
    description: 'Métricas y estadísticas'
  },
  {
    name: 'Conexiones',
    href: '/conexiones',
    icon: Network,
    description: 'Estado de servicios'
  },
  {
    name: 'Errores',
    href: '/errores',
    icon: AlertTriangle,
    description: 'Logs y diagnósticos'
  }
]

interface AppLayoutProps {
  children: React.ReactNode
}

export function AppLayout({ children }: AppLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const pathname = usePathname()

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={cn(
        "fixed inset-y-0 left-0 z-50 w-72 transform bg-card border-r border-border transition-transform duration-300 ease-in-out lg:translate-x-0",
        sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
      )}>
        <div className="flex h-full flex-col">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-border">
            <div className="flex items-center space-x-3">
              <div className="flex items-center justify-center w-10 h-10 bg-primary rounded-lg">
                <Zap className="w-6 h-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-foreground">AWS Propuestas</h1>
                <p className="text-xs text-muted-foreground">v3.0 Professional</p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="lg:hidden"
              onClick={() => setSidebarOpen(false)}
            >
              <X className="w-5 h-5" />
            </Button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2">
            {navigation.map((item) => {
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
                  )}
                  onClick={() => setSidebarOpen(false)}
                >
                  <item.icon className="w-5 h-5" />
                  <div className="flex-1">
                    <div className="font-medium">{item.name}</div>
                    <div className="text-xs opacity-75">{item.description}</div>
                  </div>
                </Link>
              )
            })}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-border">
            <div className="flex items-center space-x-3 p-3 bg-muted/30 rounded-lg">
              <Cpu className="w-5 h-5 text-primary" />
              <div className="flex-1 text-xs">
                <div className="font-medium text-foreground">6 MCP Activos</div>
                <div className="text-muted-foreground">Bedrock Runtime OK</div>
              </div>
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-72">
        {/* Mobile header */}
        <div className="sticky top-0 z-30 flex items-center justify-between p-4 bg-background/80 backdrop-blur-sm border-b border-border lg:hidden">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="w-5 h-5" />
          </Button>
          <div className="flex items-center space-x-2">
            <Zap className="w-5 h-5 text-primary" />
            <span className="font-semibold text-foreground">AWS Propuestas</span>
          </div>
          <div className="w-8" /> {/* Spacer */}
        </div>

        {/* Page content */}
        <main className="min-h-screen">
          {children}
        </main>
      </div>
    </div>
  )
}

export default AppLayout
