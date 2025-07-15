# 🏗️ Infrastructure - CloudFormation Templates

Esta carpeta contiene todos los templates de CloudFormation para desplegar la infraestructura de AWS Propuestas V3.

## 📋 **Templates Disponibles**

### 🚀 **Producción Activa**

#### `official-mcp-servers.yaml`
**Stack Principal de Servicios MCP**
- **Stack Name**: `aws-propuestas-v3-mcp-servers`
- **Estado**: ✅ CREATE_COMPLETE
- **Descripción**: Infraestructura completa de servicios MCP en ECS

**⚠️ CRÍTICO: NO ELIMINAR - Stack en producción activa**

**Recursos Desplegados:**
- ECS Cluster con Fargate
- VPC con subnets públicas  
- Application Load Balancer
- 6 Servicios MCP oficiales

**URLs de Servicios:**
- Base URL: `https://mcp.danielingram.shop`
- Frontend: `https://main.d2xsphsjdxlk24.amplifyapp.com`

#### `ecs-mcp-servers.yaml`
**Template de Infraestructura ECS Base**
- Configuración de VPC y networking
- ECS Cluster con capacidad mixta
- Security Groups y Load Balancer

#### `template.yaml`
**Template SAM para desarrollo local**
- Configuración para testing local
- Lambda functions de prueba

## 🎯 **Arquitectura Actual**

```
Frontend (Amplify) ←→ MCP Services (ECS)
├── 🧠 Core MCP (Port 8001)
├── 📖 AWS Docs MCP (Port 8002)  
├── 📊 CDK MCP (Port 8003)
├── 💰 Cost Analysis MCP (Port 8004)
├── 🎨 Diagram MCP (Port 8006)
└── 🤖 Bedrock Data MCP (Port 8007)
```

## 🔒 **Stacks PROTEGIDOS (NO TOCAR)**

### ✅ Stacks en Producción
- `aws-propuestas-v3-mcp-servers` - **CRÍTICO**
- `aws-propuestas-v3-prod` - **CRÍTICO** 
- `bedrock-chat-iam` - **NECESARIO**
- `aws-sam-cli-managed-default` - **ÚTIL**

## 🧹 **Stacks Seguros para Limpiar**

### 🔴 Stack Problemático
- `bedrock-chat-backend-prod` (REVIEW_IN_PROGRESS) - Se puede limpiar

### 📊 Stacks Antiguos/Innecesarios
- Múltiples stacks DELETE_COMPLETE (ya eliminados)
- Stacks de pruebas antiguas

## 🛠️ **Comandos de Monitoreo SEGUROS**

### Ver Estado de Stacks Activos
```bash
aws cloudformation describe-stacks \
  --stack-name aws-propuestas-v3-mcp-servers \
  --region us-east-1 \
  --query 'Stacks[0].StackStatus'
```

### Health Check de Servicios
```bash
curl https://mcp.danielingram.shop/health
```

### Ver Logs (Solo lectura)
```bash
aws logs describe-log-groups \
  --log-group-name-prefix "/ecs/aws-propuestas-v3" \
  --region us-east-1
```

## 💰 **Costos Actuales**
- **ECS Fargate**: ~$30-50/mes
- **ALB**: ~$16/mes  
- **CloudWatch**: ~$5-10/mes
- **Total**: ~$50-75/mes

---

**🚨 IMPORTANTE: Esta infraestructura está en PRODUCCIÓN ACTIVA**
**❌ NO ejecutar comandos de eliminación sin confirmación explícita**
