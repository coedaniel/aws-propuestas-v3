# Guía de Desarrollo - AWS Propuestas v3

## 🛠️ Configuración del Entorno de Desarrollo

### Prerrequisitos
- Node.js >= 18.0.0
- npm >= 8.0.0
- Git
- Acceso a AWS (para testing)

### Instalación Local
```bash
# Clonar repositorio
git clone https://github.com/coedaniel/aws-propuestas-v3.git
cd aws-propuestas-v3

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env.local
# Editar .env.local con las configuraciones necesarias

# Ejecutar en modo desarrollo
npm run dev
```

## 🏗️ Arquitectura de Desarrollo

### Estructura del Proyecto
```
aws-propuestas-v3/
├── app/                    # Next.js App Router
│   ├── arquitecto/         # Chat del arquitecto
│   ├── projects/           # Gestión de proyectos
│   └── system-status/      # Estado del sistema
├── components/             # Componentes React
│   ├── ui/                 # Componentes base
│   └── mcp-transparency/   # Componentes MCP
├── lib/                    # Utilidades y configuración
│   ├── api.ts             # Cliente API
│   ├── types/             # Definiciones TypeScript
│   └── mcp-client.ts      # Cliente MCP
├── official-mcp-servers/   # Servicios MCP oficiales
├── custom-mcp-servers/     # Servicios MCP personalizados
└── infrastructure/         # CloudFormation templates
```

### Flujo de Datos
```
Frontend (Next.js) 
    ↓
API Gateway (/arquitecto)
    ↓
Lambda (Chat Arquitecto)
    ↓
Amazon Bedrock (Nova Pro / Claude)
    ↓ (cuando necesario)
MCP Services (ECS)
    ↓
DynamoDB / S3
```

## 🔧 Comandos de Desarrollo

### Scripts Disponibles
```bash
# Desarrollo
npm run dev          # Servidor de desarrollo
npm run build        # Build de producción
npm run start        # Servidor de producción
npm run lint         # Linting
npm run type-check   # Verificación de tipos

# Testing
npm run test         # Tests unitarios
npm run test:e2e     # Tests end-to-end
```

### Variables de Entorno
```bash
# .env.local
NEXT_PUBLIC_API_URL=https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod
NEXT_PUBLIC_MCP_CORE_URL=http://localhost:8000  # Para desarrollo local
NEXT_PUBLIC_MCP_PRICING_URL=http://localhost:8001
# ... otras URLs MCP
```

## 🧪 Testing

### Testing Local
```bash
# Verificar que el frontend carga
curl http://localhost:3000

# Verificar API
curl https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod/health

# Verificar modelos de IA
curl -X POST https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod/arquitecto \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "hola"}], "selected_model": "amazon.nova-pro-v1:0"}'
```

### Testing de Componentes
- **Frontend**: Tests con Jest + React Testing Library
- **API**: Tests de integración con endpoints reales
- **MCP**: Tests unitarios de servicios

## 🚀 Despliegue

### Desarrollo → Staging → Producción
1. **Desarrollo**: Cambios locales
2. **Commit**: Push a branch feature
3. **PR**: Pull Request a main
4. **Review**: Code review
5. **Merge**: Merge a main
6. **Deploy**: Amplify auto-deploy

### Amplify Configuration
```yaml
# amplify.yml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: out
    files:
      - '**/*'
```

## 🔍 Debugging

### Logs de Desarrollo
```bash
# Frontend logs
npm run dev  # Ver en consola

# API logs (CloudWatch)
aws logs tail /aws/lambda/aws-propuestas-v3-arquitecto-prod --follow

# MCP Services logs
docker logs <container-id>  # Si corriendo localmente
```

### Herramientas de Debug
- **React DevTools**: Para componentes
- **Network Tab**: Para llamadas API
- **CloudWatch**: Para logs de producción
- **Amplify Console**: Para builds y deploys

## 📝 Convenciones de Código

### TypeScript
- Usar tipos estrictos
- Interfaces para props de componentes
- Enums para constantes

### React
- Componentes funcionales con hooks
- Props destructuring
- Naming: PascalCase para componentes

### Git
- Commits descriptivos
- Branches: `feature/nombre-feature`
- PRs con descripción detallada

### Estructura de Archivos
```typescript
// Ejemplo de componente
interface ComponentProps {
  title: string;
  onAction: () => void;
}

export default function Component({ title, onAction }: ComponentProps) {
  // Lógica del componente
  return (
    <div>
      <h1>{title}</h1>
      <button onClick={onAction}>Acción</button>
    </div>
  );
}
```

## 🐛 Solución de Problemas Comunes

### Build Failures
```bash
# Limpiar cache
rm -rf .next node_modules
npm install
npm run build
```

### Problemas de CORS
- Verificar configuración en API Gateway
- Comprobar headers en requests

### Errores de Bedrock
- Verificar formato de mensajes
- Confirmar que primer mensaje es 'user'
- Revisar permisos IAM

## 📚 Recursos Adicionales

- [Next.js Documentation](https://nextjs.org/docs)
- [AWS Amplify Docs](https://docs.amplify.aws/)
- [Amazon Bedrock API](https://docs.aws.amazon.com/bedrock/)
- [MCP Protocol](https://modelcontextprotocol.io/)

## 🤝 Contribución

1. Fork del repositorio
2. Crear branch feature
3. Desarrollar y testear
4. Crear Pull Request
5. Code review
6. Merge a main

---

**Última actualización**: 2025-07-17  
**Mantenido por**: Equipo de Desarrollo
