"""
User API routes for notifications
"""

from flask import request
from flask_restx import Namespace, Resource

from ...core.middleware.loaders import (
    LoaderType,
    load_notification,
)
from ...core.utils import success_response
from ...core.middleware import user_endpoint

from ..controllers import (
    get_my_notifications,
    mark_notification_read,
    mark_all_read,
    get_unread_count,
    get_active_announcements,
)


notifications_user_namespace = Namespace(
    "notifications",
    description = "Notification operations for users"
)


@notifications_user_namespace.route("/me")
class MyNotifications(Resource):
    @user_endpoint()
    @notifications_user_namespace.doc(
        description="Get my notifications with optional read status filter",
        params={
            "is_read": {
                "description": "Filter by read status (true/false)",
                "required": False,
                "type": "string",
                "example": "false"
            }
        },
        responses={
            200: "Success - Returns list of notifications",
            401: "Unauthorized - Authentication required",
            500: "Internal server error",
        },
    )
    def get(self, current_user, **kwargs):
        """
        Get my notifications
        """
        is_read = request.args.get("is_read")
        if is_read is not None:
            is_read = is_read.lower() == "true"

        notifications = get_my_notifications(
            user_id = current_user.id,
            is_read = is_read,
        )
        return success_response(notifications)


@notifications_user_namespace.route("/me/unread-count")
class UnreadCount(Resource):
    @user_endpoint()
    @notifications_user_namespace.doc(
        description="Get count of unread notifications for the current user",
        responses={
            200: "Success - Returns unread notification count",
            401: "Unauthorized - Authentication required",
            500: "Internal server error",
        },
    )
    def get(self, current_user, **kwargs):
        """
        Get unread notification count
        """
        count = get_unread_count(user_id = current_user.id)
        return success_response({"count": count})


@notifications_user_namespace.route("/me/<int:notification_id>/read")
class MarkRead(Resource):
    @user_endpoint()
    @load_notification(source=LoaderType.PARAM)
    @notifications_user_namespace.doc(
        description="Mark a specific notification as read",
        responses={
            200: "Success - Notification marked as read",
            401: "Unauthorized - Authentication required",
            403: "Forbidden - Cannot mark other users' notifications as read",
            404: "Not found - Notification does not exist",
            500: "Internal server error",
        },
    )
    def post(self, notification_id: int, notification, current_user, **kwargs):
        """
        Mark notification as read
        """
        notification = mark_notification_read(notification)
        return success_response(notification)


@notifications_user_namespace.route("/me/read-all")
class MarkAllRead(Resource):
    @user_endpoint()
    @notifications_user_namespace.doc(
        description="Mark all notifications as read for the current user",
        responses={
            200: "Success - All notifications marked as read, returns count of updated notifications",
            401: "Unauthorized - Authentication required",
            500: "Internal server error",
        },
    )
    def post(self, current_user, **kwargs):
        """
        Mark all notifications as read
        """
        count = mark_all_read(user_id = current_user.id)
        return success_response({"count": count})


@notifications_user_namespace.route("/announcements")
class Announcements(Resource):
    @user_endpoint()
    @notifications_user_namespace.doc(
        description="Get active announcements (system-wide or event-specific)",
        params={
            "event_id": {
                "description": "Filter by event (optional)",
                "required": False,
                "type": "integer",
                "example": 1
            }
        },
        responses={
            200: "Success - Returns list of active announcements",
            401: "Unauthorized - Authentication required",
            500: "Internal server error",
        },
    )
    def get(self, **kwargs):
        """
        Get active announcements
        """
        event_id = request.args.get("event_id", type = int)

        announcements = get_active_announcements(
            event_id = event_id,
        )
        return success_response(announcements)
