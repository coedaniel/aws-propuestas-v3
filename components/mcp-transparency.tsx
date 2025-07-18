'use client'

import { useState } from 'react'

interface MCPTransparencyProps {
  mcpService: string
  action: string
  status: 'preparing' | 'executing' | 'completed' | 'error'
  details?: string
}

export function MCPTransparency({ mcpService, action, status, details }: MCPTransparencyProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  const getStatusIcon = () => {
    switch (status) {
      case 'preparing': return '🔄'
      case 'executing': return '⚡'
      case 'completed': return '✅'
      case 'error': return '❌'
      default: return '🔄'
    }
  }

  const getStatusColor = () => {
    switch (status) {
      case 'preparing': return 'text-blue-600 bg-blue-50 border-blue-200'
      case 'executing': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'completed': return 'text-green-600 bg-green-50 border-green-200'
      case 'error': return 'text-red-600 bg-red-50 border-red-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getStatusMessage = () => {
    switch (status) {
      case 'preparing': return `Preparando MCP \`${mcpService}\` para ${action}...`
      case 'executing': return `Ejecutando MCP \`${mcpService}\` - ${action}...`
      case 'completed': return `✅ MCP \`${mcpService}\` completado exitosamente`
      case 'error': return `❌ Error en MCP \`${mcpService}\``
      default: return `MCP \`${mcpService}\` - ${action}`
    }
  }

  return (
    <div className={`border rounded-lg p-3 mb-3 ${getStatusColor()}`}>
      <div 
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center space-x-2">
          <span className="text-lg">{getStatusIcon()}</span>
          <span className="font-medium text-sm">
            {getStatusMessage()}
          </span>
        </div>
        <button className="text-xs opacity-60 hover:opacity-100">
          {isExpanded ? '▼' : '▶'}
        </button>
      </div>
      
      {isExpanded && details && (
        <div className="mt-2 pt-2 border-t border-current border-opacity-20">
          <pre className="text-xs opacity-80 whitespace-pre-wrap">{details}</pre>
        </div>
      )}
    </div>
  )
}

export function MCPServiceIndicator({ services }: { services: string[] }) {
  return (
    <div className="flex flex-wrap gap-1 mt-2">
      <span className="text-xs text-gray-500">Servicios MCP utilizados:</span>
      {services.map((service, index) => (
        <span 
          key={index}
          className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800"
        >
          {service}
        </span>
      ))}
    </div>
  )
}

// Nuevo componente para notificaciones MCP en tiempo real
export function MCPNotification({ message, type = 'info' }: { message: string, type?: 'info' | 'success' | 'warning' | 'error' }) {
  const getTypeStyles = () => {
    switch (type) {
      case 'info': return 'bg-blue-50 border-blue-200 text-blue-700'
      case 'success': return 'bg-green-50 border-green-200 text-green-700'
      case 'warning': return 'bg-yellow-50 border-yellow-200 text-yellow-700'
      case 'error': return 'bg-red-50 border-red-200 text-red-700'
      default: return 'bg-blue-50 border-blue-200 text-blue-700'
    }
  }

  const getTypeIcon = () => {
    switch (type) {
      case 'info': return '✅'
      case 'success': return '✅'
      case 'warning': return '⚠️'
      case 'error': return '❌'
      default: return '✅'
    }
  }

  return (
    <div className={`border rounded-lg p-3 mb-3 ${getTypeStyles()}`}>
      <div className="flex items-center space-x-2">
        <span className="text-lg">{getTypeIcon()}</span>
        <span className="font-medium text-sm">{message}</span>
      </div>
    </div>
  )
}
