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

    // Step 1: TEMPORARILY DISABLE MCP prompt understanding to fix basic functionality
    console.log('🧠 Basic prompt processing (MCP temporarily disabled)...');
    const promptUnderstanding = null; // Disabled for now
    
    // Step 2: Detect which services are mentioned (basic detection)
    const neededServices = detectNeededMCPServices(message);
    console.log('🔍 Detected services mentioned:', neededServices);

    // Step 3: Simplified system prompt focused on project extraction
    const systemPrompt = `
Eres un arquitecto de soluciones AWS experto.

INSTRUCCIONES IMPORTANTES:
1. Si el usuario menciona un nombre de proyecto específico (como "sukarne", "mi-app", etc.), SIEMPRE úsalo exactamente como lo menciona
2. Detecta correctamente los servicios AWS mencionados (EC2, RDS, VPC, Load Balancer, etc.)
3. Proporciona respuestas técnicas detalladas sobre arquitectura AWS
4. Si mencionan "sistema de tres capas", incluye: presentación, lógica de negocio, y datos
5. Sé específico sobre la configuración de cada servicio AWS

FORMATO DE RESPUESTA:
- Usa el nombre exacto del proyecto que mencione el usuario
- Lista los servicios AWS detectados
- Proporciona detalles técnicos específicos
- Incluye consideraciones de seguridad y mejores prácticas

Responde de manera profesional y técnica como un consultor AWS experimentado.
`;

    // Step 4: Call Bedrock model with simplified conversation
    const conversation = [
      { role: 'system', content: systemPrompt },
      ...conversationHistory,
      { role: 'user', content: message }
    ];

    const modelResponse = await callBedrockModel(selectedModel, conversation);

    // Step 5: TEMPORARILY DISABLE MCP calls to fix basic functionality
    const mcpResults: any = {};
    const usedServices: string[] = ['core']; // Only core for now
    
    // TODO: Re-enable MCP calls after fixing basic functionality
    /*
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
    */

    // Step 6: Simplified response - DISABLE MCP calls temporarily to fix basic functionality
    const finalResponse = ensureUTF8(modelResponse);
    const extractedProjectName = extractProjectName(message);
    
    return NextResponse.json({
      response: finalResponse,
      selectedModel,
      mode: 'arquitecto',
      projectInfo: {
        name: extractedProjectName || 'Proyecto AWS',
        description: extractDescriptionFromResponse(finalResponse),
        services: extractServicesFromResponse(finalResponse),
        estimatedCost: null
      },
      currentStep: 1,
      isComplete: finalResponse.toLowerCase().includes('completad') || finalResponse.toLowerCase().includes('finaliz'),
      documentsGenerated: false, // Temporarily disabled
      s3Folder: extractedProjectName || null,
      mcpServicesUsed: ['core'], // Simplified
      mcpResults: {},
      promptUnderstanding: null,
      transparency: {
        message: '🤖 Respuesta generada con modelo Bedrock',
        services: ['core'],
        documentsGenerated: 0,
        servicesDetected: [],
        actuallyUsed: false
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
    /llamado\s+([a-zA-Z0-9áéíóúñü\s]+)/i,
    /nombre\s+([a-zA-Z0-9áéíóúñü\s]+)/i,
    /proyecto\s+([a-zA-Z0-9áéíóúñü\s]+)/i,
    /sistema\s+([a-zA-Z0-9áéíóúñü\s]+)/i,
    /aplicaci[oó]n\s+([a-zA-Z0-9áéíóúñü\s]+)/i,
    /plataforma\s+([a-zA-Z0-9áéíóúñü\s]+)/i,
    /"([^"]+)"/g, // Text in quotes
  ];

  for (const pattern of patterns) {
    const match = message.match(pattern);
    if (match && match[1]) {
      const projectName = match[1].trim();
      // Filter out common words and keep real project names
      const excludeWords = ['que', 'como', 'para', 'con', 'por', 'una', 'uno', 'del', 'de', 'la', 'el', 'se', 'encuentra', 'proyecto', 'sistema'];
      const words = projectName.toLowerCase().split(/\s+/);
      const validWords = words.filter(word => !excludeWords.includes(word) && word.length > 2);
      
      if (validWords.length > 0) {
        return validWords.join(' ');
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

// Extract key terms from user message for documentation search
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
