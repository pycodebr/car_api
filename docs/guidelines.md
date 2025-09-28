# Guidelines e Padrões

## 🎯 Padrões de Código

### Estilo de Código

O projeto segue padrões rigorosos de qualidade de código utilizando **Ruff** como linter e formatador principal.

#### Configuração do Ruff

```toml
[tool.ruff]
line-length = 79
exclude = [
    ".git", ".tox", ".venv", "__pycache__",
    "migrations", "alembic"
]

[tool.ruff.lint]
preview = true
select = ['I', 'F', 'E', 'W', 'PL', 'PT']
ignore = ['PLR2004', 'PLR0917', 'PLR0913', 'PT022']

[tool.ruff.format]
preview = true
quote-style = 'single'
```

#### Regras de Formatação
- **Linha máxima**: 79 caracteres
- **Aspas**: Simples (`'`) para strings
- **Imports**: Organizados automaticamente
- **Trailing commas**: Obrigatórias em listas multi-linha

### Type Hints

**Obrigatório em todo o código:**

```python
# ✅ Correto
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

async def get_user(
    user_id: int,
    db: AsyncSession
) -> Optional[User]:
    return await db.get(User, user_id)

# ❌ Incorreto
async def get_user(user_id, db):
    return await db.get(User, user_id)
```

### Nomenclatura

#### Variáveis e Funções
```python
# ✅ Snake case
user_name = "João"
car_model = "Civic"

async def create_new_user():
    pass

async def get_car_by_id():
    pass
```

#### Classes
```python
# ✅ Pascal case
class UserSchema:
    pass

class CarPublicSchema:
    pass

class AuthenticationError:
    pass
```

#### Constantes
```python
# ✅ UPPER_SNAKE_CASE
JWT_ALGORITHM = 'HS256'
DEFAULT_PAGE_SIZE = 100
MAX_CARS_PER_USER = 50
```

#### Arquivos e Módulos
```python
# ✅ Snake case
car_schemas.py
user_models.py
auth_middleware.py
```

## 🏗️ Arquitetura e Estrutura

### Padrão de Arquitetura

O projeto segue o padrão **Repository/Service Layer** adaptado para FastAPI:

```
┌─────────────────┐
│   Controllers   │  ← FastAPI Routers
│   (Routers)     │
├─────────────────┤
│   Schemas       │  ← Pydantic Models (Validation)
│   (DTOs)        │
├─────────────────┤
│   Models        │  ← SQLAlchemy Models (Database)
│   (Entities)    │
├─────────────────┤
│   Core          │  ← Database, Security, Settings
│   (Infrastructure) │
└─────────────────┘
```

### Separação de Responsabilidades

#### 1. Routers (Controladores)
```python
# Responsabilidades:
# - Receber requisições HTTP
# - Validar parâmetros de entrada
# - Chamar lógica de negócio
# - Retornar respostas HTTP

@router.post('/', response_model=CarPublicSchema)
async def create_car(
    car: CarSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    # Validação de regras de negócio
    # Operações no banco
    # Retorno da resposta
```

#### 2. Schemas (DTOs)
```python
# Responsabilidades:
# - Validação de dados de entrada
# - Serialização de dados de saída
# - Documentação automática da API

class CarSchema(BaseModel):
    model: str = Field(..., min_length=1, max_length=100)
    factory_year: int = Field(..., ge=1900, le=2030)
    price: Decimal = Field(..., gt=0)
```

#### 3. Models (Entidades)
```python
# Responsabilidades:
# - Representar estrutura do banco
# - Definir relacionamentos
# - Validações de integridade

class Car(Base):
    __tablename__ = 'cars'

    id: Mapped[int] = mapped_column(primary_key=True)
    model: Mapped[str] = mapped_column(String(100))
    brand: Mapped['Brand'] = relationship('Brand')
```

#### 4. Core (Infraestrutura)
```python
# Responsabilidades:
# - Configurações globais
# - Conectividade com banco
# - Segurança e autenticação
# - Utilitários compartilhados
```

## 🔐 Padrões de Segurança

### Autenticação JWT

```python
# Sempre verificar autenticação em rotas protegidas
@router.get('/')
async def protected_endpoint(
    current_user: User = Depends(get_current_user)
):
    # Lógica do endpoint
```

### Validação de Propriedade

```python
# Verificar se o usuário é dono do recurso
def verify_car_ownership(current_user: User, car_owner_id: int):
    if current_user.id != car_owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Acesso negado'
        )
```

### Hash de Senhas

```python
# Sempre usar hash seguro para senhas
from pwdlib import PasswordHash

pwd_context = PasswordHash.recommended()

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

## 🗃️ Padrões de Banco de Dados

### Migrações

```python
# Sempre criar migrações para mudanças no schema
poetry run alembic revision --autogenerate -m "add new field to car model"
```

### Consultas

```python
# ✅ Usar async/await
async def get_cars(db: AsyncSession) -> list[Car]:
    result = await db.execute(select(Car))
    return result.scalars().all()

# ✅ Usar selectinload para relacionamentos
query = select(Car).options(
    selectinload(Car.brand),
    selectinload(Car.owner)
)
```

### Transações

```python
# ✅ Commit e rollback explícitos
try:
    db.add(new_car)
    await db.commit()
    await db.refresh(new_car)
except Exception:
    await db.rollback()
    raise
```

## 📊 Padrões de API

### Códigos de Status HTTP

```python
# ✅ Usar códigos apropriados
@router.post('/', status_code=status.HTTP_201_CREATED)  # Criação
@router.get('/', status_code=status.HTTP_200_OK)       # Sucesso
@router.put('/', status_code=status.HTTP_200_OK)       # Atualização
@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)  # Deleção

# ✅ Erros específicos
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Recurso não encontrado'
)
```

### Paginação

```python
# ✅ Padrão de paginação
@router.get('/')
async def list_items(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    # Implementação
    return {
        'items': items,
        'offset': offset,
        'limit': limit
    }
```

### Filtros e Busca

```python
# ✅ Parâmetros opcionais de filtro
@router.get('/')
async def list_cars(
    search: Optional[str] = Query(None),
    brand_id: Optional[int] = Query(None),
    fuel_type: Optional[FuelType] = Query(None),
):
    # Implementação
```

## 🧪 Padrões de Testes

### Estrutura de Testes

```python
# ✅ Usar pytest com fixtures
@pytest_asyncio.fixture
async def client(db_session):
    app.dependency_overrides[get_session] = lambda: db_session
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# ✅ Testar cenários positivos e negativos
async def test_create_car_success(client, sample_user):
    # Teste de sucesso

async def test_create_car_invalid_data(client):
    # Teste de erro
```

### Nomenclatura de Testes

```python
# ✅ Padrão: test_[action]_[scenario]_[expected_result]
def test_create_user_with_valid_data_returns_201():
    pass

def test_create_user_with_duplicate_email_returns_400():
    pass

def test_get_user_that_not_exists_returns_404():
    pass
```

### Cobertura de Testes

```bash
# Manter cobertura mínima de 90%
poetry run task test

# Verificar relatório HTML
open htmlcov/index.html
```

## 📝 Padrões de Documentação

### Docstrings

```python
# ✅ Usar docstrings em funções públicas
async def create_car(
    car: CarSchema,
    current_user: User,
    db: AsyncSession
) -> Car:
    """
    Criar novo carro no sistema.

    Args:
        car: Dados do carro a ser criado
        current_user: Usuário autenticado
        db: Sessão do banco de dados

    Returns:
        Car: Carro criado com ID gerado

    Raises:
        HTTPException: Se placa já existe ou marca inválida
    """
```

### Comentários

```python
# ✅ Comentários para lógica complexa
# Verificar se a placa já está em uso antes de criar
plate_exists = await db.scalar(
    select(exists().where(Car.plate == car.plate))
)

# ❌ Evitar comentários óbvios
user_id = 1  # Define user_id como 1
```

### README e Documentação

- **README.md**: Instruções básicas de instalação e uso
- **docs/**: Documentação detalhada com exemplos
- **Changelog**: Histórico de versões e mudanças

## 🚀 Padrões de Deploy

### Variáveis de Ambiente

```python
# ✅ Usar Settings com Pydantic
class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    debug: bool = False

    class Config:
        env_file = '.env'
```

### Docker

```dockerfile
# ✅ Multi-stage build
FROM python:3.13-slim as builder
# Build dependencies

FROM python:3.13-slim as runtime
# Runtime image
```

### Logs

```python
# ✅ Usar logging estruturado
import logging

logger = logging.getLogger(__name__)

async def create_car(car_data):
    logger.info(f"Creating car: {car_data.model}")
    try:
        # Lógica
        logger.info(f"Car created successfully: {car.id}")
    except Exception as e:
        logger.error(f"Failed to create car: {e}")
        raise
```

## ✅ Checklist de Qualidade

Antes de fazer commit, verificar:

- [ ] **Testes**: Todos os testes passam
- [ ] **Linting**: `poetry run task lint` sem erros
- [ ] **Formatação**: `poetry run task format` aplicado
- [ ] **Type hints**: Todas as funções tipadas
- [ ] **Documentação**: Docstrings em funções públicas
- [ ] **Segurança**: Validações e autenticação implementadas
- [ ] **Migração**: Migração criada se necessário

## 🔄 Fluxo de Desenvolvimento

### 1. Criar Feature Branch
```bash
git checkout -b feature/new-car-endpoint
```

### 2. Desenvolver com TDD
```bash
# 1. Escrever teste
# 2. Implementar funcionalidade
# 3. Refatorar
poetry run task test
```

### 3. Verificar Qualidade
```bash
poetry run task lint
poetry run task format
poetry run task test
```

### 4. Commit e Push
```bash
git add .
git commit -m "feat: add new car endpoint with validation"
git push origin feature/new-car-endpoint
```

### 5. Pull Request
- Descrição clara da funcionalidade
- Testes incluídos
- Documentação atualizada

## 📋 Convenções de Commit

Usar [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Features
git commit -m "feat: add car search endpoint"

# Bug fixes
git commit -m "fix: resolve authentication issue"

# Documentation
git commit -m "docs: update API documentation"

# Refactoring
git commit -m "refactor: improve database queries"

# Tests
git commit -m "test: add unit tests for car model"

# Breaking changes
git commit -m "feat!: change API response format"
```

## 🎯 Objetivos de Qualidade

- **Cobertura de testes**: ≥ 90%
- **Performance**: APIs respondem em < 200ms
- **Segurança**: Todas as rotas protegidas adequadamente
- **Documentação**: Todas as APIs documentadas no OpenAPI
- **Manutenibilidade**: Complexidade ciclomática < 10
- **Confiabilidade**: Zero erros em produção