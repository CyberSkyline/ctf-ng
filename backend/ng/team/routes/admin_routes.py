from flask_restx import Namespace, Resource

from ...core.utils import success_response, error_response

from ..models.Team import Team
from ...user.models.User import User

from ...core.middleware.loaders import (
    LoaderType,
    load_team,
    load_user,
)

from ...core.middleware import (
    admin_endpoint,
)

teams_admin_namespace = Namespace("/admin/teams", description="team endpoints for admins")

@teams_admin_namespace.route("")
class TeamList(Resource):
    @admin_endpoint()
    def get(self, **kwargs):
        """Get all teams"""
        teams = Team.get_all_teams()
        return success_response(teams)

@teams_admin_namespace.route("/<int:team_id>")
class TeamDetail(Resource):
    @admin_endpoint(
        json_required=False, validation_func=Team.validate
    )
    @load_team(source=LoaderType.PARAM)
    def get(self, team_id, team, **kwargs):
        """Get a team"""
        return success_response(team)

    @admin_endpoint(json_required=True, validation_func=Team.validate)
    @load_team(source=LoaderType.PARAM)
    def patch(self, team_id, team, validated_data, **kwargs):
        """Update a team"""
        

        new_name = validated_data.get("name", team.name)
        if Team.team_name_contains_member_name(name=new_name, member_names=[m.user.ctfd_user.name for m in team.members]):
            return error_response(
                "Team name cannot include a member's name.",
                "validation",
                400,
            )

        team = team.update_name(team_id, new_name)

        return success_response(team)

@teams_admin_namespace.route("/<int:team_id>/members")
class TeamMembers(Resource):
    @admin_endpoint()
    @load_team(source=LoaderType.PARAM)
    def get(self, team_id, team, **kwargs):
        """Get all members of a team"""
        return success_response(team.members)


@teams_admin_namespace.route("/<int:team_id>/kick")
class TeamKick(Resource):
    @admin_endpoint(json_required=True, validation_func=User.validate)
    @load_team(source=LoaderType.PARAM)
    @load_user(source=LoaderType.BODY)
    def post(self, team_id, user, team, **kwargs):
        """Kick a user from a team"""

        team.remove_member_and_regenerate_code(user.id)
        return success_response()

@teams_admin_namespace.route("/<int:team_id>/promote")
class TeamPromote(Resource):
    @admin_endpoint(json_required=True)
    @load_team(source=LoaderType.PARAM)
    @load_user(source=LoaderType.BODY)
    def post(self, team_id, user, team, **kwargs):
        """Promote a user to team leader"""

        team.remove_captain_and_promote(user.id)
        return success_response()

