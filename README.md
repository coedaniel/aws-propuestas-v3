# AWS Propuestas v3 - Plataforma de Arquitectura Inteligente

Sistema profesional de generación automática de propuestas técnicas AWS utilizando inteligencia artificial y servicios MCP (Model Context Protocol).

## 🚀 Estado del Sistema - ACTUALIZADO

✅ **PRODUCCIÓN** - Sistema completamente funcional  
🌐 **URL**: https://main.d2xsphsjdxlk24.amplifyapp.com/  
🤖 **Arquitecto IA**: https://main.d2xsphsjdxlk24.amplifyapp.com/arquitecto/
💬 **Chat Libre**: https://main.d2xsphsjdxlk24.amplifyapp.com/chat/

## 🆕 Nuevas Características v3.0

### **Frontend Profesional Completo**
- ✅ **Diseño Dark Mode**: Interfaz profesional estilo AWS Transform
- ✅ **4 Páginas Principales**: Chat, Arquitecto, Proyectos, Analítica
- ✅ **Navegación Lateral**: Layout profesional con sidebar responsive
- ✅ **Prompt Understanding**: Análisis en tiempo real de conversaciones
- ✅ **Estado de Conexiones**: Monitoreo de todos los servicios
- ✅ **Logs y Errores**: Sistema completo de diagnóstico

### **Páginas Implementadas**

#### 1. **Dashboard Principal** (`/`)
- Resumen ejecutivo del sistema
- Métricas en tiempo real
- Accesos rápidos a todas las funciones
- Estado de servicios y MCPs

#### 2. **Chat Libre** (`/chat`)
- Conversación libre con modelos Bedrock
- Selector de modelos (Nova Pro, Claude 3.5 Sonnet, Claude 4)
- Análisis de prompt en sidebar
- Exportación de conversaciones
- Historial y gestión de mensajes

#### 3. **Arquitecto IA** (`/arquitecto`)
- Generación guiada de propuestas arquitectónicas
- Flujo paso a paso para proyectos
- Integración automática con MCPs
- Generación de documentos profesionales
- Seguimiento de fases del proyecto

#### 4. **Proyectos** (`/proyectos`)
- Gestión completa de proyectos generados
- Vista de archivos por proyecto
- Descarga directa de documentos
- Filtros y búsqueda avanzada
- Integración con S3 para almacenamiento

#### 5. **Analítica** (`/analitica`)
- Dashboard de métricas y estadísticas
- Gráficas de uso de MCPs
- Análisis de costos por modelo
- Top 5 soluciones más solicitadas
- Métricas de rendimiento del sistema

#### 6. **Conexiones** (`/conexiones`)
- Monitoreo en tiempo real de servicios
- Health checks automáticos
- Estado de 6 servicios MCP
- Diagnóstico de conectividad
- Información de latencia y disponibilidad

#### 7. **Errores** (`/errores`)
- Sistema completo de logging
- Categorización de errores
- Filtros avanzados por tipo y estado
- Exportación de logs a CSV
- Stack traces detallados

## 🏗️ Arquitectura Técnica

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Load Balancer  │    │   ECS Services  │
│   (Amplify)     │───▶│   (ALB)          │───▶│   (6 MCP Servers)│
│   Next.js 14    │    │   Target Groups  │    │   Official MCP  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AI Models     │    │   API Gateway    │    │   Storage       │
│   Nova Pro v1.0 │◀───│   REST API       │───▶│   DynamoDB      │
│   Claude 3.5 v2 │    │   /chat          │    │   S3 Bucket     │
│   Claude 4      │    │   /arquitecto    │    │   CloudWatch    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Componentes Principales

- **Frontend**: Next.js 14 con App Router, Tailwind CSS, Zustand
- **Backend**: 6 servicios MCP en ECS + API Gateway + Lambda
- **AI**: Amazon Bedrock (Nova Pro, Claude 3.5 Sonnet v2, Claude 4)
- **Storage**: DynamoDB + S3 + CloudWatch Logs
- **Hosting**: AWS Amplify con despliegue automático

## 🤖 Modelos de IA Disponibles

### Amazon Nova Pro v1.0
- **ID**: `amazon.nova-pro-v1:0`
- **Uso**: Análisis multimodal y diagramas
- **API**: `converse` (formato estándar)
- **Estado**: ✅ Funcionando

### Claude 3.5 Sonnet v2
- **ID**: `anthropic.claude-3-5-sonnet-20241022-v2:0`
- **Uso**: Análisis técnico profundo y documentación
- **API**: `converse` (formato estándar)
- **Estado**: ✅ Funcionando

### Claude 4 (Cross-Region)
- **ID**: `anthropic.claude-sonnet-4-20250514-v1:0`
- **Uso**: Capacidades avanzadas de razonamiento
- **API**: `converse` con inference profiles
- **Estado**: ✅ Disponible

## 🛠️ Servicios MCP Activos

Los servicios MCP se invocan automáticamente cuando el modelo los necesita:

1. **Core MCP** (puerto 8000): Chat principal y coordinación
2. **Pricing MCP** (puerto 8001): Cálculos de costos AWS
3. **AWS Docs MCP** (puerto 8002): Documentación oficial AWS
4. **CloudFormation MCP** (puerto 8003): Generación de templates IaC
5. **Diagram MCP** (puerto 8004): Diagramas de arquitectura
6. **Document Generator MCP** (puerto 8005): Generación de documentos

## 📋 Funcionalidades Principales

### Chat del Arquitecto
- Conversación inteligente con modelos de IA
- Detección automática de servicios AWS necesarios
- Generación de propuestas técnicas profesionales
- Invocación inteligente de servicios MCP
- Flujo guiado paso a paso

### Generación de Documentos
- Propuestas técnicas en formato TXT/Word
- Planes de actividades en CSV/Excel
- Estimaciones de costos detalladas
- Guías para AWS Calculator
- Diagramas de arquitectura (SVG/PNG)
- Scripts CloudFormation (YAML)

### Gestión de Proyectos
- Almacenamiento en DynamoDB
- Seguimiento de estado de proyectos
- Historial de conversaciones
- Archivos generados en S3
- Descarga directa de documentos

### Monitoreo y Diagnóstico
- Health checks automáticos
- Métricas de uso en tiempo real
- Sistema de logging completo
- Análisis de costos por modelo
- Estadísticas de uso de MCPs

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
NEXT_PUBLIC_CORE_MCP_URL=https://mcp.danielingram.shop/core
NEXT_PUBLIC_PRICING_MCP_URL=https://mcp.danielingram.shop/pricing
NEXT_PUBLIC_AWSDOCS_MCP_URL=https://mcp.danielingram.shop/awsdocs
NEXT_PUBLIC_CFN_MCP_URL=https://mcp.danielingram.shop/cfn
NEXT_PUBLIC_DIAGRAM_MCP_URL=https://mcp.danielingram.shop/diagram
NEXT_PUBLIC_DOCGEN_MCP_URL=https://mcp.danielingram.shop/docgen
NEXT_PUBLIC_ENVIRONMENT=prod
NEXT_PUBLIC_REGION=us-east-1
```

## 📚 Documentación Técnica

- [**ARCHITECTURE.md**](./ARCHITECTURE.md) - Arquitectura detallada del sistema
- [**API.md**](./API.md) - Documentación de endpoints y APIs
- [**DEPLOYMENT.md**](./DEPLOYMENT.md) - Guía de despliegue
- [**TROUBLESHOOTING.md**](./TROUBLESHOOTING.md) - Solución de problemas
- [**MCP_INTEGRATION_GUIDE.md**](./MCP_INTEGRATION_GUIDE.md) - Integración con MCP

## 🔍 Monitoreo y Estado

### Health Checks
- **Frontend**: https://main.d2xsphsjdxlk24.amplifyapp.com/conexiones
- **API**: https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod/health
- **MCP Services**: Verificación automática en página de conexiones

### Logs y Métricas
- **Amplify**: Console de AWS Amplify
- **Lambda**: CloudWatch Logs `/aws/lambda/aws-propuestas-v3-arquitecto-prod`
- **ECS**: CloudWatch Logs grupos por servicio MCP
- **Frontend**: Página `/errores` para logs del sistema

## 🎯 Casos de Uso

### Para Arquitectos de Soluciones
- Generación rápida de propuestas técnicas
- Documentación automática de arquitecturas
- Cálculo de costos y estimaciones
- Diagramas profesionales automáticos

### Para Consultores
- Propuestas ejecutivas personalizadas
- Planes de actividades detallados
- Scripts de implementación (CloudFormation)
- Documentación lista para cliente

### Para Equipos de Desarrollo
- Arquitecturas serverless y microservicios
- Mejores prácticas de AWS integradas
- Validación automática de diseños
- Integración con herramientas existentes

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
- **Estado del Sistema**: https://main.d2xsphsjdxlk24.amplifyapp.com/conexiones
- **Logs del Sistema**: https://main.d2xsphsjdxlk24.amplifyapp.com/errores

---

**Última actualización**: 2025-01-19  
**Versión**: 3.0.0  
**Estado**: ✅ Producción Estable con Frontend Profesional Completo
