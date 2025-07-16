'use client'

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
  const getPhaseColor = (phase: string) => {
    switch (phase) {
      case 'planning': return 'bg-blue-100 text-blue-800'
      case 'architecture': return 'bg-purple-100 text-purple-800'
      case 'documentation': return 'bg-yellow-100 text-yellow-800'
      case 'costing': return 'bg-orange-100 text-orange-800'
      case 'completed': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getPhaseLabel = (phase: string) => {
    switch (phase) {
      case 'planning': return '📋 Planificación'
      case 'architecture': return '🏗️ Arquitectura'
      case 'documentation': return '📄 Documentación'
      case 'costing': return '💰 Costeo'
      case 'completed': return '✅ Completado'
      default: return '🔄 En progreso'
    }
  }

  const progressPercentage = totalDocuments > 0 ? (documentsGenerated / totalDocuments) * 100 : 0

  return (
    <div className="bg-white border rounded-lg p-4 mb-4 shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-gray-900">📊 Estado del Proyecto</h3>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPhaseColor(currentPhase)}`}>
          {getPhaseLabel(currentPhase)}
        </span>
      </div>

      <div className="mb-3">
        <div className="flex justify-between text-sm text-gray-600 mb-1">
          <span>Proyecto: <strong>{projectName}</strong></span>
          <span>Documentos: {documentsGenerated}/{totalDocuments}</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progressPercentage}%` }}
          ></div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {/* Tareas Completadas */}
        <div>
          <h4 className="text-sm font-medium text-green-700 mb-2">✅ Completadas</h4>
          <ul className="space-y-1">
            {completedTasks.map((task, index) => (
              <li key={index} className="text-xs text-green-600 flex items-center">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                {task}
              </li>
            ))}
          </ul>
        </div>

        {/* Tareas Pendientes */}
        <div>
          <h4 className="text-sm font-medium text-orange-700 mb-2">⏳ Pendientes</h4>
          <ul className="space-y-1">
            {pendingTasks.map((task, index) => (
              <li key={index} className="text-xs text-orange-600 flex items-center">
                <span className="w-2 h-2 bg-orange-500 rounded-full mr-2"></span>
                {task}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}
