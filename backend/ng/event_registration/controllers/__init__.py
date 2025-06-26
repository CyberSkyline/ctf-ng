"""
/backend/ctfd/plugin/event_registration/controllers/__init__.py
Event Registration controllers package.
"""
from .join_event_existing_team import join_event_existing_team
from .join_event_new_team import join_event_new_team
from .get_user_demographic import get_user_demographic
from .create_event_registration import create_event_registration


__all__ = [
    "create_event_registration",
    "join_event_existing_team",
    "join_event_new_team",
    "get_user_demographic",
]
