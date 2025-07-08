"""
Disbands a team and removes all its members.
"""

from ..models.Team import Team

def disband_team(team: Team) -> None:
    """Deletes a team and all its team members.

    """
    team.disband_team()

