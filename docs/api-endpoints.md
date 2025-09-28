# API Endpoints

## 🌐 Visão Geral da API

A Car API expõe endpoints RESTful organizados por funcionalidade. Todos os endpoints seguem padrões consistentes de nomenclatura, códigos de status HTTP e estruturas de resposta.

### 🔗 Base URL
```
http://localhost:8000/api/v1
```

### 📚 Documentação Interativa
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## 🔑 Autenticação

### Gerar Token de Acesso

**POST** `/auth/token`

Autentica um usuário e retorna um token JWT.

#### Request Body
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

#### Response (200)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Response (401)
```json
{
  "detail": "Incorrect email or password"
}
```

#### cURL Example
```bash
curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### Renovar Token

**POST** `/auth/refresh_token`

Gera um novo token para o usuário autenticado.

#### Headers
```
Authorization: Bearer <access_token>
```

#### Response (200)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## 👤 Usuários

### Criar Usuário

**POST** `/users/`

Registra um novo usuário no sistema.

#### Request Body
```json
{
  "username": "joao_silva",
  "email": "joao@example.com",
  "password": "senha_segura123"
}
```

#### Response (201)
```json
{
  "id": 1,
  "username": "joao_silva",
  "email": "joao@example.com",
  "created_at": "2023-12-01T10:00:00Z",
  "updated_at": "2023-12-01T10:00:00Z"
}
```

#### Response (400)
```json
{
  "detail": "Email já está em uso"
}
```

### Listar Usuários

**GET** `/users/`

Lista usuários com paginação e busca.

#### Query Parameters
| Parâmetro | Tipo | Obrigatório | Padrão | Descrição |
|-----------|------|-------------|--------|-----------|
| `offset` | int | Não | 0 | Registros para pular |
| `limit` | int | Não | 100 | Limite de registros (máx: 100) |
| `search` | string | Não | - | Buscar por username ou email |

#### Response (200)
```json
{
  "users": [
    {
      "id": 1,
      "username": "joao_silva",
      "email": "joao@example.com",
      "created_at": "2023-12-01T10:00:00Z",
      "updated_at": "2023-12-01T10:00:00Z"
    }
  ],
  "offset": 0,
  "limit": 100
}
```

#### cURL Example
```bash
curl -X GET "http://localhost:8000/api/v1/users/?search=joao&limit=10"
```

### Buscar Usuário por ID

**GET** `/users/{user_id}`

Retorna detalhes de um usuário específico.

#### Path Parameters
- `user_id` (int): ID do usuário

#### Response (200)
```json
{
  "id": 1,
  "username": "joao_silva",
  "email": "joao@example.com",
  "created_at": "2023-12-01T10:00:00Z",
  "updated_at": "2023-12-01T10:00:00Z"
}
```

#### Response (404)
```json
{
  "detail": "Usuário não encontrado"
}
```

### Atualizar Usuário

**PUT** `/users/{user_id}`

Atualiza dados de um usuário. Requer autenticação.

#### Headers
```
Authorization: Bearer <access_token>
```

#### Request Body (Todos os campos são opcionais)
```json
{
  "username": "novo_username",
  "email": "novo@example.com",
  "password": "nova_senha123"
}
```

#### Response (200)
```json
{
  "id": 1,
  "username": "novo_username",
  "email": "novo@example.com",
  "created_at": "2023-12-01T10:00:00Z",
  "updated_at": "2023-12-01T12:00:00Z"
}
```

### Deletar Usuário

**DELETE** `/users/{user_id}`

Remove um usuário do sistema. Requer autenticação.

#### Headers
```
Authorization: Bearer <access_token>
```

#### Response (204)
```
No Content
```

## 🏷️ Marcas

### Criar Marca

**POST** `/brands/`

Cria uma nova marca de veículo. Requer autenticação.

#### Headers
```
Authorization: Bearer <access_token>
```

#### Request Body
```json
{
  "name": "Toyota",
  "description": "Marca japonesa conhecida pela confiabilidade",
  "is_active": true
}
```

#### Response (201)
```json
{
  "id": 1,
  "name": "Toyota",
  "description": "Marca japonesa conhecida pela confiabilidade",
  "is_active": true,
  "created_at": "2023-12-01T10:00:00Z",
  "updated_at": "2023-12-01T10:00:00Z"
}
```

#### Response (400)
```json
{
  "detail": "Nome da marca já está em uso"
}
```

### Listar Marcas

**GET** `/brands/`

Lista marcas com filtros. Requer autenticação.

#### Headers
```
Authorization: Bearer <access_token>
```

#### Query Parameters
| Parâmetro | Tipo | Obrigatório | Padrão | Descrição |
|-----------|------|-------------|--------|-----------|
| `offset` | int | Não | 0 | Registros para pular |
| `limit` | int | Não | 100 | Limite de registros |
| `search` | string | Não | - | Buscar por nome da marca |
| `is_active` | boolean | Não | - | Filtrar por marcas ativas |

#### Response (200)
```json
{
  "brands": [
    {
      "id": 1,
      "name": "Toyota",
      "description": "Marca japonesa conhecida pela confiabilidade",
      "is_active": true,
      "created_at": "2023-12-01T10:00:00Z",
      "updated_at": "2023-12-01T10:00:00Z"
    }
  ],
  "offset": 0,
  "limit": 100
}
```

### Buscar Marca por ID

**GET** `/brands/{brand_id}`

Retorna detalhes de uma marca específica. Requer autenticação.

#### Headers
```
Authorization: Bearer <access_token>
```

#### Response (200)
```json
{
  "id": 1,
  "name": "Toyota",
  "description": "Marca japonesa conhecida pela confiabilidade",
  "is_active": true,
  "created_at": "2023-12-01T10:00:00Z",
  "updated_at": "2023-12-01T10:00:00Z"
}
```

### Atualizar Marca

**PUT** `/brands/{brand_id}`

Atualiza dados de uma marca. Requer autenticação.

#### Headers
```
Authorization: Bearer <access_token>
```

#### Request Body (Todos os campos são opcionais)
```json
{
  "name": "Toyota Motors",
  "description": "Marca japonesa líder mundial",
  "is_active": false
}
```

### Deletar Marca

**DELETE** `/brands/{brand_id}`

Remove uma marca do sistema. Requer autenticação.
**Nota**: Não é possível deletar marcas que possuem carros associados.

#### Headers
```
Authorization: Bearer <access_token>
```

#### Response (204)
```
No Content
```

#### Response (400)
```json
{
  "detail": "Não é possível deletar marca que possui carros associados"
}
```

## 🚗 Carros

### Criar Carro

**POST** `/cars/`

Registra um novo carro no sistema. Requer autenticação.

#### Headers
```
Authorization: Bearer <access_token>
```

#### Request Body
```json
{
  "model": "Corolla",
  "factory_year": 2022,
  "model_year": 2023,
  "color": "Prata",
  "plate": "ABC1234",
  "fuel_type": "flex",
  "transmission": "automatic",
  "price": "85000.00",
  "description": "Sedan econômico e confiável",
  "is_available": true,
  "brand_id": 1
}
```

#### Enums Válidos

**Fuel Type:**
- `gasoline` - Gasolina
- `ethanol` - Etanol
- `flex` - Flex
- `diesel` - Diesel
- `electric` - Elétrico
- `hybrid` - Híbrido

**Transmission Type:**
- `manual` - Manual
- `automatic` - Automático
- `semi_automatic` - Semi-automático
- `cvt` - CVT

#### Response (201)
```json
{
  "id": 1,
  "model": "Corolla",
  "factory_year": 2022,
  "model_year": 2023,
  "color": "Prata",
  "plate": "ABC1234",
  "fuel_type": "flex",
  "transmission": "automatic",
  "price": "85000.00",
  "description": "Sedan econômico e confiável",
  "is_available": true,
  "created_at": "2023-12-01T10:00:00Z",
  "updated_at": "2023-12-01T10:00:00Z",
  "brand": {
    "id": 1,
    "name": "Toyota",
    "description": "Marca japonesa conhecida pela confiabilidade",
    "is_active": true
  },
  "owner": {
    "id": 1,
    "username": "joao_silva",
    "email": "joao@example.com"
  }
}
```

#### Response (400)
```json
{
  "detail": "Placa já está em uso"
}
```

### Listar Carros

**GET** `/cars/`

Lista carros do usuário autenticado com filtros avançados.

#### Headers
```
Authorization: Bearer <access_token>
```

#### Query Parameters
| Parâmetro | Tipo | Obrigatório | Padrão | Descrição |
|-----------|------|-------------|--------|-----------|
| `offset` | int | Não | 0 | Registros para pular |
| `limit` | int | Não | 100 | Limite de registros |
| `search` | string | Não | - | Buscar por modelo ou placa |
| `brand_id` | int | Não | - | Filtrar por marca |
| `fuel_type` | string | Não | - | Filtrar por combustível |
| `transmission` | string | Não | - | Filtrar por transmissão |
| `is_available` | boolean | Não | - | Filtrar por disponibilidade |
| `min_price` | float | Não | - | Preço mínimo |
| `max_price` | float | Não | - | Preço máximo |

#### Response (200)
```json
{
  "cars": [
    {
      "id": 1,
      "model": "Corolla",
      "factory_year": 2022,
      "model_year": 2023,
      "color": "Prata",
      "plate": "ABC1234",
      "fuel_type": "flex",
      "transmission": "automatic",
      "price": "85000.00",
      "description": "Sedan econômico e confiável",
      "is_available": true,
      "created_at": "2023-12-01T10:00:00Z",
      "updated_at": "2023-12-01T10:00:00Z",
      "brand": {
        "id": 1,
        "name": "Toyota"
      },
      "owner": {
        "id": 1,
        "username": "joao_silva"
      }
    }
  ],
  "offset": 0,
  "limit": 100
}
```

#### cURL Example
```bash
curl -X GET "http://localhost:8000/api/v1/cars/?fuel_type=flex&min_price=50000&max_price=100000" \
  -H "Authorization: Bearer <access_token>"
```

### Buscar Carro por ID

**GET** `/cars/{car_id}`

Retorna detalhes de um carro específico. Requer autenticação e propriedade.

#### Headers
```
Authorization: Bearer <access_token>
```

#### Response (200)
```json
{
  "id": 1,
  "model": "Corolla",
  "factory_year": 2022,
  "model_year": 2023,
  "color": "Prata",
  "plate": "ABC1234",
  "fuel_type": "flex",
  "transmission": "automatic",
  "price": "85000.00",
  "description": "Sedan econômico e confiável",
  "is_available": true,
  "created_at": "2023-12-01T10:00:00Z",
  "updated_at": "2023-12-01T10:00:00Z",
  "brand": {
    "id": 1,
    "name": "Toyota",
    "description": "Marca japonesa conhecida pela confiabilidade",
    "is_active": true
  },
  "owner": {
    "id": 1,
    "username": "joao_silva",
    "email": "joao@example.com"
  }
}
```

#### Response (403)
```json
{
  "detail": "Acesso negado"
}
```

### Atualizar Carro

**PUT** `/cars/{car_id}`

Atualiza dados de um carro. Requer autenticação e propriedade.

#### Headers
```
Authorization: Bearer <access_token>
```

#### Request Body (Todos os campos são opcionais)
```json
{
  "model": "Corolla XEi",
  "price": "88000.00",
  "description": "Sedan econômico e confiável - versão XEi",
  "is_available": false
}
```

#### Response (200)
```json
{
  "id": 1,
  "model": "Corolla XEi",
  "factory_year": 2022,
  "model_year": 2023,
  "color": "Prata",
  "plate": "ABC1234",
  "fuel_type": "flex",
  "transmission": "automatic",
  "price": "88000.00",
  "description": "Sedan econômico e confiável - versão XEi",
  "is_available": false,
  "created_at": "2023-12-01T10:00:00Z",
  "updated_at": "2023-12-01T12:00:00Z",
  "brand": {
    "id": 1,
    "name": "Toyota"
  },
  "owner": {
    "id": 1,
    "username": "joao_silva"
  }
}
```

### Deletar Carro

**DELETE** `/cars/{car_id}`

Remove um carro do sistema. Requer autenticação e propriedade.

#### Headers
```
Authorization: Bearer <access_token>
```

#### Response (204)
```
No Content
```

## 🏥 Health Check

### Verificar Status da API

**GET** `/health_check`

Endpoint público para verificar se a API está funcionando.

#### Response (200)
```json
{
  "status": "ok"
}
```

## 📊 Códigos de Status HTTP

### Códigos de Sucesso
- **200 OK**: Operação bem-sucedida
- **201 Created**: Recurso criado com sucesso
- **204 No Content**: Recurso deletado com sucesso

### Códigos de Erro do Cliente
- **400 Bad Request**: Dados inválidos ou regra de negócio violada
- **401 Unauthorized**: Token inválido ou ausente
- **403 Forbidden**: Acesso negado (sem permissão)
- **404 Not Found**: Recurso não encontrado
- **422 Unprocessable Entity**: Erro de validação de dados

### Códigos de Erro do Servidor
- **500 Internal Server Error**: Erro interno do servidor

## 🔒 Segurança

### Autenticação JWT

Todos os endpoints protegidos requerem um token JWT válido no header:

```
Authorization: Bearer <access_token>
```

### Validação de Propriedade

Usuários só podem acessar/modificar seus próprios carros:

```python
def verify_car_ownership(current_user: User, car_owner_id: int):
    if current_user.id != car_owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Acesso negado'
        )
```

### Rate Limiting

⚠️ **Planejado para implementação futura**:
- Limite de 100 requests por minuto por usuário
- Limite de 1000 requests por hora por IP

## 📝 Exemplos de Uso

### Fluxo Completo: Registrar Usuário e Criar Carro

```bash
# 1. Registrar usuário
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "maria_silva",
    "email": "maria@example.com",
    "password": "senha123"
  }'

# 2. Fazer login
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "maria@example.com",
    "password": "senha123"
  }' | jq -r '.access_token')

# 3. Criar marca
curl -X POST "http://localhost:8000/api/v1/brands/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Honda",
    "description": "Marca japonesa inovadora",
    "is_active": true
  }'

# 4. Criar carro
curl -X POST "http://localhost:8000/api/v1/cars/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Civic",
    "factory_year": 2023,
    "model_year": 2023,
    "color": "Branco",
    "plate": "XYZ9876",
    "fuel_type": "flex",
    "transmission": "manual",
    "price": "95000.00",
    "description": "Sedan esportivo",
    "is_available": true,
    "brand_id": 2
  }'

# 5. Listar carros
curl -X GET "http://localhost:8000/api/v1/cars/" \
  -H "Authorization: Bearer $TOKEN"
```

### Busca Avançada de Carros

```bash
# Buscar carros Honda automáticos entre R$ 80.000 e R$ 120.000
curl -X GET "http://localhost:8000/api/v1/cars/?brand_id=2&transmission=automatic&min_price=80000&max_price=120000" \
  -H "Authorization: Bearer $TOKEN"

# Buscar carros por modelo
curl -X GET "http://localhost:8000/api/v1/cars/?search=civic" \
  -H "Authorization: Bearer $TOKEN"

# Buscar carros elétricos disponíveis
curl -X GET "http://localhost:8000/api/v1/cars/?fuel_type=electric&is_available=true" \
  -H "Authorization: Bearer $TOKEN"
```

## 🧪 Testes da API

### Executar Testes

```bash
# Todos os testes
poetry run task test

# Testes específicos
poetry run pytest tests/test_cars.py -v
poetry run pytest tests/test_auth.py::test_login_success -v
```

### Testar com HTTPie

```bash
# Instalar HTTPie
pip install httpie

# Registrar usuário
http POST localhost:8000/api/v1/users/ \
  username=test_user \
  email=test@example.com \
  password=test123

# Fazer login
http POST localhost:8000/api/v1/auth/token \
  email=test@example.com \
  password=test123
```

## 📚 Próximos Passos

Para explorar mais:

1. 🏗️ Entenda a [Modelagem do Sistema](system-modeling.md)
2. 🔐 Saiba mais sobre [Autenticação e Segurança](authentication.md)
3. 🧪 Aprenda sobre [Testes](testing.md)
4. 💻 Comece o [Desenvolvimento](development.md)