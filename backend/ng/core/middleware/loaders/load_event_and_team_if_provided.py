"""
Conditional loader for loading team_id if event_id
"""

from functools import wraps
from collections.abc import Callable
from ._util import (
    check_output_exists,
    get_model_class,
    LoaderType,
)
from ...exceptions import NotFoundError


def load_event_and_team_if_provided(
    source: LoaderType, input_key="event_id", event_output_key="event", team_output_key="team"
) -> Callable:
    """
    Load event and team if event_id is provided.
    If no event_id, sets both event=None and team=None.
    If event_id provided, loads event and finds user's team for that event.
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            check_output_exists(kwargs, event_output_key)
            check_output_exists(kwargs, team_output_key)

            current_user = kwargs.get("current_user")
            if not current_user:
                raise ValueError("User must be loaded first")

            json_data = kwargs.get("json_data", {})
            event_id = json_data.get(input_key)

            # No event_id = general ticket (no event, no team)
            if not event_id:
                kwargs[event_output_key] = None
                kwargs[team_output_key] = None
                return f(*args, **kwargs)

            Event = get_model_class("Event")
            event = Event.find_by_id(event_id)
            if not event:
                raise NotFoundError(f"Event with ID {event_id} not found")

            Team = get_model_class("Team")
            team = Team.find_by_user_and_event(user_id=current_user.id, event_id=event.id)
            if not team:
                raise NotFoundError(f"User not found in any team for event {event.id}")

            kwargs[event_output_key] = event
            kwargs[team_output_key] = team
            return f(*args, **kwargs)

        return decorated_function

    return decorator
