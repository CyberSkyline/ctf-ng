"""
Team Management Admin Routes
"""


from flask_restx import Namespace, Resource

from ...core.utils import (
    error_response,
    success_response,
)
from ...core.middleware import (
    admin_endpoint,
)
from ...core.middleware.loaders import (
    LoaderType,
    load_team,
    load_user,
)
from ..models.Team import Team
from ...user.models.User import User
from ...team.controllers.remove_member import remove_member


teams_admin_namespace = Namespace(
    "/admin/teams",
    description = "team endpoints for admins"
)


@teams_admin_namespace.route("")
class TeamList(Resource):
    @admin_endpoint()
    @teams_admin_namespace.doc(
        description="Get all teams",
        responses={
            200: "Success",
            403: "Forbidden - Admin access required",
            404: "No teams found",
            500: "Internal Server Error",
        },
    )
    def get(self, **kwargs):
        """
        Get all teams
        """
        teams = Team.get_all_teams()
        return success_response(teams)


@teams_admin_namespace.route("/<int:team_id>")
class TeamDetail(Resource):
    @admin_endpoint(json_required = False, validation_func = Team.validate)
    @load_team(source = LoaderType.PARAM)
    @teams_admin_namespace.doc(
        description="Get a team by ID",
        responses={
            200: "Success",
            404: "Team not found",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error",
        },
    )
    def get(self, team_id, team, **kwargs):
        """
        Get a team
        """
        return success_response(team)

    @admin_endpoint(json_required = True, validation_func = Team.validate)
    @load_team(source = LoaderType.PARAM)
    @teams_admin_namespace.doc(
        description="Update a team by ID",
        params={
            "json_data": {
                "description": "Updated team data",
                "in": "body",
                "required": True,
                "example": {
                    "name": "New Team Name",
                    "description": "Updated description"
                }
            }
        },
        responses={
            200: "Success",
            404: "Team not found",
            400: "Bad Request if validation fails",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error",
        },
    )
    def put(self, team_id, team, validated_data, **kwargs):
        """
        Update a team
        """
        if Team.team_name_contains_member_name(validated_data.get("name", team.name),[member.user.ctfd_user.name for member in team.members]):
            return error_response("Team name cannot include a member's name.", "validation",400)
        team.update_team(**validated_data)
        return success_response(team)


@teams_admin_namespace.route("/<int:team_id>/members")
class TeamMembers(Resource):
    @admin_endpoint()
    @load_team(source = LoaderType.PARAM)
    @teams_admin_namespace.doc(
        description="Get all members of a team",
        responses={
            200: "Success",
            404: "Team not found",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error",
        },
    )
    def get(self, team_id, team, **kwargs):
        """
        Get all members of a team
        """
        return success_response(team.members)


@teams_admin_namespace.route("/<int:team_id>/kick")
class TeamKick(Resource):
    @admin_endpoint(json_required = True, validation_func = User.validate)
    @load_team(source = LoaderType.PARAM)
    @load_user(source = LoaderType.BODY)
    @teams_admin_namespace.doc(
        description="Kick a user from a team",
        params={
            "user_id": {
                "description": "User ID to kick from the team",
                "in": "body",
                "required": True,
            "example": {
                "user_id": 123
                }
            }
        },
        responses={
            200: "Success",
            404: "Team or User not found",
            400: "Bad Request if user is not a member of the team",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error",
        },
    )
    def post(self, team_id, user, team, **kwargs):
        """
        Kick a user from a team
        """
        remove_member(team, user)
        return success_response()


@teams_admin_namespace.route("/<int:team_id>/promote")
class TeamPromote(Resource):
    @admin_endpoint(json_required = True)
    @load_team(source = LoaderType.PARAM)
    @load_user(source = LoaderType.BODY)
    @teams_admin_namespace.doc(
        description="Promote a user to team leader",
        params={
            "user_id": {
                "description": "User ID to promote to team leader",
                "in": "body",
                "required": True,
                "example": {
                    "user_id": 123
                }
            }
        },
        responses={
            200: "Success",
            404: "Team or User not found",
            400: "Bad Request if user is not a member of the team",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error",
        }
    )
    def post(self, team_id, user, team, **kwargs):
        """
        Promote a user to team leader
        """
        team.remove_captain_and_promote(user.id)
        return success_response()
