from flask_restx import Namespace, Resource
from flask import redirect


from ...core.utils import success_response, error_response

from ...event.models.Event import Event
from ...core.utils.validator import BaseValidator
from ...challenge.models.Challenge import Challenge

from ...core.exceptions import ValidationError

from ...team.models.TeamMember import TeamMember

from ...core.middleware.loaders import (
    LoaderType,
    load_challenge,
    load_event,
    load_user,
    load_team_by_user_and_event,
)

from ...core.middleware import (
    user_endpoint,
)

from ...core.middleware.permission_middleware import get_permissions, event_only_public
from ...permissions.models.enums import PermissionEnum
from ...team.models.enums import TeamRole
from ...event.models.Demographic import Demographic
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
    def get(self, **kwargs):
        """Get all public events"""
        results = Event.get_all_events(public_only=True)
        return success_response(results)


@events_user_namespace.route("/<int:event_id>")
class EventDetail(Resource):
    @user_endpoint()
    @load_event(source=LoaderType.PARAM)
    @event_only_public
    def get(self, event_id, event, **kwargs):
        """Get event details"""

        return success_response(event)


@events_user_namespace.route("/<int:event_id>/me/eligibility")
class EventEligibility(Resource):
    @user_endpoint()
    @load_event(source=LoaderType.PARAM)
    @event_only_public
    def get(self, event_id, event, current_user, **kwargs):

        """Check event eligibility"""

        try:
            Event.check_eligibility(event, current_user)
        except ValidationError as e:
            return error_response(str(e), "eligibility", 400)
        
        
        return success_response(True)


@events_user_namespace.route("/<int:event_id>/me/register")
class EventRegistration(Resource):
    @user_endpoint(json_required=True)
    @load_event(source=LoaderType.PARAM)
    @event_only_public
    def post(self, event_id: str, current_user: User, json_data, event):

        """Register for event"""
        has_invite = "invite_code" in json_data
        has_name = "team_name" in json_data


        if (not has_invite) and (not has_name):
            raise ValidationError("Either invite_code or team_name must be provided.")
        if has_invite and has_name:
            raise ValidationError("Only one of invite_code or team_name can be provided.")


        #Catch Unique team name validation
        validator = BaseValidator()
        if has_invite:
            validator.validate_string(json_data, "invite_code", 32, required=False, friendly_name="Invite code")
        if has_name:
            validator.validate_string(json_data, "team_name", 128, required=False, friendly_name="Team name")
            if Team.team_name_contains_member_name(name=json_data["team_name"], member_names=[current_user.ctfd_user.name]):
                return error_response(
                    "Team name cannot include a member's name.",
                    "validation",
                    400,
                )


        parsed_data = validator.validate()

        Event.check_eligibility(event, current_user)

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
        return success_response(team.members)

@events_user_namespace.route("/<int:event_id>/me/team/update_name")
class EventTeamUpdateName(Resource):
    @user_endpoint(json_required=True)
    @load_event(source=LoaderType.PARAM)
    @load_team_by_user_and_event()
    @get_permissions
    def put(self, event_id, team, json_data, **kwargs):
        """Update team name"""

        if PermissionEnum.CAN_EDIT_TEAM not in kwargs.get("permissions", []):
            return error_response("You do not have permission to update the team name", "forbidden", 403)
        new_name = json_data.get("name")

        if Team.team_name_contains_member_name(name=new_name, member_names=[member.user.ctfd_user.name for member in team.members]):
            return error_response(
                "Team name cannot include a member's name.",
                "validation",
                400,
            )

        team.update_name(new_name)
        return success_response(team)


@events_user_namespace.route("/<int:event_id>/me/team/kick")
class EventTeamKick(Resource):
    @user_endpoint(json_required=True)
    @load_event(source=LoaderType.PARAM)
    @load_user(source=LoaderType.BODY)
    @load_team_by_user_and_event()
    @get_permissions
    def post(self, event_id, json_data, team, permissions, current_user, **kwargs):
        """Kick a user from the user's team in the event"""
        user_id = json_data.get("user_id")
        if user_id == current_user.id:
            return error_response("You cannot kick yourself from the team.", "validation", 400)
        if PermissionEnum.CAN_EDIT_TEAM not in permissions:
            return error_response("You do not have permission to kick team members", "forbidden", 403)


        team.remove_member_and_regenerate_code(user_id)
        demographic = Demographic.find_by_user_and_event(user_id, event_id)
        demographic.delete(commit=True)
        return success_response()

@events_user_namespace.route("/<int:event_id>/me/team/promote")
class EventTeamPromote(Resource):
    @user_endpoint(json_required=True)
    @load_event(source=LoaderType.PARAM)
    @load_user(source=LoaderType.BODY)
    @load_team_by_user_and_event()
    @get_permissions
    def post(self, event_id, team, user, permissions, json_data, current_user, **kwargs):
        """Promote a user to team leader in the user's team in the event"""

        if user.id == current_user.id:
            return error_response("You cannot promote yourself.", "validation", 400)

        if PermissionEnum.CAN_EDIT_TEAM not in permissions:
            return error_response("You do not have permission to promote team members", "forbidden", 403)

        result = team.remove_captain_and_promote(user.id)
        return success_response(result)

@events_user_namespace.route("/<int:event_id>/me/team/leave")
class EventTeamLeave(Resource):
    @user_endpoint()
    @load_event(source=LoaderType.PARAM)
    @load_team_by_user_and_event()
    def get(self, event_id, team, current_user,**kwargs):
        """Leave the user's team in the event"""
        team_member = TeamMember.find_by_user_and_team(current_user.id, team.id)
        if team_member.role == TeamRole.CAPTAIN:
            return error_response("You cannot leave the team as a captain. Please promote another member first.", "forbidden", 403)
        team_member.remove_team_member(commit=True)
        demographic = Demographic.find_by_user_and_event(current_user.id, event_id)
        demographic.delete(commit=True)
        if len(team.members) == 0:
            team.delete(commit=True)

        return redirect(f"/ng/events/{event_id}/me/register", code=303)



@events_user_namespace.route("/<int:event_id>/challenges")
class EventChallenges(Resource):
    @user_endpoint()
    @load_event(source=LoaderType.PARAM)
    def get(self, event_id: int, event: Event, **kwargs):
        """Get all of the challenges within an event"""
        challenges = event.get_all_challenges()
        return success_response(challenges)


@events_user_namespace.route("/<int:event_id>/challenges/<int:challenge_id>")
class EventChallengeRender(Resource):
    @user_endpoint()
    @load_event(source=LoaderType.PARAM)
    @load_challenge(source=LoaderType.PARAM)
    @load_team_by_user_and_event()
    def get(self, event_id: int, challenge_id: int, event: Event, challenge: Challenge, team: Team, **kwargs):
        return success_response(challenge.render(team))


@events_user_namespace.route("/<int:event_id>/me/challenges")
class EventChallengeStatuses(Resource):
    @user_endpoint()
    @load_event(source=LoaderType.PARAM)
    @load_team_by_user_and_event()
    def get(self, event_id: int, event: Event, team: Team, **kwargs):
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
