from http import HTTPStatus

import pytest


def test_create_brand_success(client, auth_headers):
    brand_data = {
        'name': 'Volkswagen',
        'description': 'German automotive manufacturer',
        'is_active': True,
    }

    response = client.post(
        '/api/v1/brands/', json=brand_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data['name'] == brand_data['name']
    assert data['description'] == brand_data['description']
    assert data['is_active'] == brand_data['is_active']
    assert 'id' in data
    assert 'created_at' in data
    assert 'updated_at' in data


def test_create_brand_without_description(client, auth_headers):
    brand_data = {'name': 'BMW', 'is_active': True}

    response = client.post(
        '/api/v1/brands/', json=brand_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data['name'] == brand_data['name']
    assert data['description'] is None
    assert data['is_active'] == brand_data['is_active']


def test_create_brand_with_default_active(client, auth_headers):
    brand_data = {'name': 'Audi'}

    response = client.post(
        '/api/v1/brands/', json=brand_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data['name'] == brand_data['name']
    assert data['is_active'] is True


def test_create_brand_duplicate_name(client, auth_headers, brand):
    brand_data = {'name': brand.name, 'description': 'Different description'}

    response = client.post(
        '/api/v1/brands/', json=brand_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'Nome da marca já está em uso' in response.json()['detail']


def test_create_brand_name_too_short(client, auth_headers):
    brand_data = {'name': 'A'}

    response = client.post(
        '/api/v1/brands/', json=brand_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    data = response.json()
    assert 'Nome da marca deve ter pelo menos 2 caracteres' in str(
        data['detail']
    )


def test_create_brand_name_with_spaces_only(client, auth_headers):
    brand_data = {'name': '   '}

    response = client.post(
        '/api/v1/brands/', json=brand_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_brand_name_trimmed(client, auth_headers):
    brand_data = {'name': '  Mercedes  '}

    response = client.post(
        '/api/v1/brands/', json=brand_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data['name'] == 'Mercedes'


def test_create_brand_unauthorized(client):
    brand_data = {'name': 'Ford'}

    response = client.post('/api/v1/brands/', json=brand_data)

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_create_brand_invalid_token(client):
    brand_data = {'name': 'Ford'}
    headers = {'Authorization': 'Bearer invalid_token'}

    response = client.post('/api/v1/brands/', json=brand_data, headers=headers)

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_list_brands_success(client, auth_headers, brand, second_brand):
    response = client.get('/api/v1/brands/', headers=auth_headers)

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert 'brands' in data
    assert 'offset' in data
    assert 'limit' in data
    assert data['offset'] == 0
    assert data['limit'] == 100
    assert len(data['brands']) == 2

    brand_names = [b['name'] for b in data['brands']]
    assert brand.name in brand_names
    assert second_brand.name in brand_names


def test_list_brands_with_pagination(
    client, auth_headers, brand, second_brand
):
    response = client.get(
        '/api/v1/brands/?offset=1&limit=1', headers=auth_headers
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['offset'] == 1
    assert data['limit'] == 1
    assert len(data['brands']) == 1


def test_list_brands_with_search(client, auth_headers, brand):
    response = client.get(
        f'/api/v1/brands/?search={brand.name}', headers=auth_headers
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data['brands']) == 1
    assert data['brands'][0]['name'] == brand.name


def test_list_brands_with_search_case_insensitive(client, auth_headers, brand):
    search_term = brand.name.upper()
    response = client.get(
        f'/api/v1/brands/?search={search_term}', headers=auth_headers
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data['brands']) == 1
    assert data['brands'][0]['name'] == brand.name


def test_list_brands_with_search_no_results(client, auth_headers):
    response = client.get(
        '/api/v1/brands/?search=nonexistent', headers=auth_headers
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data['brands']) == 0


@pytest.mark.asyncio
async def test_list_brands_filter_by_active(
    client, auth_headers, session, brand
):
    brand.is_active = False
    session.add(brand)
    await session.commit()

    response = client.get(
        '/api/v1/brands/?is_active=true', headers=auth_headers
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    brand_names = [b['name'] for b in data['brands']]
    assert brand.name not in brand_names


@pytest.mark.asyncio
async def test_list_brands_filter_by_inactive(
    client, auth_headers, session, brand
):
    brand.is_active = False
    session.add(brand)
    await session.commit()

    response = client.get(
        '/api/v1/brands/?is_active=false', headers=auth_headers
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data['brands']) >= 1
    brand_names = [b['name'] for b in data['brands']]
    assert brand.name in brand_names


def test_list_brands_unauthorized(client):
    response = client.get('/api/v1/brands/')

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_get_brand_success(client, auth_headers, brand):
    response = client.get(f'/api/v1/brands/{brand.id}', headers=auth_headers)

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['id'] == brand.id
    assert data['name'] == brand.name
    assert data['description'] == brand.description
    assert data['is_active'] == brand.is_active
    assert 'created_at' in data
    assert 'updated_at' in data


def test_get_brand_not_found(client, auth_headers):
    response = client.get('/api/v1/brands/999', headers=auth_headers)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert 'Marca não encontrada' in response.json()['detail']


def test_get_brand_unauthorized(client, brand):
    response = client.get(f'/api/v1/brands/{brand.id}')

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_update_brand_success(client, auth_headers, brand):
    update_data = {
        'name': 'Toyota Updated',
        'description': 'Updated description',
        'is_active': False,
    }

    response = client.put(
        f'/api/v1/brands/{brand.id}', json=update_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['id'] == brand.id
    assert data['name'] == update_data['name']
    assert data['description'] == update_data['description']
    assert data['is_active'] == update_data['is_active']


def test_update_brand_partial_update(client, auth_headers, brand):
    original_description = brand.description
    update_data = {'name': 'Toyota Partial'}

    response = client.put(
        f'/api/v1/brands/{brand.id}', json=update_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['name'] == update_data['name']
    assert data['description'] == original_description


def test_update_brand_name_duplicate(
    client, auth_headers, brand, second_brand
):
    update_data = {'name': second_brand.name}

    response = client.put(
        f'/api/v1/brands/{brand.id}', json=update_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'Nome da marca já está em uso' in response.json()['detail']


def test_update_brand_same_name(client, auth_headers, brand):
    update_data = {'name': brand.name, 'description': 'New description'}

    response = client.put(
        f'/api/v1/brands/{brand.id}', json=update_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['name'] == brand.name
    assert data['description'] == update_data['description']


def test_update_brand_name_too_short(client, auth_headers, brand):
    update_data = {'name': 'X'}

    response = client.put(
        f'/api/v1/brands/{brand.id}', json=update_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_update_brand_name_trimmed(client, auth_headers, brand):
    update_data = {'name': '  Updated Name  '}

    response = client.put(
        f'/api/v1/brands/{brand.id}', json=update_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['name'] == 'Updated Name'


def test_update_brand_not_found(client, auth_headers):
    update_data = {'name': 'Nonexistent'}

    response = client.put(
        '/api/v1/brands/999', json=update_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert 'Marca não encontrada' in response.json()['detail']


def test_update_brand_unauthorized(client, brand):
    update_data = {'name': 'Unauthorized'}

    response = client.put(f'/api/v1/brands/{brand.id}', json=update_data)

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_delete_brand_success(client, auth_headers, brand):
    response = client.delete(
        f'/api/v1/brands/{brand.id}', headers=auth_headers
    )

    assert response.status_code == HTTPStatus.NO_CONTENT

    get_response = client.get(
        f'/api/v1/brands/{brand.id}', headers=auth_headers
    )
    assert get_response.status_code == HTTPStatus.NOT_FOUND


def test_delete_brand_with_cars(client, auth_headers, brand, car):
    response = client.delete(
        f'/api/v1/brands/{brand.id}', headers=auth_headers
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert (
        'Não é possível deletar marca que possui carros associados'
        in response.json()['detail']
    )


def test_delete_brand_not_found(client, auth_headers):
    response = client.delete('/api/v1/brands/999', headers=auth_headers)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert 'Marca não encontrada' in response.json()['detail']


def test_delete_brand_unauthorized(client, brand):
    response = client.delete(f'/api/v1/brands/{brand.id}')

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_list_brands_pagination_limits(client, auth_headers):
    response = client.get('/api/v1/brands/?limit=101', headers=auth_headers)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_list_brands_negative_offset(client, auth_headers):
    response = client.get('/api/v1/brands/?offset=-1', headers=auth_headers)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_list_brands_zero_limit(client, auth_headers):
    response = client.get('/api/v1/brands/?limit=0', headers=auth_headers)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_brand_without_existing_brands(client, auth_headers):
    brand_data = {
        'name': 'NewBrand',
        'description': 'A completely new brand',
        'is_active': True,
    }

    response = client.post(
        '/api/v1/brands/', json=brand_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data['name'] == brand_data['name']
    assert data['description'] == brand_data['description']
    assert data['is_active'] == brand_data['is_active']
    assert 'id' in data


def test_get_brand_by_id_not_found_specific_id(client, auth_headers):
    response = client.get('/api/v1/brands/12345', headers=auth_headers)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert 'Marca não encontrada' in response.json()['detail']


def test_update_brand_not_found_specific_id(client, auth_headers):
    update_data = {'name': 'Updated Brand'}

    response = client.put(
        '/api/v1/brands/12345', json=update_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert 'Marca não encontrada' in response.json()['detail']


def test_update_brand_name_conflict_with_existing(client, auth_headers):
    brand_data = {
        'name': 'FirstBrand',
        'description': 'First brand',
        'is_active': True,
    }

    first_response = client.post(
        '/api/v1/brands/', json=brand_data, headers=auth_headers
    )
    assert first_response.status_code == HTTPStatus.CREATED
    first_brand_id = first_response.json()['id']

    second_brand_data = {
        'name': 'SecondBrand',
        'description': 'Second brand',
        'is_active': True,
    }

    second_response = client.post(
        '/api/v1/brands/', json=second_brand_data, headers=auth_headers
    )
    assert second_response.status_code == HTTPStatus.CREATED

    update_data = {'name': 'SecondBrand'}

    response = client.put(
        f'/api/v1/brands/{first_brand_id}',
        json=update_data,
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'Nome da marca já está em uso' in response.json()['detail']


def test_delete_brand_not_found_specific_id(client, auth_headers):
    response = client.delete('/api/v1/brands/12345', headers=auth_headers)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert 'Marca não encontrada' in response.json()['detail']


def test_delete_brand_with_associated_cars_constraint(client, auth_headers):
    brand_data = {
        'name': 'BrandWithCars',
        'description': 'Brand that will have cars',
        'is_active': True,
    }

    brand_response = client.post(
        '/api/v1/brands/', json=brand_data, headers=auth_headers
    )
    assert brand_response.status_code == HTTPStatus.CREATED
    brand_id = brand_response.json()['id']

    car_data = {
        'model': 'TestModel',
        'factory_year': 2023,
        'model_year': 2023,
        'color': 'Red',
        'plate': 'TEST123',
        'fuel_type': 'flex',
        'transmission': 'manual',
        'price': 30000.00,
        'description': 'Test car',
        'is_available': True,
        'brand_id': brand_id,
    }

    car_response = client.post(
        '/api/v1/cars/', json=car_data, headers=auth_headers
    )
    assert car_response.status_code == HTTPStatus.CREATED

    response = client.delete(
        f'/api/v1/brands/{brand_id}', headers=auth_headers
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert (
        'Não é possível deletar marca que possui carros associados'
        in response.json()['detail']
    )


def test_list_brands_actual_retrieval(client, auth_headers):
    brand_data = {
        'name': 'ListTestBrand',
        'description': 'Brand for testing list',
        'is_active': True,
    }

    create_response = client.post(
        '/api/v1/brands/', json=brand_data, headers=auth_headers
    )
    assert create_response.status_code == HTTPStatus.CREATED

    response = client.get('/api/v1/brands/', headers=auth_headers)

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert 'brands' in data
    assert len(data['brands']) >= 1

    brand_names = [b['name'] for b in data['brands']]
    assert 'ListTestBrand' in brand_names


def test_update_brand_with_refresh_after_commit(client, auth_headers):
    brand_data = {
        'name': 'UpdateTestBrand',
        'description': 'Brand for update testing',
        'is_active': True,
    }

    create_response = client.post(
        '/api/v1/brands/', json=brand_data, headers=auth_headers
    )
    assert create_response.status_code == HTTPStatus.CREATED
    brand_id = create_response.json()['id']

    update_data = {'description': 'Updated description for testing refresh'}

    response = client.put(
        f'/api/v1/brands/{brand_id}', json=update_data, headers=auth_headers
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['description'] == update_data['description']
    assert data['name'] == brand_data['name']
