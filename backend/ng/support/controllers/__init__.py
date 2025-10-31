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
    upload_ticket_attachment,
    download_attachment,
)
from .admin_actions import (
    create_tag,
    update_tag,
    list_tags,
    set_ticket_tags,
    assign_ticket,
    unassign_ticket,
    update_ticket_status,
    update_ticket_mute,
    set_ticket_event,
    remove_ticket_event,
    set_ticket_challenge,
    remove_ticket_challenge,
)

__all__ = [
    # User actions
    "create_ticket",
    "close_my_ticket",
    # Shared actions
    "create_ticket_message",
    "get_ticket",
    "list_tickets",
    "upload_ticket_attachment",
    "download_attachment",
    # Admin actions
    "create_tag",
    "update_tag",
    "list_tags",
    "set_ticket_tags",
    "assign_ticket",
    "unassign_ticket",
    "update_ticket_status",
    "update_ticket_mute",
    "set_ticket_event",
    "remove_ticket_event",
    "set_ticket_challenge",
    "remove_ticket_challenge",
]
