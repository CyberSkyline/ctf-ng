"""
Administrative operations and system management API routes.
"""

from flask_restx import Namespace, Resource
from ...core.utils import utc_now
from ... import config

from ..controllers import (
    cleanup_orphaned_data,
    cleanup_headless_teams,
    get_data_counts,
    get_detailed_stats,
    reset_all_plugin_data,
    reset_event_data,
)
from ...core.utils import success_response
from ...core.validation import validate_admin_reset, validate_admin_event_reset
from ...core.middleware import (
    admin_endpoint,
    load_event,
)
from ...core.docs import (
    GET_DETAILED_STATS_DOC,
    GET_DATA_COUNTS_DOC,
    RESET_ALL_DATA_DOC,
    RESET_EVENT_DATA_DOC,
    CLEANUP_ORPHANED_DATA_DOC,
    CLEANUP_HEADLESS_TEAMS_DOC,
    SYSTEM_HEALTH_DOC,
)

admin_namespace = Namespace("admin", description="admin operations")


@admin_namespace.route("/stats")
class AdminStats(Resource):
    @admin_endpoint()
    @admin_namespace.doc(**GET_DETAILED_STATS_DOC)
    def get(self):
        """Get system stats"""
        result = get_detailed_stats()
        return success_response(result)


@admin_namespace.route("/stats/counts")
class AdminStatsCounts(Resource):
    @admin_endpoint()
    @admin_namespace.doc(**GET_DATA_COUNTS_DOC)
    def get(self):
        """Get data counts"""
        result = get_data_counts()
        return success_response(result)


@admin_namespace.route("/reset")
class AdminReset(Resource):
    @admin_endpoint(json_required=True, validation_func=validate_admin_reset)
    @admin_namespace.doc(**RESET_ALL_DATA_DOC)
    def post(self):
        """Reset all data"""
        result = reset_all_plugin_data()
        return success_response(result)


@admin_namespace.route("/events/<int:event_id>/reset")
class AdminEventReset(Resource):
    @admin_endpoint(json_required=True, validation_func=validate_admin_event_reset)
    @load_event()
    @admin_namespace.doc(**RESET_EVENT_DATA_DOC)
    def post(self, event_id):
        """Reset event data"""
        result = reset_event_data(event_id)
        return success_response(result)


@admin_namespace.route("/cleanup")
class AdminCleanup(Resource):
    @admin_endpoint()
    @admin_namespace.doc(**CLEANUP_ORPHANED_DATA_DOC)
    def post(self):
        """Cleanup orphaned data"""
        result = cleanup_orphaned_data()
        return success_response(result)


@admin_namespace.route("/cleanup/headless-teams")
class AdminCleanupHeadlessTeams(Resource):
    @admin_endpoint()
    @admin_namespace.doc(**CLEANUP_HEADLESS_TEAMS_DOC)
    def post(self):
        """Fix headless teams"""
        result = cleanup_headless_teams()
        return success_response(result)


@admin_namespace.route("/health")
class AdminHealth(Resource):
    @admin_endpoint()
    @admin_namespace.doc(**SYSTEM_HEALTH_DOC)
    def get(self):
        """Check system health"""
        counts = get_data_counts()
        detailed = get_detailed_stats()
        health_report = {
            "status": "healthy",
            "timestamp": utc_now().isoformat(),
            "data_counts": counts,
            "events_count": counts["events"],
            "empty_teams_count": detailed.get("total_empty_teams", 0),
            "warnings": _generate_health_warnings(counts, detailed),
        }
        return success_response({"success": True, **health_report})


def _generate_health_warnings(counts, detailed):
    """Generate health warnings based on data counts and statistics."""
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
