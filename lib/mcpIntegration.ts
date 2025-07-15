// MCP Integration for Arquitecto Chat
// This module handles intelligent MCP service routing based on user requests

export interface MCPRequest {
  service: string;
  action: string;
  data: any;
}

export interface MCPResponse {
  success: boolean;
  data?: any;
  error?: string;
}

// MCP Service URLs from environment
const MCP_BASE_URL = process.env.NEXT_PUBLIC_MCP_BASE_URL || 'https://mcp.danielingram.shop';

// MCP Service Detection Patterns
const MCP_PATTERNS = {
  diagram: [
    'diagrama', 'diagram', 'arquitectura', 'architecture', 'visual', 'grafico',
    'esquema', 'diseño', 'layout', 'topologia', 'svg', 'png', 'draw.io'
  ],
  documentation: [
    'documentacion', 'documentation', 'aws docs', 'servicio', 'service',
    'como funciona', 'que es', 'explicacion', 'guia', 'manual', 'referencia'
  ],
  cost: [
    'costo', 'cost', 'precio', 'price', 'presupuesto', 'budget', 'calculadora',
    'calculator', 'estimacion', 'estimate', 'facturacion', 'billing'
  ],
  cloudformation: [
    'cloudformation', 'cfn', 'template', 'plantilla', 'script', 'codigo',
    'infrastructure', 'infraestructura', 'iac', 'despliegue', 'deploy'
  ],
  customdoc: [
    'documento', 'document', 'word', 'propuesta', 'proposal', 'informe',
    'report', 'entregable', 'deliverable', 'archivo', 'file'
  ]
};

// Detect which MCP services are needed based on user input
export function detectMCPServices(userInput: string, conversationContext: string[]): string[] {
  const input = userInput.toLowerCase();
  const context = conversationContext.join(' ').toLowerCase();
  const combinedText = `${input} ${context}`;
  
  const neededServices: string[] = [];
  
  // Check each service pattern
  Object.entries(MCP_PATTERNS).forEach(([service, patterns]) => {
    const hasPattern = patterns.some(pattern => 
      combinedText.includes(pattern.toLowerCase())
    );
    
    if (hasPattern) {
      neededServices.push(service);
    }
  });
  
  // Smart detection based on conversation flow
  if (context.includes('generar') || context.includes('crear')) {
    if (combinedText.includes('diagrama') || combinedText.includes('arquitectura')) {
      if (!neededServices.includes('diagram')) neededServices.push('diagram');
    }
    if (combinedText.includes('documento') || combinedText.includes('propuesta')) {
      if (!neededServices.includes('customdoc')) neededServices.push('customdoc');
    }
    if (combinedText.includes('cloudformation') || combinedText.includes('script')) {
      if (!neededServices.includes('cloudformation')) neededServices.push('cloudformation');
    }
  }
  
  return neededServices;
}

// Call MCP service
export async function callMCPService(
  service: string, 
  action: string, 
  data: any
): Promise<MCPResponse> {
  try {
    const response = await fetch(`/api/mcp-proxy/${service}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        action,
        data
      })
    });

    if (!response.ok) {
      throw new Error(`MCP ${service} service error: ${response.statusText}`);
    }

    const result = await response.json();
    return {
      success: true,
      data: result
    };
  } catch (error) {
    console.error(`MCP ${service} service error:`, error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}

// Enhanced arquitecto request with MCP integration
export async function sendArquitectoRequestWithMCP(
  message: string,
  conversationHistory: Array<{role: 'user' | 'assistant', content: string}>,
  selectedModel: string,
  projectData?: any
) {
  // Extract conversation context
  const conversationContext = conversationHistory.map(msg => msg.content);
  
  // Detect needed MCP services
  const neededServices = detectMCPServices(message, conversationContext);
  
  // Prepare MCP data if services are needed
  let mcpData: any = {};
  
  if (neededServices.length > 0) {
    console.log('MCP Services needed:', neededServices);
    
    // Gather MCP data based on needed services
    for (const service of neededServices) {
      try {
        switch (service) {
          case 'documentation':
            // Get AWS documentation if user asks about specific services
            const awsServices = extractAWSServices(message);
            if (awsServices.length > 0) {
              const docResponse = await callMCPService('aws-docs', 'search', {
                query: awsServices.join(' '),
                limit: 3
              });
              if (docResponse.success) {
                mcpData.documentation = docResponse.data;
              }
            }
            break;
            
          case 'cost':
            // Get cost information if user mentions pricing
            if (projectData?.services) {
              const costResponse = await callMCPService('pricing', 'estimate', {
                services: projectData.services,
                region: projectData.region || 'us-east-1'
              });
              if (costResponse.success) {
                mcpData.costs = costResponse.data;
              }
            }
            break;
            
          case 'diagram':
            // Prepare for diagram generation
            mcpData.diagramRequest = {
              type: 'architecture',
              services: projectData?.services || [],
              title: projectData?.name || 'AWS Architecture'
            };
            break;
            
          case 'cloudformation':
            // Prepare for CloudFormation generation
            mcpData.cloudformationRequest = {
              services: projectData?.services || [],
              region: projectData?.region || 'us-east-1',
              projectName: projectData?.name || 'aws-project'
            };
            break;
            
          case 'customdoc':
            // Prepare for document generation
            mcpData.documentRequest = {
              type: 'proposal',
              projectData: projectData,
              template: 'aws-proposal'
            };
            break;
        }
      } catch (error) {
        console.error(`Error preparing MCP data for ${service}:`, error);
      }
    }
  }
  
  // Send request to arquitecto with MCP context
  const response = await fetch('/api/arquitecto', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      conversationHistory,
      selectedModel,
      projectData,
      mcpData,
      neededServices
    })
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
}

// Extract AWS services mentioned in text
function extractAWSServices(text: string): string[] {
  const awsServices = [
    'ec2', 'rds', 's3', 'lambda', 'api gateway', 'cloudfront', 'route53',
    'vpc', 'elb', 'alb', 'nlb', 'ecs', 'eks', 'fargate', 'dynamodb',
    'sqs', 'sns', 'ses', 'cloudwatch', 'cloudtrail', 'iam', 'cognito',
    'amplify', 'appsync', 'kinesis', 'redshift', 'athena', 'glue',
    'sagemaker', 'bedrock', 'opensearch', 'elasticache', 'documentdb'
  ];
  
  const lowerText = text.toLowerCase();
  return awsServices.filter(service => 
    lowerText.includes(service.toLowerCase())
  );
}

// Generate diagram using MCP
export async function generateDiagram(
  services: string[],
  title: string,
  description?: string
): Promise<MCPResponse> {
  return callMCPService('diagram', 'generate', {
    type: 'aws-architecture',
    services,
    title,
    description,
    format: ['svg', 'png', 'drawio']
  });
}

// Generate CloudFormation using MCP
export async function generateCloudFormation(
  services: string[],
  projectName: string,
  region: string = 'us-east-1'
): Promise<MCPResponse> {
  return callMCPService('cfn', 'generate', {
    services,
    projectName: projectName.replace(/[^a-zA-Z0-9]/g, '-').toLowerCase(),
    region,
    template: 'complete-stack'
  });
}

// Generate document using MCP
export async function generateDocument(
  projectData: any,
  documentType: string = 'proposal'
): Promise<MCPResponse> {
  return callMCPService('customdoc', 'generate', {
    type: documentType,
    projectData,
    format: 'docx',
    template: 'aws-proposal'
  });
}

// Get cost estimation using MCP
export async function getCostEstimation(
  services: string[],
  region: string = 'us-east-1',
  usage?: any
): Promise<MCPResponse> {
  return callMCPService('pricing', 'calculate', {
    services,
    region,
    usage: usage || 'standard',
    format: 'detailed'
  });
}
