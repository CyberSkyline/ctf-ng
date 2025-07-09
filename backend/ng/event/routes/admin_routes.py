from flask import g
from flask_restx import Namespace, Resource

from ...core.utils import success_response

from ...event.models.Event import Event

from ...core.middleware.loaders import (
    LoaderType,
    load_event
)

from ...core.middleware import (
    admin_endpoint,
)

events_admin_namespace = Namespace("/admin/events", description="event endpoints for admins")

@events_admin_namespace.route("")
class EventList(Resource):
    @admin_endpoint()
    def get(self):
        """Get all events"""
        result = Event.get_all_events(public_only=False)
        return success_response(result)

    @admin_endpoint(json_required=True, validation_func=Event.validate)
    def post(self):
        """Create event"""
        data = g.validated_data
        result = Event.create_event(**data)
        return success_response(result, status_code=201)

@events_admin_namespace.route("/<int:event_id>")
class EventDetail(Resource):
    @admin_endpoint()
    @load_event(source=LoaderType.PARAM)
    def get(self, event):
        """Get an event"""
        return success_response(event)

    @admin_endpoint(json_required=True, validation_func=Event.validate)
    @load_event(source=LoaderType.PARAM)
    def put(self, event):
        """Update event"""
        data = g.validated_data
        updated_event = event.update_event(**data)
        return success_response(updated_event)
