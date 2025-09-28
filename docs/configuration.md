# Configuração do Projeto

## 🔧 Configurações Gerais

### Arquivo de Configuração Principal

O projeto utiliza o arquivo `car_api/core/settings.py` para gerenciar todas as configurações:

```python
# car_api/core/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = 'sqlite+aiosqlite:///./car.db'
    jwt_secret_key: str
    jwt_algorithm: str = 'HS256'
    jwt_expiration_minutes: int = 30

    class Config:
        env_file = '.env'
```

## 🌍 Variáveis de Ambiente

### Arquivo .env

Crie um arquivo `.env` na raiz do projeto com as seguintes configurações:

```bash
# Banco de Dados
DATABASE_URL='sqlite+aiosqlite:///./car.db'

# JWT Authentication
JWT_SECRET_KEY='your-super-secret-jwt-key-here-change-this-in-production'
JWT_ALGORITHM='HS256'
JWT_EXPIRATION_MINUTES=30
```

### Configurações por Ambiente

#### 🔬 Desenvolvimento (SQLite)
```bash
# .env.development
DATABASE_URL='sqlite+aiosqlite:///./car.db'
JWT_SECRET_KEY='dev-secret-key-not-for-production'
JWT_ALGORITHM='HS256'
JWT_EXPIRATION_MINUTES=60
DEBUG=true
```

#### 🧪 Testes (SQLite in-memory)
```bash
# .env.test
DATABASE_URL='sqlite+aiosqlite:///:memory:'
JWT_SECRET_KEY='test-secret-key'
JWT_ALGORITHM='HS256'
JWT_EXPIRATION_MINUTES=5
DEBUG=true
```

#### 🚀 Produção (PostgreSQL)
```bash
# .env.production
DATABASE_URL='postgresql+psycopg://username:password@localhost:5432/car_api'
JWT_SECRET_KEY='super-secure-production-key-64-chars-minimum'
JWT_ALGORITHM='HS256'
JWT_EXPIRATION_MINUTES=30
DEBUG=false
```

## 🗃️ Configuração de Banco de Dados

### SQLite (Desenvolvimento)

```bash
# Configuração automática
DATABASE_URL='sqlite+aiosqlite:///./car.db'
```

**Características:**
- ✅ Não requer instalação adicional
- ✅ Arquivo local (`car.db`)
- ✅ Ideal para desenvolvimento
- ❌ Não suporta múltiplas conexões simultâneas

### PostgreSQL (Produção)

#### Configuração Local
```bash
# 1. Instalar PostgreSQL
sudo apt install postgresql postgresql-contrib

# 2. Criar banco e usuário
sudo -u postgres psql
CREATE DATABASE car_api;
CREATE USER car_api_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE car_api TO car_api_user;
\q

# 3. Configurar .env
DATABASE_URL='postgresql+psycopg://car_api_user:secure_password@localhost:5432/car_api'
```

#### Configuração com Docker
```yaml
# docker-compose.yml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: car_api
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

```bash
# .env para Docker
DATABASE_URL='postgresql+psycopg://postgres:postgres@localhost:5432/car_api'
```

## 🔐 Configuração de Segurança JWT

### Gerar Chave Secreta Segura

```bash
# Método 1: Python
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Método 2: OpenSSL
openssl rand -base64 64

# Método 3: Online (cuidado com segurança)
# https://generate-secret.vercel.app/64
```

### Configurações de JWT

```bash
# Chave secreta (mínimo 64 caracteres)
JWT_SECRET_KEY='sua-chave-super-secreta-de-pelo-menos-64-caracteres-aqui'

# Algoritmo de criptografia
JWT_ALGORITHM='HS256'  # HS256, HS384, HS512, RS256, etc.

# Tempo de expiração em minutos
JWT_EXPIRATION_MINUTES=30  # 30 minutos (recomendado para produção)
```

### Configurações Avançadas de JWT

```python
# car_api/core/settings.py (versão expandida)
class Settings(BaseSettings):
    # ... outras configurações

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = 'HS256'
    jwt_expiration_minutes: int = 30
    jwt_refresh_expiration_days: int = 7  # Para refresh tokens

    # Segurança
    cors_origins: list[str] = ['http://localhost:3000', 'http://localhost:8080']
    allowed_hosts: list[str] = ['localhost', '127.0.0.1']

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # segundos
```

## ⚙️ Configuração do Alembic

### alembic.ini

```ini
# alembic.ini
[alembic]
script_location = migrations
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s
truncate_slug_length = 40

# Formato de saída
output_encoding = utf-8

# Configurações do banco
sqlalchemy.url =

[post_write_hooks]
hooks = black
black.type = console_scripts
black.entrypoint = black
black.options = -l 79 REVISION_SCRIPT_FILENAME

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

### migrations/env.py

```python
# migrations/env.py
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Importar modelos
from car_api.models.base import Base
from car_api.models import users, cars  # noqa
from car_api.core.settings import Settings

# Configurações
config = context.config
settings = Settings()

# Configurar logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadados dos modelos
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Executar migrações offline."""
    url = settings.database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    """Executar migrações com conexão."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Executar migrações assíncronas."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.database_url

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """Executar migrações online."""
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

## 🚀 Configuração do FastAPI

### Configurações da Aplicação

```python
# car_api/app.py (versão expandida)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from car_api.core.settings import Settings
from car_api.routers import auth, brands, cars, users

settings = Settings()

app = FastAPI(
    title="Car API",
    description="API para gerenciamento de carros e usuários",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Middleware Trusted Host
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts,
)

# Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(brands.router, prefix="/api/v1/brands", tags=["brands"])
app.include_router(cars.router, prefix="/api/v1/cars", tags=["cars"])

@app.get("/health_check")
def health_check():
    return {"status": "ok", "version": "0.1.0"}
```

## 🧪 Configuração de Testes

### pytest.ini

```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
addopts =
    -v
    --strict-markers
    --strict-config
    --cov=car_api
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=90
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
    database: Tests that require database
```

### conftest.py

```python
# tests/conftest.py
import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from car_api.app import app
from car_api.core.database import get_session
from car_api.models.base import Base

# Engine de teste
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL)
TestSessionLocal = async_sessionmaker(
    test_engine, expire_on_commit=False
)

@pytest_asyncio.fixture
async def db_session():
    """Criar sessão de banco para testes."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client(db_session):
    """Cliente HTTP para testes."""
    app.dependency_overrides[get_session] = lambda: db_session

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
```

## 📦 Configuração do Poetry

### pyproject.toml

```toml
[tool.poetry]
name = "car-api"
version = "0.1.0"
description = "API para gerenciamento de carros e usuários"
authors = ["PyCodeBR <pycodebr@gmail.com>"]
readme = "README.md"
packages = [{include = "car_api"}]

[tool.poetry.dependencies]
python = "^3.13"
fastapi = {extras = ["standard"], version = "^0.116.1"}
sqlalchemy = {extras = ["asyncio"], version = "^2.0.42"}
alembic = "^1.16.4"
aiosqlite = "^0.21.0"
psycopg = {extras = ["binary"], version = "^3.2.9"}
pydantic-settings = "^2.10.1"
pwdlib = {extras = ["argon2"], version = "^0.2.1"}
pyjwt = "^2.10.1"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0.0"
pytest-asyncio = "^0.25.0"
pytest-cov = "^5.0.0"
httpx = "^0.27.0"
ruff = "^0.12.7"
taskipy = "^1.14.1"
mkdocs = "^1.6.1"
mkdocs-material = "^9.5.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.pytest.ini_options]
pythonpath = "."
addopts = "-p no:warnings"
asyncio_default_fixture_loop_scope = "function"

[tool.coverage.run]
concurrency = ["thread", "greenlet"]

[tool.ruff]
line-length = 79
exclude = [
    ".git", ".tox", ".venv", "__pycache__",
    "migrations", "alembic"
]

[tool.ruff.lint]
select = ["I", "F", "E", "W", "PL", "PT"]
ignore = ["PLR2004", "PLR0917", "PLR0913", "PT022"]

[tool.ruff.format]
quote-style = "single"

[tool.taskipy.tasks]
lint = "ruff check"
format = "ruff format"
test = "pytest -v --cov=car_api"
run = "fastapi dev car_api/app.py"
docs = "mkdocs serve"
migrate = "alembic upgrade head"
```

## 🔧 Configurações Adicionais

### Logging

```python
# car_api/core/logging.py
import logging
from typing import Any

def setup_logging(level: str = "INFO") -> None:
    """Configurar logging da aplicação."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("app.log"),
        ],
    )

# Usar na aplicação
# setup_logging(settings.log_level)
```

### CORS

```python
# Configuração detalhada de CORS
CORS_SETTINGS = {
    "allow_origins": [
        "http://localhost:3000",      # React dev
        "http://localhost:8080",      # Vue dev
        "https://yourdomain.com",     # Produção
    ],
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": [
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
    ],
}
```

## ✅ Verificação de Configuração

Execute este script para verificar todas as configurações:

```python
# scripts/check_config.py
from car_api.core.settings import Settings
from car_api.core.database import engine

async def check_configuration():
    """Verificar configurações do projeto."""
    settings = Settings()

    print("🔧 Verificando configurações...")
    print(f"✅ Database URL: {settings.database_url}")
    print(f"✅ JWT Algorithm: {settings.jwt_algorithm}")
    print(f"✅ JWT Expiration: {settings.jwt_expiration_minutes} minutos")

    # Testar conexão com banco
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        print("✅ Conexão com banco: OK")
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(check_configuration())
```

```bash
# Executar verificação
poetry run python scripts/check_config.py
```

## 📚 Próximos Passos

Após configurar o projeto:

1. 📊 Entenda a [Estrutura do Projeto](structure.md)
2. 🔍 Explore os [Guidelines e Padrões](guidelines.md)
3. 🛠️ Comece o [Desenvolvimento](development.md)
4. 🧪 Execute os [Testes](testing.md)