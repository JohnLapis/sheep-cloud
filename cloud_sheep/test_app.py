import pytest
from bson.objectid import ObjectId

import json

from . import LATEST_VERSION, app
from .db import conn


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_api_route_versioning(client):
    res = client.get("/api")
    assert res.status_code == 204
    res = client.get(f"/api/{LATEST_VERSION}")
    assert res.status_code == 204


class TestMessageRoute:
    @classmethod
    def setup_class(cls):
        cls.conn = conn
        cls.db = cls.conn["cloud-sheep"]["message"]

    @classmethod
    def teardown_class(cls):
        cls.conn.close()

    def test_get_message_using_id(self, client):
        message = {"text": "test get message"}
        message_id = self.db.insert_one(message).inserted_id

        res = client.get(f"/api/messages/{message_id}")

        assert self.db.delete_one({"_id": message_id}).deleted_count == 1
        assert res.status_code == 200
        message["_id"] = str(message_id)
        assert json.loads(res.data) == message

    def test_post_message_using_id(self, client):
        while True:
            message_id = ObjectId()
            if not self.db.find_one({"_id": message_id}):
                break

        message = {"text": "test post message"}

        res = client.post(f"/api/v1/messages/{message_id}", json=message)

        message["_id"] = message_id
        assert self.db.find_one_and_delete({"_id": message_id}) == message
        assert res.status_code == 200
