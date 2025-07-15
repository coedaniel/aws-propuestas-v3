# MCP Servers - AWS Propuestas V3

Este directorio contiene los **Model Context Protocol (MCP) servers** reales que se ejecutan como contenedores Docker en Amazon ECS. Estos servidores reemplazan la implementación anterior basada en Lambda que generaba documentos de baja calidad.

## 🏗️ Arquitectura

Los MCP servers están diseñados para ejecutarse como contenedores Docker en ECS Fargate, proporcionando:

- **Escalabilidad automática** con ECS
- **Alta disponibilidad** con múltiples AZs
- **Balanceador de carga** para distribución de tráfico
- **Monitoreo integrado** con CloudWatch
- **Compatibilidad MCP estándar** para futuras integraciones

## 📦 Servidores Disponibles

### 1. Document Generator (`document-generator/`)
- **Puerto**: 8000
- **Función**: Genera documentos Word profesionales y archivos CSV de actividades
- **Herramientas MCP**:
  - `generate_word_document`: Crea propuestas técnicas en formato Word
  - `generate_csv_activities`: Genera cronogramas de implementación
  - `generate_complete_proposal`: Paquete completo de documentos

### 2. CloudFormation Generator (`cloudformation-generator/`)
- **Puerto**: 8001
- **Función**: Genera plantillas CloudFormation para infraestructura AWS
- **Herramientas MCP**:
  - `generate_cloudformation_template`: Crea plantillas IaC basadas en requerimientos

### 3. Cost Analysis (`cost-analysis/`)
- **Puerto**: 8002
- **Función**: Genera análisis detallados de costos AWS
- **Herramientas MCP**:
  - `generate_cost_analysis`: Calcula estimaciones de costos mensuales/anuales

## 🚀 Despliegue

### Prerrequisitos

1. **Docker** instalado y ejecutándose
2. **AWS CLI** configurado con permisos adecuados
3. **Permisos IAM** para ECS, ECR, CloudFormation

### Despliegue Automático

```bash
# Desde el directorio raíz del proyecto
./scripts/deploy-mcp-servers.sh
```

Este script:
1. Construye las imágenes Docker
2. Las sube a Amazon ECR
3. Despliega la infraestructura ECS
4. Configura el Application Load Balancer
5. Inicia los servicios ECS

### Despliegue Manual

```bash
# 1. Construir imágenes Docker
cd mcp-servers/document-generator
docker build -t aws-propuestas-v3-document-generator .

cd ../cloudformation-generator
docker build -t aws-propuestas-v3-cloudformation-generator .

cd ../cost-analysis
docker build -t aws-propuestas-v3-cost-analysis .

# 2. Subir a ECR (requiere configuración previa de repositorios)
# Ver scripts/deploy-mcp-servers.sh para comandos completos

# 3. Desplegar infraestructura
aws cloudformation deploy \
    --template-file infrastructure/ecs-mcp-servers.yaml \
    --stack-name aws-propuestas-v3-mcp-servers-prod \
    --capabilities CAPABILITY_IAM
```

## 🔧 Configuración

### Variables de Entorno

Los MCP servers utilizan estas variables de entorno:

```bash
ENVIRONMENT=prod                    # Entorno de despliegue
PROJECT_NAME=aws-propuestas-v3     # Nombre del proyecto
```

### Endpoints

Una vez desplegados, los servidores están disponibles en:

```
http://<ALB-DNS>/document-generator
http://<ALB-DNS>/cloudformation-generator
http://<ALB-DNS>/cost-analysis
```

## 🧪 Testing

### Health Checks

Cada servidor expone un endpoint de salud:

```bash
curl http://<ALB-DNS>/document-generator/health
curl http://<ALB-DNS>/cloudformation-generator/health
curl http://<ALB-DNS>/cost-analysis/health
```

### Pruebas de Herramientas MCP

```bash
# Ejemplo: Generar documento Word
curl -X POST http://<ALB-DNS>/document-generator/call-tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "generate_word_document",
    "arguments": {
      "project_info": {
        "name": "Proyecto Prueba",
        "solution_type": "rapid_service",
        "selected_services": ["EC2", "RDS", "S3"]
      },
      "agent_response": "Respuesta del agente Bedrock"
    }
  }'
```

## 🔍 Monitoreo

### CloudWatch Logs

Los logs están organizados por servicio:

- `/ecs/aws-propuestas-v3-document-generator-prod`
- `/ecs/aws-propuestas-v3-cloudformation-generator-prod`
- `/ecs/aws-propuestas-v3-cost-analysis-prod`

### Métricas ECS

Monitorea en la consola de ECS:
- CPU y memoria utilizada
- Número de tareas ejecutándose
- Health checks del ALB
- Latencia de respuesta

## 🔗 Integración con Lambda

Los MCP servers se integran con la función Lambda principal a través del cliente MCP:

```python
from mcp_client import MCPClient

# Inicializar cliente
mcp_client = MCPClient()

# Generar documentos
result = mcp_client.generate_all_documents(project_info, agent_response)
```

### Variables de Entorno para Lambda

```bash
DOCUMENT_GENERATOR_ENDPOINT=http://<ALB-DNS>/document-generator
CLOUDFORMATION_GENERATOR_ENDPOINT=http://<ALB-DNS>/cloudformation-generator
COST_ANALYSIS_ENDPOINT=http://<ALB-DNS>/cost-analysis
```

## 🛠️ Desarrollo Local

### Ejecutar Localmente

```bash
# Terminal 1: Document Generator
cd mcp-servers/document-generator
python -m mcp_server

# Terminal 2: CloudFormation Generator
cd mcp-servers/cloudformation-generator
python -m mcp_server

# Terminal 3: Cost Analysis
cd mcp-servers/cost-analysis
python -m mcp_server
```

### Desarrollo con Docker

```bash
# Construir y ejecutar localmente
docker build -t doc-gen-local mcp-servers/document-generator/
docker run -p 8000:8000 doc-gen-local
```

## 📋 Troubleshooting

### Problemas Comunes

1. **Servicios no inician**
   - Verificar logs en CloudWatch
   - Comprobar health checks del ALB
   - Revisar configuración de security groups

2. **Timeouts en requests**
   - Aumentar timeout en el cliente MCP
   - Verificar capacidad de las tareas ECS
   - Comprobar latencia de red

3. **Errores de permisos**
   - Verificar IAM roles de las tareas ECS
   - Comprobar políticas de ECR
   - Revisar permisos de CloudWatch Logs

### Comandos Útiles

```bash
# Ver estado de servicios ECS
aws ecs describe-services \
    --cluster aws-propuestas-v3-mcp-cluster-prod \
    --services document-generator cloudformation-generator cost-analysis

# Ver logs en tiempo real
aws logs tail /ecs/aws-propuestas-v3-document-generator-prod --follow

# Reiniciar servicio
aws ecs update-service \
    --cluster aws-propuestas-v3-mcp-cluster-prod \
    --service document-generator \
    --force-new-deployment
```

## 🔄 Actualizaciones

Para actualizar los MCP servers:

1. Modificar el código del servidor
2. Ejecutar `./scripts/deploy-mcp-servers.sh`
3. ECS automáticamente desplegará las nuevas versiones

## 📚 Referencias

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Amazon ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [AWS Fargate Documentation](https://docs.aws.amazon.com/fargate/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
