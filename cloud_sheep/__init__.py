from flask import Flask, Blueprint
from .message import Message
from . import db


LATEST_VERSION = 'v1'

app = Flask(__name__)

api_bp = Blueprint('api', __name__)
api_bp.add_url_rule('/message/<int:id>', view_func=Message.as_view('message', db))

app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(api_bp, url_prefix=f'/api/{LATEST_VERSION}')
