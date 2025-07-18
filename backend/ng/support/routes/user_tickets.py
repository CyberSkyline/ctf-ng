"""
User facing API routes for support ticket operations.
"""

from flask import request
from flask_restx import Namespace, Resource

from ..controllers.all_actions import (
    list_tickets,
    get_ticket,
    create_ticket_message,
    update_ticket,
)

from ..controllers.user_actions import (
    create_ticket,
)

from ...core.validation import (
    validate_ticket_creation,
    validate_ticket_message,
    validate_ticket_update,
    validate_ticket_filters,
)
from ...core.utils import success_response
from ...core.middleware import (
    user_endpoint,
)
from ...core.middleware.loaders import (
    LoaderType,
    load_ticket,
)
from ..docs.user_tickets_docs import (
    GET_MY_TICKETS_DOC,
    CREATE_NEW_TICKET_DOC,
    GET_MY_TICKET_DETAILS_DOC,
    UPDATE_MY_TICKET_DOC,
    CREATE_TICKET_REPLY_DOC,
)


user_tickets_namespace = Namespace("tickets", description="support ticket operations")


@user_tickets_namespace.route("")
class TicketList(Resource):
    @user_endpoint()
    @user_tickets_namespace.doc(**GET_MY_TICKETS_DOC)
    def get(self, current_user):
        """Get user tickets"""
        filters = validate_ticket_filters(request.args.to_dict())
        result = list_tickets(current_user.id, filters.get("status", "all"), is_admin=False)
        return success_response(result)

    @user_endpoint(json_required=True, validation_func=validate_ticket_creation)
    @user_tickets_namespace.doc(**CREATE_NEW_TICKET_DOC)
    def post(self, validated_data, current_user):
        """Create ticket"""
        result = create_ticket(
            validated_data["subject"],
            current_user.id,
            validated_data.get("event_id"),
            validated_data.get("team_id"),
            validated_data.get("challenge_id"),
            validated_data.get("tag_ids"),
        )
        return success_response(result, status_code=201)

@user_tickets_namespace.route("/<int:ticket_id>")
class TicketDetail(Resource):
    @user_endpoint()
    @load_ticket(LoaderType.PARAM)
    @user_tickets_namespace.doc(**GET_MY_TICKET_DETAILS_DOC)
    def get(self, ticket_id, current_user):
        """Get ticket details"""
        result = get_ticket(ticket_id, current_user.id, is_admin=False)
        return success_response(result)

    @user_endpoint(json_required=True, validation_func=validate_ticket_update)
    @load_ticket(LoaderType.PARAM)
    @user_tickets_namespace.doc(**UPDATE_MY_TICKET_DOC)
    def patch(self, ticket_id, validated_data, current_user):
        """Update ticket"""
        result = update_ticket(ticket_id, current_user.id, is_admin=False, subject=validated_data.get("subject"))
        return success_response(result)


@user_tickets_namespace.route("/<int:ticket_id>/messages")
class TicketMessages(Resource):
    @user_endpoint(json_required=True, validation_func=validate_ticket_message)
    @load_ticket(LoaderType.PARAM)
    @user_tickets_namespace.doc(**CREATE_TICKET_REPLY_DOC)
    def post(self, ticket_id, validated_data, current_user):
        """Reply to ticket"""
        result = create_ticket_message(ticket_id, validated_data["text"], current_user.id, is_admin=False)
        return success_response(result, status_code=201)
