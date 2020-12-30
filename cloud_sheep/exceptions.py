from bson.errors import InvalidId
from .entities.message import MessageValidationError

def setup_url_rules(app):
    @app.errorhandler(InvalidId)
    def invalid_id(error):
        return "id is invalid.", 400

    @app.errorhandler(MessageValidationError)
    def invalid_id(error):
        return "message is invalid.", 400