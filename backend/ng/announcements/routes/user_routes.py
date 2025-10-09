"""
User API route for announcements
"""

from flask import request
from flask_restx import Namespace, Resource

from ...core.utils import success_response
from ...core.middleware import user_endpoint

from ..controllers import (
    get_active_announcements,
)


announcements_user_namespace = Namespace(
    "announcements",
    description = "Announcement user operations"
)


@announcements_user_namespace.route("")
class Announcements(Resource):
    @user_endpoint()
    @announcements_user_namespace.doc(
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
