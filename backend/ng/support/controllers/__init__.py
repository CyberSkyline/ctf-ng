"""
Support controllers combined package
"""

from .user_actions import (
    create_ticket,
    close_my_ticket,
)
from .all_actions import (
    create_ticket_message,
    get_ticket,
    list_tickets,
)
from .admin_actions import (
    create_tag,
    update_tag,
    list_tags,
    set_ticket_tags,
    update_ticket_assignment,
    update_ticket_status,
    update_ticket_mute,
    update_ticket_event,
    update_ticket_challenge,
)

__all__ = [
    # User actions
    "create_ticket",
    "close_my_ticket",
    # Shared actions
    "create_ticket_message",
    "get_ticket",
    "list_tickets",
    # Admin actions
    "create_tag",
    "update_tag",
    "list_tags",
    "set_ticket_tags",
    "update_ticket_assignment",
    "update_ticket_status",
    "update_ticket_mute",
    "update_ticket_event",
    "update_ticket_challenge",
]
