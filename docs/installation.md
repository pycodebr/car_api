# Instalação

## 🚀 Guia de Instalação Completo

### 1. Clone do Repositório

```bash
# HTTPS
git clone https://github.com/pycodebr/car_api.git

# SSH (se configurado)
git clone git@github.com:pycodebr/car_api.git

# Entrar no diretório
cd car_api
```

### 2. Verificar Estrutura do Projeto

```bash
ls -la
```

Você deve ver:
```
├── car_api/           # Código principal
├── tests/             # Testes automatizados
├── migrations/        # Migrações do banco
├── docs/             # Documentação
├── pyproject.toml    # Configuração do projeto
├── alembic.ini       # Configuração do Alembic
├── .env.example      # Exemplo de variáveis de ambiente
└── README.md         # Documentação básica
```

### 3. Configurar Ambiente Virtual

#### Usando Poetry (Recomendado)

```bash
# Instalar dependências e criar ambiente virtual
poetry install

# Verificar ambiente
poetry env info

# Ativar shell do ambiente (opcional)
poetry shell
```

#### Alternativa: venv + pip

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

```bash
# Copiar exemplo de configuração
cp .env.example .env

# Editar configurações
nano .env  # ou seu editor preferido
```

#### Configuração para Desenvolvimento (SQLite)
```bash
# .env
DATABASE_URL='sqlite+aiosqlite:///./car.db'
JWT_SECRET_KEY='your-super-secret-jwt-key-here'
JWT_ALGORITHM='HS256'
JWT_EXPIRATION_MINUTES=30
```

#### Configuração para Produção (PostgreSQL)
```bash
# .env
DATABASE_URL='postgresql+psycopg://postgres:postgres@localhost:5432/car_api'
JWT_SECRET_KEY='your-super-secret-jwt-key-here'
JWT_ALGORITHM='HS256'
JWT_EXPIRATION_MINUTES=30
```

### 5. Configurar Banco de Dados

#### Opção A: SQLite (Desenvolvimento)

```bash
# Executar migrações
poetry run alembic upgrade head

# Verificar se o banco foi criado
ls -la car.db
```

#### Opção B: PostgreSQL (Produção)

```bash
# 1. Criar banco de dados
sudo -u postgres createdb car_api

# 2. Criar usuário (opcional)
sudo -u postgres createuser --interactive car_api_user

# 3. Executar migrações
poetry run alembic upgrade head
```

#### Opção C: PostgreSQL com Docker

```bash
# 1. Subir banco via Docker Compose
docker-compose up -d db

# 2. Aguardar inicialização (30 segundos)
sleep 30

# 3. Executar migrações
poetry run alembic upgrade head
```

### 6. Verificar Instalação

#### Executar Testes
```bash
# Executar todos os testes
poetry run task test

# Ou apenas verificar se a aplicação inicia
poetry run task lint
```

#### Iniciar Aplicação
```bash
# Modo desenvolvimento
poetry run task run

# A aplicação estará disponível em:
# http://localhost:8000
```

#### Verificar Endpoints
```bash
# Health check
curl http://localhost:8000/health_check

# Documentação da API
# http://localhost:8000/docs
```

## 🐳 Instalação com Docker

### Desenvolvimento Completo

```bash
# Subir todos os serviços
docker-compose up -d

# Verificar logs
docker-compose logs -f

# Executar migrações
docker-compose exec api poetry run alembic upgrade head
```

### Apenas Banco de Dados

```bash
# Subir apenas PostgreSQL
docker-compose up -d db

# Verificar se está rodando
docker-compose ps
```

### Build da Aplicação

```bash
# Build da imagem
docker build -t car-api .

# Executar container
docker run -p 8000:8000 --env-file .env car-api
```

## 📋 Comandos Úteis

### Poetry

```bash
# Adicionar nova dependência
poetry add fastapi

# Adicionar dependência de desenvolvimento
poetry add --group dev pytest

# Atualizar dependências
poetry update

# Mostrar dependências
poetry show

# Exportar requirements.txt
poetry export -f requirements.txt --output requirements.txt
```

### Alembic (Migrações)

```bash
# Criar nova migração
poetry run alembic revision --autogenerate -m "descrição"

# Aplicar migrações
poetry run alembic upgrade head

# Reverter migração
poetry run alembic downgrade -1

# Verificar status
poetry run alembic current

# Histórico de migrações
poetry run alembic history
```

### Taskipy (Tarefas)

```bash
# Ver todas as tarefas disponíveis
poetry run task --list

# Executar tarefas
poetry run task run      # Iniciar aplicação
poetry run task test     # Executar testes
poetry run task lint     # Verificar código
poetry run task format   # Formatar código
poetry run task docs     # Iniciar documentação
```

## 🔧 Solução de Problemas

### Erro: "poetry not found"
```bash
# Reinstalar Poetry via pipx
pipx uninstall poetry
pipx install poetry

# Verificar PATH
export PATH="$HOME/.local/bin:$PATH"
```

### Erro: "No module named 'car_api'"
```bash
# Verificar se está no ambiente correto
poetry env info

# Reinstalar em modo development
poetry install
```

### Erro de Migração
```bash
# Verificar conexão com banco
poetry run python -c "from car_api.core.database import engine; print('OK')"

# Resetar migrações (cuidado!)
rm -rf migrations/versions/*.py
poetry run alembic revision --autogenerate -m "initial"
poetry run alembic upgrade head
```

### Erro de Dependências
```bash
# Limpar cache do Poetry
poetry cache clear . --all

# Reinstalar dependências
poetry install --no-cache
```

### Porta já em uso
```bash
# Verificar processo usando a porta
lsof -i :8000

# Matar processo
kill -9 <PID>

# Ou usar porta diferente
poetry run fastapi dev car_api/app.py --port 8001
```

### Problemas com PostgreSQL
```bash
# Verificar se está rodando
sudo systemctl status postgresql

# Reiniciar serviço
sudo systemctl restart postgresql

# Verificar logs
sudo journalctl -u postgresql

# Testar conexão
psql -h localhost -U postgres -d car_api
```

## ✅ Verificação Final

Execute este checklist para confirmar que tudo está funcionando:

```bash
# 1. Verificar ambiente
poetry env info

# 2. Verificar dependências
poetry check

# 3. Executar testes
poetry run task test

# 4. Verificar linting
poetry run task lint

# 5. Iniciar aplicação
poetry run task run
```

Se todos os comandos executarem sem erro, sua instalação está completa! 🎉

## 📚 Próximos Passos

Após a instalação bem-sucedida:

1. 📖 Leia a [Configuração do Projeto](configuration.md)
2. 🏗️ Entenda a [Estrutura do Projeto](structure.md)
3. 🚀 Explore os [API Endpoints](api-endpoints.md)
4. 🧪 Execute os [Testes](testing.md)
5. 💻 Inicie o [Desenvolvimento](development.md)