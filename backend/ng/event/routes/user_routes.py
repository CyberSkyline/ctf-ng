from flask_restx import Namespace, Resource

from ...challenge.models.Challenge import Challenge
from ...core.exceptions import ValidationError
from ...core.middleware import (
    user_endpoint,
)
from ...core.middleware.loaders import (
    LoaderType,
    load_challenge,
    load_event,
    load_team_by_user_and_event,
)
from ...core.utils import success_response
from ...core.utils.validator import BaseValidator
from ...event.models.Event import Event
from ...team.models.Team import Team
from ...user.models.User import User
from ..controllers.user import join_event_controller

events_user_namespace = Namespace("/events", description="event endpoints for users")


@events_user_namespace.route("")
class EventList(Resource):
    @user_endpoint()
    def get(self):
        """Get all public events"""
        results = Event.get_all_events(public_only=True)
        return success_response(results)


@events_user_namespace.route("/<int:event_id>")
class EventDetail(Resource):
    @user_endpoint()
    @load_event(source=LoaderType.PARAM)
    def get(self, event_id: int, event: Event):
        """Get event details"""
        return success_response(event)


@events_user_namespace.route("/<int:event_id>/me/eligibility")
class EventEligibility(Resource):
    @user_endpoint()
    @load_event(source=LoaderType.PARAM)
    def get(self, event_id: int, event: Event):
        """Check event eligibility"""
        # TODO - Actually implement eligibility check
        # event.registration_open = True
        # current time is inbetween registration start and end dates (if set)
        # user is not already in the event (i.e. does not have a demographic or is on a team)

        return success_response(True)


@events_user_namespace.route("/<int:event_id>/me/register")
class EventRegistration(Resource):
    @user_endpoint(json_required=True)
    @load_event(source=LoaderType.PARAM)
    def post(self, event_id: int, current_user: User, json_data, event: Event):
        """Register for event"""
        has_invite = "invite_code" in json_data
        has_name = "team_name" in json_data

        if (not has_invite) and (not has_name):
            raise ValidationError("Either invite_code or team_name must be provided.")
        if has_invite and has_name:
            raise ValidationError("Only one of invite_code or team_name can be provided.")

        validator = BaseValidator()
        if has_invite:
            validator.validate_string(json_data, "invite_code", 32, required=False, friendly_name="Invite code")
        if has_name:
            validator.validate_string(json_data, "team_name", 128, required=False, friendly_name="Team name")

        parsed_data = validator.validate()

        team = join_event_controller(event=event, user=current_user, **parsed_data)

        return success_response(team, status_code=201)


@events_user_namespace.route("/<int:event_id>/me/team")
class EventTeam(Resource):
    @user_endpoint()
    @load_event(source=LoaderType.PARAM)
    @load_team_by_user_and_event()
    def get(self, event_id: int, team: Team, **kwargs):
        """Get team details"""
        return success_response(team)


@events_user_namespace.route("/<int:event_id>/me/team/members")
class EventTeamMembers(Resource):
    @user_endpoint()
    @load_event(source=LoaderType.PARAM)
    @load_team_by_user_and_event()
    def get(self, event_id: int, team: Team, **kwargs):
        """Get team members"""
        members = team.members
        return success_response(members)


@events_user_namespace.route("/<int:event_id>/challenges")
class EventChallenges(Resource):
    @user_endpoint()
    @load_event(source=LoaderType.PARAM)
    def get(self, event_id: int, event: Event):
        """Get all of the challenges within an event"""
        challenges = event.get_all_challenges()
        return success_response(challenges)


@events_user_namespace.route("/<int:event_id>/challenges/<int:challenge_id>")
class EventChallengeRender(Resource):
    @user_endpoint()
    @load_event(source=LoaderType.PARAM)
    @load_challenge(source=LoaderType.PARAM)
    @load_team_by_user_and_event()
    def get(self, event_id: int, challenge_id: int, event: Event, challenge: Challenge, team: Team):
        return success_response(challenge.render(team))


@events_user_namespace.route("/<int:event_id>/me/challenges")
class EventChallengeStatuses(Resource):
    @user_endpoint()
    @load_event(source=LoaderType.PARAM)
    @load_team_by_user_and_event()
    def get(self, event_id: int, event: Event, team: Team):
        """Get all challenges and their statuses for the current user's team in the event"""
        results = []

        for challenge in event.get_all_challenges():
            results.append(
                {
                    "challenge_id": challenge.id,
                    "total_points_available": sum(q.points for q in challenge.questions),
                    "total_points_scored": 100,  # TODO: Implement actual points scoring logic
                    "num_questions_solved": 1,  # TODO: Implement actual questions solved logic
                    "num_questions_available": len(challenge.questions),
                    "num_attempts_made": 5,  # TODO: Implement actual attempts made logic
                }
            )

        return success_response(results)
