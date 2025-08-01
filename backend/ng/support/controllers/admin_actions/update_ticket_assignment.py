"""
Updates ticket assignment (admin only).
"""

from ...models.Ticket import Ticket


def update_ticket_assignment(
    ticket_id: int,
    user_id: int | None,
    ticket=None,
) -> Ticket:
    """
    Assign or unassign a ticket
    """
    if user_id is None:
        ticket.unassign(commit=True)
    else:
        ticket.assign_to_user(user_id=user_id, commit=True)

    return ticket
