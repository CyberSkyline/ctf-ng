"""
/backend/ctfd/plugin/event/routes/events.py
Defines the public API routes for creating, listing, viewing, and updating events.
"""

from flask import g
from flask_restx import Namespace, Resource
from CTFd.utils.decorators import authed_only, admins_only

from ..controllers import create_event, list_events, get_event_info, update_event
from ...team.controllers import list_teams_in_event
from ...utils.api_responses import controller_response, error_response, success_response
from ...utils.decorators import json_body_required, handle_integrity_error
from ...utils.logger import get_logger
from ...utils import get_current_user_id
from ...utils import validate_event_creation, validate_event_update

events_namespace = Namespace("events", description="event management operations")
logger = get_logger(__name__)


@events_namespace.route("")
class EventList(Resource):
    @authed_only
    @handle_integrity_error
    @events_namespace.doc(
        description="Get list of all training events with statistics",
        responses={
            200: "Success - Returns list of events with team/member counts",
            403: "Forbidden - User not authenticated",
            500: "Internal Server Error",
        },
    )
    def get(self):
        """Get all training events with their team and member stats.

        Returns:
            JSON response with list of events including team counts and member counts.
        """
        result = list_events()

        if result["success"]:
            logger.info(
                "Events list retrieved",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "event_count": len(result.get("events", [])),
                    }
                },
            )

        return controller_response(result, error_field="events")

    @admins_only
    @json_body_required
    @handle_integrity_error
    @events_namespace.doc(
        description="Create a new training event (Admin only)",
        params={
            "name": "Event name (required)",
            "description": "Event description (optional)",
        },
        responses={
            201: "Success - Event created",
            400: "Bad request - Invalid data",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error",
        },
    )
    def post(self):
        """Create a new training event with given config.

        Request Body:
            name (str): Unique name for the event.
            description (str, optional): Description of the event's purpose.
            max_team_size (int, optional): Maximum team size.

        Returns:
            JSON response with created event info or error details.
        """

        data = g.json_data

        is_valid, errors = validate_event_creation(data)
        if not is_valid:
            logger.warning(
                "Validation failed for event creation",
                extra={
                    "context": {
                        "errors": errors,
                        "admin_id": get_current_user_id(),
                        "endpoint": "event_create",
                        "data": data,
                    }
                },
            )
            return {"success": False, "errors": errors}, 400

        name = data.get("name")
        description = data.get("description")
        max_team_size = data.get("max_team_size")
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        locked = data.get("locked", False)

        result = create_event(
            name=name,
            description=description,
            max_team_size=max_team_size,
            start_time=start_time,
            end_time=end_time,
            locked=locked,
        )

        if result["success"]:
            event_data = result["event"]
            logger.warning(
                "Admin created event",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "event_id": event_data["id"],
                        "event_name": event_data["name"],
                        "max_team_size": event_data["max_team_size"],
                    }
                },
            )
            return success_response(result, status_code=201)
        else:
            logger.warning(
                "Event creation failed",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "error": result["error"],
                        "name": name,
                    }
                },
            )
            return error_response(result["error"], "event", 400)


@events_namespace.route("/<int:event_id>")
@events_namespace.param("event_id", "Event ID")
class EventDetail(Resource):
    @authed_only
    @handle_integrity_error
    @events_namespace.doc(
        description="Get detailed information about a specific event including teams",
        responses={
            200: "Success - Event details with teams returned",
            403: "Forbidden - User not authenticated",
            404: "Not found - Event does not exist",
            500: "Internal Server Error",
        },
    )
    def get(self, event_id):
        """Get detailed info about a event including all teams.

        Args:
            event_id (int): The event ID to get.

        Returns:
            JSON response with event details and list of teams in the event.
        """
        result = get_event_info(event_id)

        if result["success"]:
            teams_count = len(result.get("teams", []))
            logger.info(
                "Event info retrieved",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "event_id": event_id,
                        "teams_count": teams_count,
                    }
                },
            )
            return success_response(result)
        else:
            logger.warning(
                "Event not found",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "event_id": event_id,
                        "error": result["error"],
                    }
                },
            )
            return error_response(result["error"], "event", 404)

    @admins_only
    @json_body_required
    @handle_integrity_error
    @events_namespace.doc(
        description="Update event information (Admin only)",
        params={
            "name": "New event name (optional)",
            "description": "New event description (optional)",
        },
        responses={
            200: "Success - Event updated",
            400: "Bad request - Invalid data or name conflict",
            403: "Forbidden - Admin access required",
            404: "Not found - Event does not exist",
            500: "Internal Server Error",
        },
    )
    def patch(self, event_id):
        """Update event info with the provided fields.

        Args:
            event_id (int): The event ID to update.

        Request Body:
            name (str, optional): New name for the event.
            description (str, optional): New description for the event.
            max_team_size (int, optional): New maximum team size for teams in this event.

        Returns:
            JSON response with updated event info or error details.
        """
        data = g.json_data

        is_valid, errors = validate_event_update(data)
        if not is_valid:
            logger.warning(
                "Validation failed for event update",
                extra={
                    "context": {
                        "errors": errors,
                        "admin_id": get_current_user_id(),
                        "endpoint": "event_update",
                        "event_id": event_id,
                    }
                },
            )
            return {"success": False, "errors": errors}, 400

        name = data.get("name")
        description = data.get("description")
        max_team_size = data.get("max_team_size")
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        locked = data.get("locked")

        result = update_event(
            event_id=event_id,
            name=name,
            description=description,
            max_team_size=max_team_size,
            start_time=start_time,
            end_time=end_time,
            locked=locked,
        )

        if result["success"]:
            logger.warning(
                "Admin updated event",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "event_id": event_id,
                        "new_name": name,
                        "new_description": description,
                    }
                },
            )
            return success_response(result)
        else:
            logger.warning(
                "Event update failed",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "event_id": event_id,
                        "error": result["error"],
                    }
                },
            )
            return error_response(result["error"], "event", 400)


@events_namespace.route("/<int:event_id>/teams")
@events_namespace.param("event_id", "Event ID")
class EventTeams(Resource):
    @authed_only
    @handle_integrity_error
    @events_namespace.doc(
        description="Get all teams in a specific event",
        responses={
            200: "Success - Teams in event returned",
            403: "Forbidden - User not authenticated",
            404: "Not found - Event does not exist",
            500: "Internal Server Error",
        },
    )
    def get(self, event_id):
        """Get all teams in the event.

        Args:
            event_id (int): The event ID to list teams from.

        Returns:
            JSON response with list of teams in the event or error details.
        """
        result = list_teams_in_event(event_id)

        if result["success"]:
            logger.info(
                "Event teams retrieved",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "event_id": event_id,
                        "team_count": len(result.get("teams", [])),
                    }
                },
            )

        return controller_response(result, error_field="event")
