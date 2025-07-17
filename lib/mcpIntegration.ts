// MCP Integration utilities for AWS Propuestas v3

import { MCP_SERVICES } from './types'

/**
 * Función simulada para MCP Core prompt understanding
 */
export async function awslabscore_mcp_server___prompt_understanding() {
  return {
    analysis: 'Prompt analizado usando MCP Core',
    services_recommended: ['core', 'diagram', 'pricing'],
    confidence: 0.95
  }
}

/**
 * Detecta qué servicios MCP podrían ser necesarios basado en el texto del usuario
 * @param currentInput Texto actual del usuario
 * @param previousMessages Mensajes anteriores en la conversación
 * @returns Array de nombres de servicios MCP
 */
export function detectMCPServices(currentInput: string, previousMessages: string[]): string[] {
  const detectedServices: string[] = []
  const input = currentInput.toLowerCase()
  const context = previousMessages.join(' ').toLowerCase()
  
  // Detectar servicios basados en palabras clave
  if (input.includes('diagrama') || input.includes('arquitectura') || input.includes('diseño')) {
    detectedServices.push('diagram')
  }
  
  if (input.includes('documento') || input.includes('documentación') || input.includes('pdf')) {
    detectedServices.push('docgen')
  }
  
  if (input.includes('precio') || input.includes('costo') || input.includes('presupuesto')) {
    detectedServices.push('pricing')
  }
  
  if (input.includes('cloudformation') || input.includes('template') || input.includes('plantilla')) {
    detectedServices.push('cfn')
  }
  
  if (input.includes('documentación aws') || input.includes('manual') || input.includes('guía')) {
    detectedServices.push('awsdocs')
  }
  
  // Siempre incluir el servicio core
  if (!detectedServices.includes('core')) {
    detectedServices.push('core')
  }
  
  return detectedServices
}

/**
 * Valida la información del proyecto
 * @param projectInfo Información del proyecto
 * @returns Objeto con resultado de validación
 */
export function validateProjectInfo(projectInfo: any): { valid: boolean; errors: string[] } {
  const errors: string[] = []
  
  if (!projectInfo.name) {
    errors.push('El nombre del proyecto es obligatorio')
  }
  
  if (projectInfo.name && projectInfo.name.length < 3) {
    errors.push('El nombre del proyecto debe tener al menos 3 caracteres')
  }
  
  if (projectInfo.type && !['basic', 'standard', 'premium'].includes(projectInfo.type)) {
    errors.push('El tipo de proyecto debe ser basic, standard o premium')
  }
  
  return {
    valid: errors.length === 0,
    errors
  }
}

/**
 * Actualiza el estado de un proyecto en DynamoDB
 * @param projectId ID del proyecto
 * @param status Nuevo estado
 * @returns Promise<boolean> Éxito de la operación
 */
export async function updateProjectStatus(projectId: string, status: 'in_progress' | 'completed'): Promise<boolean> {
  try {
    // En una implementación real, esto haría una llamada a la API para actualizar el estado
    // Por ahora, simulamos una operación exitosa
    console.log(`Actualizando estado del proyecto ${projectId} a ${status}`)
    
    // Simular retraso de red
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    return true
  } catch (error) {
    console.error('Error al actualizar estado del proyecto:', error)
    return false
  }
}

/**
 * Obtiene los servicios MCP disponibles
 * @returns Array de servicios MCP
 */
export function getAvailableMCPServices(): typeof MCP_SERVICES {
  return MCP_SERVICES
}

/**
 * Verifica el estado de los servicios MCP
 * @returns Promise con el estado de los servicios
 */
export async function checkMCPServicesStatus(): Promise<{ [key: string]: boolean }> {
  try {
    // En una implementación real, esto haría una llamada a la API para verificar el estado
    // Por ahora, simulamos que todos los servicios están activos
    const status: { [key: string]: boolean } = {}
    
    MCP_SERVICES.forEach(service => {
      status[service.name] = service.status === 'active'
    })
    
    return status
  } catch (error) {
    console.error('Error al verificar estado de servicios MCP:', error)
    return {}
  }
}
