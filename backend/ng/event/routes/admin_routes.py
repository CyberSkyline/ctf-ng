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
    start_event,
    end_event,
    join_event_controller,
    import_challenge_from_yaml,
)
from ...event.models.Event import Event

from ._docs import (
    ADMIN_LIST_EVENTS_DOC,
    ADMIN_CREATE_EVENT_DOC,
    ADMIN_GET_EVENT_DOC,
    ADMIN_UPDATE_EVENT_DOC,
    ADMIN_REGISTER_USER_DOC,
    ADMIN_CREATE_CHALLENGE_DOC,
    START_EVENT_DOC,
    END_EVENT_DOC,
)


events_admin_namespace = Namespace(
    "/admin/events",
    description = "event endpoints for admins"
)


@events_admin_namespace.route("")
class EventList(Resource):
    @events_admin_namespace.doc(**ADMIN_LIST_EVENTS_DOC)
    @admin_endpoint()
    def get(self, **kwargs):
        """
        Get all events
        """
        events = Event.get_all_events(public_only = False)
        return success_response(events)

    @events_admin_namespace.doc(**ADMIN_CREATE_EVENT_DOC)
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
    @events_admin_namespace.doc(**ADMIN_GET_EVENT_DOC)
    @admin_endpoint()
    @load_event(source = LoaderType.PARAM)
    def get(self, event_id, event, **kwargs):
        """
        Get an event
        """
        return success_response(event)

    @events_admin_namespace.doc(**ADMIN_UPDATE_EVENT_DOC)
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
    @events_admin_namespace.doc(**ADMIN_REGISTER_USER_DOC)
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
    @events_admin_namespace.doc(**ADMIN_CREATE_CHALLENGE_DOC)
    @admin_endpoint(json_required = True)
    @load_event(source = LoaderType.PARAM)
    def post(self, event_id, event, json_data, **kwargs):
        """
        Create a challenge for an event
        """
        challenge = import_challenge_from_yaml(event, json_data)
        return success_response(challenge)


@events_admin_namespace.route("/<int:event_id>/start_event")
class EventStart(Resource):
    @events_admin_namespace.doc(**START_EVENT_DOC)
    @admin_endpoint()
    @load_event(source = LoaderType.PARAM)
    def post(self, event_id, event, **kwargs):
        """
        Manually start event
        """
        updated_event = start_event(event)
        return success_response(updated_event)


@events_admin_namespace.route("/<int:event_id>/end_event")
class EventEnd(Resource):
    @events_admin_namespace.doc(**END_EVENT_DOC)
    @admin_endpoint()
    @load_event(source = LoaderType.PARAM)
    def post(self, event_id, event, **kwargs):
        """
        Manually end event
        """
        updated_event = end_event(event)
        return success_response(updated_event)
