from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from car_api.core.database import get_session
from car_api.core.security import get_current_user, verify_car_ownership
from car_api.models.cars import Brand, Car, FuelType, TransmissionType
from car_api.models.users import User
from car_api.schemas.cars import (
    CarListPublicSchema,
    CarPublicSchema,
    CarSchema,
    CarUpdateSchema,
)

router = APIRouter()


@router.post(
    path='/',
    status_code=status.HTTP_201_CREATED,
    response_model=CarPublicSchema,
    summary='Criar novo carro',
)
async def create_car(
    car: CarSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    plate_exists = await db.scalar(
        select(exists().where(Car.plate == car.plate))
    )
    if plate_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Placa já está em uso',
        )

    brand_exists = await db.scalar(
        select(exists().where(Brand.id == car.brand_id))
    )
    if not brand_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Marca não encontrada',
        )

    db_car = Car(
        model=car.model,
        factory_year=car.factory_year,
        model_year=car.model_year,
        color=car.color,
        plate=car.plate,
        fuel_type=car.fuel_type,
        transmission=car.transmission,
        price=car.price,
        description=car.description,
        is_available=car.is_available,
        brand_id=car.brand_id,
        owner_id=current_user.id,
    )

    db.add(db_car)
    await db.commit()
    await db.refresh(db_car)

    result = await db.execute(
        select(Car)
        .options(selectinload(Car.brand), selectinload(Car.owner))
        .where(Car.id == db_car.id)
    )
    car_with_relations = result.scalar_one()

    return car_with_relations


@router.get(
    path='/',
    status_code=status.HTTP_200_OK,
    response_model=CarListPublicSchema,
    summary='Listar carros',
)
async def list_cars(
    offset: int = Query(0, ge=0, description='Número de registros para pular'),
    limit: int = Query(100, ge=1, le=100, description='Limite de registros'),
    search: Optional[str] = Query(
        None, description='Buscar por modelo ou placa'
    ),
    brand_id: Optional[int] = Query(None, description='Filtrar por marca'),
    fuel_type: Optional[FuelType] = Query(
        None, description='Filtrar por tipo de combustível'
    ),
    transmission: Optional[TransmissionType] = Query(
        None, description='Filtrar por transmissão'
    ),
    is_available: Optional[bool] = Query(
        None, description='Filtrar por disponibilidade'
    ),
    min_price: Optional[float] = Query(None, ge=0, description='Preço mínimo'),
    max_price: Optional[float] = Query(None, ge=0, description='Preço máximo'),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    query = select(Car).options(
        selectinload(Car.brand), selectinload(Car.owner)
    )
    query = query.where(Car.owner_id == current_user.id)

    if search:
        search_filter = f'%{search}%'
        query = query.where(
            (Car.model.ilike(search_filter)) | (Car.plate.ilike(search_filter))
        )

    if brand_id is not None:
        query = query.where(Car.brand_id == brand_id)

    if fuel_type is not None:
        query = query.where(Car.fuel_type == fuel_type)

    if transmission is not None:
        query = query.where(Car.transmission == transmission)

    if is_available is not None:
        query = query.where(Car.is_available == is_available)

    if min_price is not None:
        query = query.where(Car.price >= min_price)

    if max_price is not None:
        query = query.where(Car.price <= max_price)

    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    cars = result.scalars().all()

    return {'cars': cars, 'offset': offset, 'limit': limit}


@router.get(
    path='/{car_id}',
    status_code=status.HTTP_200_OK,
    response_model=CarPublicSchema,
    summary='Buscar carro por ID',
)
async def get_car(
    car_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(Car)
        .options(selectinload(Car.brand), selectinload(Car.owner))
        .where(Car.id == car_id)
    )
    car = result.scalar_one_or_none()

    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Carro não encontrado',
        )

    verify_car_ownership(current_user, car.owner_id)

    return car


@router.put(
    path='/{car_id}',
    status_code=status.HTTP_200_OK,
    response_model=CarPublicSchema,
    summary='Atualizar carro',
)
async def update_car(
    car_id: int,
    car_update: CarUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    car = await db.get(Car, car_id)

    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Carro não encontrado',
        )

    verify_car_ownership(current_user, car.owner_id)

    update_data = car_update.model_dump(exclude_unset=True)

    if 'plate' in update_data and update_data['plate'] != car.plate:
        plate_exists = await db.scalar(
            select(
                exists().where(
                    (Car.plate == update_data['plate']) & (Car.id != car_id)
                )
            )
        )
        if plate_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Placa já está em uso',
            )

    if 'brand_id' in update_data and update_data['brand_id'] != car.brand_id:
        brand_exists = await db.scalar(
            select(exists().where(Brand.id == update_data['brand_id']))
        )
        if not brand_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Marca não encontrada',
            )

    if 'owner_id' in update_data:
        del update_data['owner_id']

    for field, value in update_data.items():
        setattr(car, field, value)

    await db.commit()
    await db.refresh(car)

    result = await db.execute(
        select(Car)
        .options(selectinload(Car.brand), selectinload(Car.owner))
        .where(Car.id == car_id)
    )
    car_with_relations = result.scalar_one()

    return car_with_relations


@router.delete(
    path='/{car_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Deletar carro',
)
async def delete_car(
    car_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    car = await db.get(Car, car_id)

    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Carro não encontrado',
        )

    verify_car_ownership(current_user, car.owner_id)

    await db.delete(car)
    await db.commit()
