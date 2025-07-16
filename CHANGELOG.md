# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2024-12-16

### 🎉 Lanzamiento Inicial

#### Agregado
- **Arquitecto AWS Inteligente**
  - Análisis automático de requerimientos de proyecto
  - Generación de arquitecturas AWS personalizadas
  - Detección inteligente de servicios AWS necesarios
  - Extracción automática de nombres de proyecto con múltiples patrones regex

- **Integración MCP Completa**
  - 6 servicios MCP corriendo en ECS cluster
  - Transparencia completa de servicios utilizados (estilo Amazon Q CLI)
  - Generación automática de documentos técnicos
  - Diagramas de arquitectura automáticos

- **Modelos de IA Soportados**
  - Amazon Nova Pro v1 (`amazon.nova-pro-v1:0`)
  - Claude 3.5 Sonnet v2 (`anthropic.claude-3-5-sonnet-20241022-v2:0`)

- **Funcionalidades Core**
  - Chat libre para consultas generales de AWS
  - Gestión completa de proyectos
  - Analytics y métricas de uso
  - Generación de múltiples tipos de documentos

#### Servicios MCP Implementados
- **Core MCP**: Análisis y comprensión de prompts
- **AWS Docs MCP**: Búsqueda en documentación oficial
- **Diagram MCP**: Generación automática de diagramas
- **Pricing MCP**: Cálculos de costos estimados
- **Custom Doc MCP**: Generación de documentos técnicos
- **CloudFormation MCP**: Templates de infraestructura

#### Características Técnicas
- **Frontend**: Next.js 14 con App Router
- **Backend**: Amazon Bedrock integration
- **Estado**: Zustand para gestión de estado
- **Estilos**: Tailwind CSS con componentes personalizados
- **TypeScript**: Tipado estricto en toda la aplicación

#### Correcciones Implementadas
- Resolución de conflictos de interfaces TypeScript
- Configuración correcta de modelos Bedrock
- Manejo de encoding UTF-8 para contenido en español
- Extracción mejorada de nombres de proyecto
- Controles manuales de completación de proyecto
- Integración gradual de servicios MCP

### 🔧 Configuración y Deployment
- **AWS Amplify**: Configuración completa para deployment
- **Docker**: Soporte para contenedores
- **Environment Variables**: Configuración flexible para diferentes entornos
- **CI/CD**: Pipeline automatizado con GitHub Actions

### 📚 Documentación
- README completo con guías de uso
- Guía de contribución detallada
- Documentación de arquitectura
- Ejemplos de código y configuración

### 🛠️ Herramientas de Desarrollo
- ESLint y Prettier configurados
- Husky para git hooks
- Conventional commits
- TypeScript strict mode

---

## Próximas Versiones

### [3.1.0] - Planificado
- [ ] Integración con DynamoDB para persistencia
- [ ] Visor de documentos integrado
- [ ] Métricas avanzadas de uso
- [ ] Soporte para más modelos de IA

### [3.2.0] - Futuro
- [ ] Colaboración en tiempo real
- [ ] Templates personalizables
- [ ] Integración con AWS Organizations
- [ ] API pública para integraciones

---

## Notas de Migración

### Desde v2.x
- Actualizar variables de entorno para servicios MCP
- Revisar configuración de modelos Bedrock
- Actualizar dependencias de Node.js a v18+

### Configuración Requerida
```env
# Servicios MCP
NEXT_PUBLIC_MCP_BASE_URL=https://mcp.danielingram.shop
NEXT_PUBLIC_CORE_MCP_URL=https://mcp.danielingram.shop/core
# ... otros servicios MCP

# API Configuration
NEXT_PUBLIC_API_URL=https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod
```

---

## Contribuidores

- **Daniel Ingram** - Desarrollo principal y arquitectura
- **Comunidad AWS** - Feedback y testing

## Agradecimientos

- Amazon Web Services por Bedrock y servicios de IA
- Comunidad de desarrolladores por feedback y contribuciones
- Equipo de MCP por el protocolo y especificaciones
