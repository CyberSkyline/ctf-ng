from flask_restx import Namespace, Resource

from ...core.utils import success_response
from ...core.middleware import (
    user_endpoint,
)

users_user_namespace = Namespace("/users", description="user endpoints for users")

@users_user_namespace.route("/me")
class UserProfile(Resource):
    @user_endpoint()
    def get(self, user):
        """Get my user information"""
        return success_response(user)

@users_user_namespace.route("/me/events")
class UserEvents(Resource):
    @user_endpoint()
    def get(self, user):
        """Get my events"""
        # TODO - implement
        return success_response([ ])
    
# @users_user_namespace.route("/me/teams")
# class UserTeams(Resource):
#     @user_endpoint()
#     def get(self, user):
#         """Get my teams"""
#         # TODO - implement
#         return success_response([ ])