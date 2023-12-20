from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict

from app.schemas.user import User, UserCreate, UserOut
from app.crud.users import create_user, get_users
from app.auth.users import validate_user
from app.auth.jwthandler import (
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

from datetime import timedelta


router = APIRouter()


@router.get("/get_users", response_model=list[User])
async def get_list_users() -> list[User]:
    """ Get list of users."""
    result = await get_users()
    return result


@router.post('/register', response_model=User)
async def register(user:UserCreate) -> User:
    """ Add one new user."""
    result = await create_user(user)
    return result


@router.post("/login")
async def login(user: OAuth2PasswordRequestForm = Depends()) -> Dict[str, str]:
    """ Log in."""
    # Check username and password
    user = await validate_user(user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    token = jsonable_encoder(access_token)
    content = {"message": "You've successfully logged in. Welcome back!"}
    response = JSONResponse(content=content)
    # Set access token
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
async def read_users_me(current_user: UserOut = Depends(get_current_user)) -> UserOut:
    """ Returns current user."""
    return current_user


@router.get('/logout')
async def logout() -> Dict[str, str]:
    """ Log out by deleting cookie."""
    response = RedirectResponse(url='/ping')
    response.delete_cookie("Authorization")
    return response
