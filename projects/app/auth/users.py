from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext

from sqlmodel import select
from app.schemas.user import User
from app.database.db import get_session
from sqlmodel.ext.asyncio.session import AsyncSession

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(user_name: str):
    session: AsyncSession = get_session()
    async with session as s:
        result = await s.exec(select(User).where(User.username == user_name))
        users = result.first()
        return users


async def validate_user(user: OAuth2PasswordRequestForm = Depends()):
    db_user = await get_user(user.username)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    return db_user
