from fastapi import FastAPI

from app.database.db import init_db
from app.routes import users, songs

from fastapi.middleware.cors import CORSMiddleware 


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8004"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router, tags=['User'])
app.include_router(songs.router, tags=['Song'])

@app.on_event('startup')
async def on_startup():
    await init_db()


@app.get("/ping")
async def pong():
    return {"pingu": "pongu!"}


