'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Brain, Zap, Eye, Sparkles, DollarSign, Clock } from 'lucide-react'

interface BedrockModel {
  id: string
  name: string
  provider: string
  description: string
  capabilities: string[]
  pricing: {
    input: string
    output: string
  }
  speed: 'fast' | 'medium' | 'slow'
  quality: 'high' | 'medium' | 'standard'
  icon: React.ReactNode
  recommended?: boolean
}

const BEDROCK_MODELS: BedrockModel[] = [
  {
    id: 'anthropic.claude-3-5-sonnet-20241022-v2:0',
    name: 'Claude 3.5 Sonnet v2',
    provider: 'Anthropic',
    description: 'Modelo más avanzado para análisis profundo, razonamiento complejo y generación de código',
    capabilities: ['Análisis técnico', 'Generación de código', 'Razonamiento complejo', 'Documentación'],
    pricing: {
      input: '$3.00/1M tokens',
      output: '$15.00/1M tokens'
    },
    speed: 'medium',
    quality: 'high',
    icon: <Brain className="h-5 w-5" />,
    recommended: true
  },
  {
    id: 'anthropic.claude-3-haiku-20240307-v1:0',
    name: 'Claude 3 Haiku',
    provider: 'Anthropic',
    description: 'Modelo rápido y económico para tareas simples y respuestas rápidas',
    capabilities: ['Respuestas rápidas', 'Análisis básico', 'Conversación', 'Resúmenes'],
    pricing: {
      input: '$0.25/1M tokens',
      output: '$1.25/1M tokens'
    },
    speed: 'fast',
    quality: 'medium',
    icon: <Zap className="h-5 w-5" />
  },
  {
    id: 'amazon.nova-pro-v1:0',
    name: 'Amazon Nova Pro',
    provider: 'Amazon',
    description: 'Modelo multimodal para análisis de texto, imágenes y generación de contenido visual',
    capabilities: ['Multimodal', 'Análisis de imágenes', 'Generación visual', 'Diagramas'],
    pricing: {
      input: '$0.80/1M tokens',
      output: '$3.20/1M tokens'
    },
    speed: 'medium',
    quality: 'high',
    icon: <Eye className="h-5 w-5" />
  },
  {
    id: 'amazon.nova-lite-v1:0',
    name: 'Amazon Nova Lite',
    provider: 'Amazon',
    description: 'Modelo ligero y rápido para tareas básicas con capacidades multimodales',
    capabilities: ['Multimodal básico', 'Análisis rápido', 'Conversación', 'Procesamiento simple'],
    pricing: {
      input: '$0.06/1M tokens',
      output: '$0.24/1M tokens'
    },
    speed: 'fast',
    quality: 'standard',
    icon: <Sparkles className="h-5 w-5" />
  }
]

interface ModelSelectorProps {
  selectedModel: string
  onModelChange: (modelId: string) => void
  showPricing?: boolean
}

export function ModelSelector({ selectedModel, onModelChange, showPricing = true }: ModelSelectorProps) {
  const [showDetails, setShowDetails] = useState(false)

  const getSpeedIcon = (speed: BedrockModel['speed']) => {
    switch (speed) {
      case 'fast':
        return <Zap className="h-4 w-4 text-green-500" />
      case 'medium':
        return <Clock className="h-4 w-4 text-yellow-500" />
      case 'slow':
        return <Clock className="h-4 w-4 text-red-500" />
    }
  }

  const getQualityColor = (quality: BedrockModel['quality']) => {
    switch (quality) {
      case 'high':
        return 'bg-green-100 text-green-800'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800'
      case 'standard':
        return 'bg-blue-100 text-blue-800'
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Seleccionar Modelo de IA</h3>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setShowDetails(!showDetails)}
        >
          {showDetails ? 'Ocultar Detalles' : 'Ver Detalles'}
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {BEDROCK_MODELS.map((model) => (
          <Card 
            key={model.id} 
            className={`cursor-pointer transition-all hover:shadow-md ${
              selectedModel === model.id 
                ? 'ring-2 ring-blue-500 bg-blue-50' 
                : 'hover:bg-gray-50'
            }`}
            onClick={() => onModelChange(model.id)}
          >
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {model.icon}
                  <CardTitle className="text-base">{model.name}</CardTitle>
                  {model.recommended && (
                    <Badge className="bg-blue-100 text-blue-800">Recomendado</Badge>
                  )}
                </div>
                <div className="flex items-center space-x-1">
                  {getSpeedIcon(model.speed)}
                  <Badge className={getQualityColor(model.quality)}>
                    {model.quality === 'high' ? 'Alta' : 
                     model.quality === 'medium' ? 'Media' : 'Estándar'}
                  </Badge>
                </div>
              </div>
              <CardDescription className="text-sm">
                {model.description}
              </CardDescription>
            </CardHeader>

            {showDetails && (
              <CardContent className="pt-0">
                <div className="space-y-3">
                  <div>
                    <h4 className="text-sm font-medium mb-2">Capacidades:</h4>
                    <div className="flex flex-wrap gap-1">
                      {model.capabilities.map((capability) => (
                        <Badge key={capability} variant="secondary" className="text-xs">
                          {capability}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {showPricing && (
                    <div>
                      <h4 className="text-sm font-medium mb-2 flex items-center">
                        <DollarSign className="h-4 w-4 mr-1" />
                        Precios:
                      </h4>
                      <div className="text-xs text-gray-600 space-y-1">
                        <div>Input: {model.pricing.input}</div>
                        <div>Output: {model.pricing.output}</div>
                      </div>
                    </div>
                  )}

                  <div className="text-xs text-gray-500">
                    Proveedor: {model.provider}
                  </div>
                </div>
              </CardContent>
            )}
          </Card>
        ))}
      </div>

      {/* Quick Selection Buttons */}
      <div className="flex flex-wrap gap-2 pt-4 border-t">
        <span className="text-sm text-gray-600 mr-2">Acceso rápido:</span>
        {BEDROCK_MODELS.map((model) => (
          <Button
            key={model.id}
            variant={selectedModel === model.id ? "default" : "outline"}
            size="sm"
            onClick={() => onModelChange(model.id)}
            className="text-xs"
          >
            {model.name.split(' ')[0]} {model.name.split(' ')[1]}
          </Button>
        ))}
      </div>

      {/* Model Information */}
      {selectedModel && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Brain className="h-4 w-4 text-blue-600" />
            <span className="text-sm font-medium text-blue-900">
              Modelo Seleccionado: {BEDROCK_MODELS.find(m => m.id === selectedModel)?.name}
            </span>
          </div>
          <p className="text-sm text-blue-800">
            {BEDROCK_MODELS.find(m => m.id === selectedModel)?.description}
          </p>
        </div>
      )}
    </div>
  )
}
