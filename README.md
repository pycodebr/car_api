# Car API Project Documentation

## Overview

Este projeto é uma API CRUD para gerenciamento de carros, construída com FastAPI, SQLAlchemy, Pydantic e SQLite. Utiliza Alembic para migrações de banco de dados e Ruff para linting e formatação de código.

## Pré-requisitos

* Python 3.13 ou superior
* pip
* SQLite
* Git (opcional)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/pycodebr/car_api
cd car_api
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv .venv
source .venv/bin/activate  # Unix/macOS
.venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Linting & Formatação

Use o Ruff para verificar e corrigir o estilo do código:

* Verificar lint:
```bash
ruff check
```

* Auto-fix:
```bash
ruff check --fix
```   

* Formatar código (equivalente ao auto-fix):
```bash
ruff format
```

## Migrações de Banco de Dados com Alembic

1. Gere uma nova migration caso altere os models:
```bash
alembic revision --autogenerate -m "create cars table"
```

2. Aplique as migrações:
```bash
alembic upgrade head
```

## Executando a Aplicação

Inicie o servidor de desenvolvimento do FastAPI:
```bash
uvicorn car_api.app:app --reload
```

Ou usando a CLI do FastAPI:
```bash
fastapi dev car_api/app.py
```

Por padrão, a API estará disponível em `http://127.0.0.1:8000`.

## Endpoints da API

* `POST /cars/`: Cria um novo carro
* `GET /cars/`: Lista carros (suporta query params `skip` e `limit`)
* `GET /cars/{id}`: Busca um carro pelo ID
* `PUT /cars/{id}`: Atualiza todos os campos de um carro
* `PATCH /cars/{id}`: Atualização parcial de um carro
* `DELETE /cars/{id}`: Remove um carro

## Servindo Documentação com MkDocs

1. Para iniciar o servidor de documentação local:
```bash
mkdocs serve -a 127.0.0.1:8001
```

2. Abra `http://127.0.0.1:8001` no navegador para visualizar a documentação.

## Testes

Execute a suíte de testes com cobertura usando:
```bash
pytest --cov=car_api --cov-report=term --cov-report=html
```
O relatório HTML será gerado na pasta `htmlcov`.
