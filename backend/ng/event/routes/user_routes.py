from datetime import datetime

from CTFd.models import db
from flask import redirect
from flask_restx import Namespace, Resource

from ...challenge.models.Challenge import Challenge
from ...containers.controllers.start_containers import start_containers
from ...core.exceptions import ValidationError
from ...core.middleware import (
    user_endpoint,
)
from ...core.middleware.loaders import (
    LoaderType,
    load_challenge,
    load_event,
    load_team_by_user_and_event,
    load_user,
)
from ...core.middleware.permission_middleware import event_only_public, get_permissions
from ...core.utils import error_response, success_response
from ...core.utils.validator import BaseValidator
from ...event.models.Demographic import Demographic
from ...event.models.Event import Event
from ...permissions.models.enums import PermissionEnum
from ...team.models.enums import TeamRole
from ...team.models.Team import Team
from ...team.models.TeamMember import TeamMember
from ...user.models.User import User
from ..controllers.user import join_event_controller

events_user_namespace = Namespace("/events", description="event endpoints for users")


@events_user_namespace.route("")
class EventList(Resource):
    @user_endpoint()
    @events_user_namespace.doc(
        description="Get all public events.",
        responses={
            200: "Success",
            400: "Bad Request",
            500: "Internal Server Error",
        },
    )
    def get(self, **kwargs):
        """Get all public events"""
        results = Event.get_all_events(public_only=True)
        return success_response(results)


@events_user_namespace.route("/<int:event_id>")
class EventDetail(Resource):
    @user_endpoint()
    @load_event(source=LoaderType.PARAM)
    @event_only_public
    @events_user_namespace.doc(
        description="Get event details.",
        responses={
            200: "Success",
            404: "Event not found",
            403: "Forbidden if event is not public",
        },
    )
    def get(self, event_id, event, **kwargs):
        """Get event details"""

        return success_response(event)


@events_user_namespace.route("/<int:event_id>/me/eligibility")
class EventEligibility(Resource):
    @user_endpoint()
    @load_event(source=LoaderType.PARAM)
    @event_only_public
    @events_user_namespace.doc(
        description="Check if the current user is eligible to join the event.",
        responses={
            200: "Eligible",
            403: "Forbidden if not eligible",
            404: "Event not found",
        },
    )
    def get(self, event_id, event, current_user, **kwargs):
        """Check event eligibility"""

        event.check_eligibility(current_user)

        return success_response(True)


@events_user_namespace.route("/<int:event_id>/me/register")
class EventRegistration(Resource):
    @user_endpoint(json_required=True)
    @load_event(source=LoaderType.PARAM)
    @event_only_public
    @events_user_namespace.doc(
        description="Register for an event.",
        responses={
            201: "Registered successfully",
            400: "Bad Request if invite_code or team_name is missing",
            403: "Forbidden if not eligible or event is locked",
            404: "Not Found if event does not exist",
        },
        params={
            "invite_code": {
                "description": "Invite code for the event",
                "in": "body",
                "required": False,
                "example": "12lkjgchldjkzz",
            },
            "team_name": {
                "description": "Name of the team to join or create",
                "in": "body",
                "required": False,
                "example": "My new team",
            },
        },
    )
    def post(self, event_id: str, current_user: User, json_data, event):
        """Register for event"""
        has_invite = "invite_code" in json_data
        has_name = "team_name" in json_data

        if (not has_invite) and (not has_name):
            raise ValidationError("Either invite_code or team_name must be provided.")
        if has_invite and has_name:
            raise ValidationError("Only one of invite_code or team_name can be provided.")

        # Catch Unique team name validation
        validator = BaseValidator()
        if has_invite:
            validator.validate_string(json_data, "invite_code", 32, required=False, friendly_name="Invite code")
        if has_name:
            validator.validate_string(json_data, "team_name", 128, required=False, friendly_name="Team name")
            if Team.team_name_contains_member_name(
                name=json_data["team_name"],
                member_names=[current_user.ctfd_user.name],
            ):
                return error_response(
                    "Team name cannot include a member's name.",
                    "validation",
                    400,
                )

        parsed_data = validator.validate()

        event.check_eligibility(current_user)

        team = join_event_controller(event=event, user=current_user, **parsed_data)

        return success_response(team, status_code=201)


@events_user_namespace.route("/<int:event_id>/me/team")
class EventTeam(Resource):
    @user_endpoint()
    @load_event(source=LoaderType.PARAM)
    @load_team_by_user_and_event()
    @events_user_namespace.doc(
        description="Get the user's team in the event.",
        responses={
            200: "Success",
            404: "Not Found if user is not part of a team",
        },
    )
    def get(self, event_id: int, team: Team, **kwargs):
        """Get team details"""
        return success_response(team)


@events_user_namespace.route("/<int:event_id>/me/team/members")
class EventTeamMembers(Resource):
    @user_endpoint()
    @load_event(source=LoaderType.PARAM)
    @load_team_by_user_and_event()
    @events_user_namespace.doc(
        description="Get all members of the user's team in the event.",
        responses={
            200: "Success",
            404: "Not Found if user is not part of a team",
        },
    )
    def get(self, event_id: int, team: Team, **kwargs):
        """Get team members"""
        return success_response(team.members)


@events_user_namespace.route("/<int:event_id>/me/team/update_name")
class EventTeamUpdateName(Resource):
    @user_endpoint(json_required=True)
    @load_event(source=LoaderType.PARAM)
    @load_team_by_user_and_event()
    @get_permissions
    @events_user_namespace.doc(
        description="Update the user's team name in the event.",
        responses={
            200: "Team name updated successfully",
            400: "Bad Request if team name is invalid",
            403: "Forbidden if user does not have permission to edit team or event has ended",
        },
        params={
            "name": {
                "description": "New name for the team",
                "in": "body",
                "required": True,
                "example": "New Team Name",
            }
        },
    )
    def put(self, event_id, team, json_data, permissions, **kwargs):
        """Update team name"""

        new_name = json_data.get("name")

        if Team.team_name_contains_member_name(
            name=new_name,
            member_names=[member.user.ctfd_user.name for member in team.members],
        ):
            return error_response(
                "Team name cannot include a member's name.",
                "validation",
                400,
            )

        if team.event.end_time and team.event.end_time < datetime.utcnow():
            return error_response("You cannot update the team name after the event has ended.", "forbidden", 403)

        if PermissionEnum.CAN_EDIT_TEAM not in permissions:
            return error_response("You do not have permission to update the team name", "forbidden", 403)
        team.update_name(new_name)
        return success_response(team)


@events_user_namespace.route("/<int:event_id>/me/team/kick")
class EventTeamKick(Resource):
    @user_endpoint(json_required=True)
    @load_event(source=LoaderType.PARAM)
    @load_user(source=LoaderType.BODY)
    @load_team_by_user_and_event()
    @get_permissions
    @events_user_namespace.doc(
        description="Kick a user from the user's team in the event.",
        responses={
            200: "User kicked successfully",
            400: "Bad Request if user_id is missing or invalid",
            403: "Forbidden if user does not have permission to kick team members or event has ended",
        },
        params={
            "user_id": {
                "description": "ID of the user to kick from the team",
                "in": "body",
                "required": True,
                "example": "12345",
            }
        },
    )
    def post(self, event_id: int, json_data, team: Team, permissions, current_user: User, **kwargs):
        """Kick a user from the user's team in the event"""
        user_id = json_data.get("user_id")
        if user_id == current_user.id:
            return error_response("You cannot kick yourself from the team.", "validation", 400)
        if PermissionEnum.CAN_EDIT_TEAM not in permissions:
            return error_response("You do not have permission to kick team members", "forbidden", 403)

        if team.event.end_time and team.event.end_time < datetime.utcnow():
            return error_response("Cannot kick user after event has ended.", "forbidden", 403)

        if team.event.locked:
            return error_response("Cannot change team composition after the event has been locked", "forbidden", 403)

        try:
            team.remove_member_and_regenerate_code(user_id, commit=False)
            demographic = Demographic.find_by_user_and_event(user_id, event_id)
            demographic.delete(commit=False)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        return success_response()


@events_user_namespace.route("/<int:event_id>/me/team/promote")
class EventTeamPromote(Resource):
    @user_endpoint(json_required=True)
    @load_event(source=LoaderType.PARAM)
    @load_user(source=LoaderType.BODY)
    @load_team_by_user_and_event()
    @get_permissions
    @events_user_namespace.doc(
        description="Removes the current user as team captain and promotes the supplied user to be the team captain.",
        responses={
            200: "User promoted successfully",
            400: "Bad Request if user_id is missing or invalid",
            403: "Forbidden if user does not have permission to promote team members or event has ended",
        },
        params={
            "user_id": {
                "description": "ID of the user to promote to team leader",
                "in": "body",
                "required": True,
                "example": "12345",
            }
        },
    )
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
    @events_user_namespace.doc(
        description="Leave the user's team in the event.",
        responses={
            200: "Left team successfully",
            403: "Forbidden if user is a captain or event has ended",
            404: "Not Found if user is not part of a team",
        },
    )
    def get(self, event_id, event, team, current_user, **kwargs):
        """Leave the user's team in the event"""
        team_member = TeamMember.find_by_user_and_team(current_user.id, team.id)
        if event.end_time and event.end_time < datetime.utcnow():
            return error_response("You cannot leave the team after the event has ended.", "forbidden", 403)
        if team_member.role == TeamRole.CAPTAIN:
            return error_response(
                "You cannot leave the team as a captain. Please promote another member first.",
                "forbidden",
                403,
            )
        try:
            team_member.remove_team_member(commit=True)
            demographic = Demographic.find_by_user_and_event(current_user.id, event_id)
            demographic.delete(commit=True)
            if len(team.members) == 0:
                team.delete(commit=True)
        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to leave team: {str(e)}", "internal_error", 500)

        return redirect(f"/ng/events/{event_id}/me/register", code=303)


@events_user_namespace.route("/<int:event_id>/challenges")
class EventChallenges(Resource):
    @user_endpoint()
    @load_event(source=LoaderType.PARAM)
    @events_user_namespace.doc(
        description="Get all challenges within an event.",
        responses={
            200: "Success",
            404: "Event not found",
        },
    )
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
    @events_user_namespace.doc(
        description="Render a challenge for the user's team in the event.",
        responses={
            200: "Success",
            404: "Challenge or Event not found",
        },
    )
    def get(self, event_id: int, challenge_id: int, event: Event, challenge: Challenge, team: Team, **kwargs):
        return success_response(challenge.render(team))


@events_user_namespace.route("/<int:event_id>/me/challenges")
class EventChallengeStatuses(Resource):
    @user_endpoint()
    @load_event(source=LoaderType.PARAM)
    @load_team_by_user_and_event()
    @events_user_namespace.doc(
        description="Get all challenges and their statuses for the current user's team in the event.",
        responses={
            200: "Success",
            404: "Event not found",
        },
    )
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


@events_user_namespace.route("/<int:event_id>/challenge/<int:challenge_id>/containers")
class EventChallengeStartContainers(Resource):
    @events_user_namespace.doc(
        description="Start a challenges containers",
        params={
            "event_id": "Event id challenge is in",
            "challenge_id": "Challenge id to start containers for",
        },
        responses={
            200: "Sucess",
            400: "Bad request",
        },
    )
    @user_endpoint()
    @load_event(source=LoaderType.PARAM)
    @load_team_by_user_and_event()
    def get(self, team: Team, current_user: User, challenge_id: int, event_id: int, event: Event):
        started = start_containers(challenge_id, team.id, current_user)
        return success_response(started)
