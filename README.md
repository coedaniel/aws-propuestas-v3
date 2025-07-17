# AWS Propuestas v3 - Sistema de Arquitectura Inteligente

Sistema profesional de generación automática de propuestas técnicas AWS utilizando inteligencia artificial y servicios MCP (Model Context Protocol).

## 🚀 Estado del Sistema

✅ **PRODUCCIÓN** - Sistema completamente funcional  
🌐 **URL**: https://main.d2xsphsjdxlk24.amplifyapp.com/  
🤖 **Chat Arquitecto**: https://main.d2xsphsjdxlk24.amplifyapp.com/arquitecto/

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Load Balancer  │    │   ECS Services  │
│   (Amplify)     │───▶│   (ALB)          │───▶│   (MCP Servers) │
│   Next.js       │    │   Target Groups  │    │   Official MCP  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AI Models     │    │   API Gateway    │    │   Storage       │
│   Nova Pro      │◀───│   REST API       │───▶│   DynamoDB      │
│   Claude Sonnet │    │   /arquitecto    │    │   S3 Bucket     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Componentes Principales

- **Frontend**: Next.js en AWS Amplify (SSG)
- **Backend**: ECS Services con MCP Servers oficiales
- **AI**: Amazon Bedrock (Nova Pro + Claude 3.5 Sonnet)
- **Storage**: DynamoDB + S3
- **API**: API Gateway + Lambda (solo para chat arquitecto)

## 🤖 Modelos de IA Disponibles

### Amazon Nova Pro v1.0
- **ID**: `amazon.nova-pro-v1:0`
- **Uso**: Análisis técnico y documentación
- **API**: `invoke_model` (formato específico)
- **Estado**: ✅ Funcionando

### Claude 3.5 Sonnet v1
- **ID**: `anthropic.claude-3-5-sonnet-20240620-v1:0`
- **Uso**: Análisis profundo y documentación detallada
- **API**: `converse` (formato estándar)
- **Estado**: ✅ Funcionando

## 🛠️ Servicios MCP

Los servicios MCP se invocan automáticamente cuando el modelo los necesita:

- **Core MCP** (puerto 8000): Chat principal y coordinación
- **Pricing MCP** (puerto 8001): Cálculos de costos AWS
- **AWS Docs MCP** (puerto 8002): Documentación oficial AWS
- **CloudFormation MCP** (puerto 8003): Generación de templates IaC
- **Diagram MCP** (puerto 8004): Diagramas de arquitectura
- **Document Generator MCP** (puerto 8005): Generación de documentos

## 📋 Funcionalidades

### Chat del Arquitecto
- Conversación inteligente con modelos de IA
- Detección automática de servicios AWS necesarios
- Generación de propuestas técnicas profesionales
- Invocación inteligente de servicios MCP

### Generación de Documentos
- Propuestas técnicas en formato TXT
- Planes de actividades en CSV
- Estimaciones de costos en CSV
- Guías para AWS Calculator
- Diagramas de arquitectura (SVG/PNG)

### Gestión de Proyectos
- Almacenamiento en DynamoDB
- Seguimiento de estado de proyectos
- Historial de conversaciones
- Archivos generados en S3

## 🚀 Desarrollo Local

### Prerrequisitos
```bash
node >= 18.0.0
npm >= 8.0.0
```

### Instalación
```bash
git clone https://github.com/coedaniel/aws-propuestas-v3.git
cd aws-propuestas-v3
npm install
```

### Variables de Entorno
```bash
cp .env.example .env.local
# Configurar variables según .env.local.example
```

### Ejecutar en Desarrollo
```bash
npm run dev
# Aplicación disponible en http://localhost:3000
```

## 🔧 Configuración de Producción

### AWS Amplify
- **Hosting**: Amplify con Next.js SSG
- **Build**: `npm run build`
- **Deploy**: Automático desde GitHub main branch

### Variables de Entorno Requeridas
```
NEXT_PUBLIC_API_URL=https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod
NEXT_PUBLIC_MCP_CORE_URL=http://aws-propuestas-v3-alb-prod-297472567.us-east-1.elb.amazonaws.com:8000
NEXT_PUBLIC_MCP_PRICING_URL=http://aws-propuestas-v3-alb-prod-297472567.us-east-1.elb.amazonaws.com:8001
NEXT_PUBLIC_MCP_AWSDOCS_URL=http://aws-propuestas-v3-alb-prod-297472567.us-east-1.elb.amazonaws.com:8002
NEXT_PUBLIC_MCP_CFN_URL=http://aws-propuestas-v3-alb-prod-297472567.us-east-1.elb.amazonaws.com:8003
NEXT_PUBLIC_MCP_DIAGRAM_URL=http://aws-propuestas-v3-alb-prod-297472567.us-east-1.elb.amazonaws.com:8004
NEXT_PUBLIC_MCP_CUSTOMDOC_URL=http://aws-propuestas-v3-alb-prod-297472567.us-east-1.elb.amazonaws.com:8005
```

## 📚 Documentación Técnica

- [**ARCHITECTURE.md**](./ARCHITECTURE.md) - Arquitectura detallada del sistema
- [**API.md**](./API.md) - Documentación de endpoints y APIs
- [**DEPLOYMENT.md**](./DEPLOYMENT.md) - Guía de despliegue
- [**TROUBLESHOOTING.md**](./TROUBLESHOOTING.md) - Solución de problemas
- [**MCP_INTEGRATION_GUIDE.md**](./MCP_INTEGRATION_GUIDE.md) - Integración con MCP

## 🔍 Monitoreo y Estado

### Health Checks
- **Frontend**: https://main.d2xsphsjdxlk24.amplifyapp.com/system-status
- **API**: https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod/health
- **MCP Services**: Verificación automática en system-status

### Logs
- **Amplify**: Console de AWS Amplify
- **Lambda**: CloudWatch Logs `/aws/lambda/aws-propuestas-v3-arquitecto-prod`
- **ECS**: CloudWatch Logs grupos por servicio

## 🤝 Contribución

1. Fork del repositorio
2. Crear branch para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

## 📞 Soporte

Para soporte técnico o preguntas:
- **Issues**: GitHub Issues
- **Documentación**: Ver archivos MD en el repositorio
- **Estado del Sistema**: https://main.d2xsphsjdxlk24.amplifyapp.com/system-status

---

**Última actualización**: 2025-07-17  
**Versión**: 3.0.0  
**Estado**: ✅ Producción Estable
