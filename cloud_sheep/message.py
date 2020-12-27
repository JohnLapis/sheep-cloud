from flask.views import MethodView


class Message(MethodView):
    def get(self, id):
        return f'get message: {id}'

    def post(self, id):
        return f'post message: {id}'
