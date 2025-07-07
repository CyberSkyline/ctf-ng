"""
Event management API routes.
"""

from flask import g
from flask_restx import Namespace, Resource

from ..controllers import (
    create_event,
    list_events,
    get_event_info,
    update_event,
)
from ...team.controllers import list_teams_in_event
from ...core.utils import success_response

from ...event.models.Event import Event

from ...core.middleware import (
    user_endpoint,
    admin_endpoint,
    load_event,
)
from ...core.docs import (
    LIST_EVENTS_DOC,
    CREATE_EVENT_DOC,
    GET_EVENT_DOC,
    UPDATE_EVENT_DOC,
    GET_EVENT_TEAMS_DOC,
)


events_namespace = Namespace("events", description="event management operations")


@events_namespace.route("")
class EventList(Resource):
    @user_endpoint()
    @events_namespace.doc(**LIST_EVENTS_DOC)
    def get(self):
        """Get all events"""
        result = list_events()
        return success_response(result)

    @admin_endpoint(json_required=True, validation_func=Event.validate)
    @events_namespace.doc(**CREATE_EVENT_DOC)
    def post(self):
        """Create event"""
        data = g.validated_data
        result = create_event(
            data["name"],
            data.get("description"),
            data.get("max_team_size"),
            data.get("start_time"),
            data.get("end_time"),
            data.get("locked", False),
        )
        return success_response(result, status_code=201)


@events_namespace.route("/<int:event_id>")
class EventDetail(Resource):
    @user_endpoint()
    @load_event()
    @events_namespace.doc(**GET_EVENT_DOC)
    def get(self, event_id):
        """Get event details"""
        result = get_event_info(event_id)
        return success_response(result)

    @admin_endpoint(json_required=True, validation_func=Event.validate)
    @load_event()
    @events_namespace.doc(**UPDATE_EVENT_DOC)
    def patch(self, event_id):
        """Update event"""
        data = g.validated_data
        result = update_event(
            event_id,
            data.get("name"),
            data.get("description"),
            data.get("max_team_size"),
            data.get("start_time"),
            data.get("end_time"),
            data.get("locked"),
        )
        return success_response(result)


@events_namespace.route("/<int:event_id>/teams")
class EventTeams(Resource):
    @user_endpoint()
    @load_event()
    @events_namespace.doc(**GET_EVENT_TEAMS_DOC)
    def get(self, event_id):
        """Get teams in event"""
        result = list_teams_in_event(event_id)
        return success_response(result)
