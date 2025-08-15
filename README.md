# Car API

Uma API REST para gerenciamento de carros e usu�rios, construída com FastAPI, SQLAlchemy e SQLite.

## Pré-requisitos

- Python 3.13 ou superior
- pipx (para instalar Poetry)
- Poetry (para gerenciamento de dependências)

## Configuração do Ambiente

### 1. Instalação do pipx

O pipx é usado para instalar ferramentas Python em ambientes isolados.
[Documentação do pipx](https://pipx.pypa.io/stable/installation/)

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

Com o pipx instalado, instale o Poetry:

```bash
pipx install poetry
```

Verifique a instalação:
```bash
poetry --version
```

## Configuração do Projeto

### 1. Clone o repositório
```bash
git clone https://github.com/pycodebr/car_api.git
cd car_api
```

### 2. Instalar dependências

Instale todas as dependências do projeto (incluindo as de desenvolvimento):

```bash
poetry install
```

Este comando irá:
- Criar um ambiente virtual automaticamente
- Instalar todas as dependências listadas em `pyproject.toml`
- Instalar as dependências de desenvolvimento (pytest, ruff, taskipy)

### 3. Configurar o banco de dados

Execute as migrações do Alembic para criar as tabelas no banco de dados:

```bash
poetry run alembic upgrade head
```

## Comandos Disponíveis (Taskipy)

O projeto utiliza o Taskipy para automatizar tarefas comuns. Todos os comandos devem ser executados através do Poetry:

### Executar a aplicação
```bash
poetry run task run
```
Inicia o servidor de desenvolvimento FastAPI na porta padrão.

### Executar testes
```bash
poetry run task test
```
Este comando irá:
- Executar o lint automaticamente (pre_test)
- Rodar todos os testes com pytest
- Gerar relat�rio de cobertura HTML (post_test)

### Linting (verificação de código)
```bash
poetry run task lint
```
Verifica o código usando Ruff para identificar problemas de estilo e qualidade.

### Formatação de código
```bash
poetry run task format
```
Este comando irá:
- Executar correções automáticas do lint (pre_format)
- Formatar o código usando Ruff

## Estrutura do Projeto

```
car_api/
    car_api/              # Código principal da aplicação
        app.py            # Arquivo principal do FastAPI
        core/             # Configurações e funcionalidades centrais
            database.py   # Configurações do banco de dados
            security.py   # Funções de segurança e autenticação
            settings.py   # Configurações da aplicação
        models/           # Modelos SQLAlchemy
            base.py       # Modelo base
            cars.py       # Modelo de carros
            users.py      # Modelo de usuários
        routers/          # Rotas da API
            auth.py       # Rotas de autenticação
            brands.py     # Rotas de marcas
            cars.py       # Rotas de carros
            users.py      # Rotas de usuários
        schemas/          # Esquemas Pydantic
            auth.py       # Esquemas de autenticação
            brands.py     # Esquemas de marcas
            cars.py       # Esquemas de carros
            users.py      # Esquemas de usuários
    migrations/           # Migrações do Alembic
    tests/                # Testes automatizados
    alembic.ini           # Configuração do Alembic
    pyproject.toml        # Configuração do projeto e dependências
    README.md             # Este arquivo
```

## Dependências Principais

- **FastAPI**: Framework web moderno e rápido
- **SQLAlchemy**: ORM para Python
- **Alembic**: Ferramenta de migração de banco de dados
- **Aiosqlite**: Driver SQLite assíncrono
- **Pydantic Settings**: Gerenciamento de configurações
- **PWDLib**: Biblioteca para hash de senhas
- **PyJWT**: Biblioteca para tokens JWT
- **mkdocs**: Biblioteca para a documentação online do projeto

## Dependências de Desenvolvimento

- **Pytest**: Framework de testes
- **Pytest-asyncio**: Suporte para testes assíncronos
- **Ruff**: Linter e formatador de código
- **Taskipy**: Automação de tarefas
- **Coverage**: Relatórios de cobertura de testes

## Executando Comandos no Ambiente Virtual

Todos os comandos devem ser prefixados com `poetry run` para garantir que sejam executados no ambiente virtual correto:

```bash
# Executar a aplicação na porta 8000
poetry run task run

# Executar a documentação na porta 8001
poetry run task docs

# Executar testes
poetry run task test

# Verificar código
poetry run task lint

# Formatar código
poetry run task format

# Executar comandos do Alembic
poetry run alembic upgrade head
poetry run alembic revision --autogenerate -m "descrição da migração"

# Executar pytest diretamente
poetry run pytest

# Executar outros comandos Python
poetry run python -c "print('Hello World')"
```

## Desenvolvimento

1. Faça suas alterações no código
2. Execute os testes: `poetry run task test`
3. Verifique o código: `poetry run task lint`
4. Formate o código: `poetry run task format`
5. Execute a aplicação: `poetry run task run`
6. Execute a documentação: `poetry run task docs`

## Relatórios de Cobertura

Após executar os testes com `poetry run task test`, um relatório HTML de cobertura será gerado na pasta `htmlcov/`. Abra o arquivo `htmlcov/index.html` no seu navegador para visualizar o relatório detalhado.