# 🔧 Scripts de Utilidad

Este directorio contiene scripts para el mantenimiento y despliegue del sistema AWS Propuestas V3.

## 📋 Scripts Disponibles

### 🚀 Despliegue
- **`deploy-mcp-servers.sh`** - Despliega los servidores MCP en ECS
- **`deploy-frontend.sh`** - Despliega el frontend en Amplify
- **`build-and-push-images.sh`** - Construye y sube imágenes Docker a ECR

### 🔍 Monitoreo y Testing
- **`check-deployment.sh`** - Verifica el estado de los despliegues
- **`test-mcp-connectivity.js`** - Prueba la conectividad de los servicios MCP
- **`test-mcp-connectivity-fixed.js`** - Versión mejorada del test de conectividad
- **`test-frontend-integration.js`** - Prueba la integración frontend-backend

### 🛠️ Mantenimiento
- **`update-mcp-servers.sh`** - Actualiza los servidores MCP
- **`update-ecs-services.sh`** - Actualiza los servicios ECS
- **`update-dockerfiles.sh`** - Actualiza los Dockerfiles
- **`update-dockerfiles-fixed.sh`** - Versión corregida del actualizador

### 🏠 Desarrollo Local
- **`setup-local-code-doc-gen.sh`** - Configura el entorno local para generación de documentación

## 🚨 Importante

⚠️ **Estos scripts están configurados para el entorno de producción actual**
- Frontend: AWS Amplify
- Backend: Amazon ECS
- Dominio: mcp.danielingram.shop

## 📝 Uso

```bash
# Hacer ejecutable (si es necesario)
chmod +x scripts/*.sh

# Ejecutar un script
./scripts/deploy-mcp-servers.sh
```

## 🔐 Requisitos

- AWS CLI configurado
- Docker instalado
- Permisos apropiados en AWS
- Variables de entorno configuradas

---

**⚡ Scripts optimizados para la arquitectura MCP moderna**
