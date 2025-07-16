from flask_restx import Namespace, Resource
from flask import redirect

from ...core.utils import success_response, error_response

from ...event.models.Event import Event
from ...core.utils.validator import BaseValidator
from ...core.exceptions import ValidationError

from ...team.models.TeamMember import TeamMember

from ...core.middleware.loaders import (
    LoaderType,
    load_event,
    load_user,
    load_team_by_user_and_event,
)

from ...core.middleware import (
    user_endpoint,
)

from ...core.middleware.permission_middleware import get_permissions
from ...permissions.models.enums import PermissionEnum
from ...team.models.enums import TeamRole

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
    def get(self, event_id, event, **kwargs):
        """Get event details"""
        if not event.public:
            return error_response("Event not found", "not_found", 404)
        return success_response(event)


@events_user_namespace.route("/<int:event_id>/me/eligibility")
class EventEligibility(Resource):
    @user_endpoint()
    @load_event(source=LoaderType.PARAM)
    def get(self, event_id, event, **kwargs):
        """Check event eligibility"""

        if not event.public:
            return error_response("Event not found", "not_found", 404)

        try:
            Event.check_eligibility(event, kwargs.get("current_user"))
        except ValidationError as e:
            return error_response(str(e), "eligibility", 400)
        
        
        return success_response(True)


@events_user_namespace.route("/<int:event_id>/me/register")
class EventRegistration(Resource):
    @user_endpoint(json_required=True)
    @load_event(source=LoaderType.PARAM)
    def post(self, event_id, current_user, json_data, event):
        """Register for event"""
        has_invite = "invite_code" in json_data
        has_name = "team_name" in json_data

        if not event.public:
            return error_response("Event not found", "not_found", 404)

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

        parsed_data = validator.validate()

        team = join_event_controller(event=event, user=current_user, **parsed_data)

        return success_response(team, status_code=201)


@events_user_namespace.route("/<int:event_id>/me/team")
class EventTeam(Resource):
    @user_endpoint()
    @load_event(source=LoaderType.PARAM)
    @load_team_by_user_and_event()
    def get(self, event_id, team, **kwargs):
        """Get team details"""
        return success_response(team)


@events_user_namespace.route("/<int:event_id>/me/team/members")
class EventTeamMembers(Resource):
    @user_endpoint()
    @load_event(source=LoaderType.PARAM)
    @load_team_by_user_and_event()
    def get(self, event_id, team, **kwargs):
        """Get team members"""
        members = team.get_full_team_details()['team_members']
        return success_response(members)


@events_user_namespace.route("/<int:event_id>/me/team/kick")
class EventTeamKick(Resource):
    @user_endpoint(json_required=True)
    @load_event(source=LoaderType.PARAM)
    @load_user(source=LoaderType.BODY)
    @load_team_by_user_and_event()
    @get_permissions
    def post(self, event_id, **kwargs):
        """Kick a user from the user's team in the event"""
        json_data = kwargs.get("json_data", {})
        user_id = json_data.get("user_id")
        team = kwargs.get("team")
        permissions = kwargs.get("permissions", [])
        if user_id == kwargs.get("current_user").id:
            return error_response("You cannot kick yourself from the team.", "validation", 400)
        if PermissionEnum.CAN_EDIT_TEAM not in permissions:
            return error_response("You do not have permission to kick team members", "forbidden", 403)


        team.remove_member_and_regenerate_code(user_id)
        return success_response()

@events_user_namespace.route("/<int:event_id>/me/team/promote")
class EventTeamPromote(Resource):
    @user_endpoint(json_required=True)
    @load_event(source=LoaderType.PARAM)
    @load_user(source=LoaderType.BODY)
    @load_team_by_user_and_event()
    @get_permissions
    def post(self, event_id, team, json_data, **kwargs):
        """Promote a user to team leader in the user's team in the event"""
        user = kwargs.get("user")
        permissions = kwargs.get("permissions", [])

        if user.id == kwargs.get("current_user").id:
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
    def get(self, event_id, current_user,**kwargs):
        """Leave the user's team in the event"""
        team = kwargs.get("team")
        team_member = TeamMember.find_by_user_and_team(current_user.id, team.id)
        if team_member.role == TeamRole.CAPTAIN:
            return error_response("You cannot leave the team as a captain. Please promote another member first.", "forbidden", 403)
        team_member.remove_team_member(commit=True)
        if len(team.members) == 0:
            team.delete()
        


        return redirect(f"/ng/events/{event_id}/me/register", code=303)
