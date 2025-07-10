# Documentación de API - AWS Propuestas v3

Esta documentación describe todos los endpoints disponibles en la API de AWS Propuestas v3.

## 📋 Información General

- **Base URL**: `https://tu-api-gateway-url.amazonaws.com/prod`
- **Autenticación**: No requerida (público)
- **Formato**: JSON
- **Encoding**: UTF-8
- **Rate Limiting**: 1000 requests/minuto por IP

## 🔗 Endpoints Disponibles

### 1. Health Check

Verifica el estado de la API.

```http
GET /health
```

**Respuesta Exitosa (200)**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "3.0.0",
  "services": {
    "dynamodb": "healthy",
    "s3": "healthy",
    "bedrock": "healthy"
  }
}
```

**Ejemplo con curl**:
```bash
curl -X GET https://tu-api-gateway-url.amazonaws.com/prod/health
```

---

### 2. Chat Principal (Arquitecto)

Endpoint principal para interactuar con el asistente de arquitectura AWS.

```http
POST /arquitecto
```

**Headers Requeridos**:
```http
Content-Type: application/json
```

**Body**:
```json
{
  "messages": [
    {
      "role": "user",
      "content": "string"
    }
  ],
  "modelId": "string",
  "projectId": "string (opcional)"
}
```

**Parámetros**:
- `messages` (array, requerido): Historial de conversación
  - `role` (string): "user" o "assistant"
  - `content` (string): Contenido del mensaje
- `modelId` (string, requerido): ID del modelo de Bedrock a usar
- `projectId` (string, opcional): ID del proyecto existente

**Respuesta Exitosa (200)**:
```json
{
  "response": "string",
  "projectId": "string",
  "projectName": "string",
  "conversationId": "string",
  "timestamp": "2024-01-15T10:30:00Z",
  "modelUsed": "anthropic.claude-3-haiku-20240307-v1:0",
  "tokensUsed": 150
}
```

**Ejemplo con curl**:
```bash
curl -X POST https://tu-api-gateway-url.amazonaws.com/prod/arquitecto \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Necesito una arquitectura para un sistema de detección de amenazas con GuardDuty"
      }
    ],
    "modelId": "anthropic.claude-3-haiku-20240307-v1:0"
  }'
```

---

### 3. Generar Documentos

Genera documentos técnicos basados en el análisis de la conversación.

```http
POST /generate-documents
```

**Headers Requeridos**:
```http
Content-Type: application/json
```

**Body**:
```json
{
  "projectId": "string",
  "documentTypes": ["string"],
  "analysis": "string (opcional)"
}
```

**Parámetros**:
- `projectId` (string, requerido): ID del proyecto
- `documentTypes` (array, requerido): Tipos de documentos a generar
  - Valores posibles: `["cloudformation", "costs", "guide", "word", "diagram"]`
- `analysis` (string, opcional): Análisis personalizado del proyecto

**Respuesta Exitosa (200)**:
```json
{
  "success": true,
  "projectId": "string",
  "documentsGenerated": [
    {
      "type": "cloudformation",
      "filename": "cloudformation-template.yaml",
      "s3Key": "proyecto-123/cloudformation-template.yaml",
      "downloadUrl": "https://presigned-url...",
      "size": 2048
    }
  ],
  "totalDocuments": 5,
  "generationTime": "45.2s"
}
```

**Ejemplo con curl**:
```bash
curl -X POST https://tu-api-gateway-url.amazonaws.com/prod/generate-documents \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": "proyecto-123",
    "documentTypes": ["cloudformation", "costs", "guide"]
  }'
```

---

### 4. Listar Proyectos

Obtiene la lista de todos los proyectos del usuario.

```http
GET /projects
```

**Query Parameters (opcionales)**:
- `limit` (number): Número máximo de proyectos (default: 50, max: 100)
- `offset` (number): Número de proyectos a saltar (default: 0)
- `sortBy` (string): Campo para ordenar ("created_at", "updated_at", "project_name")
- `sortOrder` (string): Orden ("asc", "desc", default: "desc")

**Respuesta Exitosa (200)**:
```json
{
  "projects": [
    {
      "projectId": "string",
      "projectName": "string",
      "createdAt": "2024-01-15T10:30:00Z",
      "updatedAt": "2024-01-15T11:45:00Z",
      "status": "completed",
      "documentsCount": 5,
      "lastConversation": "string",
      "services": ["guardduty", "cloudwatch", "sns"]
    }
  ],
  "total": 25,
  "limit": 50,
  "offset": 0,
  "hasMore": false
}
```

**Ejemplo con curl**:
```bash
curl -X GET "https://tu-api-gateway-url.amazonaws.com/prod/projects?limit=10&sortBy=updated_at"
```

---

### 5. Obtener Proyecto Específico

Obtiene los detalles de un proyecto específico.

```http
GET /projects/{projectId}
```

**Path Parameters**:
- `projectId` (string, requerido): ID del proyecto

**Respuesta Exitosa (200)**:
```json
{
  "projectId": "string",
  "projectName": "string",
  "createdAt": "2024-01-15T10:30:00Z",
  "updatedAt": "2024-01-15T11:45:00Z",
  "status": "completed",
  "analysis": "string",
  "services": ["guardduty", "cloudwatch", "sns"],
  "conversations": [
    {
      "conversationId": "string",
      "timestamp": "2024-01-15T10:30:00Z",
      "messages": [
        {
          "role": "user",
          "content": "string",
          "timestamp": "2024-01-15T10:30:00Z"
        }
      ]
    }
  ],
  "documents": [
    {
      "type": "cloudformation",
      "filename": "cloudformation-template.yaml",
      "s3Key": "proyecto-123/cloudformation-template.yaml",
      "downloadUrl": "https://presigned-url...",
      "size": 2048,
      "createdAt": "2024-01-15T11:00:00Z"
    }
  ]
}
```

**Ejemplo con curl**:
```bash
curl -X GET https://tu-api-gateway-url.amazonaws.com/prod/projects/proyecto-123
```

---

### 6. Eliminar Proyecto

Elimina un proyecto y todos sus documentos asociados.

```http
DELETE /projects/{projectId}
```

**Path Parameters**:
- `projectId` (string, requerido): ID del proyecto

**Respuesta Exitosa (200)**:
```json
{
  "success": true,
  "message": "Proyecto eliminado exitosamente",
  "projectId": "string",
  "documentsDeleted": 5
}
```

**Ejemplo con curl**:
```bash
curl -X DELETE https://tu-api-gateway-url.amazonaws.com/prod/projects/proyecto-123
```

---

### 7. Descargar Documento

Obtiene una URL de descarga temporal para un documento específico.

```http
GET /projects/{projectId}/documents/{documentType}/download
```

**Path Parameters**:
- `projectId` (string, requerido): ID del proyecto
- `documentType` (string, requerido): Tipo de documento
  - Valores: `cloudformation`, `costs`, `guide`, `word`, `diagram`

**Query Parameters (opcionales)**:
- `expiresIn` (number): Tiempo de expiración en segundos (default: 3600, max: 86400)

**Respuesta Exitosa (200)**:
```json
{
  "downloadUrl": "https://presigned-url-to-s3-object...",
  "filename": "cloudformation-template.yaml",
  "size": 2048,
  "contentType": "application/x-yaml",
  "expiresAt": "2024-01-15T12:30:00Z"
}
```

**Ejemplo con curl**:
```bash
curl -X GET https://tu-api-gateway-url.amazonaws.com/prod/projects/proyecto-123/documents/cloudformation/download
```

---

### 8. Obtener Métricas

Obtiene métricas de uso del sistema.

```http
GET /metrics
```

**Query Parameters (opcionales)**:
- `period` (string): Período de tiempo ("1h", "24h", "7d", "30d", default: "24h")
- `metric` (string): Métrica específica ("requests", "projects", "documents", "errors")

**Respuesta Exitosa (200)**:
```json
{
  "period": "24h",
  "metrics": {
    "totalRequests": 1250,
    "totalProjects": 45,
    "totalDocuments": 180,
    "errorRate": 0.02,
    "averageResponseTime": 2.5,
    "topServices": [
      {"service": "guardduty", "count": 15},
      {"service": "lambda", "count": 12},
      {"service": "apigateway", "count": 8}
    ]
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Ejemplo con curl**:
```bash
curl -X GET "https://tu-api-gateway-url.amazonaws.com/prod/metrics?period=7d"
```

---

## 🔧 Códigos de Estado HTTP

### Códigos de Éxito
- `200 OK`: Solicitud exitosa
- `201 Created`: Recurso creado exitosamente
- `204 No Content`: Solicitud exitosa sin contenido de respuesta

### Códigos de Error del Cliente
- `400 Bad Request`: Solicitud malformada o parámetros inválidos
- `401 Unauthorized`: Autenticación requerida
- `403 Forbidden`: Acceso denegado
- `404 Not Found`: Recurso no encontrado
- `409 Conflict`: Conflicto con el estado actual del recurso
- `422 Unprocessable Entity`: Entidad no procesable
- `429 Too Many Requests`: Límite de rate limiting excedido

### Códigos de Error del Servidor
- `500 Internal Server Error`: Error interno del servidor
- `502 Bad Gateway`: Error de gateway
- `503 Service Unavailable`: Servicio no disponible
- `504 Gateway Timeout`: Timeout de gateway

## 🚨 Manejo de Errores

Todos los errores siguen el siguiente formato:

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": "string (opcional)",
    "timestamp": "2024-01-15T10:30:00Z",
    "requestId": "string"
  }
}
```

### Códigos de Error Comunes

#### `INVALID_REQUEST`
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "El campo 'messages' es requerido",
    "details": "El array de mensajes no puede estar vacío",
    "timestamp": "2024-01-15T10:30:00Z",
    "requestId": "req-123456"
  }
}
```

#### `PROJECT_NOT_FOUND`
```json
{
  "error": {
    "code": "PROJECT_NOT_FOUND",
    "message": "Proyecto no encontrado",
    "details": "No existe un proyecto con ID 'proyecto-123'",
    "timestamp": "2024-01-15T10:30:00Z",
    "requestId": "req-123456"
  }
}
```

#### `BEDROCK_ERROR`
```json
{
  "error": {
    "code": "BEDROCK_ERROR",
    "message": "Error al procesar con Bedrock",
    "details": "El modelo especificado no está disponible",
    "timestamp": "2024-01-15T10:30:00Z",
    "requestId": "req-123456"
  }
}
```

#### `RATE_LIMIT_EXCEEDED`
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Límite de solicitudes excedido",
    "details": "Máximo 1000 requests por minuto. Intenta de nuevo en 60 segundos",
    "timestamp": "2024-01-15T10:30:00Z",
    "requestId": "req-123456"
  }
}
```

## 📝 Modelos de Bedrock Soportados

### Modelos Disponibles
- `anthropic.claude-3-haiku-20240307-v1:0` (Recomendado para uso general)
- `anthropic.claude-3-sonnet-20240229-v1:0` (Mayor capacidad, más lento)
- `anthropic.claude-3-opus-20240229-v1:0` (Máxima capacidad, más costoso)

### Límites por Modelo
| Modelo | Tokens Máximos | Costo Aproximado |
|--------|----------------|------------------|
| Claude 3 Haiku | 200,000 | $0.25/1M tokens |
| Claude 3 Sonnet | 200,000 | $3.00/1M tokens |
| Claude 3 Opus | 200,000 | $15.00/1M tokens |

## 🔒 Consideraciones de Seguridad

### Rate Limiting
- **Límite global**: 1000 requests/minuto por IP
- **Límite por endpoint**: Varía según el endpoint
- **Headers de respuesta**:
  ```http
  X-RateLimit-Limit: 1000
  X-RateLimit-Remaining: 999
  X-RateLimit-Reset: 1642248000
  ```

### Validación de Entrada
- Todos los inputs son validados y sanitizados
- Límite de tamaño de payload: 1MB
- Timeout de request: 30 segundos

### URLs de Descarga
- URLs presignadas con expiración automática
- Máximo 24 horas de validez
- Acceso de solo lectura

## 📊 Ejemplos de Uso Completos

### Ejemplo 1: Crear Proyecto Completo
```bash
#!/bin/bash

API_BASE="https://tu-api-gateway-url.amazonaws.com/prod"

# 1. Iniciar conversación
RESPONSE=$(curl -s -X POST "$API_BASE/arquitecto" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Necesito una arquitectura para monitoreo de seguridad con GuardDuty y CloudWatch"
      }
    ],
    "modelId": "anthropic.claude-3-haiku-20240307-v1:0"
  }')

PROJECT_ID=$(echo $RESPONSE | jq -r '.projectId')
echo "Proyecto creado: $PROJECT_ID"

# 2. Generar documentos
curl -s -X POST "$API_BASE/generate-documents" \
  -H "Content-Type: application/json" \
  -d "{
    \"projectId\": \"$PROJECT_ID\",
    \"documentTypes\": [\"cloudformation\", \"costs\", \"guide\", \"word\", \"diagram\"]
  }" | jq .

# 3. Obtener detalles del proyecto
curl -s -X GET "$API_BASE/projects/$PROJECT_ID" | jq .

echo "Proyecto completo creado y documentado!"
```

### Ejemplo 2: Monitoreo de Métricas
```bash
#!/bin/bash

API_BASE="https://tu-api-gateway-url.amazonaws.com/prod"

# Obtener métricas de diferentes períodos
echo "=== Métricas de las últimas 24 horas ==="
curl -s -X GET "$API_BASE/metrics?period=24h" | jq '.metrics'

echo "=== Métricas de la última semana ==="
curl -s -X GET "$API_BASE/metrics?period=7d" | jq '.metrics'

echo "=== Solo errores ==="
curl -s -X GET "$API_BASE/metrics?period=24h&metric=errors" | jq '.metrics'
```

### Ejemplo 3: Gestión de Proyectos
```bash
#!/bin/bash

API_BASE="https://tu-api-gateway-url.amazonaws.com/prod"

# Listar todos los proyectos
echo "=== Todos los Proyectos ==="
curl -s -X GET "$API_BASE/projects" | jq '.projects[] | {projectId, projectName, status, documentsCount}'

# Obtener proyectos recientes
echo "=== Proyectos Recientes ==="
curl -s -X GET "$API_BASE/projects?limit=5&sortBy=updated_at&sortOrder=desc" | jq '.projects[] | {projectName, updatedAt}'

# Descargar documento específico
PROJECT_ID="proyecto-123"
echo "=== Descargando CloudFormation ==="
DOWNLOAD_URL=$(curl -s -X GET "$API_BASE/projects/$PROJECT_ID/documents/cloudformation/download" | jq -r '.downloadUrl')
curl -s "$DOWNLOAD_URL" -o "cloudformation-$PROJECT_ID.yaml"
echo "Descargado: cloudformation-$PROJECT_ID.yaml"
```

## 🧪 Testing de la API

### Colección de Postman
```json
{
  "info": {
    "name": "AWS Propuestas v3 API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "baseUrl",
      "value": "https://tu-api-gateway-url.amazonaws.com/prod"
    }
  ],
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{baseUrl}}/health",
          "host": ["{{baseUrl}}"],
          "path": ["health"]
        }
      }
    },
    {
      "name": "Chat Arquitecto",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"messages\": [\n    {\n      \"role\": \"user\",\n      \"content\": \"Necesito una arquitectura para GuardDuty\"\n    }\n  ],\n  \"modelId\": \"anthropic.claude-3-haiku-20240307-v1:0\"\n}"
        },
        "url": {
          "raw": "{{baseUrl}}/arquitecto",
          "host": ["{{baseUrl}}"],
          "path": ["arquitecto"]
        }
      }
    }
  ]
}
```

### Tests Automatizados con Jest
```javascript
// api.test.js
const axios = require('axios');

const API_BASE = process.env.API_BASE_URL || 'https://tu-api-gateway-url.amazonaws.com/prod';

describe('AWS Propuestas v3 API', () => {
  test('Health check should return healthy status', async () => {
    const response = await axios.get(`${API_BASE}/health`);
    expect(response.status).toBe(200);
    expect(response.data.status).toBe('healthy');
  });

  test('Arquitecto endpoint should process messages', async () => {
    const payload = {
      messages: [
        {
          role: 'user',
          content: 'Necesito una arquitectura para GuardDuty'
        }
      ],
      modelId: 'anthropic.claude-3-haiku-20240307-v1:0'
    };

    const response = await axios.post(`${API_BASE}/arquitecto`, payload);
    expect(response.status).toBe(200);
    expect(response.data).toHaveProperty('response');
    expect(response.data).toHaveProperty('projectId');
  });

  test('Projects endpoint should return list', async () => {
    const response = await axios.get(`${API_BASE}/projects`);
    expect(response.status).toBe(200);
    expect(response.data).toHaveProperty('projects');
    expect(Array.isArray(response.data.projects)).toBe(true);
  });
});
```

---

Esta documentación cubre todos los aspectos principales de la API. Para más detalles específicos o casos de uso avanzados, consulta el código fuente o contacta al equipo de desarrollo. 🚀
