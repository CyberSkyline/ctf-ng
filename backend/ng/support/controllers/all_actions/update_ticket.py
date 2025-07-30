"""
Updates ticket information.
"""

from flask import g
from typing import Any

from ....core.utils import (
    emit_event,
    build_conditional_update_data,
)

def update_ticket(
    ticket_id: int,
    actor_id: int,
    is_admin: bool = False,
    subject: str | None = None,
    event_id: int | None = None,
    team_id: int | None = None,
    challenge_id: int | None = None,
) -> dict[str, Any]:
    """Updates ticket properties based on user permissions."""
    ticket = g.ticket

    if is_admin:
        update_data = build_conditional_update_data(
            ticket,
            subject=(subject, subject is not None and subject != ticket.subject),
            event_id=(
                event_id if event_id != 0 else None,
                event_id is not None and event_id != ticket.event_id,
            ),
            team_id=(
                team_id if team_id != 0 else None,
                team_id is not None and team_id != ticket.team_id,
            ),
            challenge_id=(
                challenge_id if challenge_id != 0 else None,
                challenge_id is not None and challenge_id != ticket.challenge_id,
            ),
        )
    else:
        update_data = build_conditional_update_data(
            ticket, subject=(subject, subject is not None and subject != ticket.subject)
        )

    if not update_data:
        return {"ticket": ticket}

    changes = {field: {"old": getattr(ticket, field), "new": new_value} for field, new_value in update_data.items()}

    ticket.update_ticket(**update_data)

    emit_event(
        event_name="ticket_updated",
        data=ticket.serialize(include_admin_fields=True),
        room=f"ticket_{ticket_id}",
    )

    return {"ticket": ticket, "changes": changes}
