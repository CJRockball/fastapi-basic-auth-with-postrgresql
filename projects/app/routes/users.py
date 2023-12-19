from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Dict

from app.schemas.user import User, UserCreate, UserOut
from app.database.db import get_session
from app.crud.users import create_user
from app.auth.users import validate_user
from app.auth.jwthandler import (
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

from datetime import timedelta



router = APIRouter()

@router.get("/users", response_model=list[User])
async def get_users():
    session: AsyncSession = get_session()
    async with session as s:
        result = await s.execute(select(User))
        db_users = result.scalars().all()
        if not db_users:
            HTTPException(status_code=404, detail=f"Users not found")
        result = [User(username=user.username, hashed_password=user.hashed_password, id=user.id) for user in db_users]
    
    return result


@router.post("/simple_add", response_model=User)
async def add_user():
    session: AsyncSession = get_session()
    async with session as s:
        user = User(username=user.username, hashed_password=user.hashed_password)
        s.add(user)
        await s.commit()
        await s.refresh(user)
        if not user:
            HTTPException(status_code=404, detail=f"User not found")
    return user


@router.post('/register', response_model=User)
async def register(user:UserCreate):
    result = await create_user(user)
    return result


@router.post("/login")
async def login(user: OAuth2PasswordRequestForm = Depends()) -> Dict[str, str]:
    user = await validate_user(user)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    token = jsonable_encoder(access_token)
    content = {"message": "You've successfully logged in. Welcome back!"}
    response = JSONResponse(content=content)
    response.set_cookie(
        "Authorization",
        value=f"Bearer {token}",
        httponly=True,
        max_age=1800,
        expires=1800,
        samesite="Lax",
        secure=False,
    )

    return response


@router.get("/whoami", response_model=UserOut)
async def read_users_me(current_user: UserOut = Depends(get_current_user)):
    return current_user


@router.get('/logout')
async def logout() -> Dict[str, str]:
    response = RedirectResponse(url='/ping')
    response.delete_cookie("Authorization")
    return response
