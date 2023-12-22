import json
import pytest


def test_read_song(test_app, monkeypatch):
    test_data = {"id": 1, "name": "Song1", "artist": "Artist1"}

    async def mock_get(song_id):
        return test_data

    monkeypatch.setattr('app.crud.songs.get_song', mock_get)

    # fake_cookie = get_fake_cookie()
    # #test_app.cookies = fake_cookie
    response = test_app.get("/get_song/1")
    assert response.status_code == 200
    assert response.json() == test_data



def test_add_song(test_app, monkeypatch):
    test_request_payload = {"name": "something", "artist": "something else"}
    test_response_payload = {"id": 30, "name": "something", "artist": "something else"}

    async def mock_post(song):
        return test_response_payload

    monkeypatch.setattr('app.crud.songs.create_song', mock_post)

    response = test_app.post("/add_song/", json=test_request_payload)

    assert response.status_code == 201
    assert response.json() == test_response_payload




# def test_create_note_invalid_json(test_app):
#     response = test_app.post("/notes/", content=json.dumps({"title": "something"}))
#     assert response.status_code == 422




