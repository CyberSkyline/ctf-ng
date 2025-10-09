"""
Admin API routes for announcements
"""

from flask_restx import Namespace, Resource

from ...core.utils import success_response
from ...core.middleware import admin_endpoint
from ...core.middleware.loaders import LoaderType, load_event, load_announcement

from ..controllers import (
    send_announcement,
    send_event_announcement,
    get_all_announcements,
    delete_announcement,
)


announcements_admin_namespace = Namespace(
    "admin/announcements",
    description = "Admin announcement operations"
)


@announcements_admin_namespace.route("")
class AllAnnouncements(Resource):
    @admin_endpoint()
    @announcements_admin_namespace.doc(
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


@announcements_admin_namespace.route("/announce")
class SystemAnnouncement(Resource):
    @admin_endpoint(json_required = True)
    @announcements_admin_namespace.doc(
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
            },
            "expires_at": {
                "description": "Optional expiration datetime in ISO format (UTC)",
                "in": "body",
                "required": False,
                "type": "string",
                "example": "2025-12-31T23:59:59Z"
            },
            "send_notification": {
                "description": "Optional flag to send notification to users (default: false)",
                "in": "body",
                "required": False,
                "type": "boolean",
                "example": True
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
            expires_at = json_data.get("expires_at"),
            send_notification = json_data.get("send_notification", False),
        )
        return success_response(result)


@announcements_admin_namespace.route("/events/<int:event_id>/announce")
class EventAnnouncement(Resource):
    @admin_endpoint(json_required = True)
    @load_event(source = LoaderType.PARAM)
    @announcements_admin_namespace.doc(
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
            },
            "expires_at": {
                "description": "Optional expiration datetime in ISO format (UTC)",
                "in": "body",
                "required": False,
                "type": "string",
                "example": "2025-12-31T23:59:59Z"
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
            expires_at = json_data.get("expires_at"),
        )
        return success_response(announcement)


@announcements_admin_namespace.route("/<int:announcement_id>")
class AnnouncementDelete(Resource):
    @admin_endpoint()
    @load_announcement(source = LoaderType.PARAM)
    @announcements_admin_namespace.doc(
        description="Delete an announcement and cleanup related notifications (Admin only)",
        params={
            "announcement_id": {
                "description": "Announcement ID to delete",
                "required": True,
                "type": "integer",
                "example": 1
            }
        },
        responses={
            200: "Success - Announcement deleted with notification cleanup",
            401: "Unauthorized - Authentication required",
            403: "Forbidden - Admin access required",
            404: "Not found - Announcement does not exist",
            500: "Internal server error",
        },
    )
    def delete(self, announcement_id: int, announcement, current_user, **kwargs):
        """
        Delete announcement with notification cleanup
        """
        delete_announcement(announcement = announcement)
        return success_response()
