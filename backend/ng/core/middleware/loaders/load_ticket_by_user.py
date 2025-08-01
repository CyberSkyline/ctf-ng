from functools import wraps
from collections.abc import Callable
from ._util import check_output_exists, get_model_class
from ...exceptions import NotFoundError, PermissionError


def load_ticket_by_user(output_key="ticket") -> Callable:
    """
    Load ticket by ID and verify it belongs to the current user.
    Expects current_user to be loaded by auth middleware.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, ticket_id: int, current_user, **kwargs):
            check_output_exists(kwargs, output_key)
            Ticket = get_model_class("Ticket")

            ticket = Ticket.find_by_id(ticket_id)
            if not ticket:
                raise NotFoundError("Ticket not found")

            if ticket.author_id != current_user.id:
                raise PermissionError("You can only access your own tickets")

            kwargs[output_key] = ticket
            return f(*args, ticket_id=ticket_id, current_user=current_user, **kwargs)
        return decorated_function
    return decorator