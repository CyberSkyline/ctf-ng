"""
User Routes for Feedback Operations
"""

from flask_restx import Namespace, Resource


from ...core.middleware.loaders import (
    LoaderType,
    load_event,
    load_challenge,
    load_team_by_user_and_event,
)
from ...core.utils import error_response, success_response, utc_now
from ...core.middleware import user_endpoint
from ...core.middleware.permission_middleware import check_permissions
from ...permissions.models.enums import PermissionEnum

from ...user.models.User import User
from ...team.models.Team import Team

from ..controllers import (
    get_my_event_feedback,
    upsert_event_feedback,
    get_my_challenge_feedback,
    upsert_challenge_feedback,
)


feedback_user_namespace = Namespace(
    "feedback",
    description = "Feedback endpoints for users"
)


@feedback_user_namespace.route("/<int:event_id>/feedback")
class EventFeedback(Resource):
    @user_endpoint()
    @load_event(source = LoaderType.PARAM)
    @load_team_by_user_and_event()
    @feedback_user_namespace.doc(
        description = "Get my feedback for an event",
        responses = {
            200: "Success - Returns feedback or null if not submitted",
            401: "Unauthorized - Authentication required",
            404: "Not found - Event does not exist",
        },
    )
    def get(self, event_id: int, event, current_user: User, **kwargs):
        """
        Get my event feedback
        """
        feedback = get_my_event_feedback(
            user_id = current_user.id,
            event_id = event_id,
        )
        return success_response(feedback)

    @user_endpoint(json_required = True)
    @load_event(source = LoaderType.PARAM)
    @load_team_by_user_and_event()
    @check_permissions(PermissionEnum.CAN_VIEW_CHALLENGES, "You may not leave feedback at this time.")
    @feedback_user_namespace.doc(
        description = "Submit or update my event feedback",
        params = {
            "feedback_data": {
                "description": "Feedback data as JSON object",
                "required": True,
                "type": "object",
            }
        },
        responses = {
            200: "Success - Feedback updated",
            201: "Success - Feedback created",
            401: "Unauthorized - Authentication required",
            404: "Not found - Event does not exist",
        },
    )
    def post(self, event_id: int, event, team: Team, current_user: User, json_data, **kwargs):
        """
        Submit or update my event feedback
        """
        if team.end_time is not None and team.end_time > utc_now().replace(tzinfo = None):
          return error_response("You cannot submit event feedback until you have finished the event.", "feedback", 403)

        feedback = upsert_event_feedback(
            user_id = current_user.id,
            event_id = event_id,
            feedback_data = json_data.get("feedback_data",
                                          {}),
        )
        return success_response(feedback, status_code = 201)


@feedback_user_namespace.route(
    "/<int:event_id>/challenges/<int:challenge_id>/feedback"
)
class ChallengeFeedback(Resource):
    @user_endpoint()
    @load_event(source = LoaderType.PARAM)
    @load_challenge(source = LoaderType.PARAM)
    @load_team_by_user_and_event()
    @feedback_user_namespace.doc(
        description = "Get my feedback for a challenge",
        responses = {
            200: "Success - Returns feedback or null if not submitted",
            401: "Unauthorized - Authentication required",
            404: "Not found - Event or challenge does not exist",
        },
    )
    def get(
        self,
        event_id: int,
        challenge_id: int,
        event,
        challenge,
        current_user: User,
        **kwargs
    ):
        """
        Get my challenge feedback
        """
        feedback = get_my_challenge_feedback(
            user_id = current_user.id,
            challenge_id = challenge_id,
        )
        return success_response(feedback)

    @user_endpoint(json_required = True)
    @load_event(source = LoaderType.PARAM)
    @load_team_by_user_and_event()
    @check_permissions(PermissionEnum.CAN_VIEW_CHALLENGES, "You may not leave feedback at this time.")
    @load_challenge(source = LoaderType.PARAM)
    @feedback_user_namespace.doc(
        description = "Submit or update my challenge feedback",
        params = {
            "feedback_data": {
                "description": "Feedback data as JSON object",
                "required": True,
                "type": "object",
            }
        },
        responses = {
            200: "Success - Feedback updated",
            201: "Success - Feedback created",
            401: "Unauthorized - Authentication required",
            404: "Not found - Event or challenge does not exist",
        },
    )
    def post(
        self,
        event_id: int,
        challenge_id: int,
        event,
        challenge,
        current_user: User,
        json_data,
        **kwargs
    ):
        """
        Submit or update my challenge feedback
        """
        feedback = upsert_challenge_feedback(
            user_id = current_user.id,
            event_id = event_id,
            challenge_id = challenge_id,
            feedback_data = json_data.get("feedback_data",
                                          {}),
        )
        return success_response(feedback, status_code = 201)
