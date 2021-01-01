from flask import Flask

from . import api, exceptions, views
from .mongodb import DatabaseClient

LATEST_VERSION = "v1"

app = Flask(__name__)

exceptions.setup_error_handlers(app)

views.setup_views(db=DatabaseClient())
views = views.get_views()
api.setup_url_rules(**views)

app.register_blueprint(api.bp, url_prefix="/api")
app.register_blueprint(api.bp, url_prefix=f"/api/{LATEST_VERSION}")
