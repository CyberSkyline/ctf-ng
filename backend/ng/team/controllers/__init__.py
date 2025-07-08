"""
Team controller functions for team lifecycle and member management.
"""

from .create_team import create_team
from .disband_team import disband_team
from .get_team_captain import get_team_captain
from .get_team_info import get_team_info
from .join_team import join_team
from .leave_team import leave_team
from .list_all_teams import list_all_teams
from .remove_member import remove_member
from .transfer_captaincy import transfer_captaincy

__all__ = [
    "create_team",
    "join_team",
    "leave_team",
    "get_team_info",
    "disband_team",
    "remove_member",
    "transfer_captaincy",
    "get_team_captain",
    "list_all_teams",
]
