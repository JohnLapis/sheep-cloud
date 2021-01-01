from bson.errors import InvalidId

from .entities.message import MessageValidationError


class InvalidParam(Exception):
    pass


class InvalidValue(Exception):
    pass


def setup_error_handlers(app):
    @app.errorhandler(InvalidId)
    def invalid_id(error):
        return "id is invalid.", 400

    @app.errorhandler(MessageValidationError)
    def invalid_message(error):
        return "message is invalid.", 400
