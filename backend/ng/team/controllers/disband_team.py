"""
Disbands a team and removes all its members.
"""

from flask import g

def disband_team(team_id: int, actor_id: int, is_admin: bool = False) -> None:
    """Deletes a team and all its team members.

    Returns:
        dict: Confirmation message.
    """
    team = g.team

    team.disband_team()

