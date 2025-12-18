"""
Support controllers combined package
"""

from .admin_actions import (
    assign_ticket,
    create_tag,
    list_tags,
    remove_ticket_challenge,
    remove_ticket_event,
    set_ticket_challenge,
    set_ticket_event,
    set_ticket_tags,
    unassign_ticket,
    update_tag,
    update_ticket_mute,
    update_ticket_status,
)
from .all_actions import (
    create_ticket_message,
    download_attachment,
    get_ticket,
    list_tickets,
    upload_attachment,
)
from .user_actions import (
    close_my_ticket,
    create_ticket,
)

__all__ = [
    # User actions
    "create_ticket",
    "close_my_ticket",
    # Shared actions
    "create_ticket_message",
    "get_ticket",
    "list_tickets",
    "download_attachment",
    "upload_attachment",
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
