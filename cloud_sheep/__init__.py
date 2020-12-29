from flask import Flask

from . import api
from .views import funcs

LATEST_VERSION = "v1"

app = Flask(__name__)

api.setup_url_rules(**funcs)

app.register_blueprint(api.bp, url_prefix="/api")
app.register_blueprint(api.bp, url_prefix=f"/api/{LATEST_VERSION}")
