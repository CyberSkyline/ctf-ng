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
    @users_admin_namespace.doc(
        description="Get all users",
        responses={
            200: "Success",
            403: "Permission denied",
        }
    )
    def get(self, **kwargs):
        """Get all users on the system"""
        return success_response(User.get_all_users())

@users_admin_namespace.route("/<int:user_id>")
class UserAdminResource(Resource):
    @admin_endpoint()
    @load_user(source=LoaderType.PARAM, output_key="target_user")
    @users_admin_namespace.doc(
        description="Get a specific user by ID",
        responses={
            200: "User retrieved successfully",
            404: "User not found",
            403: "Permission denied"
        }
    )
    def get(self, user_id, target_user, **kwargs):
        """Get a specific user by ID"""
        return success_response(target_user)

    @admin_endpoint(json_required=True, validation_func=User.validate)
    @load_user(source=LoaderType.PARAM, output_key="target_user")
    @users_admin_namespace.doc(
        description="Update a specific user by ID",
        params={
            "json_data": {
                "description": "User data in JSON format",
                "in": "body",
                "required": True,
                "example": {
                    "username": "new_username",
                    "email": "new_email@example.com",
                }
            }
        },
        responses={200: "User updated successfully", 404: "User not found", 403: "Permission denied"}
    )
    def put(self, user_id, target_user, validated_data, **kwargs):
        """Update a specific user"""
        target_user.update(**validated_data)
        return success_response(target_user)


@users_admin_namespace.route("/delete")
class UserDeleteAdminResource(Resource):
    @admin_endpoint(json_required=True)
    @load_user(source=LoaderType.BODY, output_key="target_user")
    @users_admin_namespace.doc(
        description="Delete a specific user by ID",
        params={
            "user_id": {
                "description": "ID of the user to delete",
                "in": "body",
                "required": True,
                "type": "integer",
                "example": {
                    "user_id": 123
                }
            }
        },
        responses={
            200: "User deleted successfully",
            404: "User not found",
            403: "Permission denied"
        }
    )
    def delete(self,target_user, **kwargs):
        """Delete a specific user"""
        target_user.delete()
        return success_response()

@users_admin_namespace.route("/<int:user_id>/events")
class UserEventsAdminResource(Resource):
    @admin_endpoint()
    @load_user(source=LoaderType.PARAM, output_key="target_user")
    @users_admin_namespace.doc(
        description="Get events for a specific user",
        responses={
            200: "Events retrieved successfully",
            404: "User not found",
            302: "Permission denied"
        }
    )
    def get(self, user_id, target_user, **kwargs):
        """Get events for a specific user"""
        events = target_user.get_events()
        return success_response(events)

@users_admin_namespace.route("/<int:user_id>/teams")
class UserTeamsAdminResource(Resource):
    @admin_endpoint()
    @load_user(source=LoaderType.PARAM, output_key="target_user")
    @users_admin_namespace.doc(
        description="Get teams for a specific user",
        responses={
            200: "Teams retrieved successfully",
            404: "User not found",
            302: "Permission denied"
        }
    )
    def get(self, user_id, target_user, **kwargs):
        """Get teams for a specific user"""
        teams = target_user.get_teams()
        return success_response(teams)