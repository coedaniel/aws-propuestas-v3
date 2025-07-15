# ⚙️ Archivos de Configuración

Esta guía explica todos los archivos de configuración en la raíz del proyecto.

## 🚀 **Configuración de Amplify**

### `amplify.yml`
**Configuración de build para AWS Amplify**
- Define las fases de build (preBuild, build, postBuild)
- Configura variables de entorno para producción
- Especifica comandos de instalación y construcción

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci
    build:
      commands:
        - npm run build
```

### `amplify-env-vars.json` & `amplify-env-vars-updated.json`
**Variables de entorno para Amplify**
- Configuración de URLs de servicios MCP
- Variables específicas del entorno de producción
- Backup de configuraciones anteriores

## 🔧 **Configuración de Next.js**

### `next.config.js`
**Configuración principal de Next.js**
- Configuración de dominios de imágenes
- Headers de seguridad y CORS
- Optimizaciones de build

### `next-env.d.ts`
**Tipos de TypeScript para Next.js**
- Generado automáticamente
- No modificar manualmente

## 📦 **Gestión de Dependencias**

### `package.json`
**Configuración del proyecto Node.js**
- Dependencias de producción y desarrollo
- Scripts de build, dev, lint, etc.
- Metadatos del proyecto

### `package-lock.json`
**Lock file de dependencias**
- Versiones exactas de todas las dependencias
- Generado automáticamente por npm
- Asegura builds reproducibles

## 🎨 **Configuración de Estilos**

### `tailwind.config.js`
**Configuración de Tailwind CSS**
- Paths de contenido para purging
- Tema personalizado (colores, fuentes, etc.)
- Plugins adicionales

### `postcss.config.js`
**Configuración de PostCSS**
- Plugins para procesamiento de CSS
- Integración con Tailwind CSS

## 🔍 **Configuración de TypeScript**

### `tsconfig.json`
**Configuración del compilador TypeScript**
- Opciones del compilador
- Paths de módulos
- Configuración de tipos

## 🌍 **Variables de Entorno**

### `.env.local.example`
**Plantilla de variables de entorno**
- Ejemplo de todas las variables necesarias
- Documentación de cada variable
- Copiar a `.env.local` para desarrollo

#### Variables Principales:
```bash
# AWS
AWS_REGION=us-east-1
AWS_PROFILE=default

# Bedrock
BEDROCK_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# MCP Services
NEXT_PUBLIC_MCP_BASE_URL=https://mcp.danielingram.shop
```

## 📋 **Archivos de Documentación**

### Documentación Principal
- `README.md` - Introducción y guía principal
- `ARCHITECTURE.md` - Documentación de arquitectura
- `API.md` - Documentación de API
- `DEPLOYMENT.md` - Guía de despliegue
- `CONTRIBUTING.md` - Guía de contribución
- `TROUBLESHOOTING.md` - Solución de problemas
- `CHANGELOG.md` - Historial de cambios

## 🔧 **Configuración de Git**

### `.gitignore`
**Archivos ignorados por Git**
- `node_modules/`
- `.env.local`
- `.next/`
- Archivos de build y temporales

## 📊 **Jerarquía de Configuración**

```
Configuración del Proyecto
├── 🚀 Amplify (amplify.yml, amplify-env-vars.json)
├── ⚛️ Next.js (next.config.js, next-env.d.ts)
├── 📦 Node.js (package.json, package-lock.json)
├── 🎨 Estilos (tailwind.config.js, postcss.config.js)
├── 🔍 TypeScript (tsconfig.json)
├── 🌍 Entorno (.env.local.example)
└── 📋 Documentación (*.md)
```

---

**⚙️ Configuración optimizada para desarrollo y producción**
