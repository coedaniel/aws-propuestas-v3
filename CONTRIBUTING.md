# Guía de Contribución

¡Gracias por tu interés en contribuir a AWS Propuestas v3! Esta guía te ayudará a empezar.

## 🚀 Inicio Rápido

### Prerrequisitos
- Node.js 18+
- Git
- AWS CLI configurado
- Acceso a Amazon Bedrock

### Configuración del Entorno de Desarrollo

1. **Fork y clonar el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/aws-propuestas-v3.git
   cd aws-propuestas-v3
   ```

2. **Instalar dependencias**
   ```bash
   npm install
   ```

3. **Configurar variables de entorno**
   ```bash
   cp .env.example .env.local
   # Editar .env.local con tus configuraciones
   ```

4. **Ejecutar en modo desarrollo**
   ```bash
   npm run dev
   ```

## 📋 Proceso de Contribución

### 1. Crear un Issue
Antes de empezar a trabajar, crea un issue describiendo:
- El problema que quieres resolver
- La funcionalidad que quieres agregar
- Los cambios propuestos

### 2. Crear una Rama
```bash
git checkout -b feature/nombre-descriptivo
# o
git checkout -b fix/descripcion-del-bug
```

### 3. Realizar Cambios
- Sigue las convenciones de código existentes
- Agrega tests si es necesario
- Actualiza la documentación

### 4. Commit y Push
```bash
git add .
git commit -m "feat: descripción del cambio"
git push origin feature/nombre-descriptivo
```

### 5. Crear Pull Request
- Describe claramente los cambios realizados
- Referencia el issue relacionado
- Incluye capturas de pantalla si es relevante

## 🎯 Estándares de Código

### TypeScript
- Usa tipado estricto
- Define interfaces para todos los objetos
- Evita `any` cuando sea posible

### React/Next.js
- Usa componentes funcionales con hooks
- Implementa manejo de errores
- Optimiza el rendimiento con `useMemo` y `useCallback`

### Estilo de Código
```typescript
// ✅ Bueno
interface ProjectData {
  id: string;
  name: string;
  status: 'active' | 'completed';
}

const ProjectCard: React.FC<{ project: ProjectData }> = ({ project }) => {
  return (
    <div className="p-4 border rounded">
      <h3>{project.name}</h3>
      <span className={`status-${project.status}`}>
        {project.status}
      </span>
    </div>
  );
};

// ❌ Evitar
const ProjectCard = (props: any) => {
  return <div>{props.project.name}</div>;
};
```

### Convenciones de Naming
- **Archivos**: kebab-case (`project-card.tsx`)
- **Componentes**: PascalCase (`ProjectCard`)
- **Variables/Funciones**: camelCase (`projectData`)
- **Constantes**: UPPER_SNAKE_CASE (`API_BASE_URL`)

## 🧪 Testing

### Ejecutar Tests
```bash
npm run test          # Tests unitarios
npm run test:watch    # Tests en modo watch
npm run test:coverage # Coverage report
```

### Escribir Tests
```typescript
import { render, screen } from '@testing-library/react';
import { ProjectCard } from './project-card';

describe('ProjectCard', () => {
  it('should render project name', () => {
    const project = {
      id: '1',
      name: 'Test Project',
      status: 'active' as const
    };

    render(<ProjectCard project={project} />);
    
    expect(screen.getByText('Test Project')).toBeInTheDocument();
  });
});
```

## 📝 Convenciones de Commit

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>[scope opcional]: <descripción>

[cuerpo opcional]

[footer opcional]
```

### Tipos de Commit
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Cambios de formato (no afectan funcionalidad)
- `refactor`: Refactorización de código
- `test`: Agregar o modificar tests
- `chore`: Tareas de mantenimiento

### Ejemplos
```bash
feat(arquitecto): agregar detección automática de servicios AWS
fix(chat): corregir error de encoding UTF-8
docs(readme): actualizar guía de instalación
refactor(api): simplificar manejo de errores MCP
```

## 🏗️ Arquitectura del Proyecto

### Estructura de Directorios
```
aws-propuestas-v3/
├── app/                    # Next.js App Router
│   ├── api/               # API Routes
│   ├── arquitecto/        # Páginas del arquitecto
│   ├── chat/              # Chat libre
│   └── projects/          # Gestión de proyectos
├── components/            # Componentes React
│   ├── ui/               # Componentes base
│   └── features/         # Componentes específicos
├── lib/                   # Utilidades y clientes API
├── store/                # Estado global (Zustand)
├── types/                # Definiciones TypeScript
└── utils/                # Funciones helper
```

### Patrones de Diseño

#### 1. Componentes
```typescript
// Componente base con props tipadas
interface ComponentProps {
  title: string;
  onAction: () => void;
}

export const Component: React.FC<ComponentProps> = ({ title, onAction }) => {
  // Lógica del componente
};
```

#### 2. Hooks Personalizados
```typescript
// Hook para lógica reutilizable
export const useProjectData = (projectId: string) => {
  const [data, setData] = useState<ProjectData | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Lógica del hook
  
  return { data, loading, refetch };
};
```

#### 3. Estado Global
```typescript
// Store con Zustand
interface ProjectStore {
  projects: Project[];
  currentProject: Project | null;
  setCurrentProject: (project: Project) => void;
}

export const useProjectStore = create<ProjectStore>((set) => ({
  projects: [],
  currentProject: null,
  setCurrentProject: (project) => set({ currentProject: project }),
}));
```

## 🔧 Servicios MCP

### Agregar Nuevo Servicio MCP

1. **Definir el cliente**
   ```typescript
   // lib/mcp/nuevo-servicio.ts
   export class NuevoServicioMCP {
     private baseUrl: string;
     
     constructor(baseUrl: string) {
       this.baseUrl = baseUrl;
     }
     
     async ejecutarAccion(params: ActionParams): Promise<ActionResult> {
       // Implementación
     }
   }
   ```

2. **Agregar al cliente principal**
   ```typescript
   // lib/mcp/client.ts
   export class MCPClient {
     public nuevoServicio: NuevoServicioMCP;
     
     constructor() {
       this.nuevoServicio = new NuevoServicioMCP(
         process.env.NEXT_PUBLIC_NUEVO_SERVICIO_URL!
       );
     }
   }
   ```

3. **Usar en componentes**
   ```typescript
   const { data } = await mcpClient.nuevoServicio.ejecutarAccion(params);
   ```

## 🐛 Debugging

### Logs de Desarrollo
```typescript
// Usar el logger personalizado
import { logger } from '@/lib/logger';

logger.info('Información general');
logger.error('Error crítico', { error, context });
logger.debug('Información de debug', { data });
```

### Debugging MCP
```typescript
// Habilitar logs detallados de MCP
const mcpClient = new MCPClient({
  debug: process.env.NODE_ENV === 'development'
});
```

## 📚 Recursos Adicionales

- [Next.js Documentation](https://nextjs.org/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)

## ❓ Preguntas Frecuentes

### ¿Cómo pruebo los servicios MCP localmente?
```bash
# Ejecutar servicios MCP en Docker
docker-compose up mcp-services

# Configurar variables de entorno para desarrollo local
NEXT_PUBLIC_MCP_BASE_URL=http://localhost:8000
```

### ¿Cómo agrego un nuevo modelo de IA?
1. Actualizar `lib/bedrock/models.ts`
2. Agregar configuración en `lib/bedrock/client.ts`
3. Actualizar la UI de selección de modelos

### ¿Cómo manejo errores de Bedrock?
```typescript
try {
  const response = await bedrockClient.invokeModel(params);
} catch (error) {
  if (error.name === 'ThrottlingException') {
    // Manejar rate limiting
  } else if (error.name === 'ValidationException') {
    // Manejar errores de validación
  }
  
  logger.error('Error en Bedrock', { error, params });
  throw new BedrockError('Error al procesar solicitud', error);
}
```

## 🤝 Código de Conducta

- Sé respetuoso y constructivo
- Ayuda a otros contribuidores
- Reporta comportamientos inapropiados
- Mantén un ambiente inclusivo y acogedor

---

¡Gracias por contribuir a AWS Propuestas v3! 🚀
