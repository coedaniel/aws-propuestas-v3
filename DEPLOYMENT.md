# Guía de Despliegue - AWS Propuestas v3

Esta guía te llevará paso a paso para desplegar el sistema completo de AWS Propuestas v3 en tu cuenta de AWS.

## 📋 Prerrequisitos

### 1. Herramientas Requeridas
```bash
# Node.js (versión 18 o superior)
node --version  # v18.0.0+

# AWS CLI
aws --version   # aws-cli/2.0.0+

# AWS SAM CLI
sam --version   # SAM CLI, version 1.0.0+

# Python (versión 3.9)
python3 --version  # Python 3.9.0+

# Git
git --version  # git version 2.0.0+
```

### 2. Configuración de AWS
```bash
# Configurar credenciales AWS
aws configure
# AWS Access Key ID: [Tu Access Key]
# AWS Secret Access Key: [Tu Secret Key]
# Default region name: us-east-1
# Default output format: json

# Verificar configuración
aws sts get-caller-identity
```

### 3. Permisos IAM Requeridos
Tu usuario/rol debe tener los siguientes permisos:
- `CloudFormationFullAccess`
- `IAMFullAccess`
- `LambdaFullAccess`
- `APIGatewayFullAccess`
- `DynamoDBFullAccess`
- `S3FullAccess`
- `BedrockFullAccess`
- `CloudWatchFullAccess`

## 🚀 Despliegue Paso a Paso

### Paso 1: Clonar el Repositorio
```bash
git clone https://github.com/coedaniel/aws-propuestas-v3.git
cd aws-propuestas-v3
```

### Paso 2: Configurar Variables de Entorno
```bash
# Copiar archivo de ejemplo
cp .env.local.example .env.local

# Editar configuraciones
nano .env.local
```

Configurar las siguientes variables:
```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_PROFILE=default

# Bedrock Configuration
BEDROCK_REGION=us-east-1
DEFAULT_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0

# Application Configuration
ENVIRONMENT=prod
PROJECT_NAME=aws-propuestas-v3
```

### Paso 3: Instalar Dependencias del Frontend
```bash
npm install
```

### Paso 4: Construir el Backend
```bash
# Construir las funciones Lambda
sam build --template infrastructure/template.yaml

# Verificar que la construcción fue exitosa
ls -la .aws-sam/build/
```

### Paso 5: Desplegar el Backend
```bash
# Despliegue inicial (interactivo)
sam deploy --guided

# O despliegue directo
sam deploy \
  --stack-name aws-propuestas-v3-prod \
  --capabilities CAPABILITY_IAM \
  --region us-east-1 \
  --resolve-s3 \
  --parameter-overrides \
    Environment=prod
```

### Paso 6: Obtener URLs del Backend
```bash
# Obtener outputs del stack
aws cloudformation describe-stacks \
  --stack-name aws-propuestas-v3-prod \
  --query 'Stacks[0].Outputs' \
  --output table
```

Anota las siguientes URLs:
- `ApiGatewayUrl`: URL base de tu API
- `DocumentsBucketName`: Nombre del bucket S3

### Paso 7: Configurar Frontend
```bash
# Actualizar .env.local con la URL de la API
echo "NEXT_PUBLIC_API_URL=https://tu-api-gateway-url.amazonaws.com/prod" >> .env.local
```

### Paso 8: Construir y Desplegar Frontend

#### Opción A: Despliegue Local para Desarrollo
```bash
npm run dev
# Accede a http://localhost:3000
```

#### Opción B: Despliegue con AWS Amplify
```bash
# Construir para producción
npm run build

# Crear archivo de configuración de Amplify
cat > amplify.yml << EOF
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: out
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
EOF

# Subir a Amplify (manual o via CLI)
```

### Paso 9: Verificar Despliegue
```bash
# Probar health check
curl https://tu-api-gateway-url.amazonaws.com/prod/health

# Probar endpoint principal
curl -X POST https://tu-api-gateway-url.amazonaws.com/prod/arquitecto \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"hola"}],"modelId":"anthropic.claude-3-haiku-20240307-v1:0"}'
```

## 🔧 Configuración Avanzada

### Configurar Dominio Personalizado

#### 1. Crear Certificado SSL
```bash
aws acm request-certificate \
  --domain-name tu-dominio.com \
  --validation-method DNS \
  --region us-east-1
```

#### 2. Configurar API Gateway
```bash
# Crear dominio personalizado
aws apigateway create-domain-name \
  --domain-name api.tu-dominio.com \
  --certificate-arn arn:aws:acm:us-east-1:123456789012:certificate/cert-id
```

#### 3. Configurar Route 53
```bash
# Crear registro DNS
aws route53 change-resource-record-sets \
  --hosted-zone-id Z123456789 \
  --change-batch file://dns-change.json
```

### Configurar Monitoreo

#### 1. CloudWatch Dashboards
```bash
# Crear dashboard personalizado
aws cloudwatch put-dashboard \
  --dashboard-name "AWS-Propuestas-v3" \
  --dashboard-body file://dashboard.json
```

#### 2. Alertas
```bash
# Crear alarma para errores de Lambda
aws cloudwatch put-metric-alarm \
  --alarm-name "Lambda-Errors-High" \
  --alarm-description "Lambda function errors are high" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold
```

## 🔄 Actualización del Sistema

### Actualizar Backend
```bash
# Hacer cambios en el código
git pull origin main

# Reconstruir
sam build --template infrastructure/template.yaml

# Redesplegar
sam deploy --stack-name aws-propuestas-v3-prod
```

### Actualizar Frontend
```bash
# Hacer cambios en el código
git pull origin main

# Reconstruir
npm run build

# Redesplegar (Amplify)
amplify publish
```

## 🐛 Troubleshooting

### Problemas Comunes

#### 1. Error de Permisos IAM
```bash
# Verificar permisos
aws iam get-user
aws iam list-attached-user-policies --user-name tu-usuario
```

#### 2. Error de Bedrock
```bash
# Verificar acceso a Bedrock
aws bedrock list-foundation-models --region us-east-1

# Habilitar modelo si es necesario
aws bedrock put-model-invocation-logging-configuration \
  --logging-config destinationConfig='{cloudWatchConfig={logGroupName=/aws/bedrock/modelinvocations,roleArn=arn:aws:iam::123456789012:role/service-role/AmazonBedrockExecutionRoleForCloudWatchLogs}}'
```

#### 3. Error de CORS
```bash
# Verificar configuración de CORS en API Gateway
aws apigateway get-resource \
  --rest-api-id tu-api-id \
  --resource-id tu-resource-id
```

#### 4. Error de DynamoDB
```bash
# Verificar tablas
aws dynamodb list-tables

# Verificar configuración de tabla
aws dynamodb describe-table --table-name aws-propuestas-v3-projects-prod
```

### Logs y Debugging

#### Ver Logs de Lambda
```bash
# Logs en tiempo real
sam logs --stack-name aws-propuestas-v3-prod --tail

# Logs específicos de función
aws logs filter-log-events \
  --log-group-name "/aws/lambda/aws-propuestas-v3-arquitecto-prod" \
  --start-time $(date -d '1 hour ago' +%s)000
```

#### Ver Métricas
```bash
# Métricas de API Gateway
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name Count \
  --dimensions Name=ApiName,Value=aws-propuestas-v3-api \
  --start-time $(date -d '1 hour ago' -u +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

## 🔒 Configuración de Seguridad

### Habilitar Cifrado Adicional
```bash
# Crear clave KMS personalizada
aws kms create-key \
  --description "AWS Propuestas v3 encryption key" \
  --key-usage ENCRYPT_DECRYPT
```

### Configurar WAF (Opcional)
```bash
# Crear Web ACL
aws wafv2 create-web-acl \
  --name aws-propuestas-v3-waf \
  --scope REGIONAL \
  --default-action Allow={} \
  --rules file://waf-rules.json
```

## 📊 Monitoreo Post-Despliegue

### Métricas Clave a Monitorear
1. **Lambda Duration**: < 30 segundos
2. **API Gateway 4XX Errors**: < 1%
3. **API Gateway 5XX Errors**: < 0.1%
4. **DynamoDB Throttles**: 0
5. **S3 Upload Success Rate**: > 99%

### Dashboards Recomendados
- Resumen ejecutivo de la aplicación
- Métricas de rendimiento de Lambda
- Métricas de API Gateway
- Métricas de DynamoDB
- Costos y uso de recursos

## 🔄 Backup y Recuperación

### Configurar Backups Automáticos
```bash
# Habilitar backup de DynamoDB
aws dynamodb put-backup-policy \
  --table-name aws-propuestas-v3-projects-prod \
  --backup-policy BackupEnabled=true

# Configurar replicación de S3
aws s3api put-bucket-replication \
  --bucket aws-propuestas-v3-documents-prod-123456789012 \
  --replication-configuration file://replication.json
```

### Plan de Recuperación ante Desastres
1. **RTO (Recovery Time Objective)**: 4 horas
2. **RPO (Recovery Point Objective)**: 1 hora
3. **Región de respaldo**: us-west-2

## 📝 Checklist de Despliegue

### Pre-Despliegue
- [ ] Credenciales AWS configuradas
- [ ] Permisos IAM verificados
- [ ] Herramientas instaladas
- [ ] Variables de entorno configuradas
- [ ] Código actualizado desde Git

### Despliegue
- [ ] Backend construido exitosamente
- [ ] Backend desplegado sin errores
- [ ] Frontend construido exitosamente
- [ ] Frontend desplegado sin errores
- [ ] URLs obtenidas y configuradas

### Post-Despliegue
- [ ] Health checks pasando
- [ ] Endpoints funcionando
- [ ] Logs sin errores críticos
- [ ] Métricas normales
- [ ] Documentación actualizada

## 🆘 Soporte

Si encuentras problemas durante el despliegue:

1. **Revisa los logs**: CloudWatch Logs para detalles específicos
2. **Consulta la documentación**: `TROUBLESHOOTING.md`
3. **Verifica configuración**: Variables de entorno y permisos
4. **Contacta soporte**: Crea un issue en GitHub

---

¡Felicidades! Tu sistema AWS Propuestas v3 debería estar funcionando correctamente. 🎉
