from flask_restx import Namespace, Resource

from ...core.utils import success_response, error_response

from ..models.Team import Team
from ...user.models.User import User

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
    @admin_endpoint(
        json_required=False, validation_func=Team.validate
    )
    @load_team(source=LoaderType.PARAM)
    def get(self, team_id, team, **kwargs):
        """Get a team"""
        return success_response(team)

    @admin_endpoint(json_required=True, validation_func=Team.validate)
    @load_team(source=LoaderType.PARAM)
    def patch(self, team_id, **kwargs):
        """Update a team"""
        json_data = kwargs.get("validated_data", None)
        if not json_data:
            return success_response({"message": "Invalid data"}, status_code=400)

        team = kwargs.get("team")

        member_names = [member.user.ctfd_user.name for member in team.members]
        new_name = json_data.get("name")
        if any(s in new_name for s in member_names):
            return error_response(
                "You cannot include a team member's name in the team name.",
                "validation",
                400
            )

        team = team.update_name(team_id, json_data.get("name"))

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
    def post(self, team_id, **kwargs):
        """Kick a user from a team"""
        user_id = kwargs.get("validated_data", {}).get("user_id")
        team = kwargs.get("team")

        success = team.remove_member_and_regenerate_code(user_id)
        if not success:
            return error_response({"message": "Kick failed"}, status_code=400)
        return success_response()

@teams_admin_namespace.route("/<int:team_id>/promote")
class TeamPromote(Resource):
    @admin_endpoint(json_required=True)
    @load_team(source=LoaderType.PARAM)
    def post(self, team_id, **kwargs):
        """Promote a user to team leader"""
        user_id = kwargs.get("validated_data", {}).get("user_id")
        team = kwargs.get("team")

        team.remove_captain_and_promote(user_id)
        return success_response()

