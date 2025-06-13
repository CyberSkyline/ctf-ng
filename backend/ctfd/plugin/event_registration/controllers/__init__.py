"""
/backend/ctfd/plugin/event_registration/controllers/__init__.py
Event Registration controllers package.
"""
from .join_event_existing_team import join_event_existing_team
from .join_event_new_team import join_event_new_team
from .get_user_demographic import get_user_demographic


__all__ = [
    "join_event_existing_team",
    "join_event_new_team",
    "get_user_demographic",
]
