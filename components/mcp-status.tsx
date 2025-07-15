'use client'

import { useState, useEffect } from 'react'
import { checkHealth } from '@/lib/api'

interface HealthStatus {
  status: string
  timestamp: string
  legacy_api?: boolean
  mcp_servers?: { [key: string]: boolean }
}

export function MCPStatus() {
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const checkSystemHealth = async () => {
      try {
        setLoading(true)
        const status = await checkHealth()
        setHealthStatus(status)
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Health check failed')
      } finally {
        setLoading(false)
      }
    }

    checkSystemHealth()
    
    // Check health every 30 seconds
    const interval = setInterval(checkSystemHealth, 30000)
    
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="flex items-center space-x-2 text-sm text-gray-500">
        <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
        <span>Checking system status...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center space-x-2 text-sm text-red-600">
        <div className="w-2 h-2 bg-red-500 rounded-full"></div>
        <span>System check failed</span>
      </div>
    )
  }

  if (!healthStatus) {
    return null
  }

  const isHealthy = healthStatus.status === 'healthy'
  const mcpServers = healthStatus.mcp_servers || {}
  const healthyMCPCount = Object.values(mcpServers).filter(Boolean).length
  const totalMCPCount = Object.keys(mcpServers).length

  return (
    <div className="flex items-center space-x-2 text-sm">
      <div className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-green-500' : 'bg-red-500'}`}></div>
      <span className={isHealthy ? 'text-green-600' : 'text-red-600'}>
        System {isHealthy ? 'Healthy' : 'Degraded'}
      </span>
      
      {totalMCPCount > 0 && (
        <span className="text-gray-500">
          • MCP: {healthyMCPCount}/{totalMCPCount}
        </span>
      )}
      
      {healthStatus.legacy_api && (
        <span className="text-blue-500">• Legacy API</span>
      )}
    </div>
  )
}

export function MCPStatusDetailed() {
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const checkSystemHealth = async () => {
      try {
        setLoading(true)
        const status = await checkHealth()
        setHealthStatus(status)
      } catch (err) {
        console.error('Health check failed:', err)
      } finally {
        setLoading(false)
      }
    }

    checkSystemHealth()
  }, [])

  if (loading || !healthStatus) {
    return <div>Loading system status...</div>
  }

  const mcpServers = healthStatus.mcp_servers || {}

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-2">
        <h3 className="text-lg font-semibold">System Status</h3>
        <div className={`w-3 h-3 rounded-full ${healthStatus.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'}`}></div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Legacy API Status */}
        <div className="p-4 border rounded-lg">
          <div className="flex items-center justify-between">
            <span className="font-medium">Legacy API</span>
            <div className={`w-2 h-2 rounded-full ${healthStatus.legacy_api ? 'bg-green-500' : 'bg-red-500'}`}></div>
          </div>
          <p className="text-sm text-gray-600 mt-1">
            {healthStatus.legacy_api ? 'Available' : 'Unavailable'}
          </p>
        </div>

        {/* MCP Servers Status */}
        {Object.entries(mcpServers).map(([serverName, isHealthy]) => (
          <div key={serverName} className="p-4 border rounded-lg">
            <div className="flex items-center justify-between">
              <span className="font-medium capitalize">{serverName} MCP</span>
              <div className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-green-500' : 'bg-red-500'}`}></div>
            </div>
            <p className="text-sm text-gray-600 mt-1">
              {isHealthy ? 'Available' : 'Unavailable'}
            </p>
          </div>
        ))}
      </div>

      <div className="text-xs text-gray-500">
        Last checked: {new Date(healthStatus.timestamp).toLocaleString()}
      </div>
    </div>
  )
}
