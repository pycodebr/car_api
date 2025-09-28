# Autenticação e Segurança

## 🔐 Visão Geral da Segurança

A Car API implementa um sistema de segurança robusto baseado em **JWT (JSON Web Tokens)** com hash de senhas usando **Argon2**. O sistema garante autenticação segura, autorização granular e proteção contra as principais vulnerabilidades web.

## 🔑 Autenticação JWT

### Como Funciona

1. **Login**: Cliente envia email/senha
2. **Validação**: Servidor verifica credenciais
3. **Token**: Servidor gera JWT assinado
4. **Uso**: Cliente inclui token nas requisições
5. **Validação**: Servidor valida token a cada request

### Estrutura do Token JWT

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "1",
    "exp": 1640995200,
    "iat": 1640908800
  },
  "signature": "HMACSHA256(base64UrlEncode(header) + '.' + base64UrlEncode(payload), secret)"
}
```

### Configuração JWT

```python
# car_api/core/settings.py
class Settings(BaseSettings):
    jwt_secret_key: str  # Chave secreta (mín. 64 caracteres)
    jwt_algorithm: str = 'HS256'  # Algoritmo de assinatura
    jwt_expiration_minutes: int = 30  # Tempo de expiração
```

### Implementação da Autenticação

#### 1. Geração de Token

```python
# car_api/core/security.py
from datetime import datetime, timedelta
import jwt
from car_api.core.settings import Settings

settings = Settings()

def create_access_token(data: dict) -> str:
    """
    Criar token JWT com dados do usuário.

    Args:
        data: Dados para incluir no token (geralmente {'sub': user_id})

    Returns:
        str: Token JWT assinado
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)
    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
```

#### 2. Validação de Token

```python
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer
import jwt

oauth2_scheme = HTTPBearer()

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Extrair e validar usuário atual do token JWT.

    Args:
        token: Token JWT do header Authorization

    Returns:
        User: Usuário autenticado

    Raises:
        HTTPException: Se token inválido ou usuário não encontrado
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decodificar token
        payload = jwt.decode(
            token.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )

        # Extrair user ID
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise credentials_exception

    # Buscar usuário no banco
    async with get_session() as db:
        user = await db.get(User, int(user_id))
        if user is None:
            raise credentials_exception

    return user
```

### Endpoint de Login

```python
# car_api/routers/auth.py
@router.post('/token', response_model=Token)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_session)
):
    """
    Endpoint de autenticação - gerar token JWT.

    Args:
        login_data: Email e senha do usuário
        db: Sessão do banco de dados

    Returns:
        Token: Access token e tipo
    """
    # Autenticar usuário
    user = await authenticate_user(login_data.email, login_data.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect email or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    # Gerar token
    access_token = create_access_token(data={'sub': str(user.id)})

    return {
        'access_token': access_token,
        'token_type': 'bearer'
    }
```

## 🔒 Hash de Senhas

### PWDLib com Argon2

A API usa **PWDLib** com **Argon2** para hash seguro de senhas:

```python
# car_api/core/security.py
from pwdlib import PasswordHash

# Configuração recomendada para Argon2
pwd_context = PasswordHash.recommended()

def get_password_hash(password: str) -> str:
    """
    Gerar hash seguro da senha usando Argon2.

    Args:
        password: Senha em texto plano

    Returns:
        str: Hash da senha
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verificar se senha corresponde ao hash.

    Args:
        plain_password: Senha em texto plano
        hashed_password: Hash armazenado

    Returns:
        bool: True se senha correta
    """
    return pwd_context.verify(plain_password, hashed_password)
```

### Por que Argon2?

- **Resistente a ataques de força bruta**
- **Memory-hard**: Requer muita memória para calcular
- **Padrão recomendado** pela OWASP
- **Configuração adaptável** de custo computacional

## 🛡️ Autorização

### Verificação de Propriedade

```python
def verify_car_ownership(current_user: User, car_owner_id: int):
    """
    Verificar se usuário é proprietário do carro.

    Args:
        current_user: Usuário autenticado
        car_owner_id: ID do proprietário do carro

    Raises:
        HTTPException: Se usuário não é proprietário
    """
    if current_user.id != car_owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Acesso negado - você não é proprietário deste carro'
        )
```

### Decorador de Autorização

```python
from functools import wraps
from fastapi import HTTPException, status

def require_ownership(resource_field: str = 'owner_id'):
    """
    Decorador para verificar propriedade de recurso.

    Args:
        resource_field: Campo que contém o ID do proprietário
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            resource = kwargs.get('resource')

            if not current_user or not resource:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Authentication required'
                )

            owner_id = getattr(resource, resource_field)
            if current_user.id != owner_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='Access denied'
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Uso do decorador
@require_ownership('owner_id')
async def update_car(car: Car, current_user: User):
    # Lógica de atualização
    pass
```

## 🔐 Segurança de Endpoints

### Proteção de Rotas

```python
# Rota pública (sem autenticação)
@router.post('/users/', response_model=UserPublicSchema)
async def register_user(user: UserSchema, db: AsyncSession = Depends(get_session)):
    # Qualquer um pode registrar

# Rota protegida (requer autenticação)
@router.get('/cars/', response_model=CarListPublicSchema)
async def list_cars(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    # Apenas usuários autenticados

# Rota com autorização (requer ser proprietário)
@router.get('/cars/{car_id}', response_model=CarPublicSchema)
async def get_car(
    car_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    car = await db.get(Car, car_id)
    if not car:
        raise HTTPException(404, "Carro não encontrado")

    verify_car_ownership(current_user, car.owner_id)
    return car
```

### Middleware de Segurança

```python
# car_api/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()

# CORS - Controlar origens permitidas
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://app.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Trusted Host - Prevenir ataques Host Header
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
)
```

## 🚨 Tratamento de Erros de Segurança

### Respostas Padronizadas

```python
# Erro 401 - Não autenticado
{
    "detail": "Could not validate credentials"
}

# Erro 403 - Sem permissão
{
    "detail": "Acesso negado"
}

# Erro 422 - Dados inválidos
{
    "detail": [
        {
            "loc": ["body", "password"],
            "msg": "ensure this value has at least 8 characters",
            "type": "value_error.any_str.min_length"
        }
    ]
}
```

### Exception Handlers Customizados

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import jwt

app = FastAPI()

@app.exception_handler(jwt.ExpiredSignatureError)
async def expired_token_handler(request: Request, exc: jwt.ExpiredSignatureError):
    return JSONResponse(
        status_code=401,
        content={
            "detail": "Token has expired",
            "error_code": "TOKEN_EXPIRED"
        }
    )

@app.exception_handler(jwt.JWTError)
async def jwt_error_handler(request: Request, exc: jwt.JWTError):
    return JSONResponse(
        status_code=401,
        content={
            "detail": "Invalid token",
            "error_code": "INVALID_TOKEN"
        }
    )
```

## 🔍 Validação de Entrada

### Schemas Pydantic

```python
from pydantic import BaseModel, Field, validator
from typing import Optional
import re

class UserSchema(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        regex=r'^[a-zA-Z0-9_]+$'
    )
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=8)

    @validator('password')
    def password_strength(cls, v):
        """Validar força da senha."""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain digit')
        return v

class CarSchema(BaseModel):
    model: str = Field(..., min_length=1, max_length=100)
    factory_year: int = Field(..., ge=1900, le=2030)
    price: Decimal = Field(..., gt=0)
    plate: str = Field(
        ...,
        regex=r'^[A-Z]{3}[0-9]{4}$|^[A-Z]{3}[0-9][A-Z][0-9]{2}$'
    )

    @validator('plate')
    def validate_plate(cls, v):
        """Validar formato da placa brasileira."""
        v = v.upper().replace('-', '').replace(' ', '')

        # Formato antigo: ABC1234
        # Formato Mercosul: ABC1A23
        if not re.match(r'^[A-Z]{3}[0-9]{4}$|^[A-Z]{3}[0-9][A-Z][0-9]{2}$', v):
            raise ValueError('Invalid plate format')

        return v
```

### Sanitização de Dados

```python
import html
import bleach

def sanitize_input(text: str) -> str:
    """
    Sanitizar entrada de texto contra XSS.

    Args:
        text: Texto de entrada

    Returns:
        str: Texto sanitizado
    """
    # Escapar HTML
    text = html.escape(text)

    # Remover tags HTML perigosas
    allowed_tags = ['p', 'br', 'strong', 'em']
    text = bleach.clean(text, tags=allowed_tags, strip=True)

    return text

# Uso em schemas
class CarUpdateSchema(BaseModel):
    description: Optional[str] = None

    @validator('description', pre=True)
    def sanitize_description(cls, v):
        if v:
            return sanitize_input(v)
        return v
```

## 🔒 Prevenção de Vulnerabilidades

### SQL Injection

```python
# ✅ Correto - SQLAlchemy ORM com parâmetros
query = select(Car).where(Car.plate == plate_value)

# ✅ Correto - Query parametrizada
query = text("SELECT * FROM cars WHERE plate = :plate")
result = await db.execute(query, {"plate": plate_value})

# ❌ Incorreto - String concatenation (vulnerável)
query = f"SELECT * FROM cars WHERE plate = '{plate_value}'"
```

### NoSQL Injection

```python
# ✅ Correto - Validação de tipos
def get_car_by_id(car_id: int):  # Type hint garante int
    return db.get(Car, car_id)

# ❌ Incorreto - Aceitar qualquer tipo
def get_car_by_id(car_id):  # Poderia receber dict malicioso
    return db.get(Car, car_id)
```

### CSRF Protection

```python
from fastapi_csrf_protect import CsrfProtect

@CsrfProtect.validate_csrf
@router.post('/cars/')
async def create_car(car: CarSchema, csrf_protect: CsrfProtect = Depends()):
    # Endpoint protegido contra CSRF
    pass
```

### Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post('/auth/token')
@limiter.limit("5/minute")  # Máximo 5 tentativas de login por minuto
async def login(request: Request, login_data: LoginRequest):
    # Lógica de login
    pass
```

## 🔐 Configuração de Produção

### Variáveis de Ambiente Seguras

```bash
# .env.production
JWT_SECRET_KEY='sua-chave-super-secreta-de-pelo-menos-64-caracteres-aqui'
JWT_ALGORITHM='HS256'
JWT_EXPIRATION_MINUTES=30

# Database
DATABASE_URL='postgresql+psycopg://user:password@host:5432/db'

# HTTPS obrigatório
FORCE_HTTPS=true

# Logging
LOG_LEVEL=INFO
```

### Checklist de Segurança

#### ✅ Autenticação
- [ ] JWT com chave secreta forte (64+ caracteres)
- [ ] Tempo de expiração adequado (15-30 minutos)
- [ ] Hash de senhas com Argon2
- [ ] Validação de força de senha

#### ✅ Autorização
- [ ] Verificação de propriedade de recursos
- [ ] Princípio de menor privilégio
- [ ] Validação de permissões por endpoint

#### ✅ Entrada/Saída
- [ ] Validação rigorosa com Pydantic
- [ ] Sanitização de dados de entrada
- [ ] Escape de dados de saída
- [ ] Limite de tamanho de payload

#### ✅ Comunicação
- [ ] HTTPS obrigatório em produção
- [ ] CORS configurado corretamente
- [ ] Headers de segurança adequados

#### ✅ Infraestrutura
- [ ] Rate limiting implementado
- [ ] Logs de segurança habilitados
- [ ] Monitoramento de anomalias
- [ ] Backup seguro de dados

### Headers de Segurança

```python
from fastapi.middleware.secure_headers import SecureHeadersMiddleware

app.add_middleware(
    SecureHeadersMiddleware,
    server="FastAPI",  # Ocultar versão
    x_frame_options="DENY",  # Prevenir clickjacking
    content_type_options="nosniff",  # Prevenir MIME sniffing
    x_xss_protection="1; mode=block",  # XSS protection
    strict_transport_security="max-age=31536000; includeSubDomains",  # HSTS
    content_security_policy="default-src 'self'",  # CSP
)
```

## 📊 Auditoria e Monitoramento

### Logs de Segurança

```python
import logging
from datetime import datetime

security_logger = logging.getLogger("security")

async def log_authentication_attempt(email: str, success: bool, ip: str):
    """Registrar tentativa de login."""
    security_logger.info(
        f"Authentication attempt - "
        f"Email: {email}, "
        f"Success: {success}, "
        f"IP: {ip}, "
        f"Timestamp: {datetime.utcnow()}"
    )

async def log_authorization_failure(user_id: int, resource: str, action: str):
    """Registrar falha de autorização."""
    security_logger.warning(
        f"Authorization failure - "
        f"User: {user_id}, "
        f"Resource: {resource}, "
        f"Action: {action}, "
        f"Timestamp: {datetime.utcnow()}"
    )
```

### Métricas de Segurança

```python
from prometheus_client import Counter, Histogram

# Contadores de segurança
auth_attempts = Counter('auth_attempts_total', 'Total authentication attempts', ['status'])
auth_failures = Counter('auth_failures_total', 'Failed authentication attempts')
forbidden_access = Counter('forbidden_access_total', 'Forbidden access attempts')

# Histograma de tempo de autenticação
auth_duration = Histogram('auth_duration_seconds', 'Authentication duration')

# Uso nos endpoints
@auth_duration.time()
async def authenticate_user(email: str, password: str):
    try:
        # Lógica de autenticação
        auth_attempts.labels(status='success').inc()
        return user
    except AuthenticationError:
        auth_attempts.labels(status='failure').inc()
        auth_failures.inc()
        raise
```

## 🚀 Próximos Passos

Para implementar melhorias de segurança:

1. 💻 [Desenvolvimento](development.md) - Fluxo seguro de desenvolvimento
2. 🧪 [Testes](testing.md) - Testes de segurança
3. 🚀 [Deploy](deployment.md) - Deploy seguro
4. 📊 Implementar Rate Limiting com Redis
5. 🔍 Adicionar detecção de anomalias
6. 📱 Implementar 2FA (Two-Factor Authentication)