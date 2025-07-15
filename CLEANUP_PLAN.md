# 🧹 Plan de Limpieza AWS Console

## 🎯 **Objetivo**
Organizar y limpiar la consola AWS manteniendo TODOS los recursos de producción intactos.

## 🔒 **Stacks PROTEGIDOS (NO TOCAR JAMÁS)**

### ✅ Producción Activa
- `aws-propuestas-v3-mcp-servers` - **CRÍTICO** - Servicios MCP en producción
- `aws-propuestas-v3-prod` - **CRÍTICO** - Stack principal (aunque en rollback)
- `bedrock-chat-iam` - **NECESARIO** - Roles IAM para Bedrock
- `aws-sam-cli-managed-default` - **ÚTIL** - Bucket SAM
- `secure-website-starter-kit` - **ACTIVO** - Otro proyecto
- `Ec2AutomationStack` - **ACTIVO** - Automatización EC2
- `cc-iam-stack` - **ACTIVO** - Roles IAM importantes
- `IMBillingRole` - **ACTIVO** - Rol de billing
- `basictable` - **ACTIVO** - Tabla DynamoDB

### ⚠️ Control Tower (NO TOCAR)
- `AWSControlTowerBP-BASELINE-CONFIG-MASTER`
- `AWSControlTowerBP-BASELINE-CLOUDTRAIL-MASTER`

## 🔴 **Stack Problemático para Limpiar**

### Stack Colgado
- `bedrock-chat-backend-prod` (REVIEW_IN_PROGRESS)

**Comando SEGURO para limpiar:**
```bash
aws cloudformation delete-stack \
  --stack-name bedrock-chat-backend-prod \
  --region us-east-1
```

## 📊 **Organización Propuesta**

### 1. **Usar Tags para Organizar**
```bash
# Etiquetar stack principal
aws cloudformation update-stack \
  --stack-name aws-propuestas-v3-mcp-servers \
  --use-previous-template \
  --tags Key=Project,Value=AWS-Propuestas-V3 \
         Key=Environment,Value=Production \
         Key=Owner,Value=Daniel \
         Key=CostCenter,Value=MCP-Services
```

### 2. **Crear Stack Sets por Proyecto**
- **AWS Propuestas V3**: Todos los stacks relacionados
- **Utilities**: Stacks de utilidades (IAM, automation)
- **Control Tower**: Stacks de governance
- **Legacy**: Stacks antiguos pero necesarios

## 🎨 **Mejores Prácticas Implementadas**

### Naming Convention
```
Proyecto-Componente-Ambiente
aws-propuestas-v3-mcp-servers-prod
aws-propuestas-v3-frontend-prod
aws-propuestas-v3-database-prod
```

### Tags Estándar
```yaml
Project: AWS-Propuestas-V3
Environment: Production|Development|Staging
Owner: Daniel
Component: MCP|Frontend|Database|IAM
CostCenter: MCP-Services
```

## 🔍 **Comandos de Monitoreo**

### Ver Solo Stacks Activos
```bash
aws cloudformation list-stacks \
  --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE \
  --region us-east-1 \
  --query 'StackSummaries[*].[StackName,StackStatus,CreationTime]' \
  --output table
```

### Ver Stacks por Proyecto
```bash
aws cloudformation list-stacks \
  --region us-east-1 \
  --query 'StackSummaries[?contains(StackName, `aws-propuestas-v3`)].[StackName,StackStatus]' \
  --output table
```

### Costos por Stack
```bash
aws ce get-cost-and-usage \
  --time-period Start=2025-07-01,End=2025-07-15 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE
```

## 🚨 **Acciones PROHIBIDAS**

### ❌ NUNCA Ejecutar
```bash
# ❌ NO HACER - Eliminaría servicios en producción
aws cloudformation delete-stack --stack-name aws-propuestas-v3-mcp-servers
aws cloudformation delete-stack --stack-name aws-propuestas-v3-prod
aws cloudformation delete-stack --stack-name bedrock-chat-iam
```

### ❌ Recursos Críticos
- ECS Cluster: `aws-propuestas-v3-mcp-cluster-prod`
- Load Balancer: `mcp.danielingram.shop`
- VPC y Subnets del proyecto
- Roles IAM de Bedrock

## ✅ **Acciones Seguras**

### 1. Solo Limpiar Stack Colgado
```bash
aws cloudformation delete-stack \
  --stack-name bedrock-chat-backend-prod \
  --region us-east-1
```

### 2. Agregar Tags a Stacks Existentes
```bash
aws cloudformation update-stack \
  --stack-name aws-propuestas-v3-mcp-servers \
  --use-previous-template \
  --tags Key=Project,Value=AWS-Propuestas-V3
```

### 3. Crear Dashboard de Monitoreo
- CloudWatch Dashboard para métricas
- Cost Explorer para costos
- AWS Config para compliance

## 📈 **Resultado Esperado**

### Antes (Actual)
- 100+ stacks en la consola
- Difícil encontrar recursos activos
- Stacks problemáticos mezclados

### Después (Objetivo)
- Stacks organizados por tags
- Solo stacks activos visibles
- Fácil identificación de recursos
- Monitoreo claro de costos

---

**🎯 Limpieza inteligente sin afectar producción**
