"""
Administrative operations and system management API routes.
"""

from flask_restx import Namespace, Resource
from ...core.utils import utc_now

from ..controllers import (
    get_data_counts,
    get_detailed_stats,
    reset_all_plugin_data,
    reset_event_data,
)
from ...core.utils import success_response
from ...core.middleware.loaders import (
    LoaderType,
    load_event,
)

from ...core.middleware import (
    admin_endpoint,
)
from ..docs.api import (
    GET_DETAILED_STATS_DOC,
    GET_DATA_COUNTS_DOC,
    RESET_ALL_DATA_DOC,
    RESET_EVENT_DATA_DOC,
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
    @admin_namespace.doc(**RESET_ALL_DATA_DOC)
    def post(self):
        """Reset all data"""
        result = reset_all_plugin_data()
        return success_response(result)


@admin_namespace.route("/events/<int:event_id>/reset")
class AdminEventReset(Resource):
    @load_event(LoaderType.PARAM)
    @admin_namespace.doc(**RESET_EVENT_DATA_DOC)
    def post(self, event_id):
        """Reset event data"""
        reset_event_data(event_id)
        return success_response()

@admin_namespace.route("/health")
class AdminHealth(Resource):
    @admin_endpoint()
    @admin_namespace.doc(**SYSTEM_HEALTH_DOC)
    def get(self):
        """Check system health"""
        counts = get_data_counts()
        detailed = get_detailed_stats()
        health_report = {
            "timestamp": utc_now().isoformat(),
            "data_counts": counts,
            "events_count": counts["events"],
            "empty_teams_count": detailed.get("total_empty_teams", 0),
        }
        return success_response(health_report)








