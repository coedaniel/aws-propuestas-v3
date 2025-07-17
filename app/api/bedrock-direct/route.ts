import { NextRequest, NextResponse } from 'next/server'
import { BedrockRuntimeClient, ConverseCommand, InvokeModelCommand } from '@aws-sdk/client-bedrock-runtime'

const bedrockClient = new BedrockRuntimeClient({
  region: 'us-east-1',
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  }
})

interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

interface ChatRequest {
  messages: ChatMessage[]
  modelId: string
}

export async function POST(request: NextRequest) {
  try {
    const body: ChatRequest = await request.json()
    const { messages, modelId } = body

    // Convertir mensajes al formato Bedrock
    const bedrockMessages = messages.map((msg, index) => ({
      role: index === 0 && msg.role !== 'user' ? 'user' : msg.role,
      content: [{ text: msg.content }]
    }))

    let response

    // Nova Pro usa invoke_model
    if (modelId.includes('nova')) {
      const payload = {
        messages: bedrockMessages,
        inferenceConfig: {
          maxTokens: 4000,
          temperature: 0.7
        }
      }

      const command = new InvokeModelCommand({
        modelId,
        body: JSON.stringify(payload),
        contentType: 'application/json',
        accept: 'application/json'
      })

      const result = await bedrockClient.send(command)
      const responseBody = JSON.parse(new TextDecoder().decode(result.body))
      
      return NextResponse.json({
        response: responseBody.output.message.content[0].text,
        modelId,
        usage: responseBody.usage
      })
    } 
    // Claude usa converse
    else {
      const command = new ConverseCommand({
        modelId,
        messages: bedrockMessages,
        inferenceConfig: {
          maxTokens: 4000,
          temperature: 0.7
        }
      })

      const result = await bedrockClient.send(command)
      
      return NextResponse.json({
        response: result.output?.message?.content?.[0]?.text || 'No response',
        modelId,
        usage: result.usage
      })
    }

  } catch (error) {
    console.error('Bedrock Direct Error:', error)
    
    return NextResponse.json(
      { 
        error: 'Error calling Bedrock directly',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

export async function GET() {
  return NextResponse.json({
    status: 'Bedrock Direct API is running',
    models: [
      'amazon.nova-pro-v1:0',
      'anthropic.claude-3-5-sonnet-20240620-v1:0'
    ]
  })
}
