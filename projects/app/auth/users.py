from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext

from sqlmodel import select
from app.schemas.user import User
from app.database.db import get_session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(user_name: str) -> User:
    """ Return user from database.
    
    Parameters
    ---------
    user_name: str
        Name of user
        
    Returns
    -------
    users: User
        Returns the database post on user_name
    
    """
    async with get_session() as s:
        result = await s.exec(select(User).where(User.username == user_name))
        users = result.first()
        return users


async def validate_user(user:OAuth2PasswordRequestForm) -> User:
    """ Check user name against database.
    
    Parameter
    ---------
    user: OAuth2PasswordRequestForm
        
    Returns
    ------
    db_user: User
        returns the user from database
    """
    # Get user in database
    db_user = await get_user(user.username)
    # If there no user return error
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    # If the supplied password doesn't match the database password 
    # return error
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    return db_user
