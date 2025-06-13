import pytest

from car_api.models import Car


@pytest.mark.asyncio
async def test_create_car(session):
    car = Car(
        brand="Ford",
        model="Fiesta",
        color="Blue",
        factory_year=2020,
        model_year=2021,
        description="desc",
    )
    session.add(car)
    await session.commit()
    await session.refresh(car)

    assert car.id is not None
    assert car.brand == "Ford"
