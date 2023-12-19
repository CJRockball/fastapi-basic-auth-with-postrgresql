from sqlmodel import SQLModel, Field

class UserBase(SQLModel):
    username: str
    hashed_password: str


class User(UserBase, table=True):
    id: int = Field(default=None, nullable=False, primary_key=True)


class UserCreate(SQLModel):
    username: str
    password: str
    pass

class UserOut(SQLModel):
    username: str
