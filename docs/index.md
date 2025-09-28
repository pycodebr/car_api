# Car API - Documentação

Bem-vindo à documentação completa da **Car API**, uma API REST moderna para gerenciamento de carros e usuários, desenvolvida com FastAPI, SQLAlchemy e PostgreSQL/SQLite.

## 🚗 Sobre o Projeto

A Car API é um sistema completo que permite:

- **Gestão de Usuários**: Registro, autenticação e gerenciamento de perfis
- **Gestão de Carros**: CRUD completo com informações detalhadas dos veículos
- **Gestão de Marcas**: Cadastro e manutenção de marcas de veículos
- **Autenticação JWT**: Sistema seguro de autenticação baseado em tokens
- **API RESTful**: Endpoints bem estruturados seguindo padrões REST

## 📚 Estrutura da Documentação

### 🎯 Primeiros Passos
- [Visão Geral](overview.md) - Entenda o projeto e suas funcionalidades
- [Pré-requisitos](prerequisites.md) - O que você precisa para começar
- [Instalação](installation.md) - Como configurar o ambiente
- [Configuração](configuration.md) - Configurações do projeto

### 🏗️ Desenvolvimento
- [Guidelines e Padrões](guidelines.md) - Padrões de código e desenvolvimento
- [Estrutura do Projeto](structure.md) - Organização de arquivos e diretórios
- [API Endpoints](api-endpoints.md) - Documentação completa da API

### 🏛️ Arquitetura
- [Modelagem do Sistema](system-modeling.md) - Diagramas e modelos do sistema
- [Autenticação e Segurança](authentication.md) - Como funciona a segurança

### 🛠️ Operações
- [Desenvolvimento](development.md) - Fluxo de desenvolvimento
- [Testes](testing.md) - Como executar e escrever testes
- [Deploy](deployment.md) - Como fazer deploy da aplicação

### 📝 Colaboração
- [Contribuição](contributing.md) - Como contribuir com o projeto
- [Release Notes](release-notes.md) - Histórico de versões

## 🚀 Quick Start

Para começar rapidamente:

```bash
# Clone o repositório
git clone https://github.com/pycodebr/car_api.git
cd car_api

# Instale as dependências
poetry install

# Configure o banco de dados
poetry run alembic upgrade head

# Execute a aplicação
poetry run task run
```

A API estará disponível em `http://localhost:8000` e a documentação interativa em `http://localhost:8000/docs`.

## 🔗 Links Úteis

- **API Docs (Swagger)**: `http://localhost:8000/docs`
- **API Docs (ReDoc)**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health_check`

## 🏷️ Versão

**Versão atual**: 0.1.0

## 📞 Suporte

Para dúvidas, problemas ou sugestões:
- **Email**: pycodebr@gmail.com
- **GitHub Issues**: [Reportar problemas](https://github.com/pycodebr/car_api/issues)

---

*Documentação gerada automaticamente para o projeto Car API*