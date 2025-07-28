from flask_restx import Namespace, Resource


from ...core.utils import success_response

from ...event.models.Event import Event

from ...core.middleware.loaders import (
    LoaderType,
    load_event,
    load_user,
)

from ...core.middleware import (
    admin_endpoint,
)
from ..controllers.user import join_event_controller

from ...core.middleware import (
    admin_endpoint,
)
from ...core.middleware.loaders import LoaderType, load_event
from ...core.utils import success_response
from ...event.models.Event import Event
from ..controllers.admin.import_challenge_from_yaml import import_challenge_from_yaml

events_admin_namespace = Namespace("/admin/events", description="event endpoints for admins")


@events_admin_namespace.route("")
class EventList(Resource):
    @admin_endpoint()
    @events_admin_namespace.doc(
        description="Get all events",
        responses={
            200: "Success",
            404: "No events found",
        },
    )
    def get(self, **kwargs):
        """Get all events"""
        events = Event.get_all_events(public_only=False)
        return success_response(events)

    @admin_endpoint(json_required=True, validation_func=Event.validate)
    @events_admin_namespace.doc(
        description="Create a new event",
        responses={
            201: "Event created successfully",
            400: "Bad Request if validation fails",
        },
        params={
            "json_data": {
                "description": "Event data in JSON format",
                "in": "body",
                "required": True,
                "example": {
                    "name": "New Event",
                    "description": "Description of the new event",
                    "start_time": "2023-10-01T00:00:00Z",
                    "end_time": "2023-10-31T23:59:59Z"
                }
            }
        }
    )
    def post(self, validated_data, **kwargs):
        """Create event"""
        data = validated_data
        result = Event.create_event(**data)
        return success_response(result, status_code=201)


@events_admin_namespace.route("/<int:event_id>")
class EventDetail(Resource):
    @admin_endpoint()
    @load_event(source=LoaderType.PARAM)
    @events_admin_namespace.doc(
        description="Get an event by ID",
        responses={
            200: "Success",
            404: "Event not found",
        },
    )
    def get(self, event_id, event, **kwargs):
        """Get an event"""
        return success_response(event)

    @admin_endpoint(json_required=True, validation_func=Event.validate)
    @load_event(source=LoaderType.PARAM)
    @events_admin_namespace.doc(
        description="Update an event by ID",
        responses={
            200: "Success",
            404: "Event not found",
            400: "Bad Request if validation fails",
        },
        params={
            "json_data": {
                "description": "Event data in JSON format",
                "in": "body",
                "required": True,
                "example": {
                    "name": "Updated Event Name",
                    "description": "Updated description of the event",
                    "start_time": "2023-10-01T00:00:00Z",
                    "end_time": "2023-10-31T23:59:59Z"
                }
            }
        }
    )
    def put(self, event_id, event, validated_data, **kwargs):
        """Update event"""
        data = validated_data
        updated_event = event.update_event(**data)
        return success_response(updated_event)

@events_admin_namespace.route("/<int:event_id>/<int:user_id>/register")
class EventRegister(Resource):
    @admin_endpoint(json_required=True)
    @load_event(source=LoaderType.PARAM)
    @load_user(source=LoaderType.PARAM)
    @events_admin_namespace.doc(
        description="Register a user for an event",
        responses={
            200: "Success",
            400: "Bad Request if invite_code or team_name is missing",
            404: "Event or User not found",
        },
        params={
            "invite_code": {
                "description": "Invite code for the event",
                "in": "body",
                "required": False,
                "example": "xchfg459fghj",
            },
            "team_name": {
                "description": "Name of the team to join",
                "in": "body",
                "required": False,
                "example": "My Team",
            }
        }
    )
    def post(self, event_id, user_id, **kwargs):
        """Register a user for an event"""
        json_data = kwargs.get("json_data", {})
        if "invite_code" in json_data:
            result = join_event_controller(kwargs.get("event"), kwargs.get("user"), json_data["invite_code"])
        elif "team_name" in json_data:
            result = join_event_controller(kwargs.get("event"), kwargs.get("user"), team_name=json_data["team_name"])

        return success_response(result)

@events_admin_namespace.route("/<int:event_id>/challenges")
class EventChallenges(Resource):
    @events_admin_namespace.doc(
        description="Create a challenge for an event",
        responses={
            200: "Success",
            400: "Bad request",
        },
    )
    @admin_endpoint(json_required=True)
    @load_event(source=LoaderType.PARAM)
    @events_admin_namespace.doc(
        description="Create a challenge for an event",
        responses={
            200: "Success",
            400: "Bad Request if JSON data is invalid",
            404: "Event not found",
        },
        params={
            "json_data": {
                "description": "Challenge data in JSON format",
                "in": "body",
                "required": True,
                "example": {
                    "name": "New Challenge",
                    "description": "Description of the challenge",
                    "value": 100,
                    "category": "Category Name"
                }
            }
        }
    )
    def post(self, event_id, event, json_data, **kwargs):
        """Create a challenge for an event"""
        challenge = import_challenge_from_yaml(event, json_data)
        return success_response(challenge)
