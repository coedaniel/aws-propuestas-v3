# Guía de Troubleshooting - AWS Propuestas v3

Esta guía te ayudará a diagnosticar y resolver los problemas más comunes del sistema AWS Propuestas v3.

## 🚨 Problemas Críticos Conocidos

### 1. Generación de Documentos Incorrectos
**Síntoma**: Los documentos generados contienen servicios incorrectos (EC2/S3 en lugar de GuardDuty, API Gateway, etc.)

**Causa**: Funciones de extracción de servicios desincronizadas entre generadores.

**Solución**:
```bash
# Verificar que todas las funciones usen extract_services_from_analysis
grep -r "extract_services_from_analysis" backend/

# Si hay inconsistencias, actualizar el código
git pull origin main
sam build
sam deploy --stack-name aws-propuestas-v3-prod
```

### 2. Nombres de Proyecto Incorrectos
**Síntoma**: "Mis Proyectos" muestra respuestas de conversación en lugar de nombres de proyecto.

**Causa**: Lógica de extracción de nombres de proyecto defectuosa.

**Solución**:
```bash
# Verificar logs de la función
aws logs filter-log-events \
  --log-group-name "/aws/lambda/aws-propuestas-v3-arquitecto-prod" \
  --filter-pattern "project_name" \
  --start-time $(date -d '1 hour ago' +%s)000

# Limpiar proyectos con nombres incorrectos
aws dynamodb scan --table-name aws-propuestas-v3-projects-prod \
  --filter-expression "contains(project_name, :greeting)" \
  --expression-attribute-values '{":greeting":{"S":"hola"}}'
```

### 3. Inconsistencia DynamoDB vs S3
**Síntoma**: Archivos existen en S3 pero no hay registro en DynamoDB.

**Causa**: Mapeo inconsistente entre projectId (DynamoDB) y nombres de carpeta (S3).

**Diagnóstico**:
```bash
# Listar proyectos en DynamoDB
aws dynamodb scan --table-name aws-propuestas-v3-projects-prod

# Listar carpetas en S3
aws s3 ls s3://tu-bucket-name/ --recursive | grep -E "/$"

# Comparar resultados
```

**Solución**:
```bash
# Script para sincronizar (ejecutar con precaución)
python3 scripts/sync_dynamodb_s3.py
```

## 🔧 Problemas de Configuración

### Error: "Unable to import module 'lambda_function'"

**Causa**: Dependencias no instaladas correctamente o estructura de archivos incorrecta.

**Solución**:
```bash
# Verificar estructura
ls -la .aws-sam/build/ArquitectoFunction/

# Reconstruir con dependencias
sam build --use-container
sam deploy --stack-name aws-propuestas-v3-prod
```

### Error: "Access Denied" en Bedrock

**Causa**: Permisos insuficientes o modelo no habilitado.

**Diagnóstico**:
```bash
# Verificar acceso a Bedrock
aws bedrock list-foundation-models --region us-east-1

# Verificar permisos IAM
aws iam get-role-policy \
  --role-name aws-propuestas-v3-lambda-role \
  --policy-name BedrockPolicy
```

**Solución**:
```bash
# Habilitar modelo en Bedrock
aws bedrock put-model-invocation-logging-configuration \
  --logging-config destinationConfig='{cloudWatchConfig={logGroupName=/aws/bedrock/modelinvocations}}'

# Actualizar permisos IAM si es necesario
aws iam put-role-policy \
  --role-name aws-propuestas-v3-lambda-role \
  --policy-name BedrockPolicy \
  --policy-document file://bedrock-policy.json
```

### Error: "Table does not exist" en DynamoDB

**Causa**: Tabla no creada o nombre incorrecto.

**Diagnóstico**:
```bash
# Listar tablas
aws dynamodb list-tables

# Verificar configuración del stack
aws cloudformation describe-stack-resources \
  --stack-name aws-propuestas-v3-prod \
  --logical-resource-id ProjectsTable
```

**Solución**:
```bash
# Redesplegar stack completo
sam deploy --stack-name aws-propuestas-v3-prod --force-upload
```

## 🌐 Problemas de Red y CORS

### Error: "CORS policy blocked"

**Causa**: Configuración CORS incorrecta en API Gateway.

**Diagnóstico**:
```bash
# Verificar configuración CORS
aws apigateway get-resource \
  --rest-api-id tu-api-id \
  --resource-id tu-resource-id
```

**Solución**:
```bash
# Actualizar configuración CORS en template.yaml
# Luego redesplegar
sam deploy --stack-name aws-propuestas-v3-prod
```

### Error: "Network timeout"

**Causa**: Lambda timeout o problemas de conectividad.

**Diagnóstico**:
```bash
# Verificar timeout de Lambda
aws lambda get-function-configuration \
  --function-name aws-propuestas-v3-arquitecto-prod

# Verificar logs de timeout
aws logs filter-log-events \
  --log-group-name "/aws/lambda/aws-propuestas-v3-arquitecto-prod" \
  --filter-pattern "Task timed out"
```

**Solución**:
```bash
# Aumentar timeout en template.yaml
# Timeout: 300  # 5 minutos
sam deploy --stack-name aws-propuestas-v3-prod
```

## 📊 Problemas de Rendimiento

### Lambda Execution Duration Alta

**Síntoma**: Respuestas lentas del sistema.

**Diagnóstico**:
```bash
# Métricas de duración
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=aws-propuestas-v3-arquitecto-prod \
  --start-time $(date -d '1 hour ago' -u +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum
```

**Solución**:
```bash
# Aumentar memoria de Lambda
aws lambda update-function-configuration \
  --function-name aws-propuestas-v3-arquitecto-prod \
  --memory-size 1024

# O actualizar en template.yaml y redesplegar
```

### DynamoDB Throttling

**Síntoma**: Errores 400 en operaciones de base de datos.

**Diagnóstico**:
```bash
# Verificar métricas de throttling
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name UserErrors \
  --dimensions Name=TableName,Value=aws-propuestas-v3-projects-prod \
  --start-time $(date -d '1 hour ago' -u +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

**Solución**:
```bash
# Cambiar a modo On-Demand
aws dynamodb update-table \
  --table-name aws-propuestas-v3-projects-prod \
  --billing-mode PAY_PER_REQUEST
```

## 🔍 Herramientas de Diagnóstico

### Script de Health Check
```bash
#!/bin/bash
# health_check.sh

echo "=== AWS Propuestas v3 Health Check ==="

# 1. Verificar API Gateway
echo "1. Testing API Gateway..."
API_URL=$(aws cloudformation describe-stacks \
  --stack-name aws-propuestas-v3-prod \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
  --output text)

curl -s "${API_URL}/health" | jq .

# 2. Verificar Lambda
echo "2. Testing Lambda function..."
aws lambda invoke \
  --function-name aws-propuestas-v3-arquitecto-prod \
  --payload '{"httpMethod":"GET","path":"/health"}' \
  response.json

cat response.json | jq .

# 3. Verificar DynamoDB
echo "3. Testing DynamoDB..."
aws dynamodb describe-table \
  --table-name aws-propuestas-v3-projects-prod \
  --query 'Table.TableStatus'

# 4. Verificar S3
echo "4. Testing S3..."
BUCKET_NAME=$(aws cloudformation describe-stacks \
  --stack-name aws-propuestas-v3-prod \
  --query 'Stacks[0].Outputs[?OutputKey==`DocumentsBucketName`].OutputValue' \
  --output text)

aws s3 ls s3://${BUCKET_NAME}/ > /dev/null && echo "S3 OK" || echo "S3 ERROR"

echo "=== Health Check Complete ==="
```

### Script de Logs Agregados
```bash
#!/bin/bash
# aggregate_logs.sh

echo "=== Collecting AWS Propuestas v3 Logs ==="

# Función para obtener logs recientes
get_recent_logs() {
    local log_group=$1
    local hours=${2:-1}
    
    echo "--- Logs from $log_group (last $hours hours) ---"
    aws logs filter-log-events \
        --log-group-name "$log_group" \
        --start-time $(date -d "$hours hours ago" +%s)000 \
        --query 'events[*].[timestamp,message]' \
        --output text | \
        while read timestamp message; do
            echo "$(date -d @$((timestamp/1000))) | $message"
        done
}

# Obtener logs de todas las funciones Lambda
get_recent_logs "/aws/lambda/aws-propuestas-v3-arquitecto-prod" 2
get_recent_logs "/aws/lambda/aws-propuestas-v3-generator-prod" 2

# Obtener logs de API Gateway si están habilitados
get_recent_logs "/aws/apigateway/aws-propuestas-v3-api" 1

echo "=== Log Collection Complete ==="
```

### Script de Métricas
```bash
#!/bin/bash
# metrics_report.sh

echo "=== AWS Propuestas v3 Metrics Report ==="

# Función para obtener métricas
get_metric() {
    local namespace=$1
    local metric_name=$2
    local dimensions=$3
    local statistic=${4:-Average}
    
    aws cloudwatch get-metric-statistics \
        --namespace "$namespace" \
        --metric-name "$metric_name" \
        --dimensions "$dimensions" \
        --start-time $(date -d '1 hour ago' -u +%Y-%m-%dT%H:%M:%S) \
        --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
        --period 300 \
        --statistics "$statistic" \
        --query 'Datapoints[0].'"$statistic" \
        --output text
}

# Métricas de Lambda
echo "Lambda Duration (avg): $(get_metric AWS/Lambda Duration Name=FunctionName,Value=aws-propuestas-v3-arquitecto-prod Average) ms"
echo "Lambda Errors (sum): $(get_metric AWS/Lambda Errors Name=FunctionName,Value=aws-propuestas-v3-arquitecto-prod Sum)"
echo "Lambda Invocations (sum): $(get_metric AWS/Lambda Invocations Name=FunctionName,Value=aws-propuestas-v3-arquitecto-prod Sum)"

# Métricas de API Gateway
echo "API Gateway 4XX Errors: $(get_metric AWS/ApiGateway 4XXError Name=ApiName,Value=aws-propuestas-v3-api Sum)"
echo "API Gateway 5XX Errors: $(get_metric AWS/ApiGateway 5XXError Name=ApiName,Value=aws-propuestas-v3-api Sum)"
echo "API Gateway Latency (avg): $(get_metric AWS/ApiGateway Latency Name=ApiName,Value=aws-propuestas-v3-api Average) ms"

# Métricas de DynamoDB
echo "DynamoDB Read Throttles: $(get_metric AWS/DynamoDB ReadThrottles Name=TableName,Value=aws-propuestas-v3-projects-prod Sum)"
echo "DynamoDB Write Throttles: $(get_metric AWS/DynamoDB WriteThrottles Name=TableName,Value=aws-propuestas-v3-projects-prod Sum)"

echo "=== Metrics Report Complete ==="
```

## 🔄 Procedimientos de Recuperación

### Rollback de Despliegue
```bash
# Ver historial de stacks
aws cloudformation list-stack-resources \
  --stack-name aws-propuestas-v3-prod

# Rollback a versión anterior
aws cloudformation cancel-update-stack \
  --stack-name aws-propuestas-v3-prod

# O rollback manual
git checkout HEAD~1
sam build
sam deploy --stack-name aws-propuestas-v3-prod
```

### Restaurar Base de Datos
```bash
# Listar backups disponibles
aws dynamodb list-backups \
  --table-name aws-propuestas-v3-projects-prod

# Restaurar desde backup
aws dynamodb restore-table-from-backup \
  --target-table-name aws-propuestas-v3-projects-prod-restored \
  --backup-arn arn:aws:dynamodb:us-east-1:123456789012:table/aws-propuestas-v3-projects-prod/backup/01234567890123-abcdefgh
```

### Limpiar Recursos Huérfanos
```bash
# Script para limpiar recursos no utilizados
#!/bin/bash

echo "Cleaning orphaned resources..."

# Limpiar versiones antiguas de Lambda
aws lambda list-versions-by-function \
  --function-name aws-propuestas-v3-arquitecto-prod \
  --query 'Versions[?Version!=`$LATEST`].Version' \
  --output text | \
  xargs -I {} aws lambda delete-function --function-name aws-propuestas-v3-arquitecto-prod:{}

# Limpiar logs antiguos (más de 30 días)
aws logs describe-log-groups \
  --log-group-name-prefix "/aws/lambda/aws-propuestas-v3" \
  --query 'logGroups[*].logGroupName' \
  --output text | \
  xargs -I {} aws logs put-retention-policy --log-group-name {} --retention-in-days 30

echo "Cleanup complete"
```

## 📞 Escalación de Problemas

### Nivel 1: Problemas Comunes
- Reiniciar servicios
- Verificar configuración
- Revisar logs básicos

### Nivel 2: Problemas Técnicos
- Análisis profundo de logs
- Métricas detalladas
- Pruebas de componentes individuales

### Nivel 3: Problemas Críticos
- Rollback de emergencia
- Restauración desde backup
- Contacto con soporte AWS

### Información para Soporte
Cuando contactes soporte, incluye:

1. **ID del Stack**: `aws-propuestas-v3-prod`
2. **Región**: `us-east-1`
3. **Timestamp del error**: Hora exacta UTC
4. **Request ID**: De los logs de CloudWatch
5. **Pasos para reproducir**: Secuencia exacta
6. **Logs relevantes**: Últimas 100 líneas
7. **Configuración**: Variables de entorno (sin secretos)

### Plantilla de Reporte de Bug
```markdown
## Bug Report

**Descripción**: [Descripción breve del problema]

**Pasos para Reproducir**:
1. [Paso 1]
2. [Paso 2]
3. [Paso 3]

**Comportamiento Esperado**: [Qué debería pasar]

**Comportamiento Actual**: [Qué está pasando]

**Entorno**:
- Stack: aws-propuestas-v3-prod
- Región: us-east-1
- Timestamp: [YYYY-MM-DD HH:MM:SS UTC]

**Logs**:
```
[Pegar logs relevantes aquí]
```

**Métricas**:
- Lambda Duration: [X ms]
- Error Rate: [X%]
- Request ID: [ID]

**Impacto**: [Alto/Medio/Bajo]
```

---

## 🎯 Checklist de Troubleshooting

### Antes de Reportar un Bug
- [ ] Verificar logs de CloudWatch
- [ ] Revisar métricas de rendimiento
- [ ] Probar health checks
- [ ] Verificar configuración
- [ ] Intentar reproducir el problema
- [ ] Revisar cambios recientes
- [ ] Consultar esta guía de troubleshooting

### Durante la Investigación
- [ ] Documentar pasos realizados
- [ ] Capturar logs relevantes
- [ ] Tomar screenshots si aplica
- [ ] Anotar timestamps exactos
- [ ] Verificar impacto en usuarios
- [ ] Evaluar necesidad de rollback

### Después de la Resolución
- [ ] Verificar que el problema está resuelto
- [ ] Actualizar documentación si es necesario
- [ ] Comunicar resolución a stakeholders
- [ ] Implementar medidas preventivas
- [ ] Actualizar monitoreo si es necesario

¡Esta guía debería ayudarte a resolver la mayoría de problemas comunes! 🛠️
