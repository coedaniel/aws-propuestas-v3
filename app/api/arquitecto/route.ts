import { NextRequest, NextResponse } from 'next/server';
import { BedrockRuntimeClient, ConverseCommand } from '@aws-sdk/client-bedrock-runtime';

const client = new BedrockRuntimeClient({ region: 'us-east-1' });

// Your Real MCP Services running in ECS
const MCP_SERVICES = {
  core: 'https://mcp.danielingram.shop/core',
  awsdocs: 'https://mcp.danielingram.shop/awsdocs', 
  diagram: 'https://mcp.danielingram.shop/diagram',
  pricing: 'https://mcp.danielingram.shop/pricing',
  customdoc: 'https://mcp.danielingram.shop/customdoc',
  cfn: 'https://mcp.danielingram.shop/cfn'
};

// MCP Service Detection Patterns
const MCP_PATTERNS = {
  core: ['entender', 'analizar', 'que necesito', 'ayuda con'],
  awsdocs: ['documentacion', 'como hacer', 'mejores practicas', 'guia', 'tutorial'],
  diagram: ['diagrama', 'arquitectura', 'visual', 'grafico', 'esquema'],
  pricing: ['costo', 'precio', 'cuanto cuesta', 'presupuesto', 'facturacion'],
  customdoc: ['documento', 'propuesta', 'word', 'pdf', 'generar archivo', 'entregable'],
  cfn: ['cloudformation', 'template', 'infraestructura', 'codigo', 'despliegue']
};

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { 
      message, 
      conversationHistory = [], 
      selectedModel = 'amazon.nova-pro-v1:0', 
      projectData 
    } = body;

    // Step 1: Use CORE MCP for prompt understanding (like Amazon Q CLI)
    console.log('🧠 Using CORE MCP for prompt understanding...');
    const promptUnderstanding = await callMCPService('core', {
      action: 'understand',
      message: message,
      context: conversationHistory
    });

    // Step 2: Detect which MCP services are needed
    const neededServices = detectNeededMCPServices(message);
    console.log('🔍 Detected MCP services needed:', neededServices);

    // Step 3: Enhanced system prompt with MCP awareness
    const systemPrompt = `
Eres un arquitecto de soluciones AWS experto con acceso a servicios MCP especializados.

SERVICIOS MCP DISPONIBLES:
${neededServices.map(service => `- ${service.toUpperCase()}: ${getMCPDescription(service)}`).join('\n')}

PROMPT UNDERSTANDING RESULT:
${JSON.stringify(promptUnderstanding, null, 2)}

INSTRUCCIONES:
1. Analiza la consulta del usuario usando el prompt understanding
2. Decide qué servicios MCP necesitas usar
3. Proporciona respuestas completas y profesionales
4. Genera entregables cuando sea apropiado (diagramas, documentos, templates)

Responde de manera natural y profesional como un consultor AWS real.
`;

    // Step 4: Call Bedrock model
    const conversation = [
      { role: 'system', content: systemPrompt },
      ...conversationHistory,
      { role: 'user', content: message }
    ];

    const modelResponse = await callBedrockModel(selectedModel, conversation);

    // Step 5: Actually call the detected MCP services
    const mcpResults: any = {};
    const usedServices: string[] = ['core']; // Core is always used

    // Call AWS Documentation service for better responses
    if (neededServices.includes('awsdocs')) {
      console.log('📚 Calling AWS DOCS MCP service...');
      usedServices.push('awsdocs');
      try {
        const keyTerms = extractKeyTermsFromMessage(message);
        const docsResult = await callMCPService('awsdocs', {
          action: 'search',
          query: keyTerms,
          limit: 5
        });
        mcpResults.awsdocs = docsResult;
      } catch (error) {
        console.error('Error calling AWS docs MCP:', error);
      }
    }

    // Call pricing service for cost estimates
    if (neededServices.includes('pricing')) {
      console.log('💰 Calling PRICING MCP service...');
      usedServices.push('pricing');
      try {
        const services = extractServicesFromResponse(modelResponse);
        const pricingResult = await callMCPService('pricing', {
          action: 'estimate',
          services: services,
          region: 'us-east-1',
          usage: 'standard'
        });
        mcpResults.pricing = pricingResult;
      } catch (error) {
        console.error('Error calling pricing MCP:', error);
      }
    }

    // Call diagram service if architecture is mentioned
    if (neededServices.includes('diagram') || shouldGenerateDiagram(modelResponse)) {
      console.log('📊 Calling DIAGRAM MCP service...');
      usedServices.push('diagram');
      try {
        const services = extractServicesFromResponse(modelResponse);
        const diagramResult = await callMCPService('diagram', {
          action: 'generate',
          type: 'aws-architecture',
          description: extractDescriptionFromResponse(modelResponse),
          services: services,
          title: `Arquitectura - ${extractProjectName(message) || 'Proyecto AWS'}`
        });
        mcpResults.diagram = diagramResult;
      } catch (error) {
        console.error('Error calling diagram MCP:', error);
      }
    }

    // Call CloudFormation service if infrastructure code is needed
    if (neededServices.includes('cfn') || shouldGenerateCloudFormation(modelResponse)) {
      console.log('🏗️ Calling CloudFormation MCP service...');
      usedServices.push('cfn');
      try {
        const services = extractServicesFromResponse(modelResponse);
        const cfnResult = await callMCPService('cfn', {
          action: 'generate',
          services: services,
          projectName: extractProjectName(message) || 'aws-project',
          description: extractDescriptionFromResponse(modelResponse)
        });
        mcpResults.cloudformation = cfnResult;
      } catch (error) {
        console.error('Error calling CloudFormation MCP:', error);
      }
    }

    // Call document generation service for deliverables
    if (neededServices.includes('customdoc') || shouldGenerateDocument(modelResponse)) {
      console.log('📄 Calling CUSTOM DOC MCP service...');
      usedServices.push('customdoc');
      try {
        const docsResult = await callMCPService('awsdocs', {
          action: 'search',
          query: extractKeyTermsFromMessage(message),
          limit: 5
        });
        mcpResults.documentation = docsResult;
      } catch (error) {
        console.error('Error calling docs MCP:', error);
      }
    }

    // Call pricing service if needed
    if (neededServices.includes('pricing')) {
      console.log('💰 Calling PRICING MCP service...');
      usedServices.push('pricing');
      try {
        const pricingResult = await callMCPService('pricing', {
          action: 'calculate',
          services: extractServicesFromResponse(modelResponse),
          region: 'us-east-1'
        });
        mcpResults.pricing = pricingResult;
      } catch (error) {
        console.error('Error calling pricing MCP:', error);
      }
    }

    // Call CloudFormation service if needed
    if (neededServices.includes('cfn') && shouldGenerateCloudFormation(modelResponse)) {
      console.log('🏗️ Calling CFN MCP service...');
      usedServices.push('cfn');
      try {
        const cfnResult = await callMCPService('cfn', {
          action: 'generate',
          services: extractServicesFromResponse(modelResponse),
          projectName: projectData?.name || 'aws-project'
        });
        mcpResults.cloudformation = cfnResult;
      } catch (error) {
        console.error('Error calling CFN MCP:', error);
      }
    }

    // Call document generation service if needed
    if (neededServices.includes('customdoc') && shouldGenerateDocument(modelResponse)) {
      console.log('📄 Calling CUSTOM DOC MCP service...');
      usedServices.push('customdoc');
      try {
      try {
        const projectName = extractProjectName(message) || 'Proyecto AWS';
        const docResult = await callMCPService('customdoc', {
          action: 'generate',
          type: 'comprehensive-proposal',
          projectName: projectName,
          content: modelResponse,
          format: 'multiple', // Generate multiple formats
          includeCalculator: mcpResults.pricing ? true : false,
          includeDiagram: mcpResults.diagram ? true : false,
          includeCloudFormation: mcpResults.cloudformation ? true : false,
          encoding: 'utf-8' // Explicitly set UTF-8 encoding
        });
        mcpResults.document = docResult;
      } catch (error) {
        console.error('Error calling document MCP:', error);
      }
    }

    // Step 6: Enhanced response with comprehensive MCP transparency
    const finalResponse = ensureUTF8(modelResponse);
    
    return NextResponse.json({
      response: finalResponse,
      selectedModel,
      mode: 'arquitecto',
      projectInfo: {
        name: extractProjectName(message) || 'Proyecto AWS',
        description: extractDescriptionFromResponse(finalResponse),
        services: extractServicesFromResponse(finalResponse),
        estimatedCost: mcpResults.pricing?.totalCost || null
      },
      currentStep: 1,
      isComplete: finalResponse.toLowerCase().includes('completad') || finalResponse.toLowerCase().includes('finaliz'),
      documentsGenerated: Object.keys(mcpResults).length > 1, // More than just core
      s3Folder: null, // Will be set by document generation
      mcpServicesUsed: usedServices,
      mcpResults: mcpResults,
      promptUnderstanding: promptUnderstanding,
      transparency: {
        message: usedServices.length > 1 
          ? `✅ Servicios MCP utilizados: ${usedServices.filter(s => s !== 'core').join(', ')}. ${Object.keys(mcpResults).length - 1} documentos generados.`
          : '🤖 Respuesta generada solo con conocimiento del modelo',
        services: usedServices,
        documentsGenerated: Object.keys(mcpResults).filter(k => k !== 'core').length,
        servicesDetected: neededServices,
        actuallyUsed: usedServices.length > 1
      },
      usage: {
        inputTokens: 0,
        outputTokens: 0,
        totalTokens: 0
      }
    });

  } catch (error) {
    console.error('Error in arquitecto API:', error);
    return NextResponse.json(
      { error: 'Error processing request', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

// Call your MCP services running in ECS
async function callMCPService(service: string, payload: any) {
  const serviceUrl = MCP_SERVICES[service as keyof typeof MCP_SERVICES];
  
  if (!serviceUrl) {
    throw new Error(`MCP service ${service} not found`);
  }

  console.log(`🔧 Calling MCP service: ${service} at ${serviceUrl}`);
  console.log(`📤 Payload:`, JSON.stringify(payload, null, 2));
  
  const response = await fetch(serviceUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Accept': 'application/json',
      'User-Agent': 'AWS-Propuestas-v3-MCP-Client'
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error(`❌ MCP service ${service} failed:`, response.status, errorText);
    throw new Error(`MCP service ${service} failed: ${response.statusText}`);
  }

  const result = await response.json();
  console.log(`📥 MCP service ${service} response:`, result);
  
  // Ensure UTF-8 encoding in response
  if (typeof result === 'string') {
    return ensureUTF8(result);
  } else if (result && typeof result === 'object') {
    return JSON.parse(ensureUTF8(JSON.stringify(result)));
  }
  
  return result;
}

// Detect which MCP services are needed based on user message
function detectNeededMCPServices(message: string): string[] {
  const messageLower = message.toLowerCase();
  const neededServices: string[] = [];

  // Always use core for prompt understanding
  neededServices.push('core');

  // Check each service pattern
  Object.entries(MCP_PATTERNS).forEach(([service, patterns]) => {
    if (service === 'core') return; // Already added
    
    const isNeeded = patterns.some(pattern => 
      messageLower.includes(pattern.toLowerCase())
    );
    
    if (isNeeded) {
      neededServices.push(service);
    }
  });

  return neededServices;
}

function getMCPDescription(service: string): string {
  const descriptions = {
    core: 'Prompt understanding and analysis',
    awsdocs: 'AWS documentation search and best practices',
    diagram: 'Architecture diagram generation',
    pricing: 'AWS cost calculation and optimization',
    customdoc: 'Document generation (DOCX, PDF, TXT)',
    cfn: 'CloudFormation template generation'
  };
  
  return descriptions[service as keyof typeof descriptions] || 'Unknown service';
}

// Call Bedrock model
async function callBedrockModel(modelId: string, conversation: any[]) {
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
  return response.output?.message?.content?.[0]?.text || 'No response from model';
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
  const sentences = response.split('.').slice(0, 3);
  return sentences.join('.').trim();
}

// Extract project name from user message
function extractProjectName(message: string): string | null {
  // Look for patterns like "proyecto X", "sistema X", "aplicación X", etc.
  const patterns = [
    /proyecto\s+([^,.\n]+)/i,
    /sistema\s+([^,.\n]+)/i,
    /aplicaci[oó]n\s+([^,.\n]+)/i,
    /plataforma\s+([^,.\n]+)/i,
    /portal\s+([^,.\n]+)/i,
    /"([^"]+)"/g, // Text in quotes
    /llamado\s+([^,.\n]+)/i,
    /nombre\s+([^,.\n]+)/i
  ];

  for (const pattern of patterns) {
    const match = message.match(pattern);
    if (match && match[1]) {
      const projectName = match[1].trim();
      // Filter out common words that aren't project names
      if (projectName.length > 2 && 
          !['que', 'como', 'para', 'con', 'por', 'una', 'uno', 'del', 'de', 'la', 'el'].includes(projectName.toLowerCase())) {
        return projectName;
      }
    }
  }

  return null;
}

// Improve UTF-8 encoding handling
function ensureUTF8(text: string): string {
  // Fix common encoding issues
  return text
    .replace(/Ã³/g, 'ó')
    .replace(/Ã¡/g, 'á')
    .replace(/Ã©/g, 'é')
    .replace(/Ã­/g, 'í')
    .replace(/Ãº/g, 'ú')
    .replace(/Ã±/g, 'ñ')
    .replace(/Ã/g, 'Á')
    .replace(/Ã‰/g, 'É')
    .replace(/Ã/g, 'Í')
    .replace(/Ã"/g, 'Ó')
    .replace(/Ãš/g, 'Ú')
    .replace(/Ã'/g, 'Ñ');
}
function extractKeyTermsFromMessage(message: string): string {
  const commonWords = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'how', 'what', 'when', 'where', 'why'];
  const words = message.toLowerCase().split(/\s+/);
  const keyWords = words.filter(word => 
    word.length > 3 && 
    !commonWords.includes(word) &&
    (word.includes('aws') || word.includes('ec2') || word.includes('s3') || word.includes('lambda') || word.includes('rds'))
  );
  
function extractKeyTermsFromMessage(message: string): string {
  const commonWords = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'how', 'what', 'when', 'where', 'why'];
  const words = message.toLowerCase().split(/\s+/);
  const keyWords = words.filter(word => 
    word.length > 3 && 
    !commonWords.includes(word) &&
    (word.includes('aws') || word.includes('ec2') || word.includes('s3') || word.includes('lambda') || word.includes('rds'))
  );
  
  return keyWords.slice(0, 5).join(' ') || message.slice(0, 100);
}
