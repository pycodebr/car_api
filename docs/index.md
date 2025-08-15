# Car API - Documentação Completa

Uma API REST completa para gerenciamento de carros e usuários, construída com FastAPI, SQLAlchemy e SQLite.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração do Projeto](#configuração-do-projeto)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [API Endpoints](#api-endpoints)
- [Modelos de Dados](#modelos-de-dados)
- [Autenticação e Segurança](#autenticação-e-segurança)
- [Desenvolvimento](#desenvolvimento)
- [Testes](#testes)
- [Deploy](#deploy)
- [Contribuição](#contribuição)

## 🚀 Visão Geral

A Car API é uma aplicação backend moderna que oferece um sistema completo de gerenciamento de carros com as seguintes funcionalidades:

- **Gestão de Usuários**: Cadastro, autenticação e autorização
- **Gestão de Carros**: CRUD completo para veículos
- **Gestão de Marcas**: Organização por fabricantes
- **Autenticação JWT**: Sistema seguro de tokens
- **Testes Automatizados**: Cobertura completa com pytest
- **Documentação Automática**: OpenAPI/Swagger integrado

### 🛠️ Tecnologias Utilizadas

- **[FastAPI](https://fastapi.tiangolo.com/)**: Framework web moderno e de alta performance
- **[SQLAlchemy 2.0](https://www.sqlalchemy.org/)**: ORM com suporte assíncrono
- **[Alembic](https://alembic.sqlalchemy.org/)**: Ferramenta de migração de banco de dados
- **[Pydantic](https://pydantic-docs.helpmanual.io/)**: Validação de dados com tipos Python
- **[SQLite](https://www.sqlite.org/)**: Banco de dados leve e eficiente
- **[Poetry](https://python-poetry.org/)**: Gerenciamento de dependências
- **[Pytest](https://pytest.org/)**: Framework de testes
- **[Ruff](https://beta.ruff.rs/)**: Linter e formatador de código

## 📋 Pré-requisitos

- **Python 3.13+**
- **pipx** (para instalar Poetry)
- **Poetry** (para gerenciamento de dependências)
- **Git** (para controle de versão)

## 💾 Instalação

### 1. Instalação do pipx

O pipx é usado para instalar ferramentas Python em ambientes isolados.

#### No Linux:
```bash
sudo apt update
sudo apt install pipx
pipx ensurepath
```

#### No macOS:
```bash
brew install pipx
pipx ensurepath
```

#### No Windows:
```bash
python -m pip install --user pipx
python -m pipx ensurepath
```

Após a instalação, reinicie o terminal ou execute:
```bash
source ~/.bashrc  # Linux
source ~/.zshrc   # macOS com zsh
```

### 2. Instalação do Poetry

```bash
pipx install poetry
poetry --version
```

## ⚙️ Configuração do Projeto

### 1. Clone o Repositório
```bash
git clone https://github.com/pycodebr/car_api.git
cd car_api
```

### 2. Instalar Dependências

Instale todas as dependências (incluindo desenvolvimento):

```bash
poetry install
```

### 3. Configurar Banco de Dados

Execute as migrações para criar as tabelas:

```bash
poetry run alembic upgrade head
```

### 4. Executar a Aplicação

```bash
poetry run task run
```

A aplicação estará disponível em `http://127.0.0.1:8000`

- **Documentação Interativa**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

## 📁 Estrutura do Projeto

```
car_api/
├── car_api/                    # Código principal da aplicação
│   ├── app.py                  # Arquivo principal do FastAPI
│   ├── core/                   # Configurações centrais
│   │   ├── database.py         # Configuração do banco de dados
│   │   ├── security.py         # Funções de segurança e JWT
│   │   └── settings.py         # Configurações da aplicação
│   ├── models/                 # Modelos SQLAlchemy
│   │   ├── __init__.py         
│   │   ├── base.py             # Modelo base
│   │   ├── cars.py             # Modelos Car e Brand
│   │   └── users.py            # Modelo User
│   ├── routers/                # Rotas da API
│   │   ├── __init__.py         
│   │   ├── auth.py             # Autenticação e login
│   │   ├── brands.py           # CRUD de marcas
│   │   ├── cars.py             # CRUD de carros
│   │   └── users.py            # CRUD de usuários
│   └── schemas/                # Esquemas Pydantic
│       ├── __init__.py         
│       ├── auth.py             # Esquemas de autenticação
│       ├── brands.py           # Esquemas de marcas
│       ├── cars.py             # Esquemas de carros
│       └── users.py            # Esquemas de usuários
├── migrations/                 # Migrações do Alembic
│   ├── versions/               # Versões das migrações
│   ├── env.py                  # Configuração do ambiente
│   └── script.py.mako          # Template de migração
├── tests/                      # Testes automatizados
│   ├── conftest.py             # Configurações de teste
│   ├── test_auth.py            # Testes de autenticação
│   ├── test_brands.py          # Testes de marcas
│   ├── test_cars.py            # Testes de carros
│   ├── test_db.py              # Testes de banco
│   └── test_users.py           # Testes de usuários
├── docs/                       # Documentação MkDocs
├── htmlcov/                    # Relatórios de cobertura
├── alembic.ini                 # Configuração do Alembic
├── pyproject.toml              # Configuração do projeto
├── poetry.lock                 # Lock de dependências
└── README.md                   # Documentação básica
```

## 🌐 API Endpoints

### Autenticação

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/v1/auth/token` | Obter token de acesso |

### Usuários

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/v1/users/` | Criar usuário |
| `GET` | `/api/v1/users/` | Listar usuários |
| `GET` | `/api/v1/users/{user_id}` | Obter usuário por ID |
| `PUT` | `/api/v1/users/{user_id}` | Atualizar usuário |
| `DELETE` | `/api/v1/users/{user_id}` | Excluir usuário |

### Marcas

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/v1/brands/` | Criar marca |
| `GET` | `/api/v1/brands/` | Listar marcas |
| `GET` | `/api/v1/brands/{brand_id}` | Obter marca por ID |
| `PUT` | `/api/v1/brands/{brand_id}` | Atualizar marca |
| `DELETE` | `/api/v1/brands/{brand_id}` | Excluir marca |

### Carros

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/v1/cars/` | Criar carro |
| `GET` | `/api/v1/cars/` | Listar carros |
| `GET` | `/api/v1/cars/{car_id}` | Obter carro por ID |
| `PUT` | `/api/v1/cars/{car_id}` | Atualizar carro |
| `DELETE` | `/api/v1/cars/{car_id}` | Excluir carro |

### Health Check

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/health_check` | Verificar status da API |

## 🗃️ Modelos de Dados

### User (Usuário)
```python
class User:
    id: int
    username: str (único)
    email: str (único)
    password_hash: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    cars: List[Car]  # Relacionamento
```

### Brand (Marca)
```python
class Brand:
    id: int
    name: str (único)
    description: str (opcional)
    is_active: bool
    created_at: datetime
    updated_at: datetime
    cars: List[Car]  # Relacionamento
```

### Car (Carro)
```python
class Car:
    id: int
    model: str
    factory_year: int
    model_year: int
    color: str
    plate: str (único)
    fuel_type: FuelType (enum)
    transmission: TransmissionType (enum)
    price: Decimal
    description: str (opcional)
    is_available: bool
    brand_id: int (FK)
    owner_id: int (FK)
    created_at: datetime
    updated_at: datetime
    brand: Brand  # Relacionamento
    owner: User   # Relacionamento
```

### Enums

#### FuelType (Tipo de Combustível)
- `gasoline` - Gasolina
- `ethanol` - Etanol
- `flex` - Flex
- `diesel` - Diesel
- `electric` - Elétrico
- `hybrid` - Híbrido

#### TransmissionType (Tipo de Transmissão)
- `manual` - Manual
- `automatic` - Automática
- `semi_automatic` - Semi-automática
- `cvt` - CVT

## 🔐 Autenticação e Segurança

### JWT (JSON Web Tokens)

A API utiliza JWT para autenticação. O fluxo funciona da seguinte forma:

1. **Login**: Envie credenciais para `/api/v1/auth/token`
2. **Token**: Receba um token de acesso JWT
3. **Autorização**: Inclua o token no header `Authorization: Bearer {token}`

### Exemplo de Autenticação

```bash
# 1. Fazer login
curl -X POST "http://localhost:8000/api/v1/auth/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=seu_usuario&password=sua_senha"

# Resposta:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer"
# }

# 2. Usar o token em requisições
curl -X GET "http://localhost:8000/api/v1/users/" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Hash de Senhas

As senhas são protegidas usando **Argon2**, um algoritmo de hash robusto e seguro.

## 🛠️ Desenvolvimento

### Comandos Taskipy

O projeto utiliza Taskipy para automatizar tarefas:

```bash
# Executar a aplicação
poetry run task run

# Executar testes com cobertura
poetry run task test

# Verificar código (linting)
poetry run task lint

# Formatar código
poetry run task format

# Executar documentação
poetry run task docs
```

### Workflow de Desenvolvimento

1. **Faça suas alterações no código**
2. **Execute os testes**: `poetry run task test`
3. **Verifique o código**: `poetry run task lint`
4. **Formate o código**: `poetry run task format`
5. **Execute a aplicação**: `poetry run task run`

### Migrações de Banco

```bash
# Gerar nova migração
poetry run alembic revision --autogenerate -m "descrição da alteração"

# Aplicar migrações
poetry run alembic upgrade head

# Reverter migração
poetry run alembic downgrade -1

# Histórico de migrações
poetry run alembic history
```

### Configurações do Ruff

O projeto usa Ruff para linting e formatação:

- **Linha máxima**: 79 caracteres
- **Aspas**: Simples (')
- **Regras ativas**: I, F, E, W, PL, PT
- **Pastas excluídas**: migrations, alembic, __pycache__, etc.

## 🧪 Testes

### Executar Testes

```bash
# Todos os testes com cobertura
poetry run task test

# Testes específicos
poetry run pytest tests/test_cars.py

# Testes com verbose
poetry run pytest -v

# Testes com parada no primeiro erro
poetry run pytest -x
```

### Cobertura de Código

Após executar `poetry run task test`, um relatório HTML é gerado:

```bash
# Abrir relatório de cobertura
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Estrutura dos Testes

- **conftest.py**: Fixtures compartilhadas
- **test_auth.py**: Testes de autenticação
- **test_users.py**: Testes CRUD de usuários
- **test_brands.py**: Testes CRUD de marcas
- **test_cars.py**: Testes CRUD de carros
- **test_db.py**: Testes de banco de dados

## 🚀 Deploy

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Banco de dados
DATABASE_URL=sqlite:///./car.db

# JWT
SECRET_KEY=sua_chave_secreta_super_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Aplicação
DEBUG=False
```

### Docker (Opcional)

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Instalar Poetry
RUN pip install poetry

# Copiar arquivos de dependência
COPY pyproject.toml poetry.lock ./

# Instalar dependências
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev

# Copiar código
COPY . .

# Executar migrações e aplicação
CMD ["poetry", "run", "alembic", "upgrade", "head", "&&", "poetry", "run", "uvicorn", "car_api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Produção

Para produção, recomenda-se:

1. **Banco de dados**: PostgreSQL ou MySQL
2. **Servidor ASGI**: Uvicorn com Gunicorn
3. **Proxy reverso**: Nginx
4. **HTTPS**: Certificados SSL/TLS
5. **Monitoramento**: Logs e métricas

## 🤝 Contribuição

### Como Contribuir

1. **Fork** o repositório
2. **Clone** seu fork localmente
3. **Crie** uma branch para sua feature: `git checkout -b minha-feature`
4. **Faça** suas alterações
5. **Execute** os testes: `poetry run task test`
6. **Commit** suas alterações: `git commit -m "feat: nova funcionalidade"`
7. **Push** para a branch: `git push origin minha-feature`
8. **Abra** um Pull Request

### Convenções

- **Commits**: Use [Conventional Commits](https://www.conventionalcommits.org/)
- **Código**: Siga PEP 8 e as regras do Ruff
- **Testes**: Mantenha cobertura de 100%
- **Documentação**: Documente novas funcionalidades

### Padrões de Commit

- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Alterações na documentação
- `style:` - Formatação (sem mudança de lógica)
- `refactor:` - Refatoração de código
- `test:` - Adição ou correção de testes
- `chore:` - Tarefas de manutenção

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

- **Email**: pycodebr@gmail.com
- **GitHub**: [https://github.com/pycodebr/car_api](https://github.com/pycodebr/car_api)
- **Issues**: [https://github.com/pycodebr/car_api/issues](https://github.com/pycodebr/car_api/issues)

---

**Desenvolvido com ❤️ pela equipe PyCodeBR**
