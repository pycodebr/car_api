from decimal import Decimal
from http import HTTPStatus

import pytest

from car_api.models.cars import Car, FuelType, TransmissionType


def test_create_car_success(client, auth_headers, brand):
    car_data = {
        'model': 'Corolla',
        'factory_year': 2023,
        'model_year': 2023,
        'color': 'White',
        'plate': 'ABC1234',
        'fuel_type': FuelType.FLEX,
        'transmission': TransmissionType.MANUAL,
        'price': 50000.00,
        'description': 'Excellent condition',
        'is_available': True,
        'brand_id': brand.id,
    }

    response = client.post(
        '/api/v1/cars/', json=car_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data['model'] == car_data['model']
    assert data['factory_year'] == car_data['factory_year']
    assert data['model_year'] == car_data['model_year']
    assert data['color'] == car_data['color']
    assert data['plate'] == car_data['plate']
    assert data['fuel_type'] == car_data['fuel_type']
    assert data['transmission'] == car_data['transmission']
    assert float(data['price']) == car_data['price']
    assert data['description'] == car_data['description']
    assert data['is_available'] == car_data['is_available']
    assert data['brand_id'] == car_data['brand_id']
    assert 'id' in data
    assert 'created_at' in data
    assert 'updated_at' in data
    assert 'brand' in data
    assert 'owner' in data


def test_create_car_without_description(client, auth_headers, brand):
    car_data = {
        'model': 'Civic',
        'factory_year': 2022,
        'model_year': 2022,
        'color': 'Black',
        'plate': 'XYZ5678',
        'fuel_type': FuelType.GASOLINE,
        'transmission': TransmissionType.AUTOMATIC,
        'price': 45000.00,
        'brand_id': brand.id,
    }

    response = client.post(
        '/api/v1/cars/', json=car_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data['description'] is None
    assert data['is_available'] is True


def test_create_car_duplicate_plate(client, auth_headers, brand, car):
    car_data = {
        'model': 'Civic',
        'factory_year': 2022,
        'model_year': 2022,
        'color': 'Black',
        'plate': car.plate,
        'fuel_type': FuelType.GASOLINE,
        'transmission': TransmissionType.AUTOMATIC,
        'price': 45000.00,
        'brand_id': brand.id,
    }

    response = client.post(
        '/api/v1/cars/', json=car_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'Placa já está em uso' in response.json()['detail']


def test_create_car_invalid_brand(client, auth_headers):
    car_data = {
        'model': 'Civic',
        'factory_year': 2022,
        'model_year': 2022,
        'color': 'Black',
        'plate': 'XYZ5678',
        'fuel_type': FuelType.GASOLINE,
        'transmission': TransmissionType.AUTOMATIC,
        'price': 45000.00,
        'brand_id': 999,
    }

    response = client.post(
        '/api/v1/cars/', json=car_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'Marca não encontrada' in response.json()['detail']


def test_create_car_invalid_fuel_type(client, auth_headers, brand):
    car_data = {
        'model': 'Civic',
        'factory_year': 2022,
        'model_year': 2022,
        'color': 'Black',
        'plate': 'XYZ5678',
        'fuel_type': 'invalid_fuel',
        'transmission': TransmissionType.AUTOMATIC,
        'price': 45000.00,
        'brand_id': brand.id,
    }

    response = client.post(
        '/api/v1/cars/', json=car_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_car_invalid_transmission(client, auth_headers, brand):
    car_data = {
        'model': 'Civic',
        'factory_year': 2022,
        'model_year': 2022,
        'color': 'Black',
        'plate': 'XYZ5678',
        'fuel_type': FuelType.GASOLINE,
        'transmission': 'invalid_transmission',
        'price': 45000.00,
        'brand_id': brand.id,
    }

    response = client.post(
        '/api/v1/cars/', json=car_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_car_negative_price(client, auth_headers, brand):
    car_data = {
        'model': 'Civic',
        'factory_year': 2022,
        'model_year': 2022,
        'color': 'Black',
        'plate': 'XYZ5678',
        'fuel_type': FuelType.GASOLINE,
        'transmission': TransmissionType.AUTOMATIC,
        'price': -1000.00,
        'brand_id': brand.id,
    }

    response = client.post(
        '/api/v1/cars/', json=car_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_car_unauthorized(client, brand):
    car_data = {
        'model': 'Civic',
        'factory_year': 2022,
        'model_year': 2022,
        'color': 'Black',
        'plate': 'XYZ5678',
        'fuel_type': FuelType.GASOLINE,
        'transmission': TransmissionType.AUTOMATIC,
        'price': 45000.00,
        'brand_id': brand.id,
    }

    response = client.post('/api/v1/cars/', json=car_data)

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_list_cars_success(client, auth_headers, car):
    response = client.get('/api/v1/cars/', headers=auth_headers)

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert 'cars' in data
    assert 'offset' in data
    assert 'limit' in data
    assert data['offset'] == 0
    assert data['limit'] == 100
    assert len(data['cars']) >= 1

    car_data = data['cars'][0]
    assert 'brand' in car_data
    assert 'owner' in car_data


def test_list_cars_only_user_cars(client, auth_headers, car, second_user_car):
    response = client.get('/api/v1/cars/', headers=auth_headers)

    assert response.status_code == HTTPStatus.OK
    data = response.json()

    car_plates = [c['plate'] for c in data['cars']]
    assert car.plate in car_plates
    assert second_user_car.plate not in car_plates


def test_list_cars_with_pagination(client, auth_headers, car):
    response = client.get(
        '/api/v1/cars/?offset=0&limit=1', headers=auth_headers
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['offset'] == 0
    assert data['limit'] == 1
    assert len(data['cars']) <= 1


def test_list_cars_with_search_model(client, auth_headers, car):
    response = client.get(
        f'/api/v1/cars/?search={car.model}', headers=auth_headers
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data['cars']) >= 1
    assert data['cars'][0]['model'] == car.model


def test_list_cars_with_search_plate(client, auth_headers, car):
    response = client.get(
        f'/api/v1/cars/?search={car.plate}', headers=auth_headers
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data['cars']) == 1
    assert data['cars'][0]['plate'] == car.plate


def test_list_cars_with_search_case_insensitive(client, auth_headers, car):
    search_term = car.model.upper()
    response = client.get(
        f'/api/v1/cars/?search={search_term}', headers=auth_headers
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data['cars']) >= 1


def test_list_cars_filter_by_brand(client, auth_headers, car):
    response = client.get(
        f'/api/v1/cars/?brand_id={car.brand_id}', headers=auth_headers
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data['cars']) >= 1
    assert all(c['brand_id'] == car.brand_id for c in data['cars'])


def test_list_cars_filter_by_fuel_type(client, auth_headers, car):
    response = client.get(
        f'/api/v1/cars/?fuel_type={car.fuel_type}', headers=auth_headers
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data['cars']) >= 1
    assert all(c['fuel_type'] == car.fuel_type for c in data['cars'])


def test_list_cars_filter_by_transmission(client, auth_headers, car):
    response = client.get(
        f'/api/v1/cars/?transmission={car.transmission}', headers=auth_headers
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data['cars']) >= 1
    assert all(c['transmission'] == car.transmission for c in data['cars'])


def test_list_cars_filter_by_availability(client, auth_headers, car):
    response = client.get(
        f'/api/v1/cars/?is_available={car.is_available}', headers=auth_headers
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data['cars']) >= 1
    assert all(c['is_available'] == car.is_available for c in data['cars'])


def test_list_cars_filter_by_price_range(client, auth_headers, car):
    min_price = float(car.price) - 1000
    max_price = float(car.price) + 1000
    response = client.get(
        f'/api/v1/cars/?min_price={min_price}&max_price={max_price}',
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data['cars']) >= 1
    for car_data in data['cars']:
        assert min_price <= float(car_data['price']) <= max_price


def test_list_cars_filter_by_min_price_only(client, auth_headers, car):
    min_price = float(car.price) - 1000
    response = client.get(
        f'/api/v1/cars/?min_price={min_price}', headers=auth_headers
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data['cars']) >= 1
    for car_data in data['cars']:
        assert float(car_data['price']) >= min_price


def test_list_cars_filter_by_max_price_only(client, auth_headers, car):
    max_price = float(car.price) + 1000
    response = client.get(
        f'/api/v1/cars/?max_price={max_price}', headers=auth_headers
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data['cars']) >= 1
    for car_data in data['cars']:
        assert float(car_data['price']) <= max_price


def test_list_cars_no_results(client, auth_headers):
    response = client.get(
        '/api/v1/cars/?search=nonexistent', headers=auth_headers
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data['cars']) == 0


def test_list_cars_unauthorized(client):
    response = client.get('/api/v1/cars/')

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_get_car_success(client, auth_headers, car):
    response = client.get(f'/api/v1/cars/{car.id}', headers=auth_headers)

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['id'] == car.id
    assert data['model'] == car.model
    assert data['plate'] == car.plate
    assert 'brand' in data
    assert 'owner' in data


def test_get_car_not_found(client, auth_headers):
    response = client.get('/api/v1/cars/999', headers=auth_headers)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert 'Carro não encontrado' in response.json()['detail']


def test_get_car_not_owner(client, auth_headers, second_user_car):
    response = client.get(
        f'/api/v1/cars/{second_user_car.id}', headers=auth_headers
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        'Not enough permissions to access this car'
        in response.json()['detail']
    )


def test_get_car_unauthorized(client, car):
    response = client.get(f'/api/v1/cars/{car.id}')

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_update_car_success(client, auth_headers, car, second_brand):
    update_data = {
        'model': 'Updated Model',
        'color': 'Blue',
        'price': 55000.00,
        'brand_id': second_brand.id,
        'is_available': False,
    }

    response = client.put(
        f'/api/v1/cars/{car.id}', json=update_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['model'] == update_data['model']
    assert data['color'] == update_data['color']
    assert float(data['price']) == update_data['price']
    assert data['brand_id'] == update_data['brand_id']
    assert data['is_available'] == update_data['is_available']


def test_update_car_partial_update(client, auth_headers, car):
    original_model = car.model
    update_data = {'color': 'Red'}

    response = client.put(
        f'/api/v1/cars/{car.id}', json=update_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['model'] == original_model
    assert data['color'] == update_data['color']


@pytest.mark.asyncio
async def test_update_car_plate_duplicate(
    client, auth_headers, car, session, user, brand
):
    new_car = Car(
        model='Test Car',
        factory_year=2023,
        model_year=2023,
        color='Green',
        plate='DUPLICATE',
        fuel_type=FuelType.GASOLINE,
        transmission=TransmissionType.MANUAL,
        price=Decimal('30000.00'),
        brand_id=brand.id,
        owner_id=user.id,
    )
    session.add(new_car)
    await session.commit()
    await session.refresh(new_car)

    update_data = {'plate': 'DUPLICATE'}

    response = client.put(
        f'/api/v1/cars/{car.id}', json=update_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'Placa já está em uso' in response.json()['detail']


def test_update_car_same_plate(client, auth_headers, car):
    update_data = {'plate': car.plate, 'color': 'Yellow'}

    response = client.put(
        f'/api/v1/cars/{car.id}', json=update_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['plate'] == car.plate
    assert data['color'] == update_data['color']


def test_update_car_invalid_brand(client, auth_headers, car):
    update_data = {'brand_id': 999}

    response = client.put(
        f'/api/v1/cars/{car.id}', json=update_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'Marca não encontrada' in response.json()['detail']


def test_update_car_owner_ignored(client, auth_headers, car, second_user):
    update_data = {'owner_id': second_user.id, 'model': 'Updated Model'}

    response = client.put(
        f'/api/v1/cars/{car.id}', json=update_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['owner']['id'] != second_user.id
    assert data['model'] == update_data['model']


def test_update_car_not_found(client, auth_headers):
    update_data = {'model': 'Nonexistent'}

    response = client.put(
        '/api/v1/cars/999', json=update_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert 'Carro não encontrado' in response.json()['detail']


def test_update_car_not_owner(client, auth_headers, second_user_car):
    update_data = {'model': 'Unauthorized Update'}

    response = client.put(
        f'/api/v1/cars/{second_user_car.id}',
        json=update_data,
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        'Not enough permissions to access this car'
        in response.json()['detail']
    )


def test_update_car_unauthorized(client, car):
    update_data = {'model': 'Unauthorized'}

    response = client.put(f'/api/v1/cars/{car.id}', json=update_data)

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_delete_car_success(client, auth_headers, car):
    response = client.delete(f'/api/v1/cars/{car.id}', headers=auth_headers)

    assert response.status_code == HTTPStatus.NO_CONTENT

    get_response = client.get(f'/api/v1/cars/{car.id}', headers=auth_headers)
    assert get_response.status_code == HTTPStatus.NOT_FOUND


def test_delete_car_not_found(client, auth_headers):
    response = client.delete('/api/v1/cars/999', headers=auth_headers)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert 'Carro não encontrado' in response.json()['detail']


def test_delete_car_not_owner(client, auth_headers, second_user_car):
    response = client.delete(
        f'/api/v1/cars/{second_user_car.id}', headers=auth_headers
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        'Not enough permissions to access this car'
        in response.json()['detail']
    )


def test_delete_car_unauthorized(client, car):
    response = client.delete(f'/api/v1/cars/{car.id}')

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_list_cars_pagination_limits(client, auth_headers):
    response = client.get('/api/v1/cars/?limit=101', headers=auth_headers)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_list_cars_negative_offset(client, auth_headers):
    response = client.get('/api/v1/cars/?offset=-1', headers=auth_headers)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_list_cars_negative_price_filters(client, auth_headers):
    response = client.get(
        '/api/v1/cars/?min_price=-1000', headers=auth_headers
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    response = client.get(
        '/api/v1/cars/?max_price=-1000', headers=auth_headers
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_car_all_fuel_types(client, auth_headers, brand):
    fuel_types = [
        FuelType.GASOLINE,
        FuelType.ETHANOL,
        FuelType.FLEX,
        FuelType.DIESEL,
        FuelType.ELECTRIC,
        FuelType.HYBRID,
    ]

    for i, fuel_type in enumerate(fuel_types):
        car_data = {
            'model': f'Test Model {i}',
            'factory_year': 2023,
            'model_year': 2023,
            'color': 'Black',
            'plate': f'TEST{i:03d}',
            'fuel_type': fuel_type,
            'transmission': TransmissionType.MANUAL,
            'price': 40000.00,
            'brand_id': brand.id,
        }

        response = client.post(
            '/api/v1/cars/', json=car_data, headers=auth_headers
        )

        assert response.status_code == HTTPStatus.CREATED
        data = response.json()
        assert data['fuel_type'] == fuel_type


def test_create_car_all_transmission_types(client, auth_headers, brand):
    transmissions = [
        TransmissionType.MANUAL,
        TransmissionType.AUTOMATIC,
        TransmissionType.SEMI_AUTOMATIC,
        TransmissionType.CVT,
    ]

    for i, transmission in enumerate(transmissions):
        car_data = {
            'model': f'Transmission Test {i}',
            'factory_year': 2023,
            'model_year': 2023,
            'color': 'Blue',
            'plate': f'TRANS{i:02d}',
            'fuel_type': FuelType.GASOLINE,
            'transmission': transmission,
            'price': 35000.00,
            'brand_id': brand.id,
        }

        response = client.post(
            '/api/v1/cars/', json=car_data, headers=auth_headers
        )

        assert response.status_code == HTTPStatus.CREATED
        data = response.json()
        assert data['transmission'] == transmission


def test_create_car_duplicate_plate_error(client, auth_headers, brand):
    car_data = {
        'model': 'First Car',
        'factory_year': 2023,
        'model_year': 2023,
        'color': 'Red',
        'plate': 'DUPLI123',
        'fuel_type': 'gasoline',
        'transmission': 'manual',
        'price': 30000.00,
        'brand_id': brand.id,
    }

    first_response = client.post(
        '/api/v1/cars/', json=car_data, headers=auth_headers
    )
    assert first_response.status_code == HTTPStatus.CREATED

    car_data['model'] = 'Second Car'

    response = client.post(
        '/api/v1/cars/', json=car_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'Placa já está em uso' in response.json()['detail']


def test_create_car_brand_not_found_error(client, auth_headers):
    car_data = {
        'model': 'Test Car',
        'factory_year': 2023,
        'model_year': 2023,
        'color': 'Blue',
        'plate': 'NOBRAND123',
        'fuel_type': 'gasoline',
        'transmission': 'manual',
        'price': 30000.00,
        'brand_id': 99999,
    }

    response = client.post(
        '/api/v1/cars/', json=car_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'Marca não encontrada' in response.json()['detail']


def test_create_car_full_creation_flow(client, auth_headers, brand):
    car_data = {
        'model': 'Full Flow Test',
        'factory_year': 2023,
        'model_year': 2023,
        'color': 'Silver',
        'plate': 'FLOW123',
        'fuel_type': FuelType.FLEX,
        'transmission': TransmissionType.AUTOMATIC,
        'price': 45000.00,
        'description': 'Complete creation test',
        'is_available': True,
        'brand_id': brand.id,
    }

    response = client.post(
        '/api/v1/cars/', json=car_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data['model'] == car_data['model']
    assert data['plate'] == car_data['plate']
    assert data['brand_id'] == car_data['brand_id']
    assert 'id' in data
    assert 'brand' in data
    assert 'owner' in data


def test_list_cars_retrieve_actual_results(client, auth_headers):
    response = client.get('/api/v1/cars/', headers=auth_headers)

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert 'cars' in data
    assert 'offset' in data
    assert 'limit' in data
    assert data['offset'] == 0
    assert data['limit'] == 100


def test_get_car_not_found_specific_id(client, auth_headers):
    response = client.get('/api/v1/cars/12345', headers=auth_headers)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert 'Carro não encontrado' in response.json()['detail']


def test_get_car_ownership_verification_failed(
    client, auth_headers, second_user_car
):
    response = client.get(
        f'/api/v1/cars/{second_user_car.id}', headers=auth_headers
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        'Not enough permissions to access this car'
        in response.json()['detail']
    )


def test_update_car_not_found_error(client, auth_headers):
    update_data = {'model': 'Updated Model'}

    response = client.put(
        '/api/v1/cars/12345', json=update_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert 'Carro não encontrado' in response.json()['detail']


def test_update_car_plate_conflict_error(client, auth_headers, brand):
    car_data_1 = {
        'model': 'Car One',
        'factory_year': 2023,
        'model_year': 2023,
        'color': 'Red',
        'plate': 'PLATE001',
        'fuel_type': 'gasoline',
        'transmission': 'manual',
        'price': 30000.00,
        'brand_id': brand.id,
    }

    car_data_2 = {
        'model': 'Car Two',
        'factory_year': 2023,
        'model_year': 2023,
        'color': 'Blue',
        'plate': 'PLATE002',
        'fuel_type': 'gasoline',
        'transmission': 'manual',
        'price': 32000.00,
        'brand_id': brand.id,
    }

    response_1 = client.post(
        '/api/v1/cars/', json=car_data_1, headers=auth_headers
    )
    assert response_1.status_code == HTTPStatus.CREATED
    car1_id = response_1.json()['id']

    response_2 = client.post(
        '/api/v1/cars/', json=car_data_2, headers=auth_headers
    )
    assert response_2.status_code == HTTPStatus.CREATED

    update_data = {'plate': 'PLATE002'}

    response = client.put(
        f'/api/v1/cars/{car1_id}', json=update_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'Placa já está em uso' in response.json()['detail']


def test_update_car_brand_not_found_error(client, auth_headers, car):
    update_data = {'brand_id': 99999}

    response = client.put(
        f'/api/v1/cars/{car.id}', json=update_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'Marca não encontrada' in response.json()['detail']


def test_create_car_model_too_short_validation(client, auth_headers, brand):
    car_data = {
        'model': 'A',
        'factory_year': 2023,
        'model_year': 2023,
        'color': 'Red',
        'plate': 'VALID123',
        'fuel_type': 'gasoline',
        'transmission': 'manual',
        'price': 30000.00,
        'brand_id': brand.id,
    }

    response = client.post(
        '/api/v1/cars/', json=car_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    data = response.json()
    assert 'Modelo deve ter pelo menos 2 caracteres' in str(data['detail'])


def test_create_car_color_too_short_validation(client, auth_headers, brand):
    car_data = {
        'model': 'Valid Model',
        'factory_year': 2023,
        'model_year': 2023,
        'color': 'R',
        'plate': 'VALID123',
        'fuel_type': 'gasoline',
        'transmission': 'manual',
        'price': 30000.00,
        'brand_id': brand.id,
    }

    response = client.post(
        '/api/v1/cars/', json=car_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    data = response.json()
    assert 'Cor deve ter pelo menos 2 caracteres' in str(data['detail'])


def test_create_car_plate_too_short_validation(client, auth_headers, brand):
    car_data = {
        'model': 'Valid Model',
        'factory_year': 2023,
        'model_year': 2023,
        'color': 'Red',
        'plate': 'SHORT',
        'fuel_type': 'gasoline',
        'transmission': 'manual',
        'price': 30000.00,
        'brand_id': brand.id,
    }

    response = client.post(
        '/api/v1/cars/', json=car_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    data = response.json()
    assert 'Placa deve ter entre 7 e 10 caracteres' in str(data['detail'])


def test_create_car_plate_too_long_validation(client, auth_headers, brand):
    car_data = {
        'model': 'Valid Model',
        'factory_year': 2023,
        'model_year': 2023,
        'color': 'Red',
        'plate': 'TOOLONGPLATE',
        'fuel_type': 'gasoline',
        'transmission': 'manual',
        'price': 30000.00,
        'brand_id': brand.id,
    }

    response = client.post(
        '/api/v1/cars/', json=car_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    data = response.json()
    assert 'Placa deve ter entre 7 e 10 caracteres' in str(data['detail'])


def test_create_car_factory_year_too_old_validation(
    client, auth_headers, brand
):
    car_data = {
        'model': 'Valid Model',
        'factory_year': 1800,
        'model_year': 2023,
        'color': 'Red',
        'plate': 'VALID123',
        'fuel_type': 'gasoline',
        'transmission': 'manual',
        'price': 30000.00,
        'brand_id': brand.id,
    }

    response = client.post(
        '/api/v1/cars/', json=car_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    data = response.json()
    assert 'Ano deve estar entre 1900 e 2030' in str(data['detail'])


def test_create_car_model_year_too_new_validation(client, auth_headers, brand):
    car_data = {
        'model': 'Valid Model',
        'factory_year': 2023,
        'model_year': 2040,
        'color': 'Red',
        'plate': 'VALID123',
        'fuel_type': 'gasoline',
        'transmission': 'manual',
        'price': 30000.00,
        'brand_id': brand.id,
    }

    response = client.post(
        '/api/v1/cars/', json=car_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    data = response.json()
    assert 'Ano deve estar entre 1900 e 2030' in str(data['detail'])


def test_create_car_negative_price_validation(client, auth_headers, brand):
    car_data = {
        'model': 'Valid Model',
        'factory_year': 2023,
        'model_year': 2023,
        'color': 'Red',
        'plate': 'VALID123',
        'fuel_type': 'gasoline',
        'transmission': 'manual',
        'price': -1000.00,
        'brand_id': brand.id,
    }

    response = client.post(
        '/api/v1/cars/', json=car_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    data = response.json()
    assert 'Preço deve ser maior que zero' in str(data['detail'])


def test_create_car_zero_price_validation(client, auth_headers, brand):
    car_data = {
        'model': 'Valid Model',
        'factory_year': 2023,
        'model_year': 2023,
        'color': 'Red',
        'plate': 'VALID123',
        'fuel_type': 'gasoline',
        'transmission': 'manual',
        'price': 0.00,
        'brand_id': brand.id,
    }

    response = client.post(
        '/api/v1/cars/', json=car_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    data = response.json()
    assert 'Preço deve ser maior que zero' in str(data['detail'])


def test_update_car_model_too_short_validation(client, auth_headers, car):
    update_data = {'model': 'A'}

    response = client.put(
        f'/api/v1/cars/{car.id}', json=update_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    data = response.json()
    assert 'Modelo deve ter pelo menos 2 caracteres' in str(data['detail'])
