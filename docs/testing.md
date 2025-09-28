# Testes

## 🧪 Estratégia de Testes

### Pirâmide de Testes

```mermaid
graph TB
    subgraph "Pirâmide de Testes"
        E2E[End-to-End Tests]
        INT[Integration Tests]
        UNIT[Unit Tests]
    end

    subgraph "Distribuição"
        E2E_PCT[10%<br/>Poucos e Caros]
        INT_PCT[20%<br/>Moderados]
        UNIT_PCT[70%<br/>Muitos e Rápidos]
    end

    E2E --> E2E_PCT
    INT --> INT_PCT
    UNIT --> UNIT_PCT

    style UNIT fill:#e8f5e8
    style INT fill:#e3f2fd
    style E2E fill:#fff3e0
```

### Tipos de Testes Implementados

#### 1. **Unit Tests (70%)**
- Testam funções/métodos isoladamente
- Rápidos de executar (< 1s cada)
- Mocks para dependências externas
- Cobertura de lógica de negócio

#### 2. **Integration Tests (20%)**
- Testam interação entre componentes
- Incluem banco de dados de teste
- Validam schemas e validações
- Testam endpoints da API

#### 3. **End-to-End Tests (10%)**
- Testam fluxos completos
- Simulam usuário real
- Validam funcionalidades críticas
- Executados menos frequentemente

## 📁 Estrutura de Testes

```
tests/
├── __init__.py
├── conftest.py              # 🔧 Configurações e fixtures
├── unit/                    # 🧪 Testes unitários
│   ├── test_security.py     # 🔐 Funções de segurança
│   ├── test_models.py       # 🏗️ Modelos SQLAlchemy
│   └── test_schemas.py      # 📝 Validações Pydantic
├── integration/             # 🔗 Testes de integração
│   ├── test_auth.py         # 🔑 Autenticação
│   ├── test_brands.py       # 🏷️ API de marcas
│   ├── test_cars.py         # 🚗 API de carros
│   ├── test_users.py        # 👤 API de usuários
│   └── test_db.py           # 🗃️ Banco de dados
├── e2e/                     # 🎯 Testes end-to-end
│   ├── test_user_journey.py # 👤 Jornada do usuário
│   └── test_car_workflow.py # 🚗 Fluxo de carros
└── fixtures/                # 📦 Dados de teste
    ├── cars.json
    ├── brands.json
    └── users.json
```

## ⚙️ Configuração de Testes

### conftest.py - Fixtures Globais

```python
# tests/conftest.py
import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from car_api.app import app
from car_api.core.database import get_session
from car_api.core.security import create_access_token, get_password_hash
from car_api.models.base import Base
from car_api.models.cars import Brand, Car, FuelType, TransmissionType
from car_api.models.users import User

# Database de teste em memória
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """Criar event loop para a sessão de testes."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def db_engine():
    """Engine de banco de dados para testes."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(db_engine):
    """Sessão de banco de dados para testes."""
    TestSessionLocal = async_sessionmaker(
        db_engine, expire_on_commit=False
    )

    async with TestSessionLocal() as session:
        yield session

@pytest_asyncio.fixture
async def client(db_session):
    """Cliente HTTP para testes de API."""
    app.dependency_overrides[get_session] = lambda: db_session

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def sample_user(db_session):
    """Usuário de exemplo para testes."""
    user = User(
        username="testuser",
        email="test@example.com",
        password=get_password_hash("password123")
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def auth_headers(sample_user):
    """Headers de autenticação para testes."""
    token = create_access_token(data={"sub": str(sample_user.id)})
    return {"Authorization": f"Bearer {token}"}

@pytest_asyncio.fixture
async def sample_brand(db_session):
    """Marca de exemplo para testes."""
    brand = Brand(
        name="Toyota",
        description="Marca japonesa confiável",
        is_active=True
    )
    db_session.add(brand)
    await db_session.commit()
    await db_session.refresh(brand)
    return brand

@pytest_asyncio.fixture
async def sample_car(db_session, sample_user, sample_brand):
    """Carro de exemplo para testes."""
    car = Car(
        model="Corolla",
        factory_year=2022,
        model_year=2023,
        color="Prata",
        plate="ABC1234",
        fuel_type=FuelType.FLEX,
        transmission=TransmissionType.AUTOMATIC,
        price=85000.00,
        brand_id=sample_brand.id,
        owner_id=sample_user.id
    )
    db_session.add(car)
    await db_session.commit()
    await db_session.refresh(car)
    return car
```

### pytest.ini - Configuração

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
addopts =
    -v
    --strict-markers
    --strict-config
    --cov=car_api
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=90
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow tests
    database: Tests that require database
    auth: Authentication tests
```

## 🧪 Testes Unitários

### Testes de Segurança

```python
# tests/unit/test_security.py
import pytest
from datetime import datetime, timedelta
import jwt

from car_api.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    get_current_user
)
from car_api.core.settings import Settings

settings = Settings()

class TestPasswordHashing:
    def test_password_hash_and_verify(self):
        """Testar hash e verificação de senha."""
        password = "my_secure_password123"

        # Hash da senha
        hashed = get_password_hash(password)

        # Verificações
        assert hashed != password  # Hash é diferente da senha original
        assert verify_password(password, hashed) is True  # Verificação positiva
        assert verify_password("wrong_password", hashed) is False  # Verificação negativa

    def test_different_hashes_for_same_password(self):
        """Testar que a mesma senha gera hashes diferentes (salt)."""
        password = "same_password"

        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2  # Hashes diferentes devido ao salt
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

class TestJWT:
    def test_create_and_decode_token(self):
        """Testar criação e decodificação de token JWT."""
        user_data = {"sub": "123"}

        # Criar token
        token = create_access_token(data=user_data)

        # Decodificar token
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )

        assert payload["sub"] == "123"
        assert "exp" in payload  # Token tem expiração

    def test_token_expiration(self):
        """Testar expiração de token."""
        user_data = {"sub": "123"}

        # Criar token que expira imediatamente
        past_time = datetime.utcnow() - timedelta(minutes=1)
        token = jwt.encode(
            {**user_data, "exp": past_time},
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )

        # Tentar decodificar token expirado
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
```

### Testes de Modelos

```python
# tests/unit/test_models.py
import pytest
from decimal import Decimal
from datetime import datetime

from car_api.models.cars import Car, Brand, FuelType, TransmissionType
from car_api.models.users import User

class TestUserModel:
    def test_user_creation(self):
        """Testar criação de usuário."""
        user = User(
            username="testuser",
            email="test@example.com",
            password="hashed_password"
        )

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password == "hashed_password"

    def test_user_string_representation(self):
        """Testar representação string do usuário."""
        user = User(
            username="testuser",
            email="test@example.com",
            password="hashed_password"
        )

        assert str(user) == "testuser"

class TestCarModel:
    def test_car_creation(self):
        """Testar criação de carro."""
        car = Car(
            model="Civic",
            factory_year=2023,
            model_year=2023,
            color="Preto",
            plate="ABC1234",
            fuel_type=FuelType.FLEX,
            transmission=TransmissionType.MANUAL,
            price=Decimal("95000.00"),
            brand_id=1,
            owner_id=1
        )

        assert car.model == "Civic"
        assert car.factory_year == 2023
        assert car.fuel_type == FuelType.FLEX
        assert car.price == Decimal("95000.00")

    def test_fuel_type_enum(self):
        """Testar enum de tipo de combustível."""
        assert FuelType.GASOLINE == "gasoline"
        assert FuelType.ELECTRIC == "electric"
        assert FuelType.HYBRID == "hybrid"

    def test_transmission_enum(self):
        """Testar enum de transmissão."""
        assert TransmissionType.MANUAL == "manual"
        assert TransmissionType.AUTOMATIC == "automatic"
        assert TransmissionType.CVT == "cvt"
```

### Testes de Schemas

```python
# tests/unit/test_schemas.py
import pytest
from decimal import Decimal
from pydantic import ValidationError

from car_api.schemas.cars import CarSchema, CarUpdateSchema
from car_api.schemas.users import UserSchema
from car_api.models.cars import FuelType, TransmissionType

class TestUserSchema:
    def test_valid_user_schema(self):
        """Testar schema válido de usuário."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }

        user = UserSchema(**user_data)

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password == "password123"

    def test_invalid_email(self):
        """Testar email inválido."""
        user_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "password123"
        }

        with pytest.raises(ValidationError) as exc_info:
            UserSchema(**user_data)

        assert "email" in str(exc_info.value)

    def test_short_password(self):
        """Testar senha muito curta."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "123"  # Muito curta
        }

        with pytest.raises(ValidationError) as exc_info:
            UserSchema(**user_data)

        assert "password" in str(exc_info.value)

class TestCarSchema:
    def test_valid_car_schema(self):
        """Testar schema válido de carro."""
        car_data = {
            "model": "Civic",
            "factory_year": 2023,
            "model_year": 2023,
            "color": "Preto",
            "plate": "ABC1234",
            "fuel_type": "flex",
            "transmission": "manual",
            "price": "95000.00",
            "brand_id": 1
        }

        car = CarSchema(**car_data)

        assert car.model == "Civic"
        assert car.factory_year == 2023
        assert car.fuel_type == FuelType.FLEX
        assert car.price == Decimal("95000.00")

    def test_invalid_year(self):
        """Testar ano inválido."""
        car_data = {
            "model": "Civic",
            "factory_year": 1800,  # Muito antigo
            "model_year": 2023,
            "color": "Preto",
            "plate": "ABC1234",
            "fuel_type": "flex",
            "transmission": "manual",
            "price": "95000.00",
            "brand_id": 1
        }

        with pytest.raises(ValidationError) as exc_info:
            CarSchema(**car_data)

        assert "factory_year" in str(exc_info.value)

    def test_invalid_plate_format(self):
        """Testar formato inválido de placa."""
        car_data = {
            "model": "Civic",
            "factory_year": 2023,
            "model_year": 2023,
            "color": "Preto",
            "plate": "INVALID",  # Formato inválido
            "fuel_type": "flex",
            "transmission": "manual",
            "price": "95000.00",
            "brand_id": 1
        }

        with pytest.raises(ValidationError) as exc_info:
            CarSchema(**car_data)

        assert "plate" in str(exc_info.value)
```

## 🔗 Testes de Integração

### Testes de Autenticação

```python
# tests/integration/test_auth.py
import pytest
from httpx import AsyncClient

class TestAuthentication:
    async def test_login_success(self, client: AsyncClient, sample_user):
        """Testar login bem-sucedido."""
        login_data = {
            "email": sample_user.email,
            "password": "password123"
        }

        response = await client.post("/api/v1/auth/token", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_invalid_credentials(self, client: AsyncClient, sample_user):
        """Testar login com credenciais inválidas."""
        login_data = {
            "email": sample_user.email,
            "password": "wrong_password"
        }

        response = await client.post("/api/v1/auth/token", json=login_data)

        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Testar login com usuário inexistente."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }

        response = await client.post("/api/v1/auth/token", json=login_data)

        assert response.status_code == 401

    async def test_refresh_token(self, client: AsyncClient, auth_headers):
        """Testar renovação de token."""
        response = await client.post(
            "/api/v1/auth/refresh_token",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_access_protected_endpoint_without_token(self, client: AsyncClient):
        """Testar acesso a endpoint protegido sem token."""
        response = await client.get("/api/v1/cars/")

        assert response.status_code == 401
```

### Testes de API de Carros

```python
# tests/integration/test_cars.py
import pytest
from httpx import AsyncClient
from decimal import Decimal

class TestCarsAPI:
    async def test_create_car_success(self, client: AsyncClient, auth_headers, sample_brand):
        """Testar criação bem-sucedida de carro."""
        car_data = {
            "model": "Civic",
            "factory_year": 2023,
            "model_year": 2023,
            "color": "Preto",
            "plate": "XYZ9876",
            "fuel_type": "flex",
            "transmission": "manual",
            "price": "95000.00",
            "description": "Carro seminovo",
            "is_available": True,
            "brand_id": sample_brand.id
        }

        response = await client.post(
            "/api/v1/cars/",
            json=car_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["model"] == "Civic"
        assert data["plate"] == "XYZ9876"
        assert data["brand"]["name"] == sample_brand.name
        assert "owner" in data

    async def test_create_car_duplicate_plate(self, client: AsyncClient, auth_headers, sample_car):
        """Testar criação com placa duplicada."""
        car_data = {
            "model": "Civic",
            "factory_year": 2023,
            "model_year": 2023,
            "color": "Preto",
            "plate": sample_car.plate,  # Placa já existe
            "fuel_type": "flex",
            "transmission": "manual",
            "price": "95000.00",
            "brand_id": sample_car.brand_id
        }

        response = await client.post(
            "/api/v1/cars/",
            json=car_data,
            headers=auth_headers
        )

        assert response.status_code == 400
        assert "Placa já está em uso" in response.json()["detail"]

    async def test_list_cars(self, client: AsyncClient, auth_headers, sample_car):
        """Testar listagem de carros."""
        response = await client.get("/api/v1/cars/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "cars" in data
        assert len(data["cars"]) == 1
        assert data["cars"][0]["id"] == sample_car.id

    async def test_list_cars_with_filters(self, client: AsyncClient, auth_headers, sample_car):
        """Testar listagem com filtros."""
        # Filtro por marca
        response = await client.get(
            f"/api/v1/cars/?brand_id={sample_car.brand_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert len(response.json()["cars"]) == 1

        # Filtro por combustível
        response = await client.get(
            f"/api/v1/cars/?fuel_type={sample_car.fuel_type}",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert len(response.json()["cars"]) == 1

        # Filtro por preço
        response = await client.get(
            f"/api/v1/cars/?min_price=50000&max_price=100000",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert len(response.json()["cars"]) == 1

    async def test_get_car_success(self, client: AsyncClient, auth_headers, sample_car):
        """Testar busca bem-sucedida de carro."""
        response = await client.get(
            f"/api/v1/cars/{sample_car.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_car.id
        assert data["model"] == sample_car.model

    async def test_get_car_not_found(self, client: AsyncClient, auth_headers):
        """Testar busca de carro inexistente."""
        response = await client.get("/api/v1/cars/999", headers=auth_headers)

        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"]

    async def test_update_car_success(self, client: AsyncClient, auth_headers, sample_car):
        """Testar atualização bem-sucedida de carro."""
        update_data = {
            "price": "88000.00",
            "description": "Preço atualizado"
        }

        response = await client.put(
            f"/api/v1/cars/{sample_car.id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["price"] == "88000.00"
        assert data["description"] == "Preço atualizado"

    async def test_delete_car_success(self, client: AsyncClient, auth_headers, sample_car):
        """Testar deleção bem-sucedida de carro."""
        response = await client.delete(
            f"/api/v1/cars/{sample_car.id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verificar que foi deletado
        response = await client.get(
            f"/api/v1/cars/{sample_car.id}",
            headers=auth_headers
        )
        assert response.status_code == 404
```

## 🎯 Testes End-to-End

### Jornada Completa do Usuário

```python
# tests/e2e/test_user_journey.py
import pytest
from httpx import AsyncClient

class TestUserJourney:
    async def test_complete_user_journey(self, client: AsyncClient):
        """Testar jornada completa do usuário."""

        # 1. Registrar usuário
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepassword123"
        }
        response = await client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 201
        user_id = response.json()["id"]

        # 2. Fazer login
        login_data = {
            "email": "newuser@example.com",
            "password": "securepassword123"
        }
        response = await client.post("/api/v1/auth/token", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Criar marca
        brand_data = {
            "name": "Tesla",
            "description": "Veículos elétricos",
            "is_active": True
        }
        response = await client.post("/api/v1/brands/", json=brand_data, headers=headers)
        assert response.status_code == 201
        brand_id = response.json()["id"]

        # 4. Criar múltiplos carros
        cars = []
        for i in range(3):
            car_data = {
                "model": f"Model {i+1}",
                "factory_year": 2023,
                "model_year": 2023,
                "color": ["Branco", "Preto", "Vermelho"][i],
                "plate": f"TSL{i+1}234",
                "fuel_type": "electric",
                "transmission": "automatic",
                "price": f"{150000 + i*10000}.00",
                "description": f"Tesla Model {i+1}",
                "is_available": True,
                "brand_id": brand_id
            }
            response = await client.post("/api/v1/cars/", json=car_data, headers=headers)
            assert response.status_code == 201
            cars.append(response.json())

        # 5. Listar todos os carros
        response = await client.get("/api/v1/cars/", headers=headers)
        assert response.status_code == 200
        assert len(response.json()["cars"]) == 3

        # 6. Filtrar carros por preço
        response = await client.get(
            "/api/v1/cars/?min_price=160000",
            headers=headers
        )
        assert response.status_code == 200
        filtered_cars = response.json()["cars"]
        assert len(filtered_cars) == 2  # Apenas 2 carros custam mais que 160k

        # 7. Atualizar um carro
        car_to_update = cars[0]
        update_data = {"price": "145000.00", "is_available": False}
        response = await client.put(
            f"/api/v1/cars/{car_to_update['id']}",
            json=update_data,
            headers=headers
        )
        assert response.status_code == 200
        assert response.json()["price"] == "145000.00"
        assert response.json()["is_available"] is False

        # 8. Buscar carros disponíveis
        response = await client.get(
            "/api/v1/cars/?is_available=true",
            headers=headers
        )
        assert response.status_code == 200
        available_cars = response.json()["cars"]
        assert len(available_cars) == 2  # Apenas 2 estão disponíveis

        # 9. Deletar um carro
        car_to_delete = cars[1]
        response = await client.delete(
            f"/api/v1/cars/{car_to_delete['id']}",
            headers=headers
        )
        assert response.status_code == 204

        # 10. Verificar que foi deletado
        response = await client.get("/api/v1/cars/", headers=headers)
        assert response.status_code == 200
        remaining_cars = response.json()["cars"]
        assert len(remaining_cars) == 2
        assert car_to_delete['id'] not in [car['id'] for car in remaining_cars]

        # 11. Renovar token
        response = await client.post("/api/v1/auth/refresh_token", headers=headers)
        assert response.status_code == 200
        new_token = response.json()["access_token"]
        assert new_token != token  # Token deve ser diferente

        # 12. Verificar acesso com novo token
        new_headers = {"Authorization": f"Bearer {new_token}"}
        response = await client.get("/api/v1/cars/", headers=new_headers)
        assert response.status_code == 200
```

## 📊 Cobertura de Testes

### Configuração de Coverage

```toml
# pyproject.toml
[tool.coverage.run]
source = ["car_api"]
omit = [
    "*/tests/*",
    "*/venv/*",
    "*/.venv/*",
    "*/migrations/*",
    "*/__init__.py"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:"
]
```

### Executar Testes com Coverage

```bash
# Executar todos os testes com coverage
poetry run pytest --cov=car_api --cov-report=html --cov-report=term-missing

# Coverage mínima de 90%
poetry run pytest --cov=car_api --cov-fail-under=90

# Gerar relatório HTML
poetry run pytest --cov=car_api --cov-report=html
open htmlcov/index.html

# Coverage apenas de arquivos modificados
poetry run pytest --cov=car_api --cov-report=term-missing tests/integration/test_cars.py
```

### Relatório de Coverage

```
Name                          Stmts   Miss  Cover   Missing
-----------------------------------------------------------
car_api/__init__.py               0      0   100%
car_api/app.py                   15      0   100%
car_api/core/database.py         12      1    92%   23
car_api/core/security.py         45      2    96%   67-68
car_api/core/settings.py          8      0   100%
car_api/models/base.py            3      0   100%
car_api/models/cars.py           35      0   100%
car_api/models/users.py          12      0   100%
car_api/routers/auth.py          25      1    96%   47
car_api/routers/brands.py        85      3    96%   156-158
car_api/routers/cars.py         125      5    96%   234-238
car_api/routers/users.py         95      4    96%   167-170
car_api/schemas/auth.py           8      0   100%
car_api/schemas/brands.py        18      0   100%
car_api/schemas/cars.py          32      0   100%
car_api/schemas/users.py         22      0   100%
-----------------------------------------------------------
TOTAL                           540     16    97%
```

## 🚀 Automação de Testes

### GitHub Actions CI/CD

```yaml
# .github/workflows/tests.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.13]

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_car_api
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install Poetry
      uses: snok/install-poetry@v1
      with:
        version: latest
        virtualenvs-create: true
        virtualenvs-in-project: true

    - name: Load cached venv
      id: cached-poetry-dependencies
      uses: actions/cache@v3
      with:
        path: .venv
        key: venv-${{ runner.os }}-${{ matrix.python-version }}-${{ hashFiles('**/poetry.lock') }}

    - name: Install dependencies
      if: steps.cached-poetry-dependencies.outputs.cache-hit != 'true'
      run: poetry install --no-interaction --no-root

    - name: Install project
      run: poetry install --no-interaction

    - name: Run linting
      run: |
        poetry run ruff check
        poetry run ruff format --check

    - name: Run tests
      run: |
        poetry run pytest --cov=car_api --cov-report=xml --cov-fail-under=90
      env:
        DATABASE_URL: postgresql+psycopg://postgres:postgres@localhost:5432/test_car_api
        JWT_SECRET_KEY: test-secret-key-for-ci

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
```

### Pre-commit Hooks para Testes

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: tests
        name: Run tests
        entry: poetry run pytest tests/unit tests/integration --maxfail=1
        language: system
        pass_filenames: false
        always_run: true
```

## 🎯 Testes de Performance

### Teste de Carga

```python
# tests/performance/test_load.py
import asyncio
import time
from httpx import AsyncClient

class TestPerformance:
    async def test_concurrent_car_creation(self, client: AsyncClient, auth_headers, sample_brand):
        """Testar criação concorrente de carros."""

        async def create_car(i):
            car_data = {
                "model": f"Civic {i}",
                "factory_year": 2023,
                "model_year": 2023,
                "color": "Preto",
                "plate": f"ABC{i:04d}",
                "fuel_type": "flex",
                "transmission": "manual",
                "price": "95000.00",
                "brand_id": sample_brand.id
            }

            start_time = time.time()
            response = await client.post(
                "/api/v1/cars/",
                json=car_data,
                headers=auth_headers
            )
            end_time = time.time()

            return {
                "status_code": response.status_code,
                "duration": end_time - start_time
            }

        # Criar 10 carros concorrentemente
        tasks = [create_car(i) for i in range(10)]
        results = await asyncio.gather(*tasks)

        # Verificar resultados
        success_count = sum(1 for r in results if r["status_code"] == 201)
        avg_duration = sum(r["duration"] for r in results) / len(results)

        assert success_count == 10  # Todos devem ter sucesso
        assert avg_duration < 1.0   # Menos de 1 segundo por request

        print(f"Created {success_count} cars in average {avg_duration:.3f}s each")
```

## 📋 Comandos de Teste

### Comandos Básicos

```bash
# Executar todos os testes
poetry run pytest

# Executar testes específicos
poetry run pytest tests/unit/
poetry run pytest tests/integration/test_cars.py
poetry run pytest tests/e2e/ -v

# Executar com marcadores
poetry run pytest -m unit
poetry run pytest -m integration
poetry run pytest -m "not slow"

# Executar com coverage
poetry run pytest --cov=car_api
poetry run pytest --cov=car_api --cov-report=html

# Executar testes que falharam na última execução
poetry run pytest --lf

# Executar em modo watch
poetry run ptw --now
```

### Comandos Avançados

```bash
# Executar com profiling
poetry run pytest --profile

# Executar com timeout
poetry run pytest --timeout=300

# Executar em paralelo
poetry run pytest -n auto

# Verbose com duração
poetry run pytest -v --durations=10

# Gerar relatório JUnit XML
poetry run pytest --junit-xml=results.xml

# Executar apenas testes modificados
poetry run pytest --testmon
```

## 🚀 Próximos Passos

Para melhorar ainda mais os testes:

1. 🚀 [Deploy](deployment.md) - Pipeline de CI/CD
2. 📊 Implementar testes de mutation testing
3. 🎯 Adicionar testes de propriedade (Hypothesis)
4. 📱 Testes de API com Postman/Newman
5. 🔍 Testes de segurança automatizados
6. 📈 Benchmarks de performance automatizados