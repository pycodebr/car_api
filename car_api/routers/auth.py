from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from car_api.core.database import get_session
from car_api.core.security import (
    authenticate_user,
    create_access_token,
    get_current_user,
)
from car_api.models.users import User
from car_api.schemas.auth import LoginRequest, Token

router = APIRouter()


@router.post(
    '/token',
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary='Gerar token de acesso',
)
async def token(
    login_data: LoginRequest, db: AsyncSession = Depends(get_session)
):
    user = await authenticate_user(login_data.email, login_data.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect email or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token = create_access_token(data={'sub': str(user.id)})

    return {'access_token': access_token, 'token_type': 'bearer'}


@router.post(
    '/refresh_token',
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary='Atualizar token de acesso',
)
async def refresh_token(current_user: User = Depends(get_current_user)):
    access_token = create_access_token(data={'sub': str(current_user.id)})

    return {'access_token': access_token, 'token_type': 'bearer'}
