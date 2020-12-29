from flask.views import MethodView
from flask import request, abort
from bson.objectid import ObjectId


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
            messages = [{"text": message["text"]} for message in request.json]
            res = self.db.insert_many(messages)
        else:
            message = {"text": request.json["text"]}
            res = self.db.insert_one(message)

        assert res.acknowledged
        return {"_id": str(res.inserted_id)}, 201

    def put(self, id):
        pass

    def delete(self, id):
        pass
