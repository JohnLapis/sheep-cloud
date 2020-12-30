from bson.objectid import ObjectId
from flask import abort, request
from flask.views import MethodView

from ..entities.message import create_message


class MessageView(MethodView):
    def __init__(self, db):
        super()
        self.db = db

    def get(self, id=None):
        if id is None:
            # request.args
            pass
        else:
            message = self.db.find_one({"_id": ObjectId(id)})
            if message is None:
                abort(404)
            message["_id"] = str(message["_id"])
            return message

    def post(self):
        if isinstance(request.json, list):
            messages = [create_message(**message) for message in request.json]
            res = self.db.insert_many(messages)
            inserted_ids = res.inserted_ids
        else:
            message = create_message(**request.json)
            res = self.db.insert_one(message)
            inserted_ids = [res.inserted_id]

        assert res.acknowledged
        return {"inserted_ids": list(map(str, inserted_ids)) }, 201

    def put(self, id):
        pass

    def delete(self, id):
        pass
