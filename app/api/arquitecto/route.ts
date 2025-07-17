import { NextRequest, NextResponse } from 'next/server'
import { awslabscore_mcp_server___prompt_understanding } from '@/lib/mcpIntegration'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { message, conversationHistory, selectedModel, projectData } = body

    // Usar MCP Core para entender el prompt
    const promptAnalysis = await awslabscore_mcp_server___prompt_understanding()
    
    // Simular respuesta del arquitecto usando MCP
    const response = {
      response: `Como Arquitecto AWS, he analizado tu consulta: "${message}".

Basándome en mi análisis usando servicios MCP, te recomiendo:

1. **Arquitectura Serverless**: Utilizar AWS Lambda para el procesamiento
2. **Base de datos**: DynamoDB para almacenamiento NoSQL escalable  
3. **API**: API Gateway para exponer servicios REST
4. **Frontend**: Amplify para hosting y CI/CD
5. **Seguridad**: Cognito para autenticación

¿Te gustaría que profundice en algún aspecto específico de esta arquitectura?`,
      selectedModel: selectedModel || 'amazon.nova-pro-v1:0',
      mcpServicesUsed: ['core'],
      transparency: {
        message: 'Usando MCP Core para análisis de arquitectura',
        services: ['core']
      },
      promptUnderstanding: promptAnalysis,
      projectInfo: projectData || null,
      documentsGenerated: false,
      s3Folder: null,
      usage: {
        inputTokens: message?.length || 0,
        outputTokens: 150,
        totalTokens: (message?.length || 0) + 150
      }
    }

    return NextResponse.json(response)
  } catch (error) {
    console.error('Error in arquitecto API:', error)
    return NextResponse.json(
      { error: 'Error interno del servidor' },
      { status: 500 }
    )
  }
}
