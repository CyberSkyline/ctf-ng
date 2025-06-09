# /plugin/admin/routes/admin.py

from flask import request
from flask_restx import Namespace, Resource
from CTFd.utils.decorators import admins_only
from datetime import datetime

from ... import config
from ..controllers.database_controller import DatabaseController
from ...utils.api_responses import controller_response, error_response, success_response
from ...utils.decorators import handle_integrity_error
from ...utils.logger import get_logger
from ...utils import get_current_user_id
from ...utils.validators import validate_admin_reset, validate_admin_world_reset

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
        },
    )
    def get(self):
        """Get detailed system stats including per world breakdowns.

        Returns:
            JSON response with detailed stats and potential issues.
        """
        result = DatabaseController.get_detailed_stats()

        if result["success"]:
            logger.info(
                "Admin accessed detailed stats",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "worlds_count": len(result.get("worlds", [])),
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
        },
    )
    def get(self):
        """Get basic data counts for all plugin entities.

        Returns:
            JSON response with counts of worlds, teams, users, and memberships.
        """
        result = DatabaseController.get_data_counts()

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
            confirm (str): Must be {ADMIN_RESET_CONFIRMATION} to proceed.

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

        result = DatabaseController.reset_all_plugin_data()

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


@admin_namespace.route("/worlds/<int:world_id>/reset")
@admin_namespace.param("world_id", "World ID")
class AdminWorldReset(Resource):
    @admins_only
    @handle_integrity_error
    @admin_namespace.doc(
        description="Reset all data for a specific world (Admin only)",
        responses={
            200: "Success - World data reset",
            400: "Bad request - World does not exist",
            403: "Forbidden - Admin access required",
            500: "Internal error - Reset failed",
        },
    )
    def post(self, world_id):
        """Reset all data for a specific world.

        Args:
            world_id (int): The world ID to reset.

        Request Body:
            confirm (str): Must be 'DELETE_WORLD_DATA' to proceed.

        Returns:
            JSON response with deletion results or error.
        """
        data = request.get_json() or {}

        is_valid, errors = validate_admin_world_reset(data)
        if not is_valid:
            logger.warning(
                "Validation failed for world reset",
                extra={
                    "context": {
                        "errors": errors,
                        "admin_id": get_current_user_id(),
                        "endpoint": "admin_world_reset",
                        "world_id": world_id,
                    }
                },
            )
            return {"success": False, "errors": errors}, 400

        logger.warning(
            "Admin initiated world data reset",
            extra={
                "context": {
                    "admin_id": get_current_user_id(),
                    "world_id": world_id,
                    "operation": "RESET_WORLD_DATA",
                    "confirmation": data.get("confirm"),
                }
            },
        )

        result = DatabaseController.reset_world_data(world_id)

        if result["success"]:
            logger.warning(
                "Admin completed world data reset",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "world_id": world_id,
                        "deleted_counts": result.get("deleted", {}),
                    }
                },
            )
            return success_response(result)
        else:
            status_code = 404 if "not found" in result["error"].lower() else 500
            logger.error(
                "Admin world reset failed",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "world_id": world_id,
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

        result = DatabaseController.cleanup_orphaned_data()

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


@admin_namespace.route("/health")
class AdminHealth(Resource):
    @admins_only
    @handle_integrity_error
    @admin_namespace.doc(
        description="Check system health and data integrity (Admin only)",
        responses={
            200: "Success - System health report",
            403: "Forbidden - Admin access required",
        },
    )
    def get(self):
        """Check system health and data integrity.

        Returns:
            JSON response with health report and warnings.
        """
        counts = DatabaseController.get_data_counts()
        detailed = DatabaseController.get_detailed_stats()

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
            "worlds_count": len(detailed.get("worlds", [])),
            "empty_teams_count": detailed.get("total_empty_teams", 0),
            "warnings": [],
        }

        if counts["users"] > 0 and counts["memberships"] == 0:
            health_report["warnings"].append("Users exist but no team memberships found")

        if counts["teams"] > 0 and counts["memberships"] == 0:
            health_report["warnings"].append("Teams exist but no memberships found")

        if (
            counts["teams"] > 0
            and detailed.get("total_empty_teams", 0) / counts["teams"] > config.EMPTY_TEAMS_WARNING_THRESHOLD
        ):
            health_report["warnings"].append(
                f"More than {int(config.EMPTY_TEAMS_WARNING_THRESHOLD * 100)}% of teams are empty"
            )

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
