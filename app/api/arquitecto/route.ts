import { NextRequest, NextResponse } from 'next/server';
import { callMCPService } from '@/lib/mcpIntegration';
import { detectMCPServices, getEnhancedSystemPrompt, shouldUseMCP, getMCPToolsForServices } from '@/lib/mcpConfig';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { 
      message, 
      conversationHistory = [], 
      selectedModel = 'amazon.nova-pro-v1:0', 
      projectData 
    } = body;

    // Detect which MCP services are needed based on the message
    const detectedServices = detectMCPServices(message);
    const shouldUseMCPServices = shouldUseMCP(message);
    
    // Get enhanced system prompt with MCP capabilities
    const systemPrompt = getEnhancedSystemPrompt(detectedServices);

    // Prepare conversation for the model
    const conversation = [
      { role: 'system', content: systemPrompt },
      ...conversationHistory,
      { role: 'user', content: message }
    ];

    // Call the selected model
    const modelResponse = await callBedrockModel(selectedModel, conversation);

    // Initialize response data
    let responseData: any = {
      response: modelResponse,
      selectedModel,
      mcpServicesDetected: detectedServices.map(s => s.name),
      usage: {
        inputTokens: 0,
        outputTokens: 0,
        totalTokens: 0
      }
    };

    // If MCP services were detected, try to enhance the response
    if (shouldUseMCPServices && detectedServices.length > 0) {
      try {
        // Check if we should generate diagrams
        if (detectedServices.some(s => s.name === 'aws-diagram') && shouldGenerateDiagram(modelResponse)) {
          const diagramResult = await callMCPService('diagram', 'generate', {
            type: 'aws-architecture',
            services: extractServicesFromResponse(modelResponse),
            title: projectData?.name || 'AWS Architecture Diagram',
            description: extractDescriptionFromResponse(modelResponse)
          });
          
          if (diagramResult.success) {
            responseData.generatedFiles = responseData.generatedFiles || {};
            responseData.generatedFiles.diagram = diagramResult.data;
          }
        }

        // Check if we should generate CloudFormation
        if (detectedServices.some(s => s.name === 'aws-cdk') && shouldGenerateCloudFormation(modelResponse)) {
          const cfnResult = await callMCPService('cfn', 'generate', {
            services: extractServicesFromResponse(modelResponse),
            projectName: projectData?.name || 'aws-project',
            region: 'us-east-1'
          });
          
          if (cfnResult.success) {
            responseData.generatedFiles = responseData.generatedFiles || {};
            responseData.generatedFiles.cloudformation = cfnResult.data;
          }
        }

        // Check if we should search AWS documentation
        if (detectedServices.some(s => s.name === 'aws-documentation')) {
          const docSearchResult = await callMCPService('documentation', 'search', {
            query: extractKeyTermsFromMessage(message),
            limit: 5
          });
          
          if (docSearchResult.success) {
            responseData.awsDocumentation = docSearchResult.data;
          }
        }

      } catch (mcpError) {
        console.error('Error calling MCP services:', mcpError);
        // Continue with the basic response even if MCP services fail
      }
    }

    return NextResponse.json(responseData);

  } catch (error) {
    console.error('Error in arquitecto API:', error);
    return NextResponse.json(
      { error: 'Error processing request', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

// Call Bedrock model
async function callBedrockModel(modelId: string, conversation: any[]) {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      messages: conversation,
      modelId: modelId,
      maxTokens: 4000,
      temperature: 0.7
    })
  });

  if (!response.ok) {
    throw new Error(`Bedrock API error: ${response.statusText}`);
  }

  const data = await response.json();
  return data.response || data.message || 'No response from model';
}

// Helper functions to determine when to generate files
function shouldGenerateDiagram(response: string): boolean {
  const triggers = [
    'generar diagrama', 'crear diagrama', 'mostrar arquitectura',
    'diagrama de', 'esquema de', 'diseño de', 'grafico de',
    'architecture diagram', 'visual representation', 'draw architecture'
  ];
  
  return triggers.some(trigger => 
    response.toLowerCase().includes(trigger.toLowerCase())
  );
}

function shouldGenerateCloudFormation(response: string): boolean {
  const triggers = [
    'cloudformation', 'script', 'plantilla', 'template',
    'codigo', 'despliegue', 'infraestructura como codigo',
    'infrastructure as code', 'iac', 'cdk'
  ];
  
  return triggers.some(trigger => 
    response.toLowerCase().includes(trigger.toLowerCase())
  );
}

function shouldGenerateDocument(response: string): boolean {
  const triggers = [
    'documento', 'propuesta', 'informe', 'entregable',
    'archivo word', 'generar documento', 'create document',
    'generate report', 'proposal document'
  ];
  
  return triggers.some(trigger => 
    response.toLowerCase().includes(trigger.toLowerCase())
  );
}

// Extract services mentioned in the response
function extractServicesFromResponse(response: string): string[] {
  const awsServices = [
    'EC2', 'RDS', 'S3', 'Lambda', 'API Gateway', 'CloudFront', 'Route53',
    'VPC', 'ELB', 'ALB', 'NLB', 'ECS', 'EKS', 'Fargate', 'DynamoDB',
    'SQS', 'SNS', 'SES', 'CloudWatch', 'CloudTrail', 'IAM', 'Cognito',
    'ElastiCache', 'Redshift', 'EMR', 'Glue', 'Kinesis', 'Step Functions'
  ];
  
  return awsServices.filter(service => 
    response.toUpperCase().includes(service.toUpperCase())
  );
}

// Extract description from response
function extractDescriptionFromResponse(response: string): string {
  // Simple extraction - could be enhanced with NLP
  const sentences = response.split('.').slice(0, 3);
  return sentences.join('.').trim();
}

// Extract key terms from user message for documentation search
function extractKeyTermsFromMessage(message: string): string {
  // Remove common words and extract key AWS-related terms
  const commonWords = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'how', 'what', 'when', 'where', 'why'];
  const words = message.toLowerCase().split(/\s+/);
  const keyWords = words.filter(word => 
    word.length > 3 && 
    !commonWords.includes(word) &&
    (word.includes('aws') || word.includes('ec2') || word.includes('s3') || word.includes('lambda') || word.includes('rds'))
  );
  
  return keyWords.slice(0, 5).join(' ') || message.slice(0, 100);
}
