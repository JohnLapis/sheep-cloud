from flask.views import MethodView


class Message(MethodView):
    def __init__(self, db):
        super()
        self.db = db

    def get(self, id):
        return f'get message: {id}'

    def post(self, id):
        return f'post message: {id}'

    def put(self, id):
        pass

    def delete(self, id):
        pass
