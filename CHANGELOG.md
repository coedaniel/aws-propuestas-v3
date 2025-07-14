# Changelog - AWS Propuestas v3

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.2.2] - 2025-07-14

### 🚀 Optimización Crítica de Performance
- **MAJOR**: Optimización crítica del paquete Lambda arquitecto
  - Eliminada dependencia innecesaria de pandas (reducción de ~50MB)
  - Tamaño del paquete reducido de 70MB+ a 21MB (70% de reducción)
  - Resuelto `RequestEntityTooLargeException` en despliegues Lambda
  - Mejora significativa en tiempos de arranque en frío

### 🐛 Correcciones de Código
- Corregidos errores de sintaxis en `working_intelligent_generator.py`
- Eliminados bloques de código duplicados
- Corregida indentación en `app.py` línea 162
- Validación de sintaxis Python implementada antes del despliegue

### 🔧 Mejoras Técnicas
- Requirements.txt optimizado con dependencias esenciales únicamente:
  - boto3>=1.26.0, botocore>=1.29.0, python-docx>=0.8.11
  - lxml>=4.9.0, PyYAML>=6.0, charset-normalizer>=3.0.0
- Eliminadas librerías de prueba y documentación innecesarias
- Proceso de empaquetado optimizado para Lambda
- Función desplegada exitosamente en producción

## [3.2.1] - 2025-07-14

### 🔧 Correcciones Críticas
- **Lógica de Generación de Documentos**: Corregida condición redundante que impedía la generación
- **Verificación de Completitud**: Mejorada lógica para generar documentos cuando la extracción O verificación original pasan
- **Logging de Debug**: Mejorado logging de estado de completitud para mejor troubleshooting
- **Flujo de Generación**: Simplificadas condiciones de activación de generación de documentos

### 🎯 Mejoras Técnicas
- Eliminada condición redundante `has_enough_info` en verificación de generación
- Agregado logging detallado para debugging de estado de completitud
- Mejorada lógica OR para detección de completitud de proyecto
- Mejor separación de lógica de validación de completitud

## [3.2.0] - 2025-07-14

### 🚀 ACTUALIZACIÓN MAYOR: Sistema de Arquitecto Inteligente

#### Agregado
- **Extracción Inteligente de Parámetros**: Detección automática de servicio AWS, descripción del proyecto y objetivos desde conversación natural
- **Generación de Documentos Específicos por Servicio**: Todos los documentos ahora adaptados al servicio AWS específico mencionado (LEX, Lambda, API Gateway, etc.)
- **Validación Automática de Respuestas**: Sistema de puntuación de calidad (0-100 puntos) con detección automática de respuestas genéricas
- **Flujo de Conversación Adaptativo**: Conversación natural que se adapta al orden y estilo de entrada del usuario
- **Dashboard de Métricas de Calidad**: Reporte de puntuación de calidad y validación en tiempo real
- **Ingeniería de Prompts Inteligente**: Prompts reforzados que fuerzan al modelo a enfocarse en servicios específicos
- **Mecanismo de Reintento**: Reintento automático para respuestas de baja calidad o genéricas

#### Cambiado
- **Motor de Generación de Documentos**: Renovación completa de plantillas genéricas a contenido específico impulsado por IA
- **Lógica de Conversación**: De script rígido a flujo de conversación adaptativo y natural
- **Sistema de Validación**: De verificaciones básicas de completitud a validación integral de calidad
- **Nomenclatura de Archivos**: Convención de nomenclatura específica por servicio (ej. `propuesta-lex.txt`, `costos-lambda.csv`)
- **Calidad de Respuesta**: Mínimo 3 menciones del servicio objetivo requeridas en todos los entregables

#### Corregido
- **Problema de Documentos Genéricos**: Eliminadas todas las plantillas genéricas y contenido repetitivo
- **Detección de Servicios**: Mejorada la precisión en detectar el servicio AWS deseado por el usuario
- **Relevancia del Contenido**: Todo el contenido generado ahora específico al caso de uso exacto del usuario
- **Brechas de Validación**: Agregada validación integral para prevenir respuestas genéricas

#### Mejoras Técnicas
- Nuevo `simple_intelligent_generator.py` con extracción de parámetros y validación
- Ingeniería de prompts mejorada con requisitos explícitos de enfoque en servicios
- Puntuación automática de calidad y detección de problemas
- Subida a S3 con organización de archivos específica por servicio
- Logging integral y monitoreo para calidad de generación de documentos

## [3.1.0] - 2025-07-14

### Agregado
- **Selector de Modelo Compacto**: Interfaz de selección de modelo optimizada para mejor experiencia de chat
- **Optimización de Espacio**: Mejor utilización del espacio vertical en la página del arquitecto
- **UX Mejorada**: Interfaz de chat más enfocada con menos desorden visual

### Cambiado
- Selector de modelo de componente Card completo a formato compacto en línea
- Asignación mejorada de espacio para interfaz de chat
- Mantenida toda la funcionalidad de selección de modelo en menor espacio

### Corregido
- Posicionamiento de interfaz de chat y utilización de espacio
- Jerarquía visual del selector de modelo

## [3.0.0] - 2025-07-13

### 🎉 LANZAMIENTO MAYOR: Renovación Completa de la Aplicación

#### Agregado
- **Dashboard de Analytics**: Página de analytics integral con gráficos, KPIs e insights de rendimiento
- **Visualización de Tendencias de Proyectos**: Gráficos interactivos mostrando distribución de estados de proyectos
- **Seguimiento de Uso de Servicios AWS**: Uso de servicios principales con indicadores visuales
- **Línea de Tiempo de Actividad**: Actividad reciente de proyectos con timestamps detallados
- **Insights de Rendimiento**: Recomendaciones y sugerencias de optimización
- **Sistema de Navegación Unificado**: Navegación de header consistente en todas las páginas
- **Búsqueda y Filtrado Avanzado**: Búsqueda mejorada de proyectos con múltiples opciones de filtro
- **Modal de Visualizador de Documentos**: Modal grande (max-w-6xl) para mejor visualización de documentos
- **Flujo de Creación de Proyectos**: Flujo mejorado con auto-redirección a página de arquitecto
- **Funcionalidad de Eliminación**: Eliminación completa de proyectos incluyendo limpieza de documentos S3

#### Cambiado
- **UX de Página de Proyectos**: Removida animación de máquina de escribir para mostrar contenido inmediatamente
- **Funcionalidad de Búsqueda**: Renovación completa con lógica de filtrado apropiada
- **Diseño de Homepage**: Reducido texto descriptivo para mejor enfoque
- **Estructura de Navegación**: Agregado enlace de Analytics y resaltado de página activa
- **Responsividad Móvil**: Navegación y layouts mejorados para móviles
- **Manejo de Errores**: Mejorados estados de error e indicadores de carga

#### Corregido
- **Botón 'Crear Primer Proyecto'**: Ahora completamente funcional con enrutamiento correcto
- **Lógica de Búsqueda y Filtro**: Corregido mapeo de estados y operaciones de filtro
- **Errores de TypeScript**: Resueltos todos los problemas de importación y definición de tipos
- **Gestión de Estado**: Mejor manejo de estados y actualizaciones de proyectos
- **Estructura de Componentes**: Optimizada jerarquía de componentes y flujo de datos

#### Mejoras Técnicas
- Nuevo componente AppLayout con navegación unificada
- Componentes UI Badge y Dialog mejorados con Radix UI
- Definiciones de TypeScript mejoradas y manejo de errores
- Mejor gestión de estado en todas las páginas
- Proceso de build optimizado y configuración de exportación estática

## [2.0.0] - 2025-07-10

### Agregado
- Arquitectura inicial de AWS Propuestas v3
- Next.js 14 con App Router
- Integración con AWS Bedrock
- Persistencia de datos con DynamoDB
- Almacenamiento de documentos en S3
- Soporte multi-modelo de IA (Claude, Nova)
- Generación básica de documentos
- Sistema de gestión de proyectos

### Cambiado
- Reescritura completa desde arquitectura v2
- React moderno con TypeScript
- Backend serverless con AWS Lambda
- Seguridad mejorada con roles IAM

### Removido
- Componentes y dependencias legacy de v2
- Sistema de autenticación antiguo
- Endpoints de API deprecados

## [1.0.0] - 2024-12-01

### Agregado
- Lanzamiento inicial de AWS Propuestas v2
- Generación básica de propuestas
- Integración simple con servicios AWS
- Funcionalidad básica de exportación de documentos
