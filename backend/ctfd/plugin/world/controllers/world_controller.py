# /plugin/world/controllers/world_controller.py

from typing import Any

from sqlalchemy import func
from CTFd.models import db

from ... import config
from ...utils.logger import get_logger
from ...team.models.Team import Team
from ...team.models.TeamMember import TeamMember
from ..models.World import World

logger = get_logger(__name__)


class WorldController:
    @staticmethod
    def create_world(
        name: str,
        description: str | None = None,
        default_team_size: int | None = None,
    ) -> dict[str, Any]:
        """Creates a new training world with the given config.

        Args:
            name (str): The unique name for the world.
            description (str, optional): A description of the world's purpose. Defaults to None.
            default_team_size (int, optional): Default max team size for teams in this world. Defaults to config.DEFAULT_TEAM_SIZE.

        Returns:
            dict: Success status, world object, and confirmation message or error info.
        """

        existing_world = World.query.filter_by(name=name).first()
        if existing_world:
            logger.warning(
                "World creation failed - name already exists",
                extra={
                    "context": {
                        "world_name": name,
                        "existing_world_id": existing_world.id,
                    }
                },
            )
            return {"success": False, "error": f"World '{name}' already exists"}

        if default_team_size is None:
            default_team_size = config.DEFAULT_TEAM_SIZE

        world = World(name=name, description=description, default_team_size=default_team_size)

        db.session.add(world)
        db.session.commit()

        logger.info(
            "World created successfully",
            extra={
                "context": {
                    "world_id": world.id,
                    "world_name": name,
                    "description": description,
                    "default_team_size": default_team_size,
                }
            },
        )

        return {
            "success": True,
            "world": {
                "id": world.id,
                "name": world.name,
                "description": world.description,
                "default_team_size": world.default_team_size,
            },
            "message": f"World '{name}' created successfully",
        }

    @staticmethod
    def list_worlds() -> dict[str, Any]:
        """Gets all worlds with their team and member stats.

        Returns:
            dict: Success status, list of worlds with counts, and total world count.
        """
        world_stats = (
            db.session.query(
                World.id,
                World.name,
                World.description,
                func.count(Team.id.distinct()).label("team_count"),
                func.count(TeamMember.id).label("total_members"),
            )
            .outerjoin(Team, World.id == Team.world_id)
            .outerjoin(TeamMember, World.id == TeamMember.world_id)
            .group_by(World.id, World.name, World.description)
            .all()
        )

        worlds_data = []
        for world_id, name, description, team_count, total_members in world_stats:
            worlds_data.append(
                {
                    "id": world_id,
                    "name": name,
                    "description": description,
                    "team_count": team_count,
                    "total_members": total_members,
                }
            )

        logger.info(
            "Worlds listed successfully",
            extra={"context": {"total_worlds": len(worlds_data)}},
        )

        return {
            "success": True,
            "worlds": worlds_data,
            "total_worlds": len(worlds_data),
        }

    @staticmethod
    def get_world_info(world_id: int) -> dict[str, Any]:
        """Gets detailed info about a world including all its teams.

        Args:
            world_id (int): The world ID to get info for.

        Returns:
            dict: Success status, world details, and list of teams in the world.
        """

        world = World.query.get(world_id)
        if not world:
            logger.warning(
                "Get world info failed - world not found",
                extra={"context": {"world_id": world_id}},
            )
            return {"success": False, "error": "World not found."}

        teams = Team.query.filter_by(world_id=world_id).all()
        total_members = TeamMember.query.filter_by(world_id=world_id).count()

        teams_data = []
        for team in teams:
            teams_data.append(
                {
                    "id": team.id,
                    "name": team.name,
                    "member_count": team.member_count,
                    "limit": team.limit,
                    "is_full": team.is_full,
                    "ranked": team.ranked,
                }
            )

        world_data = {
            "id": world.id,
            "name": world.name,
            "description": world.description,
            "team_count": len(teams),
            "total_members": total_members,
        }

        logger.info(
            "World info retrieved successfully",
            extra={
                "context": {
                    "world_id": world_id,
                    "world_name": world.name,
                    "team_count": len(teams),
                    "total_members": total_members,
                }
            },
        )

        return {"success": True, "world": world_data, "teams": teams_data}

    @staticmethod
    def update_world(world_id: int, name: str | None = None, description: str | None = None) -> dict[str, Any]:
        """Updates world info with the provided fields.

        Args:
            world_id (int): The world ID to update.
            name (str, optional): New name for the world if changing.
            description (str, optional): New description for the world if changing.

        Returns:
            dict: Success status, updated world object, and confirmation message or error info.
        """

        world = World.query.get(world_id)
        if not world:
            logger.warning(
                "World update failed - world not found",
                extra={"context": {"world_id": world_id}},
            )
            return {"success": False, "error": "World not found."}

        changes_made = {}
        old_name = world.name
        old_description = world.description

        if name and name != world.name:
            existing = World.query.filter_by(name=name).first()
            if existing:
                logger.warning(
                    "World update failed - name already exists",
                    extra={
                        "context": {
                            "world_id": world_id,
                            "old_name": old_name,
                            "new_name": name,
                            "existing_world_id": existing.id,
                        }
                    },
                )
                return {
                    "success": False,
                    "error": f"World name '{name}' already exists",
                }
            changes_made["name"] = {"old": old_name, "new": name}
            world.name = name

        if description is not None:
            changes_made["description"] = {
                "old": old_description,
                "new": description,
            }
            world.description = description

        db.session.commit()

        logger.info(
            "World updated successfully",
            extra={
                "context": {
                    "world_id": world_id,
                    "changes_made": changes_made,
                }
            },
        )

        return {
            "success": True,
            "world": {
                "id": world.id,
                "name": world.name,
                "description": world.description,
            },
            "message": "World updated successfully",
        }
