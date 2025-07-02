"""
Support controller functions for ticket management and support operations.
"""

from .create_ticket import create_ticket
from .list_tickets import list_tickets
from .get_ticket import get_ticket
from .create_ticket_message import create_ticket_message
from .update_ticket import update_ticket

from .admin import (
    assign_ticket,
    unassign_ticket,
    close_ticket,
    reopen_ticket,
    mute_ticket,
    unmute_ticket,
    get_ticket_statistics,
)
from .tag_management import (
    create_tag,
    update_tag,
    delete_tag,
    list_tags,
    add_tags_to_ticket,
    remove_tags_from_ticket,
)

__all__ = [
    "create_ticket",
    "list_tickets",
    "get_ticket",
    "create_ticket_message",
    "update_ticket",
    "assign_ticket",
    "unassign_ticket",
    "close_ticket",
    "reopen_ticket",
    "mute_ticket",
    "unmute_ticket",
    "get_ticket_statistics",
    "create_tag",
    "update_tag",
    "delete_tag",
    "list_tags",
    "add_tags_to_ticket",
    "remove_tags_from_ticket",
]
