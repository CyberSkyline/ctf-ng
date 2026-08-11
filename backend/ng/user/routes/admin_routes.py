from flask_restx import Namespace, Resource

from ...core.utils import success_response, error_response
from ...core.middleware import (
    admin_endpoint,
)
from ...permissions.models.enums import RoleEnum
from ...permissions.controllers.get_user_roles import get_user_roles

from ...core.middleware.loaders import (
    LoaderType,
    load_user,
    load_indvidual_container_by_user,
)

from ..models.User import User
from ..controllers.ban_user import (
    ban_user,
    unban_user,
)


users_admin_namespace = Namespace("/admin/users", description="user endpoints for admins")

@users_admin_namespace.route("")
class UsersAdminResource(Resource):
    @admin_endpoint()
    @users_admin_namespace.doc(
        description="Get all users",
        responses={
            200: "Success",
            403: "Forbidden - Admin access required",
            500: "Internal server error"
        },
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
            200: "Success",
            403: "Forbidden - Admin access required",
            404: "User not found",
            500: "Internal server error"
        },
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
                "name": "new_username",
                "email": "new_email@example.com",
                }
            }
        },
        responses={
            200: "User updated successfully",
            404: "User not found",
            403: "Forbidden - Admin access required",
            500: "Internal server error",
        },
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
            403: "Forbidden - Admin access required",
            404: "User not found",
            500: "Internal server error",
        },
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
            403: "Forbidden - Admin access required",
            500: "Internal server error",
        },
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
            403: "Forbidden - Admin access required",
            500: "Internal server error",
        },
    )
    def get(self, user_id, target_user, **kwargs):
        """Get teams for a specific user"""
        teams = target_user.get_teams()
        return success_response(teams)

@users_admin_namespace.route("/<int:user_id>/container")
class UserIndvidualContainer(Resource):
    @admin_endpoint()
    @users_admin_namespace.doc(
        description="Get user's container",
        responses={
            200: "Sucess",
            400: "Bad request"
        }
    )
    @load_indvidual_container_by_user()
    def get(self, user_id, indvidual_container, **kwargs):
        data = indvidual_container.serialize()
        return success_response(data)

@users_admin_namespace.route("/<int:user_id>/container/status")
class UserIndvidualContainerStatus(Resource):
    @admin_endpoint()
    @users_admin_namespace.doc(
        description="Get current status of user's container",
        responses={
            200: "Sucess",
            400: "Bad request"
        }
    )
    @load_indvidual_container_by_user()
    def get(self, user_id, indvidual_container, **kwargs):
        data = indvidual_container.get_status()
        return success_response(data)

@users_admin_namespace.route("/<int:user_id>/container/challenge")
class UserIndvidualContainerCurrentChallenge(Resource):
    @admin_endpoint()
    @users_admin_namespace.doc(
        description="Get current challenge user's indvidual container is connected to",
        responses={
            200: "Sucess",
            400: "Bad request"
        }
    )
    @load_indvidual_container_by_user()
    def get(self, indvidual_container, user_id, **kwargs):
        data = indvidual_container.get_current_challenge()
        return success_response({
            "challenge_id": data,
        })

@users_admin_namespace.route("/<int:user_id>/container/restart")
class UserIndvidualContainerRestart(Resource):
    @admin_endpoint()
    @users_admin_namespace.doc(
        description="Restart a user's indvidual container",
        responses={
            200: "Sucess",
            400: "Bad request"
        }
    )
    @load_indvidual_container_by_user()
    def post(self, indvidual_container, user_id, **kwargs):
        indvidual_container.restart()
        return success_response(True)

@users_admin_namespace.route("/<int:user_id>/container/recycle")
class UserIndvidualContainerRecycle(Resource):
    @admin_endpoint()
    @users_admin_namespace.doc(
        description="Delete a user's indvidual container while keeping the db object",
        responses={
            200: "Sucess",
            400: "Bad request"
        }
    )
    @load_indvidual_container_by_user()
    def post(self, user_id, indvidual_container, **kwargs):
        indvidual_container.recycle()
        res = indvidual_container.serialize()
        return success_response(res)

@users_admin_namespace.route("/<int:user_id>/container/delete")
class UserIndvidualContainerDelete(Resource):
    @admin_endpoint()
    @users_admin_namespace.doc(
        description="Delete a user's indvidual container as well as the db object",
        responses={
            200: "Sucess",
            400: "Bad request"
        }
    )
    @load_indvidual_container_by_user()
    def post(self, user_id, indvidual_container, **kwargs):
        indvidual_container.delete()
        return success_response(True)

@users_admin_namespace.route("/<int:user_id>/ban")
class UserBan(Resource):
    @admin_endpoint()
    @load_user(source=LoaderType.PARAM, output_key="target_user")
    @users_admin_namespace.doc(
        description="Ban a user",
        responses={
            200: "User banned successfully",
            403: "Forbidden - Admin access required",
            404: "User not found",
            500: "Internal server error",
        },
    )
    def post(self, user_id, target_user, **kwargs):
        """
        Ban a user
        """
        if RoleEnum.ADMIN in get_user_roles(target_user.id):
            return error_response("Cannot ban an admin user", "ban", 403)

        ban_user(target_user)
        return success_response()


@users_admin_namespace.route("/<int:user_id>/unban")
class UserUnban(Resource):
    @admin_endpoint()
    @load_user(source=LoaderType.PARAM, output_key="target_user")
    @users_admin_namespace.doc(
        description="Unban a user",
        responses={
            200: "User unbanned successfully",
            403: "Forbidden - Admin access required",
            404: "User not found",
            500: "Internal server error",
        },
    )
    def post(self, user_id, target_user, **kwargs):
        """
        Unban a user
        """
        unban_user(target_user)
        return success_response()
