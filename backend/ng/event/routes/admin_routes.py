"""
User Routes for Event Operations
"""

from flask_restx import Namespace, Resource

from ...core.utils import success_response
from ...core.middleware.loaders import (
    LoaderType,
    load_event,
    load_user,
)
from ...core.middleware import (
    admin_endpoint,
)
from ..controllers import (
    join_event_controller,
    import_challenge_from_yaml,
)
from ...event.models.Event import Event



events_admin_namespace = Namespace(
    "/admin/events",
    description = "event endpoints for admins"
)


@events_admin_namespace.route("")
class EventList(Resource):
    @events_admin_namespace.doc(
        description="Get all events (public and private) for admin management",
        responses={
            200: "Success - Returns list of all events",
            404: "Not found - No events found",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error",
        },
    )
    @admin_endpoint()
    def get(self, **kwargs):
        """
        Get all events
        """
        events = Event.get_all_events(public_only = False)
        return success_response(events)

    @events_admin_namespace.doc(
        description="Create a new event with scheduling and configuration options",
        params={
            "name": {
                "description": "Event name (256 character max length)",
                "in": "body",
                "required": True,
            "type": "string",
            "example": "New CTF Event"
            },
            "description": {
                "description": "Event description (1000 character max length)",
                "in": "body",
                "required": False,
                "type": "string",
                "example": "Description of the new event"
            },
            "start_time": {
                "description": "Event start time in ISO format",
                "in": "body",
                "required": False,
                "type": "string",
                "example": "2023-10-01T00:00:00Z"
            },
            "end_time": {
                "description": "Event end time in ISO format",
                "in": "body",
                "required": False,
                "type": "string",
                "example": "2023-10-31T23:59:59Z"
            }
        },
        responses={
            201: "Success - Event created successfully",
            400: "Bad request - Validation failed or name conflict",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error",
        }
    )
    @admin_endpoint(json_required = True, validation_func = Event.validate)
    def post(self, validated_data, **kwargs):
        """
        Create event
        """
        data = validated_data
        result = Event.create_event(**data)
        return success_response(result, status_code = 201)


@events_admin_namespace.route("/<int:event_id>")
class EventDetail(Resource):
    @events_admin_namespace.doc(description="Get detailed information about a specific event",
    responses={
        200: "Success - Returns event details",
        404: "Not found - Event does not exist",
        403: "Forbidden - Admin access required",
        500: "Internal Server Error",
    },)
    @admin_endpoint()
    @load_event(source = LoaderType.PARAM)
    def get(self, event_id, event, **kwargs):
        """
        Get an event
        """
        return success_response(event)

    @events_admin_namespace.doc(
        description="Update an existing event's configuration and settings",
        params={
            "name": {
                "description": "Updated event name (256 character max length)",
                "in": "body",
                "required": False,
            "type": "string",
            "example": "Updated Event Name"
        },
        "description": {
            "description": "Updated event description (1000 character max length)",
            "in": "body",
            "required": False,
            "type": "string",
            "example": "Updated description of the event"
        },
        "start_time": {
            "description": "Updated event start time in ISO format",
            "in": "body",
            "required": False,
            "type": "string",
            "example": "2023-10-01T00:00:00Z"
        },
        "end_time": {
            "description": "Updated event end time in ISO format",
            "in": "body",
            "required": False,
            "type": "string",
            "example": "2023-10-31T23:59:59Z"
        }
    },
        responses={
            200: "Success - Event updated successfully",
            400: "Bad request - Validation failed",
            404: "Not found - Event does not exist",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error",
        }
    )
    @admin_endpoint(json_required = True, validation_func = Event.validate)
    @load_event(source = LoaderType.PARAM)
    def put(self, event_id, event, validated_data, **kwargs):
        """
        Update event
        """
        data = validated_data
        updated_event = event.update_event(**data)
        return success_response(updated_event)


@events_admin_namespace.route("/<int:event_id>/<int:user_id>/register")
class EventRegister(Resource):
    @events_admin_namespace.doc(
        description="Register a user for an event using invite code or team name",
        params={
            "invite_code": {
                "description": "Invite code for joining an existing team",
                "in": "body",
                "required": False,
            "type": "string",
            "example": "xchfg459fghj"
        },
        "team_name": {
            "description": "Name for creating a new team",
            "in": "body",
            "required": False,
            "type": "string",
            "example": "My Team"
        }
    },
        responses={
            200: "Success - User registered for event",
            400: "Bad request - Missing invite_code or team_name",
            404: "Not found - Event or user does not exist",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error",
        },
    )
    @admin_endpoint(json_required = True)
    @load_event(source = LoaderType.PARAM)
    @load_user(source = LoaderType.PARAM)
    def post(self, event_id, user_id, **kwargs):
        """
        Register a user for an event
        """
        json_data = kwargs.get("json_data", {})
        if "invite_code" in json_data:
            result = join_event_controller(
                kwargs.get("event"),
                kwargs.get("user"),
                json_data["invite_code"]
            )
        elif "team_name" in json_data:
            result = join_event_controller(
                kwargs.get("event"),
                kwargs.get("user"),
                team_name = json_data["team_name"]
            )
        return success_response(result)


@events_admin_namespace.route("/<int:event_id>/challenges")
class EventChallenges(Resource):
    @events_admin_namespace.doc(
        description="Create a challenge for an event using YAML configuration",
        params={
            "name": {
                "description": "Challenge name",
                "in": "body",
                "required": True,
            "type": "string",
            "example": "Web Security Challenge"
        },
        "description": {
            "description": "Challenge description and instructions",
            "in": "body",
            "required": True,
            "type": "string",
            "example": "Find the vulnerability in this web application"
        },
        "value": {
            "description": "Point value for the challenge",
            "in": "body",
            "required": True,
            "type": "integer",
            "example": 100
        },
        "category": {
            "description": "Challenge category",
            "in": "body",
            "required": True,
            "type": "string",
            "example": "Web"
        }
    },
    responses={
        200: "Success - Challenge created successfully",
        400: "Bad request - Invalid challenge data",
        404: "Not found - Event does not exist",
        403: "Forbidden - Admin access required",
        500: "Internal Server Error",
    },
)
    @admin_endpoint(json_required = True)
    @load_event(source = LoaderType.PARAM)
    def post(self, event_id, event, json_data, **kwargs):
        """
        Create a challenge for an event
        """
        challenge = import_challenge_from_yaml(event, json_data)
        return success_response(challenge)

