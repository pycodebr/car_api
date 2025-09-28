# Visão Geral do Projeto

## 🎯 Propósito

A **Car API** é uma aplicação web RESTful moderna desenvolvida para gerenciar um sistema de carros e usuários. O projeto demonstra as melhores práticas de desenvolvimento usando tecnologias Python modernas, incluindo FastAPI, SQLAlchemy 2.0 e autenticação JWT.

## ✨ Principais Funcionalidades

### 👥 Gestão de Usuários
- **Registro de usuários** com validação de dados
- **Autenticação segura** com JWT (JSON Web Tokens)
- **Gerenciamento de perfis** de usuários
- **Refresh de tokens** para sessões prolongadas

### 🚗 Gestão de Carros
- **CRUD completo** para veículos
- **Informações detalhadas**: modelo, ano de fabricação, ano do modelo, cor, combustível, transmissão
- **Gestão de preços** com precisão decimal
- **Controle de disponibilidade** dos veículos
- **Associação com proprietários** (usuários)

### 🏷️ Gestão de Marcas
- **Cadastro de marcas** de veículos
- **Controle de ativação/desativação** de marcas
- **Descrições detalhadas** das marcas
- **Relacionamento com carros**

### 🔐 Segurança
- **Autenticação JWT** com tokens seguros
- **Hash de senhas** usando Argon2
- **Proteção de rotas** com middleware de autenticação
- **Validação rigorosa** de dados de entrada

## 🏗️ Arquitetura do Sistema

### Padrão Arquitetural
O projeto segue uma **arquitetura em camadas** bem definida:

```
┌─────────────────┐
│   API Layer     │  ← FastAPI Routers
├─────────────────┤
│ Business Logic  │  ← Service Layer (implícito nos routers)
├─────────────────┤
│   Data Access   │  ← SQLAlchemy Models
├─────────────────┤
│   Database      │  ← PostgreSQL/SQLite
└─────────────────┘
```

### Principais Componentes

1. **FastAPI Application** (`app.py`)
   - Ponto de entrada da aplicação
   - Configuração de routers e middleware

2. **Core Modules** (`core/`)
   - **Database**: Configuração e sessões do banco
   - **Security**: Funções de autenticação e autorização
   - **Settings**: Configurações da aplicação

3. **Models** (`models/`)
   - **User**: Modelo de usuários
   - **Car**: Modelo de carros com relacionamentos
   - **Base**: Classe base para todos os modelos

4. **Schemas** (`schemas/`)
   - **Pydantic models** para validação de entrada e saída
   - **DTOs** (Data Transfer Objects) da API

5. **Routers** (`routers/`)
   - **Auth**: Endpoints de autenticação
   - **Users**: CRUD de usuários
   - **Cars**: CRUD de carros
   - **Brands**: CRUD de marcas

## 🛠️ Stack Tecnológica

### Backend Framework
- **FastAPI**: Framework web moderno e rápido
- **Python 3.13+**: Linguagem de programação

### Banco de Dados
- **SQLAlchemy 2.0**: ORM moderno com suporte async
- **PostgreSQL**: Banco principal (produção)
- **SQLite**: Banco para desenvolvimento
- **Alembic**: Migrações de banco de dados

### Autenticação & Segurança
- **PyJWT**: Tokens JWT
- **PWDLib[argon2]**: Hash seguro de senhas
- **Pydantic**: Validação de dados

### Desenvolvimento
- **Poetry**: Gerenciamento de dependências
- **Pytest**: Framework de testes
- **Ruff**: Linter e formatador
- **Taskipy**: Automação de tarefas

### DevOps
- **Docker**: Containerização
- **Docker Compose**: Orquestração de containers
- **MkDocs**: Documentação

## 🌟 Diferenciais do Projeto

### Código Moderno
- **Type Hints** completos em todo o código
- **Async/Await** para operações I/O
- **SQLAlchemy 2.0** com mapped columns
- **Pydantic V2** para validação

### Boas Práticas
- **Separação de responsabilidades** clara
- **Injeção de dependências** com FastAPI
- **Tratamento de erros** consistente
- **Documentação automática** com OpenAPI

### Qualidade de Código
- **Testes automatizados** com alta cobertura
- **Linting automático** com Ruff
- **Formatação consistente** de código
- **CI/CD ready** com tasks automatizadas

## 🎯 Casos de Uso

### Para Desenvolvedores
- **Template de projeto** FastAPI moderno
- **Referência de boas práticas** Python
- **Exemplo de autenticação JWT**
- **Estrutura de projeto escalável**

### Para Aprendizado
- **API REST completa** com CRUD
- **Relacionamentos de banco** complexos
- **Autenticação e autorização**
- **Testes automatizados**

### Para Produção
- **Sistema de gestão** de frotas
- **Base para marketplace** de carros
- **API para aplicativos móveis**
- **Microserviço de veículos**

## 📊 Métricas do Projeto

- **Linguagem**: Python 3.13+
- **Framework**: FastAPI
- **Linhas de código**: ~1000+ linhas
- **Cobertura de testes**: 90%+
- **Dependências**: 15+ bibliotecas
- **Endpoints**: 15+ rotas API