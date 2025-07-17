// Función para mostrar notificaciones MCP de forma estandarizada
export function showMCPNotification(service: string, action: string): string {
  return `✅ *Voy a usar el MCP \`${service}\` para ${action}...*`;
}

// Función mejorada para detectar servicios MCP necesarios
export function detectMCPServices(userInput: string, conversationContext: string[] = []): string[] {
  const input = userInput.toLowerCase();
  const context = conversationContext.join(' ').toLowerCase();
  const combinedText = `${input} ${context}`;

  const neededServices: string[] = [];
  
  // Patrones mejorados para detección de servicios
  const patterns = {
    'diagram-mcp': ['diagrama', 'arquitectura', 'visual', 'dibujo', 'esquema'],
    'awsdocs-mcp': ['documentación', 'docs', 'guía', 'manual', 'referencia'],
    'pricing-mcp': ['costo', 'precio', 'presupuesto', 'calculadora', 'estimación'],
    'cfn-mcp': ['cloudformation', 'template', 'infraestructura', 'iac', 'despliegue'],
    'customdoc-mcp': ['documento', 'word', 'propuesta', 'informe', 'entregable'],
    'core-mcp': ['análisis', 'entender', 'procesar', 'evaluar']
  };
  
  // Detectar servicios basados en patrones
  Object.entries(patterns).forEach(([service, keywords]) => {
    if (keywords.some(keyword => combinedText.includes(keyword))) {
      neededServices.push(service);
    }
  });
  
  // Detección inteligente basada en contexto
  if (combinedText.includes('generar') || combinedText.includes('crear')) {
    if (combinedText.includes('diagrama') || combinedText.includes('arquitectura')) {
      if (!neededServices.includes('diagram-mcp')) neededServices.push('diagram-mcp');
    }
    if (combinedText.includes('documento') || combinedText.includes('propuesta')) {
      if (!neededServices.includes('customdoc-mcp')) neededServices.push('customdoc-mcp');
    }
    if (combinedText.includes('cloudformation') || combinedText.includes('template')) {
      if (!neededServices.includes('cfn-mcp')) neededServices.push('cfn-mcp');
    }
  }
  
  // Siempre incluir core-mcp para análisis básico si no hay otros servicios
  if (neededServices.length === 0) {
    neededServices.push('core-mcp');
  }
  
  return neededServices;
}

// Función para validar información del proyecto
export function validateProjectInfo(projectInfo: any): { valid: boolean; message: string } {
  if (!projectInfo?.name) {
    return { valid: false, message: "Por favor, define un nombre para el proyecto antes de continuar." };
  }
  if (!projectInfo?.type) {
    return { valid: false, message: "Por favor, define el tipo de solución para el proyecto antes de continuar." };
  }
  return { valid: true, message: "Información del proyecto validada correctamente." };
}

// Función para actualizar estado en DynamoDB
export async function updateProjectStatus(projectId: string, status: string = 'completed'): Promise<boolean> {
  try {
    // En una implementación real, esto haría una llamada a la API para actualizar DynamoDB
    // Por ahora, simulamos una respuesta exitosa
    console.log(`Actualizando estado del proyecto ${projectId} a ${status}`);
    
    // Simular retraso de red
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    return true;
  } catch (error) {
    console.error('Error updating project status:', error);
    return false;
  }
}

// Función para obtener documentos de un proyecto desde S3
export async function getProjectDocuments(projectName: string, s3Folder: string): Promise<any[]> {
  try {
    // En una implementación real, esto haría una llamada a la API para obtener los documentos de S3
    // Por ahora, simulamos una respuesta con documentos ficticios
    console.log(`Obteniendo documentos del proyecto ${projectName} desde ${s3Folder}`);
    
    // Simular retraso de red
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    return [
      {
        name: `${projectName}-arquitectura.docx`,
        path: `${s3Folder}/${projectName}-arquitectura.docx`,
        type: 'text',
        size: 245000,
        lastModified: new Date().toISOString()
      },
      {
        name: `${projectName}-costos.xlsx`,
        path: `${s3Folder}/${projectName}-costos.xlsx`,
        type: 'spreadsheet',
        size: 125000,
        lastModified: new Date().toISOString()
      },
      {
        name: `${projectName}-cloudformation.yaml`,
        path: `${s3Folder}/${projectName}-cloudformation.yaml`,
        type: 'code',
        size: 35000,
        lastModified: new Date().toISOString()
      },
      {
        name: `${projectName}-diagrama.svg`,
        path: `${s3Folder}/${projectName}-diagrama.svg`,
        type: 'image',
        size: 85000,
        lastModified: new Date().toISOString()
      }
    ];
  } catch (error) {
    console.error('Error getting project documents:', error);
    return [];
  }
}

// Función para extraer el nombre del proyecto de la entrada del usuario
export function extractProjectNameFromInput(input: string): string | null {
  // Patrones para detectar nombres de proyecto
  const patterns = [
    /proyecto\s+([a-zA-Z0-9áéíóúñü\s_-]+)/i,
    /llamado\s+([a-zA-Z0-9áéíóúñü\s_-]+)/i,
    /nombre\s+([a-zA-Z0-9áéíóúñü\s_-]+)/i,
    /"([^"]+)"/g
  ]
  
  for (const pattern of patterns) {
    const match = input.match(pattern)
    if (match && match[1]) {
      return match[1].trim()
    }
  }
  
  // Buscar palabras capitalizadas que podrían ser nombres de proyecto
  const words = input.split(' ')
  for (const word of words) {
    if (word.length > 3 && /^[A-Z]/.test(word) && !/^(Proyecto|Sistema|Aplicacion|Plataforma)$/i.test(word)) {
      return word
    }
  }
  
  return null
}

// Función para determinar la fase del proyecto basada en el contexto
export function determineProjectPhase(messages: any[]): 'planning' | 'architecture' | 'documentation' | 'costing' | 'completed' {
  // Buscar palabras clave en los mensajes para determinar la fase
  const combinedText = messages.map(m => m.content).join(' ').toLowerCase();
  
  if (combinedText.includes('completado') || combinedText.includes('finalizado')) {
    return 'completed';
  }
  
  if (combinedText.includes('costo') || combinedText.includes('precio') || combinedText.includes('presupuesto')) {
    return 'costing';
  }
  
  if (combinedText.includes('documento') || combinedText.includes('word') || combinedText.includes('excel')) {
    return 'documentation';
  }
  
  if (combinedText.includes('arquitectura') || combinedText.includes('diagrama') || combinedText.includes('diseño')) {
    return 'architecture';
  }
  
  return 'planning';
}
