from flask.views import MethodView
from flask import request
from bson.objectid import ObjectId


class Message(MethodView):
    def __init__(self, db):
        super()
        self.db = db

    def get(self, id):
        message = self.db.find_one({"_id": ObjectId(id)})
        message["_id"] = str(message["_id"])
        return message

    def post(self, id=None):
        if id is None:
            id = ObjectId()
        else:
            id = ObjectId(id)

        message = {"_id": id, "text": request.json["text"]}
        assert self.db.insert_one(message).acknowledged
        return "i don't know what POST should return"

    def put(self, id):
        pass

    def delete(self, id):
        pass
