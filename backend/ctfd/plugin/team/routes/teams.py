# /plugin/team/routes/teams.py

from flask import request, g
from flask_restx import Namespace, Resource
from CTFd.utils.decorators import authed_only
from CTFd.utils.user import is_admin

from ..controllers.team_controller import TeamController
from ...utils.api_responses import controller_response, error_response, success_response
from ...utils.decorators import (
    authed_user_required,
    json_body_required,
    handle_integrity_error,
)
from ...utils.logger import get_logger
from ...utils import get_current_user_id
from ...utils.validators import (
    validate_team_creation,
    validate_team_update,
    validate_team_join,
    validate_team_leave,
    validate_team_join_by_code,
    validate_captain_assignment,
    validate_world_id_param,
)

teams_namespace = Namespace("teams", description="team management operations")
logger = get_logger(__name__)


@teams_namespace.route("")
class TeamList(Resource):
    @authed_only
    @handle_integrity_error
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

        is_valid, errors = validate_world_id_param(world_id)
        if not is_valid:
            logger.warning(
                "Validation failed for team list",
                extra={
                    "context": {
                        "errors": errors,
                        "user_id": get_current_user_id(),
                        "endpoint": "teams_list",
                        "world_id": world_id,
                    }
                },
            )
            return {"success": False, "errors": errors}, 400

        world_id = int(world_id)

        result = TeamController.list_teams_in_world(world_id)

        if result["success"]:
            logger.info(
                "Teams list retrieved",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "world_id": world_id,
                        "team_count": len(result.get("teams", [])),
                    }
                },
            )

        return controller_response(result, error_field="world")

    @authed_only
    @authed_user_required
    @json_body_required
    @handle_integrity_error
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
        data = g.json_data

        is_valid, errors = validate_team_creation(data)
        if not is_valid:
            logger.warning(
                "Validation failed for team creation",
                extra={
                    "context": {
                        "errors": errors,
                        "user_id": get_current_user_id(),
                        "endpoint": "team_create",
                        "data": data,
                    }
                },
            )
            return {"success": False, "errors": errors}, 400

        limit = data.get("limit")
        ranked = data.get("ranked", False)

        result = TeamController.create_team(
            name=data["name"],
            world_id=data["world_id"],
            creator_id=g.user.id,
            limit=limit,
            ranked=ranked,
        )

        if result["success"]:
            logger.info(
                "Team created successfully",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "team_id": result["team"].id,
                        "team_name": result["team"].name,
                        "world_id": result["team"].world_id,
                    }
                },
            )
            return success_response(result, status_code=201)
        else:
            logger.warning(
                "Team creation failed",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "error": result["error"],
                        "endpoint": "team_create",
                    }
                },
            )
            return error_response(result["error"], "team", 400)


@teams_namespace.route("/<int:team_id>")
@teams_namespace.param("team_id", "Team ID")
class TeamDetail(Resource):
    @authed_only
    @handle_integrity_error
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
            logger.info(
                "Team info retrieved",
                extra={"context": {"user_id": get_current_user_id(), "team_id": team_id}},
            )
            return success_response(result)
        else:
            logger.warning(
                "Team not found",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "team_id": team_id,
                        "error": result["error"],
                    }
                },
            )
            return error_response(result["error"], "team", 404)

    @authed_only
    @authed_user_required
    @handle_integrity_error
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
        data = request.get_json() or {}

        is_valid, errors = validate_team_update(data)
        if not is_valid:
            logger.warning(
                "Validation failed for team update",
                extra={
                    "context": {
                        "errors": errors,
                        "user_id": get_current_user_id(),
                        "endpoint": "team_update",
                        "team_id": team_id,
                    }
                },
            )
            return {"success": False, "errors": errors}, 400

        new_name = data.get("name")

        result = TeamController.update_team(
            team_id=team_id,
            actor_id=g.user.id,
            new_name=new_name,
            is_admin=is_admin(),
        )

        if result["success"]:
            logger.info(
                "Team updated successfully",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "team_id": team_id,
                        "new_name": new_name,
                    }
                },
            )
            return success_response(result)
        else:
            status_code = 403 if "not authorized" in result["error"].lower() else 400
            if status_code == 403:
                logger.warning(
                    "Unauthorized team update attempt",
                    extra={
                        "context": {
                            "user_id": get_current_user_id(),
                            "team_id": team_id,
                            "error": result["error"],
                        }
                    },
                )
            return error_response(result["error"], "update", status_code)

    @authed_only
    @authed_user_required
    @handle_integrity_error
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
        user_is_admin = is_admin()

        result = TeamController.disband_team(team_id=team_id, actor_id=g.user.id, is_admin=user_is_admin)

        if result["success"]:
            logger.info(
                "Team disbanded successfully",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "team_id": team_id,
                        "is_admin": user_is_admin,
                    }
                },
            )
            return success_response(result)
        else:
            status_code = 403 if "not authorized" in result["error"].lower() else 400
            if status_code == 403:
                logger.warning(
                    "Unauthorized team disband attempt",
                    extra={
                        "context": {
                            "user_id": get_current_user_id(),
                            "team_id": team_id,
                            "error": result["error"],
                        }
                    },
                )
            return error_response(result["error"], "delete", status_code)


@teams_namespace.route("/<int:team_id>/join")
@teams_namespace.param("team_id", "Team ID")
class TeamJoin(Resource):
    @authed_only
    @authed_user_required
    @handle_integrity_error
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

        is_valid, errors = validate_team_join(data)
        if not is_valid:
            logger.warning(
                "Validation failed for team join",
                extra={
                    "context": {
                        "errors": errors,
                        "user_id": get_current_user_id(),
                        "endpoint": "team_join",
                        "team_id": team_id,
                    }
                },
            )
            return {"success": False, "errors": errors}, 400

        world_id = data.get("world_id")

        result = TeamController.join_team(user_id=g.user.id, team_id=team_id, world_id=world_id)

        if result["success"]:
            logger.info(
                "User joined team successfully",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "team_id": team_id,
                        "team_name": result["team"].name,
                        "world_id": world_id,
                    }
                },
            )
            return success_response(result)
        else:
            logger.warning(
                "Team join failed",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "team_id": team_id,
                        "world_id": world_id,
                        "error": result["error"],
                    }
                },
            )
            return error_response(result["error"], "join", 400)


@teams_namespace.route("/leave")
class TeamLeave(Resource):
    @authed_only
    @authed_user_required
    @handle_integrity_error
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

        is_valid, errors = validate_team_leave(data)
        if not is_valid:
            logger.warning(
                "Validation failed for team leave",
                extra={
                    "context": {
                        "errors": errors,
                        "user_id": get_current_user_id(),
                        "endpoint": "team_leave",
                    }
                },
            )
            return {"success": False, "errors": errors}, 400

        world_id = data.get("world_id")

        result = TeamController.leave_team(user_id=g.user.id, world_id=world_id)

        if result["success"]:
            logger.info(
                "User left team successfully",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "world_id": world_id,
                        "former_team": result["former_team"],
                    }
                },
            )
            return success_response(result)
        else:
            logger.warning(
                "Team leave failed",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "world_id": world_id,
                        "error": result["error"],
                    }
                },
            )
            return error_response(result["error"], "leave", 400)


@teams_namespace.route("/join-by-code")
class TeamJoinByCode(Resource):
    @authed_only
    @authed_user_required
    @handle_integrity_error
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

        is_valid, errors = validate_team_join_by_code(data)
        if not is_valid:
            logger.warning(
                "Validation failed for team join by code",
                extra={
                    "context": {
                        "errors": errors,
                        "user_id": get_current_user_id(),
                        "endpoint": "team_join_by_code",
                    }
                },
            )
            return {"success": False, "errors": errors}, 400

        invite_code = data.get("invite_code")

        result = TeamController.join_team_by_invite_code(user_id=g.user.id, invite_code=invite_code)

        if result["success"]:
            logger.info(
                "User joined team via invite code",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "team_id": result["team"].id,
                        "team_name": result["team"].name,
                        "invite_code": invite_code,
                    }
                },
            )
            return success_response(result)
        else:
            logger.warning(
                "Team join by invite code failed",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "invite_code": invite_code,
                        "error": result["error"],
                    }
                },
            )
            return error_response(result["error"], "invite", 400)


@teams_namespace.route("/<int:team_id>/captain")
@teams_namespace.param("team_id", "Team ID")
class TeamCaptain(Resource):
    @authed_only
    @handle_integrity_error
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
            logger.info(
                "Team captain info retrieved",
                extra={"context": {"user_id": get_current_user_id(), "team_id": team_id}},
            )
            return success_response(result)
        else:
            logger.warning(
                "Team captain not found",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "team_id": team_id,
                        "error": result["error"],
                    }
                },
            )
            return error_response(result["error"], "captain", 404)

    @authed_only
    @authed_user_required
    @handle_integrity_error
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
        data = request.get_json() or {}

        is_valid, errors = validate_captain_assignment(data)
        if not is_valid:
            logger.warning(
                "Validation failed for captain assignment",
                extra={
                    "context": {
                        "errors": errors,
                        "user_id": get_current_user_id(),
                        "endpoint": "captain_assignment",
                        "team_id": team_id,
                    }
                },
            )
            return {"success": False, "errors": errors}, 400

        new_captain_user_id = int(data.get("user_id"))

        result = TeamController.transfer_captaincy(
            team_id=team_id,
            new_captain_id=new_captain_user_id,
            actor_id=g.user.id,
            is_admin=is_admin(),
        )

        if result["success"]:
            logger.info(
                "Team captaincy transferred",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "team_id": team_id,
                        "new_captain_id": new_captain_user_id,
                        "is_admin": is_admin(),
                    }
                },
            )
            return success_response(result)
        else:
            status_code = (
                403
                if "not authorized" in result["error"].lower()
                else 404
                if "not found" in result["error"].lower()
                else 400
            )
            if status_code == 403:
                logger.warning(
                    "Unauthorized captain assignment attempt",
                    extra={
                        "context": {
                            "user_id": get_current_user_id(),
                            "team_id": team_id,
                            "new_captain_id": new_captain_user_id,
                            "error": result["error"],
                        }
                    },
                )
            return error_response(result["error"], "captain", status_code)

    @authed_only
    @handle_integrity_error
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
            logger.info(
                "Team captain removed",
                extra={"context": {"user_id": get_current_user_id(), "team_id": team_id}},
            )
            return success_response(result)
        else:
            logger.warning(
                "Captain removal failed",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "team_id": team_id,
                        "error": result["error"],
                    }
                },
            )
            return error_response(result["error"], "captain", 400)


@teams_namespace.route("/<int:team_id>/members/<int:user_id>")
@teams_namespace.param("team_id", "Team ID")
@teams_namespace.param("user_id", "User ID of the member")
class TeamMemberManager(Resource):
    @authed_only
    @authed_user_required
    @handle_integrity_error
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
        result = TeamController.remove_member(
            team_id=team_id,
            member_to_remove_id=user_id,
            actor_id=g.user.id,
            is_admin=is_admin(),
        )

        if result["success"]:
            logger.info(
                "Team member removed",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "team_id": team_id,
                        "removed_user_id": user_id,
                        "is_admin": is_admin(),
                    }
                },
            )
            return success_response(result)
        else:
            status_code = 403 if "not authorized" in result["error"].lower() else 400
            if status_code == 403:
                logger.warning(
                    "Unauthorized member removal attempt",
                    extra={
                        "context": {
                            "user_id": get_current_user_id(),
                            "team_id": team_id,
                            "target_user_id": user_id,
                            "error": result["error"],
                        }
                    },
                )
            return error_response(result["error"], "remove", status_code)
