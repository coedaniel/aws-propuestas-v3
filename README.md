# AWS Propuestas V3

Sistema conversacional profesional para generar propuestas ejecutivas de soluciones AWS con IA.

## 🏗️ Arquitectura

- **Frontend**: Next.js desplegado en AWS Amplify
- **Backend**: Servidores MCP en AWS ECS (sin Lambdas)
- **Dominio**: https://main.d2xsphsjdxlk24.amplifyapp.com

## 🚀 Servicios MCP

Los siguientes servidores MCP están desplegados en ECS:

- **Core MCP**: Funcionalidades principales
- **AWS Docs MCP**: Documentación de AWS  
- **Diagram MCP**: Generación de diagramas
- **Pricing MCP**: Cálculos de costos
- **CloudFormation MCP**: Plantillas de infraestructura
- **Custom Doc MCP**: Documentación personalizada

**URL Base**: https://mcp.danielingram.shop

## 📁 Estructura del Proyecto

```
├── app/                    # Frontend Next.js (Amplify)
├── components/             # Componentes React
├── lib/                    # Utilidades y tipos
├── store/                  # Estado global (Zustand)
├── official-mcp-servers/   # Servidores MCP
└── scripts/               # Scripts de despliegue
```

## 🛠️ Despliegue

- **Frontend**: Automático via Amplify (conectado a este repo)
- **MCP Servers**: Desplegados en ECS via Docker

## 🌐 URLs

- **Frontend**: https://main.d2xsphsjdxlk24.amplifyapp.com
- **System Status**: https://main.d2xsphsjdxlk24.amplifyapp.com/system-status
- **MCP Services**: https://mcp.danielingram.shop/{service}

## 📊 Estado

✅ **Activo y funcionando**
- Frontend desplegado en Amplify
- 6 servicios MCP funcionando en ECS
- CORS configurado correctamente
- Health checks operativos
