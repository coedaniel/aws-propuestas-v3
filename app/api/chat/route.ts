import { NextRequest, NextResponse } from 'next/server'
import { BedrockRuntimeClient, InvokeModelCommand } from '@aws-sdk/client-bedrock-runtime'

const bedrockClient = new BedrockRuntimeClient({
  region: process.env.NEXT_PUBLIC_REGION || 'us-east-1'
})

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { messages, modelId = 'amazon.nova-pro-v1:0', mode = 'chat-libre' } = body

    if (!messages || !Array.isArray(messages)) {
      return NextResponse.json(
        { error: 'Messages are required and must be an array' },
        { status: 400 }
      )
    }

    // System prompt for chat libre mode
    const systemPrompt = `Eres un asistente experto en AWS (Amazon Web Services) con amplio conocimiento en:

- Arquitecturas de soluciones en la nube
- Servicios de AWS y sus casos de uso
- Mejores prácticas de seguridad, escalabilidad y costos
- Diseño de infraestructura serverless y tradicional
- Migración a la nube y modernización de aplicaciones
- DevOps, CI/CD y automatización en AWS
- Análisis de costos y optimización

Proporciona respuestas técnicas precisas, prácticas y profesionales. Incluye ejemplos específicos cuando sea relevante y sugiere mejores prácticas. Mantén un tono profesional pero accesible.

Si la pregunta no está relacionada con AWS o tecnología en la nube, redirige amablemente la conversación hacia temas de AWS donde puedas ser más útil.`

    // Prepare the prompt based on model
    let promptBody: any

    if (modelId.startsWith('anthropic.claude')) {
      // Claude format
      promptBody = {
        anthropic_version: 'bedrock-2023-05-31',
        max_tokens: 4000,
        system: systemPrompt,
        messages: messages
      }
    } else if (modelId.startsWith('amazon.nova')) {
      // Nova format - combine system prompt with first user message
      const novaMessages = [
        {
          role: 'user',
          content: [{ text: systemPrompt + '\n\nUsuario: ' + messages[0]?.content || '' }]
        }
      ]
      
      // Add remaining messages
      if (messages.length > 1) {
        for (let i = 1; i < messages.length; i++) {
          novaMessages.push({
            role: messages[i].role,
            content: [{ text: messages[i].content }]
          })
        }
      }

      promptBody = {
        messages: novaMessages,
        inferenceConfig: {
          max_new_tokens: 4000,
          temperature: 0.7
        }
      }
    } else {
      // Default format
      promptBody = {
        messages: [{ role: 'system', content: systemPrompt }, ...messages],
        max_tokens: 4000,
        temperature: 0.7
      }
    }

    console.log(`🚀 CHAT LIBRE - USING MODEL: ${modelId}`)

    // Call Bedrock
    const command = new InvokeModelCommand({
      modelId,
      body: JSON.stringify(promptBody),
      contentType: 'application/json'
    })

    const response = await bedrockClient.send(command)
    const responseBody = JSON.parse(new TextDecoder().decode(response.body))

    // Extract response based on model
    let aiResponse: string
    let usage: any = {}

    if (modelId.startsWith('anthropic.claude')) {
      aiResponse = responseBody.content?.[0]?.text || ''
      usage = {
        inputTokens: responseBody.usage?.input_tokens,
        outputTokens: responseBody.usage?.output_tokens
      }
    } else if (modelId.startsWith('amazon.nova')) {
      aiResponse = responseBody.output?.message?.content?.[0]?.text || ''
      usage = {
        inputTokens: responseBody.usage?.inputTokens,
        outputTokens: responseBody.usage?.outputTokens,
        totalTokens: responseBody.usage?.totalTokens
      }
    } else {
      aiResponse = responseBody.content || responseBody.message || ''
    }

    return NextResponse.json({
      response: aiResponse,
      modelId,
      mode,
      usage
    })

  } catch (error) {
    console.error('Error in chat API:', error)
    
    return NextResponse.json(
      { 
        error: 'Internal server error',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}
