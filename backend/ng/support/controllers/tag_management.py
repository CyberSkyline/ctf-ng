"""
/backend/ng/support/controllers/tag_management.py
Manages ticket tags (admin only).
"""

from typing import Any, Optional

from ...core.utils.logger import get_logger
from ..models.TicketTag import TicketTag
from ..models.Ticket import Ticket
from ..exceptions import TagNotFoundError, TicketValidationError, TicketNotFoundError

logger = get_logger(__name__)


def create_tag(
    name: str,
    color: Optional[str] = None,
    description: Optional[str] = None
) -> dict[str, Any]:
    """Creates a new ticket tag.
    
    Args:
        name: Tag name
        color: Optional hex color code
        description: Optional tag description
        
    Returns:
        dict: Success status and created tag data
        
    Raises:
        TicketValidationError: If tag name already exists
    """
    # Check if tag name already exists TODO
    existing = TicketTag.find_by_name(name)
    if existing:
        raise TicketValidationError(f"Tag with name '{name}' already exists")
    
    tag = TicketTag.create(
        name=name,
        color=color,
        description=description
    )
    
    logger.info(
        "Ticket tag created",
        extra={
            "context": {
                "tag_id": tag.id,
                "tag_name": name
            }
        }
    )
    
    return {
        "success": True,
        "tag": tag.serialize(),
        "message": f"Tag '{name}' created successfully"
    }


def update_tag(
    tag_id: int,
    name: Optional[str] = None,
    color: Optional[str] = None,
    description: Optional[str] = None
) -> dict[str, Any]:
    """Updates an existing tag.
    
    Args:
        tag_id: Tag to update
        name: New tag name
        color: New color
        description: New description
        
    Returns:
        dict: Success status and updated tag data
        
    Raises:
        TagNotFoundError: If tag doesn't exist
        TicketValidationError: If new name already exists
    """
    tag = TicketTag.find_by_id(tag_id)
    if not tag:
        raise TagNotFoundError(f"Tag with ID {tag_id} not found")
    
    # Check name uniqueness if changing TODO
    if name and name != tag.name:
        existing = TicketTag.find_by_name(name)
        if existing:
            raise TicketValidationError(f"Tag with name '{name}' already exists")
    
    # Track changes
    changes = {}
    if name and name != tag.name:
        changes["name"] = {"old": tag.name, "new": name}
    if color is not None and color != tag.color:
        changes["color"] = {"old": tag.color, "new": color}
    if description is not None and description != tag.description:
        changes["description"] = {"old": tag.description, "new": description}
    
    # Apply updates
    update_data = {}
    if name:
        update_data["name"] = name
    if color is not None:
        update_data["color"] = color
    if description is not None:
        update_data["description"] = description
    
    if update_data:
        tag.update_tag(**update_data)
        
        logger.info(
            "Ticket tag updated",
            extra={
                "context": {
                    "tag_id": tag_id,
                    "changes": changes
                }
            }
        )
    
    return {
        "success": True,
        "tag": tag.serialize(),
        "changes": changes
    }


def delete_tag(tag_id: int) -> dict[str, Any]:
    """Deletes a tag.
    
    Args:
        tag_id: Tag to delete
        
    Returns:
        dict: Success status
        
    Raises:
        TagNotFoundError: If tag doesn't exist
    """
    tag = TicketTag.find_by_id(tag_id)
    if not tag:
        raise TagNotFoundError(f"Tag with ID {tag_id} not found")
    
    tag_name = tag.name
    ticket_count = len(tag.tickets)
    
    tag.delete_tag()
    
    logger.info(
        "Ticket tag deleted",
        extra={
            "context": {
                "tag_id": tag_id,
                "tag_name": tag_name,
                "affected_tickets": ticket_count
            }
        }
    )
    
    return {
        "success": True,
        "message": f"Tag '{tag_name}' deleted successfully",
        "affected_tickets": ticket_count
    }


def list_tags() -> dict[str, Any]:
    """Lists all available tags.
    
    Returns:
        dict: Success status and list of tags
    """
    tags = TicketTag.get_all_tags()
    
    return {
        "success": True,
        "tags": [tag.serialize() for tag in tags],
        "total": len(tags)
    }


def add_tags_to_ticket(ticket_id: int, tag_ids: list[int]) -> dict[str, Any]:
    """Adds tags to a ticket.
    
    Args:
        ticket_id: Ticket to add tags to
        tag_ids: List of tag IDs to add
        
    Returns:
        dict: Success status and updated ticket
        
    Raises:
        TicketNotFoundError: If ticket doesn't exist
        TagNotFoundError: If any tag doesn't exist
    """
    ticket = Ticket.find_by_id(ticket_id)
    if not ticket:
        raise TicketNotFoundError(f"Ticket with ID {ticket_id} not found")
    
    # Validate all tags exist TODO
    tags = []
    for tag_id in tag_ids:
        tag = TicketTag.find_by_id(tag_id)
        if not tag:
            raise TagNotFoundError(f"Tag with ID {tag_id} not found")
        tags.append(tag)
    
    # Add tags
    ticket.add_tags(tags)
    
    return {
        "success": True,
        "ticket": ticket.serialize(include_admin_fields=True),
        "message": f"Added {len(tags)} tags to ticket"
    }


def remove_tags_from_ticket(ticket_id: int, tag_ids: list[int]) -> dict[str, Any]:
    """Removes tags from a ticket.
    
    Args:
        ticket_id: Ticket to remove tags from
        tag_ids: List of tag IDs to remove
        
    Returns:
        dict: Success status and updated ticket
        
    Raises:
        TicketNotFoundError: If ticket doesn't exist
        TagNotFoundError: If any tag doesn't exist
    """
    ticket = Ticket.find_by_id(ticket_id)
    if not ticket:
        raise TicketNotFoundError(f"Ticket with ID {ticket_id} not found")
    
    # Validate all tags exist TODO
    tags = []
    for tag_id in tag_ids:
        tag = TicketTag.find_by_id(tag_id)
        if not tag:
            raise TagNotFoundError(f"Tag with ID {tag_id} not found")
        tags.append(tag)
    
    # Remove tags
    ticket.remove_tags(tags)
    
    return {
        "success": True,
        "ticket": ticket.serialize(include_admin_fields=True),
        "message": f"Removed {len(tags)} tags from ticket"
    }
