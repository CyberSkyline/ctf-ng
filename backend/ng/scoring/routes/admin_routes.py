"""
Admin API routes for scoring management
"""

from flask_restx import Namespace, Resource

from ...core.middleware import admin_endpoint
from ...core.middleware.loaders import (
    LoaderType,
    load_event,
    load_team,
)
from ...core.utils import success_response

from ..models import ManualPointAward
from ..controllers import (
    award_manual_points, 
    recalculate_score, 
    get_score_history,
)

from ._docs import (
    AWARD_MANUAL_POINTS_DOC,
    RECALCULATE_SCORE_DOC,
    GET_SCORE_HISTORY_DOC,
)
scoring_admin_namespace = Namespace("admin/scoring", description="Admin scoring operations")


@scoring_admin_namespace.route("/events/<int:event_id>/teams/<int:team_id>/award-points")
class AwardPoints(Resource):

    @admin_endpoint(json_required=True, validation_func=ManualPointAward.validate_api_award)
    @scoring_admin_namespace.doc(**AWARD_MANUAL_POINTS_DOC)
    def post(self, event_id: int, team_id: int, current_user, validated_data, **kwargs):
        """
        Award manual points to a team
        """        
        result = award_manual_points(
            event_id=event_id,
            team_id=team_id,
            points=validated_data['points'],
            reason=validated_data['reason'],
            admin_id=current_user.id
        )
        return success_response(result, status_code=201)


@scoring_admin_namespace.route("/events/<int:event_id>/teams/<int:team_id>/recalculate")
class RecalculateScore(Resource):

    @admin_endpoint()
    @scoring_admin_namespace.doc(**RECALCULATE_SCORE_DOC)
    def post(self, event_id: int, team_id: int, **kwargs):
        """
        Recalculate a team's score (if needed)
        """
        result = recalculate_score(
            event_id=event_id,
            team_id=team_id
        )
        return success_response(result)


@scoring_admin_namespace.route("/events/<int:event_id>/teams/<int:team_id>/history")
class ScoreHistory(Resource):

    @admin_endpoint()
    @scoring_admin_namespace.doc(**GET_SCORE_HISTORY_DOC)
    def get(self, event_id: int, team_id: int, **kwargs):
        """
        Get scoring history for a team
        """       
        limit = request.args.get('limit', 50, type=int)
        if limit < 1 or limit > 500:
            raise ValidationError("Limit must be between 1 and 500")
        
        result = get_score_history(
            event_id=event_id,
            team_id=team_id,
            limit=limit
        )
        return success_response(result)


