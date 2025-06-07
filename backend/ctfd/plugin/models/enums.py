"""
# /plugin/models/enums.py
Enumerations to ensure type safety and prevent magic string bugs
"""

import enum


class TeamRole(str, enum.Enum):
    """Enumeration of valid team member roles.
    Using an enum prevents typos and provides a single source of truth for role values.
    """

    CAPTAIN = "captain"
    MEMBER = "member"
