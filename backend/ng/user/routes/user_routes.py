from flask_restx import Namespace, Resource

from ...core.utils import success_response
from ...core.middleware import (
    user_endpoint,
)

users_user_namespace = Namespace("/users", description="user endpoints for users")

@users_user_namespace.route("/me")
class UserProfile(Resource):
    @user_endpoint()
    @users_user_namespace.doc(description="Get my user information",
                              responses={
                                  200: "Success",
                                  404: "User not found",
                              })
    def get(self, current_user, **kwargs):
        """Get my user information"""
        return success_response(current_user)

@users_user_namespace.route("/me/events")
class UserEvents(Resource):
    @user_endpoint()
    @users_user_namespace.doc(description="Get my events",
                              responses={
                                  200: "Success",
                                  404: "User not found",
                              })
    def get(self, current_user, **kwargs):
        """Get my events"""
        events = current_user.get_events()
        return success_response(events)

@users_user_namespace.route("/me/teams")
class UserTeams(Resource):
    @user_endpoint()
    @users_user_namespace.doc(description="Get my teams",
                              responses={
                                  200: "Success",
                                  404: "User not found",
                              })
    def get(self, current_user, **kwargs):
        """Get my teams"""
        teams = current_user.get_teams()
        return success_response(teams)