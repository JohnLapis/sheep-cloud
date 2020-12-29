from flask import Blueprint

bp = Blueprint("api", __name__)


def setup_url_rules(*, message_view):
    bp.add_url_rule("", view_func=lambda: ("", 204))
    bp.add_url_rule("/messages/<string:id>", view_func=message_view)
