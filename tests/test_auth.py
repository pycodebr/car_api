from datetime import datetime, timedelta, timezone
from http import HTTPStatus

import jwt
import pytest

from car_api.core.settings import Settings


def test_token_success(client, user, user_data):
    login_data = {
        'email': user_data['email'],
        'password': user_data['password'],
    }

    response = client.post('/api/v1/auth/token', json=login_data)

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'
    assert isinstance(data['access_token'], str)
    assert len(data['access_token']) > 0


def test_token_invalid_email(client, user_data):
    login_data = {
        'email': 'wrong@example.com',
        'password': user_data['password'],
    }

    response = client.post('/api/v1/auth/token', json=login_data)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert 'Incorrect email or password' in response.json()['detail']


def test_token_invalid_password(client, user, user_data):
    login_data = {'email': user_data['email'], 'password': 'wrongpassword'}

    response = client.post('/api/v1/auth/token', json=login_data)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert 'Incorrect email or password' in response.json()['detail']


def test_token_nonexistent_user(client):
    login_data = {
        'email': 'nonexistent@example.com',
        'password': 'anypassword',
    }

    response = client.post('/api/v1/auth/token', json=login_data)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert 'Incorrect email or password' in response.json()['detail']


def test_token_invalid_email_format(client):
    login_data = {'email': 'invalid-email', 'password': 'password123'}

    response = client.post('/api/v1/auth/token', json=login_data)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_token_password_too_short(client):
    login_data = {'email': 'test@example.com', 'password': '123'}

    response = client.post('/api/v1/auth/token', json=login_data)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    data = response.json()
    assert 'Senha deve ter pelo menos 6 caracteres' in str(data['detail'])


def test_token_missing_email(client):
    login_data = {'password': 'password123'}

    response = client.post('/api/v1/auth/token', json=login_data)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_token_missing_password(client):
    login_data = {'email': 'test@example.com'}

    response = client.post('/api/v1/auth/token', json=login_data)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_token_empty_request(client):
    response = client.post('/api/v1/auth/token', json={})

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_token_malformed_json(client):
    response = client.post(
        '/api/v1/auth/token',
        data='invalid json',
        headers={'Content-Type': 'application/json'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_refresh_token_success(client, auth_headers):
    response = client.post('/api/v1/auth/refresh_token', headers=auth_headers)

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'
    assert isinstance(data['access_token'], str)
    assert len(data['access_token']) > 0


def test_refresh_token_unauthorized(client):
    response = client.post('/api/v1/auth/refresh_token')

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_refresh_token_invalid_token(client):
    headers = {'Authorization': 'Bearer invalid_token'}
    response = client.post('/api/v1/auth/refresh_token', headers=headers)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert 'Could not validate credentials' in response.json()['detail']


def test_refresh_token_expired_token(client):
    settings = Settings()
    expired_data = {
        'sub': '1',
        'exp': datetime.now(timezone.utc) - timedelta(hours=1),
    }
    expired_token = jwt.encode(
        expired_data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    headers = {'Authorization': f'Bearer {expired_token}'}

    response = client.post('/api/v1/auth/refresh_token', headers=headers)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert 'Token has expired' in response.json()['detail']


def test_refresh_token_malformed_token(client):
    headers = {'Authorization': 'Bearer malformed.token.here'}
    response = client.post('/api/v1/auth/refresh_token', headers=headers)

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_refresh_token_missing_bearer_prefix(client, access_token):
    headers = {'Authorization': access_token}
    response = client.post('/api/v1/auth/refresh_token', headers=headers)

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_refresh_token_empty_authorization_header(client):
    headers = {'Authorization': ''}
    response = client.post('/api/v1/auth/refresh_token', headers=headers)

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_refresh_token_wrong_authorization_scheme(client, access_token):
    headers = {'Authorization': f'Basic {access_token}'}
    response = client.post('/api/v1/auth/refresh_token', headers=headers)

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_token_valid_jwt_payload(client, user, user_data):
    login_data = {
        'email': user_data['email'],
        'password': user_data['password'],
    }

    response = client.post('/api/v1/auth/token', json=login_data)

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    token = data['access_token']

    settings = Settings()
    payload = jwt.decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )

    assert 'sub' in payload
    assert payload['sub'] == str(user.id)
    assert 'exp' in payload

    exp_datetime = datetime.fromtimestamp(payload['exp'], timezone.utc)
    now = datetime.now(timezone.utc)
    assert exp_datetime > now
    assert exp_datetime <= now + timedelta(
        minutes=settings.JWT_EXPIRATION_MINUTES + 1
    )


def test_refresh_token_valid_jwt_payload(client, auth_headers, user):
    response = client.post('/api/v1/auth/refresh_token', headers=auth_headers)

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    token = data['access_token']

    settings = Settings()
    payload = jwt.decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )

    assert 'sub' in payload
    assert payload['sub'] == str(user.id)
    assert 'exp' in payload


@pytest.mark.asyncio
async def test_token_user_not_in_database_anymore(
    client, session, user, user_data
):
    login_data = {
        'email': user_data['email'],
        'password': user_data['password'],
    }

    await session.delete(user)
    await session.commit()

    response = client.post('/api/v1/auth/token', json=login_data)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert 'Incorrect email or password' in response.json()['detail']


@pytest.mark.asyncio
async def test_refresh_token_user_not_in_database_anymore(
    client, session, user, auth_headers
):
    await session.delete(user)
    await session.commit()

    response = client.post('/api/v1/auth/refresh_token', headers=auth_headers)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert 'Could not validate credentials' in response.json()['detail']


def test_token_with_wrong_algorithm(client):
    wrong_payload = {
        'sub': '1',
        'exp': datetime.now(timezone.utc) + timedelta(minutes=30),
    }
    wrong_token = jwt.encode(wrong_payload, 'wrong_secret', algorithm='HS256')
    headers = {'Authorization': f'Bearer {wrong_token}'}

    response = client.post('/api/v1/auth/refresh_token', headers=headers)

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_token_with_invalid_sub_format(client):
    settings = Settings()
    invalid_payload = {
        'sub': 'not_a_number',
        'exp': datetime.now(timezone.utc) + timedelta(minutes=30),
    }
    invalid_token = jwt.encode(
        invalid_payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    headers = {'Authorization': f'Bearer {invalid_token}'}

    response = client.post('/api/v1/auth/refresh_token', headers=headers)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert 'Could not validate credentials' in response.json()['detail']


def test_token_without_sub_claim(client):
    settings = Settings()
    no_sub_payload = {
        'exp': datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    no_sub_token = jwt.encode(
        no_sub_payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    headers = {'Authorization': f'Bearer {no_sub_token}'}

    response = client.post('/api/v1/auth/refresh_token', headers=headers)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert 'Could not validate credentials' in response.json()['detail']


def test_token_case_sensitivity(client, user, user_data):
    login_data = {
        'email': user_data['email'].upper(),
        'password': user_data['password'],
    }

    response = client.post('/api/v1/auth/token', json=login_data)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert 'Incorrect email or password' in response.json()['detail']


def test_token_password_case_sensitivity(client, user, user_data):
    login_data = {
        'email': user_data['email'],
        'password': user_data['password'].upper(),
    }

    response = client.post('/api/v1/auth/token', json=login_data)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert 'Incorrect email or password' in response.json()['detail']


def test_refresh_token_with_none_sub_claim(client):
    settings = Settings()
    payload_with_none_sub = {
        'sub': None,
        'exp': datetime.now(timezone.utc) + timedelta(minutes=30),
    }
    token_with_none_sub = jwt.encode(
        payload_with_none_sub,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    headers = {'Authorization': f'Bearer {token_with_none_sub}'}

    response = client.post('/api/v1/auth/refresh_token', headers=headers)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert 'Could not validate credentials' in response.json()['detail']


def test_refresh_token_with_type_error_sub(client):
    settings = Settings()
    payload_with_complex_sub = {
        'sub': {'invalid': 'object'},
        'exp': datetime.now(timezone.utc) + timedelta(minutes=30),
    }
    token_with_complex_sub = jwt.encode(
        payload_with_complex_sub,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    headers = {'Authorization': f'Bearer {token_with_complex_sub}'}

    response = client.post('/api/v1/auth/refresh_token', headers=headers)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert 'Could not validate credentials' in response.json()['detail']


def test_get_current_user_with_nonexistent_user_id(client):
    settings = Settings()
    nonexistent_user_payload = {
        'sub': '99999',
        'exp': datetime.now(timezone.utc) + timedelta(minutes=30),
    }
    token_nonexistent_user = jwt.encode(
        nonexistent_user_payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    headers = {'Authorization': f'Bearer {token_nonexistent_user}'}

    response = client.post('/api/v1/auth/refresh_token', headers=headers)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert 'Could not validate credentials' in response.json()['detail']
