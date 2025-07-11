from flask_restx import Namespace, Resource

from ...core.utils import success_response

from ..models.Team import Team

from ...core.middleware.loaders import (
    LoaderType,
    load_team
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
    @admin_endpoint()
    @load_team(source=LoaderType.PARAM)
    def get(self, team_id, team):
        """Get a team"""
        return success_response(team)

@teams_admin_namespace.route("/<int:team_id>/members")
class TeamMembers(Resource):
    @admin_endpoint()
    @load_team(source=LoaderType.PARAM)
    def get(self, team_id, team):
        """Get all members of a team"""
        return success_response(team.members)