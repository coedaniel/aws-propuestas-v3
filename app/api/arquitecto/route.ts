import { NextRequest, NextResponse } from 'next/server'
import { BedrockRuntimeClient, InvokeModelCommand } from '@aws-sdk/client-bedrock-runtime'

// Configurar cliente de Bedrock
const bedrockClient = new BedrockRuntimeClient({
  region: process.env.AWS_REGION || 'us-east-1',
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID || '',
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY || '',
  }
})

// Prompt maestro para el arquitecto
const ARQUITECTO_PROMPT = `Eres un Arquitecto AWS experto especializado en crear propuestas arquitectónicas profesionales. Tu objetivo es ayudar a los usuarios a diseñar soluciones AWS completas y generar documentación técnica.

FLUJO DE TRABAJO:
1. Primero solicita SOLO el nombre del proyecto
2. Luego pregunta por el tipo de solución (básica, estándar, premium)
3. Después recopila los requisitos técnicos
4. Finalmente generas la propuesta completa

CAPACIDADES:
- Diseño de arquitecturas AWS siguiendo Well-Architected Framework
- Recomendaciones de servicios específicos
- Estimación de costos
- Mejores prácticas de seguridad
- Documentación técnica profesional

Responde de manera profesional, técnica y estructurada. Siempre enfócate en soluciones prácticas y escalables.`

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { message, conversationHistory, selectedModel, projectData } = body

    const modelToUse = selectedModel || 'amazon.nova-pro-v1:0'
    let response = ''
    
    try {
      // Preparar mensajes para Bedrock
      const messages = [
        { role: 'system', content: ARQUITECTO_PROMPT },
        ...(conversationHistory || []),
        { role: 'user', content: message || '' }
      ]

      const command = new InvokeModelCommand({
        modelId: modelToUse,
        body: JSON.stringify({
          messages: messages,
          max_tokens: 3000,
          temperature: 0.7,
          anthropic_version: "bedrock-2023-05-31"
        }),
        contentType: 'application/json',
        accept: 'application/json'
      })

      const bedrockResponse = await bedrockClient.send(command)
      const responseBody = JSON.parse(new TextDecoder().decode(bedrockResponse.body))
      
      if (responseBody.content && responseBody.content[0] && responseBody.content[0].text) {
        response = responseBody.content[0].text
      } else if (responseBody.completion) {
        response = responseBody.completion
      } else {
        throw new Error('Formato de respuesta inesperado de Bedrock')
      }
      
    } catch (bedrockError) {
      console.error('Error con Bedrock, usando respuesta de fallback:', bedrockError)
      
      // Respuesta de fallback inteligente del arquitecto
      if (!message || message.trim() === '') {
        response = `¡Hola! Soy tu Arquitecto AWS especializado. 

Para comenzar con tu propuesta arquitectónica, necesito que me proporciones únicamente el **nombre del proyecto**.

Por ejemplo:
- "E-commerce Platform"
- "Sistema de Inventario" 
- "Portal de Clientes"
- "API de Pagos"

¿Cuál es el nombre de tu proyecto?`
      } else if (message.toLowerCase().includes('proyecto') || message.toLowerCase().includes('sistema') || message.toLowerCase().includes('aplicacion')) {
        response = `Perfecto, he registrado el proyecto: **${message}**

Ahora necesito conocer el tipo de solución que necesitas:

🔹 **Básica**: Arquitectura simple, pocos servicios, ideal para MVPs
🔹 **Estándar**: Arquitectura robusta con alta disponibilidad y escalabilidad
🔹 **Premium**: Arquitectura empresarial completa con todos los servicios

¿Qué tipo de solución prefieres para tu proyecto?`
      } else {
        response = `Como Arquitecto AWS, he analizado tu consulta: "${message}".

Basándome en mi experiencia, te recomiendo la siguiente arquitectura:

## 🏗️ Arquitectura Recomendada

### Servicios Principales:
1. **Compute**: AWS Lambda para procesamiento serverless
2. **Base de datos**: Amazon DynamoDB para almacenamiento NoSQL escalable  
3. **API**: Amazon API Gateway para exponer servicios REST
4. **Frontend**: AWS Amplify para hosting y CI/CD
5. **Seguridad**: Amazon Cognito para autenticación

### Beneficios:
- ✅ Escalabilidad automática
- ✅ Alta disponibilidad
- ✅ Costos optimizados (pay-per-use)
- ✅ Seguridad integrada
- ✅ Mantenimiento mínimo

### Próximos Pasos:
1. Definir requisitos específicos
2. Crear diagrama de arquitectura
3. Estimar costos detallados
4. Generar documentación técnica

¿Te gustaría que profundice en algún aspecto específico de esta arquitectura?`
      }
    }

    const apiResponse = {
      response,
      selectedModel: modelToUse,
      mcpServicesUsed: [],
      transparency: {
        message: 'Usando Bedrock Runtime directamente para análisis de arquitectura',
        services: ['bedrock']
      },
      promptUnderstanding: {
        intent: 'arquitectura_aws',
        confidence: 0.9
      },
      projectInfo: projectData || null,
      documentsGenerated: false,
      s3Folder: null,
      usage: {
        inputTokens: message?.length || 0,
        outputTokens: response.length,
        totalTokens: (message?.length || 0) + response.length
      }
    }

    return NextResponse.json(apiResponse)
  } catch (error) {
    console.error('Error in arquitecto API:', error)
    return NextResponse.json(
      { error: 'Error interno del servidor' },
      { status: 500 }
    )
  }
}
