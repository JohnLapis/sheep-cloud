from datetime import datetime

import pytest
from bson.objectid import ObjectId

from . import LATEST_VERSION, app
from .mongodb import DatabaseClient


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
        cls.db = DatabaseClient()
        cls.message = cls.db.message

    @classmethod
    def teardown_class(cls):
        cls.db.conn.close()

    def test_get_message_using_id(self, client):
        message = {"text": "test get message"}
        message_id = self.message.insert_one(message).inserted_id

        res = client.get(f"/api/messages/{message_id}")

        assert self.message.delete_one({"_id": message_id}).acknowledged
        assert res.status_code == 200
        message["_id"] = str(message_id)
        assert res.json == message

    def test_get_message_using_nonexistent_id(self, client):
        # guarantees id doesn't already exist
        message = {"text": "text"}
        id = self.message.insert_one(message).inserted_id
        self.message.delete_one({"_id": id})

        res = client.get(f"/api/messages/{id}")

        assert res.status_code == 404

    def test_get_message_using_invalid_id(self, client):
        id = "invalid id"
        res = client.get(f"/api/messages/{id}")

        assert res.status_code == 400
        error_message = (f"'{id}' is not a valid ObjectId, it must be a 12-byte"
                         " input or a 24-character hex string")
        assert error_message == res.json["message"]
        assert res.json["error"] == "InvalidId"

    def test_get_message_using_params(self, client):
        messages = [
            {"text": "text", "created_at": datetime.now()},
            {"text": "text", "created_at": datetime.now()},
        ]
        inserted_ids = set(map(str, self.message.insert_many(messages).inserted_ids))

        today = datetime.now().strftime("%Y%m%d")  # YYYYMMDD

        res = client.get(
            f"/api/messages?created_at=gt:{today}&sort=-created_at&limit=2"
        )

        assert res.status_code == 200
        assert set([m["_id"] for m in res.json["messages"]]) == inserted_ids
        for id in inserted_ids:
            assert self.message.delete_one({"_id": id}).acknowledged

    def test_post_message(self, client):
        message = {"text": "test post message", "title": "test post title"}
        res = client.post("/api/v1/messages", json=message)

        id = ObjectId(res.json["inserted_ids"][0])
        created_message = self.message.find_one_and_delete({"_id": id})
        assert created_message["text"] == message["text"]
        assert created_message["title"] == message["title"]
        assert res.status_code == 201

    def test_post_message_with_invalid_text(self, client):
        message = {"text": False}
        res = client.post("/api/v1/messages", json=message)

        assert res.status_code == 400
        assert res.json["message"] == "Message's text is not valid."
        assert res.json["error"] == "InvalidMessage"

    def test_post_message_with_too_large_title(self, client):
        from .entities.message import TITLE_MAX_LENGTH

        message = {
            "text": "test post message",
            "title": "a" * (TITLE_MAX_LENGTH + 1),
        }
        res = client.post("/api/v1/messages", json=message)

        assert res.status_code == 400
        assert res.json["message"] == "Message's title is not valid."
        assert res.json["error"] == "InvalidMessage"

    def test_post_many_messages(self, client):
        NUM_MESSAGES = 5
        messages = [{"text": f"test post message {i}"} for i in range(NUM_MESSAGES)]

        res = client.post("/api/v1/messages", json=messages)

        assert len(res.json["inserted_ids"]) == NUM_MESSAGES
        for id in res.json["inserted_ids"]:
            created_message = self.message.find_one_and_delete({"_id": ObjectId(id)})
            matching_messages = [
                m for m in messages if m["text"] == created_message["text"]
            ]
            assert len(matching_messages) == 1

        assert res.status_code == 201

    def test_put_message_using_id(self, client):
        old_message = {"text": "test put text", "title": "test put title"}
        id = self.message.insert_one(old_message).inserted_id

        new_text = {"text": "new text"}
        res = client.put(f"/api/v1/messages/{id}", json=new_text)

        updated_message = self.message.find_one_and_delete({"_id": id})
        assert updated_message["text"] == new_text["text"]
        assert updated_message["title"] == old_message["title"]
        assert res.status_code == 201 and res.json["modified_count"] == 1
