# /plugin/controllers/user_controller.py

from CTFd.models import db
from sqlalchemy.exc import IntegrityError
from typing import Dict, Any


class UserController:

    @staticmethod
    def get_user_teams(user_id: int) -> Dict[str, Any]:
        """Gets all team memberships for a user across all worlds.

        Args:
            user_id (int): The user ID to get teams for.

        Returns:
            dict: Success status, list of teams with world info, and total count.
        """
        try:
            from ..models.User import User
            from ..models.TeamMember import TeamMember
            from ..models.Team import Team
            from ..models.World import World

            user = User.query.get(user_id)
            if not user:
                return {"success": False, "error": "User not found in extended system"}

            memberships = TeamMember.query.filter_by(user_id=user_id).all()

            teams_data = []
            for membership in memberships:
                team = Team.query.get(membership.team_id)
                world = World.query.get(membership.world_id)

                if team and world:
                    teams_data.append(
                        {
                            "team_id": team.id,
                            "team_name": team.name,
                            "world_id": world.id,
                            "world_name": world.name,
                            "joined_at": membership.joined_at,
                            "team_member_count": team.member_count,
                            "team_limit": team.limit,
                        }
                    )

            return {
                "success": True,
                "teams": teams_data,
                "total_teams": len(teams_data),
            }

        except IntegrityError:
            return {
                "success": False,
                "error": "Database constraint error while retrieving user teams.",
            }

    @staticmethod
    def get_user_teams_in_world(user_id: int, world_id: int) -> Dict[str, Any]:
        """Gets a user's team membership in a world.

        Args:
            user_id (int): The user ID.
            world_id (int): The world ID to check.

        Returns:
            dict: Success status, team info if user is in a team, or None if not.
        """
        try:
            from ..models.World import World
            from ..models.TeamMember import TeamMember
            from ..models.Team import Team

            world = World.query.get(world_id)
            if not world:
                return {
                    "success": False,
                    "error": f"World with ID {world_id} does not exist",
                }

            membership = TeamMember.query.filter_by(user_id=user_id, world_id=world_id).first()

            if membership:
                team = Team.query.get(membership.team_id)
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
            else:
                return {"success": True, "in_team": False, "team": None}

        except IntegrityError:
            return {
                "success": False,
                "error": "Database constraint error while retrieving user teams in world.",
            }

    @staticmethod
    def can_join_team_in_world(user_id: int, world_id: int) -> Dict[str, Any]:
        """Checks if a user can join a team in the world.

        Args:
            user_id (int): The user ID.
            world_id (int): The world ID to check eligibility for.

        Returns:
            dict: Success status, eligibility boolean, and reason if not eligible.
        """
        try:
            from ..models.TeamMember import TeamMember

            existing_membership = TeamMember.query.filter_by(user_id=user_id, world_id=world_id).first()

            return {
                "success": True,
                "can_join": existing_membership is None,
                "reason": ("User already in a team for this world" if existing_membership else None),
            }

        except IntegrityError:
            return {
                "success": False,
                "error": "Database constraint error while checking join eligibility.",
            }

    @staticmethod
    def get_user_stats(user_id: int) -> Dict[str, Any]:
        """Gets participation stats for a user across all worlds.

        Args:
            user_id (int): The user ID to get stats for.

        Returns:
            dict: Success status and participation stats.
        """
        try:
            from ..models.User import User
            from ..models.TeamMember import TeamMember
            from ..models.World import World

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

        except IntegrityError:
            return {
                "success": False,
                "error": "Database constraint error while retrieving user statistics.",
            }
