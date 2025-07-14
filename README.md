# AWS Propuestas v3.2.0 🚀

> **Sistema Conversacional Profesional para Generar Propuestas Ejecutivas de Soluciones AWS con IA**

[![Version](https://img.shields.io/badge/version-3.2.0-blue.svg)](https://github.com/coedaniel/aws-propuestas-v3)
[![AWS](https://img.shields.io/badge/AWS-Bedrock%20%7C%20Lambda%20%7C%20S3-orange.svg)](https://aws.amazon.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 🎯 ¿Qué es AWS Propuestas v3?

AWS Propuestas v3 es un **sistema inteligente de arquitectura conversacional** que genera automáticamente propuestas ejecutivas profesionales para soluciones AWS. Utilizando IA avanzada, el sistema mantiene conversaciones naturales con usuarios para entender sus necesidades y crear documentación técnica y comercial específica.

### 🆕 **NUEVO en v3.2.0: Sistema de Arquitecto Inteligente**

- **🧠 Detección Automática de Servicios**: Identifica automáticamente qué servicio AWS necesitas (LEX, Lambda, API Gateway, etc.)
- **📄 Documentos Específicos**: Genera contenido adaptado al servicio específico, no genérico
- **🔍 Validación de Calidad**: Sistema de puntuación automática (0-100) que detecta respuestas genéricas
- **💬 Conversación Natural**: Se adapta a tu estilo de conversación, sin seguir un script rígido
- **⚡ Generación Inteligente**: Todos los documentos centrados en tu caso de uso específico

## ✨ Características Principales

### 🎨 **Interfaz de Usuario Moderna**
- **Dashboard de Analytics**: Visualización completa de proyectos con gráficos interactivos
- **Navegación Unificada**: Header consistente en todas las páginas
- **Búsqueda Avanzada**: Filtros múltiples y búsqueda en tiempo real
- **Visualizador de Documentos**: Modal expandido para mejor lectura
- **Responsive Design**: Optimizado para desktop y móvil

### 🤖 **IA Conversacional Avanzada**
- **Multi-Modelo**: Soporte para Claude 3.5 Sonnet, Claude Haiku, y Amazon Nova Pro
- **Conversación Adaptativa**: Flujo natural que se ajusta a tu estilo de comunicación
- **Detección Inteligente**: Identifica automáticamente servicios AWS y requerimientos
- **Validación Automática**: Previene respuestas genéricas con sistema de calidad

### 📊 **Generación de Documentos Profesionales**
- **📄 Propuesta Ejecutiva**: Documento completo con resumen ejecutivo y solución propuesta
- **🔧 Documento Técnico**: Especificaciones detalladas de arquitectura y configuraciones
- **📈 Plan de Implementación**: Cronograma por fases con actividades específicas
- **💰 Estimación de Costos**: Análisis detallado de costos por servicio AWS
- **🏗️ CloudFormation Template**: Infraestructura como código lista para desplegar
- **📋 Guía de Calculadora AWS**: Instrucciones paso a paso para estimar costos

### 🏗️ **Arquitectura Serverless**
- **Frontend**: Next.js 14 con TypeScript y Tailwind CSS
- **Backend**: AWS Lambda con Python 3.9
- **Base de Datos**: Amazon DynamoDB para persistencia
- **Almacenamiento**: Amazon S3 para documentos generados
- **IA**: Amazon Bedrock con múltiples modelos
- **Despliegue**: AWS Amplify con CI/CD automático

## 🚀 Inicio Rápido

### Prerrequisitos
- Node.js 18+ y npm
- Cuenta AWS con acceso a Bedrock
- AWS CLI configurado

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
# Editar .env.local con tus configuraciones AWS
```

### 4. Ejecutar en Desarrollo
```bash
npm run dev
```

### 5. Acceder a la Aplicación
Abre [http://localhost:3000](http://localhost:3000) en tu navegador.

## 📖 Guías de Uso

### 🎯 **Modo Arquitecto - Conversación Inteligente**

1. **Inicia la Conversación**: Ve a la página "Arquitecto" y describe tu proyecto
   ```
   "Necesito un chatbot para atención al cliente en mi tienda online"
   ```

2. **El Sistema Detecta Automáticamente**:
   - **Servicio**: Amazon LEX (para chatbots)
   - **Descripción**: Chatbot para atención al cliente
   - **Objetivo**: Automatizar soporte en tienda online

3. **Generación Automática**: El sistema crea documentos específicos para LEX:
   - Propuesta ejecutiva centrada en LEX
   - Arquitectura técnica con LEX como componente principal
   - Costos específicos de LEX y servicios complementarios
   - CloudFormation template con recursos de LEX

### 📊 **Dashboard de Analytics**

- **KPIs en Tiempo Real**: Proyectos totales, completados, en progreso
- **Gráficos Interactivos**: Distribución de estados y tendencias
- **Servicios AWS Populares**: Ranking de servicios más utilizados
- **Línea de Tiempo**: Actividad reciente de proyectos

### 🔍 **Gestión de Proyectos**

- **Búsqueda Inteligente**: Por nombre, contenido o ID de proyecto
- **Filtros Avanzados**: Por estado (DRAFT, IN_PROGRESS, COMPLETED)
- **Visualización de Documentos**: Modal expandido para mejor lectura
- **Descarga de Archivos**: Acceso directo a todos los documentos generados

## 🏗️ Arquitectura del Sistema

### Frontend (Next.js 14)
```
app/
├── page.tsx                 # Homepage
├── arquitecto/              # Modo Arquitecto Inteligente
├── projects/                # Gestión de Proyectos
├── analytics/               # Dashboard de Analytics
└── chat/                    # Chat General

components/
├── ui/                      # Componentes UI base
├── AppLayout.tsx            # Layout unificado
├── ModelSelector.tsx        # Selector de modelos IA
└── TypewriterViewer.tsx     # Visualizador de documentos
```

### Backend (AWS Lambda)
```
lambda/
├── arquitecto/              # Sistema Inteligente Principal
│   ├── app.py              # Handler principal
│   └── generators/         # Generadores inteligentes
│       ├── simple_intelligent_generator.py
│       ├── intelligent_architect.py
│       └── smart_document_generator.py
├── projects/               # Gestión de proyectos
├── chat/                   # Chat general
└── documents/              # Generación de documentos
```

### Servicios AWS
- **Amazon Bedrock**: Modelos de IA (Claude, Nova)
- **AWS Lambda**: Lógica de backend serverless
- **Amazon DynamoDB**: Base de datos de proyectos
- **Amazon S3**: Almacenamiento de documentos
- **AWS Amplify**: Hosting y CI/CD
- **Amazon API Gateway**: APIs REST

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# Frontend
NEXT_PUBLIC_API_URL=https://tu-api.execute-api.region.amazonaws.com/prod
NEXT_PUBLIC_ENVIRONMENT=prod
NEXT_PUBLIC_REGION=us-east-1

# Backend (Lambda)
REGION=us-east-1
PROJECTS_TABLE=aws-propuestas-projects
DOCUMENTS_BUCKET=aws-propuestas-documents
```

### Modelos de IA Soportados
- **Amazon Nova Pro**: Modelo por defecto, equilibrado
- **Claude 3 Haiku**: Rápido y económico
- **Claude 3.5 Sonnet**: Más avanzado, razonamiento superior

## 📈 Métricas y Calidad

### Sistema de Validación v3.2.0
- **Puntuación de Calidad**: 0-100 puntos por documento generado
- **Detección de Contenido Genérico**: Automática con alertas
- **Validación de Servicios**: Mínimo 3 menciones del servicio objetivo
- **Métricas de Rendimiento**: Tiempo de generación y calidad de respuesta

### KPIs del Sistema
- **Tiempo Promedio de Generación**: < 30 segundos
- **Calidad Promedio de Documentos**: > 80/100 puntos
- **Tasa de Éxito**: > 95% de documentos específicos (no genéricos)
- **Satisfacción de Usuario**: Medida por especificidad del contenido

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor lee [CONTRIBUTING.md](CONTRIBUTING.md) para detalles sobre nuestro código de conducta y el proceso para enviar pull requests.

### Desarrollo Local
1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📚 Documentación Adicional

- [🏗️ Guía de Arquitectura](ARCHITECTURE.md)
- [🚀 Guía de Despliegue](DEPLOYMENT.md)
- [🔧 Troubleshooting](TROUBLESHOOTING.md)
- [📡 Documentación de API](API.md)
- [📝 Changelog Completo](CHANGELOG.md)

## 🆕 Novedades v3.2.0

### 🎯 **Sistema de Arquitecto Inteligente**
- **Conversación Natural**: Ya no sigue un script rígido
- **Detección Automática**: Identifica servicios AWS automáticamente
- **Documentos Específicos**: Contenido adaptado al servicio detectado
- **Validación de Calidad**: Previene respuestas genéricas
- **Puntuación Automática**: Sistema de calidad 0-100 puntos

### 🔍 **Ejemplos de Detección**
```
Usuario: "Quiero un bot para WhatsApp"
Sistema: Detecta → Amazon LEX + descripción + objetivo
Genera: Documentos específicos para LEX

Usuario: "Necesito una API para mi app móvil"  
Sistema: Detecta → API Gateway + descripción + objetivo
Genera: Documentos específicos para API Gateway
```

## 📞 Soporte

- **Issues**: [GitHub Issues](https://github.com/coedaniel/aws-propuestas-v3/issues)
- **Documentación**: [Wiki del Proyecto](https://github.com/coedaniel/aws-propuestas-v3/wiki)
- **Email**: soporte@aws-propuestas.com

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🙏 Agradecimientos

- **AWS Bedrock Team** por los modelos de IA avanzados
- **Anthropic** por Claude 3.5 Sonnet
- **Amazon** por Nova Pro
- **Next.js Team** por el framework excepcional
- **Vercel** por las herramientas de desarrollo

---

**Desarrollado con ❤️ para la comunidad AWS**

*¿Te gusta el proyecto? ¡Dale una ⭐ en GitHub!*
