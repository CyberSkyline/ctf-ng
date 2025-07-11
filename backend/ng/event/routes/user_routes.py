from flask_restx import Namespace, Resource

from ...core.utils import success_response

from ...event.models.Event import Event
from ...core.utils.validator import BaseValidator
from ...core.exceptions import ValidationError

from ...user.models.User import User

from ...core.middleware.loaders import (
    LoaderType,
    load_event,
    load_team_by_user_and_event,
)

from ...core.middleware import (
    user_endpoint,
)

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
    def get(self, event_id, event):
        """Get event details"""
        return success_response(event)
    
@events_user_namespace.route("/<int:event_id>/me/eligibility")
class EventEligibility(Resource):
    @user_endpoint()
    @load_event(source=LoaderType.PARAM)
    def get(self, event_id, event):
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
    def post(self, event_id : str, current_user : User, json_data, event):
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

        is_valid, errors, parsed_data = validator.is_valid()
        if not is_valid:
            raise ValidationError("Join event data is invalid.", errors=errors)

        team = join_event_controller(
            event=event,
            user=current_user,
            **parsed_data
        )

        return success_response(team, status_code=201)

@events_user_namespace.route("/<int:event_id>/me/team")
class EventTeam(Resource):
    @user_endpoint()
    @load_event(source=LoaderType.PARAM)
    @load_team_by_user_and_event()
    def get(self, event_id, team):
        """Get team details"""
        return success_response(team)

@events_user_namespace.route("/<int:event_id>/me/team/members")
class EventTeamMembers(Resource):
    @user_endpoint()
    @load_event(source=LoaderType.PARAM)
    @load_team_by_user_and_event()
    def get(self, event_id, team):
        """Get team members"""
        members = team.members
        return success_response(members)
