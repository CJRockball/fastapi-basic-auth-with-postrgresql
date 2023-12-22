import pytest
from starlette.testclient import TestClient

from datetime import timedelta
from fastapi.encoders import jsonable_encoder
from app.auth.jwthandler import (create_access_token,)

from app.main import app


def get_fake_cookie():
    access_token = create_access_token(
        data={"sub": "mofo"}, expires_delta=timedelta(minutes=30)
    )
    
    token = jsonable_encoder(access_token)
    fake_cookie = {"Authorization": f"Bearer {token}"}
    return fake_cookie


@pytest.fixture(scope='session')
def test_app():
    fake_cookie = get_fake_cookie()
    client = TestClient(app, cookies=fake_cookie)
    yield client