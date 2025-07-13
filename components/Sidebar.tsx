'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { 
  Cloud,
  MessageCircle,
  Building2,
  FolderOpen,
  User,
  Settings,
  LogOut,
  Menu,
  X,
  Home
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface SidebarProps {
  className?: string
}

export default function Sidebar({ className }: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const pathname = usePathname()

  const navigation = [
    {
      name: 'Inicio',
      href: '/',
      icon: Home,
      current: pathname === '/'
    },
    {
      name: 'Chat Libre',
      href: '/chat',
      icon: MessageCircle,
      current: pathname === '/chat'
    },
    {
      name: 'Crear Propuesta',
      href: '/arquitecto',
      icon: Building2,
      current: pathname === '/arquitecto'
    },
    {
      name: 'Proyectos',
      href: '/projects',
      icon: FolderOpen,
      current: pathname === '/projects'
    }
  ]

  const userNavigation = [
    {
      name: 'Mi Perfil',
      href: '#',
      icon: User,
      disabled: true
    },
    {
      name: 'Configuración',
      href: '#',
      icon: Settings,
      disabled: true
    },
    {
      name: 'Cerrar Sesión',
      href: '#',
      icon: LogOut,
      disabled: true
    }
  ]

  return (
    <div className={cn(
      "flex flex-col h-full bg-white border-r border-gray-200 transition-all duration-300",
      isCollapsed ? "w-16" : "w-64",
      className
    )}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        {!isCollapsed && (
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <Cloud className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-sm font-bold text-gray-900">AWS Propuestas v3</h1>
              <p className="text-xs text-gray-600">Sistema Profesional</p>
            </div>
          </div>
        )}
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-2"
        >
          {isCollapsed ? <Menu className="h-4 w-4" /> : <X className="h-4 w-4" />}
        </Button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        <div className="space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors",
                  item.current
                    ? "bg-blue-100 text-blue-700"
                    : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                )}
              >
                <Icon className={cn("flex-shrink-0", isCollapsed ? "h-5 w-5" : "h-5 w-5 mr-3")} />
                {!isCollapsed && item.name}
              </Link>
            )
          })}
        </div>

        {/* Divider */}
        <div className="border-t border-gray-200 my-4" />

        {/* User Navigation */}
        <div className="space-y-1">
          {!isCollapsed && (
            <p className="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Usuario
            </p>
          )}
          {userNavigation.map((item) => {
            const Icon = item.icon
            return (
              <button
                key={item.name}
                disabled={item.disabled}
                className={cn(
                  "w-full flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors",
                  item.disabled
                    ? "text-gray-400 cursor-not-allowed"
                    : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                )}
                onClick={() => {
                  if (!item.disabled) {
                    // Handle navigation
                  } else {
                    alert('Funcionalidad próximamente disponible')
                  }
                }}
              >
                <Icon className={cn("flex-shrink-0", isCollapsed ? "h-5 w-5" : "h-5 w-5 mr-3")} />
                {!isCollapsed && item.name}
              </button>
            )
          })}
        </div>
      </nav>

      {/* Footer */}
      {!isCollapsed && (
        <div className="p-4 border-t border-gray-200">
          <div className="text-xs text-gray-500 text-center">
            <p>v3.0.0</p>
            <p>© 2025 AWS Propuestas</p>
          </div>
        </div>
      )}
    </div>
  )
}
