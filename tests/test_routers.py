import pytest
from fastapi import HTTPException

from car_api.routers import (
    create_car,
    delete_car,
    get_car,
    list_cars,
    patch_car,
    update_car,
)
from car_api.schemas import CarPartialUpdate, CarSchema


@pytest.mark.asyncio
async def test_crud_flow(session):
    schema = CarSchema(
        brand='Ford',
        model='Fiesta',
        color='Blue',
        factory_year=2020,
        model_year=2021,
        description='desc',
    )

    car = await create_car(schema, session)
    car_id = car.id

    result = await get_car(car_id, session)
    assert result.model == 'Fiesta'

    cars = await list_cars(session)
    assert len(cars['cars']) == 1

    schema.model = 'Focus'
    updated = await update_car(car_id, schema, session)
    assert updated.model == 'Focus'

    partial = CarPartialUpdate(color='Red')
    patched = await patch_car(car_id, partial, session)
    assert patched.color == 'Red'

    await delete_car(car_id, session)
    cars = await list_cars(session)
    assert cars['cars'] == []


@pytest.mark.asyncio
async def test_car_not_found_errors(session):
    schema = CarSchema(
        brand='Ford',
        model='Fiesta',
        color='Blue',
        factory_year=2020,
        model_year=2021,
        description='desc',
    )
    with pytest.raises(HTTPException):
        await get_car(999, session)

    with pytest.raises(HTTPException):
        await update_car(999, schema, session)

    with pytest.raises(HTTPException):
        await patch_car(999, CarPartialUpdate(model='X'), session)

    with pytest.raises(HTTPException):
        await delete_car(999, session)
