from .message import Message
from ..db import db

funcs = {
    "message_view": Message.as_view("get_message", db["message"]),
}
