from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlmodel import Session, select
from typing import Dict

from app.schemas.song import Song, SongCreate, SongUpdate, SongFilter
from app.crud.songs import create_song, get_songs, get_song, update_song_, delete_song_, filter_songs_, upload_data
from app.auth.jwthandler import get_current_user
    
router = APIRouter()


@router.get('/get_songs', response_model=list[Song], dependencies=[Depends(get_current_user)])
async def get_songs_open():
    """ List all the songs in the database."""
    data = await get_songs()
    return data


@router.get('/get_song/{song_id}', response_model=Song, dependencies=[Depends(get_current_user)])
async def get_song_id(song_id: int):
    """ Return one song from the database by id."""
    result = await get_song(song_id)
    return result


@router.post('/filter_song', response_model=list[Song], dependencies=[Depends(get_current_user)])
async def filter_songs(song_filter: SongFilter):
    """ Search database and filter by name, artist or both."""
    result = await filter_songs_(song_filter)
    return result

@router.post("/uploadfile/", dependencies=[Depends(get_current_user)])
async def create_upload_file(file: UploadFile = File(...)) -> Dict[str,str]:
    """ Batch load database from csv file."""
    if not file.content_type == 'text/csv':
        HTTPException(status_code=422, detail=f"Wrong format")
    df_shape = await upload_data(file.file)
    file.file.close()
    return {"File name": file.filename, "Number of Songs Added":df_shape[0]}


@router.post('/add_song', response_model=Song, dependencies=[Depends(get_current_user)])
async def add_song(song:SongCreate):
    """ Add one song to database."""
    result = await create_song(song)
    return result


@router.patch("/update_song/{song_id}", response_model=Song, dependencies=[Depends(get_current_user)])
async def update_song(song_id: int, song_update: SongUpdate):
    """ Change parts or all of one songs data."""
    result = await update_song_(song_id, song_update)
    return result

@router.delete('/delete_song/{song_id}', dependencies=[Depends(get_current_user)])
async def delete_song(song_id:int):
    """ Delete one song by id."""
    result = await delete_song_(song_id)
    return result
