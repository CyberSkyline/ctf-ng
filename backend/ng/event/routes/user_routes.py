"""
User Routes for Event Operations
"""

from datetime import datetime
from flask_restx import Namespace, Resource

from CTFd.models import db

from ... import config

from ...core.middleware import (
    user_endpoint,
)
from ...core.middleware.loaders import (
    load_user,
    LoaderType,
    load_event,
    load_challenge,
    load_team_by_user_and_event,
)
from ...core.exceptions import ValidationError
from ...core.utils.validator import BaseValidator
from ...core.middleware.permission_middleware import (
    get_permissions,
    event_only_public,
)
from ...core.utils import (
    error_response,
    success_response,
)
from ..controllers import (
    get_challenge_progress,
    join_event_controller,
)
from ...containers.controllers.start_containers import (
    start_containers,
)
from ...user.models.User import User
from ...team.models.Team import Team
from ...team.models.enums import TeamRole
from ...team.models.TeamMember import TeamMember

from ...event.models.Event import Event
from ...event.models.Demographic import Demographic
from ...challenge.models.Challenge import Challenge
from ...permissions.models.enums import PermissionEnum

from ._docs import (
    USER_LIST_EVENTS_DOC,
    USER_GET_EVENT_DOC,
    CHECK_ELIGIBILITY_DOC,
    REGISTER_FOR_EVENT_DOC,
    GET_MY_TEAM_DOC,
    GET_TEAM_MEMBERS_DOC,
    UPDATE_TEAM_NAME_DOC,
    KICK_TEAM_MEMBER_DOC,
    PROMOTE_TEAM_MEMBER_DOC,
    LEAVE_TEAM_DOC,
    LIST_CHALLENGES_DOC,
    GET_CHALLENGE_DOC,
    GET_CHALLENGE_PROGRESS_DOC,
    START_CHALLENGE_CONTAINERS_DOC,
)


events_user_namespace = Namespace(
    "/events",
    description = "event endpoints for users"
)


@events_user_namespace.route("")
class EventList(Resource):
    @events_user_namespace.doc(**USER_LIST_EVENTS_DOC)
    @user_endpoint()
    def get(self, **kwargs):
        """
        Get all public events
        """
        results = Event.get_all_events(public_only = True)
        return success_response(results)


@events_user_namespace.route("/<int:event_id>")
class EventDetail(Resource):
    @events_user_namespace.doc(**USER_GET_EVENT_DOC)
    @user_endpoint()
    @load_event(source = LoaderType.PARAM)
    @event_only_public
    def get(self, event_id, event, **kwargs):
        """
        Get event details
        """
        return success_response(event)


@events_user_namespace.route("/<int:event_id>/me/eligibility")
class EventEligibility(Resource):
    @events_user_namespace.doc(**CHECK_ELIGIBILITY_DOC)
    @user_endpoint()
    @load_event(source = LoaderType.PARAM)
    @event_only_public
    def get(self, event_id, event, current_user, **kwargs):
        """
        Check event eligibility
        """
        event.check_eligibility(current_user)
        return success_response(True)


@events_user_namespace.route("/<int:event_id>/me/register")
class EventRegistration(Resource):
    @events_user_namespace.doc(**REGISTER_FOR_EVENT_DOC)
    @user_endpoint(json_required = True)
    @load_event(source = LoaderType.PARAM)
    @event_only_public
    def post(self, event_id: str, current_user: User, json_data, event):
        """
        Register for event
        """
        has_invite = "invite_code" in json_data
        has_name = "team_name" in json_data

        if (not has_invite) and (not has_name):
            raise ValidationError(
                "Either invite_code or team_name must be provided."
            )
        if has_invite and has_name:
            raise ValidationError(
                "Only one of invite_code or team_name can be provided."
            )

        # Catch Unique team name validation
        validator = BaseValidator()
        if has_invite:
            validator.validate_string(
                json_data,
                "invite_code",
                max_length=config.INVITE_CODE_MAX_LENGTH,
                required = False,
                friendly_name = "Invite code"
            )
        if has_name:
            validator.validate_string(
                json_data,
                "team_name",
                min_length=config.TEAM_NAME_MIN_LENGTH,
                max_length=config.TEAM_NAME_MAX_LENGTH,
                required = False,
                friendly_name = "Team name"
            )
            if Team.team_name_contains_member_name(
                    name = json_data["team_name"],
                    member_names = [current_user.ctfd_user.name],
            ):
                return error_response(
                    "Team name cannot include a member's name.",
                    "validation",
                    400,
                )

        parsed_data = validator.validate()

        event.check_eligibility(current_user)

        team = join_event_controller(
            event = event,
            user = current_user,
            **parsed_data
        )
        return success_response(team, status_code = 201)


@events_user_namespace.route("/<int:event_id>/me/team")
class EventTeam(Resource):
    @events_user_namespace.doc(**GET_MY_TEAM_DOC)
    @user_endpoint()
    @load_event(source = LoaderType.PARAM)
    @load_team_by_user_and_event()
    def get(self, event_id: int, team: Team, **kwargs):
        """
        Get team details
        """
        return success_response(team)


@events_user_namespace.route("/<int:event_id>/me/team/members")
class EventTeamMembers(Resource):
    @events_user_namespace.doc(**GET_TEAM_MEMBERS_DOC)
    @user_endpoint()
    @load_event(source = LoaderType.PARAM)
    @load_team_by_user_and_event()
    def get(self, event_id: int, team: Team, **kwargs):
        """
        Get team members
        """
        return success_response(team.members)


@events_user_namespace.route("/<int:event_id>/me/team/update_name")
class EventTeamUpdateName(Resource):
    @events_user_namespace.doc(**UPDATE_TEAM_NAME_DOC)
    @user_endpoint(json_required = True)
    @load_event(source = LoaderType.PARAM)
    @load_team_by_user_and_event()
    @get_permissions
    def put(self, event_id, team, json_data, permissions, **kwargs):
        """
        Update team name
        """
        new_name = json_data.get("name")

        if Team.team_name_contains_member_name(
                name = new_name,
                member_names = [member.user.ctfd_user.name
                                for member in team.members],
        ):
            return error_response(
                "Team name cannot include a member's name.",
                "validation",
                400,
            )

        if team.event.end_time and team.event.end_time < datetime.utcnow():
            return error_response(
                "You cannot update the team name after the event has ended.",
                "forbidden",
                403
            )

        if PermissionEnum.CAN_EDIT_TEAM not in permissions:
            return error_response(
                "You do not have permission to update the team name",
                "forbidden",
                403
            )
        team.update_name(new_name)
        return success_response(team)


@events_user_namespace.route("/<int:event_id>/me/team/kick")
class EventTeamKick(Resource):
    @events_user_namespace.doc(**KICK_TEAM_MEMBER_DOC)
    @user_endpoint(json_required = True)
    @load_event(source = LoaderType.PARAM)
    @load_user(source = LoaderType.BODY)
    @load_team_by_user_and_event()
    @get_permissions
    def post(
        self,
        event_id: int,
        json_data,
        team: Team,
        permissions,
        current_user: User,
        **kwargs
    ):
        """
        Kick a user from the user's team in the event
        """
        user_id = json_data.get("user_id")
        if user_id == current_user.id:
            return error_response(
                "You cannot kick yourself from the team.",
                "validation",
                400
            )
        if PermissionEnum.CAN_EDIT_TEAM not in permissions:
            return error_response(
                "You do not have permission to kick team members",
                "forbidden",
                403
            )

        if team.event.end_time and team.event.end_time < datetime.utcnow():
            return error_response(
                "Cannot kick user after event has ended.",
                "forbidden",
                403
            )

        if team.event.locked:
            return error_response(
                "Cannot change team composition after the event has been locked",
                "forbidden",
                403
            )

        try:
            team.remove_member_and_regenerate_code(user_id, commit = False)
            demographic = Demographic.find_by_user_and_event(user_id, event_id)
            demographic.delete(commit = False)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        return success_response()


@events_user_namespace.route("/<int:event_id>/me/team/promote")
class EventTeamPromote(Resource):
    @events_user_namespace.doc(**PROMOTE_TEAM_MEMBER_DOC)
    @user_endpoint(json_required = True)
    @load_event(source = LoaderType.PARAM)
    @load_user(source = LoaderType.BODY)
    @load_team_by_user_and_event()
    @get_permissions
    def post(
        self,
        event_id,
        team,
        user,
        permissions,
        json_data,
        current_user,
        **kwargs
    ):
        """
        Promote a user to team leader in the user's team in the event
        """
        if user.id == current_user.id:
            return error_response(
                "You cannot promote yourself.",
                "validation",
                400
            )

        if PermissionEnum.CAN_EDIT_TEAM not in permissions:
            return error_response(
                "You do not have permission to promote team members",
                "forbidden",
                403
            )

        result = team.remove_captain_and_promote(user.id)
        return success_response(result)


@events_user_namespace.route("/<int:event_id>/me/team/leave")
class EventTeamLeave(Resource):
    @events_user_namespace.doc(**LEAVE_TEAM_DOC)
    @user_endpoint()
    @load_event(source = LoaderType.PARAM)
    @load_team_by_user_and_event()
    def post(self, event_id, event, team, current_user, **kwargs):
        """
        Leave the user's team in the event
        """
        team_member = TeamMember.find_by_user_and_team(
            current_user.id,
            team.id
        )
        if event.end_time and event.end_time < datetime.utcnow():
            return error_response(
                "You cannot leave the team after the event has ended.",
                "forbidden",
                403
            )
        if len(team.members) > 1 and team_member.role == TeamRole.CAPTAIN:
            return error_response(
                "You cannot leave the team as a captain. Please promote another member first.",
                "forbidden",
                403,
            )
        try:
            team_member.remove_team_member(commit = False)
            demographic = Demographic.find_by_user_and_event(
                current_user.id,
                event_id
            )
            demographic.delete(commit = False)
            if len(team.members) == 0:
                team.disband_team(commit = False)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return error_response(
                f"Failed to leave team: {str(e)}",
                "internal_error",
                500
            )
        return success_response()


@events_user_namespace.route("/<int:event_id>/challenges")
class EventChallenges(Resource):
    @events_user_namespace.doc(**LIST_CHALLENGES_DOC)
    @user_endpoint()
    @load_event(source = LoaderType.PARAM)
    def get(self, event_id: int, event: Event, **kwargs):
        """
        Get all of the challenges within an event
        """
        challenges = event.get_all_challenges()
        return success_response(challenges)


@events_user_namespace.route("/<int:event_id>/challenges/<int:challenge_id>")
class EventChallengeRender(Resource):
    @events_user_namespace.doc(**GET_CHALLENGE_DOC)
    @user_endpoint()
    @load_event(source = LoaderType.PARAM)
    @load_challenge(source = LoaderType.PARAM)
    @load_team_by_user_and_event()
    def get(
        self,
        event_id: int,
        challenge_id: int,
        event: Event,
        challenge: Challenge,
        team: Team,
        **kwargs
    ):
        """
        Render Challenge
        """
        return success_response(challenge.render(team))


@events_user_namespace.route("/<int:event_id>/me/challenges")
class EventChallengeStatuses(Resource):
    @events_user_namespace.doc(**GET_CHALLENGE_PROGRESS_DOC)
    @user_endpoint()
    @load_event(source = LoaderType.PARAM)
    @load_team_by_user_and_event()
    def get(self, event_id: int, event: Event, team: Team, **kwargs):
        """
        Get all challenges and their status
        """
        results = get_challenge_progress(
            event_id = event_id,
            team_id = team.id
        )
        return success_response(results)


@events_user_namespace.route(
    "/<int:event_id>/challenge/<int:challenge_id>/containers"
)
class EventChallengeStartContainers(Resource):
    @events_user_namespace.doc(**START_CHALLENGE_CONTAINERS_DOC)
    @user_endpoint()
    @load_event(source = LoaderType.PARAM)
    @load_team_by_user_and_event()
    def get(
        self,
        team: Team,
        current_user: User,
        challenge_id: int,
        event_id: int,
        event: Event
    ):
        """
        Challenge containers
        """
        started = start_containers(challenge_id, team.id, current_user)
        return success_response(started)
