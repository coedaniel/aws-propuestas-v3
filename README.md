# 🚀 AWS Propuestas V3

> Sistema conversacional profesional para generar propuestas ejecutivas de soluciones AWS con IA

[![Amplify Status](https://img.shields.io/badge/Amplify-Deployed-success)](https://main.d2xsphsjdxlk24.amplifyapp.com)
[![MCP Services](https://img.shields.io/badge/MCP-6%20Services-blue)](https://mcp.danielingram.shop)
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)

## ✨ Características Principales

- **🤖 IA Conversacional**: Integración con Amazon Bedrock para generación inteligente
- **📊 Diagramas Automáticos**: Creación de arquitecturas AWS visuales
- **📚 Documentación AWS**: Acceso en tiempo real a documentación oficial
- **💰 Análisis de Costos**: Estimaciones precisas de precios AWS
- **🔧 CloudFormation**: Generación automática de templates IaC
- **📝 Documentación Custom**: Generación de documentación técnica personalizada

## 🏗️ Arquitectura Moderna

### Frontend (Next.js + Amplify)
```
🌐 AWS Amplify
├── Next.js 14 + TypeScript
├── Tailwind CSS + shadcn/ui
├── Zustand (Estado Global)
└── Componentes Reutilizables
```

### Backend (MCP Servers en ECS)
```
🐳 Amazon ECS
├── 🧠 Core MCP Server
├── 📖 AWS Documentation MCP
├── 📊 Diagram Generator MCP
├── 💰 Pricing Calculator MCP
├── ☁️ CloudFormation MCP
└── 📝 Custom Documentation MCP
```

## 🚀 URLs de Producción

- **🌐 Frontend**: https://main.d2xsphsjdxlk24.amplifyapp.com
- **📊 System Status**: https://main.d2xsphsjdxlk24.amplifyapp.com/system-status
- **🔧 MCP Services**: https://mcp.danielingram.shop

## 📁 Estructura del Proyecto

```
aws-propuestas-v3/
├── app/                    # 🎯 Frontend Next.js (Amplify)
├── components/             # 🧩 Componentes React
├── lib/                    # 🛠️ Utilidades y tipos
├── store/                  # 📦 Estado global (Zustand)
├── official-mcp-servers/   # 🐳 Servidores MCP
├── infrastructure/         # ☁️ Configuración AWS
├── docs/                   # 📚 Documentación adicional
└── scripts/               # 🔧 Scripts de utilidad
```

## 🛠️ Desarrollo Local

```bash
# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.local.example .env.local

# Ejecutar en desarrollo
npm run dev

# Abrir en el navegador
open http://localhost:3000
```

## 🚀 Despliegue

- **Frontend**: Automático via AWS Amplify (conectado a este repositorio)
- **MCP Servers**: Desplegados en Amazon ECS via Docker
- **CORS**: Configurado correctamente para integración frontend-backend

## 📚 Documentación Completa

| Documento | Descripción |
|-----------|-------------|
| [🏗️ Arquitectura](./ARCHITECTURE.md) | Diseño detallado del sistema |
| [🔌 API](./API.md) | Endpoints y servicios MCP |
| [🚀 Despliegue](./DEPLOYMENT.md) | Guía completa de deployment |
| [🤝 Contribución](./CONTRIBUTING.md) | Cómo contribuir al proyecto |
| [🔧 Troubleshooting](./TROUBLESHOOTING.md) | Solución de problemas comunes |

## 📊 Estado del Sistema

✅ **Sistema Completamente Operativo**
- ✅ Frontend desplegado y funcionando en Amplify
- ✅ 6 servicios MCP activos en ECS
- ✅ CORS configurado correctamente
- ✅ Health checks operativos
- ✅ Migración completa a arquitectura MCP (sin Lambdas)

## 🎯 Migración Completada

Este proyecto ha migrado exitosamente de una arquitectura basada en Lambda a una arquitectura moderna basada en **MCP (Model Context Protocol)**, ofreciendo:

- 🚀 **Mayor rendimiento** y escalabilidad
- 🔧 **Mejor mantenibilidad** del código
- 💰 **Optimización de costos** AWS
- 🛡️ **Mayor seguridad** y control

---

**Desarrollado con ❤️ para la comunidad AWS**
