"""
Test routes for middleware testing isolated in a separate Flask app instance.
/backend/ng/core/testing/system/middleware_test_routes.py
"""

from flask import Blueprint, jsonify
from ...middleware.middleware import lookup
from ....user.models.User import User
from ....event.models.Event import Event
from ....team.models.Team import Team
from ....team.models.TeamMember import TeamMember

middleware_test_routes = Blueprint("middleware_test_routes", __name__)


@middleware_test_routes.route("/id", methods=["GET"])
@lookup(User, ["user_id"])
@lookup(Event, ["event_id"])
@lookup(Team, ["team_id"])
def test_middleware_id_lookups(**kwargs):
    return jsonify(
        {
            "success": True,
            "user_id": kwargs.get("user").id,
            "event_name": kwargs.get("event").name,
            "team_name": kwargs.get("team").name,
        }
    )


@middleware_test_routes.route("/name", methods=["GET"])
@lookup(Event, ["event_name"])
def test_middleware_name_lookups(**kwargs):
    return jsonify({"success": True, "event_name": kwargs.get("event").name})


@middleware_test_routes.route("/multi", methods=["GET"])
@lookup(TeamMember, ["event_id", "user_id"])
def test_multi_attribute_lookup(**kwargs):
    return jsonify({"success": True, "team_id": kwargs.get("teammember").id})


@middleware_test_routes.route("/rel", methods=["GET"])
@lookup(Team, ["event_id", "user_id"])
def test_relationship_lookup(**kwargs):
    return jsonify(
        {
            "success": True,
            "team_name": kwargs.get("team").name,
        }
    )


@middleware_test_routes.route("/relgen", methods=["GET"])
@lookup(Event, ["locked", "team_id"])
def test_relationship_lookup_with_generic_params(**kwargs):
    return jsonify(
        {
            "success": True,
            "event_name": kwargs.get("event").name,
            "locked": kwargs.get("event").locked,
        }
    )


@middleware_test_routes.route("/date", methods=["GET"])
@lookup(Event, ["start_time", "end_time"])
def test_date_lookup(**kwargs):
    return jsonify(
        {
            "success": True,
            "event_name": kwargs.get("event").name,
        }
    )
