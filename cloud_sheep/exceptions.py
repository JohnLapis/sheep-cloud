from bson.errors import InvalidId

from .entities.message import MessageValidationError


class InvalidParam(Exception):
    pass


class InvalidValue(Exception):
    pass


class InvalidQuery(Exception):
    pass


def setup_error_handlers(app):
    @app.errorhandler(MessageValidationError)
    @app.errorhandler(InvalidParam)
    @app.errorhandler(InvalidValue)
    @app.errorhandler(InvalidQuery)
    @app.errorhandler(InvalidId)
    def invalid_value(error):
        return {"message": error.args[0], "error": type(error).__name__}, 400
