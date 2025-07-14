'use client'

import React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { 
  Cloud, 
  FolderOpen, 
  MessageCircle, 
  Building2, 
  BarChart3,
  Home
} from 'lucide-react'

interface AppLayoutProps {
  children: React.ReactNode
  showSidebar?: boolean
}

export default function AppLayout({ children, showSidebar = true }: AppLayoutProps) {
  const pathname = usePathname()

  const navigation = [
    { name: 'Inicio', href: '/', icon: Home },
    { name: 'Chat', href: '/chat', icon: MessageCircle },
    { name: 'Arquitecto', href: '/arquitecto', icon: Building2 },
    { name: 'Proyectos', href: '/projects', icon: FolderOpen },
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  ]

  if (!showSidebar) {
    return <>{children}</>
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <Cloud className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">AWS Propuestas v3</h1>
                <p className="text-sm text-gray-600">Sistema Conversacional Profesional</p>
              </div>
            </Link>
            
            {/* Navigation */}
            <nav className="hidden md:flex items-center space-x-1">
              {navigation.map((item) => {
                const isActive = pathname === item.href
                const Icon = item.icon
                return (
                  <Link key={item.name} href={item.href}>
                    <Button 
                      variant={isActive ? "default" : "ghost"} 
                      size="sm"
                      className={isActive ? "bg-blue-600 hover:bg-blue-700" : ""}
                    >
                      <Icon className="w-4 h-4 mr-2" />
                      {item.name}
                    </Button>
                  </Link>
                )
              })}
            </nav>

            {/* Mobile menu button */}
            <div className="md:hidden">
              <Button variant="outline" size="sm">
                <FolderOpen className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>
    </div>
  )
}
