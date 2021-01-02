from bson.errors import InvalidId

from .entities.message import InvalidMessage
from .entities.param import InvalidExpression, InvalidParam
from .mongodb import InvalidQuery, InvalidValue


def setup_error_handlers(app):
    @app.errorhandler(InvalidMessage)
    @app.errorhandler(InvalidExpression)
    @app.errorhandler(InvalidParam)
    @app.errorhandler(InvalidValue)
    @app.errorhandler(InvalidQuery)
    @app.errorhandler(InvalidId)
    def invalid_value(error):
        return {"message": error.args[0], "error": type(error).__name__}, 400
