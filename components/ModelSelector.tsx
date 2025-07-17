'use client'

import React from 'react'
import { AVAILABLE_MODELS, Model } from '@/lib/types'
import { cn } from '@/lib/utils'

interface ModelSelectorProps {
  selectedModel: string
  onModelChange: (modelId: string) => void
  disabled?: boolean
  compact?: boolean
  className?: string
}

export default function ModelSelector({ 
  selectedModel, 
  onModelChange, 
  disabled = false, 
  compact = false,
  className 
}: ModelSelectorProps) {
  const currentModel = AVAILABLE_MODELS.find(m => m.id === selectedModel) || AVAILABLE_MODELS[0]

  if (compact) {
    return (
      <div className={cn("flex items-center space-x-3", className)}>
        <span className="text-sm font-medium text-gray-700">Modelo:</span>
        <select
          value={selectedModel}
          onChange={(e) => onModelChange(e.target.value)}
          disabled={disabled}
          className="text-sm border border-gray-300 rounded-md px-3 py-1.5 bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {AVAILABLE_MODELS.map((model) => (
            <option key={model.id} value={model.id}>
              {model.icon || '🤖'} {model.name}
            </option>
          ))}
        </select>
        <div className="text-xs text-gray-500">
          ${currentModel.costPer1kTokens || 0}/1k tokens
        </div>
      </div>
    )
  }

  return (
    <div className={cn("space-y-4", className)}>
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Seleccionar Modelo IA</h3>
        <div className="text-sm text-gray-500">
          Actual: <span className="font-medium">{currentModel.name}</span>
        </div>
      </div>
      
      <div className="grid gap-3">
        {AVAILABLE_MODELS.map((model) => (
          <ModelCard
            key={model.id}
            model={model}
            isSelected={selectedModel === model.id}
            onSelect={() => onModelChange(model.id)}
            disabled={disabled}
          />
        ))}
      </div>
      
      <div className="text-xs text-gray-500 bg-gray-50 p-3 rounded-lg">
        <p className="font-medium mb-1">💡 Recomendaciones:</p>
        <ul className="space-y-1">
          <li>• <strong>Nova Pro</strong>: Ideal para conversaciones complejas y análisis detallado</li>
          <li>• <strong>Claude Haiku</strong>: Perfecto para respuestas rápidas y técnicas</li>
          <li>• <strong>Claude 3.5 Sonnet</strong>: El más avanzado con razonamiento superior</li>
        </ul>
      </div>
    </div>
  )
}

interface ModelCardProps {
  model: Model
  isSelected: boolean
  onSelect: () => void
  disabled: boolean
}

function ModelCard({ model, isSelected, onSelect, disabled }: ModelCardProps) {
  return (
    <div
      onClick={disabled ? undefined : onSelect}
      className={cn(
        "relative p-4 border rounded-lg cursor-pointer transition-all duration-200",
        isSelected 
          ? "border-blue-500 bg-blue-50 ring-2 ring-blue-200" 
          : "border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50",
        disabled && "opacity-50 cursor-not-allowed"
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-3">
          <div className="text-2xl">{model.icon || '🤖'}</div>
          <div>
            <h4 className="font-semibold">{model.name}</h4>
            <p className="text-sm text-gray-600 mt-1">{model.description}</p>
            <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
              <span>Proveedor: {model.provider}</span>
              <span>Max tokens: {model.maxTokens.toLocaleString()}</span>
              <span className="font-medium">${model.costPer1kTokens || 0}/1k tokens</span>
            </div>
          </div>
        </div>
        
        {isSelected && (
          <div className="absolute top-2 right-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full flex items-center justify-center">
              <div className="w-1.5 h-1.5 bg-white rounded-full"></div>
            </div>
          </div>
        )}
      </div>
      
      <div className="mt-3 flex flex-wrap gap-1">
        {model.capabilities.map((capability: string) => (
          <span
            key={capability}
            className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-full"
          >
            {capability}
          </span>
        ))}
      </div>
    </div>
  )
}
