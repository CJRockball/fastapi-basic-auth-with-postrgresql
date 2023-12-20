""" Functionality for songs database."""

from fastapi import HTTPException
from sqlmodel import select, and_
from sqlalchemy.sql import text

from app.schemas.song import Song, SongCreate, SongUpdate, SongFilter
from app.database.db import get_session

import pandas as pd
import numpy as np

async def get_songs() -> list[Song]:
    """ Gets the top 100 posts in the songs database and returns sorted by id.
    
    Returns
    -------
    result : List of type Song
    
    """
    async with get_session() as s:
        # Search the Song database, return the top 100 results sorted by id
        result = await s.exec(select(Song).order_by(Song.id).limit(100))
        db_songs = result.all()
        # If there are no songs return error
        if not db_songs:
            HTTPException(status_code=404, detail=f"Songs not found")
        # db_songs is an iterator. Go through and return a list
        result = [Song(name=song.name, artist=song.artist, id=song.id) for song in db_songs]
        return result


async def create_song(song: SongCreate) -> Song:
    """ Insert a song into the Song database
    
    Returns
    -------
    song : type Song
    
    """
    try:
        async with get_session() as s:
            song = Song(name=song.name, artist=song.artist)
            s.add(song)
            await s.commit()
            # Referesh to get the inserted result
            await s.refresh(song)
            return song
    # Return an error if something goes wrong  
    except:
        raise HTTPException(status_code=401, detail=f"Sorry, cannot.")

    
async def upload_data(file) -> np.ndarray:
    """ Insert a csv file of songs into the Song database.
    
    Use this function to populate the database. Datafile should have two columns: "name" and "artist"
    
    Parameters
    ----------
    file : .csv from user
    
    Returns
    -------
    df.shape : 2x1 array
    
    """
    # Convert to dict via dataframe
    df = pd.read_csv(file)
    data_dict = df.to_dict(orient="records")
    # Input check, if data doesn't have two columns an error is raised
    if df.shape[1] != 2:
        HTTPException(status_code=422, detail=f"Wrong table format")
    # Connect to database and bulk insert data    
    async with get_session() as s:    
        await s.run_sync(lambda session: session.bulk_insert_mappings(Song, data_dict))
        await s.commit()
    return df.shape


async def get_song(song_id:int) -> Song:
    """ Returns one song from database by id.
    
    Returns
    -------
    db_song : type Song
    
    """
    async with get_session() as s:
        result = await s.exec(select(Song).where(Song.id == song_id))
        db_song = result.one()
        # Return error if no entry with that id
        if not db_song:
            HTTPException(status_code=404, detail=f"Song {song_id} not found")
        return db_song


async def filter_songs_(song_filter:SongFilter) -> list[Song]:
    """ Database search with filter for song name or artist.
    
    Parameter
    --------
    song_filter: type SongFilter contains "name" and "artist"
    
    Returns
    -------
    final_result: type List[Song] 
    
    """
    # If there is more than one filter atribute we need a list
    where_clause = []
    # Get filters in dict format
    song_data = song_filter.model_dump(exclude_unset=True)
    # Make filter string in the right format Song.name='Singer_name'
    for key, value in song_data.items():
        where_clause.append(text('Song.' + str(key) + '=\'' + str(value) + '\''))
    # Connect to database, search and filter.
    # If there is only on filter the format is different
    async with get_session() as s:
        stmt = select(Song)
        if len(where_clause) == 1:
            stmt = stmt.where(where_clause[0])
        elif len(where_clause) > 1:
            stmt = stmt.where(and_(*where_clause))

        result = await s.exec(stmt)
        db_songs = result.all()
        # Raise error if no songs are returned
        if not db_songs:
            HTTPException(status_code=404, detail=f"Songs not found")
        # The database result is an iterator. Go through and put in a list
        final_result = [Song(name=song.name, artist=song.artist, id=song.id) for song in db_songs]

        return final_result 


async def update_song_(song_id: int, song_update: SongUpdate) -> Song:
    """ Partial (or full) update of song post
    
    Parameters
    ---------
    song_id : int 
        The song id to be updated
    
    song_update : SongUpdate
        Contains the atribute to be updated: 'name', 'artist' or both
        
    Returns
    -------
    db_song: Song
        Returns the updated post for the song
    
    """
    async with get_session() as s:
        # Get song from database
        result = await s.exec(select(Song).where(Song.id == song_id))
        db_song = result.one()
        # If it doesn't exist return error
        if not db_song:
            HTTPException(status_code=404, detail=f"Song {song_id} not found")
        # Get the update data in dict format
        song_data = song_update.model_dump(exclude_unset=True)
        # Change the atributes and commit
        for key, value in song_data.items():
            setattr(db_song, key, value)
        s.add(db_song)
        await s.commit()
        # Refresh to return the updated post
        await s.refresh(db_song)
        return db_song


async def delete_song_(song_id:int) -> dict:
    """ Delete song by id.

    Return
    ------
    : dict
    """
    async with get_session() as s:
        # Get song by id
        result = await s.exec(select(Song).where(Song.id == song_id))
        db_song = result.one()
        # if song doesn't exist return error
        if not db_song:
            HTTPException(status_code=404, detail=f"Song {song_id} not found")
        
        await s.delete(db_song)
        await s.commit()
        return {"ok": True}



