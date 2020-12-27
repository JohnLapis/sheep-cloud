from flask import Flask
from . import api

app = Flask(__name__)

LATEST_VERSION = 'v1'

app.register_blueprint(api.bp, url_prefix='/api')
app.register_blueprint(api.bp, url_prefix=f'/api/{LATEST_VERSION}')
