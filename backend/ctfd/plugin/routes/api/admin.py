# plugin/routes/api/admin.py

from flask import request
from flask_restx import Namespace, Resource
from CTFd.utils.decorators import admins_only

from ...controllers.database_controller import DatabaseController
from ...utils.api_responses import controller_response, error_response

admin_namespace = Namespace("admin", description="admin operations")


@admin_namespace.route("/stats")
class AdminStats(Resource):
    @admins_only
    @admin_namespace.doc(
        description="Get comprehensive system statistics (Admin only)",
        responses={
            200: "Success - Returns detailed system statistics",
            403: "Forbidden - Admin access required",
        },
    )
    def get(self):
        """Get detailed system stats including per-world breakdowns.

        Returns:
            JSON response with detailed stats and potential issues.
        """
        result = DatabaseController.get_detailed_stats()

        return controller_response(result, error_field="stats")


@admin_namespace.route("/stats/counts")
class AdminStatsCounts(Resource):
    @admins_only
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
            return error_response(result["error"], "counts", 400)
        else:
            from ...utils.api_responses import success_response

            return success_response(result)


@admin_namespace.route("/reset")
class AdminReset(Resource):
    @admins_only
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
            confirm (str): Must be 'DELETE_ALL_DATA' to proceed.

        Returns:
            JSON response with deletion results or error.
        """
        data = request.get_json() or {}
        confirmation = data.get("confirm")

        if confirmation != "DELETE_ALL_DATA":
            return error_response(
                "You must send 'confirm': 'DELETE_ALL_DATA' to proceed with this destructive operation",
                "confirmation",
                400,
            )

        result = DatabaseController.reset_all_plugin_data()

        if result["success"]:
            from ...utils.api_responses import success_response

            return success_response(result)
        else:
            return error_response(result["error"], "reset", 500)


@admin_namespace.route("/worlds/<int:world_id>/reset")
@admin_namespace.param("world_id", "World ID")
class AdminWorldReset(Resource):
    @admins_only
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
        confirmation = data.get("confirm")

        if confirmation != "DELETE_WORLD_DATA":
            return error_response(
                "You must send 'confirm': 'DELETE_WORLD_DATA' to proceed",
                "confirmation",
                400,
            )

        result = DatabaseController.reset_world_data(world_id)

        if result["success"]:
            from ...utils.api_responses import success_response

            return success_response(result)
        else:
            status_code = 400 if "does not exist" in result["error"] else 500
            return error_response(result["error"], "reset", status_code)


@admin_namespace.route("/cleanup")
class AdminCleanup(Resource):
    @admins_only
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
        result = DatabaseController.cleanup_orphaned_data()

        if result["success"]:
            from ...utils.api_responses import success_response

            return success_response(result)
        else:
            return error_response(result["error"], "cleanup", 500)


@admin_namespace.route("/health")
class AdminHealth(Resource):
    @admins_only
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
            return error_response("Unable to fetch system statistics", "health", 500)

        from datetime import datetime

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

        if detailed.get("total_empty_teams", 0) > counts["teams"] * 0.5:
            health_report["warnings"].append("More than 50% of teams are empty")

        from ...utils.api_responses import success_response

        return success_response({"success": True, **health_report})
