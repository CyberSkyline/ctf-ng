# /plugin/controllers/database_controller.py

from CTFd.models import db
from sqlalchemy.exc import IntegrityError
from typing import Dict, Any


class DatabaseController:
    """db utilities"""

    @staticmethod
    def reset_all_plugin_data() -> Dict[str, Any]:
        """Deletes all plugin data from the database.

        Returns:
            dict: Success status and deletion counts or error info.
        """
        try:
            from ..models.TeamMember import TeamMember
            from ..models.Team import Team
            from ..models.User import User
            from ..models.World import World

            initial_counts = DatabaseController.get_data_counts()

            TeamMember.query.delete()
            Team.query.delete()
            User.query.delete()
            World.query.delete()

            db.session.commit()

            return {
                "success": True,
                "message": "All plugin data reset successfully",
                "deleted": initial_counts,
            }

        except IntegrityError:
            db.session.rollback()
            return {
                "success": False,
                "error": "Unable to reset data due to database constraints.",
            }

    @staticmethod
    def get_data_counts() -> Dict[str, Any]:
        """Gets count stats for all plugin data.

        Returns:
            dict: Counts of worlds, teams, users, and memberships.
        """
        try:
            from ..models.World import World
            from ..models.Team import Team
            from ..models.User import User
            from ..models.TeamMember import TeamMember

            return {
                "worlds": World.query.count(),
                "teams": Team.query.count(),
                "users": User.query.count(),
                "memberships": TeamMember.query.count(),
            }
        except IntegrityError:
            return {"error": "Database constraint error while retrieving data counts."}

    @staticmethod
    def get_detailed_stats() -> Dict[str, Any]:
        """Gets detailed stats including per world breakdowns and empty teams.

        Returns:
            dict: Detailed stats with world data and potential issues.
        """
        try:
            from ..models.World import World
            from ..models.Team import Team
            from ..models.TeamMember import TeamMember

            worlds = World.query.all()
            world_stats = []

            for world in worlds:
                teams_in_world = Team.query.filter_by(world_id=world.id).count()
                members_in_world = TeamMember.query.filter_by(world_id=world.id).count()

                world_stats.append(
                    {
                        "id": world.id,
                        "name": world.name,
                        "teams": teams_in_world,
                        "total_members": members_in_world,
                    }
                )

            all_teams = Team.query.all()
            empty_teams = []
            for team in all_teams:
                if team.member_count == 0:
                    empty_teams.append({"id": team.id, "name": team.name, "world_id": team.world_id})

            return {
                "success": True,
                "overview": DatabaseController.get_data_counts(),
                "worlds": world_stats,
                "empty_teams": empty_teams,
                "total_empty_teams": len(empty_teams),
            }

        except IntegrityError:
            return {
                "success": False,
                "error": "Database constraint error while retrieving detailed statistics.",
            }

    @staticmethod
    def reset_world_data(world_id: int) -> Dict[str, Any]:
        """Deletes all teams and memberships for a world.

        Args:
            world_id (int): The ID of the world to reset.

        Returns:
            dict: Success status and deletion counts or error info.
        """
        try:
            from ..models.World import World
            from ..models.Team import Team
            from ..models.TeamMember import TeamMember

            world = World.query.get(world_id)
            if not world:
                return {"success": False, "error": "World not found."}

            memberships_count = TeamMember.query.filter_by(world_id=world_id).count()
            teams_count = Team.query.filter_by(world_id=world_id).count()

            TeamMember.query.filter_by(world_id=world_id).delete()
            Team.query.filter_by(world_id=world_id).delete()

            db.session.commit()

            return {
                "success": True,
                "message": f"Reset world '{world.name}' successfully",
                "deleted": {"memberships": memberships_count, "teams": teams_count},
                "world": {"id": world.id, "name": world.name},
            }

        except IntegrityError:
            db.session.rollback()
            return {
                "success": False,
                "error": "Unable to reset world data due to database constraints.",
            }

    @staticmethod
    def cleanup_orphaned_data() -> Dict[str, Any]:
        """Removes user records that have no team memberships.

        Returns:
            dict: Success status and count of cleaned up users.
        """
        try:
            from ..models.TeamMember import TeamMember
            from ..models.User import User

            users_with_memberships = db.session.query(TeamMember.user_id).distinct().all()
            user_ids_with_memberships = [row[0] for row in users_with_memberships]

            orphaned_users = User.query.filter(~User.id.in_(user_ids_with_memberships)).all()
            orphaned_count = len(orphaned_users)

            for user in orphaned_users:
                db.session.delete(user)

            db.session.commit()

            return {
                "success": True,
                "message": "Cleanup completed successfully",
                "cleaned_up": {"orphaned_users": orphaned_count},
            }

        except IntegrityError:
            db.session.rollback()
            return {
                "success": False,
                "error": "Unable to cleanup data due to database constraints.",
            }
