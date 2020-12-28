import pytest
from . import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_api_routes(client):
    res1 = client.get('/api/v1/message/44')
    res2 = client.get('/api/message/44')
    assert res1.data == res2.data == b'get message: 44'
