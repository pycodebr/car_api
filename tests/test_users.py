

def test_create_user_success(client):
    response = client.post(
        '/api/v1/users/',
        json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
        },
    )

    assert response.status_code == 201
    user_data = response.json()
    assert user_data['username'] == 'newuser'
    assert user_data['email'] == 'newuser@example.com'
    assert user_data['id'] == 1
    assert 'created_at' in user_data
    assert 'updated_at' in user_data


def test_create_user_username_too_short(client):
    response = client.post(
        '/api/v1/users/',
        json={
            'username': 'ab',
            'email': 'test@example.com',
            'password': 'password123',
        },
    )

    assert response.status_code == 422
    error_data = response.json()
    assert 'Username deve ter pelo menos 3 caracteres' in str(error_data)


def test_create_user_password_too_short(client):
    response = client.post(
        '/api/v1/users/',
        json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': '12345',
        },
    )

    assert response.status_code == 422
    error_data = response.json()
    assert 'Senha deve ter pelo menos 6 caracteres' in str(error_data)


def test_create_user_invalid_email(client):
    response = client.post(
        '/api/v1/users/',
        json={
            'username': 'testuser',
            'email': 'invalid-email',
            'password': 'password123',
        },
    )

    assert response.status_code == 422


def test_create_user_duplicate_username(client, user):
    response = client.post(
        '/api/v1/users/',
        json={
            'username': user.username,
            'email': 'different@example.com',
            'password': 'password123',
        },
    )

    assert response.status_code == 400
    error_data = response.json()
    assert error_data['detail'] == 'Username já está em uso'


def test_create_user_duplicate_email(client, user):
    response = client.post(
        '/api/v1/users/',
        json={
            'username': 'differentuser',
            'email': user.email,
            'password': 'password123',
        },
    )

    assert response.status_code == 400
    error_data = response.json()
    assert error_data['detail'] == 'Email já está em uso'


def test_list_users_empty(client):
    response = client.get('/api/v1/users/')

    assert response.status_code == 200
    data = response.json()
    assert data['users'] == []
    assert data['offset'] == 0
    assert data['limit'] == 100


def test_list_users_with_users(client, user, second_user):
    response = client.get('/api/v1/users/')

    assert response.status_code == 200
    data = response.json()
    assert len(data['users']) == 2
    assert data['offset'] == 0
    assert data['limit'] == 100

    usernames = [u['username'] for u in data['users']]
    assert user.username in usernames
    assert second_user.username in usernames


def test_list_users_with_pagination(client, user, second_user):
    response = client.get('/api/v1/users/?offset=1&limit=1')

    assert response.status_code == 200
    data = response.json()
    assert len(data['users']) == 1
    assert data['offset'] == 1
    assert data['limit'] == 1


def test_list_users_search_by_username(client, user, second_user):
    response = client.get(f'/api/v1/users/?search={user.username[:4]}')

    assert response.status_code == 200
    data = response.json()
    assert len(data['users']) == 1
    assert data['users'][0]['username'] == user.username


def test_list_users_search_by_email(client, user, second_user):
    response = client.get(f'/api/v1/users/?search={user.email[:4]}')

    assert response.status_code == 200
    data = response.json()
    assert len(data['users']) == 1
    assert data['users'][0]['email'] == user.email


def test_list_users_search_no_results(client, user):
    response = client.get('/api/v1/users/?search=nonexistent')

    assert response.status_code == 200
    data = response.json()
    assert len(data['users']) == 0


def test_list_users_invalid_offset(client):
    response = client.get('/api/v1/users/?offset=-1')

    assert response.status_code == 422


def test_list_users_invalid_limit(client):
    response = client.get('/api/v1/users/?limit=0')

    assert response.status_code == 422


def test_list_users_limit_exceeds_maximum(client):
    response = client.get('/api/v1/users/?limit=101')

    assert response.status_code == 422


def test_get_user_success(client, user):
    response = client.get(f'/api/v1/users/{user.id}')

    assert response.status_code == 200
    user_data = response.json()
    assert user_data['id'] == user.id
    assert user_data['username'] == user.username
    assert user_data['email'] == user.email
    assert 'created_at' in user_data
    assert 'updated_at' in user_data


def test_get_user_not_found(client):
    response = client.get('/api/v1/users/999')

    assert response.status_code == 404
    error_data = response.json()
    assert error_data['detail'] == 'Usuário não encontrado'


def test_update_user_success(client, user, auth_headers):
    response = client.put(
        f'/api/v1/users/{user.id}',
        json={'username': 'updateduser'},
        headers=auth_headers,
    )

    assert response.status_code == 200
    user_data = response.json()
    assert user_data['username'] == 'updateduser'
    assert user_data['email'] == user.email


def test_update_user_email(client, user, auth_headers):
    response = client.put(
        f'/api/v1/users/{user.id}',
        json={'email': 'updated@example.com'},
        headers=auth_headers,
    )

    assert response.status_code == 200
    user_data = response.json()
    assert user_data['email'] == 'updated@example.com'


def test_update_user_password(client, user, auth_headers):
    response = client.put(
        f'/api/v1/users/{user.id}',
        json={'password': 'newpassword123'},
        headers=auth_headers,
    )

    assert response.status_code == 200
    user_data = response.json()
    assert user_data['username'] == user.username


def test_update_user_all_fields(client, user, auth_headers):
    response = client.put(
        f'/api/v1/users/{user.id}',
        json={
            'username': 'fullyupdated',
            'email': 'fully@example.com',
            'password': 'newpassword123',
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    user_data = response.json()
    assert user_data['username'] == 'fullyupdated'
    assert user_data['email'] == 'fully@example.com'


def test_update_user_no_auth(client, user):
    response = client.put(
        f'/api/v1/users/{user.id}',
        json={'username': 'updateduser'},
    )

    assert response.status_code == 403


def test_update_user_not_found(client, auth_headers):
    response = client.put(
        '/api/v1/users/999',
        json={'username': 'updateduser'},
        headers=auth_headers,
    )

    assert response.status_code == 404
    error_data = response.json()
    assert error_data['detail'] == 'Usuário não encontrado'


def test_update_user_username_too_short(client, user, auth_headers):
    response = client.put(
        f'/api/v1/users/{user.id}',
        json={'username': 'ab'},
        headers=auth_headers,
    )

    assert response.status_code == 422
    error_data = response.json()
    assert 'Username deve ter pelo menos 3 caracteres' in str(error_data)


def test_update_user_password_too_short(client, user, auth_headers):
    response = client.put(
        f'/api/v1/users/{user.id}',
        json={'password': '12345'},
        headers=auth_headers,
    )

    assert response.status_code == 422
    error_data = response.json()
    assert 'Senha deve ter pelo menos 6 caracteres' in str(error_data)


def test_update_user_invalid_email(client, user, auth_headers):
    response = client.put(
        f'/api/v1/users/{user.id}',
        json={'email': 'invalid-email'},
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_update_user_duplicate_username(
    client, user, second_user, auth_headers
):
    response = client.put(
        f'/api/v1/users/{user.id}',
        json={'username': second_user.username},
        headers=auth_headers,
    )

    assert response.status_code == 400
    error_data = response.json()
    assert error_data['detail'] == 'Username já está em uso'


def test_update_user_duplicate_email(client, user, second_user, auth_headers):
    response = client.put(
        f'/api/v1/users/{user.id}',
        json={'email': second_user.email},
        headers=auth_headers,
    )

    assert response.status_code == 400
    error_data = response.json()
    assert error_data['detail'] == 'Email já está em uso'


def test_update_user_same_username(client, user, auth_headers):
    response = client.put(
        f'/api/v1/users/{user.id}',
        json={'username': user.username},
        headers=auth_headers,
    )

    assert response.status_code == 200
    user_data = response.json()
    assert user_data['username'] == user.username


def test_update_user_same_email(client, user, auth_headers):
    response = client.put(
        f'/api/v1/users/{user.id}',
        json={'email': user.email},
        headers=auth_headers,
    )

    assert response.status_code == 200
    user_data = response.json()
    assert user_data['email'] == user.email


def test_update_user_empty_payload(client, user, auth_headers):
    response = client.put(
        f'/api/v1/users/{user.id}',
        json={},
        headers=auth_headers,
    )

    assert response.status_code == 200
    user_data = response.json()
    assert user_data['username'] == user.username
    assert user_data['email'] == user.email


def test_delete_user_success(client, user, auth_headers):
    response = client.delete(
        f'/api/v1/users/{user.id}',
        headers=auth_headers,
    )

    assert response.status_code == 204

    get_response = client.get(f'/api/v1/users/{user.id}')
    assert get_response.status_code == 404


def test_delete_user_no_auth(client, user):
    response = client.delete(f'/api/v1/users/{user.id}')

    assert response.status_code == 403


def test_delete_user_not_found(client, auth_headers):
    response = client.delete(
        '/api/v1/users/999',
        headers=auth_headers,
    )

    assert response.status_code == 404
    error_data = response.json()
    assert error_data['detail'] == 'Usuário não encontrado'


def test_create_user_missing_fields(client):
    response = client.post(
        '/api/v1/users/',
        json={
            'username': 'test',
        },
    )

    assert response.status_code == 422


def test_create_user_empty_fields(client):
    response = client.post(
        '/api/v1/users/',
        json={
            'username': '',
            'email': '',
            'password': '',
        },
    )

    assert response.status_code == 422


def test_list_users_case_insensitive_search(client, user):
    response = client.get(f'/api/v1/users/?search={user.username.upper()}')

    assert response.status_code == 200
    data = response.json()
    assert len(data['users']) == 1
    assert data['users'][0]['username'] == user.username


def test_list_users_partial_email_search(client, user):
    email_part = user.email.split('@')[0]
    response = client.get(f'/api/v1/users/?search={email_part}')

    assert response.status_code == 200
    data = response.json()
    assert len(data['users']) == 1
    assert data['users'][0]['email'] == user.email


def test_update_user_partial_fields(client, user, auth_headers):
    original_email = user.email
    response = client.put(
        f'/api/v1/users/{user.id}',
        json={'username': 'partialupdate'},
        headers=auth_headers,
    )

    assert response.status_code == 200
    user_data = response.json()
    assert user_data['username'] == 'partialupdate'
    assert user_data['email'] == original_email


def test_update_user_only_password(client, user, auth_headers):
    original_username = user.username
    original_email = user.email

    response = client.put(
        f'/api/v1/users/{user.id}',
        json={'password': 'onlynewpassword'},
        headers=auth_headers,
    )

    assert response.status_code == 200
    user_data = response.json()
    assert user_data['username'] == original_username
    assert user_data['email'] == original_email
