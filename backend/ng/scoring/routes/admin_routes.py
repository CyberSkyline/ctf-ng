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
    get_submission_history,
)
from ._docs import (
    AWARD_MANUAL_POINTS_DOC,
    RECALCULATE_SCORE_DOC,
    GET_SCORE_HISTORY_DOC,
    GET_SUBMISSION_HISTORY_DOC,
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
    "/events/<int:event_id>/teams/<int:team_id>/submission_history"
)
class SubmissionHistory(Resource):
    @scoring_admin_namespace.doc(**GET_SUBMISSION_HISTORY_DOC)
    @admin_endpoint()
    @load_event(LoaderType.PARAM)
    @load_team(LoaderType.PARAM)
    def get(self, event_id: int, team_id: int, event, team, **kwargs):
        """
        Get submission history including all scoring events
        """
        limit = request.args.get(
            "limit",
            config.DEFAULT_SUBMISSION_HISTORY_LIMIT,
            type = int
        )

        if limit < 1 or limit > config.MAX_SUBMISSION_HISTORY_LIMIT:
            raise ValidationError(f"Limit must be between 1 and {config.MAX_SUBMISSION_HISTORY_LIMIT}")

        result = get_submission_history(
            team_id = team_id,
            event_id = event_id,
            limit = limit
        )

        enriched_score_events = []
        for score_event in result["score_events"]:
            event_data = score_event.serialize(include_admin_fields = True)
            event_data["team_name"] = team.name

            if score_event.attempts:
                event_data["source_type"] = "attempt"
                event_data["source_id"] = score_event.attempts[0].id
            elif score_event.hint_redemptions:
                event_data["source_type"] = "hint_redemption"
                event_data["source_id"] = score_event.hint_redemptions[0].id
            elif score_event.manual_awards:
                event_data["source_type"] = "manual_award"
                event_data["source_id"] = score_event.manual_awards[0].id
            enriched_score_events.append(event_data)

        enriched_attempts = []
        for attempt in result["attempts"]:
            attempt_data = attempt.serialize(include_admin_fields = True)
            attempt_data["team_name"] = team.name

            if attempt.user:
                user_data = attempt.user.serialize()
                attempt_data["user_name"] = user_data["name"]

            if attempt.challenge:
                attempt_data["challenge_name"] = attempt.challenge.name
            if attempt.question:
                attempt_data["question_name"] = attempt.question.name
            enriched_attempts.append(attempt_data)

        enriched_hints = []
        for redemption in result["hint_redemptions"]:
            hint_data = redemption.serialize(include_admin_fields = True)
            hint_data["team_name"] = team.name

            if redemption.user:
                user_data = redemption.user.serialize()
                hint_data["user_name"] = user_data["name"]

            if redemption.hint:
                hint_data["hint_preview"] = redemption.hint.preview
            enriched_hints.append(hint_data)

        enriched_awards = []
        for award in result["manual_awards"]:
            award_data = award.serialize(include_admin_fields = True)
            award_data["team_name"] = team.name

            if award.admin:
                award_data["admin_name"] = award.admin.name
            enriched_awards.append(award_data)

        return success_response(
            {
                "score_events": enriched_score_events,
                "attempts": enriched_attempts,
                "hint_redemptions": enriched_hints,
                "manual_awards": enriched_awards
            }
        )
