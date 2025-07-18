# MCP Integration Guide - AWS Propuestas v3

## Overview

This document describes the Model Context Protocol (MCP) integration implemented in the AWS Propuestas v3 application. The integration provides enhanced capabilities for AWS architecture consulting through specialized MCP services.

## Architecture

### Components

1. **MCP Configuration (`lib/mcpConfig.ts`)**
   - Service definitions and detection patterns
   - Priority-based service selection
   - Enhanced system prompt generation

2. **MCP Integration Layer (`lib/mcpIntegration.ts`)**
   - Service routing and communication
   - Fallback mechanisms
   - Error handling

3. **Enhanced API Endpoints**
   - `/api/arquitecto` - MCP-enhanced architecture consulting
   - `/api/chat` - MCP fallback for legacy chat

4. **Frontend Integration (`lib/api.ts`)**
   - Automatic fallback to MCP services
   - Backward compatibility with legacy APIs

## Available MCP Services

### 1. AWS Diagram Service (`aws-diagram`)
- **Tools**: `generate_diagram`, `list_icons`, `get_diagram_examples`
- **Patterns**: diagram, architecture, visual, draw, chart, graph
- **Use Cases**: Generate AWS architecture diagrams, visual representations

### 2. AWS Documentation Service (`aws-documentation`)
- **Tools**: `search_documentation`, `read_documentation`, `recommend`
- **Patterns**: documentation, docs, guide, tutorial, reference
- **Use Cases**: Real-time AWS documentation lookup, best practices

### 3. AWS CDK Service (`aws-cdk`)
- **Tools**: `CDKGeneralGuidance`, `SearchGenAICDKConstructs`, `ExplainCDKNagRule`
- **Patterns**: cdk, infrastructure as code, iac, cloudformation
- **Use Cases**: Infrastructure as Code guidance, CDK constructs

### 4. AWS Serverless Service (`aws-serverless`)
- **Tools**: `sam_init`, `sam_build`, `sam_deploy`, `deploy_webapp`
- **Patterns**: serverless, lambda, sam, api gateway
- **Use Cases**: Serverless application development and deployment

### 5. AWS IAM Service (`aws-iam`)
- **Tools**: `list_users`, `create_user`, `attach_user_policy`
- **Patterns**: iam, security, permissions, policies, roles
- **Use Cases**: Identity and access management, security configuration

### 6. DynamoDB Service (`dynamodb`)
- **Tools**: `create_table`, `put_item`, `get_item`, `query`, `scan`
- **Patterns**: dynamodb, database, nosql, table
- **Use Cases**: Database operations and data modeling

### 7. Bedrock Knowledge Base Service (`bedrock-kb`)
- **Tools**: `ListKnowledgeBases`, `QueryKnowledgeBases`
- **Patterns**: knowledge base, bedrock, rag, retrieval
- **Use Cases**: AI-powered knowledge retrieval and search

### 8. Nova Canvas Service (`nova-canvas`)
- **Tools**: `generate_image`, `generate_image_with_colors`
- **Patterns**: image, generate image, nova canvas, picture
- **Use Cases**: Custom image and illustration generation

## How It Works

### 1. Service Detection
When a user sends a message, the system:
1. Analyzes the message content for MCP service patterns
2. Scores and ranks relevant services by relevance and priority
3. Selects the most appropriate services for the request

### 2. Enhanced System Prompt
Based on detected services, the system generates an enhanced prompt that:
- Includes service-specific capabilities
- Provides context about available tools
- Guides the AI to use appropriate MCP services

### 3. Response Enhancement
After generating the base response, the system:
- Checks if additional MCP services should be called
- Generates diagrams, documents, or other artifacts as needed
- Enriches the response with real-time AWS data

### 4. Fallback Mechanisms
The integration includes multiple fallback layers:
- Legacy API → MCP services → Error handling
- Service-specific fallbacks for each MCP service
- Graceful degradation when services are unavailable

## Usage Examples

### Architecture Consultation
```
User: "I need to design a serverless web application with user authentication"

System:
1. Detects: aws-serverless, aws-iam, aws-diagram services
2. Generates enhanced prompt with serverless and security guidance
3. Provides architecture recommendations
4. Optionally generates architecture diagram
5. Suggests IAM policies and roles
```

### Cost Optimization
```
User: "How can I optimize costs for my EC2 instances?"

System:
1. Detects: aws-documentation service
2. Searches real-time AWS documentation for cost optimization
3. Provides current best practices and recommendations
4. References latest AWS pricing and instance types
```

### Infrastructure as Code
```
User: "Generate CloudFormation template for a three-tier web application"

System:
1. Detects: aws-cdk service
2. Provides CDK guidance and best practices
3. Generates CloudFormation template
4. Includes security and monitoring configurations
```

## Configuration

### Environment Variables
```bash
# Enable MCP fallback in chat API
USE_MCP_FALLBACK=true

# MCP service endpoints (if using external MCP servers)
MCP_DIAGRAM_ENDPOINT=http://localhost:3001
MCP_DOCUMENTATION_ENDPOINT=http://localhost:3002
```

### Service Priority
Services are prioritized based on:
1. **Pattern Match Score**: Exact matches get higher scores
2. **Service Priority**: Lower numbers = higher priority
3. **Context Relevance**: Based on conversation history

## Error Handling

### Service Unavailability
- Graceful degradation to base AI capabilities
- Error logging for monitoring and debugging
- User-friendly error messages

### Partial Failures
- Continue with available services
- Log failed service calls
- Provide best-effort responses

## Monitoring and Debugging

### Logging
- Service detection results
- MCP service call success/failure
- Response enhancement status
- Performance metrics

### Debug Information
Response includes:
- `mcpServicesDetected`: List of detected services
- `mcpServicesUsed`: Services actually called
- `generatedFiles`: Additional artifacts created
- `awsDocumentation`: Real-time documentation data

## Future Enhancements

### Planned Features
1. **Cost Calculator Service**: Real-time AWS cost estimation
2. **Security Scanner Service**: Automated security assessments
3. **Performance Optimizer Service**: Performance recommendations
4. **Migration Planner Service**: Cloud migration guidance

### Integration Improvements
1. **Caching Layer**: Cache frequently accessed documentation
2. **Service Health Monitoring**: Real-time service status
3. **Load Balancing**: Distribute requests across MCP instances
4. **Analytics Dashboard**: Usage metrics and insights

## Troubleshooting

### Common Issues

1. **MCP Services Not Detected**
   - Check pattern matching in `mcpConfig.ts`
   - Verify service definitions are correct
   - Review message content for trigger words

2. **Service Calls Failing**
   - Check MCP server availability
   - Verify network connectivity
   - Review error logs for specific failures

3. **Fallback Not Working**
   - Ensure `USE_MCP_FALLBACK=true` is set
   - Check legacy API availability
   - Verify error handling logic

### Debug Steps
1. Check browser console for client-side errors
2. Review server logs for MCP service calls
3. Test individual MCP services directly
4. Verify configuration and environment variables

## Contributing

When adding new MCP services:
1. Define service configuration in `mcpConfig.ts`
2. Add detection patterns and tools
3. Update integration logic in `mcpIntegration.ts`
4. Test service detection and routing
5. Update documentation and examples

## Support

For issues related to MCP integration:
1. Check this documentation first
2. Review error logs and debug information
3. Test with individual MCP services
4. Contact the development team with specific error details
