"""
User API routes for support tickets
"""

from flask import request
from flask_restx import Namespace, Resource

from ...core.middleware import user_endpoint
from ...core.middleware.loaders import load_ticket_by_user
from ...core.utils import success_response
from ...user.models import User

from ..controllers import (
    create_ticket,
    close_my_ticket,
    list_tickets,
    get_ticket,
    create_ticket_message,
)

from ._docs import (
    CREATE_TICKET_DOC,
    LIST_MY_TICKETS_DOC,
    GET_MY_TICKET_DOC,
    ADD_MESSAGE_DOC,
    CLOSE_MY_TICKET_DOC,
)

support_user_namespace = Namespace("support", description="Support ticket operations for users")


@support_user_namespace.route("/tickets")
class Tickets(Resource):
    @support_user_namespace.doc(**CREATE_TICKET_DOC)
    @user_endpoint(json_required=True)
    def post(self, current_user: User, json_data, **kwargs):
        """
        Create a new support ticket
        """
        ticket = create_ticket(
            subject=json_data.get("subject"),
            text=json_data.get("text"),
            current_user=current_user,
            event_id=json_data.get("event_id"),
            team_id=json_data.get("team_id"),
            challenge_id=json_data.get("challenge_id"),
        )
        return success_response(ticket, status_code=201)


@support_user_namespace.route("/me/tickets")
class MyTickets(Resource):
    @support_user_namespace.doc(**LIST_MY_TICKETS_DOC)
    @user_endpoint()
    def get(self, current_user: User, **kwargs):
        """
        Get all tickets for the current user
        """
        status = request.args.get("status", "all")

        tickets = list_tickets(
            user_id=current_user.id,
            status=status,
            is_admin=False,
        )
        return success_response(tickets)


@support_user_namespace.route("/me/tickets/<int:ticket_id>")
class MyTicket(Resource):
    @support_user_namespace.doc(**GET_MY_TICKET_DOC)
    @user_endpoint()
    @load_ticket_by_user()
    def get(self, ticket_id: int, ticket, current_user: User, **kwargs):
        """
        Get ticket details with all messages
        """
        result = get_ticket(ticket_id=ticket_id, ticket=ticket)
        return success_response(result)

    @support_user_namespace.doc(**ADD_MESSAGE_DOC)
    @user_endpoint(json_required=True)
    @load_ticket_by_user()
    def post(self, ticket_id: int, ticket, current_user: User, json_data, **kwargs):
        """
        Add a new message to the ticket
        """
        message = create_ticket_message(
            ticket_id=ticket_id,
            text=json_data.get("text"),
            author_id=current_user.id,
            is_admin=False,
            ticket=ticket,
        )
        return success_response(message, status_code=201)


@support_user_namespace.route("/me/tickets/<int:ticket_id>/close")
class CloseMyTicket(Resource):
    @support_user_namespace.doc(**CLOSE_MY_TICKET_DOC)
    @user_endpoint()
    @load_ticket_by_user()
    def post(self, ticket_id: int, ticket, current_user: User, **kwargs):
        """
        Close user's own ticket
        """
        closed_ticket = close_my_ticket(
            ticket_id=ticket_id,
            ticket=ticket,
            current_user=current_user,
        )

        return success_response(closed_ticket)

