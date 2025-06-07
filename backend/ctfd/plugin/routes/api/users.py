# plugin/routes/api/users.py

from flask_restx import Namespace, Resource
from CTFd.utils.decorators import authed_only, admins_only
from CTFd.utils.user import get_current_user

from ...controllers.user_controller import UserController
from ...utils.api_responses import controller_response, error_response

users_namespace = Namespace("users", description="user team operations")


@users_namespace.route("/me/teams")
class UserTeams(Resource):
    @authed_only
    @users_namespace.doc(
        description="Get current user's team memberships across all worlds",
        responses={
            200: "Success - Returns user teams across all worlds",
            403: "Forbidden - User not authenticated",
        },
    )
    def get(self):
        """Get current user's team memberships across all worlds.

        Returns:
            JSON response with list of user's teams and world info.
        """
        current_user = get_current_user()
        if not current_user:
            return error_response("User not found in session", "auth", 403)

        result = UserController.get_user_teams(current_user.id)

        return controller_response(result, error_field="user")


@users_namespace.route("/me/worlds/<int:world_id>/teams")
@users_namespace.param("world_id", "World ID")
class UserWorldTeams(Resource):
    @authed_only
    @users_namespace.doc(
        description="Get current user's team in a specific world",
        responses={
            200: "Success - Returns user team in specified world",
            403: "Forbidden - User not authenticated",
            404: "Not found - World does not exist",
        },
    )
    def get(self, world_id):
        """Get current user's team membership in a world.

        Args:
            world_id (int): The world ID to check team membership.

        Returns:
            JSON response with team info if user is in a team, or None if not.
        """
        current_user = get_current_user()
        if not current_user:
            return error_response("User not found in session", "auth", 403)

        result = UserController.get_user_teams_in_world(current_user.id, world_id)

        return controller_response(result, error_field="user")


@users_namespace.route("/me/worlds/<int:world_id>/eligibility")
@users_namespace.param("world_id", "World ID")
class UserWorldEligibility(Resource):
    @authed_only
    @users_namespace.doc(
        description="Check if current user can join a team in the specified world",
        responses={
            200: "Success - Returns eligibility status",
            403: "Forbidden - User not authenticated",
        },
    )
    def get(self, world_id):
        """Check if current user can join a team in the world.

        Args:
            world_id (int): The world ID to check eligibility for.

        Returns:
            JSON response with eligibility status and reason if not eligible.
        """
        current_user = get_current_user()
        if not current_user:
            return error_response("User not found in session", "auth", 403)

        result = UserController.can_join_team_in_world(current_user.id, world_id)

        return controller_response(result, error_field="eligibility")


@users_namespace.route("/me/stats")
class UserStats(Resource):
    @authed_only
    @users_namespace.doc(
        description="Get current user's participation statistics across all worlds",
        responses={
            200: "Success - Returns user participation statistics",
            403: "Forbidden - User not authenticated",
        },
    )
    def get(self):
        """Get current user's participation stats across all worlds.

        Returns:
            JSON response with participation stats and metrics.
        """
        current_user = get_current_user()
        if not current_user:
            return error_response("User not found in session", "auth", 403)

        result = UserController.get_user_stats(current_user.id)

        return controller_response(result, error_field="stats")


# Admin endpoints for managing other users
@users_namespace.route("/<int:user_id>/teams")
@users_namespace.param("user_id", "User ID")
class AdminUserTeams(Resource):
    @admins_only
    @users_namespace.doc(
        description="Get any user's team memberships (Admin only)",
        responses={
            200: "Success - Returns user teams",
            403: "Forbidden - Admin access required",
            404: "Not found - User does not exist",
        },
    )
    def get(self, user_id):
        """Get any user's team memberships across all worlds (Admin only).

        Args:
            user_id (int): The user ID to get teams for.

        Returns:
            JSON response with list of user's teams and world info.
        """
        result = UserController.get_user_teams(user_id)

        return controller_response(result, error_field="user")


@users_namespace.route("/<int:user_id>/stats")
@users_namespace.param("user_id", "User ID")
class AdminUserStats(Resource):
    @admins_only
    @users_namespace.doc(
        description="Get any user's participation statistics (Admin only)",
        responses={
            200: "Success - Returns user statistics",
            403: "Forbidden - Admin access required",
            404: "Not found - User does not exist",
        },
    )
    def get(self, user_id):
        """Get any user's participation stats across all worlds (Admin only).

        Args:
            user_id (int): The user ID to get stats for.

        Returns:
            JSON response with participation stats and metrics.
        """
        result = UserController.get_user_stats(user_id)

        return controller_response(result, error_field="stats")
