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

export function ModelSelector({ 
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
        <span className="text-sm font-medium text-gray-300">Modelo:</span>
        <select
          value={selectedModel}
          onChange={(e) => onModelChange(e.target.value)}
          disabled={disabled}
          className="text-sm border border-gray-600 rounded-md px-3 py-1.5 bg-gray-800 text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {AVAILABLE_MODELS.map((model) => (
            <option key={model.id} value={model.id} className="bg-gray-800 text-white">
              {model.icon || '🤖'} {model.name}
            </option>
          ))}
        </select>
        <div className="text-xs text-gray-400">
          ${currentModel.costPer1kTokens || 0}/1k tokens
        </div>
      </div>
    )
  }

  return (
    <div className={cn("space-y-4", className)}>
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">Seleccionar Modelo IA</h3>
        <div className="text-sm text-gray-400">
          Actual: <span className="font-medium text-white">{currentModel.name}</span>
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
      
      <div className="text-xs text-gray-400 bg-gray-800 p-3 rounded-lg border border-gray-700">
        <p className="font-medium mb-1 text-white">💡 Recomendaciones para AWS:</p>
        <ul className="space-y-1">
          <li>• <strong className="text-white">Nova Pro</strong>: Ideal para arquitecturas AWS complejas</li>
          <li>• <strong className="text-white">Meta Llama 3.2</strong>: Excelente para análisis de infraestructura</li>
          <li>• <strong className="text-white">Claude 3.5 Sonnet v2</strong>: El más avanzado para proyectos enterprise</li>
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
          ? "border-blue-500 bg-blue-900/20 ring-2 ring-blue-400/50" 
          : "border-gray-700 bg-gray-800 hover:border-gray-600 hover:bg-gray-750",
        disabled && "opacity-50 cursor-not-allowed"
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-3">
          <div className="text-2xl">{model.icon || '🤖'}</div>
          <div>
            <h4 className="font-semibold text-white">{model.name}</h4>
            <p className="text-sm text-gray-300 mt-1">{model.description}</p>
            <div className="flex items-center space-x-4 mt-2 text-xs text-gray-400">
              <span>Proveedor: <span className="text-gray-300">{model.provider}</span></span>
              <span>Max tokens: <span className="text-gray-300">{model.maxTokens.toLocaleString()}</span></span>
              <span className="font-medium text-green-400">${model.costPer1kTokens || 0}/1k tokens</span>
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
            className="px-2 py-1 text-xs bg-gray-700 text-gray-300 rounded-full border border-gray-600"
          >
            {capability}
          </span>
        ))}
      </div>
    </div>
  )
}
