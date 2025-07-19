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
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-border">
        <h3 className="text-lg font-semibold text-foreground flex items-center space-x-2">
          <Brain className="w-5 h-5 text-primary" />
          <span>Análisis de Conversación</span>
        </h3>
        <p className="text-sm text-muted-foreground mt-1">
          Entendimiento del prompt y uso de recursos
        </p>
      </div>

      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {/* Summary Stats */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center space-x-2">
                <Target className="w-4 h-4" />
                <span>Resumen de Sesión</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Mensajes totales</span>
                <Badge variant="secondary">{messages.length}</Badge>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">MCPs ejecutados</span>
                <Badge variant="secondary" className="bg-purple-500/10 text-purple-500">
                  {totalMcpUsage}
                </Badge>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Tokens procesados</span>
                <Badge variant="secondary" className="bg-blue-500/10 text-blue-500">
                  {totalTokens.toLocaleString()}
                </Badge>
              </div>
            </CardContent>
          </Card>

          {/* Message Analysis */}
          {messages.length > 0 && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm flex items-center space-x-2">
                  <FileText className="w-4 h-4" />
                  <span>Análisis por Mensaje</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {messages.slice(-5).map((message, index) => (
                    <MessageAnalysis key={message.id} message={message} index={index} />
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* MCP Usage Details */}
          {totalMcpUsage > 0 && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm flex items-center space-x-2">
                  <Zap className="w-4 h-4" />
                  <span>Uso de MCPs</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {assistantMessages
                    .filter(msg => msg.mcpUsed && msg.mcpUsed.length > 0)
                    .map((message, index) => (
                      <div key={message.id} className="p-2 bg-muted/30 rounded-lg">
                        <div className="text-xs text-muted-foreground mb-1">
                          Mensaje #{messages.indexOf(message) + 1}
                        </div>
                        <div className="flex flex-wrap gap-1">
                          {message.mcpUsed?.map((mcp, mcpIndex) => (
                            <Badge 
                              key={mcpIndex} 
                              variant="outline" 
                              className="text-xs bg-purple-500/10 text-purple-500"
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

          {/* System Status */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center space-x-2">
                <Network className="w-4 h-4" />
                <span>Estado del Sistema</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-3 h-3 text-green-500" />
                  <span className="text-muted-foreground">Bedrock Runtime</span>
                </div>
                <Badge variant="secondary" className="bg-green-500/10 text-green-500">
                  Online
                </Badge>
              </div>
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-3 h-3 text-green-500" />
                  <span className="text-muted-foreground">MCPs Disponibles</span>
                </div>
                <Badge variant="secondary" className="bg-green-500/10 text-green-500">
                  6/6
                </Badge>
              </div>
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-2">
                  <Clock className="w-3 h-3 text-blue-500" />
                  <span className="text-muted-foreground">Latencia promedio</span>
                </div>
                <Badge variant="secondary" className="bg-blue-500/10 text-blue-500">
                  ~2.1s
                </Badge>
              </div>
            </CardContent>
          </Card>

          {/* Tips */}
          <Card className="bg-blue-500/5 border-blue-500/20">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center space-x-2 text-blue-900 dark:text-blue-100">
                <Cpu className="w-4 h-4" />
                <span>Consejos de Optimización</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="text-xs text-blue-700 dark:text-blue-300 space-y-1">
                <li>• Sé específico en tus preguntas para mejores resultados</li>
                <li>• Los MCPs se activan automáticamente según el contexto</li>
                <li>• Usa el historial para mantener contexto en la conversación</li>
              </ul>
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
  
  return (
    <div className="p-3 bg-muted/20 rounded-lg border border-border/50">
      <div className="flex items-center space-x-2 mb-2">
        {isUser ? (
          <User className="w-3 h-3 text-blue-500" />
        ) : (
          <Bot className="w-3 h-3 text-purple-500" />
        )}
        <span className="text-xs font-medium">
          {isUser ? 'Usuario' : 'Asistente'} #{index + 1}
        </span>
        {message.timestamp && (
          <span className="text-xs text-muted-foreground">
            {new Date(message.timestamp).toLocaleTimeString()}
          </span>
        )}
      </div>
      
      <div className="text-xs text-muted-foreground mb-2 line-clamp-2">
        {message.content.substring(0, 100)}
        {message.content.length > 100 && '...'}
      </div>
      
      <div className="flex flex-wrap gap-1">
        {message.usage && (
          <Badge variant="outline" className="text-xs">
            {(message.usage?.inputTokens || 0) + (message.usage?.outputTokens || 0)} tokens
          </Badge>
        )}
        {message.mcpUsed && message.mcpUsed.length > 0 && (
          <Badge variant="outline" className="text-xs bg-purple-500/10 text-purple-500">
            {message.mcpUsed.length} MCP
          </Badge>
        )}
        {!isUser && !message.mcpUsed?.length && (
          <Badge variant="outline" className="text-xs bg-green-500/10 text-green-500">
            Modelo base
          </Badge>
        )}
      </div>
    </div>
  )
}
