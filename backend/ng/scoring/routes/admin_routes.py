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

scoring_admin_namespace = Namespace(
    "admin/scoring",
    description = "Admin scoring operations"
)


@scoring_admin_namespace.route(
    "/events/<int:event_id>/teams/<int:team_id>/award-points"
)
class AwardPoints(Resource):
    @admin_endpoint(json_required = True)
    @load_event(LoaderType.PARAM)
    @load_team(LoaderType.PARAM)
    @load_score_by_team_and_event()
    @scoring_admin_namespace.doc(
        description="Award or deduct points manually with reason for audit trail (Admin only)",
        params={
            "points": {
                "description": "Points to award (positive) or deduct (negative). Cannot be zero.",
                "required": True,
                "type": "integer",
                "example": 50
            },
            "reason": {
                "description": "Reason for manual point adjustment (512 character max length)",
                "in": "body",
                "required": True,
                "type": "string",
                "example": "Bonus points for creative solution"
            }
        },
        responses={
        201: "Success - Points awarded or deducted successfully",
        400: "Bad request - Invalid points value (cannot be zero) or missing reason",
        403: "Forbidden - Admin access required",
        404: "Not found - Team has no score in the specified event",
        500: "Internal Server Error",
    },)
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
    @admin_endpoint(json_required = False)
    @load_event(LoaderType.PARAM)
    @load_team(LoaderType.PARAM)
    @load_score_by_team_and_event()
    @scoring_admin_namespace.doc(
        description="Recalculate a team's score from all score events (Admin only)",
        responses={
            200: "Success - Score recalculated with old/new values and difference",
            403: "Forbidden - Admin access required",
            404: "Not found - Team has no score in the specified event",
            500: "Internal Server Error",
        },
    )
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
    @admin_endpoint()
    @load_event(LoaderType.PARAM)
    @load_team(LoaderType.PARAM)
    @scoring_admin_namespace.doc(
        description="Get detailed scoring history for audit and debugging purposes (Admin only)",
        params={
            "limit": {
                "description": "Maximum number of score events to return",
                "required": False,
                "type": "integer",
                "example": 100,
                "default": 50
            }
        },
        responses={
            200: "Success - Returns list of all score events with source details",
            400: "Bad request - Invalid limit parameter (must be 1-500)",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error",
        },
    )
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
    @admin_endpoint()
    @load_event(LoaderType.PARAM)
    @load_team(LoaderType.PARAM)
    @scoring_admin_namespace.doc(
        description="Get all attempts (correct and incorrect) for a team in an event (Admin only)",
        responses={
            200: "Success - Returns list of all attempts with enriched names",
            403: "Forbidden - Admin access required",
            404: "Not found - Event or team does not exist",
            500: "Internal Server Error",
        },
    )
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
    @admin_endpoint()
    @load_event(LoaderType.PARAM)
    @load_team(LoaderType.PARAM)
    @scoring_admin_namespace.doc(
        description="Get all hint redemptions for a team in an event (Admin only)",
        responses={
            200: "Success - Returns list of hint redemptions with enriched names and challenge info",
            403: "Forbidden - Admin access required",
            404: "Not found - Event or team does not exist",
            500: "Internal Server Error",
        },
    )
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
    @admin_endpoint()
    @load_event(LoaderType.PARAM)
    @load_team(LoaderType.PARAM)
    @scoring_admin_namespace.doc(
        description="Get all manual point awards for a team in an event (Admin only)",
        responses={
            200: "Success - Returns list of all manual point awards with enriched names",
            403: "Forbidden - Admin access required",
            404: "Not found - Event or team does not exist",
            500: "Internal Server Error",
        },
    )
    def get(self, event_id: int, team_id: int, event, team, **kwargs):
        """
        Get all manual point awards for a team in an event
        """
        awards = get_team_manual_awards(team_id, event_id)
        return success_response(awards)
