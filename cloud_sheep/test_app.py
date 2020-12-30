import pytest
from bson.objectid import ObjectId

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
        assert res.json == message

    def test_get_message_using_nonexistent_id(self, client):
        # guarantees id doesn't already exist
        message = {"text": "text"}
        id = self.db.insert_one(message).inserted_id
        self.db.delete_one({"_id": id})

        res = client.get(f"/api/messages/{id}")

        assert res.status_code == 404

    def test_get_message_using_invalid_id(self, client):
        id = "invalid id"
        res = client.get(f"/api/messages/{id}")

        assert res.status_code == 400
        assert res.data == b"id is invalid."


    def test_post_message(self, client):
        message = {"text": "test post message", "title": "test post title"}
        res = client.post("/api/v1/messages", json=message)

        id = ObjectId(res.json["inserted_ids"][0])
        created_message = self.db.find_one_and_delete({"_id": id})
        assert created_message["text"] == message["text"]
        assert created_message["title"] == message["title"]
        assert created_message["size"] == len(message["text"])
        assert res.status_code == 201

    def test_post_message_with_invalid_text(self, client):
        message = {"text": False}
        res = client.post("/api/v1/messages", json=message)

        assert res.status_code == 400
        assert res.data == b"message is invalid."

    def test_post_message_with_too_large_title(self, client):
        from .entities.message import TITLE_MAX_LENGTH

        message = {"text": "test post message", "title": "a" * (TITLE_MAX_LENGTH + 1)}
        res = client.post("/api/v1/messages", json=message)

        assert res.status_code == 400
        assert res.data == b"message is invalid."

    def test_post_many_messages(self, client):
        NUM_MESSAGES = 5
        messages = [{"text": f"test post message {i}"} for i in range(NUM_MESSAGES)]

        res = client.post("/api/v1/messages", json=messages)

        assert len(res.json["inserted_ids"]) == NUM_MESSAGES
        for id in res.json["inserted_ids"]:
            created_message = self.db.find_one_and_delete({"_id": ObjectId(id)})
            matching_messages = [
                m for m in messages if m["text"] == created_message["text"]
            ]
            assert len(matching_messages) == 1
            assert created_message["size"] == len(matching_messages[0]["text"])

        assert res.status_code == 201

