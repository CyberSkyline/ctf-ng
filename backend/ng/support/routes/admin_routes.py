"""
Admin API routes for support tickets
"""

from flask_restx import Namespace, Resource

from ...core.middleware import admin_endpoint
from ...core.middleware.loaders import (
    LoaderType,
    load_ticket,
    load_ticket_tag,
    load_user,
)
from ...core.utils import success_response
from ...user.models import User

from ..controllers import (
    create_tag,
    update_tag,
    list_tags,
    set_ticket_tags,
    update_ticket_assignment,
    update_ticket_status,
    update_ticket_mute,
    update_ticket_event,
    update_ticket_challenge,
    list_tickets,
    get_ticket,
    create_ticket_message,
)

from ._docs import (
    LIST_TICKETS_DOC,
    GET_TICKET_DOC,
    ADD_ADMIN_MESSAGE_DOC,
    SET_TICKET_TAGS_DOC,
    ASSIGN_TICKET_DOC,
    UNASSIGN_TICKET_DOC,
    UPDATE_STATUS_DOC,
    UPDATE_MUTE_DOC,
    UPDATE_EVENT_DOC,
    UPDATE_CHALLENGE_DOC,
    LIST_TAGS_DOC,
    CREATE_TAG_DOC,
    UPDATE_TAG_DOC,
)

support_admin_namespace = Namespace("admin/support", description="Admin support ticket operations")


@support_admin_namespace.route("/tickets")
class AdminTickets(Resource):
    @support_admin_namespace.doc(**LIST_TICKETS_DOC)
    @admin_endpoint(json_required=True)
    def get(self, current_user: User, json_data, **kwargs):
        """
        Get all tickets with optional filters
        """
        user_id = json_data.get("user_id")
        status = json_data.get("status", "all")
        assigned_to = json_data.get("assigned_to")
        event_id = json_data.get("event_id")
        team_id = json_data.get("team_id")

        tickets = list_tickets(
            user_id=user_id,
            status=status,
            assigned_to=assigned_to,
            event_id=event_id,
            team_id=team_id,
            is_admin=True,
        )
        return success_response(tickets)


@support_admin_namespace.route("/tickets/<int:ticket_id>")
class AdminTicket(Resource):
    @support_admin_namespace.doc(**GET_TICKET_DOC)
    @admin_endpoint()
    @load_ticket(LoaderType.PARAM)
    def get(self, ticket_id: int, ticket, current_user: User, **kwargs):
        """
        Get any ticket with all messages
        """
        result = get_ticket(ticket_id=ticket_id, ticket=ticket)
        return success_response(result)

    @support_admin_namespace.doc(**ADD_ADMIN_MESSAGE_DOC)
    @admin_endpoint(json_required=True)
    @load_ticket(LoaderType.PARAM)
    def post(self, ticket_id: int, ticket, current_user: User, json_data, **kwargs):
        """
        Add admin message (reopens closed tickets)
        """
        message = create_ticket_message(
            text=json_data.get("text"),
            author_id=current_user.id,
            ticket=ticket,
            is_admin=True,
        )
        return success_response(message, status_code=201)


@support_admin_namespace.route("/tickets/<int:ticket_id>/tag")
class AdminTicketTags(Resource):
    @support_admin_namespace.doc(**SET_TICKET_TAGS_DOC)
    @admin_endpoint(json_required=True)
    @load_ticket(LoaderType.PARAM)
    def put(self, ticket_id: int, ticket, current_user: User, json_data, **kwargs):
        """
        Set ticket tags (replaces all existing tags)
        """
        updated_ticket = set_ticket_tags(
            tag_ids=json_data.get("tag_ids", []),
            ticket=ticket,
        )
        return success_response(updated_ticket)


@support_admin_namespace.route("/tickets/<int:ticket_id>/assign")
class AdminTicketAssignment(Resource):
    @support_admin_namespace.doc(**ASSIGN_TICKET_DOC)
    @admin_endpoint(json_required=True)
    @load_ticket(LoaderType.PARAM)
    @load_user(source=LoaderType.BODY)
    def put(self, ticket_id: int, ticket, user, current_user: User, json_data, **kwargs):
        """
        Assign ticket to a user
        """
        updated_ticket = update_ticket_assignment(
            user=user,
            ticket=ticket,
        )
        return success_response(updated_ticket)


@support_admin_namespace.route("/tickets/<int:ticket_id>/unassign")
class AdminTicketUnassignment(Resource):
    @support_admin_namespace.doc(**UNASSIGN_TICKET_DOC)
    @admin_endpoint(json_required=True)
    @load_ticket(LoaderType.PARAM)
    def put(self, ticket_id: int, ticket, current_user: User, json_data, **kwargs):
        """
        Unassign ticket from current user
        """
        updated_ticket = update_ticket_assignment(
            user=None,
            ticket=ticket,
        )
        return success_response(updated_ticket)


@support_admin_namespace.route("/tickets/<int:ticket_id>/close")
class AdminTicketStatus(Resource):
    @support_admin_namespace.doc(**UPDATE_STATUS_DOC)
    @admin_endpoint(json_required=True)
    @load_ticket(LoaderType.PARAM)
    def put(self, ticket_id: int, ticket, current_user: User, json_data, **kwargs):
        """
        Toggle ticket open/closed status
        """
        updated_ticket = update_ticket_status(
            closed=json_data.get("closed", False),
            ticket=ticket,
            current_user=current_user,
        )
        return success_response(updated_ticket)


@support_admin_namespace.route("/tickets/<int:ticket_id>/mute")
class AdminTicketMute(Resource):
    @support_admin_namespace.doc(**UPDATE_MUTE_DOC)
    @admin_endpoint(json_required=True)
    @load_ticket(LoaderType.PARAM)
    def put(self, ticket_id: int, ticket, current_user: User, json_data, **kwargs):
        """
        Toggle ticket mute status
        """
        updated_ticket = update_ticket_mute(
            ticket_id=ticket_id,
            muted=json_data.get("muted", False),
            ticket=ticket,
        )

        return success_response(updated_ticket)


@support_admin_namespace.route("/tickets/<int:ticket_id>/event")
class AdminTicketEvent(Resource):
    @support_admin_namespace.doc(**UPDATE_EVENT_DOC)
    @admin_endpoint(json_required=True)
    @load_ticket(LoaderType.PARAM)
    def put(self, ticket_id: int, ticket, current_user: User, json_data, **kwargs):
        """
        Update ticket event/team association
        """
        updated_ticket = update_ticket_event(
            ticket_id=ticket_id,
            event_id=json_data.get("event_id"),
            team_id=json_data.get("team_id"),
            ticket=ticket,
        )
        return success_response(updated_ticket)


@support_admin_namespace.route("/tickets/<int:ticket_id>/challenge")
class AdminTicketChallenge(Resource):
    @support_admin_namespace.doc(**UPDATE_CHALLENGE_DOC)
    @admin_endpoint(json_required=True)
    @load_ticket(LoaderType.PARAM)
    def put(self, ticket_id: int, ticket, current_user: User, json_data, **kwargs):
        """
        Update ticket challenge association
        """
        updated_ticket = update_ticket_challenge(
            ticket_id=ticket_id,
            challenge_id=json_data.get("challenge_id"),
            ticket=ticket,
        )
        return success_response(updated_ticket)


@support_admin_namespace.route("/tags")
class AdminTags(Resource):
    @support_admin_namespace.doc(**LIST_TAGS_DOC)
    @admin_endpoint()
    def get(self, current_user: User, **kwargs):
        """
        Get all ticket tags
        """
        tags = list_tags()
        return success_response(tags)

    @support_admin_namespace.doc(**CREATE_TAG_DOC)
    @admin_endpoint(json_required=True)
    def post(self, current_user: User, json_data, **kwargs):
        """
        Create a new tag
        """
        tag = create_tag(
            name=json_data.get("name"),
            color=json_data.get("color"),
            description=json_data.get("description"),
        )
        return success_response(tag, status_code=201)


@support_admin_namespace.route("/tags/<int:ticket_tag_id>")
class AdminTag(Resource):
    @support_admin_namespace.doc(**UPDATE_TAG_DOC)
    @admin_endpoint(json_required=True)
    @load_ticket_tag(LoaderType.PARAM)
    def put(self, ticket_tag_id: int, ticket_tag, current_user: User, json_data, **kwargs):
        """
        Update an existing tag
        """
        updated_tag = update_tag(
            tag=ticket_tag,
            name=json_data.get("name"),
            color=json_data.get("color"),
            description=json_data.get("description"),
        )
        return success_response(updated_tag)
