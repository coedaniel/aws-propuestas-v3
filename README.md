# AWS Propuestas v3 🚀

Sistema conversacional profesional para generar propuestas ejecutivas de soluciones AWS con IA avanzada y arquitectura MCP (Model Context Protocol).

## 🌟 Características Principales

### 🎨 Interfaz Profesional
- **Diseño oscuro moderno** inspirado en AWS Transform
- **13 páginas completas** con navegación intuitiva
- **Responsive design** optimizado para desktop y móvil
- **Componentes UI avanzados** con shadcn/ui

### 🤖 Modelos IA de Última Generación
- **Amazon Nova Pro** - Modelo nativo AWS para arquitecturas complejas
- **Claude 3.5 Sonnet** - Razonamiento avanzado para proyectos enterprise
- **Meta Llama 3.2 90B** - El mejor modelo de Meta para análisis técnico
- **Claude 3.5 Sonnet v2** - La versión más avanzada para proyectos AWS

### 🔧 Arquitectura MCP Completa
- **6 servicios MCP** ejecutándose en ECS Fargate
- **Backend Lambda** con Smart MCP Handler
- **Integración completa** con servicios AWS
- **Análisis en tiempo real** de conversaciones

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend        │    │   MCP Services  │
│   Next.js 14    │◄──►│   Lambda         │◄──►│   ECS Fargate   │
│   Amplify       │    │   API Gateway    │    │   6 Services    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 🎯 Servicios MCP Activos
1. **Core MCP** - Funcionalidades básicas
2. **Pricing MCP** - Calculadora de costos AWS
3. **AWS Docs MCP** - Documentación oficial
4. **CFN MCP** - CloudFormation templates
5. **Diagram MCP** - Generación de diagramas
6. **DocGen MCP** - Generación de documentación

## 📱 Páginas Disponibles

### 🏠 Páginas Principales
- **Dashboard** (`/`) - Vista general del sistema
- **Chat Libre** (`/chat`) - Conversación con IA
- **Arquitecto IA** (`/arquitecto`) - Diseño de arquitecturas AWS
- **Proyectos** (`/projects`) - Gestión de proyectos
- **Analytics** (`/analytics`) - Métricas y análisis

### 🇪🇸 Páginas en Español
- **Analítica** (`/analitica`) - Dashboard de métricas
- **Conexiones** (`/conexiones`) - Estado de servicios
- **Errores** (`/errores`) - Logs y troubleshooting
- **Proyectos** (`/proyectos`) - Gestión simplificada

## ⚙️ Configuración Técnica

### 🌡️ Temperaturas Optimizadas para AWS
```typescript
export const AWS_TEMPERATURE_CONFIGS = {
  arquitecto: 0.3,        // Arquitecturas precisas
  documentacion: 0.4,     // Documentación técnica
  chat: 0.5,             // Conversaciones naturales
  analisis: 0.2,         // Análisis técnicos
  troubleshooting: 0.3,  // Solución de problemas
  default: 0.4           // Configuración por defecto
}
```

### 🧠 System Prompts Especializados
- **Arquitecto AWS Senior** - 10+ años experiencia, certificaciones Professional
- **Consultor AWS Expert** - Especialista en transformación digital
- **Technical Writer** - Documentación técnica especializada

## 🚀 Deployment

### 📦 Frontend (Amplify)
```bash
# Build local
npm run build

# Deploy automático via GitHub
git push origin main
```

### 🐳 Backend (ECS + Lambda)
```bash
# Actualizar servicios MCP
./update-all-mcp-services.sh

# Deploy Lambda
sam build && sam deploy
```

## 🔧 Desarrollo Local

### 📋 Prerrequisitos
- Node.js 18+
- AWS CLI configurado
- Docker (para servicios MCP)

### 🛠️ Instalación
```bash
# Clonar repositorio
git clone https://github.com/coedaniel/aws-propuestas-v3.git
cd aws-propuestas-v3

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.local.example .env.local

# Ejecutar en desarrollo
npm run dev
```

### 🌐 Variables de Entorno
```env
NEXT_PUBLIC_API_URL=https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod
NEXT_PUBLIC_MCP_BASE_URL=https://mcp.danielingram.shop
NEXT_PUBLIC_CORE_MCP_URL=https://mcp.danielingram.shop/core
NEXT_PUBLIC_PRICING_MCP_URL=https://mcp.danielingram.shop/pricing
NEXT_PUBLIC_AWSDOCS_MCP_URL=https://mcp.danielingram.shop/awsdocs
NEXT_PUBLIC_CFN_MCP_URL=https://mcp.danielingram.shop/cfn
NEXT_PUBLIC_DIAGRAM_MCP_URL=https://mcp.danielingram.shop/diagram
NEXT_PUBLIC_DOCGEN_MCP_URL=https://mcp.danielingram.shop/docgen
```

## 📊 Métricas y Monitoreo

### 🎯 KPIs del Sistema
- **Tiempo de respuesta** < 2s promedio
- **Disponibilidad** 99.9% uptime
- **Uso de tokens** optimizado por modelo
- **Eficiencia MCP** > 85%

### 📈 Analytics Disponibles
- Uso por modelo de IA
- Patrones de conversación
- Rendimiento de servicios MCP
- Costos por sesión

## 🔒 Seguridad

### 🛡️ Medidas Implementadas
- **IAM roles** con permisos mínimos
- **API Gateway** con throttling
- **VPC** para servicios MCP
- **Secrets Manager** para credenciales
- **CloudWatch** para monitoreo

## 📚 Documentación Adicional

- [Guía de Arquitectura](./ARCHITECTURE.md)
- [API Reference](./API.md)
- [Guía de Deployment](./DEPLOYMENT.md)
- [Troubleshooting](./TROUBLESHOOTING.md)
- [Integración MCP](./MCP_INTEGRATION_GUIDE.md)

## 🤝 Contribución

1. Fork el repositorio
2. Crear branch feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](./LICENSE) para más detalles.

## 🌐 Enlaces

- **Aplicación**: https://d2xsphsjdxlk24.amplifyapp.com
- **Repositorio**: https://github.com/coedaniel/aws-propuestas-v3
- **Documentación**: [Wiki del proyecto](https://github.com/coedaniel/aws-propuestas-v3/wiki)

---

**Desarrollado con ❤️ para la comunidad AWS**

*Sistema profesional de propuestas AWS con IA avanzada y arquitectura MCP*
