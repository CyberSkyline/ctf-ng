# /plugin/controllers/world_controller.py

from CTFd.models import db
from sqlalchemy.exc import IntegrityError
from typing import Dict, Any, Optional


class WorldController:
    @staticmethod
    def create_world(name: str, description: Optional[str] = None, default_team_size: int = 4) -> Dict[str, Any]:
        """Creates a new training world with the given config.

        Args:
            name (str): The unique name for the world.
            description (str, optional): A description of the world's purpose. Defaults to None.
            default_team_size (int, optional): Default max team size for teams in this world. Defaults to 4.

        Returns:
            dict: Success status, world object, and confirmation message or error info.
        """
        try:
            from ..models.World import World

            existing_world = World.query.filter_by(name=name).first()
            if existing_world:
                return {"success": False, "error": f"World '{name}' already exists"}

            world = World(name=name, description=description, default_team_size=default_team_size)

            db.session.add(world)
            db.session.commit()

            return {
                "success": True,
                "world": world,
                "message": f"World '{name}' created successfully",
            }

        except IntegrityError:
            db.session.rollback()
            return {"success": False, "error": "A world with this name already exists."}

    @staticmethod
    def list_worlds() -> Dict[str, Any]:
        """Gets all worlds with their team and member stats.

        Returns:
            dict: Success status, list of worlds with counts, and total world count.
        """
        try:
            from ..models.World import World
            from ..models.Team import Team
            from ..models.TeamMember import TeamMember

            worlds = World.query.all()

            worlds_data = []
            for world in worlds:
                team_count = Team.query.filter_by(world_id=world.id).count()
                member_count = TeamMember.query.filter_by(world_id=world.id).count()

                worlds_data.append(
                    {
                        "id": world.id,
                        "name": world.name,
                        "description": world.description,
                        "team_count": team_count,
                        "total_members": member_count,
                    }
                )

            return {
                "success": True,
                "worlds": worlds_data,
                "total_worlds": len(worlds_data),
            }

        except IntegrityError:
            return {
                "success": False,
                "error": "Database constraint error while listing worlds.",
            }

    @staticmethod
    def get_world_info(world_id: int) -> Dict[str, Any]:
        """Gets detailed info about a world including all its teams.

        Args:
            world_id (int): The world ID to get info for.

        Returns:
            dict: Success status, world details, and list of teams in the world.
        """
        try:
            from ..models.World import World
            from ..models.Team import Team
            from ..models.TeamMember import TeamMember

            world = World.query.get(world_id)
            if not world:
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

            return {"success": True, "world": world_data, "teams": teams_data}

        except IntegrityError:
            return {
                "success": False,
                "error": "Database constraint error while retrieving world information.",
            }

    @staticmethod
    def update_world(world_id: int, name: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
        """Updates world info with the provided fields.

        Args:
            world_id (int): The world ID to update.
            name (str, optional): New name for the world if changing.
            description (str, optional): New description for the world if changing.

        Returns:
            dict: Success status, updated world object, and confirmation message or error info.
        """
        try:
            from ..models.World import World

            world = World.query.get(world_id)
            if not world:
                return {"success": False, "error": "World not found."}

            if name and name != world.name:
                existing = World.query.filter_by(name=name).first()
                if existing:
                    return {
                        "success": False,
                        "error": f"World name '{name}' already exists",
                    }
                world.name = name

            if description is not None:
                world.description = description

            db.session.commit()

            return {
                "success": True,
                "world": world,
                "message": "World updated successfully",
            }

        except IntegrityError:
            db.session.rollback()
            return {"success": False, "error": "A world with this name already exists."}
