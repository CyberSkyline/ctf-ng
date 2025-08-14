from flask_restx import Namespace, Resource

from ...core.utils import success_response
from ...core.middleware import (
    admin_endpoint,
)

from ...core.middleware.loaders import (
    LoaderType,
    load_user,
    load_indvidual_container_by_user,
)

from ..models.User import User

from ._docs import (
    GET_ALL_USERS_DOC,
    GET_USER_DOC,
    UPDATE_USER_DOC,
    DELETE_USER_DOC,
    GET_USER_EVENTS_DOC,
    GET_USER_TEAMS_DOC,
)

users_admin_namespace = Namespace("/admin/users", description="user endpoints for admins")

@users_admin_namespace.route("")
class UsersAdminResource(Resource):
    @admin_endpoint()
    @users_admin_namespace.doc(**GET_ALL_USERS_DOC)
    def get(self, **kwargs):
        """Get all users on the system"""
        return success_response(User.get_all_users())

@users_admin_namespace.route("/<int:user_id>")
class UserAdminResource(Resource):
    @admin_endpoint()
    @load_user(source=LoaderType.PARAM, output_key="target_user")
    @users_admin_namespace.doc(**GET_USER_DOC)
    def get(self, user_id, target_user, **kwargs):
        """Get a specific user by ID"""
        return success_response(target_user)

    @admin_endpoint(json_required=True, validation_func=User.validate)
    @load_user(source=LoaderType.PARAM, output_key="target_user")
    @users_admin_namespace.doc(**UPDATE_USER_DOC)
    def put(self, user_id, target_user, validated_data, **kwargs):
        """Update a specific user"""
        target_user.update(**validated_data)
        return success_response(target_user)


@users_admin_namespace.route("/delete")
class UserDeleteAdminResource(Resource):
    @admin_endpoint(json_required=True)
    @load_user(source=LoaderType.BODY, output_key="target_user")
    @users_admin_namespace.doc(**DELETE_USER_DOC)
    def delete(self,target_user, **kwargs):
        """Delete a specific user"""
        target_user.delete()
        return success_response()

@users_admin_namespace.route("/<int:user_id>/events")
class UserEventsAdminResource(Resource):
    @admin_endpoint()
    @load_user(source=LoaderType.PARAM, output_key="target_user")
    @users_admin_namespace.doc(**GET_USER_EVENTS_DOC)
    def get(self, user_id, target_user, **kwargs):
        """Get events for a specific user"""
        events = target_user.get_events()
        return success_response(events)

@users_admin_namespace.route("/<int:user_id>/teams")
class UserTeamsAdminResource(Resource):
    @admin_endpoint()
    @load_user(source=LoaderType.PARAM, output_key="target_user")
    @users_admin_namespace.doc(**GET_USER_TEAMS_DOC)
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
    def get(self, user_id, indvidual_container):
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
    def get(self, user_id, indvidual_container):
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
    def get(self, indvidual_container, user_id):
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
    def get(self, indvidual_container, user_id):
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
    def get(self, user_id, indvidual_container):
        indvidual_container.recycle()
        res = indvidual_container.serialize()
        return success_response(res)
