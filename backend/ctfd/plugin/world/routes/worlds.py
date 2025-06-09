# /plugin/world/routes/worlds.py

from flask import g
from flask_restx import Namespace, Resource
from CTFd.utils.decorators import authed_only, admins_only

from ..controllers.world_controller import WorldController
from ...team.controllers.team_controller import TeamController
from ...utils.api_responses import controller_response, error_response, success_response
from ...utils.decorators import json_body_required, handle_integrity_error
from ...utils.logger import get_logger
from ...utils import get_current_user_id
from ...utils.validators import validate_world_creation, validate_world_update

worlds_namespace = Namespace("worlds", description="world management operations")
logger = get_logger(__name__)


@worlds_namespace.route("")
class WorldList(Resource):
    @authed_only
    @handle_integrity_error
    @worlds_namespace.doc(
        description="Get list of all training worlds with statistics",
        responses={
            200: "Success - Returns list of worlds with team/member counts",
            403: "Forbidden - User not authenticated",
        },
    )
    def get(self):
        """Get all training worlds with their team and member stats.

        Returns:
            JSON response with list of worlds including team counts and member counts.
        """
        result = WorldController.list_worlds()

        if result["success"]:
            logger.info(
                "Worlds list retrieved",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "world_count": len(result.get("worlds", [])),
                    }
                },
            )

        return controller_response(result, error_field="worlds")

    @admins_only
    @json_body_required
    @handle_integrity_error
    @worlds_namespace.doc(
        description="Create a new training world (Admin only)",
        params={
            "name": "World name (required)",
            "description": "World description (optional)",
        },
        responses={
            201: "Success - World created",
            400: "Bad request - Invalid data",
            403: "Forbidden - Admin access required",
        },
    )
    def post(self):
        """Create a new training world with given config.

        Request Body:
            name (str): Unique name for the world.
            description (str, optional): Description of the world's purpose.
            default_team_size (int, optional): Default max team size.

        Returns:
            JSON response with created world info or error details.
        """

        data = g.json_data

        is_valid, errors = validate_world_creation(data)
        if not is_valid:
            logger.warning(
                "Validation failed for world creation",
                extra={
                    "context": {
                        "errors": errors,
                        "admin_id": get_current_user_id(),
                        "endpoint": "world_create",
                        "data": data,
                    }
                },
            )
            return {"success": False, "errors": errors}, 400

        name = data.get("name")
        description = data.get("description")
        default_team_size = data.get("default_team_size")

        result = WorldController.create_world(name=name, description=description, default_team_size=default_team_size)

        if result["success"]:
            world_data = result["world"]
            logger.warning(
                "Admin created world",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "world_id": world_data["id"],
                        "world_name": world_data["name"],
                        "default_team_size": world_data["default_team_size"],
                    }
                },
            )
            return success_response(result, status_code=201)
        else:
            logger.warning(
                "World creation failed",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "error": result["error"],
                        "name": name,
                    }
                },
            )
            return error_response(result["error"], "world", 400)


@worlds_namespace.route("/<int:world_id>")
@worlds_namespace.param("world_id", "World ID")
class WorldDetail(Resource):
    @authed_only
    @handle_integrity_error
    @worlds_namespace.doc(
        description="Get detailed information about a specific world including teams",
        responses={
            200: "Success - World details with teams returned",
            403: "Forbidden - User not authenticated",
            404: "Not found - World does not exist",
        },
    )
    def get(self, world_id):
        """Get detailed info about a world including all teams.

        Args:
            world_id (int): The world ID to get.

        Returns:
            JSON response with world details and list of teams in the world.
        """
        result = WorldController.get_world_info(world_id)

        if result["success"]:
            teams_count = len(result.get("teams", []))
            logger.info(
                "World info retrieved",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "world_id": world_id,
                        "teams_count": teams_count,
                    }
                },
            )
            return success_response(result)
        else:
            logger.warning(
                "World not found",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "world_id": world_id,
                        "error": result["error"],
                    }
                },
            )
            return error_response(result["error"], "world", 404)

    @admins_only
    @json_body_required
    @handle_integrity_error
    @worlds_namespace.doc(
        description="Update world information (Admin only)",
        params={
            "name": "New world name (optional)",
            "description": "New world description (optional)",
        },
        responses={
            200: "Success - World updated",
            400: "Bad request - Invalid data or name conflict",
            403: "Forbidden - Admin access required",
            404: "Not found - World does not exist",
        },
    )
    def patch(self, world_id):
        """Update world info with the provided fields.

        Args:
            world_id (int): The world ID to update.

        Request Body:
            name (str, optional): New name for the world.
            description (str, optional): New description for the world.

        Returns:
            JSON response with updated world info or error details.
        """
        data = g.json_data

        is_valid, errors = validate_world_update(data)
        if not is_valid:
            logger.warning(
                "Validation failed for world update",
                extra={
                    "context": {
                        "errors": errors,
                        "admin_id": get_current_user_id(),
                        "endpoint": "world_update",
                        "world_id": world_id,
                    }
                },
            )
            return {"success": False, "errors": errors}, 400

        name = data.get("name")
        description = data.get("description")

        result = WorldController.update_world(world_id=world_id, name=name, description=description)

        if result["success"]:
            logger.warning(
                "Admin updated world",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "world_id": world_id,
                        "new_name": name,
                        "new_description": description,
                    }
                },
            )
            return success_response(result)
        else:
            logger.warning(
                "World update failed",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "world_id": world_id,
                        "error": result["error"],
                    }
                },
            )
            return error_response(result["error"], "world", 400)


@worlds_namespace.route("/<int:world_id>/teams")
@worlds_namespace.param("world_id", "World ID")
class WorldTeams(Resource):
    @authed_only
    @handle_integrity_error
    @worlds_namespace.doc(
        description="Get all teams in a specific world",
        responses={
            200: "Success - Teams in world returned",
            403: "Forbidden - User not authenticated",
            404: "Not found - World does not exist",
        },
    )
    def get(self, world_id):
        """Get all teams in the world.

        Args:
            world_id (int): The world ID to list teams from.

        Returns:
            JSON response with list of teams in the world or error details.
        """
        result = TeamController.list_teams_in_world(world_id)

        if result["success"]:
            logger.info(
                "World teams retrieved",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "world_id": world_id,
                        "team_count": len(result.get("teams", [])),
                    }
                },
            )

        return controller_response(result, error_field="world")
