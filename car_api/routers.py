from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from car_api.database import get_session
from car_api.models import Car
from car_api.schemas import (
    CarList,
    CarPartialUpdate,
    CarPublic,
    CarSchema,
)

router = APIRouter(
    prefix='/api/v1/cars',
    tags=['cars'],
)


Session = Annotated[AsyncSession, Depends(get_session)]


@router.post(
    '/', response_model=CarPublic, status_code=status.HTTP_201_CREATED
)
async def create_car(
    car: CarSchema,
    session: Session,
):
    car = Car(**car.model_dump())
    session.add(car)
    await session.commit()
    await session.refresh(car)
    return car


@router.get('/', response_model=CarList)
async def list_cars(
    session: Session,
    skip: int = 0,
    limit: int = 100,
):
    query = await session.scalars(select(Car).offset(skip).limit(limit))
    cars = query.all()
    return {'cars': cars}


@router.get('/{car_id}', response_model=CarPublic)
async def get_car(
    car_id: int,
    session: Session,
):
    car = await session.get(Car, car_id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Car not found'
        )
    return car


@router.put('/{car_id}', response_model=CarPublic)
async def update_car(
    car_id: int,
    car: CarSchema,
    session: Session,
):
    db_car = await session.get(Car, car_id)
    if not db_car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Car not found'
        )
    for field, value in car.model_dump().items():
        setattr(db_car, field, value)
    await session.commit()
    await session.refresh(db_car)
    return db_car


@router.patch('/{car_id}', response_model=CarPublic)
async def patch_car(
    car_id: int,
    car: CarPartialUpdate,
    session: Session,
):
    db_car = await session.get(Car, car_id)
    if not db_car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Car not found'
        )
    update_data = {k: v for k, v in car.model_dump(exclude_unset=True).items()}
    for field, value in update_data.items():
        setattr(db_car, field, value)
    await session.commit()
    await session.refresh(db_car)
    return db_car


@router.delete('/{car_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_car(
    car_id: int,
    session: Session,
):
    car = await session.get(Car, car_id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Car not found'
        )
    await session.delete(car)
    await session.commit()
