# /plugin/controllers/database_controller.py

from CTFd.models import db
from sqlalchemy.exc import IntegrityError
from typing import Any

from ..utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseController:
    """db utilities"""

    @staticmethod
    def reset_all_plugin_data() -> dict[str, Any]:
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

            logger.warning(
                "Initiating full plugin data reset",
                extra={"context": {"initial_counts": initial_counts}},
            )

            TeamMember.query.delete()
            Team.query.delete()
            User.query.delete()
            World.query.delete()

            db.session.commit()

            logger.info(
                "All plugin data reset successfully",
                extra={"context": {"deleted_counts": initial_counts}},
            )

            return {
                "success": True,
                "message": "All plugin data reset successfully",
                "deleted": initial_counts,
            }

        except IntegrityError as e:
            db.session.rollback()
            logger.error(
                "Failed to reset all plugin data due to database constraints",
                extra={"context": {"error": str(e)}},
            )
            return {
                "success": False,
                "error": "Unable to reset data due to database constraints.",
            }

    @staticmethod
    def get_data_counts() -> dict[str, Any]:
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
        except IntegrityError as e:
            logger.error(
                "Failed to get data counts due to database error",
                extra={"context": {"error": str(e)}},
            )
            return {"error": "Database constraint error while retrieving data counts."}

    @staticmethod
    def get_detailed_stats() -> dict[str, Any]:
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

        except IntegrityError as e:
            logger.error(
                "Failed to get detailed stats due to database error",
                extra={"context": {"error": str(e)}},
            )
            return {
                "success": False,
                "error": "Database constraint error while retrieving detailed statistics.",
            }

    @staticmethod
    def reset_world_data(world_id: int) -> dict[str, Any]:
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
                logger.warning(
                    "World reset failed - world not found",
                    extra={"context": {"world_id": world_id}},
                )
                return {"success": False, "error": "World not found."}

            memberships_count = TeamMember.query.filter_by(world_id=world_id).count()
            teams_count = Team.query.filter_by(world_id=world_id).count()

            logger.warning(
                "Initiating world data reset",
                extra={
                    "context": {
                        "world_id": world_id,
                        "world_name": world.name,
                        "teams_to_delete": teams_count,
                        "memberships_to_delete": memberships_count,
                    }
                },
            )

            TeamMember.query.filter_by(world_id=world_id).delete()
            Team.query.filter_by(world_id=world_id).delete()

            db.session.commit()

            logger.info(
                "World data reset successfully",
                extra={
                    "context": {
                        "world_id": world_id,
                        "world_name": world.name,
                        "deleted_teams": teams_count,
                        "deleted_memberships": memberships_count,
                    }
                },
            )

            return {
                "success": True,
                "message": f"Reset world '{world.name}' successfully",
                "deleted": {"memberships": memberships_count, "teams": teams_count},
                "world": {"id": world.id, "name": world.name},
            }

        except IntegrityError as e:
            db.session.rollback()
            logger.error(
                "Failed to reset world data due to database constraints",
                extra={"context": {"world_id": world_id, "error": str(e)}},
            )
            return {
                "success": False,
                "error": "Unable to reset world data due to database constraints.",
            }

    @staticmethod
    def cleanup_orphaned_data() -> dict[str, Any]:
        """Removes user records that have no team memberships."""
        try:
            from ..models.TeamMember import TeamMember
            from ..models.User import User

            orphaned_users_query = User.query.outerjoin(TeamMember, User.id == TeamMember.user_id).filter(
                TeamMember.id.is_(None)
            )

            orphaned_users = orphaned_users_query.all()
            orphaned_count = len(orphaned_users)

            if orphaned_count > 0:
                logger.info(
                    "Starting orphaned data cleanup",
                    extra={"context": {"orphaned_users_count": orphaned_count}},
                )

                orphaned_users_query.delete(synchronize_session=False)
                db.session.commit()

                logger.info(
                    "Orphaned data cleanup completed successfully",
                    extra={"context": {"cleaned_up_users": orphaned_count}},
                )
            else:
                logger.info("No orphaned data found to cleanup")

            return {
                "success": True,
                "message": "Cleanup completed successfully",
                "cleaned_up": {"orphaned_users": orphaned_count},
            }

        except IntegrityError as e:
            db.session.rollback()
            logger.error(
                "Failed to cleanup orphaned data due to database constraints",
                extra={"context": {"error": str(e)}},
            )
            return {
                "success": False,
                "error": "Unable to cleanup data due to database constraints.",
            }
