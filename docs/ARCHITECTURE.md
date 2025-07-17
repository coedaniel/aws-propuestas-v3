# Arquitectura del Sistema - AWS Propuestas v3

## 🏗️ **ARQUITECTURA ACTUAL - FUNCIONAL**

### **Frontend (Next.js + Amplify)**
```
├── /chat          ✅ Chat libre con Bedrock (estado local)
├── /arquitecto    ✅ Generación de proyectos (Zustand + MCP)
├── /projects      ⚠️  Dashboard (requiere DynamoDB)
└── /system-status ✅ Monitoreo MCP
```

### **Backend (Lambda + API Gateway)**
```
API Gateway: https://jvdvd1qcdj.execute-api.us-east-1.amazonaws.com/prod/
├── /chat          ✅ Chat libre directo a Bedrock
├── /arquitecto    ✅ Proyectos con prompt maestro + MCP
├── /projects      ✅ CRUD de proyectos
├── /documents     ✅ Generación de documentos
└── /health        ✅ Health checks
```

### **Servicios AWS**
- **Bedrock**: Nova Pro + Claude Sonnet
- **Lambda**: 6 funciones especializadas
- **DynamoDB**: Proyectos + Chat Sessions
- **S3**: Documentos generados
- **ECS**: Servicios MCP (opcional)

## 🔧 **GESTIÓN DE ESTADO**

### **Chat Libre (/chat) - Estado Local**
```typescript
// ✅ FUNCIONAL: Estado local simple
const [localMessages, setLocalMessages] = useState<Message[]>([])
const [localLoading, setLocalLoading] = useState(false)

// Renderizado inmediato garantizado
setLocalMessages(prev => [...prev, newMessage])
```

### **Arquitecto (/arquitecto) - Zustand Store**
```typescript
// ✅ APROPIADO: Estado complejo compartido
const {
  sessions,
  currentSessionId,
  messages,
  addMessage,
  setLoading
} = useChatStore()
```

### **Principio de Diseño:**
- **Estado Local**: Para funcionalidad simple y directa
- **Zustand Store**: Para estado complejo compartido entre componentes
- **No sobre-ingenierizar**: Usar la herramienta apropiada

## 🎯 **ENDPOINTS Y COMPORTAMIENTO**

### **Chat Libre (`/chat`)**
- **Propósito**: Chat natural con modelos Bedrock
- **Comportamiento**: Sin restricciones, como consola Bedrock
- **Modelos**: Nova Pro + Claude Sonnet
- **Contexto**: Mantiene historial completo
- **Estado**: Local (useState)

### **Arquitecto (`/arquitecto`)**
- **Propósito**: Generación de proyectos completos
- **Comportamiento**: Prompt maestro + preguntas guiadas
- **MCP**: Servicios cuando necesario
- **Documentos**: Generación automática
- **Estado**: Zustand store

## 📊 **MÉTRICAS DE RENDIMIENTO**

### **Chat Libre**
- **Response Time**: ~8 segundos (Bedrock normal)
- **Success Rate**: 100%
- **User Experience**: Fluido y natural

### **Arquitecto**
- **Response Time**: ~10-15 segundos (con MCP)
- **Success Rate**: 95%
- **Document Generation**: ~30 segundos

## 🚀 **DEPLOYMENT**

### **Frontend (Amplify)**
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

### **Backend (SAM/CloudFormation)**
- **6 Lambda Functions**: Especializadas por funcionalidad
- **API Gateway**: Routing centralizado
- **DynamoDB**: 2 tablas (proyectos + sessions)
- **S3**: Bucket para documentos

---
**Última Actualización**: 2025-07-17  
**Status**: ✅ SISTEMA FUNCIONAL
