# 🧩 Components - Componentes React

Esta carpeta contiene todos los componentes React reutilizables de la aplicación.

## 🏗️ Estructura de Componentes

### 📱 **Componentes Principales**

#### `AppLayout.tsx`
**Layout principal de la aplicación**
- Estructura base con sidebar y contenido principal
- Navegación responsive
- Integración con el estado global

#### `Sidebar.tsx`
**Barra lateral de navegación**
- Menú de navegación principal
- Enlaces a diferentes secciones
- Estado activo de rutas

#### `ModelSelector.tsx`
**Selector de modelos de IA**
- Selección de modelos Bedrock
- Configuración de parámetros
- Estado de modelo activo

#### `mcp-status.tsx`
**Monitor de estado MCP**
- Estado de servicios MCP
- Health checks en tiempo real
- Indicadores visuales de conectividad

### 🎨 **Componentes UI (shadcn/ui)**

La carpeta `ui/` contiene componentes base del sistema de diseño:

#### Componentes Disponibles
- **`badge.tsx`** - Badges y etiquetas
- **`button.tsx`** - Botones con variantes
- **`card.tsx`** - Tarjetas de contenido
- **`dialog.tsx`** - Modales y diálogos
- **`input.tsx`** - Campos de entrada
- **`textarea.tsx`** - Áreas de texto

## 🎯 Patrones de Uso

### Importación de Componentes
```typescript
// Componentes principales
import { AppLayout } from '@/components/AppLayout'
import { Sidebar } from '@/components/Sidebar'

// Componentes UI
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
```

### Integración con Estado
```typescript
// Uso con Zustand stores
import { useChatStore } from '@/store/chatStore'

const MyComponent = () => {
  const { messages } = useChatStore()
  return <div>{/* componente */}</div>
}
```

## 🎨 Sistema de Diseño

- **Framework**: Tailwind CSS
- **Componentes Base**: shadcn/ui
- **Iconos**: Lucide React
- **Responsive**: Mobile-first design

## 🔧 Características

- **⚡ Performance**: Componentes optimizados
- **🎯 TypeScript**: Completamente tipados
- **📱 Responsive**: Diseño adaptativo
- **♿ Accesibilidad**: Componentes accesibles
- **🎨 Consistencia**: Sistema de diseño unificado

## 📦 Dependencias

- React 18+
- Next.js 14+
- Tailwind CSS
- shadcn/ui
- Lucide React

---

**🧩 Componentes modernos y reutilizables**
