"""
Admin Routes for Feedback Operations
"""

from flask_restx import Namespace, Resource

from ...core.middleware.loaders import (
    LoaderType,
    load_event,
    load_challenge,
)
from ...core.utils import success_response
from ...core.middleware import admin_endpoint

from ..controllers import (
    list_event_feedback,
    list_challenge_feedback,
)


feedback_admin_namespace = Namespace(
    "feedback",
    description = "Feedback endpoints for admins"
)


@feedback_admin_namespace.route("/<int:event_id>/feedback")
class AdminEventFeedback(Resource):
    @admin_endpoint()
    @load_event(source = LoaderType.PARAM)
    @feedback_admin_namespace.doc(
        description = "Get all feedback for an event (Admin only)",
        responses = {
            200: "Success - Returns list of all event feedback",
            403: "Forbidden - Admin access required",
            404: "Not found - Event does not exist",
        },
    )
    def get(self, event_id: int, event, **kwargs):
        """
        Get all event feedback
        """
        feedback_list = list_event_feedback(event_id = event_id)
        return success_response(feedback_list)


@feedback_admin_namespace.route(
    "/<int:event_id>/challenges/<int:challenge_id>/feedback"
)
class AdminChallengeFeedback(Resource):
    @admin_endpoint()
    @load_event(source = LoaderType.PARAM)
    @load_challenge(source = LoaderType.PARAM)
    @feedback_admin_namespace.doc(
        description = "Get all feedback for a challenge (Admin only)",
        responses = {
            200: "Success - Returns list of all challenge feedback",
            403: "Forbidden - Admin access required",
            404: "Not found - Event or challenge does not exist",
        },
    )
    def get(self, event_id: int, challenge_id: int, event, challenge, **kwargs):
        """
        Get all challenge feedback
        """
        feedback_list = list_challenge_feedback(challenge_id = challenge_id)
        return success_response(feedback_list)
