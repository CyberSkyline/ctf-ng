"""
Team management API routes.
"""

from flask import g
from flask_restx import Namespace, Resource
from CTFd.utils.user import is_admin

from ..controllers import (
    create_team,
    join_team,
    leave_team,
    get_team_info,
    update_team,
    disband_team,
    remove_member,
    transfer_captaincy,
    get_team_captain,
    list_all_teams,
)
from ...core.middleware import (
    user_endpoint,
    admin_endpoint,
    load_team,
    load_event_from_request,
    load_team_and_event,
    load_target_member,
    load_user_team_in_event,
    require_team_captain,
    require_team_member_management,
    check_team_join_eligibility,
    load_team_and_event_by_invite,
)
from ...core.utils import success_response
from ...core.validation import (
    validate_team_creation,
    validate_team_update,
    validate_team_leave,
    validate_team_join_by_code,
    validate_captain_assignment,
)
from ...core.docs import (
    LIST_ALL_TEAMS_DOC,
    CREATE_TEAM_DOC,
    GET_TEAM_DOC,
    UPDATE_TEAM_DOC,
    DISBAND_TEAM_DOC,
    JOIN_TEAM_DOC,
    LEAVE_TEAM_DOC,
    GET_CAPTAIN_DOC,
    TRANSFER_CAPTAINCY_DOC,
    REMOVE_MEMBER_DOC,
)

teams_namespace = Namespace("teams", description="team management operations")


@teams_namespace.route("")
class TeamList(Resource):
    @admin_endpoint()
    @teams_namespace.doc(**LIST_ALL_TEAMS_DOC)
    def get(self):
        """Get all teams"""
        result = list_all_teams()
        return success_response(result)

    @user_endpoint(json_required=True, validation_func=validate_team_creation)
    @load_event_from_request()
    @check_team_join_eligibility()
    @teams_namespace.doc(**CREATE_TEAM_DOC)
    def post(self):
        """Create team"""
        data = g.validated_data
        result = create_team(
            name=data["name"],
            event_id=data["event_id"],
            creator_id=g.user.id,
            ranked=data.get("ranked", False),
        )
        return success_response(result, status_code=201)


@teams_namespace.route("/<int:team_id>")
class TeamDetail(Resource):
    @user_endpoint()
    @load_team()
    @teams_namespace.doc(**GET_TEAM_DOC)
    def get(self, team_id):
        """Get team details"""
        result = get_team_info(team_id)
        return success_response(result)

    @user_endpoint(json_required=True, validation_func=validate_team_update)
    @load_team()
    @require_team_captain()
    @teams_namespace.doc(**UPDATE_TEAM_DOC)
    def patch(self, team_id):
        """Update team"""
        data = g.validated_data
        result = update_team(
            team_id=team_id,
            actor_id=g.user.id,
            new_name=data.get("name"),
            is_admin=is_admin(),
        )
        return success_response(result)

    @user_endpoint()
    @load_team()
    @require_team_captain()
    @teams_namespace.doc(**DISBAND_TEAM_DOC)
    def delete(self, team_id):
        """Disband team"""
        result = disband_team(team_id, g.user.id, is_admin())
        return success_response(result)


@teams_namespace.route("/join")
class TeamJoin(Resource):
    @user_endpoint(json_required=True, validation_func=validate_team_join_by_code)
    @load_team_and_event_by_invite()
    @check_team_join_eligibility()
    @teams_namespace.doc(**JOIN_TEAM_DOC)
    def post(self):
        """Join team"""
        data = g.validated_data
        result = join_team(g.user.id, data["invite_code"])
        return success_response(result)


@teams_namespace.route("/leave")
class TeamLeave(Resource):
    @user_endpoint(json_required=True, validation_func=validate_team_leave)
    @load_user_team_in_event()
    @teams_namespace.doc(**LEAVE_TEAM_DOC)
    def post(self):
        """Leave team"""
        result = leave_team()
        return success_response(result)


@teams_namespace.route("/<int:team_id>/captain")
class TeamCaptain(Resource):
    @user_endpoint()
    @load_team()
    @teams_namespace.doc(**GET_CAPTAIN_DOC)
    def get(self, team_id):
        """Get captain"""
        result = get_team_captain(team_id)
        return success_response(result)

    @user_endpoint(json_required=True, validation_func=validate_captain_assignment)
    @load_team()
    @require_team_captain()
    @load_target_member()
    @teams_namespace.doc(**TRANSFER_CAPTAINCY_DOC)
    def post(self, team_id):
        """Transfer captaincy"""
        data = g.validated_data
        result = transfer_captaincy(team_id, data["user_id"], g.user.id, is_admin())
        return success_response(result)


@teams_namespace.route("/<int:team_id>/members/<int:user_id>")
class TeamMemberManager(Resource):
    @user_endpoint()
    @load_team_and_event()
    @require_team_member_management()
    @load_target_member()
    @teams_namespace.doc(**REMOVE_MEMBER_DOC)
    def delete(self, team_id, user_id):
        """Remove member"""
        result = remove_member(team_id, user_id, g.user.id, is_admin())
        return success_response(result)
