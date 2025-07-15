// MCP Configuration and Service Management
export interface MCPServiceConfig {
  name: string
  description: string
  tools: string[]
  patterns: string[]
  priority: number
}

export const MCP_SERVICES: MCPServiceConfig[] = [
  {
    name: 'aws-diagram',
    description: 'AWS architecture diagram generation',
    tools: ['generate_diagram', 'list_icons', 'get_diagram_examples'],
    patterns: [
      'diagram', 'architecture', 'visual', 'draw', 'chart', 'graph',
      'topology', 'infrastructure diagram', 'system design',
      'aws architecture', 'cloud diagram'
    ],
    priority: 1
  },
  {
    name: 'aws-documentation',
    description: 'AWS documentation search and retrieval',
    tools: ['search_documentation', 'read_documentation', 'recommend'],
    patterns: [
      'documentation', 'docs', 'guide', 'tutorial', 'reference',
      'how to', 'best practices', 'aws docs', 'manual',
      'specification', 'api reference'
    ],
    priority: 2
  },
  {
    name: 'aws-cdk',
    description: 'AWS CDK guidance and constructs',
    tools: ['CDKGeneralGuidance', 'SearchGenAICDKConstructs', 'ExplainCDKNagRule'],
    patterns: [
      'cdk', 'infrastructure as code', 'iac', 'cloudformation',
      'constructs', 'stack', 'deployment', 'aws cdk',
      'typescript', 'python cdk', 'cdk nag'
    ],
    priority: 3
  },
  {
    name: 'aws-serverless',
    description: 'AWS Serverless application development',
    tools: ['sam_init', 'sam_build', 'sam_deploy', 'deploy_webapp', 'get_lambda_guidance'],
    patterns: [
      'serverless', 'lambda', 'sam', 'api gateway', 'dynamodb',
      'event-driven', 'microservices', 'functions', 'serverless framework'
    ],
    priority: 4
  },
  {
    name: 'aws-iam',
    description: 'AWS IAM management and security',
    tools: ['list_users', 'create_user', 'attach_user_policy', 'simulate_principal_policy'],
    patterns: [
      'iam', 'security', 'permissions', 'policies', 'roles',
      'access control', 'authentication', 'authorization',
      'users', 'groups', 'security best practices'
    ],
    priority: 5
  },
  {
    name: 'dynamodb',
    description: 'DynamoDB database operations',
    tools: ['create_table', 'put_item', 'get_item', 'query', 'scan', 'dynamodb_data_modeling'],
    patterns: [
      'dynamodb', 'database', 'nosql', 'table', 'item',
      'query', 'scan', 'gsi', 'data modeling', 'partition key'
    ],
    priority: 6
  },
  {
    name: 'bedrock-kb',
    description: 'Amazon Bedrock Knowledge Base retrieval',
    tools: ['ListKnowledgeBases', 'QueryKnowledgeBases'],
    patterns: [
      'knowledge base', 'bedrock', 'rag', 'retrieval',
      'search knowledge', 'ai search', 'semantic search'
    ],
    priority: 7
  },
  {
    name: 'nova-canvas',
    description: 'Amazon Nova Canvas image generation',
    tools: ['generate_image', 'generate_image_with_colors'],
    patterns: [
      'image', 'generate image', 'nova canvas', 'picture',
      'visual content', 'illustration', 'graphic'
    ],
    priority: 8
  }
]

export function detectMCPServices(message: string): MCPServiceConfig[] {
  const messageLower = message.toLowerCase()
  const detectedServices: Array<{ service: MCPServiceConfig; score: number }> = []

  for (const service of MCP_SERVICES) {
    let score = 0
    
    for (const pattern of service.patterns) {
      if (messageLower.includes(pattern.toLowerCase())) {
        // Exact match gets higher score
        if (messageLower === pattern.toLowerCase()) {
          score += 10
        } else if (messageLower.includes(pattern.toLowerCase())) {
          score += 5
        }
      }
    }
    
    if (score > 0) {
      detectedServices.push({ service, score })
    }
  }

  // Sort by score (descending) and then by priority (ascending)
  return detectedServices
    .sort((a, b) => {
      if (a.score !== b.score) {
        return b.score - a.score
      }
      return a.service.priority - b.service.priority
    })
    .map(item => item.service)
}

export function getMCPToolsForServices(services: MCPServiceConfig[]): string[] {
  const tools = new Set<string>()
  
  for (const service of services) {
    for (const tool of service.tools) {
      tools.add(tool)
    }
  }
  
  return Array.from(tools)
}

export function shouldUseMCP(message: string): boolean {
  const detectedServices = detectMCPServices(message)
  return detectedServices.length > 0
}

// Enhanced system prompt for MCP-enabled arquitecto
export function getEnhancedSystemPrompt(detectedServices: MCPServiceConfig[]): string {
  const basePrompt = `You are an AWS Solutions Architect expert with access to specialized MCP (Model Context Protocol) services. You provide comprehensive AWS architecture guidance, cost optimization, and implementation recommendations.`

  if (detectedServices.length === 0) {
    return basePrompt
  }

  const serviceDescriptions = detectedServices
    .map(service => `- ${service.name}: ${service.description}`)
    .join('\n')

  return `${basePrompt}

AVAILABLE MCP SERVICES:
${serviceDescriptions}

INSTRUCTIONS:
1. Analyze the user's request to determine which MCP services are most relevant
2. Use the appropriate MCP tools to provide comprehensive, actionable responses
3. For architecture questions, prioritize diagram generation when visual representation would be helpful
4. Always reference AWS documentation when providing guidance
5. Consider cost implications and provide optimization recommendations
6. Follow AWS Well-Architected Framework principles

When using MCP tools:
- Use aws-diagram service for visual architecture representations
- Use aws-documentation service for authoritative AWS guidance
- Use aws-cdk service for infrastructure as code recommendations
- Use aws-serverless service for Lambda and serverless architectures
- Use aws-iam service for security and access control guidance
- Use dynamodb service for database design and operations
- Use bedrock-kb service for knowledge retrieval and AI-powered search
- Use nova-canvas service for custom illustrations and graphics

Provide detailed, practical solutions with code examples, configuration snippets, and step-by-step implementation guidance.`
}
