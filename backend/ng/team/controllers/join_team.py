"""
Allows a user to join a team using an invite code.
"""

from ..models.Team import Team
from ..models.TeamMember import TeamMember
from ..models.enums import TeamRole
from ...user.models.User import User


def join_team(user: User, team: Team) -> None:
    TeamMember.create_team_member(
        user_id=user.id,
        team_id=team.id,
        event_id=team.event_id,
        role=TeamRole.MEMBER,
    )

