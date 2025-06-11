"""
/backend/ctfd/plugin/user/routes/users.py
Defines the public API routes for user-specific data, including team affiliations and stats.
"""

from flask import g
from flask_restx import Namespace, Resource
from CTFd.utils.decorators import authed_only, admins_only

from ..controllers import (
    get_user_teams,
    get_user_teams_in_event,
    can_join_team_in_event,
    get_user_stats,
)
from ...utils.api_responses import controller_response
from ...utils.decorators import authed_user_required, handle_integrity_error
from ...utils.logger import get_logger
from ...utils import get_current_user_id

users_namespace = Namespace("users", description="user team operations")
logger = get_logger(__name__)


@users_namespace.route("/me/teams")
class UserTeams(Resource):
    @authed_only
    @authed_user_required
    @handle_integrity_error
    @users_namespace.doc(
        description="Get current user's teams across all events",
        responses={
            200: "Success - Returns user teams across all events",
            403: "Forbidden - User not authenticated",
            500: "Internal Server Error",
        },
    )
    def get(self):
        """Get current user's teams across all events.

        Returns:
            JSON response with list of user's teams and event info.
        """
        result = get_user_teams(g.user.id)

        if result["success"]:
            logger.info(
                "User teams retrieved",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "team_count": len(result.get("teams", [])),
                    }
                },
            )

        return controller_response(result, error_field="user")


@users_namespace.route("/me/events/<int:event_id>/teams")
@users_namespace.param("event_id", "Event ID")
class UserEventTeams(Resource):
    @authed_only
    @authed_user_required
    @handle_integrity_error
    @users_namespace.doc(
        description="Get current user's team in a specific event",
        responses={
            200: "Success - Returns user team in specified event",
            403: "Forbidden - User not authenticated",
            404: "Not found - Event does not exist",
            500: "Internal Server Error",
        },
    )
    def get(self, event_id):
        """Get current user's team membership in a event.

        Args:
            event_id (int): The event ID to check team membership.

        Returns:
            JSON response with team info if user is in a team, or None if not.
        """
        result = get_user_teams_in_event(g.user.id, event_id)

        if result["success"]:
            team_info = result.get("team")
            logger.info(
                "User event team membership retrieved",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "event_id": event_id,
                        "has_team": team_info is not None,
                        "team_id": team_info.get("id") if team_info else None,
                    }
                },
            )

        return controller_response(result, error_field="user")


@users_namespace.route("/me/events/<int:event_id>/eligibility")
@users_namespace.param("event_id", "Event ID")
class UserEventEligibility(Resource):
    @authed_only
    @authed_user_required
    @handle_integrity_error
    @users_namespace.doc(
        description="Check if current user can join a team in the specified event",
        responses={
            200: "Success - Returns eligibility status",
            403: "Forbidden - User not authenticated",
            500: "Internal Server Error",
        },
    )
    def get(self, event_id):
        """Check if current user can join a team in the event.

        Args:
            event_id (int): The event ID to check eligibility for.

        Returns:
            JSON response with eligibility status and reason if not eligible.
        """
        result = can_join_team_in_event(g.user.id, event_id)

        if result["success"]:
            logger.info(
                "User eligibility checked",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "event_id": event_id,
                        "can_join": result.get("can_join", False),
                    }
                },
            )

        return controller_response(result, error_field="eligibility")


@users_namespace.route("/me/stats")
class UserStats(Resource):
    @authed_only
    @authed_user_required
    @handle_integrity_error
    @users_namespace.doc(
        description="Get current user's participation statistics across all events",
        responses={
            200: "Success - Returns user participation statistics",
            403: "Forbidden - User not authenticated",
            500: "Internal Server Error",
        },
    )
    def get(self):
        """Get current user's participation stats across all events.

        Returns:
            JSON response with participation stats and metrics.
        """
        result = get_user_stats(g.user.id)

        if result["success"]:
            stats = result.get("stats", {})
            logger.info(
                "User stats retrieved",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "events_participated": stats.get("events_participated", 0),
                        "teams_joined": stats.get("teams_joined", 0),
                    }
                },
            )

        return controller_response(result, error_field="stats")


# Admin endpoints for managing other users
@users_namespace.route("/<int:user_id>/teams")
@users_namespace.param("user_id", "User ID")
class AdminUserTeams(Resource):
    @admins_only
    @handle_integrity_error
    @users_namespace.doc(
        description="Get any user's teams (Admin only)",
        responses={
            200: "Success - Returns user teams",
            403: "Forbidden - Admin access required",
            404: "Not found - User does not exist",
            500: "Internal Server Error",
        },
    )
    def get(self, user_id):
        """Get any user's teams across all events (Admin only).

        Args:
            user_id (int): The user ID to get teams for.

        Returns:
            JSON response with list of user's teams and event info.
        """
        result = get_user_teams(user_id)

        if result["success"]:
            logger.info(
                "Admin accessed user teams",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "target_user_id": user_id,
                        "team_count": len(result.get("teams", [])),
                    }
                },
            )
        else:
            logger.warning(
                "Admin user teams access failed",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "target_user_id": user_id,
                        "error": result.get("error"),
                    }
                },
            )

        return controller_response(result, error_field="user")


@users_namespace.route("/<int:user_id>/stats")
@users_namespace.param("user_id", "User ID")
class AdminUserStats(Resource):
    @admins_only
    @handle_integrity_error
    @users_namespace.doc(
        description="Get any user's participation statistics (Admin only)",
        responses={
            200: "Success - Returns user statistics",
            403: "Forbidden - Admin access required",
            404: "Not found - User does not exist",
            500: "Internal Server Error",
        },
    )
    def get(self, user_id):
        """Get any user's participation stats across all events (Admin only).

        Args:
            user_id (int): The user ID to get stats for.

        Returns:
            JSON response with participation stats and metrics.
        """
        result = get_user_stats(user_id)

        if result["success"]:
            stats = result.get("stats", {})
            logger.info(
                "Admin accessed user stats",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "target_user_id": user_id,
                        "events_participated": stats.get("events_participated", 0),
                        "teams_joined": stats.get("teams_joined", 0),
                    }
                },
            )
        else:
            logger.warning(
                "Admin user stats access failed",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "target_user_id": user_id,
                        "error": result.get("error"),
                    }
                },
            )

        return controller_response(result, error_field="stats")
