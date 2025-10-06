"""
Main API blueprint and namespace configuration for the plugin.
"""

from typing import Any

from flask import Blueprint
from flask_restx import Api
from werkzeug.routing import Map
from ...challenge.routes import challenge_admin_namespace
from ...event.routes import events_admin_namespace, events_user_namespace
from ...permissions.routes import permissions_admin_namespace
from ...permissions.routes.user_routes import permissions_user_namespace
from ...team.routes import teams_admin_namespace
from ...user.routes import users_admin_namespace, users_user_namespace
from ...user.routes.authenticate import oauth_namespace
from ...scoring.routes import scoring_admin_namespace, scoring_user_namespace
from ...support.routes import support_user_namespace, support_admin_namespace

from ...admin.routes.admin import admin_namespace
# from ...event_registration.routes.event_registration import event_reg_namespace
# from ...challenge.routes.routes import challenge_namespace
from ...containers.routes.routes import container_namespace
from ...containers.routes.admin_routes import admin_container_namespace

from ...notifications.routes import (
    notifications_user_namespace,
    notifications_admin_namespace,
)


api_blueprint = Blueprint("plugin_api", __name__)


def remove_blueprint(app, blueprint_name: str):
    prefix = blueprint_name + "."

    app.blueprints.pop(blueprint_name, None)


    for d in (
        app.before_request_funcs,
        app.after_request_funcs,
        app.teardown_request_funcs,
        app.url_value_preprocessors,
        app.url_default_functions,
        app.template_context_processors,
    ):
        d.pop(blueprint_name, None)
    for endpoint in list(app.view_functions):
        if endpoint.startswith(prefix):
            app.view_functions.pop(endpoint, None)


    kept = []
    for r in app.url_map.iter_rules():
        if not r.endpoint.startswith(prefix):
            kept.append(r.empty())


    new_map = Map(
        strict_slashes=app.url_map.strict_slashes,
        host_matching=app.url_map.host_matching,
        redirect_defaults=app.url_map.redirect_defaults,
    )

    for r in kept:
        new_map.add(r)


    app.url_map = new_map


    assert all(not e.startswith(prefix) for e in app.view_functions), "view_functions still references removed endpoints"
    for r in app.url_map.iter_rules():
        assert not r.endpoint.startswith(prefix), f"Leftover rule: {r}"

    try:
        app.url_map._remap = True
    except Exception:
        pass


def delete_unwanted_ctfd_routes(app: Any) -> None:
    """Remove or override CTFd routes that conflict with our plugin."""
    remove_blueprint(app, "challenges")
    remove_blueprint(app, "tags")
    remove_blueprint(app, "topics")
    remove_blueprint(app, "submissions")
    remove_blueprint(app, "notifications")
    remove_blueprint(app, "awards")
    remove_blueprint(app, "hints")
    remove_blueprint(app, "flags")
    remove_blueprint(app, "scoreboard")
    remove_blueprint(app, "teams")
    remove_blueprint(app, "users")
    remove_blueprint(app, "statistics")
    remove_blueprint(app, "files")
    remove_blueprint(app, "pages")
    remove_blueprint(app, "unlocks")
    remove_blueprint(app, "scoreboard")
    remove_blueprint(app, "teams")
    remove_blueprint(app, "users")
    remove_blueprint(app, "statistics")
    remove_blueprint(app, "files")
    remove_blueprint(app, "notifications")
    remove_blueprint(app, "pages")
    remove_blueprint(app, "unlocks")
    remove_blueprint(app, "tokens")
    remove_blueprint(app, "comments")
    remove_blueprint(app, "shares")
    remove_blueprint(app, "brackets")
    remove_blueprint(app, "exports")
    remove_blueprint(app, "solutions")
    remove_blueprint(app, "auth")
    remove_blueprint(app, "events")
    remove_blueprint(app, "social")
    remove_blueprint(app, "theme")
    remove_blueprint(app, "views")

def _remove_appwide_handler(bucket: dict, predicate):
    lst = bucket.get(None, [])
    keep = [f for f in lst if not predicate(f)]
    lst[:] = keep

def remove_registered_helpers(app):
    _remove_appwide_handler(
        app.url_default_functions,
        lambda f: f.__name__ in {"inject_theme", "env_asset_url_default", "asset_cache_url_default"}
    )

    _remove_appwide_handler(
        app.before_request_funcs,
        lambda f: f.__name__ in {"needs_setup", "needs_setup_safe"}
    )

def remove_registered_errorhandlers(app):
    app.error_handler_spec.clear()






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
api_v1.add_namespace(oauth_namespace, path="/authenticate")
api_v1.add_namespace(scoring_user_namespace, path="/events")
# api_v1.add_namespace(challenge_namespace, path="/challenge")
api_v1.add_namespace(support_user_namespace, path="/support")
api_v1.add_namespace(container_namespace, path="/container")
api_v1.add_namespace(permissions_user_namespace, path="/permissions")
api_v1.add_namespace(notifications_user_namespace, path="/notifications")

# Admin namespaces
api_v1.add_namespace(admin_namespace, path="/admin")
api_v1.add_namespace(support_admin_namespace, path="/admin/support")
api_v1.add_namespace(events_admin_namespace, path="/admin/events")
api_v1.add_namespace(users_admin_namespace, path="/admin/users")
api_v1.add_namespace(teams_admin_namespace, path="/admin/teams")
api_v1.add_namespace(permissions_admin_namespace, path="/admin/permissions")
api_v1.add_namespace(challenge_admin_namespace, path="/admin/challenges")
api_v1.add_namespace(scoring_admin_namespace, path="/admin/scoring")
api_v1.add_namespace(admin_container_namespace, path="/admin/container")
api_v1.add_namespace(notifications_admin_namespace, path="/admin/notifications")
