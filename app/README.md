# 📱 App - Next.js App Router

Esta carpeta contiene la estructura de rutas y páginas de la aplicación usando Next.js 14 App Router.

## 🗂️ Estructura de Rutas

### 📄 **Páginas Principales**

#### `/` - `page.tsx`
**Página de inicio**
- Dashboard principal
- Acceso rápido a funcionalidades
- Estado del sistema

#### `/chat` - `chat/page.tsx`
**Interfaz de chat conversacional**
- Chat con IA para generar propuestas
- Integración con servicios MCP
- Historial de conversaciones

#### `/arquitecto` - `arquitecto/page.tsx`
**Generador de arquitecturas**
- Creación de diagramas AWS
- Templates de arquitectura
- Exportación de diagramas

#### `/projects` - `projects/page.tsx`
**Gestión de proyectos**
- Lista de proyectos activos
- Creación y edición de proyectos
- Metadatos y configuración

#### `/analytics` - `analytics/page.tsx`
**Panel de analíticas**
- Métricas de uso
- Estadísticas de generación
- Reportes de rendimiento

#### `/system-status` - `system-status/page.tsx`
**Estado del sistema**
- Health checks de servicios MCP
- Monitoreo en tiempo real
- Diagnósticos de conectividad

### 🔌 **API Routes**

#### `/api/mcp-proxy`
**Proxy para servicios MCP**
- Intermediario entre frontend y servicios MCP
- Manejo de CORS
- Autenticación y autorización

## 🎨 **Archivos Globales**

### `layout.tsx`
**Layout raíz de la aplicación**
- Configuración global de HTML
- Providers de estado
- Metadatos y SEO

### `globals.css`
**Estilos globales**
- Configuración de Tailwind CSS
- Variables CSS personalizadas
- Estilos base de la aplicación

## 🚀 **Características del App Router**

- **📁 File-based routing** - Rutas basadas en estructura de archivos
- **🔄 Server Components** - Renderizado del lado del servidor por defecto
- **⚡ Streaming** - Carga progresiva de contenido
- **🎯 TypeScript** - Soporte completo de tipos
- **📱 Responsive** - Diseño adaptativo

## 🛠️ **Integración con MCP**

Todas las páginas están integradas con los servicios MCP:

```typescript
// Ejemplo de integración
const response = await fetch('/api/mcp-proxy/core', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ action: 'generate' })
})
```

## 📊 **Estado y Datos**

- **Estado Global**: Zustand stores
- **Datos Remotos**: Servicios MCP via API routes
- **Persistencia**: localStorage para datos del cliente
- **Cache**: Next.js built-in caching

---

**📱 Aplicación Next.js moderna con App Router**
