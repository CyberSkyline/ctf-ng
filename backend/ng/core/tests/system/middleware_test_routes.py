"""
Test routes for middleware testing isolated in a separate Flask app instance.
/backend/ng/core/testing/system/middleware_test_routes.py
"""

from flask import Blueprint, jsonify
from ...middleware.permission_middleware import (
    get_permissions,

)
from ...middleware.auth import user_endpoint, admin_endpoint
from ...middleware.loaders import (
    load_event,
    load_team_by_user_and_event,
    load_team_by_invite_code,
    load_team,
    load_user,
    load_ticket,
    load_ticket_tag,
)
from ...middleware.loaders._util import LoaderType

middleware_test_routes = Blueprint("middleware_test_routes", __name__)


@middleware_test_routes.route("/user_decorator_test", methods=["GET"])
@user_endpoint(
    json_required=False,
)
def api_decorator_test(**kwargs):
    """
    Endpoint to test the API decorator.
    """
    return jsonify({"success": True, "message": "API decorator test successful."})


@middleware_test_routes.route("/admin_decorator_test", methods=["GET"])
@admin_endpoint(
    json_required=False,
)
def admin_decorator_test(**kwargs):
    """
    Endpoint to test the admin decorator.
    """
    print("gets here")
    return jsonify({"success": True, "message": "Admin decorator test successful."})


@middleware_test_routes.route("/loading_model_objects", methods=["POST"])
@user_endpoint(
    json_required=True,
)
@load_event(source=LoaderType.BODY)
@load_team_by_invite_code(source=LoaderType.BODY)
@load_team(source=LoaderType.BODY,output_key="team2")
@load_team_by_user_and_event(output_key="team3")
@load_user(source=LoaderType.BODY)
@load_ticket(source=LoaderType.BODY)
@load_ticket_tag(source=LoaderType.BODY)
def loading_model_objects(**kwargs):
    """
    Endpoint to test the loading of model objects.
    """
    user = kwargs.get("user")
    event = kwargs.get("event")
    team = kwargs.get("team")
    team2 = kwargs.get("team2")
    team3 = kwargs.get("team3")
    ticket = kwargs.get("ticket")
    ticket_tag = kwargs.get("ticket_tag")
    missing = [name for name, obj in [("user", user), ("event", event), ("team", team), ("team2", team2), ("team3", team3), ("ticket", ticket), ("ticket_tag", ticket_tag)] if obj is None]
    if missing:
        return jsonify({"success": False, "message": f"Missing required model objects: {', '.join(missing)}."}), 400
    return jsonify({"success": True, "message": "Loading model objects successful."})



@middleware_test_routes.route("/get_user_permissions", methods=["GET"])
@user_endpoint()
@get_permissions
def get_user_permissions(**kwargs):
    """
    Endpoint to retrieve user permissions.
    The permissions are attached to the request context by the decorator.
    """
    return jsonify({"success": True, "permissions": kwargs.get("permissions", [])})

