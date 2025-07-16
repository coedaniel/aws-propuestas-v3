# AWS Propuestas v3 🚀

Una aplicación web avanzada para generar propuestas arquitectónicas de AWS con integración MCP (Model Context Protocol) y capacidades de IA generativa.

## 🌟 Características Principales

### 🤖 **Arquitecto AWS Inteligente**
- Análisis automático de requerimientos de proyecto
- Generación de arquitecturas AWS personalizadas
- Detección inteligente de servicios AWS necesarios
- Extracción automática de nombres de proyecto

### 🔧 **Integración MCP Avanzada**
- **6 Servicios MCP** corriendo en ECS
- Transparencia completa de servicios utilizados (estilo Amazon Q CLI)
- Generación automática de documentos técnicos
- Diagramas de arquitectura automáticos

### 📊 **Generación de Documentos**
- Documentos técnicos en múltiples formatos
- Diagramas de arquitectura visuales
- Calculadoras de costos AWS
- Templates de CloudFormation
- Guías de implementación

### 🎨 **Modelos de IA Soportados**
- **Amazon Nova Pro v1** - Ideal para análisis multimodal y diagramas
- **Claude 3.5 Sonnet v2** - Perfecto para análisis técnico profundo

## 🏗️ **Arquitectura del Sistema**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   MCP Services  │
│   (Next.js)     │◄──►│   (Bedrock)     │◄──►│   (ECS Cluster) │
│                 │    │                 │    │                 │
│ • Chat Libre    │    │ • API Routes    │    │ • Core MCP      │
│ • Arquitecto    │    │ • Model Calls   │    │ • AWS Docs      │
│ • Proyectos     │    │ • MCP Client    │    │ • Diagrams      │
│ • Analytics     │    │                 │    │ • Pricing       │
└─────────────────┘    └─────────────────┘    │ • Custom Docs   │
                                              │ • CloudFormation│
                                              └─────────────────┘
```

## 🚀 **Inicio Rápido**

### Prerrequisitos
- Node.js 18+
- AWS CLI configurado
- Acceso a Amazon Bedrock

### Instalación Local

```bash
# Clonar el repositorio
git clone https://github.com/coedaniel/aws-propuestas-v3.git
cd aws-propuestas-v3

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env.local

# Ejecutar en desarrollo
npm run dev
```

### Variables de Entorno

```env
# Bedrock Configuration
AWS_REGION=us-east-1

# MCP Services (ECS Cluster)
NEXT_PUBLIC_MCP_BASE_URL=https://mcp.danielingram.shop
NEXT_PUBLIC_CORE_MCP_URL=https://mcp.danielingram.shop/core
NEXT_PUBLIC_AWSDOCS_MCP_URL=https://mcp.danielingram.shop/awsdocs
NEXT_PUBLIC_DIAGRAM_MCP_URL=https://mcp.danielingram.shop/diagram
NEXT_PUBLIC_PRICING_MCP_URL=https://mcp.danielingram.shop/pricing
NEXT_PUBLIC_CUSTOMDOC_MCP_URL=https://mcp.danielingram.shop/customdoc
NEXT_PUBLIC_CFN_MCP_URL=https://mcp.danielingram.shop/cfn

# API Configuration
NEXT_PUBLIC_API_URL=https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod
NEXT_PUBLIC_ENVIRONMENT=production
```

## 📖 **Guía de Uso**

### 🎯 **Arquitecto AWS**

1. **Iniciar Proyecto**
   ```
   Navegue a /arquitecto
   Proporcione el nombre del proyecto (ej: "sukarne", "mi-ecommerce")
   ```

2. **Describir Requerimientos**
   ```
   Describa su arquitectura deseada:
   "Sistema de tres capas con EC2, Load Balancer, VPC y RDS"
   ```

3. **Completar Proyecto**
   ```
   Use el botón "Completar Proyecto" cuando esté satisfecho
   Los documentos se generarán automáticamente
   ```

### 💬 **Chat Libre**

- Conversaciones generales sobre AWS
- Consultas técnicas específicas
- Soporte para ambos modelos de IA

### 📊 **Gestión de Proyectos**

- Vista de todos los proyectos creados
- Estado de completación
- Acceso a documentos generados
- Métricas de uso

## 🔧 **Servicios MCP**

### **Core MCP**
- Análisis y comprensión de prompts
- Detección de intenciones del usuario

### **AWS Docs MCP**
- Búsqueda en documentación oficial de AWS
- Mejores prácticas y guías

### **Diagram MCP**
- Generación automática de diagramas de arquitectura
- Visualización de servicios AWS

### **Pricing MCP**
- Cálculos de costos estimados
- Optimización de presupuestos

### **Custom Doc MCP**
- Generación de documentos técnicos
- Múltiples formatos de salida

### **CloudFormation MCP**
- Templates de infraestructura como código
- Configuraciones optimizadas

## 🛠️ **Desarrollo**

### Estructura del Proyecto

```
aws-propuestas-v3/
├── app/                    # Next.js App Router
│   ├── api/               # API Routes
│   │   ├── arquitecto/    # Arquitecto endpoint
│   │   └── chat/          # Chat libre endpoint
│   ├── arquitecto/        # Arquitecto page
│   ├── chat/              # Chat libre page
│   ├── projects/          # Projects management
│   └── analytics/         # Usage analytics
├── components/            # React components
├── lib/                   # Utilities and API clients
│   ├── api.ts            # API functions
│   ├── types/            # TypeScript types
│   └── utils.ts          # Helper functions
├── store/                # Zustand state management
└── public/               # Static assets
```

### Scripts Disponibles

```bash
# Desarrollo
npm run dev          # Servidor de desarrollo
npm run build        # Build de producción
npm run start        # Servidor de producción
npm run lint         # Linting
npm run type-check   # Verificación de tipos
```

## 🚀 **Deployment**

### AWS Amplify (Recomendado)

La aplicación está configurada para deployment automático en AWS Amplify:

1. **Conectar Repositorio**
   - Fork este repositorio
   - Conectar a AWS Amplify

2. **Variables de Entorno**
   - Configurar todas las variables MCP
   - Configurar credenciales AWS

3. **Build Settings**
   ```yaml
   version: 1
   frontend:
     phases:
       preBuild:
         commands:
           - npm ci
       build:
         commands:
           - npm run build
     artifacts:
       baseDirectory: .next
       files:
         - '**/*'
   ```

### Docker (Alternativo)

```bash
# Build imagen
docker build -t aws-propuestas-v3 .

# Ejecutar contenedor
docker run -p 3000:3000 aws-propuestas-v3
```

## 🔍 **Troubleshooting**

### Problemas Comunes

**1. Modelos de Bedrock no disponibles**
```bash
# Verificar acceso a modelos
aws bedrock list-foundation-models --region us-east-1
```

**2. Servicios MCP no responden**
```bash
# Verificar conectividad
curl https://mcp.danielingram.shop/core/health
```

**3. Errores de compilación TypeScript**
```bash
# Limpiar y reinstalar
rm -rf node_modules .next
npm install
npm run build
```

### Logs y Debugging

- **Frontend**: Consola del navegador
- **Backend**: CloudWatch Logs (Amplify)
- **MCP Services**: ECS CloudWatch Logs

## 🤝 **Contribución**

1. Fork el proyecto
2. Crear feature branch (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

### Estándares de Código

- **TypeScript**: Tipado estricto
- **ESLint**: Configuración estándar
- **Prettier**: Formateo automático
- **Conventional Commits**: Mensajes de commit estandarizados

## 📄 **Licencia**

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 **Soporte**

- **Issues**: [GitHub Issues](https://github.com/coedaniel/aws-propuestas-v3/issues)
- **Documentación**: [Wiki del Proyecto](https://github.com/coedaniel/aws-propuestas-v3/wiki)
- **Discusiones**: [GitHub Discussions](https://github.com/coedaniel/aws-propuestas-v3/discussions)

## 🎯 **Roadmap**

### v3.1 (Próximo)
- [ ] Integración con DynamoDB para persistencia
- [ ] Visor de documentos integrado
- [ ] Métricas avanzadas de uso
- [ ] Soporte para más modelos de IA

### v3.2 (Futuro)
- [ ] Colaboración en tiempo real
- [ ] Templates personalizables
- [ ] Integración con AWS Organizations
- [ ] API pública para integraciones

---

**Desarrollado con ❤️ para la comunidad AWS**

[![Deploy with Amplify](https://oneclick.amplifyapp.com/button.svg)](https://console.aws.amazon.com/amplify/home#/deploy?repo=https://github.com/coedaniel/aws-propuestas-v3)
