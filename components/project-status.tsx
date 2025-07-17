'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { CheckCircle, Clock, AlertCircle } from 'lucide-react'

interface ProjectStatusProps {
  projectName: string
  documentsGenerated: number
  totalDocuments: number
  pendingTasks: string[]
  completedTasks: string[]
  currentPhase: 'planning' | 'architecture' | 'documentation' | 'costing' | 'completed'
}

export function ProjectStatus({
  projectName,
  documentsGenerated,
  totalDocuments,
  pendingTasks,
  completedTasks,
  currentPhase
}: ProjectStatusProps) {
  const progress = Math.round((documentsGenerated / totalDocuments) * 100)
  
  const getPhaseLabel = (phase: string) => {
    switch (phase) {
      case 'planning': return 'Planificación'
      case 'architecture': return 'Arquitectura'
      case 'documentation': return 'Documentación'
      case 'costing': return 'Costos'
      case 'completed': return 'Completado'
      default: return phase
    }
  }
  
  const getPhaseColor = (phase: string) => {
    switch (phase) {
      case 'planning': return 'text-blue-600'
      case 'architecture': return 'text-purple-600'
      case 'documentation': return 'text-green-600'
      case 'costing': return 'text-orange-600'
      case 'completed': return 'text-emerald-600'
      default: return 'text-gray-600'
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Estado del Proyecto: {projectName}</span>
          <span className={`text-sm font-medium ${getPhaseColor(currentPhase)}`}>
            Fase: {getPhaseLabel(currentPhase)}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Progreso de documentos */}
        <div>
          <div className="flex items-center justify-between mb-1 text-sm">
            <span>Documentos generados</span>
            <span className="font-medium">{documentsGenerated} de {totalDocuments}</span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>
        
        {/* Tareas */}
        <div className="grid grid-cols-2 gap-4">
          {/* Tareas completadas */}
          <div>
            <h4 className="text-sm font-medium text-gray-600 mb-2 flex items-center">
              <CheckCircle className="h-4 w-4 mr-1 text-green-600" />
              Completadas
            </h4>
            <ul className="space-y-1">
              {completedTasks.map((task, index) => (
                <li key={index} className="text-xs flex items-center text-green-700">
                  <span className="mr-1">✓</span>
                  {task}
                </li>
              ))}
              {completedTasks.length === 0 && (
                <li className="text-xs text-gray-500 italic">No hay tareas completadas</li>
              )}
            </ul>
          </div>
          
          {/* Tareas pendientes */}
          <div>
            <h4 className="text-sm font-medium text-gray-600 mb-2 flex items-center">
              <Clock className="h-4 w-4 mr-1 text-yellow-600" />
              Pendientes
            </h4>
            <ul className="space-y-1">
              {pendingTasks.map((task, index) => (
                <li key={index} className="text-xs flex items-center text-yellow-700">
                  <span className="mr-1">○</span>
                  {task}
                </li>
              ))}
              {pendingTasks.length === 0 && (
                <li className="text-xs text-gray-500 italic">No hay tareas pendientes</li>
              )}
            </ul>
          </div>
        </div>
        
        {/* Estado general */}
        <div className={`text-xs p-2 rounded ${
          currentPhase === 'completed' 
            ? 'bg-green-50 text-green-700' 
            : 'bg-blue-50 text-blue-700'
        }`}>
          {currentPhase === 'completed' ? (
            <div className="flex items-center">
              <CheckCircle className="h-3 w-3 mr-1" />
              <span>Proyecto completado. Todos los documentos están disponibles.</span>
            </div>
          ) : (
            <div className="flex items-center">
              <AlertCircle className="h-3 w-3 mr-1" />
              <span>Proyecto en progreso. Fase actual: {getPhaseLabel(currentPhase)}.</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
