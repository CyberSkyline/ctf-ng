"""
Main API blueprint and namespace configuration for the plugin.
/backend/ctfd/plugin/core/routes/__init__.py
"""

from flask import Blueprint
from flask_restx import Api
from typing import Any

from plugin.team.routes.teams import teams_namespace
from plugin.event.routes.events import events_namespace
from plugin.user.routes.users import users_namespace
from plugin.admin.routes.admin import admin_namespace

api_blueprint = Blueprint("plugin_api", __name__)


def delete_unwanted_ctfd_routes(app: Any) -> None:
    """Remove or override CTFd routes that conflict with our plugin."""
    # This is a placeholder function that can be used to remove
    # CTFd routes that conflict with our plugin's functionality
    pass


# Swagger Docs
api_v1 = Api(
    api_blueprint,
    version="1.0",
    title="CTFd Plugin API",
    description="The API for CTF-NG. Used to manage events, teams, scoring, and other features for our custom plugin.",
    doc="/docs",
    authorizations={"sessionAuth": {"type": "apiKey", "in": "cookie", "name": "session"}},
    security=["sessionAuth"],
)


api_v1.add_namespace(teams_namespace, path="/teams")
api_v1.add_namespace(events_namespace, path="/events")
api_v1.add_namespace(users_namespace, path="/users")
api_v1.add_namespace(admin_namespace, path="/admin")
