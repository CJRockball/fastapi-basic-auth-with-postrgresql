""" Database interaction hub."""

import os

from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from sqlalchemy.pool import NullPool

# Get Database_url from docker-compose environment
DATABASE_URL = os.environ.get("DATABASE_URL")

# Add poolclass=NullPool, otherwise tests fail 
# because it calls the engine multiple times
engine = create_async_engine(DATABASE_URL, echo=False, future=True, poolclass=NullPool,)


async def init_db():
    """ Create database if it doesn't exist.
    
    The method is not asyn so it runs in sync mode.
    For SQLModel, this will create the tables (but won't drop existing ones)
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


@asynccontextmanager
async def get_session() -> AsyncSession:
    """ Creates database connection.
    
    Ref: https://github.com/tiangolo/sqlmodel/issues/626
    """
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
