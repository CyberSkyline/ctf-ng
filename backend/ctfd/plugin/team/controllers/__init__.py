"""
/backend/ctfd/plugin/team/controllers/__init__.py
Team controller functions for team lifecycle and member management.
"""

from .create_team import create_team
from .join_team import join_team
from .leave_team import leave_team
from .list_teams_in_event import list_teams_in_event
from .get_team_info import get_team_info
from .update_team import update_team
from .disband_team import disband_team
from .remove_member import remove_member
from .transfer_captaincy import transfer_captaincy
from .get_team_captain import get_team_captain
from ._generate_invite_code import _generate_invite_code

__all__ = [
    "create_team",
    "join_team",
    "leave_team",
    "list_teams_in_event",
    "get_team_info",
    "update_team",
    "disband_team",
    "remove_member",
    "transfer_captaincy",
    "get_team_captain",
    "_generate_invite_code",
]
