"""
Sets tags on a ticket (admin only).
"""

from ...models.Ticket import Ticket


def set_ticket_tags(
    ticket_id: int,
    tag_ids: list[int],
    ticket=None,
) -> Ticket:
    """
    Set tags on a ticket
    """
    ticket.set_tags(tag_ids=tag_ids, commit=True)

    return ticket
