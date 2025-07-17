"""
Main API blueprint and namespace configuration for the plugin.
"""

from typing import Any

from flask import Blueprint
from flask_restx import Api

from ...challenge.routes import challenge_admin_namespace
from ...event.routes import events_admin_namespace, events_user_namespace
from ...permissions.routes import permissions_admin_namespace
from ...team.routes import teams_admin_namespace
from ...user.routes import users_admin_namespace, users_user_namespace
from ...scoring.routes import scoring_admin_namespace, scoring_user_namespace

# from ...admin.routes.admin import admin_namespace
# from ...support.routes.user_tickets import user_tickets_namespace
# from ...support.routes.admin_tickets import admin_tickets_namespace
# from ...event_registration.routes.event_registration import event_reg_namespace
# from ...challenge.routes.routes import challenge_namespace

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
    description="The API for CTF-NG. Used to manage events, teams, scoring, support tickets, and other features for our custom plugin.",
    doc="/docs",
    authorizations={"sessionAuth": {"type": "apiKey", "in": "cookie", "name": "session"}},
    security=["sessionAuth"],
)

# User namespaces
api_v1.add_namespace(events_user_namespace, path="/events")
api_v1.add_namespace(users_user_namespace, path="/users")
api_v1.add_namespace(scoring_user_namespace, path="/events")
# api_v1.add_namespace(user_tickets_namespace, path="/tickets")

# Admin namespaces
api_v1.add_namespace(events_admin_namespace, path="/admin/events")
api_v1.add_namespace(users_admin_namespace, path="/admin/users")
# api_v1.add_namespace(admin_tickets_namespace, path="/admin/tickets")
api_v1.add_namespace(teams_admin_namespace, path="/admin/teams")
api_v1.add_namespace(permissions_admin_namespace, path="/admin/permissions")
api_v1.add_namespace(challenge_admin_namespace, path="/admin/challenge")
api_v1.add_namespace(scoring_admin_namespace, path="/admin/scoring")
