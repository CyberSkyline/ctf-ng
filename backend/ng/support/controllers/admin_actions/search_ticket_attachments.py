"""
Search ticket attachments by filename
"""

from .... import config
from ....core.exceptions import ValidationError
from ...models import TicketAttachment


def search_ticket_attachments(
    filename_query: str,
    limit: int = config.DEFAULT_ATTACHMENT_SEARCH_LIMIT,
    offset: int = 0,
) -> dict:
    """
    Search ticket attachments by filename (partial match)

    Args:
        filename_query: Search term for filename
        limit: Max results to return
        offset: Pagination offset

    Returns:
        Dict with attachments list and pagination metadata
    """
    if not filename_query or not filename_query.strip():
        raise ValidationError(
            "Search query required",
            errors = {"filename": "Filename search term is required"}
        )

    if len(filename_query.strip()) < config.MIN_SEARCH_QUERY_LENGTH:
        raise ValidationError(
            "Search query too short",
            errors = {
                "filename": f"Search term must be at least {config.MIN_SEARCH_QUERY_LENGTH} characters"
            }
        )

    limit = min(max(limit, 1), config.MAX_ATTACHMENT_SEARCH_LIMIT)

    if offset < 0:
        raise ValidationError(
            "Invalid offset",
            errors = {"offset": "Offset must be 0 or greater"}
        )

    attachments, total_count = TicketAttachment.search_by_filename(
        filename_query=filename_query.strip(),
        limit=limit,
        offset=offset
    )

    serialized_attachments = [
        attachment.serialize(
            include_admin_fields = True
        ) for attachment in attachments
    ]

    return {
        "attachments": serialized_attachments,
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "query": filename_query.strip()
    }
