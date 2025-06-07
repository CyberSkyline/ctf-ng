# /plugin/routes/api/worlds.py

from flask import request
from flask_restx import Namespace, Resource
from CTFd.utils.decorators import authed_only, admins_only

from ...controllers.world_controller import WorldController
from ...utils.api_responses import controller_response, error_response

worlds_namespace = Namespace("worlds", description="world management operations")


@worlds_namespace.route("")
class WorldList(Resource):
    @authed_only
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

        return controller_response(result, error_field="worlds")

    @admins_only
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
        data = request.get_json()

        if not data:
            return error_response("JSON body is required", "body", 400)

        name = data.get("name")
        if not name:
            return error_response("World name is required", "name", 400)

        description = data.get("description", "")
        default_team_size = data.get("default_team_size", 4)

        try:
            default_team_size = int(default_team_size)
            if default_team_size < 1 or default_team_size > 20:
                return error_response("Team size must be between 1 and 20", "default_team_size", 400)
        except (ValueError, TypeError):
            return error_response("Team size must be a valid number", "default_team_size", 400)

        result = WorldController.create_world(name=name, description=description, default_team_size=default_team_size)

        if result["success"]:
            return {
                "success": True,
                "data": {
                    "world": {
                        "id": result["world"].id,
                        "name": result["world"].name,
                        "description": result["world"].description,
                    },
                    "message": result["message"],
                },
            }, 201
        else:
            return error_response(result["error"], "world", 400)


@worlds_namespace.route("/<int:world_id>")
@worlds_namespace.param("world_id", "World ID")
class WorldDetail(Resource):
    @authed_only
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
            from ...utils.api_responses import success_response

            return success_response(result)
        else:
            return error_response(result["error"], "world", 404)

    @admins_only
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
        data = request.get_json()

        if not data:
            return error_response("JSON body is required", "body", 400)

        name = data.get("name")
        description = data.get("description")

        if name is None and description is None:
            return error_response(
                "At least one field (name or description) must be provided",
                "fields",
                400,
            )

        result = WorldController.update_world(world_id=world_id, name=name, description=description)

        if result["success"]:
            return {
                "success": True,
                "data": {
                    "world": {
                        "id": result["world"].id,
                        "name": result["world"].name,
                        "description": result["world"].description,
                    },
                    "message": result["message"],
                },
            }, 200
        else:
            return error_response(result["error"], "world", 400)


@worlds_namespace.route("/<int:world_id>/teams")
@worlds_namespace.param("world_id", "World ID")
class WorldTeams(Resource):
    @authed_only
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

        from ...controllers.team_controller import TeamController

        result = TeamController.list_teams_in_world(world_id)

        return controller_response(result, error_field="world")
