# AWS Propuestas v3

Aplicación web para generar propuestas de arquitectura AWS utilizando servicios MCP (Model Composition Protocol).

## Características Principales

- **Chat Libre**: Interfaz de chat que permite utilizar dos modelos de IA diferentes:
  - Amazon Nova Pro v1: Ideal para análisis multimodal y diagramas
  - Claude 3.5 Sonnet v2: Perfecto para análisis técnico profundo

- **Arquitecto AWS**: Asistente especializado para diseñar arquitecturas AWS con:
  - Generación de diagramas de arquitectura
  - Creación de documentación técnica
  - Estimación de costos
  - Plantillas de CloudFormation

- **Integración MCP**: Utiliza servicios MCP para extender las capacidades:
  - `core-mcp`: Análisis básico y procesamiento de consultas
  - `diagram-mcp`: Generación de diagramas de arquitectura
  - `awsdocs-mcp`: Acceso a documentación oficial de AWS
  - `pricing-mcp`: Estimación de costos de servicios AWS
  - `cfn-mcp`: Generación de plantillas CloudFormation
  - `customdoc-mcp`: Creación de documentos personalizados

## Estructura del Proyecto

```
aws-propuestas-v3-github/
├── app/                    # Páginas de la aplicación (Next.js App Router)
│   ├── arquitecto/         # Página del Arquitecto AWS
│   ├── chat/               # Página de Chat Libre
│   └── projects/           # Página de gestión de proyectos
├── components/             # Componentes reutilizables
│   ├── mcp-transparency.tsx # Componentes de transparencia MCP
│   ├── project-status.tsx  # Componente de estado del proyecto
│   └── document-viewer.tsx # Visor de documentos generados
├── lib/                    # Utilidades y funciones
│   ├── api.ts              # Funciones de API
│   ├── mcpIntegration.ts   # Integración con servicios MCP
│   └── types/              # Tipos TypeScript
└── scripts/                # Scripts de utilidad
    └── cleanup.sh          # Script de limpieza
```

## Despliegue

La aplicación está desplegada en AWS Amplify con la siguiente URL:

```
https://main.d2xsphsjdxlk24.amplifyapp.com/
```

### Variables de Entorno

Las siguientes variables de entorno son necesarias para el funcionamiento de la aplicación:

```
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

## Desarrollo Local

1. Clonar el repositorio:
```bash
git clone https://github.com/username/aws-propuestas-v3-github.git
cd aws-propuestas-v3-github
```

2. Instalar dependencias:
```bash
npm install
```

3. Crear archivo `.env.local` con las variables de entorno necesarias.

4. Iniciar el servidor de desarrollo:
```bash
npm run dev
```

5. Abrir [http://localhost:3000](http://localhost:3000) en el navegador.

## Construcción para Producción

```bash
npm run build
```

## Licencia

Este proyecto está licenciado bajo la licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.
