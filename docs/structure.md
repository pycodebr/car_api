# Estrutura do Projeto

## 📁 Visão Geral da Estrutura

```
car_api/
├── car_api/                    # 📦 Código principal da aplicação
│   ├── __init__.py
│   ├── app.py                  # 🚀 Arquivo principal do FastAPI
│   ├── core/                   # ⚙️ Funcionalidades centrais
│   │   ├── __init__.py
│   │   ├── database.py         # 🗃️ Configuração do banco de dados
│   │   ├── security.py         # 🔐 Funções de segurança e JWT
│   │   └── settings.py         # 📋 Configurações da aplicação
│   ├── models/                 # 🏗️ Modelos SQLAlchemy
│   │   ├── __init__.py
│   │   ├── base.py             # 📄 Classe base para modelos
│   │   ├── cars.py             # 🚗 Modelos de carros e marcas
│   │   └── users.py            # 👤 Modelo de usuários
│   ├── routers/                # 🛣️ Rotas da API
│   │   ├── __init__.py
│   │   ├── auth.py             # 🔑 Rotas de autenticação
│   │   ├── brands.py           # 🏷️ Rotas de marcas
│   │   ├── cars.py             # 🚗 Rotas de carros
│   │   └── users.py            # 👤 Rotas de usuários
│   └── schemas/                # 📝 Esquemas Pydantic
│       ├── __init__.py
│       ├── auth.py             # 🔑 Esquemas de autenticação
│       ├── brands.py           # 🏷️ Esquemas de marcas
│       ├── cars.py             # 🚗 Esquemas de carros
│       └── users.py            # 👤 Esquemas de usuários
├── docs/                       # 📚 Documentação do projeto
│   ├── index.md                # 🏠 Página inicial da documentação
│   ├── overview.md             # 📖 Visão geral
│   ├── prerequisites.md        # 🔧 Pré-requisitos
│   ├── installation.md         # 💿 Instalação
│   ├── configuration.md        # ⚙️ Configuração
│   ├── guidelines.md           # 📏 Guidelines e padrões
│   ├── structure.md            # 📁 Este arquivo
│   └── ...                     # 📄 Outros arquivos de documentação
├── migrations/                 # 🔄 Migrações do Alembic
│   ├── env.py                  # 🌍 Configuração do ambiente Alembic
│   └── versions/               # 📅 Versões das migrações
│       └── *.py                # 📄 Arquivos de migração
├── tests/                      # 🧪 Testes automatizados
│   ├── __init__.py
│   ├── conftest.py             # ⚙️ Configurações dos testes
│   ├── test_auth.py            # 🔑 Testes de autenticação
│   ├── test_brands.py          # 🏷️ Testes de marcas
│   ├── test_cars.py            # 🚗 Testes de carros
│   ├── test_db.py              # 🗃️ Testes de banco de dados
│   └── test_users.py           # 👤 Testes de usuários
├── .env                        # 🔐 Variáveis de ambiente (local)
├── .env.example                # 📋 Exemplo de variáveis de ambiente
├── alembic.ini                 # ⚙️ Configuração do Alembic
├── docker-compose.yml          # 🐳 Configuração Docker Compose
├── Dockerfile                  # 🐳 Imagem Docker da aplicação
├── Dockerfile.mkdocs           # 📚 Imagem Docker para documentação
├── poetry.lock                 # 🔒 Lock file do Poetry
├── pyproject.toml              # 📦 Configuração do projeto
├── README.md                   # 📖 Documentação básica
└── requirements.txt            # 📋 Dependências (gerado pelo Poetry)
```

## 📦 Detalhamento dos Diretórios

### 🚀 `car_api/app.py` - Aplicação Principal

Arquivo de entrada da aplicação FastAPI:

```python
from fastapi import FastAPI
from car_api.routers import auth, brands, cars, users

app = FastAPI()

# Configuração de routers
app.include_router(auth.router, prefix='/api/v1/auth', tags=['authentication'])
app.include_router(users.router, prefix='/api/v1/users', tags=['users'])
app.include_router(brands.router, prefix='/api/v1/brands', tags=['brands'])
app.include_router(cars.router, prefix='/api/v1/cars', tags=['cars'])

# Health check endpoint
@app.get('/health_check')
def health_check():
    return {'status': 'ok'}
```

**Responsabilidades:**
- Criar instância do FastAPI
- Registrar routers e middleware
- Configurar CORS e outros middleware
- Definir endpoints globais

### ⚙️ `car_api/core/` - Funcionalidades Centrais

#### `database.py` - Configuração do Banco

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(settings.database_url)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with SessionLocal() as session:
        yield session
```

**Responsabilidades:**
- Configurar engine do SQLAlchemy
- Gerenciar sessões de banco
- Dependency injection para sessões

#### `security.py` - Segurança e Autenticação

```python
from pwdlib import PasswordHash
import jwt

pwd_context = PasswordHash.recommended()

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    return jwt.encode(data, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
```

**Responsabilidades:**
- Hash de senhas com Argon2
- Criação e validação de tokens JWT
- Dependency para usuário atual
- Verificação de permissões

#### `settings.py` - Configurações

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = 'sqlite+aiosqlite:///./car.db'
    jwt_secret_key: str
    jwt_algorithm: str = 'HS256'
    jwt_expiration_minutes: int = 30

    class Config:
        env_file = '.env'
```

**Responsabilidades:**
- Centralizar configurações
- Validação de variáveis de ambiente
- Type hints para configurações

### 🏗️ `car_api/models/` - Modelos de Dados

#### `base.py` - Classe Base

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

#### `users.py` - Modelo de Usuários

```python
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(onupdate=func.now())

    cars: Mapped[list['Car']] = relationship(back_populates='owner')
```

#### `cars.py` - Modelos de Carros e Marcas

```python
class Brand(Base):
    __tablename__ = 'brands'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(default=True)

class Car(Base):
    __tablename__ = 'cars'

    id: Mapped[int] = mapped_column(primary_key=True)
    model: Mapped[str] = mapped_column(String(100))
    factory_year: Mapped[int]
    model_year: Mapped[int]
    color: Mapped[str] = mapped_column(String(30))
    plate: Mapped[str] = mapped_column(String(10), unique=True)
    fuel_type: Mapped[FuelType]
    transmission: Mapped[TransmissionType]
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    # Relacionamentos
    brand_id: Mapped[int] = mapped_column(ForeignKey('brands.id'))
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    brand: Mapped['Brand'] = relationship('Brand', back_populates='cars')
    owner: Mapped['User'] = relationship('User', back_populates='cars')
```

**Características dos Modelos:**
- **Type hints completos** com `Mapped[]`
- **Relacionamentos bidirecionais**
- **Campos de auditoria** (created_at, updated_at)
- **Validações de integridade**
- **Enums** para campos categóricos

### 🛣️ `car_api/routers/` - Rotas da API

Cada router implementa as operações CRUD para sua entidade:

#### Estrutura Padrão de Router

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=Schema)
async def create_item(): pass

@router.get('/', status_code=status.HTTP_200_OK, response_model=ListSchema)
async def list_items(): pass

@router.get('/{item_id}', status_code=status.HTTP_200_OK, response_model=Schema)
async def get_item(): pass

@router.put('/{item_id}', status_code=status.HTTP_200_OK, response_model=Schema)
async def update_item(): pass

@router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(): pass
```

#### Funcionalidades Implementadas

**`auth.py`:**
- `POST /token` - Gerar token de acesso
- `POST /refresh_token` - Renovar token

**`users.py`:**
- CRUD completo de usuários
- Busca por username/email
- Validação de unicidade

**`brands.py`:**
- CRUD completo de marcas
- Filtros por status ativo
- Proteção contra deleção com carros

**`cars.py`:**
- CRUD completo de carros
- Filtros avançados (preço, combustível, etc.)
- Verificação de propriedade
- Busca por modelo/placa

### 📝 `car_api/schemas/` - Esquemas Pydantic

#### Padrão de Nomenclatura

```python
# Schema para criação (entrada)
class UserSchema(BaseModel):
    username: str
    email: str
    password: str

# Schema para atualização (entrada parcial)
class UserUpdateSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

# Schema público (saída - sem senha)
class UserPublicSchema(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Schema para listagem
class UserListPublicSchema(BaseModel):
    users: list[UserPublicSchema]
    offset: int
    limit: int
```

#### Funcionalidades dos Schemas

**Validação de Entrada:**
```python
class CarSchema(BaseModel):
    model: str = Field(..., min_length=1, max_length=100)
    factory_year: int = Field(..., ge=1900, le=2030)
    price: Decimal = Field(..., gt=0)
    plate: str = Field(..., regex=r'^[A-Z]{3}[0-9]{4}$|^[A-Z]{3}[0-9][A-Z][0-9]{2}$')
```

**Configuração para SQLAlchemy:**
```python
class Config:
    from_attributes = True  # Permite conversão de modelos SQLAlchemy
```

### 🔄 `migrations/` - Migrações do Banco

#### Estrutura das Migrações

```
migrations/
├── env.py                      # Configuração do Alembic
└── versions/
    └── 20231201_120000_create_tables.py
```

#### Exemplo de Migração

```python
"""create tables

Revision ID: d519a757c476
Revises:
Create Date: 2023-12-01 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = 'd519a757c476'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Criar tabelas
    op.create_table('users', ...)
    op.create_table('brands', ...)
    op.create_table('cars', ...)

def downgrade() -> None:
    # Reverter tabelas
    op.drop_table('cars')
    op.drop_table('brands')
    op.drop_table('users')
```

### 🧪 `tests/` - Testes Automatizados

#### Estrutura dos Testes

```
tests/
├── conftest.py                 # Fixtures compartilhadas
├── test_auth.py               # Testes de autenticação
├── test_brands.py             # Testes de marcas
├── test_cars.py               # Testes de carros
├── test_db.py                 # Testes de banco
└── test_users.py              # Testes de usuários
```

#### Fixtures Principais (`conftest.py`)

```python
@pytest_asyncio.fixture
async def db_session():
    # Sessão de banco para testes

@pytest_asyncio.fixture
async def client(db_session):
    # Cliente HTTP para testes

@pytest_asyncio.fixture
async def sample_user(db_session):
    # Usuário de exemplo para testes

@pytest_asyncio.fixture
async def auth_headers(sample_user):
    # Headers de autenticação
```

#### Padrão de Testes

```python
class TestCarEndpoints:
    async def test_create_car_success(self, client, auth_headers):
        # Teste de criação bem-sucedida

    async def test_create_car_invalid_data(self, client, auth_headers):
        # Teste com dados inválidos

    async def test_get_car_not_found(self, client, auth_headers):
        # Teste de recurso não encontrado
```

## 🔧 Arquivos de Configuração

### `pyproject.toml` - Configuração Principal

```toml
[project]
name = "car-api"
version = "0.1.0"
description = "API para gerenciamento de carros"

[tool.ruff]
line-length = 79
select = ['I', 'F', 'E', 'W', 'PL', 'PT']

[tool.taskipy.tasks]
lint = 'ruff check'
format = 'ruff format'
test = 'pytest -v --cov=car_api'
run = 'fastapi dev car_api/app.py'
```

### `alembic.ini` - Configuração de Migrações

```ini
[alembic]
script_location = migrations
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s

sqlalchemy.url =
```

### `docker-compose.yml` - Orquestração

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgresql+psycopg://postgres:postgres@db:5432/car_api

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: car_api
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## 📊 Métricas da Estrutura

### Tamanho dos Módulos

| Módulo | Arquivos | Linhas de Código | Responsabilidade |
|--------|----------|------------------|------------------|
| `core/` | 3 | ~200 | Infraestrutura |
| `models/` | 3 | ~150 | Modelo de dados |
| `routers/` | 4 | ~800 | API endpoints |
| `schemas/` | 4 | ~300 | Validação |
| `tests/` | 6 | ~600 | Testes |

### Complexidade

- **Módulos independentes**: Baixo acoplamento
- **Responsabilidades claras**: Alta coesão
- **Facilidade de teste**: Dependency injection
- **Escalabilidade**: Fácil adicionar novos módulos

## 🎯 Princípios Arquiteturais

### Single Responsibility Principle (SRP)
Cada módulo tem uma responsabilidade específica:
- `routers/`: Apenas endpoints HTTP
- `models/`: Apenas estrutura de dados
- `schemas/`: Apenas validação
- `core/`: Apenas infraestrutura

### Dependency Inversion Principle (DIP)
```python
# ✅ Depende de abstração (AsyncSession)
async def create_car(db: AsyncSession):
    pass

# ❌ Dependeria de implementação concreta
async def create_car(postgres_connection):
    pass
```

### Open/Closed Principle (OCP)
- Fácil adicionar novos endpoints sem modificar existentes
- Fácil adicionar novos modelos sem afetar outros
- Middleware pode ser adicionado sem modificar routers

### Interface Segregation Principle (ISP)
- Schemas específicos para cada operação
- Dependencies injetadas apenas quando necessárias
- Interfaces pequenas e focadas

## 🚀 Escalabilidade

### Horizontal (Adicionar Funcionalidades)

1. **Novo Modelo de Dados:**
   ```
   car_api/models/categories.py      # Novo modelo
   car_api/schemas/categories.py     # Novos schemas
   car_api/routers/categories.py     # Novos endpoints
   tests/test_categories.py          # Novos testes
   ```

2. **Nova Funcionalidade:**
   ```
   car_api/core/notifications.py    # Nova infraestrutura
   car_api/services/email.py        # Nova service layer
   ```

### Vertical (Melhorar Existente)

1. **Otimização de Performance:**
   - Cache em `core/cache.py`
   - Rate limiting em `core/middleware.py`

2. **Melhor Observabilidade:**
   - Logging em `core/logging.py`
   - Métricas em `core/metrics.py`

## 📚 Próximos Passos

Para entender melhor a estrutura:

1. 📖 Leia os [Guidelines e Padrões](guidelines.md)
2. 🛠️ Explore os [API Endpoints](api-endpoints.md)
3. 🏗️ Entenda a [Modelagem do Sistema](system-modeling.md)
4. 💻 Comece o [Desenvolvimento](development.md)