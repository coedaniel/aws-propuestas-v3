# AWS Propuestas V3 - Configuración de Agentes Duales

## 🚀 Estado Actual del Despliegue

### ✅ Agentes Bedrock Configurados

#### 1. Nova Pro (Multimodal)
- **Agent ID**: `WUGHP2HGH9`
- **Agent Alias ID**: `ZNZ3SYTP5L`
- **Modelo**: `amazon.nova-pro-v1:0`
- **Especialización**: Diagramas, análisis visual, contenido multimodal
- **Estado**: ✅ PREPARED y ACTIVO

#### 2. Claude 3.5 Sonnet (Análisis)
- **Agent ID**: `W3YRJXXIRE`
- **Agent Alias ID**: `ULPAGJS0VW`
- **Modelo**: `anthropic.claude-3-5-sonnet-20240620-v1:0`
- **Especialización**: Análisis técnico profundo, documentación detallada
- **Estado**: ✅ PREPARED y ACTIVO

### 🏗️ Infraestructura Desplegada

#### CloudFormation Stack
- **Nombre**: `aws-propuestas-v3-dual-agents`
- **Estado**: 🔄 REVIEW_IN_PROGRESS (desplegándose)
- **Región**: us-east-1

#### Funciones Lambda
1. **DualAgentsFunction**: Función principal con selector de agentes
2. **ModelsInfoFunction**: Endpoint para información de modelos

#### API Gateway
- **Endpoints**:
  - `POST /chat` - Chat principal con selector de modelos
  - `GET /models` - Información de modelos disponibles
  - `OPTIONS /*` - CORS habilitado

#### S3 Bucket
- **Propósito**: Almacenamiento de documentos generados
- **Nombre**: `aws-propuestas-documents-prod-{AccountId}`

## 🎯 Funcionalidades Implementadas

### Frontend (Next.js)
- ✅ **ModelSelector Component**: Switch para elegir entre Nova Pro y Claude
- ✅ **Tipos actualizados**: Soporte para agentes duales
- ✅ **API actualizada**: Envío de `selected_model` en requests

### Backend (Lambda + Bedrock Agents)
- ✅ **Dual Agent Architecture**: Dos agentes especializados
- ✅ **Dynamic Model Selection**: Selección basada en frontend
- ✅ **Streaming Responses**: Procesamiento de respuestas en tiempo real
- ✅ **Error Handling**: Manejo robusto de errores
- ✅ **CORS Support**: Configuración completa de CORS

### Action Groups (5 especializados)
1. **DocumentGenerationV2** (ID: AVZJ0XP1WE)
2. **CoreOrchestrationV2** (ID: S6NGAP04YL)
3. **DiagramCreationV2** (ID: HPT1ROS4ZM)
4. **CloudFormationTemplatesV2** (ID: 1UE9SLQQML)
5. **CDKGenerationV2** (ID: IPJ8VI3HZP)

## 🔧 Configuración del Selector de Modelos

### Uso Recomendado

#### Nova Pro 🎨
```javascript
selectedModel: 'nova'
```
**Ideal para**:
- Generar diagramas de arquitectura
- Análisis de imágenes de infraestructura
- Crear contenido visual
- Procesamiento multimodal (texto + imagen + video)

#### Claude 3.5 Sonnet 🧠
```javascript
selectedModel: 'claude'
```
**Ideal para**:
- Propuestas ejecutivas detalladas
- Análisis de costos complejos
- Código CloudFormation/CDK optimizado
- Documentación técnica profunda

### Ejemplo de Request
```javascript
const response = await fetch('/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    selected_model: 'nova', // o 'claude'
    project_info: {
      name: 'Mi Proyecto',
      description: 'Descripción del proyecto',
      services: ['Lambda', 'DynamoDB', 'API Gateway']
    },
    query: 'Genera una propuesta completa',
    session_id: 'unique-session-id'
  })
});
```

## 📋 Próximos Pasos

### 1. Verificar Despliegue
```bash
# Verificar estado del stack
aws cloudformation describe-stacks \
  --stack-name aws-propuestas-v3-dual-agents \
  --region us-east-1 \
  --query 'Stacks[0].StackStatus'

# Obtener URL del API Gateway
aws cloudformation describe-stacks \
  --stack-name aws-propuestas-v3-dual-agents \
  --region us-east-1 \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
  --output text
```

### 2. Actualizar Frontend
```bash
# Actualizar .env.local con la nueva URL del API
NEXT_PUBLIC_API_URL=https://NEW_API_ID.execute-api.us-east-1.amazonaws.com/prod
```

### 3. Probar Funcionalidad
```bash
# Probar endpoint de modelos
curl https://NEW_API_ID.execute-api.us-east-1.amazonaws.com/prod/models

# Probar chat con Nova Pro
curl -X POST https://NEW_API_ID.execute-api.us-east-1.amazonaws.com/prod/chat \
  -H "Content-Type: application/json" \
  -d '{"selected_model":"nova","query":"Hola, genera un diagrama de arquitectura"}'

# Probar chat con Claude
curl -X POST https://NEW_API_ID.execute-api.us-east-1.amazonaws.com/prod/chat \
  -H "Content-Type: application/json" \
  -d '{"selected_model":"claude","query":"Genera una propuesta ejecutiva detallada"}'
```

### 4. Desplegar en Amplify
```bash
# Build del frontend
npm run build

# Desplegar en Amplify (automático con git push)
git add .
git commit -m "feat: Dual Bedrock Agents with Model Selector"
git push origin main
```

## 🔍 Monitoreo y Debugging

### CloudWatch Logs
- **DualAgentsFunction**: `/aws/lambda/aws-propuestas-dual-agents-prod`
- **ModelsInfoFunction**: `/aws/lambda/aws-propuestas-models-info-prod`

### Métricas Importantes
- **Invocaciones por modelo**: Nova vs Claude
- **Latencia de respuesta**: Tiempo de procesamiento
- **Errores**: Rate de errores por agente
- **Costos**: Uso de tokens por modelo

### Comandos de Debug
```bash
# Ver logs en tiempo real
aws logs tail /aws/lambda/aws-propuestas-dual-agents-prod --follow

# Verificar estado de agentes
aws bedrock-agent get-agent --agent-id WUGHP2HGH9 --region us-east-1
aws bedrock-agent get-agent --agent-id W3YRJXXIRE --region us-east-1
```

## 💡 Optimizaciones Futuras

1. **Caching**: Implementar cache de respuestas frecuentes
2. **Load Balancing**: Distribuir carga entre agentes
3. **A/B Testing**: Comparar rendimiento de modelos
4. **Cost Optimization**: Análisis de costos por modelo
5. **Performance Monitoring**: Métricas detalladas de rendimiento

---

## 📞 Soporte

Si encuentras algún problema:

1. **Verificar logs** en CloudWatch
2. **Revisar estado** de agentes Bedrock
3. **Validar configuración** de API Gateway
4. **Comprobar permisos** IAM

**Estado del sistema**: 🟡 En despliegue - Esperando confirmación final
