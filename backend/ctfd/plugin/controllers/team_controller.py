# /plugin/controllers/team_controller.py

from CTFd.models import db
from datetime import datetime
import secrets
import string
import uuid
from sqlalchemy.exc import IntegrityError
from typing import Dict, Any, Optional

from .. import config
from ..utils.logger import get_logger
from ..models.enums import TeamRole

logger = get_logger(__name__)


class TeamController:
    @staticmethod
    def create_team(
        name: str,
        world_id: int,
        creator_id: int,
        limit: Optional[int] = None,
        ranked: bool = False,
    ) -> Dict[str, Any]:
        """Creates a new team in the world with the creator as captain.

        Args:
            name (str): The team name.
            world_id (int): The world ID where the team will be created.
            creator_id (int): The user ID who becomes captain.
            limit (int, optional): Max team size. Defaults to world's default_team_size.
            ranked (bool, optional): Whether the team is ranked. Defaults to False.

        Returns:
            dict: Success status, team object, invite code, and message or error info.
        """
        try:
            # Lazy import to prevent circular dependencies
            from ..models.World import World
            from ..models.Team import Team
            from ..models.User import User
            from ..models.TeamMember import TeamMember

            world = World.query.get(world_id)
            if not world:
                logger.warning(
                    "Team creation failed - world not found",
                    extra={"context": {"world_id": world_id, "team_name": name}},
                )
                return {
                    "success": False,
                    "error": f"World with ID {world_id} does not exist",
                }

            if limit is None:
                limit = world.default_team_size

            existing_team = Team.query.filter_by(name=name, world_id=world_id).first()
            if existing_team:
                logger.warning(
                    "Team creation failed - name already exists",
                    extra={
                        "context": {
                            "team_name": name,
                            "world_id": world_id,
                            "world_name": world.name,
                            "existing_team_id": existing_team.id,
                        }
                    },
                )
                return {
                    "success": False,
                    "error": f"Team '{name}' already exists in {world.name}",
                }

            existing_membership = TeamMember.query.filter_by(user_id=creator_id, world_id=world_id).first()
            if existing_membership:
                logger.warning(
                    "Team creation failed - user already in team",
                    extra={
                        "context": {
                            "user_id": creator_id,
                            "world_id": world_id,
                            "existing_team_id": existing_membership.team_id,
                        }
                    },
                )
                return {
                    "success": False,
                    "error": "You are already in a team for this world.",
                }

            invite_code = TeamController._generate_invite_code()

            team = Team(
                name=name,
                world_id=world_id,
                limit=limit,
                ranked=ranked,
                invite_code=invite_code,
            )

            db.session.add(team)
            db.session.flush()

            ng_user = User.query.get(creator_id)
            if not ng_user:
                ng_user = User(id=creator_id)
                db.session.add(ng_user)

            membership = TeamMember(
                user_id=creator_id,
                team_id=team.id,
                world_id=world_id,
                joined_at=datetime.utcnow(),
                role=TeamRole.CAPTAIN,
            )

            db.session.add(membership)
            db.session.commit()

            logger.info(
                "Team created successfully",
                extra={
                    "context": {
                        "team_id": team.id,
                        "team_name": name,
                        "world_id": world_id,
                        "world_name": world.name,
                        "creator_id": creator_id,
                        "invite_code": invite_code,
                        "team_limit": limit,
                        "ranked": ranked,
                    }
                },
            )

            return {
                "success": True,
                "team": team,
                "invite_code": invite_code,
                "message": f"Team '{name}' created successfully in {world.name}",
            }

        except IntegrityError as e:
            db.session.rollback()
            logger.error(
                "Failed to create team due to database conflict",
                extra={
                    "context": {
                        "team_name": name,
                        "world_id": world_id,
                        "creator_id": creator_id,
                        "error": str(e),
                    }
                },
            )
            return {
                "success": False,
                "error": "A team with this name already exists in this world, or there was a conflict creating the team.",
            }

    @staticmethod
    def join_team(user_id: int, team_id: int, world_id: int) -> Dict[str, Any]:
        """Adds a user to a team as a member.

        Args:
            user_id (int): The user ID joining the team.
            team_id (int): The team ID to join.
            world_id (int): The world ID containing the team.

        Returns:
            dict: Success status, team info, and membership details or error info.
        """
        try:
            # Lazy import to prevent circular dependencies
            from ..models.Team import Team
            from ..models.User import User
            from ..models.TeamMember import TeamMember

            team = Team.query.get(team_id)
            if not team:
                logger.warning(
                    "Team join failed - team not found",
                    extra={
                        "context": {
                            "team_id": team_id,
                            "user_id": user_id,
                            "world_id": world_id,
                        }
                    },
                )
                return {"success": False, "error": "Team not found."}

            if team.world_id != world_id:
                logger.warning(
                    "Team join failed - team not in specified world",
                    extra={
                        "context": {
                            "team_id": team_id,
                            "team_name": team.name,
                            "team_world_id": team.world_id,
                            "requested_world_id": world_id,
                            "user_id": user_id,
                        }
                    },
                )
                return {
                    "success": False,
                    "error": f"Team {team.name} is not in world {world_id}",
                }

            if team.is_full:
                logger.warning(
                    "Team join failed - team is full",
                    extra={
                        "context": {
                            "team_id": team_id,
                            "team_name": team.name,
                            "world_id": world_id,
                            "user_id": user_id,
                            "member_count": team.member_count,
                            "team_limit": team.limit,
                        }
                    },
                )
                return {
                    "success": False,
                    "error": f"Team {team.name} is full ({team.member_count}/{team.limit})",
                }

            user = User.query.get(user_id)
            if not user:
                user = User(id=user_id)
                db.session.add(user)
                db.session.flush()

            existing_membership = TeamMember.query.filter_by(user_id=user_id, world_id=world_id).first()
            if existing_membership:
                existing_team = Team.query.get(existing_membership.team_id)
                logger.warning(
                    "Team join failed - user already in team",
                    extra={
                        "context": {
                            "user_id": user_id,
                            "world_id": world_id,
                            "existing_team_id": existing_membership.team_id,
                            "existing_team_name": existing_team.name if existing_team else "Unknown",
                            "requested_team_id": team_id,
                            "requested_team_name": team.name,
                        }
                    },
                )
                return {
                    "success": False,
                    "error": f"User is already in team '{existing_team.name}' for this world",
                }

            role = TeamRole.MEMBER

            membership = TeamMember(
                user_id=user_id,
                team_id=team_id,
                world_id=world_id,
                joined_at=datetime.utcnow(),
                role=role,
            )

            db.session.add(membership)
            db.session.commit()

            logger.info(
                "User successfully joined team",
                extra={
                    "context": {
                        "user_id": user_id,
                        "team_id": team_id,
                        "team_name": team.name,
                        "world_id": world_id,
                        "role": role,
                    }
                },
            )

            return {
                "success": True,
                "message": f"User successfully joined team '{team.name}'",
                "team": team,
                "membership": membership,
            }

        except IntegrityError as e:
            db.session.rollback()
            logger.error(
                "Failed to join team due to database conflict",
                extra={
                    "context": {
                        "user_id": user_id,
                        "team_id": team_id,
                        "world_id": world_id,
                        "error": str(e),
                    }
                },
            )
            return {
                "success": False,
                "error": "You are already in a team for this world, or there was a conflict joining the team.",
            }

    @staticmethod
    def leave_team(user_id: int, world_id: int) -> Dict[str, Any]:
        """Removes a user from their current team in the world.

        Args:
            user_id (int): The user ID leaving the team.
            world_id (int): The world ID containing the team.

        Returns:
            dict: Success status, former team name, and message or error info.
        """
        try:
            # Lazy imports
            from ..models.Team import Team
            from ..models.TeamMember import TeamMember

            membership = TeamMember.query.filter_by(user_id=user_id, world_id=world_id).first()
            if not membership:
                logger.warning(
                    "Team leave failed - user not in any team",
                    extra={"context": {"user_id": user_id, "world_id": world_id}},
                )
                return {
                    "success": False,
                    "error": "User is not in any team for this world",
                }

            team = Team.query.get(membership.team_id)
            team_name = team.name if team else "Unknown Team"

            db.session.delete(membership)
            db.session.commit()

            logger.info(
                "User successfully left team",
                extra={
                    "context": {
                        "user_id": user_id,
                        "world_id": world_id,
                        "team_id": membership.team_id,
                        "team_name": team_name,
                    }
                },
            )

            return {
                "success": True,
                "message": f"Successfully left team '{team_name}'",
                "former_team": team_name,
            }

        except IntegrityError as e:
            db.session.rollback()
            logger.error(
                "Failed to leave team due to database constraints",
                extra={
                    "context": {
                        "user_id": user_id,
                        "world_id": world_id,
                        "error": str(e),
                    }
                },
            )
            return {
                "success": False,
                "error": "Unable to leave team due to database constraints.",
            }

    @staticmethod
    def list_teams_in_world(world_id: int) -> Dict[str, Any]:
        """Gets all teams in a world with their basic info.

        Args:
            world_id (int): The world ID to list teams from.

        Returns:
            dict: Success status, list of teams with stats, and world info.
        """
        try:
            # Lazy import
            from ..models.World import World
            from ..models.Team import Team

            world = World.query.get(world_id)
            if not world:
                return {
                    "success": False,
                    "error": f"World with ID {world_id} does not exist",
                }

            teams = Team.query.filter_by(world_id=world_id).all()

            team_list = []
            for team in teams:
                team_list.append(
                    {
                        "id": team.id,
                        "name": team.name,
                        "member_count": team.member_count,
                        "limit": team.limit,
                        "is_full": team.is_full,
                        "invite_code": team.invite_code,
                        "ranked": team.ranked,
                    }
                )

            return {
                "success": True,
                "teams": team_list,
                "world_name": world.name,
                "total_teams": len(team_list),
            }

        except IntegrityError:
            return {
                "success": False,
                "error": "Database constraint error while listing teams.",
            }

    @staticmethod
    def get_team_info(team_id: int) -> Dict[str, Any]:
        """Gets detailed info about a team.

        Args:
            team_id (int): The team ID to get info for.

        Returns:
            dict: Success status, team details, member IDs, and membership info.
        """
        try:
            # Lazy imports
            from ..models.Team import Team
            from ..models.World import World
            from ..models.TeamMember import TeamMember

            team = Team.query.get(team_id)
            if not team:
                return {"success": False, "error": "Team not found."}

            world = World.query.get(team.world_id)
            memberships = TeamMember.query.filter_by(team_id=team_id).all()
            member_ids = [m.user_id for m in memberships]

            team_data = {
                "id": team.id,
                "name": team.name,
                "world_id": team.world_id,
                "world_name": world.name if world else "Unknown",
                "member_count": team.member_count,
                "limit": team.limit,
                "is_full": team.is_full,
                "invite_code": team.invite_code,
                "ranked": team.ranked,
            }

            return {
                "success": True,
                "team": team_data,
                "member_ids": member_ids,
                "memberships": [{"user_id": m.user_id, "joined_at": m.joined_at, "role": m.role} for m in memberships],
            }

        except IntegrityError:
            return {
                "success": False,
                "error": "Database constraint error while retrieving team information.",
            }

    @staticmethod
    def join_team_by_invite_code(user_id: int, invite_code: str) -> Dict[str, Any]:
        """Lets a user join a team using its invite code.

        Args:
            user_id (int): The user ID joining the team.
            invite_code (str): The team's invite code.

        Returns:
            dict: Success status, team info, and join confirmation or error info.
        """
        try:
            # Lazy import
            from ..models.Team import Team

            team = Team.query.filter_by(invite_code=invite_code).first()
            if not team:
                return {"success": False, "error": "Invalid invite code"}

            result = TeamController.join_team(user_id, team.id, team.world_id)

            if result["success"]:
                result["joined_via_invite"] = True
                result["invite_code"] = invite_code

            return result

        except IntegrityError:
            return {
                "success": False,
                "error": "You are already in a team for this world, or there was a conflict joining the team.",
            }

    @staticmethod
    def update_team(
        team_id: int,
        actor_id: int,
        new_name: Optional[str] = None,
        is_admin: bool = False,
    ) -> Dict[str, Any]:
        """Updates team info with proper auth checks.

        Args:
            team_id (int): The team ID to update.
            actor_id (int): The user ID doing the update.
            new_name (str, optional): New team name if changing.
            is_admin (bool, optional): Whether the actor is admin. Defaults to False.

        Returns:
            dict: Success status, updated team info, and message or error info.
        """
        try:
            # Lazy imports
            from ..models.Team import Team
            from ..models.TeamMember import TeamMember

            team = Team.query.get(team_id)
            if not team:
                logger.warning(
                    "Team update failed - team not found",
                    extra={"context": {"team_id": team_id, "actor_id": actor_id}},
                )
                return {"success": False, "error": "Team not found."}

            is_captain = TeamMember.query.filter_by(team_id=team_id, user_id=actor_id, role=TeamRole.CAPTAIN).first()

            if not is_admin and not is_captain:
                logger.warning(
                    "Team update failed - unauthorized user",
                    extra={
                        "context": {
                            "team_id": team_id,
                            "team_name": team.name,
                            "actor_id": actor_id,
                            "is_admin": is_admin,
                            "is_captain": bool(is_captain),
                        }
                    },
                )
                return {
                    "success": False,
                    "error": "You are not authorized to edit this team",
                }

            changes_made = {}
            old_name = team.name

            if new_name is not None:
                if not new_name.strip():
                    return {
                        "success": False,
                        "error": "Team name cannot be empty.",
                    }

                existing_team = Team.query.filter(
                    Team.world_id == team.world_id,
                    Team.name == new_name,
                    Team.id != team_id,
                ).first()
                if existing_team:
                    logger.warning(
                        "Team update failed - name already exists",
                        extra={
                            "context": {
                                "team_id": team_id,
                                "old_name": team.name,
                                "new_name": new_name,
                                "world_id": team.world_id,
                                "existing_team_id": existing_team.id,
                                "actor_id": actor_id,
                            }
                        },
                    )
                    return {
                        "success": False,
                        "error": f"A team with the name '{new_name}' already exists in this world.",
                    }
                changes_made["name"] = {"old": old_name, "new": new_name}
                team.name = new_name

            db.session.commit()

            logger.info(
                "Team updated successfully",
                extra={
                    "context": {
                        "team_id": team_id,
                        "actor_id": actor_id,
                        "is_admin": is_admin,
                        "changes_made": changes_made,
                        "world_id": team.world_id,
                    }
                },
            )

            return {
                "success": True,
                "team": team,
                "message": "Team updated successfully",
            }

        except IntegrityError as e:
            db.session.rollback()
            logger.error(
                "Failed to update team due to database conflict",
                extra={
                    "context": {
                        "team_id": team_id,
                        "actor_id": actor_id,
                        "new_name": new_name,
                        "error": str(e),
                    }
                },
            )
            return {
                "success": False,
                "error": "A team with this name already exists in this world.",
            }

    @staticmethod
    def disband_team(team_id: int, actor_id: int, is_admin: bool = False) -> Dict[str, Any]:
        """Deletes a team and all its memberships.

        Args:
            team_id (int): The team ID to disband.
            actor_id (int): The user ID doing the action.
            is_admin (bool, optional): Whether the actor is admin. Defaults to False.

        Returns:
            dict: Success status and confirmation message or error info.
        """
        try:
            # Lazy imports
            from ..models.Team import Team
            from ..models.TeamMember import TeamMember

            team = Team.query.get(team_id)
            if not team:
                logger.warning(
                    "Team disband failed - team not found",
                    extra={"context": {"team_id": team_id, "actor_id": actor_id}},
                )
                return {"success": False, "error": "Team not found."}

            is_captain = TeamMember.query.filter_by(team_id=team_id, user_id=actor_id, role=TeamRole.CAPTAIN).first()

            if not is_admin and not is_captain:
                logger.warning(
                    "Team disband failed - unauthorized user",
                    extra={
                        "context": {
                            "team_id": team_id,
                            "team_name": team.name,
                            "actor_id": actor_id,
                            "is_admin": is_admin,
                            "is_captain": bool(is_captain),
                        }
                    },
                )
                return {
                    "success": False,
                    "error": "You are not authorized to disband this team",
                }

            team_name = team.name
            world_id = team.world_id
            member_count = team.member_count

            db.session.delete(team)
            db.session.commit()

            logger.info(
                "Team disbanded successfully",
                extra={
                    "context": {
                        "team_id": team_id,
                        "team_name": team_name,
                        "world_id": world_id,
                        "actor_id": actor_id,
                        "is_admin": is_admin,
                        "member_count": member_count,
                    }
                },
            )

            return {
                "success": True,
                "message": f"Team '{team_name}' has been disbanded.",
            }

        except IntegrityError as e:
            db.session.rollback()
            logger.error(
                "Failed to disband team due to database constraints",
                extra={
                    "context": {
                        "team_id": team_id,
                        "actor_id": actor_id,
                        "error": str(e),
                    }
                },
            )
            return {
                "success": False,
                "error": "Unable to disband team due to database constraints.",
            }

    @staticmethod
    def remove_member(team_id: int, member_to_remove_id: int, actor_id: int, is_admin: bool = False) -> Dict[str, Any]:
        """Removes a member from a team with auth checks.

        Args:
            team_id (int): The team ID.
            member_to_remove_id (int): The member ID to remove.
            actor_id (int): The user ID doing the removal.
            is_admin (bool, optional): Whether the actor is admin. Defaults to False.

        Returns:
            dict: Success status and confirmation message or error info.
        """
        try:
            # Lazy imports
            from ..models.Team import Team
            from ..models.TeamMember import TeamMember

            team = Team.query.get(team_id)
            if not team:
                return {"success": False, "error": "Team not found."}

            is_captain = TeamMember.query.filter_by(team_id=team_id, user_id=actor_id, role=TeamRole.CAPTAIN).first()

            if not is_admin and not is_captain:
                return {
                    "success": False,
                    "error": "You are not authorized to remove members",
                }

            membership_to_remove = TeamMember.query.filter_by(team_id=team_id, user_id=member_to_remove_id).first()

            if not membership_to_remove:
                return {"success": False, "error": "User is not a member of this team"}

            if membership_to_remove.user_id == actor_id:
                return {
                    "success": False,
                    "error": "Captains cannot remove themselves. Use the 'Leave Team' or 'Disband Team' feature.",
                }

            db.session.delete(membership_to_remove)
            db.session.commit()
            return {"success": True, "message": "Team member removed successfully."}

        except IntegrityError:
            db.session.rollback()
            return {
                "success": False,
                "error": "Unable to remove team member due to database constraints.",
            }

    @staticmethod
    def _generate_invite_code(length: int = config.INVITE_CODE_LENGTH) -> str:
        # Lazy imports
        from ..models.Team import Team
        from ..config import INVITE_CODE_GENERATION_ATTEMPTS

        characters = string.ascii_uppercase + string.digits
        characters = (
            characters.replace("0", "").replace("O", "").replace("1", "").replace("I", "")
        )  # Remove confusing chars like 0/O and 1/I

        for attempt in range(INVITE_CODE_GENERATION_ATTEMPTS):
            code = "".join(secrets.choice(characters) for _ in range(length))
            if not Team.query.filter_by(invite_code=code).first():
                return code

        while True:
            uuid_code = str(uuid.uuid4()).replace("-", "").upper()[:length]
            if not Team.query.filter_by(invite_code=uuid_code).first():
                return uuid_code

            length += 1
            if length > config.INVITE_CODE_MAX_LENGTH:  # Prevents runaway
                raise RuntimeError(f"Unable to generate unique invite code (tried up to {length} characters)")

    @staticmethod
    def transfer_captaincy(team_id: int, new_captain_id: int, actor_id: int, is_admin: bool = False) -> Dict[str, Any]:
        """Transfers captain role from current captain to another member.

        Args:
            team_id (int): The team ID.
            new_captain_id (int): The user ID who becomes captain.
            actor_id (int): The user ID doing the transfer.
            is_admin (bool, optional): Whether the actor is admin. Defaults to False.

        Returns:
            dict: Success status, new captain info, and message or error info.
        """
        try:
            # Lazy imports
            from ..models.Team import Team
            from ..models.TeamMember import TeamMember

            team = Team.query.get(team_id)
            if not team:
                logger.warning(
                    "Captain transfer failed - team not found",
                    extra={
                        "context": {
                            "team_id": team_id,
                            "actor_id": actor_id,
                            "new_captain_id": new_captain_id,
                        }
                    },
                )
                return {"success": False, "error": "Team not found."}

            is_current_captain = TeamMember.query.filter_by(
                team_id=team_id, user_id=actor_id, role=TeamRole.CAPTAIN
            ).first()

            if not is_admin and not is_current_captain:
                logger.warning(
                    "Captain transfer failed - unauthorized user",
                    extra={
                        "context": {
                            "team_id": team_id,
                            "team_name": team.name,
                            "actor_id": actor_id,
                            "new_captain_id": new_captain_id,
                            "is_admin": is_admin,
                            "is_current_captain": bool(is_current_captain),
                        }
                    },
                )
                return {
                    "success": False,
                    "error": "You are not authorized to assign captain",
                }

            new_captain_membership = TeamMember.query.filter_by(user_id=new_captain_id, team_id=team_id).first()
            if not new_captain_membership:
                logger.warning(
                    "Captain transfer failed - new captain not a team member",
                    extra={
                        "context": {
                            "team_id": team_id,
                            "team_name": team.name,
                            "actor_id": actor_id,
                            "new_captain_id": new_captain_id,
                        }
                    },
                )
                return {"success": False, "error": "User is not a member of this team"}

            existing_captain = TeamMember.query.filter_by(team_id=team_id, role=TeamRole.CAPTAIN).first()
            old_captain_id = existing_captain.user_id if existing_captain else None

            if existing_captain:
                existing_captain.role = TeamRole.MEMBER

            new_captain_membership.role = TeamRole.CAPTAIN

            db.session.commit()

            logger.info(
                "Captain transferred successfully",
                extra={
                    "context": {
                        "team_id": team_id,
                        "team_name": team.name,
                        "old_captain_id": old_captain_id,
                        "new_captain_id": new_captain_id,
                        "actor_id": actor_id,
                        "is_admin": is_admin,
                    }
                },
            )

            return {
                "success": True,
                "message": f"User {new_captain_id} is now captain of '{team.name}'",
                "team_id": team.id,
                "captain_id": new_captain_id,
            }

        except IntegrityError as e:
            db.session.rollback()
            logger.error(
                "Failed to transfer captaincy due to database constraints",
                extra={
                    "context": {
                        "team_id": team_id,
                        "actor_id": actor_id,
                        "new_captain_id": new_captain_id,
                        "error": str(e),
                    }
                },
            )
            return {
                "success": False,
                "error": "Unable to transfer captaincy due to database constraints.",
            }

    @staticmethod
    def remove_captain(team_id: int) -> Dict[str, Any]:
        """Demotes the current captain to a regular member.

        Args:
            team_id (int): The team ID.

        Returns:
            dict: Success status, team info, and message or error info.
        """
        try:
            # Lazy imports
            from ..models.Team import Team
            from ..models.TeamMember import TeamMember

            team = Team.query.get(team_id)
            if not team:
                return {"success": False, "error": "Team not found."}

            captain = TeamMember.query.filter_by(team_id=team_id, role=TeamRole.CAPTAIN).first()
            if not captain:
                return {"success": False, "error": "Team has no captain"}

            captain.role = TeamRole.MEMBER
            db.session.commit()

            return {
                "success": True,
                "message": f"Captain removed from '{team.name}'",
                "team": team,
            }

        except IntegrityError:
            db.session.rollback()
            return {
                "success": False,
                "error": "Unable to remove captain due to database constraints.",
            }

    @staticmethod
    def get_team_captain(team_id: int) -> Dict[str, Any]:
        """Gets the current captain info for a team.

        Args:
            team_id (int): The team ID.

        Returns:
            dict: Success status, captain ID if exists, and captain status info.
        """
        try:
            # Lazy imports
            from ..models.TeamMember import TeamMember

            captain = TeamMember.query.filter_by(team_id=team_id, role=TeamRole.CAPTAIN).first()

            if captain:
                return {
                    "success": True,
                    "captain_id": captain.user_id,
                    "has_captain": True,
                }
            else:
                return {"success": True, "captain_id": None, "has_captain": False}

        except IntegrityError:
            return {
                "success": False,
                "error": "Database constraint error while retrieving captain information.",
            }
