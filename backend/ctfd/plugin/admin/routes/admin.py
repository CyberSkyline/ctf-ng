"""
/backend/ctfd/plugin/admin/routes/admin.py
Defines the public API routes for all administrative operations and system management.
"""

from flask import request
from flask_restx import Namespace, Resource
from CTFd.utils.decorators import admins_only
from datetime import datetime

from ... import config
from ..controllers import (
    cleanup_orphaned_data,
    cleanup_headless_teams,
    get_data_counts,
    get_detailed_stats,
    reset_all_plugin_data,
    reset_event_data,
)
from ...utils.api_responses import controller_response, error_response, success_response
from ...utils.decorators import handle_integrity_error
from ...utils.logger import get_logger
from ...utils import get_current_user_id
from ...utils import validate_admin_reset, validate_admin_event_reset

admin_namespace = Namespace("admin", description="admin operations")
logger = get_logger(__name__)


@admin_namespace.route("/stats")
class AdminStats(Resource):
    @admins_only
    @handle_integrity_error
    @admin_namespace.doc(
        description="Get comprehensive system statistics (Admin only)",
        responses={
            200: "Success - Returns detailed system statistics",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error",
        },
    )
    def get(self):
        """Get detailed system stats including per event breakdowns.

        Returns:
            JSON response with detailed stats and potential issues.
        """
        result = get_detailed_stats()

        if result["success"]:
            logger.info(
                "Admin accessed detailed stats",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "events_count": len(result.get("events", [])),
                    }
                },
            )

        return controller_response(result, error_field="stats")


@admin_namespace.route("/stats/counts")
class AdminStatsCounts(Resource):
    @admins_only
    @handle_integrity_error
    @admin_namespace.doc(
        description="Get basic data counts (Admin only)",
        responses={
            200: "Success - Returns data counts",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error",
        },
    )
    def get(self):
        """Get basic data counts for all plugin entities.

        Returns:
            JSON response with counts of events, teams, users, and team members.
        """
        result = get_data_counts()

        if "error" in result:
            logger.warning(
                "Admin stats counts failed",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "error": result["error"],
                    }
                },
            )
            return error_response(result["error"], "counts", 400)
        else:
            logger.info(
                "Admin accessed data counts",
                extra={"context": {"admin_id": get_current_user_id(), "counts": result}},
            )
            return success_response(result)


@admin_namespace.route("/reset")
class AdminReset(Resource):
    @admins_only
    @handle_integrity_error
    @admin_namespace.doc(
        description="Reset ALL plugin data - WARNING: This deletes everything! (Admin only)",
        responses={
            200: "Success - All data reset",
            403: "Forbidden - Admin access required",
            500: "Internal error - Reset failed",
        },
    )
    def post(self):
        """Reset ALL plugin data - WARNING: This deletes everything!

        Request Body:
            confirm (str): Must be ADMIN_RESET_CONFIRMATION to proceed.

        Returns:
            JSON response with deletion results or error.
        """
        data = request.get_json() or {}

        is_valid, errors = validate_admin_reset(data)
        if not is_valid:
            logger.warning(
                "Validation failed for admin reset",
                extra={
                    "context": {
                        "errors": errors,
                        "admin_id": get_current_user_id(),
                        "endpoint": "admin_reset",
                    }
                },
            )
            return {"success": False, "errors": errors}, 400

        logger.warning(
            "Admin initiated FULL DATA RESET",
            extra={
                "context": {
                    "admin_id": get_current_user_id(),
                    "operation": "RESET_ALL_PLUGIN_DATA",
                    "confirmation": data.get("confirm"),
                }
            },
        )

        result = reset_all_plugin_data()

        if result["success"]:
            logger.warning(
                "Admin completed FULL DATA RESET",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "deleted_counts": result.get("deleted", {}),
                    }
                },
            )
            return success_response(result)
        else:
            logger.error(
                "Admin full reset failed",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "error": result["error"],
                    }
                },
            )
            return error_response(result["error"], "reset", 500)


@admin_namespace.route("/events/<int:event_id>/reset")
@admin_namespace.param("event_id", "Event ID")
class AdminEventReset(Resource):
    @admins_only
    @handle_integrity_error
    @admin_namespace.doc(
        description="Reset all data for a specific event (Admin only)",
        responses={
            200: "Success - Event data reset",
            400: "Bad request - Event does not exist",
            403: "Forbidden - Admin access required",
            500: "Internal error - Reset failed",
        },
    )
    def post(self, event_id):
        """Reset all data for a specific event.

        Args:
            event_id (int): The event ID to reset.

        Request Body:
            confirm (str): Must be 'DELETE_EVENT_DATA' to proceed.

        Returns:
            JSON response with deletion results or error.
        """
        data = request.get_json() or {}

        is_valid, errors = validate_admin_event_reset(data)
        if not is_valid:
            logger.warning(
                "Validation failed for event reset",
                extra={
                    "context": {
                        "errors": errors,
                        "admin_id": get_current_user_id(),
                        "endpoint": "admin_event_reset",
                        "event_id": event_id,
                    }
                },
            )
            return {"success": False, "errors": errors}, 400

        logger.warning(
            "Admin initiated event data reset",
            extra={
                "context": {
                    "admin_id": get_current_user_id(),
                    "event_id": event_id,
                    "operation": "RESET_EVENT_DATA",
                    "confirmation": data.get("confirm"),
                }
            },
        )

        result = reset_event_data(event_id)

        if result["success"]:
            logger.warning(
                "Admin completed event data reset",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "event_id": event_id,
                        "deleted_counts": result.get("deleted", {}),
                    }
                },
            )
            return success_response(result)
        else:
            status_code = 404 if "not found" in result["error"].lower() else 500
            logger.error(
                "Admin event reset failed",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "event_id": event_id,
                        "error": result["error"],
                    }
                },
            )
            return error_response(result["error"], "reset", status_code)


@admin_namespace.route("/cleanup")
class AdminCleanup(Resource):
    @admins_only
    @handle_integrity_error
    @admin_namespace.doc(
        description="Clean up orphaned data (users with no teams, etc.) (Admin only)",
        responses={
            200: "Success - Cleanup completed",
            403: "Forbidden - Admin access required",
            500: "Internal error - Cleanup failed",
        },
    )
    def post(self):
        """Clean up orphaned data like users with no teams.

        Returns:
            JSON response with cleanup results.
        """
        logger.warning(
            "Admin initiated cleanup operation",
            extra={
                "context": {
                    "admin_id": get_current_user_id(),
                    "operation": "CLEANUP_ORPHANED_DATA",
                }
            },
        )

        result = cleanup_orphaned_data()

        if result["success"]:
            logger.warning(
                "Admin completed cleanup operation",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "cleaned_counts": result.get("cleaned", {}),
                    }
                },
            )
            return success_response(result)
        else:
            logger.error(
                "Admin cleanup failed",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "error": result["error"],
                    }
                },
            )
            return error_response(result["error"], "cleanup", 500)


@admin_namespace.route("/cleanup/headless-teams")
class AdminCleanupHeadlessTeams(Resource):
    @admins_only
    @handle_integrity_error
    @admin_namespace.doc(
        description="Fix teams without captains by auto-promoting oldest member (Admin only)",
        responses={
            200: "Success - Headless teams cleanup completed",
            403: "Forbidden - Admin access required",
            500: "Internal error - Cleanup failed",
        },
    )
    def post(self):
        """Fix teams without captains due to user deletion.

        This endpoint finds teams that have members but no captain
        and automatically promotes the oldest member to captain role.

        Returns:
            JSON response with cleanup results.
        """
        logger.warning(
            "Admin initiated headless teams cleanup",
            extra={
                "context": {
                    "admin_id": get_current_user_id(),
                    "operation": "CLEANUP_HEADLESS_TEAMS",
                }
            },
        )

        result = cleanup_headless_teams()

        if result["success"]:
            logger.warning(
                "Admin completed headless teams cleanup",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "message": result["message"],
                    }
                },
            )
            return success_response(result)
        else:
            logger.error(
                "Admin headless teams cleanup failed",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "error": result.get("error", "Unknown error"),
                    }
                },
            )
            return error_response(result.get("error", "Cleanup failed"), "cleanup", 500)


@admin_namespace.route("/health")
class AdminHealth(Resource):
    @admins_only
    @handle_integrity_error
    @admin_namespace.doc(
        description="Check system health and data integrity (Admin only)",
        responses={
            200: "Success - System health report",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error",
        },
    )
    def get(self):
        """Check system health and data integrity.

        Returns:
            JSON response with health report and warnings.
        """
        counts = get_data_counts()
        detailed = get_detailed_stats()

        if "error" in counts or not detailed["success"]:
            logger.error(
                "Admin health check failed",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "error": "Unable to fetch system statistics",
                    }
                },
            )
            return error_response("Unable to fetch system statistics", "health", 500)

        health_report = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "data_counts": counts,
            "events_count": counts["events"],
            "empty_teams_count": detailed.get("total_empty_teams", 0),
            "warnings": [],
        }

        health_report["warnings"] = _generate_health_warnings(counts, detailed)

        logger.info(
            "Admin performed health check",
            extra={
                "context": {
                    "admin_id": get_current_user_id(),
                    "status": health_report["status"],
                    "warnings_count": len(health_report["warnings"]),
                }
            },
        )

        return success_response({"success": True, **health_report})


def _generate_health_warnings(counts, detailed):
    """Generate health warnings based on data counts and statistics.

    Args:
        counts: Dictionary of data counts
        detailed: Detailed statistics dictionary

    Returns:
        list: List of warning messages
    """
    warnings = []

    if counts["users"] > 0 and counts["team_members"] == 0:
        warnings.append("Users exist but no team members found")

    if counts["teams"] > 0 and counts["team_members"] == 0:
        warnings.append("Teams exist but no team members found")

    if (
        counts["teams"] > 0
        and detailed.get("total_empty_teams", 0) / counts["teams"] > config.EMPTY_TEAMS_WARNING_THRESHOLD
    ):
        warnings.append(f"More than {int(config.EMPTY_TEAMS_WARNING_THRESHOLD * 100)}% of teams are empty")

    return warnings
