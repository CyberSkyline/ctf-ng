"""
/backend/ng/support/routes/admin_tickets.py
Admin API routes for support ticket management.
"""

from flask import request, g
from flask_restx import Namespace, Resource
from CTFd.utils.decorators import admins_only

from ..controllers import (
    list_tickets,
    get_ticket,
    create_ticket_message,
    update_ticket,
    assign_ticket,
    unassign_ticket,
    close_ticket,
    reopen_ticket,
    mute_ticket,
    unmute_ticket,
    get_ticket_statistics,
    create_tag,
    update_tag,
    delete_tag,
    list_tags,
    add_tags_to_ticket,
    remove_tags_from_ticket
)
from ..exceptions import (
    TicketNotFoundError,
    TicketValidationError,
    TicketOperationError,
    TagNotFoundError
)
from ..validators import (
    validate_ticket_filters,
    validate_ticket_message,
    validate_ticket_update,
    validate_ticket_assignment,
    validate_tag_creation,
    validate_tag_update
)
from ...core.utils.api_responses import success_response, error_response
from ...core.utils.logger import get_logger
from ...core.utils import get_current_user_id
from ...core.middleware import handle_integrity_error, json_body_required

admin_tickets_namespace = Namespace("admin/support", description="admin support ticket operations")
logger = get_logger(__name__)


@admin_tickets_namespace.route("/tickets")
class AdminTicketList(Resource):
    @admins_only
    @handle_integrity_error
    @admin_tickets_namespace.doc(
        description="Get all support tickets with filters (Admin only)",
        responses={
            200: "Success - Returns filtered list of tickets",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error"
        }
    )
    def get(self):
        """Get all tickets with optional filters.
        
        Query Parameters:
            status: Filter by status (open, closed, muted, all)
            user_id: Filter by ticket author
            assigned_to: Filter by assigned user
            event_id: Filter by event
            team_id: Filter by team
            
        Returns:
            JSON response with filtered tickets
        """

        filters = {
            "status": request.args.get("status", "all"),
            "user_id": request.args.get("user_id", type=int),
            "assigned_to": request.args.get("assigned_to", type=int),
            "event_id": request.args.get("event_id", type=int),
            "team_id": request.args.get("team_id", type=int)
        }
        
        filters = {k: v for k, v in filters.items() if v is not None}
        
        is_valid, errors = validate_ticket_filters(filters)
        if not is_valid:
            return {"success": False, "errors": errors}, 400
        
        try:
            result = list_tickets(
                user_id=filters.get("user_id"),
                status=filters.get("status", "all"),
                assigned_to=filters.get("assigned_to"),
                event_id=filters.get("event_id"),
                team_id=filters.get("team_id"),
                is_admin=True
            )
            
            logger.info(
                "Admin accessed ticket list",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "filters": filters,
                        "ticket_count": len(result.get("tickets", []))
                    }
                }
            )
            
            return success_response(result)
            
        except Exception as e:
            logger.error(
                "Failed to list tickets for admin",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "error": str(e)
                    }
                }
            )
            return error_response("Failed to retrieve tickets", "tickets", 500)


@admin_tickets_namespace.route("/tickets/<int:ticket_id>")
@admin_tickets_namespace.param("ticket_id", "Ticket ID")
class AdminTicketDetail(Resource):
    @admins_only
    @handle_integrity_error
    @admin_tickets_namespace.doc(
        description="Get any ticket with full details (Admin only)",
        responses={
            200: "Success - Ticket details returned",
            404: "Not found - Ticket does not exist",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error"
        }
    )
    def get(self, ticket_id):
        """Get full details of any ticket.
        
        Args:
            ticket_id (int): The ticket ID to get
            
        Returns:
            JSON response with full ticket details
        """
        try:
            result = get_ticket(
                ticket_id=ticket_id,
                user_id=get_current_user_id(),
                is_admin=True
            )
            
            return success_response(result)
            
        except TicketNotFoundError as e:
            return error_response(str(e), "ticket", 404)
        except Exception as e:
            logger.error(
                "Failed to get ticket for admin",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "ticket_id": ticket_id,
                        "error": str(e)
                    }
                }
            )
            return error_response("Failed to retrieve ticket", "ticket", 500)

    @admins_only
    @json_body_required
    @handle_integrity_error
    @admin_tickets_namespace.doc(
        description="Update any ticket (Admin only)",
        responses={
            200: "Success - Ticket updated",
            400: "Bad request - Invalid data",
            404: "Not found - Ticket does not exist",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error"
        }
    )
    def patch(self, ticket_id):
        """Update ticket with full admin capabilities.
        
        Args:
            ticket_id (int): The ticket ID to update
            
        Request Body:
            subject (str): New subject
            event_id (int): New event association (0 to unassign)
            team_id (int): New team association (0 to unassign)
            challenge_id (int): New challenge association (0 to unassign)
            
        Returns:
            JSON response with updated ticket
        """
        data = g.json_data
        
        # Validate data
        is_valid, errors = validate_ticket_update(data)
        if not is_valid:
            return {"success": False, "errors": errors}, 400
        
        try:
            result = update_ticket(
                ticket_id=ticket_id,
                actor_id=get_current_user_id(),
                is_admin=True,
                subject=data.get("subject"),
                event_id=data.get("event_id"),
                team_id=data.get("team_id"),
                challenge_id=data.get("challenge_id")
            )
            
            return success_response(result)
            
        except TicketNotFoundError as e:
            return error_response(str(e), "ticket", 404)
        except TicketValidationError as e:
            return error_response(str(e), "ticket", 400)
        except Exception as e:
            logger.error(
                "Failed to update ticket for admin",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "ticket_id": ticket_id,
                        "error": str(e)
                    }
                }
            )
            return error_response("Failed to update ticket", "ticket", 500)


@admin_tickets_namespace.route("/tickets/<int:ticket_id>/messages")
@admin_tickets_namespace.param("ticket_id", "Ticket ID")
class AdminTicketMessages(Resource):
    @admins_only
    @json_body_required
    @handle_integrity_error
    @admin_tickets_namespace.doc(
        description="Admin reply to any ticket",
        responses={
            201: "Success - Message created",
            400: "Bad request - Invalid data",
            404: "Not found - Ticket does not exist",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error"
        }
    )
    def post(self, ticket_id):
        """Admin reply to any ticket.
        
        Args:
            ticket_id (int): The ticket to reply to
            
        Request Body:
            text (str): Message content
            
        Returns:
            JSON response with created message
        """
        data = g.json_data
        
        # Validate data
        is_valid, errors = validate_ticket_message(data)
        if not is_valid:
            return {"success": False, "errors": errors}, 400
        
        try:
            result = create_ticket_message(
                ticket_id=ticket_id,
                text=data["text"],
                author_id=get_current_user_id(),
                is_admin=True
            )
            
            return success_response(result, status_code=201)
            
        except TicketNotFoundError as e:
            return error_response(str(e), "ticket", 404)
        except Exception as e:
            logger.error(
                "Failed to create admin message",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "ticket_id": ticket_id,
                        "error": str(e)
                    }
                }
            )
            return error_response("Failed to create message", "message", 500)


@admin_tickets_namespace.route("/tickets/<int:ticket_id>/assign")
@admin_tickets_namespace.param("ticket_id", "Ticket ID")
class AdminTicketAssign(Resource):
    @admins_only
    @json_body_required
    @handle_integrity_error
    @admin_tickets_namespace.doc(
        description="Assign ticket to a user (Admin only)",
        responses={
            200: "Success - Ticket assigned",
            400: "Bad request - Invalid data",
            404: "Not found - Ticket or user does not exist",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error"
        }
    )
    def post(self, ticket_id):
        """Assign ticket to a user.
        
        Args:
            ticket_id (int): The ticket to assign
            
        Request Body:
            user_id (int): User to assign to
            
        Returns:
            JSON response with updated ticket
        """
        data = g.json_data
        
        # Validate data
        is_valid, errors = validate_ticket_assignment(data)
        if not is_valid:
            return {"success": False, "errors": errors}, 400
        
        try:
            result = assign_ticket(
                ticket_id=ticket_id,
                user_id=data["user_id"],
                admin_id=get_current_user_id()
            )
            
            return success_response(result)
            
        except TicketNotFoundError as e:
            return error_response(str(e), "ticket", 404)
        except TicketValidationError as e:
            return error_response(str(e), "user", 400)
        except Exception as e:
            logger.error(
                "Failed to assign ticket",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "ticket_id": ticket_id,
                        "error": str(e)
                    }
                }
            )
            return error_response("Failed to assign ticket", "assignment", 500)

    @admins_only
    @handle_integrity_error
    @admin_tickets_namespace.doc(
        description="Remove ticket assignment (Admin only)",
        responses={
            200: "Success - Assignment removed",
            404: "Not found - Ticket does not exist",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error"
        }
    )
    def delete(self, ticket_id):
        """Remove ticket assignment.
        
        Args:
            ticket_id (int): The ticket to unassign
            
        Returns:
            JSON response with updated ticket
        """
        try:
            result = unassign_ticket(
                ticket_id=ticket_id,
                admin_id=get_current_user_id()
            )
            
            return success_response(result)
            
        except TicketNotFoundError as e:
            return error_response(str(e), "ticket", 404)
        except Exception as e:
            logger.error(
                "Failed to unassign ticket",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "ticket_id": ticket_id,
                        "error": str(e)
                    }
                }
            )
            return error_response("Failed to unassign ticket", "assignment", 500)


@admin_tickets_namespace.route("/tickets/<int:ticket_id>/close")
@admin_tickets_namespace.param("ticket_id", "Ticket ID")
class AdminTicketClose(Resource):
    @admins_only
    @handle_integrity_error
    @admin_tickets_namespace.doc(
        description="Close a ticket (Admin only)",
        responses={
            200: "Success - Ticket closed",
            400: "Bad request - Ticket already closed",
            404: "Not found - Ticket does not exist",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error"
        }
    )
    def post(self, ticket_id):
        """Close a ticket.
        
        Args:
            ticket_id (int): The ticket to close
            
        Returns:
            JSON response with updated ticket
        """
        try:
            result = close_ticket(
                ticket_id=ticket_id,
                admin_id=get_current_user_id()
            )
            
            return success_response(result)
            
        except TicketNotFoundError as e:
            return error_response(str(e), "ticket", 404)
        except TicketValidationError as e:
            return error_response(str(e), "ticket", 400)
        except Exception as e:
            logger.error(
                "Failed to close ticket",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "ticket_id": ticket_id,
                        "error": str(e)
                    }
                }
            )
            return error_response("Failed to close ticket", "ticket", 500)


@admin_tickets_namespace.route("/tickets/<int:ticket_id>/reopen")
@admin_tickets_namespace.param("ticket_id", "Ticket ID")
class AdminTicketReopen(Resource):
    @admins_only
    @handle_integrity_error
    @admin_tickets_namespace.doc(
        description="Reopen a closed ticket (Admin only)",
        responses={
            200: "Success - Ticket reopened",
            400: "Bad request - Ticket not closed",
            404: "Not found - Ticket does not exist",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error"
        }
    )
    def post(self, ticket_id):
        """Reopen a closed ticket.
        
        Args:
            ticket_id (int): The ticket to reopen
            
        Returns:
            JSON response with updated ticket
        """
        try:
            result = reopen_ticket(
                ticket_id=ticket_id,
                admin_id=get_current_user_id()
            )
            
            return success_response(result)
            
        except TicketNotFoundError as e:
            return error_response(str(e), "ticket", 404)
        except TicketValidationError as e:
            return error_response(str(e), "ticket", 400)
        except Exception as e:
            logger.error(
                "Failed to reopen ticket",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "ticket_id": ticket_id,
                        "error": str(e)
                    }
                }
            )
            return error_response("Failed to reopen ticket", "ticket", 500)


@admin_tickets_namespace.route("/tickets/<int:ticket_id>/mute")
@admin_tickets_namespace.param("ticket_id", "Ticket ID")
class AdminTicketMute(Resource):
    @admins_only
    @handle_integrity_error
    @admin_tickets_namespace.doc(
        description="Mute/unmute a ticket (Admin only)",
        responses={
            200: "Success - Ticket muted/unmuted",
            400: "Bad request - Invalid operation",
            404: "Not found - Ticket does not exist",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error"
        }
    )
    def post(self, ticket_id):
        """Mute a ticket.
        
        Args:
            ticket_id (int): The ticket to mute
            
        Returns:
            JSON response with updated ticket
        """
        try:
            result = mute_ticket(
                ticket_id=ticket_id,
                admin_id=get_current_user_id()
            )
            
            return success_response(result)
            
        except TicketNotFoundError as e:
            return error_response(str(e), "ticket", 404)
        except TicketValidationError as e:
            return error_response(str(e), "ticket", 400)
        except Exception as e:
            logger.error(
                "Failed to mute ticket",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "ticket_id": ticket_id,
                        "error": str(e)
                    }
                }
            )
            return error_response("Failed to mute ticket", "ticket", 500)

    @admins_only
    @handle_integrity_error
    @admin_tickets_namespace.doc(
        description="Unmute a ticket (Admin only)",
        responses={
            200: "Success - Ticket unmuted",
            400: "Bad request - Ticket not muted",
            404: "Not found - Ticket does not exist",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error"
        }
    )
    def delete(self, ticket_id):
        """Unmute a ticket.
        
        Args:
            ticket_id (int): The ticket to unmute
            
        Returns:
            JSON response with updated ticket
        """
        try:
            result = unmute_ticket(
                ticket_id=ticket_id,
                admin_id=get_current_user_id()
            )
            
            return success_response(result)
            
        except TicketNotFoundError as e:
            return error_response(str(e), "ticket", 404)
        except TicketValidationError as e:
            return error_response(str(e), "ticket", 400)
        except Exception as e:
            logger.error(
                "Failed to unmute ticket",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "ticket_id": ticket_id,
                        "error": str(e)
                    }
                }
            )
            return error_response("Failed to unmute ticket", "ticket", 500)


@admin_tickets_namespace.route("/tickets/statistics")
class AdminTicketStatistics(Resource):
    @admins_only
    @handle_integrity_error
    @admin_tickets_namespace.doc(
        description="Get ticket system statistics (Admin only)",
        responses={
            200: "Success - Statistics returned",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error"
        }
    )
    def get(self):
        """Get overall ticket system statistics.
        
        Returns:
            JSON response with statistics
        """
        try:
            result = get_ticket_statistics()
            
            return success_response(result)
            
        except Exception as e:
            logger.error(
                "Failed to get ticket statistics",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "error": str(e)
                    }
                }
            )
            return error_response("Failed to get statistics", "statistics", 500)


# Tag management routes
@admin_tickets_namespace.route("/tags")
class AdminTagList(Resource):
    @admins_only
    @handle_integrity_error
    @admin_tickets_namespace.doc(
        description="Get all ticket tags (Admin only)",
        responses={
            200: "Success - Tags returned",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error"
        }
    )
    def get(self):
        """Get all available tags.
        
        Returns:
            JSON response with list of tags
        """
        try:
            result = list_tags()
            
            return success_response(result)
            
        except Exception as e:
            logger.error(
                "Failed to list tags",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "error": str(e)
                    }
                }
            )
            return error_response("Failed to retrieve tags", "tags", 500)

    @admins_only
    @json_body_required
    @handle_integrity_error
    @admin_tickets_namespace.doc(
        description="Create a new tag (Admin only)",
        responses={
            201: "Success - Tag created",
            400: "Bad request - Invalid data or name exists",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error"
        }
    )
    def post(self):
        """Create a new tag.
        
        Request Body:
            name (str): Tag name (required)
            color (str): Hex color code (optional)
            description (str): Tag description (optional)
            
        Returns:
            JSON response with created tag
        """
        data = g.json_data
        
        # Validate data
        is_valid, errors = validate_tag_creation(data)
        if not is_valid:
            return {"success": False, "errors": errors}, 400
        
        try:
            result = create_tag(
                name=data["name"],
                color=data.get("color"),
                description=data.get("description")
            )
            
            return success_response(result, status_code=201)
            
        except TicketValidationError as e:
            return error_response(str(e), "tag", 400)
        except Exception as e:
            logger.error(
                "Failed to create tag",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "error": str(e)
                    }
                }
            )
            return error_response("Failed to create tag", "tag", 500)


@admin_tickets_namespace.route("/tags/<int:tag_id>")
@admin_tickets_namespace.param("tag_id", "Tag ID")
class AdminTagDetail(Resource):
    @admins_only
    @json_body_required
    @handle_integrity_error
    @admin_tickets_namespace.doc(
        description="Update a tag (Admin only)",
        responses={
            200: "Success - Tag updated",
            400: "Bad request - Invalid data",
            404: "Not found - Tag does not exist",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error"
        }
    )
    def patch(self, tag_id):
        """Update a tag.
        
        Args:
            tag_id (int): The tag to update
            
        Request Body:
            name (str): New name
            color (str): New color
            description (str): New description
            
        Returns:
            JSON response with updated tag
        """
        data = g.json_data
        
        # Validate data
        is_valid, errors = validate_tag_update(data)
        if not is_valid:
            return {"success": False, "errors": errors}, 400
        
        try:
            result = update_tag(
                tag_id=tag_id,
                name=data.get("name"),
                color=data.get("color"),
                description=data.get("description")
            )
            
            return success_response(result)
            
        except TagNotFoundError as e:
            return error_response(str(e), "tag", 404)
        except TicketValidationError as e:
            return error_response(str(e), "tag", 400)
        except Exception as e:
            logger.error(
                "Failed to update tag",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "tag_id": tag_id,
                        "error": str(e)
                    }
                }
            )
            return error_response("Failed to update tag", "tag", 500)

    @admins_only
    @handle_integrity_error
    @admin_tickets_namespace.doc(
        description="Delete a tag (Admin only)",
        responses={
            200: "Success - Tag deleted",
            404: "Not found - Tag does not exist",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error"
        }
    )
    def delete(self, tag_id):
        """Delete a tag.
        
        Args:
            tag_id (int): The tag to delete
            
        Returns:
            JSON response confirming deletion
        """
        try:
            result = delete_tag(tag_id=tag_id)
            
            return success_response(result)
            
        except TagNotFoundError as e:
            return error_response(str(e), "tag", 404)
        except Exception as e:
            logger.error(
                "Failed to delete tag",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "tag_id": tag_id,
                        "error": str(e)
                    }
                }
            )
            return error_response("Failed to delete tag", "tag", 500)


@admin_tickets_namespace.route("/tickets/<int:ticket_id>/tags")
@admin_tickets_namespace.param("ticket_id", "Ticket ID")
class AdminTicketTags(Resource):
    @admins_only
    @json_body_required
    @handle_integrity_error
    @admin_tickets_namespace.doc(
        description="Add tags to a ticket (Admin only)",
        responses={
            200: "Success - Tags added",
            400: "Bad request - Invalid data",
            404: "Not found - Ticket or tags not found",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error"
        }
    )
    def post(self, ticket_id):
        """Add tags to a ticket.
        
        Args:
            ticket_id (int): The ticket to add tags to
            
        Request Body:
            tag_ids (list[int]): List of tag IDs to add
            
        Returns:
            JSON response with updated ticket
        """
        data = g.json_data
        
        if "tag_ids" not in data or not isinstance(data["tag_ids"], list):
            return error_response("tag_ids must be a list", "tag_ids", 400)
        
        try:
            result = add_tags_to_ticket(
                ticket_id=ticket_id,
                tag_ids=data["tag_ids"]
            )
            
            return success_response(result)
            
        except TicketNotFoundError as e:
            return error_response(str(e), "ticket", 404)
        except TagNotFoundError as e:
            return error_response(str(e), "tag", 404)
        except Exception as e:
            logger.error(
                "Failed to add tags to ticket",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "ticket_id": ticket_id,
                        "error": str(e)
                    }
                }
            )
            return error_response("Failed to add tags", "tags", 500)

    @admins_only
    @json_body_required
    @handle_integrity_error
    @admin_tickets_namespace.doc(
        description="Remove tags from a ticket (Admin only)",
        responses={
            200: "Success - Tags removed",
            400: "Bad request - Invalid data",
            404: "Not found - Ticket or tags not found",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error"
        }
    )
    def delete(self, ticket_id):
        """Remove tags from a ticket.
        
        Args:
            ticket_id (int): The ticket to remove tags from
            
        Request Body:
            tag_ids (list[int]): List of tag IDs to remove
            
        Returns:
            JSON response with updated ticket
        """
        data = g.json_data
        
        if "tag_ids" not in data or not isinstance(data["tag_ids"], list):
            return error_response("tag_ids must be a list", "tag_ids", 400)
        
        try:
            result = remove_tags_from_ticket(
                ticket_id=ticket_id,
                tag_ids=data["tag_ids"]
            )
            
            return success_response(result)
            
        except TicketNotFoundError as e:
            return error_response(str(e), "ticket", 404)
        except TagNotFoundError as e:
            return error_response(str(e), "tag", 404)
        except Exception as e:
            logger.error(
                "Failed to remove tags from ticket",
                extra={
                    "context": {
                        "admin_id": get_current_user_id(),
                        "ticket_id": ticket_id,
                        "error": str(e)
                    }
                }
            )
            return error_response("Failed to remove tags", "tags", 500)
