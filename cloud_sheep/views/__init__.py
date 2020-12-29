from .message import MessageView
from ..db import db

funcs = {
    "message_view": MessageView.as_view("get_message", db["message"]),
}
