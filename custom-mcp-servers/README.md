# 🔧 Custom MCP Servers

Esta carpeta contiene servidores MCP personalizados desarrollados específicamente para AWS Propuestas V3.

## 📦 Servidores Disponibles

### 📝 **Document Generator MCP**
**Generador de documentación personalizada**

#### Funcionalidades
- 📄 Generación de documentos técnicos
- 📊 Templates personalizables
- 🔄 Integración con datos del proyecto
- 📋 Exportación en múltiples formatos

#### Estructura
```
document-generator-mcp/
├── Dockerfile                          # Configuración del contenedor
├── document_generator_mcp.py           # Lógica principal del servidor
├── mcp_http_wrapper.py                 # Wrapper HTTP base
├── mcp_http_wrapper_customdoc.py       # Wrapper específico
├── requirements.txt                    # Dependencias Python
└── src/                               # Código fuente adicional
```

#### Endpoints
- **POST** `/generate` - Genera documentación personalizada
- **GET** `/templates` - Lista templates disponibles
- **GET** `/health` - Health check del servicio

## 🚀 Despliegue

### Desarrollo Local
```bash
cd custom-mcp-servers/document-generator-mcp
pip install -r requirements.txt
python document_generator_mcp.py
```

### Producción (Docker)
```bash
docker build -t custom-doc-mcp .
docker run -p 8005:8005 custom-doc-mcp
```

## 🔧 Configuración

### Variables de Entorno
```bash
PORT=8005
CORS_ORIGINS=https://main.d2xsphsjdxlk24.amplifyapp.com,http://localhost:3000
```

### Integración con Frontend
```typescript
const response = await fetch('/api/mcp-proxy/custom-doc', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    template: 'technical-proposal',
    data: projectData
  })
})
```

## 🎯 Diferencias con Official MCP Servers

| Aspecto | Custom MCP | Official MCP |
|---------|------------|--------------|
| **Propósito** | Funcionalidades específicas del proyecto | Servicios generales AWS |
| **Mantenimiento** | Desarrollado internamente | Mantenido por AWS Labs |
| **Personalización** | Completamente personalizable | Configuración limitada |
| **Despliegue** | Independiente | Parte del stack principal |

## 📊 Estado Actual

✅ **Document Generator MCP**
- ✅ Desarrollado y funcional
- ✅ Dockerizado para despliegue
- ✅ Integrado con frontend
- ✅ Health checks implementados

## 🛠️ Desarrollo

### Agregar Nuevo Servidor MCP
1. Crear nueva carpeta en `custom-mcp-servers/`
2. Implementar lógica MCP
3. Crear Dockerfile
4. Configurar health checks
5. Integrar con frontend

### Estructura Recomendada
```
new-mcp-server/
├── Dockerfile
├── server.py
├── requirements.txt
├── README.md
└── src/
```

---

**🔧 Servidores MCP personalizados para necesidades específicas**
