"""
User API routes for scoring
"""

from flask import request
from flask_restx import Namespace, Resource

from ...core.middleware import user_endpoint, public_endpoint
from ...core.middleware.loaders import (
    LoaderType,
    load_event,
    load_challenge,
    load_question,
    load_hint,
    load_team_by_user_and_event,
    load_score_by_team_and_event,
)
from ...core.middleware.permission_middleware import check_permissions
from ...permissions.models.enums import PermissionEnum
from ... import config
from ...core.utils import success_response
from ...core.exceptions import ValidationError

from ...user.models import User

from ..controllers import (
    get_leaderboard,
    get_team_score,
    submit_answer,
    redeem_hint,
)

scoring_user_namespace = Namespace("scoring", description="Scoring operations for users")


@scoring_user_namespace.route("/<int:event_id>/leaderboard")
class EventLeaderboard(Resource):
    @public_endpoint()
    @load_event(LoaderType.PARAM)
    @scoring_user_namespace.doc(
        description="Get the event leaderboard showing team rankings and scores with optional limit",
        params={
            "limit": {
                "description": "Maximum number of teams to return on leaderboard",
                "required": False,
                "type": "integer",
                "example": 50,
                "default": 100
            }
        },
        responses={
            200: "Success - Returns ordered list of teams with scores and rankings",
            403: "Forbidden - Authentication required",
            404: "Not found - Event does not exist or has no scores",
            500: "Internal Server Error",
        },
    )
    def get(self, event_id: int, event, **kwargs):
        """
        Get event leaderboard
        """
        current_user = kwargs.get("current_user", None)
        limit = request.args.get("limit", config.DEFAULT_LEADERBOARD_LIMIT, type=int)
        if limit < 1 or limit > config.MAX_LEADERBOARD_LIMIT:
            raise ValidationError(f"Limit must be between 1 and {config.MAX_LEADERBOARD_LIMIT}")

        leaderboard_data = get_leaderboard(event_id=event_id, limit=limit)
        return success_response(leaderboard_data)


@scoring_user_namespace.route("/<int:event_id>/me/team/score")
class MyTeamScore(Resource):
    @scoring_user_namespace.doc(
        description="Get current team score, rank, and optionally recent scoring history",
        responses={
            200: "Success - Returns team score, rank, and optional history",
            403: "Forbidden - Authentication required",
            404: "Not found - Team not found in event or no score exists",
            500: "Internal Server Error",
        },
    )
    @user_endpoint()
    @load_event(LoaderType.PARAM)
    @load_team_by_user_and_event()
    @load_score_by_team_and_event()
    def get(self, event_id: int, event, team, score, current_user: User, **kwargs):
        """
        Get my team's score
        """
        result = get_team_score(score=score)
        return success_response(result)


@scoring_user_namespace.route("/<int:event_id>/challenges/<int:challenge_id>/questions/<int:question_id>/submit")
class SubmitAnswer(Resource):
    @user_endpoint(json_required=True)
    @load_event(LoaderType.PARAM)
    @load_challenge(LoaderType.PARAM)
    @load_question(LoaderType.PARAM)
    @load_team_by_user_and_event()
    @check_permissions(PermissionEnum.CAN_PLAY_CHALLENGES, "You do not have permission to play challenges.")
    @scoring_user_namespace.doc(
        description="Submit an answer to a challenge question for scoring",
        params={
            "submission": {
                "description": "Answer submission text (4096 character max length)",
                "in": "body",
                "required": True,
                "type": "string",
                "example": "flag{example_answer}"
            }
        },
        responses={
            201: "Success - Answer accepted and scored",
            400: "Bad request - Invalid submission, exceeded max attempts, or event locked",
            401: "Unauthorized - Authentication required",
            404: "Not found - Question, challenge, or team not found",
        },
    )
    def post(
        self,
        event_id: int,
        challenge_id: int,
        question_id: int,
        event,
        challenge,
        question,
        team,
        current_user: User,
        permissions,
        json_data,
        **kwargs,
    ):
        """
        Submit an answer to a question
        """

        result = submit_answer(
            event=event,
            challenge=challenge,
            question=question,
            team=team,
            current_user=current_user,
            submission=json_data.get("submission", ""),
        )
        return success_response(result, status_code=201)


@scoring_user_namespace.route("/<int:event_id>/challenges/<int:challenge_id>/hint/<int:hint_id>/redeem")
class RedeemHint(Resource):
    @user_endpoint(json_required=False)
    @load_event(LoaderType.PARAM)
    @load_challenge(LoaderType.PARAM)
    @load_hint(LoaderType.PARAM)
    @load_team_by_user_and_event()
    @check_permissions(PermissionEnum.CAN_PLAY_CHALLENGES, "You do not have permission to play challenges.")
    @scoring_user_namespace.doc(
        description="Redeem a hint for a challenge, deducting points from the team's score",
        responses={
            201: "Success - Hint redeemed successfully",
            400: "Bad request - Hint already redeemed, event locked, or hint doesn't belong to challenge",
            401: "Unauthorized - Authentication required",
            404: "Not found - Event, challenge, hint, or team not found",
        },
    )
    def post(
        self,
        event_id: int,
        challenge_id: int,
        hint_id: int,
        event,
        challenge,
        hint,
        team,
        permissions,
        current_user: User,
        **kwargs,
    ):
        """
        Redeem a hint
        """

        result = redeem_hint(
            event=event,
            challenge=challenge,
            hint=hint,
            team=team,
            current_user=current_user,
        )
        return success_response(result, status_code=201)
