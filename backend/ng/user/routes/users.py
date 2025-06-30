"""
User team operations and statistics API routes.
"""

from flask import g
from flask_restx import Namespace, Resource

from ..controllers import (
    get_user_teams,
    get_user_teams_in_event,
    can_join_team_in_event,
    get_user_stats,
    list_users,
    get_user_info,
)
from ...core.utils import success_response
from ...core.middleware import (
    user_endpoint,
    admin_endpoint,
    load_user,
    load_event,
    load_current_user_as_target,
    load_user_stats,
    load_user_teams,
    load_user_event_team_data,
    load_user_details,
    check_team_join_eligibility,
)
from ...core.docs import (
    LIST_ALL_USERS_DOC,
    GET_USER_DETAILS_DOC,
    GET_MY_TEAMS_DOC,
    GET_MY_EVENT_TEAM_DOC,
    GET_MY_ELIGIBILITY_DOC,
    GET_MY_STATS_DOC,
    GET_USER_TEAMS_DOC,
    GET_USER_STATS_DOC,
)

users_namespace = Namespace("users", description="user team operations")


@users_namespace.route("/<int:user_id>")
class UserDetails(Resource):
    @admin_endpoint()
    @load_user()
    @load_user_details()
    @users_namespace.doc(**GET_USER_DETAILS_DOC)
    def get(self, user_id):
        """Get user details"""
        result = get_user_info(user_id)
        return success_response(result)


@users_namespace.route("/me/teams")
class UserTeams(Resource):
    @user_endpoint()
    @load_current_user_as_target()
    @load_user_teams()
    @users_namespace.doc(**GET_MY_TEAMS_DOC)
    def get(self):
        """Get my teams"""
        result = get_user_teams(g.user.id)
        return success_response(result)


@users_namespace.route("/me/events/<int:event_id>/teams")
class UserEventTeams(Resource):
    @user_endpoint()
    @load_current_user_as_target()
    @load_event()
    @load_user_event_team_data()
    @users_namespace.doc(**GET_MY_EVENT_TEAM_DOC)
    def get(self, event_id):
        """Get my team in event"""
        result = get_user_teams_in_event(g.user.id, event_id)
        return success_response(result)


@users_namespace.route("/me/events/<int:event_id>/eligibility")
class UserEventEligibility(Resource):
    @user_endpoint()
    @load_current_user_as_target()
    @load_event()
    @check_team_join_eligibility()
    @users_namespace.doc(**GET_MY_ELIGIBILITY_DOC)
    def get(self, event_id):
        """Check eligibility"""
        result = can_join_team_in_event(g.user.id, event_id)
        return success_response(result)


@users_namespace.route("/me/stats")
class UserStats(Resource):
    @user_endpoint()
    @load_current_user_as_target()
    @load_user_stats()
    @users_namespace.doc(**GET_MY_STATS_DOC)
    def get(self):
        """Get my stats"""
        result = get_user_stats(g.user.id)
        return success_response(result)


# ============ ADMIN ENDPOINTS FOR MANAGING OTHER USERS ============


@users_namespace.route("/all")
class UserList(Resource):
    @admin_endpoint()
    @users_namespace.doc(**LIST_ALL_USERS_DOC)
    def get(self):
        """Get all users"""
        result = list_users()
        return success_response(result)


@users_namespace.route("/<int:user_id>/teams")
class AdminUserTeams(Resource):
    @admin_endpoint()
    @load_user()
    @load_user_teams()
    @users_namespace.doc(**GET_USER_TEAMS_DOC)
    def get(self, user_id):
        """Get any user's teams"""
        result = get_user_teams(user_id)
        return success_response(result)


@users_namespace.route("/<int:user_id>/stats")
class AdminUserStats(Resource):
    @admin_endpoint()
    @load_user()
    @load_user_stats()
    @users_namespace.doc(**GET_USER_STATS_DOC)
    def get(self, user_id):
        """Get any user's stats"""
        result = get_user_stats(user_id)
        return success_response(result)
