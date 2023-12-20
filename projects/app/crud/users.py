""" Provides functionality to user routes."""

from fastapi import HTTPException
from passlib.context import CryptContext
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.schemas.user import User, UserCreate
from app.database.db import get_session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_users() -> list[User]:
    """ Connects to database and returns list of usernames, hashed passwords and user id.
    
    Returns
    -------
    result : List of type User
        
    """
    # Create async session with database
    async with get_session() as s:
        # Execute database operations within the context manager
        # Selects all users from the database
        result = await s.exec(select(User))
        db_users = result.all()
        # If the database is empty an error is returned
        if not db_users:
            HTTPException(status_code=404, detail=f"No users in database")
        # The db_user object is an iterable. Go through and collect in a list.
        result = [User(username=user.username, hashed_password=user.hashed_password, id=user.id) for user in db_users]
        return result


async def create_user(user: UserCreate) -> User:
    """ Connects to database to add user.
    
    Returns
    -------
    user : type User 
    """
    user.password = pwd_context.encrypt(user.password)

    try:
        async with get_session() as s:
            user = User(username=user.username, hashed_password=user.password)
            s.add(user)
            await s.commit()
            # Refresh to return the inserted user.
            await s.refresh(user)
            return user
    # Return error if something goes wrong
    except:
        raise HTTPException(status_code=401, detail=f"Something went wrong.")
