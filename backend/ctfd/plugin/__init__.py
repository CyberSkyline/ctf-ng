#!/usr/bin/env python3

from .routes import delete_unwanted_ctfd_routes
from .routes.views import plugin_views
from .controllers import api as plugin_api
from CTFd.models import db

def load(app):
    try:
        delete_unwanted_ctfd_routes(app)

        print("Loading plugin...", flush=True)

        db.create_all()

        app.register_blueprint(plugin_views)
        app.register_blueprint(plugin_api, url_prefix="/plugin/api/")
        print("Plugin loaded successfully", flush=True)
    except Exception as e:
        print("Error loading plugin:", e, flush=True)

