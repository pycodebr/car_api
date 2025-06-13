from car_api.schemas import CarList, CarPartialUpdate, CarPublic, CarSchema


def test_car_schema_valid():
    car = CarSchema(
        brand='Ford',
        model='Fiesta',
        color='Blue',
        factory_year=2020,
        model_year=2021,
        description='desc',
    )
    assert car.model == 'Fiesta'


def test_car_partial_update_optional():
    data = CarPartialUpdate(model='Focus')
    assert data.model == 'Focus'
    assert data.brand is None


def test_car_public():
    car = CarPublic(
        id=1,
        brand='Ford',
        model='Fiesta',
        color='Blue',
        factory_year=2020,
        model_year=2021,
        description='desc',
    )
    assert car.id == 1


def test_car_list():
    car = CarPublic(
        id=1,
        brand='Ford',
        model='Fiesta',
        color='Blue',
        factory_year=2020,
        model_year=2021,
        description='desc',
    )
    cars = CarList(cars=[car])
    assert cars.cars[0].brand == 'Ford'
