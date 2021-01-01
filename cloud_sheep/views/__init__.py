from .message import MessageView

views = {}


def setup_views(*, db):
    global views
    views = {
        "message_view": MessageView.as_view("get_message", db),
    }


def get_views():
    return views
