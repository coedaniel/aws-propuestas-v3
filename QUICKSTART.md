# 🚀 Guía de Inicio Rápido - AWS Propuestas v3

Esta guía te ayudará a tener **AWS Propuestas v3** funcionando en menos de 10 minutos.

## ⚡ Inicio Rápido (3 pasos)

### 1️⃣ **Configuración Inicial**
```bash
# Clonar y configurar
git clone https://github.com/coedaniel/aws-propuestas-v3.git
cd aws-propuestas-v3
npm install

# Configurar variables de entorno
cp .env.local.example .env.local
```

### 2️⃣ **Configurar AWS**
```bash
# Configurar credenciales AWS (si no lo has hecho)
aws configure

# Verificar acceso a Bedrock
aws bedrock list-foundation-models --region us-east-1
```

### 3️⃣ **Ejecutar**
```bash
# Iniciar en modo desarrollo
npm run dev

# Abrir http://localhost:3000
```

## 🎯 Primeros Pasos

### Chat Libre
1. Ve a **Chat Libre** desde la página principal
2. Selecciona un modelo IA (Nova Pro recomendado)
3. Haz una pregunta: *"¿Cómo diseñar una arquitectura serverless?"*
4. ¡Disfruta de las respuestas expertas!

### Modo Arquitecto
1. Ve a **Arquitecto AWS** desde la página principal
2. Inicia un nuevo proyecto
3. Responde las preguntas guiadas
4. Recibe documentos profesionales automáticamente

## 🔧 Configuración Avanzada

### Variables de Entorno Importantes
```bash
# .env.local
NEXT_PUBLIC_REGION=us-east-1
NEXT_PUBLIC_ENVIRONMENT=dev
NEXT_PUBLIC_API_URL=http://localhost:3000
```

### Modelos Bedrock Requeridos
Asegúrate de tener acceso a estos modelos en tu cuenta AWS:
- `amazon.nova-pro-v1:0`
- `anthropic.claude-3-haiku-20240307-v1:0`
- `anthropic.claude-3-sonnet-20240229-v1:0`

## 🚀 Despliegue Rápido

### Opción 1: AWS Amplify (Recomendado)
1. Conecta tu repositorio GitHub a AWS Amplify
2. Amplify detectará automáticamente la configuración
3. Configura las variables de entorno en Amplify Console
4. ¡Deploy automático!

### Opción 2: Scripts Automatizados
```bash
# Deploy completo
./scripts/deploy.sh

# Solo frontend
./scripts/deploy-frontend.sh

# Solo backend
./scripts/deploy-backend.sh
```

## 🆘 Solución de Problemas Comunes

### Error: "Access denied to Bedrock"
```bash
# Verificar permisos
aws sts get-caller-identity
aws bedrock list-foundation-models --region us-east-1

# Solicitar acceso a modelos si es necesario
# Ir a AWS Console > Bedrock > Model access
```

### Error: "Module not found"
```bash
# Limpiar e instalar dependencias
rm -rf node_modules package-lock.json
npm install
```

### Error: "API endpoint not found"
```bash
# Verificar que el servidor esté corriendo
npm run dev

# Verificar variables de entorno
cat .env.local
```

## 📚 Recursos Adicionales

- **Documentación completa**: Ver `README.md`
- **Arquitectura**: Ver `docs/ARCHITECTURE.md`
- **APIs**: Ver `docs/API.md`
- **Despliegue**: Ver `docs/DEPLOYMENT.md`

## 🎉 ¡Listo!

Tu sistema está funcionando. Ahora puedes:

✅ Chatear con IA sobre AWS  
✅ Generar propuestas profesionales  
✅ Descargar documentos automáticos  
✅ Gestionar proyectos desde el dashboard  

**¿Necesitas ayuda?** Abre un issue en GitHub o consulta la documentación completa.

---

**¡Disfruta creando propuestas AWS profesionales con IA! 🚀**
