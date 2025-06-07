# /plugin/routes/api/teams.py

from flask import request, session
from flask_restx import Namespace, Resource
from CTFd.utils.decorators import authed_only, admins_only
from CTFd.utils.user import get_current_user, is_admin

from ...controllers.team_controller import TeamController
from ...controllers.world_controller import WorldController

teams_namespace = Namespace("teams", description="team management operations")


@teams_namespace.route("")
class TeamList(Resource):

    @authed_only
    @teams_namespace.doc(
        description="Get teams in a specific world",
        params={"world_id": "World ID to filter teams (required)"},
        responses={
            200: "Success - Returns list of teams",
            400: "Bad request - Missing or invalid world_id",
            403: "Forbidden - User not authenticated",
        },
    )
    def get(self):
        """Get all teams in a world.

        Query Parameters:
            world_id (int): The world ID to list teams from.

        Returns:
            JSON response with team list and world info or error details.
        """
        world_id = request.args.get("world_id")

        if not world_id:
            return {
                "success": False,
                "errors": {"world_id": "World ID is required"},
            }, 400

        try:
            world_id = int(world_id)
        except ValueError:
            return {
                "success": False,
                "errors": {"world_id": "World ID must be a number"},
            }, 400

        result = TeamController.list_teams_in_world(world_id)

        if result["success"]:
            return {"success": True, "data": result}, 200
        else:
            return {"success": False, "errors": {"world": result["error"]}}, 400

    @authed_only
    @teams_namespace.doc(
        description="Create a new team in a world",
        params={},
        responses={
            201: "Success - Team created",
            400: "Bad request - Invalid data",
            403: "Forbidden - User not authenticated",
        },
    )
    def post(self):
        """Create a new team in the world with current user as captain.

        Request Body:
            name (str): The team name.
            world_id (int): The world ID where the team will be created.
            limit (int, optional): Max team size.
            ranked (bool, optional): Whether team is ranked.

        Returns:
            JSON response with created team info and invite code or error details.
        """
        data = request.get_json()

        if not data:
            return {"success": False, "errors": {"body": "JSON body is required"}}, 400

        required_fields = ["name", "world_id"]
        errors = {}

        for field in required_fields:
            if field not in data or not data[field]:
                errors[field] = f"{field} is required"

        if errors:
            return {"success": False, "errors": errors}, 400

        current_user = get_current_user()
        if not current_user:
            return {
                "success": False,
                "errors": {"auth": "User not found in session"},
            }, 403

        # optional fields
        limit = data.get("limit")  # none if not specified, controller will use world default
        ranked = data.get("ranked", False)

        result = TeamController.create_team(
            name=data["name"],
            world_id=data["world_id"],
            creator_id=current_user.id,
            limit=limit,
            ranked=ranked,
        )

        if result["success"]:
            return {
                "success": True,
                "data": {
                    "team": {
                        "id": result["team"].id,
                        "name": result["team"].name,
                        "limit": result["team"].limit,
                        "member_count": result["team"].member_count,
                        "is_full": result["team"].is_full,
                        "ranked": result["team"].ranked,
                        "world_id": result["team"].world_id,
                    },
                    "invite_code": result["invite_code"],
                    "message": result["message"],
                },
            }, 201
        else:
            return {"success": False, "errors": {"team": result["error"]}}, 400


@teams_namespace.route("/<int:team_id>")
@teams_namespace.param("team_id", "Team ID")
class TeamDetail(Resource):

    @authed_only
    @teams_namespace.doc(
        description="Get detailed information about a specific team",
        responses={
            200: "Success - Team details returned",
            403: "Forbidden - User not authenticated",
            404: "Not found - Team does not exist",
        },
    )
    def get(self, team_id):
        """Get detailed info about a team.

        Args:
            team_id (int): The team ID to get.

        Returns:
            JSON response with team details, members, and world info.
        """
        result = TeamController.get_team_info(team_id)

        if result["success"]:
            return {"success": True, "data": result}, 200
        else:
            return {"success": False, "errors": {"team": result["error"]}}, 404

    @authed_only
    @teams_namespace.doc(
        description="Update team details (Captain/Admin only)",
        responses={
            200: "Success - Team updated",
            400: "Bad request - Invalid data",
            403: "Forbidden - Not authorized",
            404: "Not found - Team does not exist",
        },
    )
    def patch(self, team_id):
        """Update team info with proper auth checks.

        Args:
            team_id (int): The team ID to update.

        Request Body:
            name (str): New team name.

        Returns:
            JSON response with updated team info or error details.
        """
        current_user = get_current_user()
        if not current_user:
            return {"success": False, "errors": {"auth": "User not found"}}, 403

        data = request.get_json() or {}
        new_name = data.get("name")

        if not new_name:
            return {"success": False, "errors": {"name": "New name is required"}}, 400

        result = TeamController.update_team(
            team_id=team_id,
            actor_id=current_user.id,
            new_name=new_name,
            is_admin=is_admin(),
        )

        if result["success"]:
            return {"success": True, "data": {"message": result["message"]}}, 200
        else:
            status_code = 403 if "not authorized" in result["error"].lower() else 400
            return {
                "success": False,
                "errors": {"update": result["error"]},
            }, status_code

    @authed_only
    @teams_namespace.doc(
        description="Disband a team (Captain/Admin only)",
        responses={
            200: "Success - Team disbanded",
            400: "Bad request - Cannot disband team",
            403: "Forbidden - Not authorized",
            404: "Not found - Team does not exist",
        },
    )
    def delete(self, team_id):
        """Disband a team and remove all its members.

        Args:
            team_id (int): The team ID to disband.

        Returns:
            JSON response with confirmation message or error details.
        """
        current_user = get_current_user()
        if not current_user:
            return {"success": False, "errors": {"auth": "User not found"}}, 403

        user_is_admin = is_admin()

        result = TeamController.disband_team(team_id=team_id, actor_id=current_user.id, is_admin=user_is_admin)

        if result["success"]:
            return {"success": True, "data": {"message": result["message"]}}, 200
        else:
            status_code = 403 if "not authorized" in result["error"].lower() else 400
            return {
                "success": False,
                "errors": {"delete": result["error"]},
            }, status_code


@teams_namespace.route("/<int:team_id>/join")
@teams_namespace.param("team_id", "Team ID")
class TeamJoin(Resource):

    @authed_only
    @teams_namespace.doc(
        description="Join a specific team in a world",
        params={"world_id": "World ID where the team exists (required in body)"},
        responses={
            200: "Success - Joined team",
            400: "Bad request - Cannot join team",
            403: "Forbidden - User not authenticated",
            404: "Not found - Team does not exist",
        },
    )
    def post(self, team_id):
        """Join the team as a member.

        Args:
            team_id (int): The team ID to join.

        Request Body:
            world_id (int): The world ID containing the team.

        Returns:
            JSON response with team info and membership details.
        """
        data = request.get_json() or {}
        world_id = data.get("world_id")

        if not world_id:
            return {
                "success": False,
                "errors": {"world_id": "World ID is required"},
            }, 400

        current_user = get_current_user()
        if not current_user:
            return {
                "success": False,
                "errors": {"auth": "User not found in session"},
            }, 403

        result = TeamController.join_team(user_id=current_user.id, team_id=team_id, world_id=world_id)

        if result["success"]:
            return {
                "success": True,
                "data": {
                    "message": result["message"],
                    "team": {
                        "id": result["team"].id,
                        "name": result["team"].name,
                        "member_count": result["team"].member_count,
                        "limit": result["team"].limit,
                    },
                },
            }, 200
        else:
            return {"success": False, "errors": {"join": result["error"]}}, 400


@teams_namespace.route("/leave")
class TeamLeave(Resource):

    @authed_only
    @teams_namespace.doc(
        description="Leave current team in a specific world",
        params={"world_id": "World ID to leave team from (required in body)"},
        responses={
            200: "Success - Left team",
            400: "Bad request - Not in a team or invalid world",
            403: "Forbidden - User not authenticated",
        },
    )
    def post(self):
        """Leave the current team in the world.

        Request Body:
            world_id (int): The world ID to leave team from.

        Returns:
            JSON response with confirmation message and former team name.
        """
        data = request.get_json() or {}
        world_id = data.get("world_id")

        if not world_id:
            return {
                "success": False,
                "errors": {"world_id": "World ID is required"},
            }, 400

        current_user = get_current_user()
        if not current_user:
            return {
                "success": False,
                "errors": {"auth": "User not found in session"},
            }, 403

        result = TeamController.leave_team(user_id=current_user.id, world_id=world_id)

        if result["success"]:
            return {
                "success": True,
                "data": {
                    "message": result["message"],
                    "former_team": result["former_team"],
                },
            }, 200
        else:
            return {"success": False, "errors": {"leave": result["error"]}}, 400


@teams_namespace.route("/join-by-code")
class TeamJoinByCode(Resource):

    @authed_only
    @teams_namespace.doc(
        description="Join a team using an invite code",
        params={"invite_code": "Team invite code (required in body)"},
        responses={
            200: "Success - Joined team via invite code",
            400: "Bad request - Invalid invite code or cannot join",
            403: "Forbidden - User not authenticated",
        },
    )
    def post(self):
        """Join a team using its invite code.

        Request Body:
            invite_code (str): The team's invite code.

        Returns:
            JSON response with team info and join confirmation.
        """
        data = request.get_json() or {}
        invite_code = data.get("invite_code")

        if not invite_code:
            return {
                "success": False,
                "errors": {"invite_code": "Invite code is required"},
            }, 400

        current_user = get_current_user()
        if not current_user:
            return {
                "success": False,
                "errors": {"auth": "User not found in session"},
            }, 403

        result = TeamController.join_team_by_invite_code(user_id=current_user.id, invite_code=invite_code)

        if result["success"]:
            return {
                "success": True,
                "data": {
                    "message": result["message"],
                    "team": {
                        "id": result["team"].id,
                        "name": result["team"].name,
                        "member_count": result["team"].member_count,
                        "limit": result["team"].limit,
                    },
                    "invite_code": result["invite_code"],
                    "joined_via_invite": result["joined_via_invite"],
                },
            }, 200
        else:
            return {"success": False, "errors": {"invite": result["error"]}}, 400


@teams_namespace.route("/<int:team_id>/captain")
@teams_namespace.param("team_id", "Team ID")
class TeamCaptain(Resource):

    @authed_only
    @teams_namespace.doc(
        description="Get the current captain of a team",
        responses={
            200: "Success - Captain information returned",
            403: "Forbidden - User not authenticated",
            404: "Not found - Team does not exist or has no captain",
        },
    )
    def get(self, team_id):
        """Get the current captain info for the team.

        Args:
            team_id (int): The team ID.

        Returns:
            JSON response with captain user ID and status info.
        """
        result = TeamController.get_team_captain(team_id)

        if result["success"]:
            return {"success": True, "data": result}, 200
        else:
            return {"success": False, "errors": {"captain": result["error"]}}, 404

    @authed_only
    @teams_namespace.doc(
        description="Assign team captain",
        params={"user_id": "User ID (required)"},
        responses={
            200: "Success",
            400: "Bad request",
            403: "Forbidden",
            404: "Not found",
        },
    )
    def post(self, team_id):
        """Transfer team captaincy to another member.

        Args:
            team_id (int): The team ID.

        Request Body:
            user_id (int): The user ID of the new captain.

        Returns:
            JSON response with new captain info and confirmation.
        """

        current_user = get_current_user()
        if not current_user:
            return {
                "success": False,
                "errors": {"auth": "User not found in session"},
            }, 403

        data = request.get_json() or {}
        new_captain_user_id = data.get("user_id")

        if not new_captain_user_id:
            return {"success": False, "errors": {"user_id": "User ID is required"}}, 400

        try:
            new_captain_user_id = int(new_captain_user_id)
        except (ValueError, TypeError):
            return {
                "success": False,
                "errors": {"user_id": "User ID must be a number"},
            }, 400

        result = TeamController.transfer_captaincy(
            team_id=team_id,
            new_captain_id=new_captain_user_id,
            actor_id=current_user.id,
            is_admin=is_admin(),
        )

        if result["success"]:
            return {"success": True, "data": result}, 200
        else:
            status_code = (
                403
                if "not authorized" in result["error"].lower()
                else 404 if "does not exist" in result["error"] else 400
            )
            return {
                "success": False,
                "errors": {"captain": result["error"]},
            }, status_code

    @authed_only
    @teams_namespace.doc(
        description="Remove the current captain from a team",
        responses={
            200: "Success - Captain removed",
            400: "Bad request - Cannot remove captain",
            403: "Forbidden - User not authenticated",
            404: "Not found - Team does not exist or has no captain",
        },
    )
    def delete(self, team_id):
        """Demote the current captain to a regular member.

        Args:
            team_id (int): The team ID.

        Returns:
            JSON response with confirmation message.
        """
        result = TeamController.remove_captain(team_id)

        if result["success"]:
            return {
                "success": True,
                "data": {"message": result["message"], "team_id": team_id},
            }, 200
        else:
            return {"success": False, "errors": {"captain": result["error"]}}, 400


@teams_namespace.route("/<int:team_id>/members/<int:user_id>")
@teams_namespace.param("team_id", "Team ID")
@teams_namespace.param("user_id", "User ID of the member")
class TeamMemberManager(Resource):

    @authed_only
    @teams_namespace.doc(
        description="Remove a member from a team (Captain/Admin only)",
        responses={
            200: "Success - Member removed",
            400: "Bad request - Cannot remove member",
            403: "Forbidden - Not authorized",
            404: "Not found - Team or member does not exist",
        },
    )
    def delete(self, team_id, user_id):
        """Remove a member from the team (Captain/Admin only).

        Args:
            team_id (int): The team ID.
            user_id (int): The member ID to remove.

        Returns:
            JSON response with confirmation message or error details.
        """
        current_user = get_current_user()
        if not current_user:
            return {"success": False, "errors": {"auth": "User not found"}}, 403

        result = TeamController.remove_member(
            team_id=team_id,
            member_to_remove_id=user_id,
            actor_id=current_user.id,
            is_admin=is_admin(),
        )

        if result["success"]:
            return {"success": True, "data": {"message": result["message"]}}, 200
        else:
            status_code = 403 if "not authorized" in result["error"].lower() else 400
            return {
                "success": False,
                "errors": {"remove": result["error"]},
            }, status_code
