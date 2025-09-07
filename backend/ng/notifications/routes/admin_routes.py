"""
Admin API routes for notifications
"""

from flask_restx import Namespace, Resource

from ...core.utils import success_response
from ...core.middleware import admin_endpoint
from ...core.middleware.loaders import LoaderType, load_event

from ..controllers import (
    send_announcement,
    send_event_announcement,
    get_all_announcements,
)
from ._docs import (
    SEND_SYSTEM_ANNOUNCEMENT_DOC,
    SEND_EVENT_ANNOUNCEMENT_DOC,
    GET_ALL_ANNOUNCEMENTS_DOC,
)


notifications_admin_namespace = Namespace(
    "admin/notifications",
    description = "Admin notification operations"
)


@notifications_admin_namespace.route("/announce")
class SystemAnnouncement(Resource):
    @admin_endpoint(json_required = True)
    @notifications_admin_namespace.doc(**SEND_SYSTEM_ANNOUNCEMENT_DOC)
    def post(self, current_user, json_data, **kwargs):
        """
        Send system-wide announcement
        """
        result = send_announcement(
            title = json_data.get("title"),
            message = json_data.get("message"),
            sender_id = current_user.id,
        )
        return success_response(result)


@notifications_admin_namespace.route("/events/<int:event_id>/announce")
class EventAnnouncement(Resource):
    @admin_endpoint(json_required = True)
    @load_event(source = LoaderType.PARAM)
    @notifications_admin_namespace.doc(**SEND_EVENT_ANNOUNCEMENT_DOC)
    def post(self, event_id: int, event, current_user, json_data, **kwargs):
        """
        Send event announcement
        """
        announcement = send_event_announcement(
            event_id = event_id,
            title = json_data.get("title"),
            message = json_data.get("message"),
            announcement_type = json_data.get("type",
                                              "event_update"),
            sender_id = current_user.id,
        )
        return success_response(announcement)


@notifications_admin_namespace.route("/announcements")
class AllAnnouncements(Resource):
    @admin_endpoint()
    @notifications_admin_namespace.doc(**GET_ALL_ANNOUNCEMENTS_DOC)
    def get(self, **kwargs):
        """
        Get all announcements
        """
        announcements = get_all_announcements()
        return success_response(announcements)
