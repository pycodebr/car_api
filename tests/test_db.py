import pytest
from sqlalchemy import select

from car_api.models import User


@pytest.mark.asyncio
async def test_create_user(session):
    new_user = User(
        username='pycode',
        password='secret',
        email='teste@test.com',
    )
    session.add(new_user)
    await session.commit()

    user = await session.scalar(
        select(User).where(User.email == 'teste@test.com')
    )

    new_user_data = {
        'id': user.id,
        'username': user.username,
        'password': user.password,
        'email': user.email,
    }

    assert new_user_data == {
        'id': 1,
        'username': 'pycode',
        'password': 'secret',
        'email': 'teste@test.com',
    }
