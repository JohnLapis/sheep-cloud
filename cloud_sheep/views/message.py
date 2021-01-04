from functools import wraps

from bson.objectid import ObjectId
from flask import abort, request
from flask.views import MethodView
from werkzeug.datastructures import MultiDict

from ..entities.message import create_message, create_message_update


def handle_message(view):
    def serialize_id(message):
        message["_id"] = str(message["_id"])
        return message

    @wraps(view)
    def wrapper(*args, **kwargs):
        res = view(*args, **kwargs)
        if res.get("messages"):
            return {"messages": list(map(serialize_id, res["messages"]))}
        else:
            return serialize_id(res)

    return wrapper


class MessageView(MethodView):
    def __init__(self, db):
        super().__init__()
        self.db = db

    @handle_message
    def get(self, id=None):
        if id is None:
            url_query = MultiDict(request.args)
            limit_param = self.db.get_limit_param(
                url_query.pop("limit", default=None)
            )
            sorting_params = [
                self.db.get_sort_param(param)
                for param in url_query.poplist("sort") or ["last_modified"]
            ]
            query = self.db.create_query_from_dict(url_query)
            messages = (
                self.db.message.find(query).sort(sorting_params).limit(limit_param)
            )
            if not messages:
                abort(404)
            return {"messages": messages}
        else:
            message = self.db.message.find_one(ObjectId(id))
            if not message:
                abort(404)
            return message

    def post(self):
        if type(request.json) == list:
            messages = [create_message(**m) for m in request.json]
            res = self.db.message.insert_many(messages)
            inserted_ids = res.inserted_ids
        else:
            message = create_message(**request.json)
            res = self.db.message.insert_one(message)
            inserted_ids = [res.inserted_id]

        assert res.acknowledged
        return {"inserted_ids": list(map(str, inserted_ids))}, 201

    def put(self, id=None):
        update = create_message_update(**request.json)
        if id is None:
            url_query = MultiDict(request.args)
            res = self.db.message.update_many(
                self.db.create_query_from_dict(url_query), self.db.create_update_query(update)
            )
        else:
            res = self.db.message.update_one(
                {"_id": ObjectId(id)}, self.db.create_update_query(update)
            )
            assert res.matched_count == 1

        assert res.acknowledged
        return {"modified_count": res.modified_count}, 201

    def delete(self, id):
        pass
