# Guía de Contribución - AWS Propuestas v3

¡Gracias por tu interés en contribuir al proyecto AWS Propuestas v3! Esta guía te ayudará a entender cómo puedes participar en el desarrollo y mejora del sistema.

## 📋 Tabla de Contenidos

- [Código de Conducta](#código-de-conducta)
- [Cómo Contribuir](#cómo-contribuir)
- [Configuración del Entorno de Desarrollo](#configuración-del-entorno-de-desarrollo)
- [Proceso de Desarrollo](#proceso-de-desarrollo)
- [Estándares de Código](#estándares-de-código)
- [Testing](#testing)
- [Documentación](#documentación)
- [Proceso de Review](#proceso-de-review)

## 🤝 Código de Conducta

Este proyecto adhiere a un código de conducta profesional. Al participar, te comprometes a mantener un ambiente respetuoso y colaborativo.

### Comportamientos Esperados
- Usar lenguaje inclusivo y respetuoso
- Ser receptivo a críticas constructivas
- Enfocarse en lo que es mejor para la comunidad
- Mostrar empatía hacia otros miembros

### Comportamientos Inaceptables
- Uso de lenguaje o imágenes sexualizadas
- Comentarios despectivos o ataques personales
- Acoso público o privado
- Publicar información privada de otros sin permiso

## 🚀 Cómo Contribuir

### Tipos de Contribuciones Bienvenidas

#### 🐛 Reportar Bugs
- Usa la plantilla de issue para bugs
- Incluye pasos para reproducir el problema
- Proporciona logs y capturas de pantalla
- Especifica el entorno donde ocurre

#### 💡 Sugerir Mejoras
- Usa la plantilla de issue para features
- Describe claramente el problema que resuelve
- Explica por qué sería útil para otros usuarios
- Considera alternativas que hayas evaluado

#### 📝 Mejorar Documentación
- Corregir errores tipográficos
- Clarificar instrucciones confusas
- Agregar ejemplos útiles
- Traducir contenido

#### 🔧 Contribuir Código
- Corregir bugs reportados
- Implementar nuevas características
- Mejorar rendimiento
- Refactorizar código existente

### Proceso para Contribuir

1. **Fork el repositorio**
2. **Crear una rama para tu feature/fix**
3. **Hacer tus cambios**
4. **Escribir/actualizar tests**
5. **Actualizar documentación**
6. **Crear Pull Request**

## 🛠️ Configuración del Entorno de Desarrollo

### Prerrequisitos
```bash
# Node.js 18+
node --version  # v18.0.0+

# Python 3.9+
python3 --version  # Python 3.9.0+

# AWS CLI
aws --version  # aws-cli/2.0.0+

# SAM CLI
sam --version  # SAM CLI, version 1.0.0+

# Git
git --version  # git version 2.0.0+
```

### Configuración Inicial
```bash
# 1. Fork y clonar el repositorio
git clone https://github.com/tu-usuario/aws-propuestas-v3.git
cd aws-propuestas-v3

# 2. Configurar remotes
git remote add upstream https://github.com/coedaniel/aws-propuestas-v3.git

# 3. Instalar dependencias del frontend
npm install

# 4. Configurar variables de entorno
cp .env.local.example .env.local
# Editar .env.local con tus configuraciones

# 5. Configurar AWS CLI
aws configure
```

### Configuración de AWS para Desarrollo
```bash
# Crear perfil de desarrollo
aws configure --profile aws-propuestas-dev

# Configurar variables de entorno
export AWS_PROFILE=aws-propuestas-dev
export AWS_REGION=us-east-1
```

### Configuración de Base de Datos Local (Opcional)
```bash
# Instalar DynamoDB Local
npm install -g dynamodb-local

# Ejecutar DynamoDB Local
dynamodb-local --port 8000 --inMemory

# Crear tablas locales
aws dynamodb create-table \
  --table-name aws-propuestas-v3-projects-dev \
  --attribute-definitions AttributeName=projectId,AttributeType=S \
  --key-schema AttributeName=projectId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --endpoint-url http://localhost:8000
```

## 🔄 Proceso de Desarrollo

### Workflow de Git

#### 1. Crear Nueva Rama
```bash
# Actualizar main
git checkout main
git pull upstream main

# Crear rama para feature/fix
git checkout -b feature/nueva-funcionalidad
# o
git checkout -b fix/corregir-bug
# o
git checkout -b docs/actualizar-readme
```

#### 2. Hacer Cambios
```bash
# Hacer tus cambios
# Commitear frecuentemente con mensajes descriptivos
git add .
git commit -m "feat: agregar detección de servicios de ML"

# Mantener rama actualizada
git fetch upstream
git rebase upstream/main
```

#### 3. Testing Local
```bash
# Frontend
npm run test
npm run lint
npm run build

# Backend
cd backend
python -m pytest tests/
sam build
sam local start-api
```

#### 4. Push y Pull Request
```bash
# Push a tu fork
git push origin feature/nueva-funcionalidad

# Crear Pull Request en GitHub
# Usar la plantilla de PR
```

### Convenciones de Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Formato
<tipo>[scope opcional]: <descripción>

# Ejemplos
feat: agregar soporte para Amazon Comprehend
fix: corregir detección de servicios de API Gateway
docs: actualizar guía de instalación
style: formatear código según estándares
refactor: reorganizar funciones de generación de documentos
test: agregar tests para dynamic_generator
chore: actualizar dependencias
```

#### Tipos de Commit
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Cambios de formato (no afectan funcionalidad)
- `refactor`: Refactoring de código
- `test`: Agregar o modificar tests
- `chore`: Tareas de mantenimiento

## 📏 Estándares de Código

### Python (Backend)

#### Estilo de Código
```python
# Usar Black para formateo
black backend/

# Usar isort para imports
isort backend/

# Usar flake8 para linting
flake8 backend/
```

#### Configuración en pyproject.toml
```toml
[tool.black]
line-length = 88
target-version = ['py39']

[tool.isort]
profile = "black"
line_length = 88

[tool.flake8]
max-line-length = 88
extend-ignore = E203, W503
```

#### Ejemplo de Función Bien Documentada
```python
def extract_services_from_analysis(analysis: str) -> List[str]:
    """
    Extrae servicios AWS mencionados en el análisis de conversación.
    
    Args:
        analysis (str): Texto de análisis de la conversación
        
    Returns:
        List[str]: Lista de servicios AWS detectados
        
    Raises:
        ValueError: Si el análisis está vacío o es None
        
    Example:
        >>> extract_services_from_analysis("Necesito GuardDuty y CloudWatch")
        ['guardduty', 'cloudwatch']
    """
    if not analysis:
        raise ValueError("El análisis no puede estar vacío")
    
    # Implementación...
    return detected_services
```

### JavaScript/TypeScript (Frontend)

#### Estilo de Código
```bash
# Usar Prettier para formateo
npm run format

# Usar ESLint para linting
npm run lint

# Usar TypeScript para type checking
npm run type-check
```

#### Configuración en .eslintrc.js
```javascript
module.exports = {
  extends: [
    'next/core-web-vitals',
    '@typescript-eslint/recommended',
    'prettier'
  ],
  rules: {
    '@typescript-eslint/no-unused-vars': 'error',
    '@typescript-eslint/explicit-function-return-type': 'warn',
    'prefer-const': 'error'
  }
};
```

#### Ejemplo de Componente React
```typescript
interface ProjectCardProps {
  project: Project;
  onSelect: (projectId: string) => void;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({ 
  project, 
  onSelect 
}) => {
  const handleClick = useCallback(() => {
    onSelect(project.projectId);
  }, [project.projectId, onSelect]);

  return (
    <div 
      className="project-card"
      onClick={handleClick}
      role="button"
      tabIndex={0}
    >
      <h3>{project.projectName}</h3>
      <p>{project.status}</p>
    </div>
  );
};
```

### CloudFormation/SAM

#### Estructura de Template
```yaml
# Usar comentarios descriptivos
# Organizar recursos por categoría
# Usar parámetros para valores configurables

AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: 'AWS Propuestas v3 - Infraestructura principal'

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues: [dev, staging, prod]
    Description: Entorno de despliegue

Globals:
  Function:
    Runtime: python3.9
    Timeout: 30
    Environment:
      Variables:
        ENVIRONMENT: !Ref Environment

Resources:
  # Lambda Functions
  ArquitectoFunction:
    Type: AWS::Serverless::Function
    Properties:
      # Configuración...
```

## 🧪 Testing

### Estructura de Tests
```
tests/
├── unit/                 # Tests unitarios
│   ├── backend/
│   │   ├── test_dynamic_generator.py
│   │   └── test_helpers.py
│   └── frontend/
│       ├── components/
│       └── utils/
├── integration/          # Tests de integración
│   ├── test_api_endpoints.py
│   └── test_document_generation.py
└── e2e/                 # Tests end-to-end
    ├── test_user_flows.py
    └── test_complete_workflow.py
```

### Tests de Backend (Python)

#### Configuración pytest
```python
# conftest.py
import pytest
import boto3
from moto import mock_dynamodb, mock_s3

@pytest.fixture
def mock_aws():
    with mock_dynamodb(), mock_s3():
        yield

@pytest.fixture
def sample_project():
    return {
        'projectId': 'test-project-123',
        'projectName': 'Test Project',
        'analysis': 'Test analysis with GuardDuty'
    }
```

#### Ejemplo de Test Unitario
```python
# test_dynamic_generator.py
import pytest
from backend.dynamic_generator import extract_services_from_analysis

class TestServiceExtraction:
    def test_extract_guardduty_service(self):
        analysis = "Necesito implementar GuardDuty para detección de amenazas"
        services = extract_services_from_analysis(analysis)
        assert 'guardduty' in services

    def test_extract_multiple_services(self):
        analysis = "Usar API Gateway con Lambda y DynamoDB"
        services = extract_services_from_analysis(analysis)
        expected = ['apigateway', 'lambda', 'dynamodb']
        assert all(service in services for service in expected)

    def test_empty_analysis_raises_error(self):
        with pytest.raises(ValueError):
            extract_services_from_analysis("")
```

#### Ejemplo de Test de Integración
```python
# test_api_endpoints.py
import json
import pytest
from backend.lambda_function import lambda_handler

class TestAPIEndpoints:
    def test_health_endpoint(self, mock_aws):
        event = {
            'httpMethod': 'GET',
            'path': '/health'
        }
        
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['status'] == 'healthy'

    def test_arquitecto_endpoint_with_valid_input(self, mock_aws):
        event = {
            'httpMethod': 'POST',
            'path': '/arquitecto',
            'body': json.dumps({
                'messages': [{'role': 'user', 'content': 'Hola'}],
                'modelId': 'anthropic.claude-3-haiku-20240307-v1:0'
            })
        }
        
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'response' in body
        assert 'projectId' in body
```

### Tests de Frontend (Jest + React Testing Library)

#### Configuración Jest
```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1'
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts'
  ]
};
```

#### Ejemplo de Test de Componente
```typescript
// __tests__/components/ProjectCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ProjectCard } from '@/components/ProjectCard';

const mockProject = {
  projectId: 'test-123',
  projectName: 'Test Project',
  status: 'completed',
  documentsCount: 5
};

describe('ProjectCard', () => {
  it('renders project information correctly', () => {
    const onSelect = jest.fn();
    
    render(<ProjectCard project={mockProject} onSelect={onSelect} />);
    
    expect(screen.getByText('Test Project')).toBeInTheDocument();
    expect(screen.getByText('completed')).toBeInTheDocument();
  });

  it('calls onSelect when clicked', () => {
    const onSelect = jest.fn();
    
    render(<ProjectCard project={mockProject} onSelect={onSelect} />);
    
    fireEvent.click(screen.getByRole('button'));
    
    expect(onSelect).toHaveBeenCalledWith('test-123');
  });
});
```

### Ejecutar Tests

```bash
# Backend
cd backend
python -m pytest tests/ -v --cov=.

# Frontend
npm test
npm run test:coverage

# E2E (con Playwright)
npm run test:e2e
```

## 📚 Documentación

### Actualizar Documentación

#### Cuando Agregar/Actualizar Docs
- Nuevas funcionalidades
- Cambios en API
- Nuevos endpoints
- Cambios en configuración
- Corrección de errores en docs existentes

#### Tipos de Documentación
1. **README.md**: Información general del proyecto
2. **API.md**: Documentación de endpoints
3. **DEPLOYMENT.md**: Guía de despliegue
4. **TROUBLESHOOTING.md**: Solución de problemas
5. **ARCHITECTURE.md**: Arquitectura del sistema
6. **CONTRIBUTING.md**: Esta guía

#### Estilo de Documentación
- Usar Markdown estándar
- Incluir ejemplos de código
- Agregar capturas de pantalla cuando sea útil
- Mantener tabla de contenidos actualizada
- Usar emojis para mejorar legibilidad

### Documentación de Código

#### Python
```python
def generate_cloudformation_template(services: List[str], project_name: str) -> str:
    """
    Genera template de CloudFormation basado en servicios detectados.
    
    Esta función crea un template de CloudFormation dinámico que incluye
    recursos específicos para los servicios AWS detectados en el análisis
    de la conversación.
    
    Args:
        services (List[str]): Lista de servicios AWS a incluir
        project_name (str): Nombre del proyecto para naming de recursos
        
    Returns:
        str: Template de CloudFormation en formato YAML
        
    Raises:
        ValueError: Si la lista de servicios está vacía
        TemplateGenerationError: Si hay error generando el template
        
    Example:
        >>> services = ['guardduty', 'cloudwatch']
        >>> template = generate_cloudformation_template(services, 'mi-proyecto')
        >>> 'AWS::GuardDuty::Detector' in template
        True
        
    Note:
        El template generado incluye configuraciones básicas de seguridad
        y mejores prácticas para cada servicio.
    """
```

#### TypeScript
```typescript
/**
 * Hook personalizado para manejar el estado de proyectos
 * 
 * @param initialProjects - Lista inicial de proyectos
 * @returns Objeto con proyectos, funciones de manejo y estado de carga
 * 
 * @example
 * ```tsx
 * const { projects, loading, addProject, deleteProject } = useProjects([]);
 * ```
 */
export const useProjects = (initialProjects: Project[] = []) => {
  // Implementación...
};
```

## 🔍 Proceso de Review

### Checklist para Pull Requests

#### Antes de Crear PR
- [ ] Código sigue estándares establecidos
- [ ] Tests pasan localmente
- [ ] Documentación actualizada
- [ ] Commits siguen convención
- [ ] Rama actualizada con main

#### Plantilla de Pull Request
```markdown
## Descripción
Breve descripción de los cambios realizados.

## Tipo de Cambio
- [ ] Bug fix (cambio que corrige un issue)
- [ ] Nueva funcionalidad (cambio que agrega funcionalidad)
- [ ] Breaking change (cambio que rompe funcionalidad existente)
- [ ] Documentación (cambios solo en documentación)

## ¿Cómo se ha probado?
Describe las pruebas realizadas para verificar los cambios.

## Checklist
- [ ] Mi código sigue las guías de estilo del proyecto
- [ ] He realizado una auto-revisión de mi código
- [ ] He comentado mi código, especialmente en áreas difíciles de entender
- [ ] He realizado cambios correspondientes en la documentación
- [ ] Mis cambios no generan nuevas advertencias
- [ ] He agregado tests que prueban que mi fix es efectivo o que mi funcionalidad funciona
- [ ] Tests unitarios nuevos y existentes pasan localmente con mis cambios

## Capturas de Pantalla (si aplica)
Agregar capturas de pantalla para mostrar cambios visuales.
```

### Proceso de Review

#### Para Reviewers
1. **Verificar funcionalidad**: ¿Los cambios hacen lo que dicen hacer?
2. **Revisar código**: ¿El código es limpio y mantenible?
3. **Verificar tests**: ¿Los tests cubren los casos importantes?
4. **Revisar documentación**: ¿La documentación está actualizada?
5. **Probar localmente**: ¿Los cambios funcionan en tu entorno?

#### Comentarios de Review
```markdown
# Comentario constructivo
Considera usar `const` en lugar de `let` aquí ya que la variable no se reasigna.

# Sugerencia de mejora
¿Qué te parece extraer esta lógica a una función separada para mejorar la legibilidad?

# Pregunta para clarificación
¿Podrías explicar por qué elegiste este enfoque en lugar de usar el patrón existente?

# Aprobación
¡Excelente trabajo! El código está limpio y bien documentado. LGTM! 🚀
```

## 🏷️ Versionado y Releases

### Semantic Versioning
Seguimos [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Cambios incompatibles con versiones anteriores
- **MINOR** (0.X.0): Nueva funcionalidad compatible con versiones anteriores
- **PATCH** (0.0.X): Correcciones de bugs compatibles

### Proceso de Release

#### 1. Preparar Release
```bash
# Crear rama de release
git checkout -b release/v3.1.0

# Actualizar versión en package.json
npm version minor

# Actualizar CHANGELOG.md
# Hacer commit de cambios de versión
git commit -m "chore: bump version to 3.1.0"
```

#### 2. Testing de Release
```bash
# Tests completos
npm run test:all
npm run build
sam build
sam deploy --stack-name aws-propuestas-v3-staging
```

#### 3. Crear Release
```bash
# Merge a main
git checkout main
git merge release/v3.1.0

# Crear tag
git tag -a v3.1.0 -m "Release version 3.1.0"

# Push cambios y tags
git push origin main
git push origin v3.1.0
```

#### 4. Deploy a Producción
```bash
# Deploy automático via GitHub Actions
# O deploy manual
sam deploy --stack-name aws-propuestas-v3-prod
```

## 🎯 Roadmap y Prioridades

### Áreas de Contribución Prioritarias

#### 🔥 Alta Prioridad
1. **Detección de Servicios**: Mejorar algoritmos de detección
2. **Generación de Documentos**: Agregar más tipos de documentos
3. **Testing**: Aumentar cobertura de tests
4. **Performance**: Optimizar tiempos de respuesta

#### 🚀 Media Prioridad
1. **UI/UX**: Mejorar interfaz de usuario
2. **Monitoreo**: Agregar más métricas y alertas
3. **Documentación**: Expandir guías y ejemplos
4. **Internacionalización**: Soporte para múltiples idiomas

#### 💡 Baja Prioridad
1. **Integraciones**: Conectar con otras herramientas AWS
2. **Mobile**: Versión móvil de la aplicación
3. **Plugins**: Sistema de plugins para extensibilidad
4. **Analytics**: Dashboard de analytics avanzado

### Ideas para Nuevos Contribuidores

#### 🌱 Good First Issues
- Corregir errores tipográficos en documentación
- Agregar tests unitarios para funciones existentes
- Mejorar mensajes de error
- Agregar validaciones de entrada

#### 🔧 Intermediate Issues
- Implementar nuevos generadores de documentos
- Agregar soporte para nuevos servicios AWS
- Mejorar algoritmos de detección de servicios
- Optimizar consultas a base de datos

#### 🚀 Advanced Issues
- Implementar sistema de cache distribuido
- Agregar soporte para multi-región
- Implementar sistema de plugins
- Crear herramientas de migración

## 📞 Contacto y Soporte

### Canales de Comunicación
- **GitHub Issues**: Para bugs y feature requests
- **GitHub Discussions**: Para preguntas y discusiones generales
- **Email**: [tu-email@ejemplo.com] para temas sensibles

### Obtener Ayuda
1. **Revisa la documentación**: README, API docs, troubleshooting
2. **Busca en issues existentes**: Puede que tu problema ya esté reportado
3. **Crea un nuevo issue**: Usa las plantillas apropiadas
4. **Únete a las discusiones**: Comparte ideas y obtén feedback

---

¡Gracias por contribuir a AWS Propuestas v3! Tu participación hace que este proyecto sea mejor para toda la comunidad. 🙌

## 📝 Plantillas de Issues

### Bug Report
```markdown
**Describe el bug**
Una descripción clara y concisa del bug.

**Para Reproducir**
Pasos para reproducir el comportamiento:
1. Ve a '...'
2. Haz clic en '....'
3. Desplázate hacia abajo hasta '....'
4. Ve el error

**Comportamiento Esperado**
Una descripción clara y concisa de lo que esperabas que pasara.

**Capturas de Pantalla**
Si aplica, agrega capturas de pantalla para ayudar a explicar tu problema.

**Entorno (completa la siguiente información):**
 - OS: [e.g. macOS, Windows, Linux]
 - Browser [e.g. chrome, safari]
 - Version [e.g. 22]

**Información Adicional**
Agrega cualquier otro contexto sobre el problema aquí.
```

### Feature Request
```markdown
**¿Tu feature request está relacionado con un problema? Describe.**
Una descripción clara y concisa del problema. Ej. Siempre me frustra cuando [...]

**Describe la solución que te gustaría**
Una descripción clara y concisa de lo que quieres que pase.

**Describe alternativas que has considerado**
Una descripción clara y concisa de cualquier solución o funcionalidad alternativa que hayas considerado.

**Contexto adicional**
Agrega cualquier otro contexto o capturas de pantalla sobre el feature request aquí.
```
