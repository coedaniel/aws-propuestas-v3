import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { messages, modelId } = body

    const lastMessage = messages[messages.length - 1]?.content || ''
    
    // Simular respuesta inteligente basada en el contenido
    let response = ''
    
    if (lastMessage.toLowerCase().includes('aws')) {
      response = `Excelente pregunta sobre AWS. Te puedo ayudar con:

• **Servicios de Compute**: Lambda, EC2, ECS, Fargate
• **Bases de datos**: DynamoDB, RDS, Aurora
• **Almacenamiento**: S3, EFS, EBS
• **Redes**: VPC, CloudFront, Route 53
• **Seguridad**: IAM, Cognito, KMS
• **AI/ML**: Bedrock, SageMaker, Rekognition

¿Sobre qué servicio específico te gustaría saber más?`
    } else if (lastMessage.toLowerCase().includes('arquitectura')) {
      response = `Para diseñar una arquitectura AWS efectiva, consideremos:

🏗️ **Patrones Arquitectónicos**:
- Serverless (Lambda + API Gateway + DynamoDB)
- Microservicios (ECS/EKS + ALB + RDS)
- Event-driven (EventBridge + SQS + Lambda)

📊 **Principios del Well-Architected Framework**:
1. Excelencia operacional
2. Seguridad
3. Confiabilidad
4. Eficiencia de rendimiento
5. Optimización de costos

¿Qué tipo de aplicación estás planeando construir?`
    } else if (lastMessage.toLowerCase().includes('costo')) {
      response = `Para optimizar costos en AWS:

💰 **Estrategias de Ahorro**:
- Reserved Instances para cargas predecibles
- Spot Instances para workloads flexibles
- Auto Scaling para ajustar recursos
- S3 Intelligent Tiering para almacenamiento

📈 **Herramientas de Monitoreo**:
- AWS Cost Explorer
- AWS Budgets
- Cost Anomaly Detection
- Trusted Advisor

¿Necesitas ayuda con algún servicio específico para reducir costos?`
    } else {
      response = `Hola! Soy tu asistente AWS especializado. Puedo ayudarte con:

🔧 **Servicios AWS**: Configuración y mejores prácticas
🏗️ **Arquitecturas**: Diseño de soluciones escalables
💰 **Costos**: Optimización y análisis de gastos
🔒 **Seguridad**: Implementación de controles
📊 **Monitoreo**: CloudWatch y observabilidad

¿En qué puedo ayudarte hoy?`
    }

    const apiResponse = {
      response,
      modelId: modelId || 'amazon.nova-pro-v1:0',
      mode: 'chat',
      mcpServicesUsed: ['core'],
      usage: {
        inputTokens: lastMessage.length,
        outputTokens: response.length,
        totalTokens: lastMessage.length + response.length
      }
    }

    return NextResponse.json(apiResponse)
  } catch (error) {
    console.error('Error in chat API:', error)
    return NextResponse.json(
      { error: 'Error interno del servidor' },
      { status: 500 }
    )
  }
}
