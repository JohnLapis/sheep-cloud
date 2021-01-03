from bson.errors import InvalidId

from .entities.message import InvalidMessage
from .entities.param import InvalidExpression, InvalidParam
from .mongodb import InvalidOperator, InvalidQuery, InvalidValue


def setup_error_handlers(app):
    @app.errorhandler(InvalidMessage)
    @app.errorhandler(InvalidExpression)
    @app.errorhandler(InvalidParam)
    @app.errorhandler(InvalidOperator)
    @app.errorhandler(InvalidQuery)
    @app.errorhandler(InvalidValue)
    @app.errorhandler(InvalidId)
    def invalid_value(error):
        return {"message": error.args[0], "error": type(error).__name__}, 400
