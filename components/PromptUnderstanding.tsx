'use client'

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Message } from '@/lib/types'
import { 
  Brain, 
  Zap, 
  Target, 
  FileText,
  Bot,
  User,
  Cpu,
  Network,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react'

interface PromptUnderstandingProps {
  messages: Message[]
}

export function PromptUnderstanding({ messages }: PromptUnderstandingProps) {
  const assistantMessages = messages.filter(m => m.role === 'assistant')
  const totalMcpUsage = assistantMessages.reduce((acc, msg) => acc + (msg.mcpUsed?.length || 0), 0)
  const totalTokens = assistantMessages.reduce((acc, msg) => 
    acc + (msg.usage?.inputTokens || 0) + (msg.usage?.outputTokens || 0), 0
  )

  return (
    <div className="h-full flex flex-col bg-gray-900 text-white min-w-0">
      <div className="p-4 border-b border-gray-700 flex-shrink-0">
        <h3 className="text-lg font-semibold text-white flex items-center space-x-2">
          <Brain className="w-5 h-5 text-blue-400" />
          <span>Análisis de Conversación</span>
        </h3>
        <p className="text-sm text-gray-400 mt-1">
          Entendimiento del prompt y uso de recursos
        </p>
      </div>

      <ScrollArea className="flex-1 p-4 min-h-0">
        <div className="space-y-4">
          {/* Summary Stats */}
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center space-x-2 text-white">
                <Target className="w-4 h-4 text-green-400" />
                <span>Resumen de Sesión</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">Mensajes totales</span>
                <Badge variant="secondary" className="bg-gray-700 text-white border-gray-600">
                  {messages.length}
                </Badge>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">MCPs ejecutados</span>
                <Badge variant="secondary" className="bg-purple-900/50 text-purple-300 border-purple-700">
                  {totalMcpUsage}
                </Badge>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">Tokens procesados</span>
                <Badge variant="secondary" className="bg-blue-900/50 text-blue-300 border-blue-700">
                  {totalTokens.toLocaleString()}
                </Badge>
              </div>
            </CardContent>
          </Card>

          {/* Message Analysis */}
          {messages.length > 0 && (
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm flex items-center space-x-2 text-white">
                  <FileText className="w-4 h-4 text-yellow-400" />
                  <span>Análisis por Mensaje</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 max-h-80 overflow-y-auto">
                  {messages.slice(-5).map((message, index) => (
                    <MessageAnalysis key={message.id} message={message} index={index} />
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* MCP Usage Details */}
          {totalMcpUsage > 0 && (
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm flex items-center space-x-2 text-white">
                  <Zap className="w-4 h-4 text-purple-400" />
                  <span>Uso de MCPs</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {assistantMessages
                    .filter(msg => msg.mcpUsed && msg.mcpUsed.length > 0)
                    .slice(-3)
                    .map((message, index) => (
                      <div key={message.id} className="flex items-center space-x-2 text-sm">
                        <Bot className="w-3 h-3 text-purple-400" />
                        <span className="text-gray-400">Mensaje {index + 1}:</span>
                        <div className="flex flex-wrap gap-1">
                          {message.mcpUsed?.map((mcp, mcpIndex) => (
                            <Badge 
                              key={mcpIndex} 
                              variant="outline" 
                              className="text-xs bg-purple-900/30 text-purple-300 border-purple-700"
                            >
                              {mcp}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Performance Metrics */}
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center space-x-2 text-white">
                <Cpu className="w-4 h-4 text-orange-400" />
                <span>Métricas de Rendimiento</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">Promedio tokens/mensaje</span>
                <Badge variant="secondary" className="bg-gray-700 text-white border-gray-600">
                  {messages.length > 0 ? Math.round(totalTokens / messages.length) : 0}
                </Badge>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">Eficiencia MCP</span>
                <Badge variant="secondary" className="bg-green-900/50 text-green-300 border-green-700">
                  {messages.length > 0 ? Math.round((totalMcpUsage / messages.length) * 100) : 0}%
                </Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      </ScrollArea>
    </div>
  )
}

interface MessageAnalysisProps {
  message: Message
  index: number
}

function MessageAnalysis({ message, index }: MessageAnalysisProps) {
  const isUser = message.role === 'user'
  const hasTokens = message.usage && (message.usage.inputTokens || message.usage.outputTokens)
  const hasMcp = message.mcpUsed && message.mcpUsed.length > 0

  return (
    <div className="flex items-start space-x-3 p-3 bg-gray-750 rounded-lg border border-gray-600">
      <div className="flex-shrink-0">
        {isUser ? (
          <User className="w-4 h-4 text-blue-400" />
        ) : (
          <Bot className="w-4 h-4 text-green-400" />
        )}
      </div>
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center space-x-2 mb-1">
          <span className="text-xs font-medium text-white">
            {isUser ? 'Usuario' : 'Asistente'}
          </span>
          <Badge variant="outline" className="text-xs bg-gray-700 text-gray-300 border-gray-600">
            #{index + 1}
          </Badge>
        </div>
        
        <div className="text-xs text-gray-400 truncate mb-2">
          {message.content.substring(0, 100)}...
        </div>
        
        <div className="flex items-center space-x-3 text-xs">
          {hasTokens && (
            <div className="flex items-center space-x-1">
              <Clock className="w-3 h-3 text-blue-400" />
              <span className="text-gray-400">
                {((message.usage?.inputTokens || 0) + (message.usage?.outputTokens || 0)).toLocaleString()} tokens
              </span>
            </div>
          )}
          
          {hasMcp && (
            <div className="flex items-center space-x-1">
              <Network className="w-3 h-3 text-purple-400" />
              <span className="text-gray-400">
                {message.mcpUsed?.length} MCPs
              </span>
            </div>
          )}
          
          <div className="flex items-center space-x-1">
            {hasMcp || hasTokens ? (
              <CheckCircle className="w-3 h-3 text-green-400" />
            ) : (
              <AlertCircle className="w-3 h-3 text-yellow-400" />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
