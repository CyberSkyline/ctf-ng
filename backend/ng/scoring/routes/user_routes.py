"""
User API routes for scoring
"""

from flask import request
from flask_restx import Namespace, Resource

from ...core.middleware import user_endpoint
from ...core.middleware.loaders import (
    LoaderType,
    load_event,
    load_challenge,
    load_question,
    load_hint,
    load_team_by_user_and_event,
    load_score_by_team_and_event,
)
from ...core.middleware.permission_middleware import get_permissions
from ...permissions.models.enums import PermissionEnum
from ... import config
from ...core.utils import success_response, error_response
from ...core.exceptions import ValidationError

from ...user.models import User

from ..controllers import (
    get_leaderboard,
    get_team_score,
    submit_answer,
    redeem_hint,
)
from ._docs import (
    GET_LEADERBOARD_DOC,
    GET_TEAM_SCORE_DOC,
    SUBMIT_ANSWER_DOC,
    REDEEM_HINT_DOC,
)

scoring_user_namespace = Namespace("scoring", description="Scoring operations for users")


@scoring_user_namespace.route("/<int:event_id>/leaderboard")
class EventLeaderboard(Resource):
    @scoring_user_namespace.doc(**GET_LEADERBOARD_DOC)
    @user_endpoint()
    @load_event(LoaderType.PARAM)
    def get(self, event_id: int, event, current_user: User, **kwargs):
        """
        Get event leaderboard
        """
        limit = request.args.get("limit", config.DEFAULT_LEADERBOARD_LIMIT, type=int)
        if limit < 1 or limit > config.MAX_LEADERBOARD_LIMIT:
            raise ValidationError(f"Limit must be between 1 and {config.MAX_LEADERBOARD_LIMIT}")

        leaderboard_data = get_leaderboard(event_id=event_id, limit=limit)
        return success_response(leaderboard_data)


@scoring_user_namespace.route("/<int:event_id>/me/team/score")
class MyTeamScore(Resource):
    @scoring_user_namespace.doc(**GET_TEAM_SCORE_DOC)
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
    @scoring_user_namespace.doc(**SUBMIT_ANSWER_DOC)
    @user_endpoint(json_required=True)
    @load_event(LoaderType.PARAM)
    @load_challenge(LoaderType.PARAM)
    @load_question(LoaderType.PARAM)
    @load_team_by_user_and_event()
    @get_permissions
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
        if PermissionEnum.CAN_PLAY_CHALLENGES not in permissions:
            return error_response("You do not have permission to play challenges.", 403)

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
    @scoring_user_namespace.doc(**REDEEM_HINT_DOC)
    @user_endpoint(json_required=False)
    @load_event(LoaderType.PARAM)
    @load_challenge(LoaderType.PARAM)
    @load_hint(LoaderType.PARAM)
    @load_team_by_user_and_event()
    @get_permissions
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

        if PermissionEnum.CAN_PLAY_CHALLENGES not in permissions:
            return error_response("You do not have permission to play challenges.", 403)

        result = redeem_hint(
            event=event,
            challenge=challenge,
            hint=hint,
            team=team,
            current_user=current_user,
        )
        return success_response(result, status_code=201)
