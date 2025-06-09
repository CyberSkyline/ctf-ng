# /plugin/user/controllers/user_controller.py

from typing import Any

from sqlalchemy import func
from CTFd.models import db

from ...utils.logger import get_logger
from ...world.models.World import World
from ...team.models.Team import Team
from ...team.models.TeamMember import TeamMember
from ..models.User import User

logger = get_logger(__name__)


class UserController:
    @staticmethod
    def get_user_teams(user_id: int) -> dict[str, Any]:
        """Gets all team memberships for a user across all worlds.

        Args:
            user_id (int): The user ID to get teams for.

        Returns:
            dict: Success status, list of teams with world info, and total count.
        """

        user = User.query.get(user_id)
        if not user:
            logger.warning(
                "Get user teams failed - user not found",
                extra={"context": {"user_id": user_id}},
            )
            return {"success": False, "error": "User not found in extended system"}

        memberships_query = (
            db.session.query(
                TeamMember.joined_at,
                Team.id.label("team_id"),
                Team.name.label("team_name"),
                Team.limit.label("team_limit"),
                World.id.label("world_id"),
                World.name.label("world_name"),
            )
            .join(Team, TeamMember.team_id == Team.id)
            .join(World, TeamMember.world_id == World.id)
            .filter(TeamMember.user_id == user_id)
            .all()
        )

        teams_data = []
        for membership in memberships_query:
            teams_data.append(
                {
                    "team_id": membership.team_id,
                    "team_name": membership.team_name,
                    "world_id": membership.world_id,
                    "world_name": membership.world_name,
                    "joined_at": membership.joined_at.isoformat() if membership.joined_at else None,
                    "team_limit": membership.team_limit,
                }
            )

        if teams_data:
            team_ids = [team["team_id"] for team in teams_data]
            member_counts = dict(
                db.session.query(TeamMember.team_id, func.count(TeamMember.id))
                .filter(TeamMember.team_id.in_(team_ids))
                .group_by(TeamMember.team_id)
                .all()
            )

            for team in teams_data:
                team["team_member_count"] = member_counts.get(team["team_id"], 0)

        logger.info(
            "User teams retrieved successfully",
            extra={
                "context": {
                    "user_id": user_id,
                    "total_teams": len(teams_data),
                    "total_memberships": len(teams_data),
                }
            },
        )

        return {
            "success": True,
            "teams": teams_data,
            "total_teams": len(teams_data),
        }

    @staticmethod
    def get_user_teams_in_world(user_id: int, world_id: int) -> dict[str, Any]:
        """Gets a user's team membership in a world.

        Args:
            user_id (int): The user ID.
            world_id (int): The world ID to check.

        Returns:
            dict: Success status, team info if user is in a team, or None if not.
        """

        world = World.query.get(world_id)
        if not world:
            logger.warning(
                "Get user teams in world failed - world not found",
                extra={"context": {"user_id": user_id, "world_id": world_id}},
            )
            return {
                "success": False,
                "error": f"World with ID {world_id} does not exist",
            }

        membership = TeamMember.query.filter_by(user_id=user_id, world_id=world_id).first()

        if not membership:
            logger.info(
                "User has no team membership in world",
                extra={
                    "context": {
                        "user_id": user_id,
                        "world_id": world_id,
                        "world_name": world.name,
                    }
                },
            )
            return {"success": True, "in_team": False, "team": None}

        team = Team.query.get(membership.team_id)
        logger.info(
            "User team membership found in world",
            extra={
                "context": {
                    "user_id": user_id,
                    "world_id": world_id,
                    "world_name": world.name,
                    "team_id": team.id,
                    "team_name": team.name,
                    "role": membership.role,
                }
            },
        )
        return {
            "success": True,
            "in_team": True,
            "team": {
                "id": team.id,
                "name": team.name,
                "member_count": team.member_count,
                "limit": team.limit,
                "is_full": team.is_full,
                "ranked": team.ranked,
            },
            "membership": {
                "joined_at": membership.joined_at,
                "role": membership.role,
            },
        }

    @staticmethod
    def can_join_team_in_world(user_id: int, world_id: int) -> dict[str, Any]:
        """Checks if a user can join a team in the world.

        Args:
            user_id (int): The user ID.
            world_id (int): The world ID to check eligibility for.

        Returns:
            dict: Success status, eligibility boolean, and reason if not eligible.
        """

        existing_membership = TeamMember.query.filter_by(user_id=user_id, world_id=world_id).first()

        return {
            "success": True,
            "can_join": existing_membership is None,
            "reason": ("User already in a team for this world" if existing_membership else None),
        }

    @staticmethod
    def get_user_stats(user_id: int) -> dict[str, Any]:
        """Gets participation stats for a user across all worlds.

        Args:
            user_id (int): The user ID to get stats for.

        Returns:
            dict: Success status and participation stats.
        """

        user = User.query.get(user_id)
        if not user:
            return {"success": False, "error": "User not found in extended system"}

        memberships = TeamMember.query.filter_by(user_id=user_id).all()

        worlds_participated = set()
        for membership in memberships:
            worlds_participated.add(membership.world_id)

        total_worlds = World.query.count()

        return {
            "success": True,
            "stats": {
                "total_team_memberships": len(memberships),
                "worlds_participated": len(worlds_participated),
                "total_worlds_available": total_worlds,
                "participation_rate": (len(worlds_participated) / total_worlds if total_worlds > 0 else 0),
            },
        }
