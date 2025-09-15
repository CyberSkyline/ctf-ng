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


notifications_admin_namespace = Namespace(
    "admin/notifications",
    description = "Admin notification operations"
)


@notifications_admin_namespace.route("/announce")
class SystemAnnouncement(Resource):
    @admin_endpoint(json_required = True)
    @notifications_admin_namespace.doc(
        description="Send system-wide announcement to all users",
        params={
            "title": {
                "description": "Announcement title",
                "in": "body",
                "required": True,
                "type": "string",
                "example": "System Maintenance"
            },
            "message": {
                "description": "Announcement message content",
                "in": "body",
                "required": True,
                "type": "string",
                "example": "The system will be under maintenance from 2-4 PM UTC"
            }
        },
        responses={
            200: "Success - System announcement sent",
            400: "Bad request - Invalid title or message",
            401: "Unauthorized - Authentication required",
            403: "Forbidden - Admin access required",
            500: "Internal server error",
        },
    )
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
    @notifications_admin_namespace.doc(
        description="Send announcement to all participants in a specific event",
        params={
            "title": {
                "description": "Announcement title",
                "in": "body",
                "required": True,
                "type": "string",
                "example": "Event Update"
            },
            "message": {
                "description": "Announcement message content",
                "in": "body",
                "required": True,
                "type": "string",
                "example": "New challenge has been released!"
            },
            "type": {
                "description": "Announcement type (general, event_update, event_start, event_end, leaderboard_update)",
                "in": "body",
                "required": False,
                "type": "string",
                "example": "event_update",
                "default": "event_update"
            }
        },
        responses={
            200: "Success - Event announcement sent to all participants",
            400: "Bad request - Invalid announcement data or type",
            401: "Unauthorized - Authentication required",
            403: "Forbidden - Admin access required",
            404: "Not found - Event does not exist",
            500: "Internal server error",
        },
    )
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
    @notifications_admin_namespace.doc(
        description="Get all announcements for admin management (includes expired)",
        responses={
            200: "Success - Returns list of all announcements",
            401: "Unauthorized - Authentication required",
            403: "Forbidden - Admin access required",
            500: "Internal server error",
        },
    )
    def get(self, **kwargs):
        """
        Get all announcements
        """
        announcements = get_all_announcements()
        return success_response(announcements)
