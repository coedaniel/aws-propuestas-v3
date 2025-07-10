# AWS Propuestas v3 - Sistema Dinámico e Inteligente

Sistema completo de generación automática de propuestas técnicas y comerciales para proyectos AWS, utilizando IA para análisis dinámico de requerimientos.

## 🚀 Características Principales

### ✨ Generación Dinámica e Inteligente
- **Análisis de IA**: El modelo analiza la conversación y extrae requerimientos automáticamente
- **Detección de Servicios**: Identifica servicios AWS mencionados sin hardcodeo
- **Documentos Específicos**: Genera contenido específico para cada servicio detectado
- **Completamente Flexible**: Maneja cualquier servicio AWS sin modificar código

### 📄 Documentos Generados
- **Propuesta Ejecutiva** (Word): Documento profesional para presentación
- **Documento Técnico** (Word): Especificaciones técnicas detalladas
- **CloudFormation Template** (YAML): Template funcional para despliegue
- **Plan de Actividades** (CSV): Cronograma de implementación
- **Estimación de Costos** (CSV): Costos detallados por servicio
- **Diagramas de Arquitectura** (SVG, Draw.io): Visualización de la solución
- **Guía de Calculadora AWS** (TXT): Instrucciones para estimación de costos

### 🎯 Servicios AWS Soportados
- **Compute**: EC2, Lambda, Fargate, Batch
- **Storage**: S3, EFS, FSx, EBS
- **Database**: RDS, DynamoDB, Redshift, Aurora
- **Networking**: VPC, CloudFront, Route53, ELB, ALB, NLB
- **API & Integration**: API Gateway, EventBridge, SNS, SQS, Step Functions
- **Security**: GuardDuty, Inspector, Macie, Config, CloudTrail, WAF, Shield
- **Monitoring**: CloudWatch, X-Ray, Systems Manager
- **AI/ML**: SageMaker, Bedrock, Comprehend, Rekognition
- **Y muchos más...

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway    │    │   Lambda        │
│   (Next.js)     │───▶│   (REST API)     │───▶│   Functions     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                       ┌─────────────────┐              │
                       │   DynamoDB      │◀─────────────┤
                       │   (Projects)    │              │
                       └─────────────────┘              │
                                                        │
                       ┌─────────────────┐              │
                       │   S3 Bucket     │◀─────────────┘
                       │   (Documents)   │
                       └─────────────────┘
```

## 📁 Estructura del Proyecto

```
aws-propuestas-v3/
├── README.md                          # Este archivo
├── DEPLOYMENT.md                      # Guía de despliegue
├── ARCHITECTURE.md                    # Documentación de arquitectura
├── API_REFERENCE.md                   # Referencia de API
├── TROUBLESHOOTING.md                 # Guía de resolución de problemas
├── 
├── app/                               # Frontend Next.js
│   ├── arquitecto/                    # Página del arquitecto
│   ├── chat/                         # Chat general
│   ├── projects/                     # Gestión de proyectos
│   └── globals.css                   # Estilos globales
├── 
├── components/                        # Componentes React
│   ├── ui/                           # Componentes de UI
│   ├── chat/                         # Componentes de chat
│   └── projects/                     # Componentes de proyectos
├── 
├── lambda/                           # Funciones Lambda
│   ├── arquitecto/                   # Lambda del arquitecto
│   │   ├── app.py                   # Handler principal
│   │   ├── conversation_analyzer.py  # Análisis de conversaciones
│   │   └── generators/              # Generadores dinámicos
│   │       ├── dynamic_generator.py  # Generador principal
│   │       ├── dynamic_helpers.py    # Funciones auxiliares
│   │       └── s3_uploader.py       # Subida a S3
│   ├── chat/                        # Lambda de chat general
│   ├── projects/                    # Lambda de proyectos
│   ├── documents/                   # Lambda de documentos
│   └── health/                      # Lambda de health check
├── 
├── infrastructure/                   # Infraestructura como código
│   └── template.yaml                # Template SAM
├── 
├── docs/                            # Documentación adicional
│   ├── examples/                    # Ejemplos de uso
│   ├── api/                        # Documentación de API
│   └── deployment/                 # Guías de despliegue
├── 
├── scripts/                         # Scripts de utilidad
│   ├── deploy.sh                   # Script de despliegue
│   ├── build.sh                    # Script de construcción
│   └── test.sh                     # Script de pruebas
├── 
└── package.json                     # Dependencias del frontend
```

## 🚀 Inicio Rápido

### Prerrequisitos
- Node.js 18+
- AWS CLI configurado
- AWS SAM CLI
- Python 3.9+

### 1. Clonar el Repositorio
```bash
git clone https://github.com/coedaniel/aws-propuestas-v3.git
cd aws-propuestas-v3
```

### 2. Instalar Dependencias
```bash
npm install
```

### 3. Configurar Variables de Entorno
```bash
cp .env.local.example .env.local
# Editar .env.local con tus configuraciones
```

### 4. Desplegar Backend
```bash
sam build --template infrastructure/template.yaml
sam deploy --stack-name aws-propuestas-v3-prod --capabilities CAPABILITY_IAM --region us-east-1 --resolve-s3
```

### 5. Ejecutar Frontend
```bash
npm run dev
```

## 🔧 Configuración

### Variables de Entorno
```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_PROFILE=default

# API Configuration
NEXT_PUBLIC_API_URL=https://your-api-gateway-url.amazonaws.com/prod

# Bedrock Configuration
BEDROCK_REGION=us-east-1
DEFAULT_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
```

### Configuración de AWS
```bash
aws configure
# Ingresa tus credenciales AWS
```

## 📖 Uso del Sistema

### 1. Acceder al Arquitecto
- Navega a `/arquitecto`
- Inicia una conversación describiendo tu proyecto
- El sistema analizará automáticamente tus requerimientos

### 2. Ejemplo de Conversación
```
Usuario: "Hola, necesito ayuda con un proyecto"
Sistema: "¿Cuál es el nombre del proyecto?"
Usuario: "MiAPI"
Sistema: "¿Es una solución integral o servicio rápido?"
Usuario: "Necesito implementar API Gateway para mi aplicación web"
Sistema: [Genera documentos específicos de API Gateway]
```

### 3. Documentos Generados
Los documentos se generan automáticamente y se suben a S3:
- Propuesta ejecutiva con información específica del servicio
- CloudFormation template funcional
- Estimación de costos real
- Guía de calculadora AWS personalizada

## 🔍 Cómo Funciona la Detección Dinámica

### 1. Análisis de Conversación
```python
# El sistema analiza el texto de la conversación
conversation_text = "Necesito implementar API Gateway para mi aplicación"

# Extrae servicios mencionados
services = extract_services_from_analysis(conversation_text)
# Resultado: ['Amazon API Gateway']
```

### 2. Generación de Recursos
```python
# Genera recursos específicos para cada servicio
if 'API Gateway' in services:
    resources['ApiGateway'] = {
        'Type': 'AWS::ApiGateway::RestApi',
        'Properties': {
            'Name': project_name + '-api',
            # ... configuración específica
        }
    }
```

### 3. Costos Específicos
```python
# Genera costos reales para el servicio
if 'API Gateway' in service:
    writer.writerow(['Amazon API Gateway', 'REST API Calls', '1,000,000', '3.50', 'Llamadas a API REST'])
```

## 🛠️ Desarrollo

### Estructura de Generadores
```python
# generators/dynamic_generator.py
def generate_dynamic_cloudformation(project_info, ai_analysis):
    services = extract_services_from_analysis(ai_analysis)
    # Genera template específico para servicios detectados

# generators/dynamic_helpers.py  
def generate_simple_costs_csv(project_info, ai_analysis):
    services = extract_services_from_analysis(ai_analysis)
    # Genera costos específicos para servicios detectados
```

### Agregar Nuevo Servicio
1. Agregar keywords en `service_keywords` en `dynamic_generator.py`
2. Agregar parámetros en `generate_dynamic_parameters()`
3. Agregar recursos en `generate_dynamic_resources()`
4. Agregar outputs en `generate_dynamic_outputs()`
5. Agregar costos en `dynamic_helpers.py`

## 🚀 Despliegue

### Desarrollo
```bash
npm run dev
```

### Producción
```bash
npm run build
sam deploy --stack-name aws-propuestas-v3-prod
```

### CI/CD
El proyecto incluye configuración para GitHub Actions y AWS Amplify.

## 📊 Monitoreo

### CloudWatch Logs
```bash
sam logs --stack-name aws-propuestas-v3-prod --tail
```

### Métricas
- Invocaciones de Lambda
- Errores de API Gateway
- Uso de DynamoDB
- Almacenamiento en S3

## 🔒 Seguridad

### IAM Roles
- Principio de menor privilegio
- Roles específicos por función Lambda
- Políticas granulares para S3 y DynamoDB

### Cifrado
- Datos en reposo cifrados en DynamoDB y S3
- Comunicación HTTPS/TLS
- Secrets Manager para credenciales

## 🤝 Contribución

1. Fork el repositorio
2. Crea una rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 Soporte

- **Documentación**: Ver carpeta `docs/`
- **Issues**: GitHub Issues
- **Troubleshooting**: Ver `TROUBLESHOOTING.md`

## 🔄 Changelog

### v3.0.0 (Actual)
- ✅ Sistema dinámico e inteligente implementado
- ✅ Detección automática de servicios AWS
- ✅ Generación específica de documentos
- ✅ Soporte para 50+ servicios AWS
- ✅ CloudFormation templates funcionales
- ✅ Estimaciones de costos reales

### v2.0.0
- Sistema con servicios hardcodeados
- Documentos genéricos

### v1.0.0
- Versión inicial básica

---

**Desarrollado con ❤️ para la comunidad AWS**
