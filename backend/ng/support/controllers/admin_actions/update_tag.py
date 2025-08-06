"""
Updates an existing ticket tag (admin only).
"""

from ...models.TicketTag import TicketTag


def update_tag(
    tag: TicketTag,
    name: str | None = None,
    color: str | None = None,
    description: str | None = None,
) -> TicketTag:
    """
    Update an existing ticket tag
    """
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if color is not None:
        update_data["color"] = color
    if description is not None:
        update_data["description"] = description

    if update_data:
        tag.update_tag(commit=True, **update_data)

    return tag
