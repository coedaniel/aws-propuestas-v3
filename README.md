# AWS Propuestas v3

Sistema inteligente de generación automática de propuestas técnicas y comerciales para proyectos AWS. Utiliza IA para analizar conversaciones y generar documentación específica para cada servicio AWS detectado.

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

## 📚 Documentación

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Guía completa de despliegue
- **[API.md](API.md)** - Documentación de la API REST
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Arquitectura del sistema
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Solución de problemas
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Guía de contribución
- **[CHANGELOG.md](CHANGELOG.md)** - Historial de cambios
