from fastapi import HTTPException
from passlib.context import CryptContext
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.schemas.user import User, UserCreate
from app.database.db import get_session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



async def get_list():
    session: AsyncSession = get_session()
    async with session as s:
        result = await s.exec(select(User))
        db_users = result.all()
        if not db_users:
            HTTPException(status_code=404, detail=f"Users not found")
        result = [User(username=user.username, hashed_password=user.hashed_password, id=user.id) for user in db_users]
        return result


async def create_user(user: UserCreate):
    user.password = pwd_context.encrypt(user.password)

    try:
        session: AsyncSession = get_session()
        async with session as s:
            user = User(username=user.username, hashed_password=user.password)
            s.add(user)
            await s.commit()
            await s.refresh(user)
            return user        
    except:
        raise HTTPException(status_code=401, detail=f"Sorry, that username already exists.")
