from flask import Blueprint
from .message import Message


bp = Blueprint('api', __name__)

bp.add_url_rule('/message/<int:id>', view_func=Message.as_view('message'))
