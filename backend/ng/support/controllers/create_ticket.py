"""
Creates a new support ticket.
"""

from typing import Any

from ...core.utils import emit_event
from ...core import ValidationError, NotFoundError

from ..models.Ticket import Ticket


def create_ticket(
    subject: str,
    author_id: int,
    event_id: int | None = None,
    team_id: int | None = None,
    challenge_id: int | None = None,
    tag_ids: list[int] | None = None,
) -> dict[str, Any]:
    """Creates a new support ticket."""
    result = Ticket.create_with_validation(
        subject=subject,
        author_id=author_id,
        event_id=event_id,
        team_id=team_id,
        challenge_id=challenge_id,
        tag_ids=tag_ids,
    )

    if not result["success"]:
        if "not found" in result["error"].lower():
            raise NotFoundError(result["error"])
        else:
            raise ValidationError(result["error"])

    ticket = result["ticket"]

    emit_event(
        event_name="new_ticket",
        data=ticket.serialize(include_admin_fields=True),
        room="support_staff",
    )

    return {
        "ticket": ticket,
        "ticket_created": True,
    }
