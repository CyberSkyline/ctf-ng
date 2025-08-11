"""
My User API routes
"""

from flask_restx import Namespace, Resource

from ...core.utils import success_response
from ...core.middleware import (
    user_endpoint,
)
from ._docs import (
    GET_MY_USER_DOC,
    GET_MY_EVENTS_DOC,
    GET_MY_TEAMS_DOC,
)

users_user_namespace = Namespace("/users", description="user endpoints for users")


@users_user_namespace.route("/me")
class UserProfile(Resource):
    @user_endpoint()
    @users_user_namespace.doc(**GET_MY_USER_DOC)
    def get(self, current_user, **kwargs):
        """Get my user information"""
        return success_response(current_user)

@users_user_namespace.route("/me/events")
class UserEvents(Resource):
    @user_endpoint()
    @users_user_namespace.doc(**GET_MY_EVENTS_DOC)
    def get(self, current_user, **kwargs):
        """Get my events"""
        events = current_user.get_events()
        return success_response(events)

@users_user_namespace.route("/me/teams")
class UserTeams(Resource):
    @user_endpoint()
    @users_user_namespace.doc(**GET_MY_TEAMS_DOC)
    def get(self, current_user, **kwargs):
        """Get my teams"""
        teams = current_user.get_teams()
        return success_response(teams)
