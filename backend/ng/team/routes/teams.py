"""
Team management API routes.
"""

from flask_restx import Namespace, Resource
from backend.ng.core.middleware.loaders import load_team_by_invite_code

from ..controllers import (
    get_team_info,
    get_team_captain,
    list_all_teams,
)

from ...core.middleware.loaders import (
    LoaderType,
    load_team,
)

from ...core.middleware.checks import (
    check_can_manage_team
)

from ...core.middleware import (
    user_endpoint,
    admin_endpoint,
)
from ...core.utils import success_response

from ..docs.api import (
    LIST_ALL_TEAMS_DOC,
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

    # TODO - This should be an admin-only endpoint. Users would create their team via the event registration page
    # @user_endpoint(json_required=True, validation_func=Team.validate)
    # @load_event(LoaderType.BODY)
    # @teams_namespace.doc(**CREATE_TEAM_DOC)
    # def post(self):
    #     """Create team"""
    #     data = g.validated_data
    #     result = create_team(
    #         name=data["name"],
    #         ranked=data.get("ranked", False),
    #     )
    #     return success_response(result, status_code=201)


@teams_namespace.route("/<int:team_id>")
class TeamDetail(Resource):
    @user_endpoint()
    @load_team(LoaderType.PARAM)
    @teams_namespace.doc(**GET_TEAM_DOC)
    def get(self, team_id):
        """Get team details"""
        result = get_team_info(team_id)
        return success_response(result)

    @user_endpoint(json_required=True)
    @load_team(LoaderType.PARAM)
    @check_can_manage_team()
    @teams_namespace.doc(**UPDATE_TEAM_DOC)
    def patch(self):
        raise Exception("Not implemented yet")

    @user_endpoint()
    @load_team(LoaderType.PARAM)
    @check_can_manage_team()
    @teams_namespace.doc(**DISBAND_TEAM_DOC)
    def delete(self):
        raise Exception("Not implemented yet")


@teams_namespace.route("/join")
class TeamJoin(Resource):
    @user_endpoint(json_required=True)
    @load_team_by_invite_code(LoaderType.BODY)
    @teams_namespace.doc(**JOIN_TEAM_DOC)
    def post(self, team):
        """Join team"""
        raise Exception("Not implemented yet")
        # result = join_team(g.user, team)
        # return success_response(result)


@teams_namespace.route("/leave")
class TeamLeave(Resource):
    @user_endpoint(json_required=True)
    @teams_namespace.doc(**LEAVE_TEAM_DOC)
    def post(self):
        raise Exception("Not implemented yet")
        # """Leave team"""
        # result = leave_team()
        # return success_response(result)


@teams_namespace.route("/<int:team_id>/captain")
class TeamCaptain(Resource):
    @user_endpoint()
    @load_team(LoaderType.PARAM)
    @teams_namespace.doc(**GET_CAPTAIN_DOC)
    def get(self, team):
        """Get captain"""
        result = get_team_captain(team)
        return success_response(result)

    @user_endpoint(json_required=True)
    @load_team(LoaderType.PARAM)
    # @load_user(LoaderType.BODY, input_key="user_id", output_key="target_user")
    # @check_can_manage_team()
    # @load_target_member()
    @teams_namespace.doc(**TRANSFER_CAPTAINCY_DOC)
    def post(self):
        raise Exception("Not implemented yet")
        # """Transfer captaincy"""
        # data = g.validated_data
        # result = transfer_captaincy(team_id, data["user_id"], g.user.id, is_admin())
        # return success_response(result)


@teams_namespace.route("/<int:team_id>/members/<int:user_id>")
class TeamMemberManager(Resource):
    @user_endpoint()
    @load_team(LoaderType.PARAM)
    @check_can_manage_team()
    # @load_target_member()
    @teams_namespace.doc(**REMOVE_MEMBER_DOC)
    def delete(self):
        raise Exception("Not implemented yet")
        """Remove member"""
        # result = remove_member(team_id, user_id, g.user.id, is_admin())
        # return success_response(result)
