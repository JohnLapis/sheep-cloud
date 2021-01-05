from .message import MessageView

VIEWS = {}


def setup_views(*, db):
    global VIEWS
    VIEWS = {
        "message_view": MessageView.as_view("get_message", db),
    }


def get_views():
    return VIEWS
