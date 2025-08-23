"""
Admin API routes for scoring management
"""

from flask import request
from flask_restx import Namespace, Resource

from ...core.middleware import admin_endpoint
from ...core.exceptions import ValidationError
from ...core.middleware.loaders import (
    LoaderType,
    load_event,
    load_team,
    load_score_by_team_and_event,
)
from ... import config
from ...core.utils import success_response

from ..controllers import (
    award_manual_points,
    recalculate_score,
    get_score_history,
    get_team_attempts,
    get_team_hint_redemptions,
    get_team_manual_awards,
)
from ._docs import (
    AWARD_MANUAL_POINTS_DOC,
    RECALCULATE_SCORE_DOC,
    GET_SCORE_HISTORY_DOC,
    GET_TEAM_ATTEMPTS_DOC,
    GET_TEAM_HINT_REDEMPTIONS_DOC,
    GET_TEAM_MANUAL_AWARDS_DOC,
)


scoring_admin_namespace = Namespace(
    "admin/scoring",
    description = "Admin scoring operations"
)


@scoring_admin_namespace.route(
    "/events/<int:event_id>/teams/<int:team_id>/award-points"
)
class AwardPoints(Resource):
    @scoring_admin_namespace.doc(**AWARD_MANUAL_POINTS_DOC)
    @admin_endpoint(json_required = True)
    @load_event(LoaderType.PARAM)
    @load_team(LoaderType.PARAM)
    @load_score_by_team_and_event()
    def post(
        self,
        event_id: int,
        team_id: int,
        event,
        team,
        score,
        current_user,
        json_data,
        **kwargs
    ):
        """
        Award manual points to a team
        """
        result = award_manual_points(
            event = event,
            team = team,
            score = score,
            points = json_data.get("points"),
            reason = json_data.get("reason"),
            admin_id = current_user.id,
        )
        return success_response(result, status_code = 201)


@scoring_admin_namespace.route(
    "/events/<int:event_id>/teams/<int:team_id>/recalculate"
)
class RecalculateScore(Resource):
    @scoring_admin_namespace.doc(**RECALCULATE_SCORE_DOC)
    @admin_endpoint(json_required = False)
    @load_event(LoaderType.PARAM)
    @load_team(LoaderType.PARAM)
    @load_score_by_team_and_event()
    def post(self, event_id: int, team_id: int, event, team, score, **kwargs):
        """
        Recalculate a team's score (if needed)
        """
        result = recalculate_score(score = score)
        return success_response(result)


@scoring_admin_namespace.route(
    "/events/<int:event_id>/teams/<int:team_id>/history"
)
class ScoreHistory(Resource):
    @scoring_admin_namespace.doc(**GET_SCORE_HISTORY_DOC)
    @admin_endpoint()
    @load_event(LoaderType.PARAM)
    @load_team(LoaderType.PARAM)
    def get(self, event_id: int, team_id: int, event, team, **kwargs):
        """
        Get scoring history for a team
        """
        limit = request.args.get(
            "limit",
            config.DEFAULT_SCORE_HISTORY_LIMIT,
            type = int
        )
        if limit < 1 or limit > config.MAX_SCORE_HISTORY_LIMIT:
            raise ValidationError(
                f"Limit must be between 1 and {config.MAX_SCORE_HISTORY_LIMIT}"
            )

        result = get_score_history(event = event, team = team, limit = limit)
        return success_response(result)



@scoring_admin_namespace.route(
    "/events/<int:event_id>/teams/<int:team_id>/attempts"
)
class TeamAttempts(Resource):
    @scoring_admin_namespace.doc(**GET_TEAM_ATTEMPTS_DOC)
    @admin_endpoint()
    @load_event(LoaderType.PARAM)
    @load_team(LoaderType.PARAM)
    def get(self, event_id: int, team_id: int, event, team, **kwargs):
        """
        Get all attempts (correct and incorrect) for a team in an event
        """
        attempts = get_team_attempts(team_id, event_id)
        return success_response(attempts)


@scoring_admin_namespace.route(
    "/events/<int:event_id>/teams/<int:team_id>/hint_redemptions"
)
class TeamHintRedemptions(Resource):
    @scoring_admin_namespace.doc(**GET_TEAM_HINT_REDEMPTIONS_DOC)
    @admin_endpoint()
    @load_event(LoaderType.PARAM)
    @load_team(LoaderType.PARAM)
    def get(self, event_id: int, team_id: int, event, team, **kwargs):
        """
        Get all hint redemptions for a team in an event
        """
        redemptions = get_team_hint_redemptions(team_id, event_id)
        return success_response(redemptions)


@scoring_admin_namespace.route(
    "/events/<int:event_id>/teams/<int:team_id>/manual_awards"
)
class TeamManualAwards(Resource):
    @scoring_admin_namespace.doc(**GET_TEAM_MANUAL_AWARDS_DOC)
    @admin_endpoint()
    @load_event(LoaderType.PARAM)
    @load_team(LoaderType.PARAM)
    def get(self, event_id: int, team_id: int, event, team, **kwargs):
        """
        Get all manual point awards for a team in an event
        """
        awards = get_team_manual_awards(team_id, event_id)
        return success_response(awards)
