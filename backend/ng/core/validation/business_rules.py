"""
Reusable validators for common resource validation patterns.
"""

from typing import Any
from ..exceptions import ConflictError, BusinessLogicError

# General
def validate_unique_name(
    model_class: type,
    new_name: str,
    current_object: object | None = None,
    scope_field: str | None = None,
    scope_value: Any | None = None,
    error_message: str | None = None,
) -> None:
    """Validates that a name is unique within a given scope."""
    if current_object and new_name == getattr(current_object, "name", None):
        return
    query = model_class.query.filter_by(name=new_name)
    if scope_field and scope_value is not None:
        query = query.filter(getattr(model_class, scope_field) == scope_value)
    if current_object:
        query = query.filter(model_class.id != current_object.id)
    existing = query.first()
    if existing:
        if not error_message:
            scope_text = f" in this {scope_field.replace('_id', '')}" if scope_field else ""
            error_message = f"Name '{new_name}' already exists{scope_text}"
        raise ConflictError(error_message)


# Support
def validate_ticket_reply_allowed(ticket, is_admin: bool) -> None:
    """Check if replies are allowed on this ticket"""
    if ticket.status == "closed" and not is_admin:
        raise BusinessLogicError("Cannot reply to a closed ticket")
