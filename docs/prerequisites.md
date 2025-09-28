# Pré-requisitos

## 🐍 Python

### Versão Necessária
- **Python 3.13 ou superior**

O projeto utiliza recursos modernos do Python, incluindo:
- Type hints avançados
- Pattern matching (match/case)
- Melhorias de performance
- Novos recursos de async/await

### Verificar Versão
```bash
python --version
# ou
python3 --version
```

### Instalação do Python

#### 🐧 Linux
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.13 python3.13-venv python3.13-dev

# Fedora/CentOS/RHEL
sudo dnf install python3.13 python3.13-venv python3.13-devel

# Arch Linux
sudo pacman -S python
```

#### 🍎 macOS
```bash
# Usando Homebrew (recomendado)
brew install python@3.13

# Ou baixar do site oficial
# https://www.python.org/downloads/macos/
```

#### 🪟 Windows
1. Baixe do [site oficial](https://www.python.org/downloads/windows/)
2. Execute o instalador
3. ✅ **IMPORTANTE**: Marque "Add Python to PATH"

## 📦 Gerenciador de Pacotes

### pipx (Recomendado)
O pipx é usado para instalar ferramentas Python em ambientes isolados.

#### Instalação do pipx

**Linux:**
```bash
sudo apt update
sudo apt install pipx
pipx ensurepath
```

**macOS:**
```bash
brew install pipx
pipx ensurepath
```

**Windows:**
```bash
python -m pip install --user pipx
python -m pipx ensurepath
```

#### Após a instalação
Reinicie o terminal ou execute:
```bash
# Linux
source ~/.bashrc

# macOS com zsh
source ~/.zshrc
```

### Poetry
O Poetry é usado para gerenciamento de dependências e ambientes virtuais.

#### Instalação via pipx
```bash
pipx install poetry
```

#### Verificar instalação
```bash
poetry --version
```

#### Configuração recomendada
```bash
# Criar .venv na pasta do projeto
poetry config virtualenvs.in-project true

# Verificar configuração
poetry config --list
```

## 🗃️ Banco de Dados

### Desenvolvimento (SQLite)
- **Incluído no Python**: Não requer instalação adicional
- **Arquivo local**: `car.db` criado automaticamente

### Produção (PostgreSQL)

#### 🐧 Linux
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# Fedora/CentOS/RHEL
sudo dnf install postgresql postgresql-server postgresql-contrib

# Arch Linux
sudo pacman -S postgresql
```

#### 🍎 macOS
```bash
# Homebrew
brew install postgresql

# Ou usando Postgres.app
# https://postgresapp.com/
```

#### 🪟 Windows
1. Baixe do [site oficial](https://www.postgresql.org/download/windows/)
2. Execute o instalador
3. Configure usuário e senha

#### Docker (Alternativa)
```bash
# PostgreSQL via Docker
docker run --name postgres-car-api \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=car_api \
  -p 5432:5432 \
  -d postgres:15
```

## 🔧 Ferramentas de Desenvolvimento

### Git
```bash
# Linux
sudo apt install git  # Ubuntu/Debian
sudo dnf install git  # Fedora/CentOS/RHEL

# macOS
brew install git

# Windows
# Baixar de: https://git-scm.com/download/win
```

### Editor/IDE (Opcional)
Editores recomendados:
- **VS Code** com extensões Python
- **PyCharm** (Community ou Professional)
- **Vim/Neovim** com plugins Python
- **Sublime Text** com Package Control

### Docker (Opcional)
Para desenvolvimento com containers:

```bash
# Linux
sudo apt install docker.io docker-compose  # Ubuntu/Debian
sudo dnf install docker docker-compose     # Fedora/CentOS/RHEL

# macOS
brew install docker docker-compose

# Windows
# Baixar Docker Desktop: https://www.docker.com/products/docker-desktop
```

## 🌐 Variáveis de Ambiente

### Arquivo .env
O projeto requer um arquivo `.env` com as seguintes variáveis:

```bash
# Banco de Dados
DATABASE_URL='postgresql+psycopg://user:password@localhost:5432/dbname'

# JWT (altere para sua chave secreta)
JWT_SECRET_KEY='sua-chave-secreta-super-forte'
JWT_ALGORITHM='HS256'
JWT_EXPIRATION_MINUTES=30
```

### Gerar Chave JWT
```bash
# Usando Python
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Usando OpenSSL
openssl rand -base64 64
```

## ✅ Verificação dos Pré-requisitos

Execute este script para verificar se tudo está instalado:

```bash
#!/bin/bash

echo "🔍 Verificando pré-requisitos..."

# Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "✅ Python: $PYTHON_VERSION"
else
    echo "❌ Python não encontrado"
fi

# Poetry
if command -v poetry &> /dev/null; then
    POETRY_VERSION=$(poetry --version | cut -d' ' -f3)
    echo "✅ Poetry: $POETRY_VERSION"
else
    echo "❌ Poetry não encontrado"
fi

# Git
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version | cut -d' ' -f3)
    echo "✅ Git: $GIT_VERSION"
else
    echo "❌ Git não encontrado"
fi

# PostgreSQL (opcional)
if command -v psql &> /dev/null; then
    PSQL_VERSION=$(psql --version | cut -d' ' -f3)
    echo "✅ PostgreSQL: $PSQL_VERSION"
else
    echo "⚠️  PostgreSQL não encontrado (opcional)"
fi

echo "🎉 Verificação concluída!"
```

## 🔧 Solução de Problemas

### Python não encontrado
```bash
# Verificar se está no PATH
echo $PATH

# Criar alias (temporário)
alias python=python3

# Adicionar ao .bashrc/.zshrc (permanente)
echo 'alias python=python3' >> ~/.bashrc
```

### Poetry não funciona
```bash
# Reinstalar via pipx
pipx uninstall poetry
pipx install poetry

# Verificar PATH
poetry config --list
```

### Problemas de permissão (Linux)
```bash
# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Relogar ou executar
newgrp docker
```

### PostgreSQL não conecta
```bash
# Verificar se está rodando
sudo systemctl status postgresql

# Iniciar serviço
sudo systemctl start postgresql

# Criar usuário/banco
sudo -u postgres createuser --interactive
sudo -u postgres createdb car_api
```