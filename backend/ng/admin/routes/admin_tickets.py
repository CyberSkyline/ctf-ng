"""
Admin API routes for support ticket management.
"""

from flask import request, g
from flask_restx import Namespace, Resource

from ...support.controllers import (
    list_tickets,
    get_ticket,
    update_ticket,
    assign_ticket,
    close_ticket,
    create_tag,
    update_tag,
    delete_tag,
    list_tags,
)
from ...core.validation import (
    validate_ticket_update,
    validate_ticket_assignment,
    validate_ticket_filters,
    validate_tag_creation,
    validate_tag_update,
)
from ...core.utils import success_response
from ...core.middleware import (
    admin_endpoint,
    load_ticket,
    load_tag,
    load_associations_from_request,
)
from ...core.docs import (
    ADMIN_GET_ALL_TICKETS_DOC,
    ADMIN_GET_TICKET_DETAILS_DOC,
    ADMIN_UPDATE_TICKET_DOC,
    ADMIN_ASSIGN_TICKET_DOC,
    ADMIN_CLOSE_TICKET_DOC,
    ADMIN_CREATE_TAG_DOC,
    ADMIN_UPDATE_TAG_DOC,
    ADMIN_DELETE_TAG_DOC,
    LIST_TAGS_DOC,
)


admin_tickets_namespace = Namespace("admin/support", description="admin support ticket operations")


@admin_tickets_namespace.route("/tickets")
class AdminTicketList(Resource):
    @admin_endpoint()
    @admin_tickets_namespace.doc(**ADMIN_GET_ALL_TICKETS_DOC)
    def get(self):
        """Get all tickets"""
        filters = validate_ticket_filters(request.args.to_dict())
        result = list_tickets(
            filters.get("user_id"),
            filters.get("status", "all"),
            filters.get("assigned_to"),
            filters.get("event_id"),
            filters.get("team_id"),
            is_admin=True,
        )
        return success_response(result)


@admin_tickets_namespace.route("/tickets/<int:ticket_id>")
class AdminTicketDetail(Resource):
    @admin_endpoint()
    @load_ticket()
    @admin_tickets_namespace.doc(**ADMIN_GET_TICKET_DETAILS_DOC)
    def get(self, ticket_id):
        """Get any ticket"""
        result = get_ticket(ticket_id, g.user.id, is_admin=True)
        return success_response(result)

    @admin_endpoint(json_required=True, validation_func=validate_ticket_update)
    @load_ticket()
    @load_associations_from_request()
    @admin_tickets_namespace.doc(**ADMIN_UPDATE_TICKET_DOC)
    def patch(self, ticket_id):
        """Update any ticket"""
        data = g.validated_data
        result = update_ticket(
            ticket_id,
            g.user.id,
            is_admin=True,
            subject=data.get("subject"),
            event_id=data.get("event_id"),
            team_id=data.get("team_id"),
            challenge_id=data.get("challenge_id"),
        )
        return success_response(result)


@admin_tickets_namespace.route("/tickets/<int:ticket_id>/assign")
class AdminTicketAssign(Resource):
    @admin_endpoint(json_required=True, validation_func=validate_ticket_assignment)
    @load_ticket()
    @admin_tickets_namespace.doc(**ADMIN_ASSIGN_TICKET_DOC)
    def post(self, ticket_id):
        """Assign ticket"""
        data = g.validated_data
        result = assign_ticket(ticket_id, data["user_id"], g.user.id)
        return success_response(result)


@admin_tickets_namespace.route("/tickets/<int:ticket_id>/close")
class AdminTicketClose(Resource):
    @admin_endpoint()
    @load_ticket()
    @admin_tickets_namespace.doc(**ADMIN_CLOSE_TICKET_DOC)
    def post(self, ticket_id):
        """Close ticket"""
        result = close_ticket(ticket_id, g.user.id)
        return success_response(result)


@admin_tickets_namespace.route("/tags")
class AdminTagList(Resource):
    @admin_endpoint()
    @admin_tickets_namespace.doc(**LIST_TAGS_DOC)
    def get(self):
        """List all tags"""
        result = list_tags()
        return success_response(result)

    @admin_endpoint(json_required=True, validation_func=validate_tag_creation)
    @admin_tickets_namespace.doc(**ADMIN_CREATE_TAG_DOC)
    def post(self):
        """Create tag"""
        data = g.validated_data
        result = create_tag(data["name"], data.get("color"), data.get("description"))
        return success_response(result, status_code=201)


@admin_tickets_namespace.route("/tags/<int:tag_id>")
class AdminTagDetail(Resource):
    @admin_endpoint(json_required=True, validation_func=validate_tag_update)
    @load_tag()
    @admin_tickets_namespace.doc(**ADMIN_UPDATE_TAG_DOC)
    def patch(self, tag_id):
        """Update tag"""
        data = g.validated_data
        result = update_tag(tag_id, data.get("name"), data.get("color"), data.get("description"))
        return success_response(result)

    @admin_endpoint()
    @load_tag()
    @admin_tickets_namespace.doc(**ADMIN_DELETE_TAG_DOC)
    def delete(self, tag_id):
        """Delete tag"""
        result = delete_tag(tag_id)
        return success_response(result)
