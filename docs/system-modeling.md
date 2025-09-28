# Modelagem do Sistema

## 🏗️ Visão Geral Arquitetural

Este documento apresenta a modelagem completa do sistema Car API, incluindo diagramas de dados, arquitetura, fluxos de autenticação e operações CRUD.

## 📊 Modelo de Dados (ERD)

### Diagrama Entidade-Relacionamento

```mermaid
erDiagram
    USERS {
        int id PK
        string username UK
        string email UK
        string password
        datetime created_at
        datetime updated_at
    }

    BRANDS {
        int id PK
        string name UK
        text description
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    CARS {
        int id PK
        string model
        int factory_year
        int model_year
        string color
        string plate UK
        string fuel_type
        string transmission
        decimal price
        text description
        boolean is_available
        int brand_id FK
        int owner_id FK
        datetime created_at
        datetime updated_at
    }

    USERS ||--o{ CARS : "owns"
    BRANDS ||--o{ CARS : "belongs_to"
```

### Descrição das Entidades

#### 👤 USERS (Usuários)
- **Propósito**: Armazenar informações dos usuários do sistema
- **Características**:
  - Cada usuário pode ter múltiplos carros
  - Username e email são únicos
  - Senha armazenada com hash Argon2
  - Timestamps de auditoria

#### 🏷️ BRANDS (Marcas)
- **Propósito**: Catálogo de marcas de veículos
- **Características**:
  - Nome único no sistema
  - Controle de ativação/desativação
  - Descrição opcional
  - Uma marca pode ter múltiplos carros

#### 🚗 CARS (Carros)
- **Propósito**: Registro de veículos no sistema
- **Características**:
  - Placa única no sistema
  - Relacionamento com marca e proprietário
  - Informações técnicas detalhadas
  - Controle de disponibilidade
  - Preço com precisão decimal

### Relacionamentos

1. **USERS → CARS** (1:N)
   - Um usuário pode possuir múltiplos carros
   - Um carro pertence a apenas um usuário
   - Relacionamento obrigatório (owner_id NOT NULL)

2. **BRANDS → CARS** (1:N)
   - Uma marca pode ter múltiplos carros
   - Um carro pertence a apenas uma marca
   - Relacionamento obrigatório (brand_id NOT NULL)

### Constraints e Validações

```sql
-- Constraints de unicidade
UNIQUE(users.username)
UNIQUE(users.email)
UNIQUE(brands.name)
UNIQUE(cars.plate)

-- Constraints de integridade referencial
FOREIGN KEY(cars.owner_id) REFERENCES users(id)
FOREIGN KEY(cars.brand_id) REFERENCES brands(id)

-- Constraints de validação
CHECK(cars.factory_year >= 1900 AND cars.factory_year <= 2030)
CHECK(cars.model_year >= 1900 AND cars.model_year <= 2030)
CHECK(cars.price > 0)
CHECK(cars.fuel_type IN ('gasoline', 'ethanol', 'flex', 'diesel', 'electric', 'hybrid'))
CHECK(cars.transmission IN ('manual', 'automatic', 'semi_automatic', 'cvt'))
```

## 🏛️ Arquitetura do Sistema

### Diagrama de Arquitetura

```mermaid
graph TB
    subgraph "Cliente"
        CLI[Cliente HTTP]
        UI[Interface Web]
        MOB[App Mobile]
    end

    subgraph "API Layer"
        GW[API Gateway]
        LB[Load Balancer]
    end

    subgraph "FastAPI Application"
        RT[Routers]
        MW[Middleware]
        DI[Dependency Injection]
    end

    subgraph "Business Layer"
        AUTH[Auth Service]
        USER[User Service]
        CAR[Car Service]
        BRAND[Brand Service]
    end

    subgraph "Data Layer"
        ORM[SQLAlchemy ORM]
        CACHE[Redis Cache]
        DB[(PostgreSQL)]
    end

    subgraph "External Services"
        JWT[JWT Provider]
        LOG[Logging]
        MON[Monitoring]
    end

    CLI --> GW
    UI --> GW
    MOB --> GW

    GW --> LB
    LB --> RT

    RT --> MW
    MW --> DI
    DI --> AUTH
    DI --> USER
    DI --> CAR
    DI --> BRAND

    AUTH --> ORM
    USER --> ORM
    CAR --> ORM
    BRAND --> ORM

    ORM --> CACHE
    ORM --> DB

    AUTH --> JWT
    RT --> LOG
    MW --> MON

    style CLI fill:#e1f5fe
    style UI fill:#e1f5fe
    style MOB fill:#e1f5fe
    style RT fill:#f3e5f5
    style DB fill:#e8f5e8
    style CACHE fill:#fff3e0
```

### Camadas da Arquitetura

#### 1. **Cliente Layer**
- **Responsabilidade**: Interface com usuário
- **Componentes**: CLI, Web UI, Mobile App
- **Protocolos**: HTTP/HTTPS, REST

#### 2. **API Layer**
- **Responsabilidade**: Gerenciamento de tráfego
- **Componentes**: API Gateway, Load Balancer
- **Funcionalidades**: Rate limiting, CORS, SSL

#### 3. **Application Layer**
- **Responsabilidade**: Lógica de apresentação
- **Componentes**: FastAPI Routers, Middleware
- **Funcionalidades**: Roteamento, validação, serialização

#### 4. **Business Layer**
- **Responsabilidade**: Regras de negócio
- **Componentes**: Services (implícitos nos routers)
- **Funcionalidades**: Autenticação, CRUD, validações

#### 5. **Data Layer**
- **Responsabilidade**: Persistência de dados
- **Componentes**: SQLAlchemy ORM, PostgreSQL
- **Funcionalidades**: Transações, relacionamentos, cache

## 🔑 Fluxo de Autenticação

### Diagrama de Autenticação JWT

```mermaid
sequenceDiagram
    participant C as Cliente
    participant A as API
    participant JWT as JWT Service
    participant DB as Database

    C->>A: POST /auth/token (username, password)
    A->>DB: Validar credenciais
    DB-->>A: Usuário válido
    A->>JWT: Gerar token
    JWT-->>A: Access token
    A-->>C: {access_token, token_type}

    Note over C: Cliente armazena token

    C->>A: GET /users/ (Authorization: Bearer token)
    A->>JWT: Validar token
    JWT-->>A: Token válido + user_id
    A->>DB: Buscar dados do usuário
    DB-->>A: Dados do usuário
    A-->>C: Lista de usuários
```

### Componentes de Segurança

#### 1. **Password Hashing**
```python
from pwdlib import PasswordHash

pwd_context = PasswordHash.recommended()

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

#### 2. **JWT Token Management**
```python
import jwt
from datetime import datetime, timedelta

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
```

#### 3. **Authorization Middleware**
```python
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user_by_id(user_id)
    if user is None:
        raise credentials_exception

    return user
```

## 🚗 Fluxo CRUD de Carros

### Diagrama de Operações CRUD

```mermaid
flowchart TD
    Start([Início]) --> Auth{Token válido?}
    Auth -->|Não| Unauthorized[401 Unauthorized]
    Auth -->|Sim| Operation{Tipo de operação?}

    Operation -->|CREATE| ValidateData[Validar dados do carro]
    ValidateData --> CheckBrand{Marca existe?}
    CheckBrand -->|Não| CreateBrand[Criar nova marca]
    CheckBrand -->|Sim| CheckPlate{Placa única?}
    CreateBrand --> CheckPlate
    CheckPlate -->|Não| ConflictError[409 Conflict]
    CheckPlate -->|Sim| CreateCar[Criar carro]
    CreateCar --> ReturnCar[Retornar carro criado]

    Operation -->|READ| GetCars[Buscar carros]
    GetCars --> FilterOwner{Filtrar por proprietário?}
    FilterOwner -->|Sim| UserCars[Carros do usuário]
    FilterOwner -->|Não| AllCars[Todos os carros]
    UserCars --> ReturnCars[Retornar lista]
    AllCars --> ReturnCars

    Operation -->|UPDATE| FindCar[Buscar carro por ID]
    FindCar --> CarExists{Carro existe?}
    CarExists -->|Não| NotFound[404 Not Found]
    CarExists -->|Sim| CheckOwner{É o proprietário?}
    CheckOwner -->|Não| Forbidden[403 Forbidden]
    CheckOwner -->|Sim| UpdateCar[Atualizar carro]
    UpdateCar --> ReturnUpdated[Retornar carro atualizado]

    Operation -->|DELETE| FindCar2[Buscar carro por ID]
    FindCar2 --> CarExists2{Carro existe?}
    CarExists2 -->|Não| NotFound2[404 Not Found]
    CarExists2 -->|Sim| CheckOwner2{É o proprietário?}
    CheckOwner2 -->|Não| Forbidden2[403 Forbidden]
    CheckOwner2 -->|Sim| DeleteCar[Deletar carro]
    DeleteCar --> Success[204 No Content]

    style Start fill:#e8f5e8
    style Success fill:#e8f5e8
    style ReturnCar fill:#e8f5e8
    style ReturnCars fill:#e8f5e8
    style ReturnUpdated fill:#e8f5e8
    style Unauthorized fill:#ffe8e8
    style ConflictError fill:#ffe8e8
    style NotFound fill:#ffe8e8
    style NotFound2 fill:#ffe8e8
    style Forbidden fill:#ffe8e8
    style Forbidden2 fill:#ffe8e8
```

### Validações e Regras de Negócio

#### 1. **Validações de Criação**
```python
async def create_car(car: CarSchema, current_user: User, db: AsyncSession):
    # 1. Validar placa única
    plate_exists = await db.scalar(select(exists().where(Car.plate == car.plate)))
    if plate_exists:
        raise HTTPException(400, "Placa já está em uso")

    # 2. Validar marca existe
    brand_exists = await db.scalar(select(exists().where(Brand.id == car.brand_id)))
    if not brand_exists:
        raise HTTPException(400, "Marca não encontrada")

    # 3. Criar carro com proprietário
    db_car = Car(**car.dict(), owner_id=current_user.id)
```

#### 2. **Validações de Propriedade**
```python
def verify_car_ownership(current_user: User, car_owner_id: int):
    if current_user.id != car_owner_id:
        raise HTTPException(403, "Acesso negado")
```

#### 3. **Filtros de Busca**
```python
# Aplicar filtros dinamicamente
if search:
    query = query.where(
        (Car.model.ilike(f'%{search}%')) |
        (Car.plate.ilike(f'%{search}%'))
    )

if brand_id:
    query = query.where(Car.brand_id == brand_id)

if fuel_type:
    query = query.where(Car.fuel_type == fuel_type)

if min_price:
    query = query.where(Car.price >= min_price)
```

## 🛡️ Fluxo de Segurança

### Diagrama de Segurança Integrada

```mermaid
flowchart LR
    subgraph REQ_PROC ["Request Processing"]
        REQ[HTTP Request] --> CORS[CORS Middleware]
        CORS --> RATE[Rate Limiting]
        RATE --> AUTH[Authentication]
        AUTH --> AUTHZ[Authorization]
        AUTHZ --> VAL[Input Validation]
        VAL --> BIZ[Business Logic]
        BIZ --> RES[Response]
    end

    subgraph SEC_LAYERS ["Security Layers"]
        subgraph NET_SEC ["Network Security"]
            HTTPS[HTTPS/TLS]
            FIREWALL[Firewall]
        end

        subgraph APP_SEC ["Application Security"]
            JWT_SEC[JWT Validation]
            HASH[Password Hashing]
            SANIT[Input Sanitization]
        end

        subgraph DATA_SEC ["Data Security"]
            ENCRYPT[Database Encryption]
            BACKUP[Secure Backups]
            AUDIT[Audit Logs]
        end
    end

    subgraph THREAT_MIT ["Threat Mitigation"]
        DDOS[DDoS Protection]
        INJECTION[SQL Injection Prevention]
        XSS[XSS Protection]
        CSRF[CSRF Protection]
    end

    REQ --> HTTPS
    AUTH --> JWT_SEC
    VAL --> SANIT
    BIZ --> AUDIT

    style REQ fill:#ffebee
    style AUTH fill:#e8f5e8
    style VAL fill:#e3f2fd
    style RES fill:#f3e5f5
```

### Controles de Segurança Implementados

#### 1. **Autenticação Multi-Camada**
```python
# Layer 1: Token Validation
async def validate_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(401, "Token inválido")

# Layer 2: User Verification
async def get_current_user(payload: dict, db: AsyncSession) -> User:
    user = await db.get(User, payload["sub"])
    if not user:
        raise HTTPException(401, "Usuário não encontrado")
    return user

# Layer 3: Resource Authorization
def verify_resource_access(user: User, resource_owner_id: int):
    if user.id != resource_owner_id:
        raise HTTPException(403, "Acesso negado")
```

#### 2. **Validação de Entrada**
```python
# Schema Validation
class CarSchema(BaseModel):
    model: str = Field(..., min_length=1, max_length=100)
    factory_year: int = Field(..., ge=1900, le=2030)
    price: Decimal = Field(..., gt=0)
    plate: str = Field(..., regex=r'^[A-Z]{3}[0-9]{4}$|^[A-Z]{3}[0-9][A-Z][0-9]{2}$')

# SQL Injection Prevention (SQLAlchemy ORM)
query = select(Car).where(Car.plate == plate)  # Parameterized query
```

#### 3. **Rate Limiting e CORS**
```python
# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Rate Limiting (Planned)
@limits(calls=100, period=60)  # 100 calls per minute
async def rate_limited_endpoint():
    pass
```

## 📊 Métricas e Monitoramento

### Diagrama de Observabilidade

```mermaid
graph LR
    subgraph "Application"
        APP[FastAPI App]
        LOGS[Application Logs]
        METRICS[Business Metrics]
    end

    subgraph "Monitoring Stack"
        PROM[Prometheus]
        GRAF[Grafana]
        ALERT[AlertManager]
    end

    subgraph "Logging Stack"
        ELASTIC[Elasticsearch]
        LOGSTASH[Logstash]
        KIBANA[Kibana]
    end

    subgraph "Tracing"
        JAEGER[Jaeger]
        TRACE[Distributed Tracing]
    end

    APP --> LOGS
    APP --> METRICS

    LOGS --> LOGSTASH
    LOGSTASH --> ELASTIC
    ELASTIC --> KIBANA

    METRICS --> PROM
    PROM --> GRAF
    PROM --> ALERT

    APP --> TRACE
    TRACE --> JAEGER

    style APP fill:#e8f5e8
    style PROM fill:#e3f2fd
    style ELASTIC fill:#fff3e0
    style JAEGER fill:#f3e5f5
```

### KPIs e Métricas

#### 1. **Métricas de Performance**
- Response time médio: < 200ms
- Throughput: requests/segundo
- Error rate: < 1%
- Uptime: > 99.9%

#### 2. **Métricas de Negócio**
- Usuários ativos
- Carros cadastrados
- Transações por hora
- Taxa de conversão

#### 3. **Métricas de Segurança**
- Tentativas de login falhadas
- Tokens expirados
- Acessos negados
- Anomalias de tráfego

## 🔄 Padrões de Integração

### Diagrama de Integrações

```mermaid
graph TB
    subgraph "Car API Core"
        API[FastAPI Application]
        DB[(PostgreSQL)]
        CACHE[(Redis)]
    end

    subgraph "External APIs"
        PAYMENT[Payment Gateway]
        MAPS[Maps Service]
        NOTIF[Notification Service]
        FILE[File Storage]
    end

    subgraph "Internal Services"
        USER_SVC[User Service]
        INVENTORY[Inventory Service]
        ANALYTICS[Analytics Service]
    end

    subgraph "Event System"
        QUEUE[Message Queue]
        EVENTS[Event Bus]
    end

    API <--> PAYMENT
    API <--> MAPS
    API <--> NOTIF
    API <--> FILE

    API --> QUEUE
    QUEUE --> USER_SVC
    QUEUE --> INVENTORY
    QUEUE --> ANALYTICS

    API --> EVENTS
    EVENTS --> CACHE
    EVENTS --> DB

    style API fill:#e8f5e8
    style QUEUE fill:#e3f2fd
    style EVENTS fill:#fff3e0
```

## 📈 Escalabilidade e Performance

### Estratégias de Escalabilidade

#### 1. **Horizontal Scaling**
```mermaid
graph TB
    LB[Load Balancer]

    subgraph "API Instances"
        API1[Car API - Instance 1]
        API2[Car API - Instance 2]
        API3[Car API - Instance 3]
    end

    subgraph "Database Cluster"
        MASTER[(PostgreSQL Master)]
        SLAVE1[(PostgreSQL Slave 1)]
        SLAVE2[(PostgreSQL Slave 2)]
    end

    CACHE[(Redis Cluster)]

    LB --> API1
    LB --> API2
    LB --> API3

    API1 --> MASTER
    API1 --> SLAVE1
    API2 --> MASTER
    API2 --> SLAVE2
    API3 --> MASTER
    API3 --> SLAVE1

    API1 --> CACHE
    API2 --> CACHE
    API3 --> CACHE
```

#### 2. **Caching Strategy**
```python
# Multi-level caching
@cache.memoize(timeout=300)  # 5 minutes
async def get_popular_cars():
    return await db.execute(
        select(Car).where(Car.is_available == True).limit(10)
    )

# Database query optimization
query = select(Car).options(
    selectinload(Car.brand),  # Eager loading
    selectinload(Car.owner)
).where(Car.owner_id == user_id)
```

## 🎯 Próximos Passos

Para explorar mais detalhes:

1. 🔐 [Autenticação e Segurança](authentication.md) - Implementação detalhada
2. 💻 [Desenvolvimento](development.md) - Fluxo de desenvolvimento
3. 🧪 [Testes](testing.md) - Estratégias de teste
4. 🚀 [Deploy](deployment.md) - Processo de implantação