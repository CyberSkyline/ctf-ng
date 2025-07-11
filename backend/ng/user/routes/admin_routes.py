from flask_restx import Namespace, Resource

from ...core.utils import success_response
from ...core.middleware import (
    admin_endpoint,
)

from ...core.middleware.loaders import (
    LoaderType,
    load_user,
)

from ..models.User import User

users_admin_namespace = Namespace("/admin/users", description="user endpoints for admins")

@users_admin_namespace.route("")
class UsersAdminResource(Resource):
    @admin_endpoint()
    def get(self):
        """Get all users on the system"""
        return success_response(User.get_all_users())

#     @admin_endpoint(json_required=True, validation_func=User.validate)
#     def post(self, validated_data):
#         """Create a new user"""
#         data = validated_data
#         return User.create_user(**data)

@users_admin_namespace.route("/<int:user_id>")
class UserAdminResource(Resource):
    @admin_endpoint()
    @load_user(source=LoaderType.PARAM, output_key="target_user")
    def get(self, user_id, target_user):
        """Get a specific user by ID"""
        return success_response(target_user)

    @admin_endpoint(json_required=True, validation_func=User.validate)
    @load_user(source=LoaderType.PARAM, output_key="target_user")
    def put(self, user_id, target_user, validated_data):
        """Update a specific user"""
        target_user.update(**validated_data)
        return success_response()

    # @admin_endpoint()
    # @load_user(source=LoaderType.PARAM, output_key="target_user")
    # def delete(self, target_user):
    #     # TODO implement
    #     return success_response()

@users_admin_namespace.route("/<int:user_id>/events")
class UserEventsAdminResource(Resource):
    @admin_endpoint()
    @load_user(source=LoaderType.PARAM, output_key="target_user")
    def get(self, user_id, target_user):
        """Get events for a specific user"""
        events = target_user.get_events()
        return success_response(events)
    
@users_admin_namespace.route("/<int:user_id>/teams")
class UserTeamsAdminResource(Resource):
    @admin_endpoint()
    @load_user(source=LoaderType.PARAM, output_key="target_user")
    def get(self, user_id, target_user):
        """Get teams for a specific user"""
        teams = target_user.get_teams()
        return success_response(teams)