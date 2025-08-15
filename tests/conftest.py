from decimal import Decimal

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from car_api.app import app
from car_api.core.database import get_session
from car_api.core.security import create_access_token, get_password_hash
from car_api.models import Base
from car_api.models.cars import Brand, Car, FuelType, TransmissionType
from car_api.models.users import User


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        url='sqlite+aiosqlite:///:memory:',
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user_data():
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'secret123',
    }


@pytest_asyncio.fixture
async def user(session, user_data):
    hashed_password = get_password_hash(user_data['password'])
    db_user = User(
        username=user_data['username'],
        email=user_data['email'],
        password=hashed_password,
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@pytest_asyncio.fixture
async def second_user(session):
    hashed_password = get_password_hash('password123')
    db_user = User(
        username='seconduser',
        email='second@example.com',
        password=hashed_password,
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@pytest.fixture
def access_token(user):
    return create_access_token(data={'sub': str(user.id)})


@pytest.fixture
def auth_headers(access_token):
    return {'Authorization': f'Bearer {access_token}'}


@pytest_asyncio.fixture
async def brand_data():
    return {
        'name': 'Toyota',
        'description': 'Japanese automotive manufacturer',
        'is_active': True,
    }


@pytest_asyncio.fixture
async def brand(session, brand_data):
    db_brand = Brand(
        name=brand_data['name'],
        description=brand_data['description'],
        is_active=brand_data['is_active'],
    )
    session.add(db_brand)
    await session.commit()
    await session.refresh(db_brand)
    return db_brand


@pytest_asyncio.fixture
async def second_brand(session):
    db_brand = Brand(
        name='Honda',
        description='Japanese automotive manufacturer',
        is_active=True,
    )
    session.add(db_brand)
    await session.commit()
    await session.refresh(db_brand)
    return db_brand


@pytest_asyncio.fixture
async def car_data(brand):
    return {
        'model': 'Corolla',
        'factory_year': 2023,
        'model_year': 2023,
        'color': 'White',
        'plate': 'ABC1234',
        'fuel_type': FuelType.FLEX,
        'transmission': TransmissionType.MANUAL,
        'price': Decimal('50000.00'),
        'description': 'Excellent condition',
        'is_available': True,
        'brand_id': brand.id,
    }


@pytest_asyncio.fixture
async def car(session, user, brand, car_data):
    db_car = Car(
        model=car_data['model'],
        factory_year=car_data['factory_year'],
        model_year=car_data['model_year'],
        color=car_data['color'],
        plate=car_data['plate'],
        fuel_type=car_data['fuel_type'],
        transmission=car_data['transmission'],
        price=car_data['price'],
        description=car_data['description'],
        is_available=car_data['is_available'],
        brand_id=car_data['brand_id'],
        owner_id=user.id,
    )
    session.add(db_car)
    await session.commit()
    await session.refresh(db_car)
    return db_car


@pytest_asyncio.fixture
async def second_user_car(session, second_user, brand):
    db_car = Car(
        model='Civic',
        factory_year=2022,
        model_year=2022,
        color='Black',
        plate='XYZ9876',
        fuel_type=FuelType.GASOLINE,
        transmission=TransmissionType.AUTOMATIC,
        price=Decimal('45000.00'),
        description='Great car',
        is_available=True,
        brand_id=brand.id,
        owner_id=second_user.id,
    )
    session.add(db_car)
    await session.commit()
    await session.refresh(db_car)
    return db_car
