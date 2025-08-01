"""
Creates a new ticket tag (admin only).
"""

from ...models.TicketTag import TicketTag


def create_tag(
    name: str,
    color: str | None = None,
    description: str | None = None,
) -> TicketTag:
    """
    Create a new ticket tag
    """
    tag = TicketTag.create_tag(
        name=name,
        color=color,
        description=description,
        commit=True,
    )

    return tag
