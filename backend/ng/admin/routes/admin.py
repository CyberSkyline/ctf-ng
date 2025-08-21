"""
Administrative operations and system management API routes.
"""

from flask_restx import Namespace, Resource
from flask import session
from ...core.utils import utc_now
from CTFd.utils.security.csrf import generate_nonce
from ..controllers import (
    get_data_counts,
    get_detailed_stats,
    reset_event_data,
)
from ...permissions.models.enums import PermissionEnum
from ...permissions.controllers.get_user_roles import get_user_roles
from ...core.utils import success_response, error_response
from ...core.middleware.loaders import (
    LoaderType,
    load_event,
    load_user
)
from ...core.utils.logger import get_logger
from ...core.middleware import (
    admin_endpoint,
    user_endpoint
)
from ...core.middleware.permission_middleware import (
    get_permissions,
)
from ..docs.api import (
    GET_DETAILED_STATS_DOC,
    GET_DATA_COUNTS_DOC,
    RESET_EVENT_DATA_DOC,
    SYSTEM_HEALTH_DOC,
)

logger = get_logger(__name__)

admin_namespace = Namespace("admin", description="admin operations")

@admin_namespace.route("/stats")
class AdminStats(Resource):
    @admin_endpoint()
    @admin_namespace.doc(**GET_DETAILED_STATS_DOC)
    def get(self, **kwargs):
        """Get system stats"""
        result = get_detailed_stats()
        return success_response(result)


@admin_namespace.route("/stats/counts")
class AdminStatsCounts(Resource):
    @admin_endpoint()
    @admin_namespace.doc(**GET_DATA_COUNTS_DOC)
    def get(self, **kwargs):
        """Get data counts"""


        result = get_data_counts()
        return success_response(result)


@admin_namespace.route("/events/<int:event_id>/reset")
class AdminEventReset(Resource):
    @admin_endpoint()
    @load_event(LoaderType.PARAM)
    @admin_namespace.doc(**RESET_EVENT_DATA_DOC)
    def post(self, event_id, **kwargs):
        """Reset event data"""
        reset_event_data(event_id)
        return success_response()

@admin_namespace.route("/health")
class AdminHealth(Resource):
    @admin_endpoint()
    @admin_namespace.doc(**SYSTEM_HEALTH_DOC)
    def get(self, **kwargs):
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

@admin_namespace.route("/impersonate")
class AdminImpersonate(Resource):
    @admin_endpoint(json_required=True)
    @load_user(LoaderType.BODY)
    @get_permissions
    @admin_namespace.doc(
        description="Impersonate a user by ID",
        responses={
            200: "Success",
            403: "Forbidden - User does not have permission to impersonate",
            404: "User not found"
        }
    )
    def post(self, json_data,current_user, permissions, **kwargs):
        """Impersonate a user by ID"""
        user_id = json_data.get("user_id")
        if PermissionEnum.CAN_IMPERSONATE_USERS not in permissions:
            return error_response("You do not have permission to impersonate users.", "permissions", 403)

        if user_id == current_user.id:
            return error_response("You cannot impersonate yourself.", "impersonation", 403)

        if get_user_roles(user_id) != []:
            return error_response("You cannot impersonate privileged users", "impersonation", 403)

        if session.get("impersonated"):
            # Should never be able to get here but just in case
            return error_response("You are already impersonating another user.", "impersonation", 403)

        logger.info(f"Admin {current_user.id} is impersonating user {user_id}")

        session["admin_id"] = current_user.id
        session["impersonated"] = True
        session["id"] = user_id
        session["nonce"] = generate_nonce()

        return success_response()


@admin_namespace.route("/stop_impersonating")
class AdminStopImpersonating(Resource):
    @user_endpoint(json_required=True)
    @admin_namespace.doc(
        description="Stop impersonating a user",
        responses={
            200: "Success",
            403: "Forbidden - User is not impersonating"
        }
    )
    def post(self,json_data, **kwargs):
        """Stop impersonating a user"""
        if not session.get("impersonated"):
            return error_response("You are not currently impersonating any user.", "impersonation", 403)

        logger.info(f"Admin {session['admin_id']} stopped impersonating user {session['id']}")

        session["id"] = session["admin_id"]
        session.pop("admin_id", None)
        session.pop("impersonated", None)
        session["nonce"] = generate_nonce()


        return success_response()









