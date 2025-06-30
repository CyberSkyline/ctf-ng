"""
Admin only operations for support tickets.
"""

from flask import g
from typing import Any

from ...core import ValidationError
from ...core.utils import emit_event

from ..models.Ticket import Ticket


def assign_ticket(ticket_id: int, user_id: int, admin_id: int) -> dict[str, Any]:
    """Assigns a ticket to a support user."""
    ticket = g.ticket

    result = ticket.assign_to_user_with_validation(user_id)
    if not result["success"]:
        raise ValidationError(result["error"])

    emit_event(
        event_name="ticket_updated",
        data=ticket.serialize(include_admin_fields=True),
        room=f"ticket_{ticket_id}",
    )

    return {
        "ticket": ticket,
        "message": f"Ticket assigned to {result['user_name']}",
    }


def unassign_ticket(ticket_id: int, admin_id: int) -> dict[str, Any]:
    """Removes the assignment from a ticket."""
    ticket = g.ticket
    ticket.unassign()

    emit_event(
        event_name="ticket_updated",
        data=ticket.serialize(include_admin_fields=True),
        room=f"ticket_{ticket_id}",
    )

    return {
        "ticket": ticket,
        "message": "Ticket assignment removed",
    }


def close_ticket(ticket_id: int, admin_id: int) -> dict[str, Any]:
    """Changes a ticket's status to 'closed'."""
    ticket = g.ticket

    if ticket.status == "closed":
        raise ValidationError("Ticket is already closed")

    ticket.close_ticket()

    emit_event(
        event_name="ticket_updated",
        data=ticket.serialize(include_admin_fields=True),
        room=f"ticket_{ticket_id}",
    )

    return {
        "ticket": ticket,
        "message": "Ticket closed successfully",
    }


def reopen_ticket(ticket_id: int, admin_id: int) -> dict[str, Any]:
    """Reopens a previously closed ticket."""
    ticket = g.ticket

    if ticket.status != "closed":
        raise ValidationError("Ticket is not closed")

    ticket.reopen_ticket()

    emit_event(
        event_name="ticket_updated",
        data=ticket.serialize(include_admin_fields=True),
        room=f"ticket_{ticket_id}",
    )

    return {"ticket": ticket, "message": "Ticket reopened successfully"}


def mute_ticket(ticket_id: int, admin_id: int) -> dict[str, Any]:
    """Changes a ticket's status to 'muted'."""
    ticket = g.ticket

    if ticket.muted:
        raise ValidationError("Ticket is already muted")

    ticket.mute_ticket()

    emit_event(
        event_name="ticket_updated",
        data=ticket.serialize(include_admin_fields=True),
        room=f"ticket_{ticket_id}",
    )

    return {
        "ticket": ticket,
        "message": "Ticket muted successfully",
    }


def unmute_ticket(ticket_id: int, admin_id: int) -> dict[str, Any]:
    """Removes the 'muted' status from a ticket."""
    ticket = g.ticket

    if not ticket.muted:
        raise ValidationError("Ticket is not muted")

    ticket.unmute_ticket()

    emit_event(
        event_name="ticket_updated",
        data=ticket.serialize(include_admin_fields=True),
        room=f"ticket_{ticket_id}",
    )

    return {
        "ticket": ticket,
        "message": "Ticket unmuted successfully",
    }


def get_ticket_statistics() -> dict[str, Any]:
    """Gets overall ticket statistics for the admin dashboard."""
    stats = Ticket.get_ticket_stats()
    return {"statistics": stats}
