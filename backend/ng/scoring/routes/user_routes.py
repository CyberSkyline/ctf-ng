"""
User API routes for scoring
"""

from flask import request
from flask_restx import Namespace, Resource

from ...core.middleware import user_endpoint
from ...core.middleware.loaders import (
    LoaderType,
    load_event,
    load_team_by_user_and_event,
)
from ...core.utils import success_response
from ...core.exceptions import ValidationError

from ...user.models import User

from ..models import Attempt, HintRedemption
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

    @user_endpoint()
    @scoring_user_namespace.doc(**GET_LEADERBOARD_DOC)
    def get(self, event_id: int, current_user: User, **kwargs):
        """
        Get event leaderboard
        """
        limit = request.args.get('limit', 100, type=int)
        if limit < 1 or limit > 1000:
            raise ValidationError("Limit must be between 1 and 1000")
        
        leaderboard_data = get_leaderboard(event_id=event_id, limit=limit)
        return success_response(leaderboard_data)


@scoring_user_namespace.route("/<int:event_id>/me/team/score")
class MyTeamScore(Resource):

    @user_endpoint()
    @scoring_user_namespace.doc(**GET_TEAM_SCORE_DOC)
    @load_team_by_user_and_event()
    def get(self, event_id: int, team, current_user: User, **kwargs):
        """
        Get my team's score
        """
        include_history = request.args.get('include_history', 'false').lower() == 'true'
        
        result = get_team_score(
            event_id=event_id,
            team_id=team.id, 
            include_history=include_history
        )
        return success_response(result)


@scoring_user_namespace.route("/<int:event_id>/challenges/<int:challenge_id>/questions/<int:question_id>/submit")
class SubmitAnswer(Resource):

    @user_endpoint(json_required=True, validation_func=Attempt.validate_api_submission)
    @scoring_user_namespace.doc(**SUBMIT_ANSWER_DOC)
    def post(self, event_id: int, challenge_id: int, question_id: int, 
             current_user: User, validated_data, **kwargs):
        """
        Submit an answer to a question
        """        
        result = submit_answer(
            event_id=event_id,
            challenge_id=challenge_id,
            question_id=question_id,
            submission=validated_data['submission'],
            current_user_id=current_user.id
        )
        return success_response(result, status_code=201)


@scoring_user_namespace.route("/<int:event_id>/challenges/<int:challenge_id>/hint/<int:hint_id>/redeem")
class RedeemHint(Resource):

    @user_endpoint()
    @scoring_user_namespace.doc(**REDEEM_HINT_DOC)
    def post(self, event_id: int, challenge_id: int, hint_id: int, 
             current_user: User, **kwargs):
        """
        Redeem a hint
        """
        result = redeem_hint(
            event_id=event_id,
            challenge_id=challenge_id,
            hint_id=hint_id,
            current_user_id=current_user.id
        )
        return success_response(result, status_code=201)


