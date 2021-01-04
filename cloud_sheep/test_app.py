import random
import re
from datetime import datetime

import pytest
from bson.objectid import ObjectId

from . import LATEST_VERSION, app
from .entities.message import create_message
from .mongodb import DatabaseClient


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def get_random_string(length):
    letters = "abcdefghijklmnopqrstuvwxyz"
    return "".join(random.choice(letters) for i in range(length))


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
        message = create_message(text="test get message")
        message_id = self.message.insert_one(message).inserted_id

        res = client.get(f"/api/messages/{message_id}")

        assert self.message.delete_one({"_id": message_id}).deleted_count == 1
        assert res.status_code == 200
        message["_id"] = str(message_id)
        assert res.json["text"] == message["text"]

        # timezone (%Z) is ignored
        timeformat = "%a, %d %b %Y %H:%M:%S"
        assert re.match(
            message["created_at"].strftime(timeformat), res.json["created_at"]
        )

    def test_get_message_using_nonexistent_id(self, client):
        # guarantees id doesn't already exist
        message = create_message(text="text")
        id = self.message.insert_one(message).inserted_id
        self.message.delete_one({"_id": id})

        res = client.get(f"/api/messages/{id}")

        assert res.status_code == 404

    def test_get_message_using_invalid_id(self, client):
        id = "invalid id"
        res = client.get(f"/api/messages/{id}")

        assert res.status_code == 400
        error_message = (
            f"'{id}' is not a valid ObjectId, it must be a 12-byte"
            " input or a 24-character hex string"
        )
        assert error_message == res.json["message"]
        assert res.json["error"] == "InvalidId"

    def test_get_message_using_params(self, client):
        # the messages have the attr "created_at" set to the current date
        messages = [
            create_message(text="text1"),
            create_message(text="text2"),
        ]
        inserted_ids = set(
            [m for m in self.message.insert_many(messages).inserted_ids]
        )

        today = datetime.now().strftime("%Y%m%d")  # YYYYMMDD

        res = client.get(
            f"/api/messages?created_at=gt:{today}&sort=-created_at&limit=2"
        )

        assert res.status_code == 200
        assert (
            set([ObjectId(m["_id"]) for m in res.json["messages"]]) == inserted_ids
        )
        for id in inserted_ids:
            assert self.message.delete_one({"_id": id}).deleted_count == 1

    def test_get_message_using_invalid_params(self, client):
        res = client.put(
            "/api/messages?created_at=gt:not a date",
            json={"text": "new text"},
        )

        assert res.status_code == 400
        assert res.json["message"] == "'not a date' is not a valid date."
        assert res.json["error"] == "InvalidValue"

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

        update = {"text": "new text"}
        res = client.put(f"/api/v1/messages/{id}", json=update)

        updated_message = self.message.find_one_and_delete({"_id": id})
        assert updated_message["text"] == update["text"]
        assert updated_message["title"] == old_message["title"]
        assert res.status_code == 201 and res.json["modified_count"] == 1

    def test_put_message_with_too_large_title(self, client):
        from .entities.message import TITLE_MAX_LENGTH

        old_message = create_message(text="text", title="title")
        id = self.message.insert_one(old_message).inserted_id

        update = {"title": "a" * (TITLE_MAX_LENGTH + 1)}
        res = client.put(f"/api/v1/messages/{id}", json=update)

        assert self.message.delete_one({"_id": id}).deleted_count == 1
        assert res.status_code == 400
        assert res.json["message"] == "Message's title is not valid."
        assert res.json["error"] == "InvalidMessage"

    def test_put_message_using_params(self, client):
        random_string = get_random_string(10)
        messages = [
            create_message(title=random_string + "a", text="text"),
            create_message(title=random_string + "b", text="text"),
        ]
        inserted_ids = self.message.insert_many(messages).inserted_ids

        today = datetime.now().strftime("%Y%m%d")  # YYYYMMDD
        update = {"text": "new text"}
        res = client.put(
            f"/api/messages?created_at=gt:{today}&title=rg:{random_string}",
            json=update,
        )

        for id in inserted_ids:
            updated_message = self.message.find_one_and_delete({"_id": id})
            assert updated_message["text"] == update["text"]

        assert res.status_code == 201 and res.json["modified_count"] == 2

    def test_put_message_using_invalid_params(self, client):
        random_string = get_random_string(10)
        res = client.put(
            f"/api/messages?title=rg:{random_string}&invalidParam=0",
            json={"text": "new text"},
        )

        assert res.status_code == 400
        assert res.json["message"] == "'invalidParam' is not a valid parameter."
        assert res.json["error"] == "InvalidParam"

    def test_delete_message_using_id(self, client):
        random_string = get_random_string(10).lower()
        message = create_message(text=random_string.upper())
        id = self.message.insert_one(message).inserted_id

        res = client.delete(f"/api/messages/{id}")

        assert not self.message.find_one({"_id": id})
        assert res.status_code == 200
        assert res.json["deleted_count"] == 1

    def test_delete_message_using_nonexistent_id(self, client):
        # guarantees id doesn't already exist
        message = create_message(text="text")
        id = self.message.insert_one(message).inserted_id
        self.message.delete_one({"_id": id})

        res = client.delete(f"/api/messages/{id}")

        assert res.status_code == 200
        assert res.json["deleted_count"] == 0

    def test_delete_message_using_params(self, client):
        random_string = get_random_string(10).lower()
        messages = [
            create_message(title=random_string.upper(), text="text"),
            create_message(title=random_string.upper(), text="text"),
            create_message(title=random_string.upper(), text="text"),
        ]
        inserted_ids = self.message.insert_many(messages).inserted_ids

        res = client.delete(f"/api/messages?title=rg:{random_string}&title=op:i")

        total_not_deleted = 0
        for id in inserted_ids:
            total_not_deleted += self.message.delete_one({"_id": id}).deleted_count

        assert total_not_deleted == 0
        assert res.status_code == 200
        assert res.json["deleted_count"] == len(inserted_ids)
