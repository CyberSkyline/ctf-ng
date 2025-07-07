"""
Admin-only support ticket operations.
"""

from .assign_ticket import assign_ticket
from .unassign_ticket import unassign_ticket
from .close_ticket import close_ticket
from .reopen_ticket import reopen_ticket
from .get_ticket_statistics import get_ticket_statistics
from ..all_actions.list_tickets import list_tickets

from .tag_management import (
    create_tag,
    update_tag,
    delete_tag,
    list_tags,
    add_tags_to_ticket,
    remove_tags_from_ticket,
)

__all__ = [
    "assign_ticket",
    "unassign_ticket",
    "close_ticket",
    "reopen_ticket",
    "get_ticket_statistics",
    "assign_ticket",
    "unassign_ticket",
    "close_ticket",
    "reopen_ticket",
    "get_ticket_statistics",
    "create_tag",
    "update_tag",
    "delete_tag",
    "list_tags",
    "add_tags_to_ticket",
    "remove_tags_from_ticket",
    "list_tickets",
]
