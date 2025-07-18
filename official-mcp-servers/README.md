# 🐳 Servidores MCP Oficiales

Este directorio contiene los servidores MCP (Model Context Protocol) que forman el backend del sistema AWS Propuestas V3.

## 🏗️ Arquitectura MCP

Los servidores MCP están desplegados en **Amazon ECS** y proporcionan funcionalidades especializadas a través de HTTP endpoints.

## 📦 Servicios Disponibles

### 🧠 Core MCP Server
- **Puerto**: 8000
- **Función**: Funcionalidades principales del sistema
- **Endpoint**: https://mcp.danielingram.shop/core

### 📖 AWS Documentation MCP
- **Puerto**: 8001  
- **Función**: Acceso a documentación oficial de AWS
- **Endpoint**: https://mcp.danielingram.shop/aws-docs

### 📊 Diagram Generator MCP
- **Puerto**: 8002
- **Función**: Generación de diagramas de arquitectura AWS
- **Endpoint**: https://mcp.danielingram.shop/diagram

### 💰 Pricing Calculator MCP
- **Puerto**: 8003
- **Función**: Cálculos de costos y estimaciones AWS
- **Endpoint**: https://mcp.danielingram.shop/pricing

### ☁️ CloudFormation MCP
- **Puerto**: 8004
- **Función**: Generación de templates CloudFormation
- **Endpoint**: https://mcp.danielingram.shop/cloudformation

### 📝 Custom Documentation MCP
- **Puerto**: 8005
- **Función**: Generación de documentación personalizada
- **Endpoint**: https://mcp.danielingram.shop/custom-doc

## 🔧 Configuración

Cada servidor MCP incluye:
- **Dockerfile** - Configuración de contenedor
- **requirements.txt** - Dependencias Python
- **Código fuente** - Lógica específica del servicio
- **Health checks** - Monitoreo de estado

## 🚀 Despliegue

Los servidores se despliegan automáticamente en ECS usando:
```bash
./scripts/deploy-mcp-servers.sh
```

## 🔍 Monitoreo

- **Health Checks**: Cada servicio expone `/health`
- **Logs**: Disponibles en CloudWatch
- **Métricas**: Monitoreadas via ECS

## 🌐 CORS

Todos los servicios están configurados con CORS para permitir requests desde:
- https://main.d2xsphsjdxlk24.amplifyapp.com
- http://localhost:3000 (desarrollo)

## 📊 Estado Actual

✅ **Todos los servicios operativos**
- ✅ Desplegados en ECS
- ✅ Health checks pasando
- ✅ CORS configurado
- ✅ Integración con frontend funcionando

---

**🚀 Arquitectura MCP moderna y escalable**
