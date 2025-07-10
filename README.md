# 🚀 AWS Propuestas v3 - Sistema Conversacional Profesional

Sistema conversacional profesional basado en Next.js y AWS para generar propuestas ejecutivas de soluciones en la nube. Incluye modo libre con IA y un modo guiado "Arquitecto AWS" que genera todos los entregables: Word, CSV, YAML, diagramas y subida a S3.

## ✨ Características Principales

### 🤖 **Chat Libre con IA**
- Conversación natural con múltiples modelos de Amazon Bedrock
- Selección dinámica entre Nova Pro, Claude Haiku y Claude Sonnet
- Historial persistente de conversaciones
- Respuestas expertas en AWS y arquitectura cloud

### 🏗️ **Modo Arquitecto AWS**
- Entrevista guiada paso a paso para capturar requerimientos
- Generación automática de entregables profesionales
- Flujo inteligente que se adapta al tipo de proyecto
- Almacenamiento completo en DynamoDB y S3

### 📄 **Generación Automática de Documentos**
- **Documento Word**: Propuesta ejecutiva profesional
- **CSV de Actividades**: Plan de implementación detallado
- **CSV de Costos**: Estimación de servicios AWS
- **CloudFormation YAML**: Scripts de infraestructura
- **Diagramas**: SVG, PNG y archivos .drawio editables
- **Guía de Calculadora**: Instrucciones para AWS Pricing Calculator

### 📊 **Dashboard de Proyectos**
- Vista completa de todos los proyectos generados
- Filtros por estado, fecha y tipo
- Descarga directa de documentos desde S3
- Métricas y estadísticas de uso

## 🛠️ Stack Tecnológico

### Frontend
- **Next.js 14** con App Router y Server Components
- **React 18** con hooks modernos
- **Tailwind CSS** para estilos responsivos
- **shadcn/ui** para componentes de interfaz
- **Zustand** para manejo de estado global
- **TypeScript** para tipado estático

### Backend
- **Next.js API Routes** para endpoints REST
- **AWS Lambda** (opcional) para procesamiento pesado
- **Amazon Bedrock** para modelos de IA
- **DynamoDB** para persistencia de datos
- **Amazon S3** para almacenamiento de documentos

### Despliegue
- **AWS Amplify Hosting** para frontend
- **CloudFormation/SAM** para infraestructura
- **GitHub Actions** para CI/CD

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend APIs   │    │   AWS Services  │
│   (Next.js)     │◄──►│   (Next.js)      │◄──►│                 │
│                 │    │                  │    │ • Bedrock       │
│ • Chat UI       │    │ • /api/chat      │    │ • DynamoDB      │
│ • Arquitecto UI │    │ • /api/arquitecto │    │ • S3            │
│ • Projects UI   │    │ • /api/projects  │    │ • Lambda        │
│ • Model Select  │    │ • Document Gen   │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Instalación y Configuración

### Prerrequisitos
- Node.js 18+ y npm
- AWS CLI configurado
- Cuenta AWS con permisos para Bedrock, DynamoDB y S3

### 1. Clonar el repositorio
```bash
git clone https://github.com/coedaniel/aws-propuestas-v3.git
cd aws-propuestas-v3
```

### 2. Instalar dependencias
```bash
npm install
```

### 3. Configurar variables de entorno
```bash
cp .env.local.example .env.local
# Editar .env.local con tus configuraciones
```

### 4. Configurar AWS
```bash
# Configurar credenciales AWS
aws configure

# Habilitar modelos en Bedrock (si es necesario)
aws bedrock put-model-invocation-logging-configuration \
  --logging-config cloudWatchConfig='{logGroupName="/aws/bedrock/modelinvocations",roleArn="arn:aws:iam::ACCOUNT:role/service-role/AmazonBedrockExecutionRoleForLogging"}'
```

### 5. Ejecutar en desarrollo
```bash
npm run dev
```

La aplicación estará disponible en `http://localhost:3000`

## 📁 Estructura del Proyecto

```
aws-propuestas-v3/
├── app/                          # Next.js App Router
│   ├── api/                      # API Routes
│   │   ├── chat/route.ts         # Chat libre endpoint
│   │   ├── arquitecto/route.ts   # Arquitecto endpoint
│   │   └── projects/route.ts     # Proyectos endpoint
│   ├── chat/page.tsx             # Página de chat libre
│   ├── arquitecto/page.tsx       # Página de arquitecto
│   ├── projects/page.tsx         # Dashboard de proyectos
│   ├── layout.tsx                # Layout principal
│   ├── page.tsx                  # Página de inicio
│   └── globals.css               # Estilos globales
├── components/                   # Componentes React
│   ├── ui/                       # Componentes base (shadcn/ui)
│   ├── chat/                     # Componentes de chat
│   ├── arquitecto/               # Componentes de arquitecto
│   ├── projects/                 # Componentes de proyectos
│   └── ModelSelector.tsx         # Selector de modelos IA
├── lib/                          # Utilidades y configuración
│   ├── types/index.ts            # Definiciones de tipos
│   ├── utils.ts                  # Funciones utilitarias
│   └── aws/                      # Clientes AWS
├── store/                        # Estado global (Zustand)
│   ├── chatStore.ts              # Estado del chat
│   ├── arquitectoStore.ts        # Estado del arquitecto
│   └── projectsStore.ts          # Estado de proyectos
├── lambda/                       # Funciones Lambda (opcional)
│   ├── arquitecto/               # Lógica del arquitecto
│   │   ├── app.py                # Handler principal
│   │   ├── generators/           # Generadores de documentos
│   │   └── utils/                # Utilidades
│   └── shared/                   # Código compartido
├── infrastructure/               # CloudFormation/SAM
│   └── template.yaml             # Template de infraestructura
├── scripts/                      # Scripts de deployment
│   ├── deploy.sh                 # Deploy completo
│   ├── deploy-frontend.sh        # Deploy frontend
│   └── deploy-backend.sh         # Deploy backend
└── docs/                         # Documentación
    ├── API.md                    # Documentación de APIs
    ├── DEPLOYMENT.md             # Guía de despliegue
    └── ARCHITECTURE.md           # Arquitectura detallada
```

## 🔧 Configuración de AWS

### IAM Policy Mínima
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "dynamodb:*",
        "s3:*"
      ],
      "Resource": "*"
    }
  ]
}
```

### Servicios AWS Requeridos
- **Amazon Bedrock**: Modelos de IA (Nova Pro, Claude)
- **DynamoDB**: 2 tablas (proyectos y sesiones de chat)
- **S3**: 1 bucket para documentos generados
- **Lambda**: Funciones para generación de documentos (opcional)
- **API Gateway**: Para APIs REST (si se usa Lambda)

## 🎯 Flujo de Uso

### Chat Libre
1. Seleccionar modelo de IA (Nova Pro, Claude Haiku, etc.)
2. Hacer preguntas sobre AWS y arquitectura
3. Recibir respuestas expertas y personalizadas
4. Historial automático de conversaciones

### Modo Arquitecto
1. Iniciar nuevo proyecto
2. Responder entrevista guiada paso a paso
3. El sistema captura todos los requerimientos
4. Generación automática de documentos
5. Subida a S3 y notificación de completado
6. Descarga desde dashboard de proyectos

## 📊 Modelos de IA Disponibles

| Modelo | Proveedor | Uso Recomendado | Costo/1k tokens |
|--------|-----------|-----------------|-----------------|
| Nova Pro | Amazon | Análisis complejo, conversaciones largas | $0.008 |
| Claude Haiku | Anthropic | Respuestas rápidas, tareas técnicas | $0.0025 |
| Claude Sonnet | Anthropic | Balance velocidad/capacidad | $0.015 |

## 🚀 Despliegue en Producción

### Opción 1: AWS Amplify (Recomendado)
```bash
# Conectar repositorio a Amplify
aws amplify create-app --name aws-propuestas-v3 --repository https://github.com/tu-usuario/aws-propuestas-v3

# Configurar variables de entorno en Amplify Console
# Desplegar automáticamente con cada push
```

### Opción 2: Manual con scripts
```bash
# Desplegar backend
./scripts/deploy-backend.sh

# Desplegar frontend
./scripts/deploy-frontend.sh

# Verificar despliegue
./scripts/verify-deployment.sh
```

## 🧪 Testing

```bash
# Tests unitarios
npm test

# Tests de integración
npm run test:integration

# Tests E2E
npm run test:e2e
```

## 📈 Monitoreo y Logs

- **CloudWatch**: Logs de Lambda y métricas
- **X-Ray**: Trazabilidad de requests
- **Bedrock Logs**: Uso de modelos IA
- **Amplify Console**: Métricas de frontend

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 Soporte

- **Issues**: [GitHub Issues](https://github.com/coedaniel/aws-propuestas-v3/issues)
- **Documentación**: Ver carpeta `/docs`
- **Email**: daniel@ejemplo.com

## 🎉 Changelog

### v3.0.0 (2024-07-10)
- ✨ Sistema conversacional completo con múltiples modelos IA
- 🏗️ Modo Arquitecto con generación automática de documentos
- 📊 Dashboard de proyectos con métricas
- 🚀 Despliegue optimizado en AWS Amplify
- 📱 UI/UX completamente rediseñada
- 🔒 Seguridad mejorada con IAM roles específicos

---

**Desarrollado con ❤️ para la comunidad AWS**
