# 📦 Store - Estado Global

Esta carpeta contiene los stores de Zustand para el manejo del estado global de la aplicación.

## 🏪 Stores Disponibles

### 💬 `chatStore.ts`
**Estado del sistema de chat**
- Gestión de sesiones de chat
- Historial de mensajes
- Estado de carga y errores
- Persistencia local de conversaciones

```typescript
// Uso
import { useChatStore } from '@/store/chatStore'

const { messages, addMessage, currentSession } = useChatStore()
```

### 🏗️ `arquitectoStore.ts`
**Estado del módulo arquitecto**
- Configuración de arquitecturas AWS
- Templates y diagramas generados
- Estado de generación de propuestas

```typescript
// Uso
import { useArquitectoStore } from '@/store/arquitectoStore'

const { currentArchitecture, generateDiagram } = useArquitectoStore()
```

### 📋 `projectsStore.ts`
**Estado de gestión de proyectos**
- Lista de proyectos activos
- Metadatos de proyectos
- Estado de sincronización

```typescript
// Uso
import { useProjectsStore } from '@/store/projectsStore'

const { projects, addProject, updateProject } = useProjectsStore()
```

## 🔧 Características

- **🔄 Persistencia**: Los datos se guardan automáticamente en localStorage
- **🛠️ DevTools**: Integración con Redux DevTools para debugging
- **⚡ Performance**: Estado optimizado con Zustand
- **🎯 TypeScript**: Completamente tipado para mejor DX

## 📱 Integración

Los stores están integrados con:
- **Next.js App Router** - SSR compatible
- **TypeScript** - Tipos seguros
- **Componentes React** - Hooks reactivos
- **Persistencia** - localStorage automático

---

**🚀 Estado global moderno con Zustand**
