"""
User API routes for notifications
"""

from flask import request
from flask_restx import Namespace, Resource

from ...core.middleware import user_endpoint
from ...core.utils import success_response

from ..controllers import (
    get_my_notifications,
    mark_notification_read,
    mark_all_read,
    get_unread_count,
    get_active_announcements,
)
from ._docs import (
    GET_MY_NOTIFICATIONS_DOC,
    GET_UNREAD_COUNT_DOC,
    MARK_NOTIFICATION_READ_DOC,
    MARK_ALL_READ_DOC,
    GET_ACTIVE_ANNOUNCEMENTS_DOC,
)


notifications_user_namespace = Namespace(
    "notifications",
    description = "Notification operations for users"
)


@notifications_user_namespace.route("/me")
class MyNotifications(Resource):
    @user_endpoint()
    @notifications_user_namespace.doc(**GET_MY_NOTIFICATIONS_DOC)
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
    @notifications_user_namespace.doc(**GET_UNREAD_COUNT_DOC)
    def get(self, current_user, **kwargs):
        """
        Get unread notification count
        """
        count = get_unread_count(user_id = current_user.id)
        return success_response({"count": count})


@notifications_user_namespace.route("/me/<int:notification_id>/read")
class MarkRead(Resource):
    @user_endpoint()
    @notifications_user_namespace.doc(**MARK_NOTIFICATION_READ_DOC)
    def post(self, notification_id: int, current_user, **kwargs):
        """
        Mark notification as read
        """
        notification = mark_notification_read(
            notification_id = notification_id,
            user_id = current_user.id,
        )
        return success_response(notification)


@notifications_user_namespace.route("/me/read-all")
class MarkAllRead(Resource):
    @user_endpoint()
    @notifications_user_namespace.doc(**MARK_ALL_READ_DOC)
    def post(self, current_user, **kwargs):
        """
        Mark all notifications as read
        """
        count = mark_all_read(user_id = current_user.id)
        return success_response({"count": count})


@notifications_user_namespace.route("/announcements")
class Announcements(Resource):
    @user_endpoint()
    @notifications_user_namespace.doc(**GET_ACTIVE_ANNOUNCEMENTS_DOC)
    def get(self, **kwargs):
        """
        Get active announcements
        """
        event_id = request.args.get("event_id", type = int)

        announcements = get_active_announcements(
            event_id = event_id,
        )
        return success_response(announcements)
