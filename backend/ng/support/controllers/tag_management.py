"""
Manages the lifecycle of ticket tags and their association with tickets.
"""

from flask import g
from typing import Any

from ...core.utils import emit_event
from ...core.utils import build_conditional_update_data
from ...core.validation import validate_unique_name

from ..models.TicketTag import TicketTag


def create_tag(name: str, color: str | None = None, description: str | None = None) -> dict[str, Any]:
    """Creates a new ticket tag definition. This is an admin-only operation."""
    validate_unique_name(TicketTag, name)
    tag = TicketTag.create(name=name, color=color, description=description)

    return {
        "tag": tag,
        "tag_created": True,
    }


def update_tag(
    tag_id: int,
    name: str | None = None,
    color: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """Updates the properties of an existing tag definition."""
    tag = g.tag

    if name:
        validate_unique_name(TicketTag, name, current_object=tag)

    update_data = build_conditional_update_data(
        tag,
        name=(name, name is not None and name != tag.name),
        color=(color, color is not None and color != tag.color),
        description=(
            description,
            description is not None and description != tag.description,
        ),
    )

    if update_data:
        tag.update_tag(**update_data)

    return {"tag": tag}


def delete_tag(tag_id: int) -> dict[str, Any]:
    """Deletes a tag definition from the system."""
    tag = g.tag
    tag_name = tag.name
    ticket_count = len(tag.tickets)
    tag.delete_tag()

    return {
        "tag_deleted": True,
        "tag_name": tag_name,
        "affected_tickets_count": ticket_count,
    }


def list_tags() -> dict[str, Any]:
    """Lists all available tag definitions."""
    tags = TicketTag.get_all_tags()
    return {
        "tags": tags,
        "total": len(tags),
    }


def add_tags_to_ticket(ticket_id: int, tag_ids: list[int]) -> dict[str, Any]:
    """Adds one or more tags to a specific ticket."""
    ticket = g.ticket
    tags = g.tags
    ticket.add_tags(tags)

    emit_event(
        event_name="ticket_updated",
        data=ticket.serialize(include_admin_fields=True),
        room=f"ticket_{ticket_id}",
    )

    return {
        "ticket": ticket,
        "tags_added": len(tags),
        "operation_completed": True,
    }


def remove_tags_from_ticket(ticket_id: int, tag_ids: list[int]) -> dict[str, Any]:
    """Removes one or more tags from a specific ticket."""
    ticket = g.ticket
    tags = g.tags
    ticket.remove_tags(tags)

    emit_event(
        event_name="ticket_updated",
        data=ticket.serialize(include_admin_fields=True),
        room=f"ticket_{ticket_id}",
    )

    return {
        "ticket": ticket,
        "tags_removed": len(tags),
        "operation_completed": True,
    }
