from fastapi import HTTPException
from sqlmodel import select, and_
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.sql import text

from app.schemas.song import Song, SongCreate, SongUpdate, SongFilter
from app.database.db import get_session

import pandas as pd


async def get_songs() -> list[Song]:
    session: AsyncSession = get_session()
    async with session as s:
        result = await s.exec(select(Song).order_by(Song.id).limit(100))
        db_songs = result.all()
        if not db_songs:
            HTTPException(status_code=404, detail=f"Songs not found")
            
        result = [Song(name=song.name, artist=song.artist, id=song.id) for song in db_songs]
        return result


async def create_song(song: SongCreate) -> Song:
    try:
        session: AsyncSession = get_session()
        async with session as s:
            song = Song(name=song.name, artist=song.artist)
            s.add(song)
            await s.commit()
            await s.refresh(song)
            return song       
    except:
        raise HTTPException(status_code=401, detail=f"Sorry, cannot.")

    
async def upload_data(file):
    df = pd.read_csv(file)
    if df.shape[1] != 2:
        HTTPException(status_code=422, detail=f"Wrong table format")
        
    session: AsyncSession = get_session()
    async with session as s:    
        await s.run_sync(lambda session: session.bulk_insert_mappings(Song, df.to_dict(orient="records")))
        await s.commit()
    return df.shape


async def get_song(song_id:int) -> Song:
    session: AsyncSession = get_session()
    async with session as s:
        result = await s.exec(select(Song).where(Song.id == song_id))
        db_song = result.one()
        if not db_song:
            HTTPException(status_code=404, detail=f"Song {song_id} not found")
        return db_song


async def filter_songs_(song_filter:SongFilter) -> list[Song]:
    where_clause = []
    song_data = song_filter.model_dump(exclude_unset=True)
    for key, value in song_data.items():
        where_clause.append(text('Song.' + str(key) + '=\'' + str(value) + '\''))
    
    session: AsyncSession = get_session()
    async with session as s:
        stmt = select(Song)
        if len(where_clause) == 1:
            stmt = stmt.where(where_clause[0])
        elif len(where_clause) > 1:
            stmt = stmt.where(and_(*where_clause))

        result = await s.exec(stmt)
        db_songs = result.all()
        if not db_songs:
            HTTPException(status_code=404, detail=f"Songs not found")
            
        final_result = [Song(name=song.name, artist=song.artist, id=song.id) for song in db_songs]

        return final_result 


async def update_song_(song_id: int, song_update: SongUpdate) -> Song:
    session: AsyncSession = get_session()
    async with session as s:
        result = await s.exec(select(Song).where(Song.id == song_id))
        db_song = result.one()
        if not db_song:
            HTTPException(status_code=404, detail=f"Song {song_id} not found")
        
        song_data = song_update.model_dump(exclude_unset=True)
        for key, value in song_data.items():
            setattr(db_song, key, value)
        s.add(db_song)
        await s.commit()
        await s.refresh(db_song)
        return db_song



async def delete_song_(song_id:int) -> dict:
    session: AsyncSession = get_session()
    async with session as s:
        result = await s.exec(select(Song).where(Song.id == song_id))
        db_song = result.one()
        if not db_song:
            HTTPException(status_code=404, detail=f"Song {song_id} not found")
            
        await s.delete(db_song)
        await s.commit()
        return {"ok": True}



