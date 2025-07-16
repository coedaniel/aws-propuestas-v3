import { NextRequest, NextResponse } from 'next/server';
import { BedrockRuntimeClient, ConverseCommand } from '@aws-sdk/client-bedrock-runtime';

const client = new BedrockRuntimeClient({ region: 'us-east-1' });

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { 
      messages, 
      modelId = 'amazon.nova-pro-v1:0',
      mode = 'chat-libre'
    } = body;

    console.log('🗣️ Chat libre request:', { modelId, messageCount: messages.length });

    // Simple system prompt for chat libre
    const systemPrompt = `
Eres un asistente de AWS experto y amigable. 

INSTRUCCIONES:
- Responde de manera natural y conversacional
- Proporciona información técnica precisa sobre AWS
- Sé útil y profesional
- Si no sabes algo, admítelo honestamente
- Mantén las respuestas concisas pero informativas

Responde en español de manera natural y profesional.
`;

    // Prepare conversation for Bedrock
    const conversation = [
      { role: 'system', content: systemPrompt },
      ...messages
    ];

    // Call Bedrock model
    const command = new ConverseCommand({
      modelId: modelId,
      messages: conversation.slice(1), // Remove system message for Converse API
      system: [{ text: conversation[0].content }],
      inferenceConfig: {
        maxTokens: 4000,
        temperature: 0.7
      }
    });

    const response = await client.send(command);
    const responseText = response.output?.message?.content?.[0]?.text || 'No response from model';

    return NextResponse.json({
      response: responseText,
      modelId: modelId,
      mode: mode,
      usage: {
        inputTokens: response.usage?.inputTokens || 0,
        outputTokens: response.usage?.outputTokens || 0,
        totalTokens: (response.usage?.inputTokens || 0) + (response.usage?.outputTokens || 0)
      }
    });

  } catch (error) {
    console.error('Error in chat API:', error);
    return NextResponse.json(
      { error: 'Error processing chat request', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
