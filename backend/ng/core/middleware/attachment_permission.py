"""
Attachment-specific permission middleware for checking access via parent entities
"""

from functools import wraps

from ...permissions.controllers.get_user_permissions import get_user_permissions
from ...permissions.models.enums import PermissionCheck, PermissionEnum
from ..exceptions import NotFoundError, PermissionError

SUPPORT_MANAGEMENT_PERMISSION = PermissionEnum.CAN_MANAGE_SUPPORT_TICKETS

def has_support_management_permission(user):
    trace = PermissionCheck()
    trace.merge(get_user_permissions(user))

    permissions = list({grant.permission.name for grant in trace.granted})

    return SUPPORT_MANAGEMENT_PERMISSION.name in permissions


def check_attachment_ownership(attachment_key: str = "attachment", error_message: str = None):
    """
    Decorator to check that the current user owns the ticket associated with an attachment.

    Args:
        attachment_key: The key in kwargs where the attachment object is stored
        error_message: Optional custom error message for permission violations
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            attachment = kwargs.get(attachment_key)
            if not attachment:
                raise ValueError(f"Attachment '{attachment_key}' must be loaded first")

            current_user = kwargs.get("current_user")
            if not current_user:
                raise ValueError("current_user must be loaded first")

            ticket = attachment.ticket
            if not ticket:
                raise NotFoundError("Associated ticket not found for this attachment")

            # You must be the author or have support ticket permissions
            if ticket.author_id != current_user.id and not has_support_management_permission(current_user):
                message = error_message or "You can only access attachments from your own tickets"
                raise PermissionError(message)

            kwargs["ticket"] = ticket

            return f(*args, **kwargs)

        return decorated_function

    return decorator
