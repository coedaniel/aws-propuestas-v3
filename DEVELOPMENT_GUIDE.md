# 🚀 Guía de Desarrollo - AWS Propuestas v3

## 📋 Comandos Esenciales

### 🏠 Desarrollo Local
```bash
# Clonar el repositorio
git clone https://github.com/coedaniel/aws-propuestas-v3.git
cd aws-propuestas-v3

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.local.example .env.local
# Editar .env.local con tus configuraciones

# Iniciar servidor de desarrollo
npm run dev
# Acceder a: http://localhost:3000
```

### 🔧 Scripts Disponibles
```bash
# Desarrollo
npm run dev          # Servidor de desarrollo
npm run build        # Build para producción
npm run start        # Servidor de producción
npm run lint         # Linter ESLint
npm run export       # Exportar estático

# Utilidades personalizadas
./run-local.sh       # Script automático de inicio
```

### 🌐 URLs de Desarrollo Local
- **Dashboard**: http://localhost:3000
- **Arquitecto IA**: http://localhost:3000/arquitecto
- **Proyectos**: http://localhost:3000/proyectos
- **Chat**: http://localhost:3000/chat
- **Analítica**: http://localhost:3000/analitica

## 🏗️ Arquitectura del Proyecto

### 📁 Estructura de Directorios
```
aws-propuestas-v3/
├── app/                    # 📱 Páginas Next.js (App Router)
│   ├── arquitecto/        # 🤖 Chat IA Inteligente
│   ├── proyectos/         # 📁 Gestión de Proyectos
│   ├── chat/              # 💬 Chat Básico
│   ├── analitica/         # 📊 Dashboard Analytics
│   ├── globals.css        # 🎨 Estilos globales
│   ├── layout.tsx         # 📐 Layout principal
│   └── page.tsx           # 🏠 Página de inicio
├── components/            # 🧩 Componentes React reutilizables
│   ├── ui/               # 🎨 Componentes UI base
│   ├── ModelSelector.tsx  # 🤖 Selector de modelos IA
│   └── PromptUnderstanding.tsx # 🧠 Análisis de prompts
├── lib/                   # 📚 Utilidades y tipos
│   ├── types.ts          # 📝 Definiciones TypeScript
│   └── utils.ts          # 🛠️ Funciones utilitarias
├── store/                 # 🗄️ Estado global (Zustand)
│   └── chatStore.ts      # 💬 Estado del chat
├── lambda/                # 🚀 Funciones AWS Lambda
│   ├── chat/             # 💬 Lambda del chat
│   └── arquitecto/       # 🤖 Lambda del arquitecto
├── infrastructure/        # 🏗️ Infraestructura como código
├── official-mcp-servers/  # 🏢 MCPs oficiales de AWS Labs
├── custom-mcp-servers/    # 🔧 MCPs personalizados
├── docs/                  # 📚 Documentación adicional
├── scripts/               # 📜 Scripts de utilidad
├── template.yaml          # 📋 SAM Template principal
├── package.json           # 📦 Configuración npm
├── tailwind.config.js     # 🎨 Configuración Tailwind
├── tsconfig.json          # ⚙️ Configuración TypeScript
└── next.config.js         # ⚙️ Configuración Next.js
```

## 🔧 Configuración de Desarrollo

### 📝 Variables de Entorno (.env.local)
```bash
# API URL (usar endpoint desplegado para desarrollo)
NEXT_PUBLIC_API_URL=https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod

# Configuración AWS (opcional para desarrollo frontend)
AWS_REGION=us-east-1
BEDROCK_REGION=us-east-1
```

### 🎨 Personalización de Estilos
- **Tailwind CSS**: Configuración en `tailwind.config.js`
- **Componentes UI**: Basados en Radix UI en `components/ui/`
- **Estilos globales**: En `app/globals.css`

### 🧩 Componentes Principales

#### 🤖 Arquitecto IA (`app/arquitecto/page.tsx`)
- Chat inteligente con orquestación de MCPs
- Integración con modelos Bedrock
- Generación automática de documentos
- Estado del proyecto en tiempo real

#### 📁 Proyectos (`app/proyectos/page.tsx`)
- Dashboard de proyectos generados
- Filtros y búsqueda avanzada
- Descarga de archivos
- Métricas y estadísticas

#### 💬 Chat (`app/chat/page.tsx`)
- Chat básico con modelos IA
- Selector de modelos
- Historial de conversaciones

## 🚀 Despliegue

### 🏗️ Infraestructura (AWS SAM)
```bash
# Build del proyecto SAM
sam build

# Deploy a AWS
sam deploy --guided

# Deploy rápido (configuración existente)
sam deploy
```

### 🌐 Frontend (AWS Amplify)
- **Auto-deploy** desde GitHub
- **Build automático** en cada push a main
- **CDN global** con CloudFront

## 🔍 Debugging y Troubleshooting

### 📊 Logs y Monitoreo
- **CloudWatch Logs**: Para funciones Lambda
- **Browser DevTools**: Para frontend
- **Network Tab**: Para debugging de API calls

### 🐛 Problemas Comunes
1. **CORS Issues**: Verificar configuración en API Gateway
2. **Build Errors**: Verificar dependencias y TypeScript
3. **API Timeouts**: Revisar configuración de Lambda timeout

### 🔧 Herramientas de Desarrollo
- **ESLint**: Linting de código
- **TypeScript**: Type checking
- **Tailwind**: Utilidades CSS
- **Git**: Control de versiones

## 📚 Recursos Adicionales

### 📖 Documentación
- `README.md`: Documentación principal
- `ARCHITECTURE.md`: Arquitectura del sistema
- `API.md`: Documentación de la API
- `DEPLOYMENT.md`: Guía de despliegue

### 🔗 Enlaces Útiles
- **Repositorio**: https://github.com/coedaniel/aws-propuestas-v3
- **Producción**: https://main.d2xsphsjdxlk24.amplifyapp.com/
- **API Docs**: Incluida en el proyecto

## 🤝 Contribución

### 📝 Flujo de Trabajo
1. Fork del repositorio
2. Crear branch para feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -m "feat: nueva funcionalidad"`
4. Push branch: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

### 📋 Estándares de Código
- **TypeScript**: Tipado estricto
- **ESLint**: Seguir reglas configuradas
- **Commits**: Usar conventional commits
- **Testing**: Incluir tests para nuevas funcionalidades

---

**¡Happy Coding!** 🚀
