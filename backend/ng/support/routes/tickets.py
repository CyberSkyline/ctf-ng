"""
/backend/ng/support/routes/tickets.py
User-facing API routes for support ticket operations.
"""

from flask import request, g
from flask_restx import Namespace, Resource
from CTFd.utils.decorators import authed_only

from ..controllers import (
    create_ticket,
    list_tickets,
    get_ticket,
    create_ticket_message,
    update_ticket
)
from ..exceptions import (
    TicketNotFoundError,
    TicketPermissionError,
    TicketValidationError,
    TicketOperationError,
    TagNotFoundError
)
from ..validators import (
    validate_ticket_creation,
    validate_ticket_message,
    validate_ticket_update,
    validate_ticket_filters
)
from ...core.utils.api_responses import success_response, error_response
from ...core.utils.logger import get_logger
from ...core.utils import get_current_user_id
from ...core.middleware import authed_user_required, handle_integrity_error, json_body_required

tickets_namespace = Namespace("tickets", description="support ticket operations")
logger = get_logger(__name__)


@tickets_namespace.route("")
class TicketList(Resource):
    @authed_only
    @authed_user_required
    @handle_integrity_error
    @tickets_namespace.doc(
        description="Get user's own support tickets",
        responses={
            200: "Success - Returns list of user's tickets",
            403: "Forbidden - User not authenticated",
            500: "Internal Server Error"
        }
    )
    def get(self):
        """Get current user's support tickets.
        
        Query Parameters:
            status: Filter by status (open, closed, muted, all)
            
        Returns:
            JSON response with list of user's tickets
        """
        # Get filter parameters
        filters = {
            "status": request.args.get("status", "all")
        }
        
        # Validate filters
        is_valid, errors = validate_ticket_filters(filters)
        if not is_valid:
            return {"success": False, "errors": errors}, 400
        
        try:
            result = list_tickets(
                user_id=g.user.id,
                status=filters["status"],
                is_admin=False
            )
            
            return success_response(result)
            
        except Exception as e:
            logger.error(
                "Failed to list user tickets",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "error": str(e)
                    }
                }
            )
            return error_response("Failed to retrieve tickets", "tickets", 500)

    @authed_only
    @authed_user_required
    @json_body_required
    @handle_integrity_error
    @tickets_namespace.doc(
        description="Create a new support ticket",
        responses={
            201: "Success - Ticket created",
            400: "Bad request - Invalid data",
            403: "Forbidden - User not authenticated",
            500: "Internal Server Error"
        }
    )
    def post(self):
        """Create a new support ticket.
        
        Request Body:
            subject (str): Ticket subject (required)
            event_id (int): Optional event association
            team_id (int): Optional team association
            challenge_id (int): Optional challenge association
            tag_ids (list[int]): Optional list of tag IDs
            
        Returns:
            JSON response with created ticket info
        """
        data = g.json_data
        
        # Validate data
        is_valid, errors = validate_ticket_creation(data)
        if not is_valid:
            logger.warning(
                "Validation failed for ticket creation",
                extra={
                    "context": {
                        "errors": errors,
                        "user_id": get_current_user_id()
                    }
                }
            )
            return {"success": False, "errors": errors}, 400
        
        try:
            result = create_ticket(
                subject=data["subject"],
                author_id=g.user.id,
                event_id=data.get("event_id"),
                team_id=data.get("team_id"),
                challenge_id=data.get("challenge_id"),
                tag_ids=data.get("tag_ids")
            )
            
            return success_response(result, status_code=201)
            
        except (TicketValidationError, TagNotFoundError) as e:
            return error_response(str(e), "ticket", 400)
        except Exception as e:
            logger.error(
                "Failed to create ticket",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "error": str(e)
                    }
                }
            )
            return error_response("Failed to create ticket", "ticket", 500)


@tickets_namespace.route("/<int:ticket_id>")
@tickets_namespace.param("ticket_id", "Ticket ID")
class TicketDetail(Resource):
    @authed_only
    @authed_user_required
    @handle_integrity_error
    @tickets_namespace.doc(
        description="Get detailed information about a specific ticket",
        responses={
            200: "Success - Ticket details returned",
            403: "Forbidden - No permission to view ticket",
            404: "Not found - Ticket does not exist",
            500: "Internal Server Error"
        }
    )
    def get(self, ticket_id):
        """Get detailed info about a ticket.
        
        Args:
            ticket_id (int): The ticket ID to get
            
        Returns:
            JSON response with ticket details and messages
        """
        try:
            result = get_ticket(
                ticket_id=ticket_id,
                user_id=g.user.id,
                is_admin=False
            )
            
            return success_response(result)
            
        except TicketNotFoundError as e:
            return error_response(str(e), "ticket", 404)
        except TicketPermissionError as e:
            return error_response(str(e), "ticket", 403)
        except Exception as e:
            logger.error(
                "Failed to get ticket",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "ticket_id": ticket_id,
                        "error": str(e)
                    }
                }
            )
            return error_response("Failed to retrieve ticket", "ticket", 500)

    @authed_only
    @authed_user_required
    @json_body_required
    @handle_integrity_error
    @tickets_namespace.doc(
        description="Update ticket information (limited fields for users)",
        responses={
            200: "Success - Ticket updated",
            400: "Bad request - Invalid data",
            403: "Forbidden - No permission to update ticket",
            404: "Not found - Ticket does not exist",
            500: "Internal Server Error"
        }
    )
    def patch(self, ticket_id):
        """Update ticket info (users can only update subject).
        
        Args:
            ticket_id (int): The ticket ID to update
            
        Request Body:
            subject (str): New ticket subject
            
        Returns:
            JSON response with updated ticket info
        """
        data = g.json_data
        
        # Validate data
        is_valid, errors = validate_ticket_update(data)
        if not is_valid:
            return {"success": False, "errors": errors}, 400
        
        try:
            result = update_ticket(
                ticket_id=ticket_id,
                actor_id=g.user.id,
                is_admin=False,
                subject=data.get("subject")
            )
            
            return success_response(result)
            
        except TicketNotFoundError as e:
            return error_response(str(e), "ticket", 404)
        except TicketPermissionError as e:
            return error_response(str(e), "ticket", 403)
        except Exception as e:
            logger.error(
                "Failed to update ticket",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "ticket_id": ticket_id,
                        "error": str(e)
                    }
                }
            )
            return error_response("Failed to update ticket", "ticket", 500)


@tickets_namespace.route("/<int:ticket_id>/messages")
@tickets_namespace.param("ticket_id", "Ticket ID")
class TicketMessages(Resource):
    @authed_only
    @authed_user_required
    @json_body_required
    @handle_integrity_error
    @tickets_namespace.doc(
        description="Reply to a support ticket",
        responses={
            201: "Success - Message created",
            400: "Bad request - Invalid data",
            403: "Forbidden - No permission to reply",
            404: "Not found - Ticket does not exist",
            500: "Internal Server Error"
        }
    )
    def post(self, ticket_id):
        """Add a reply to the ticket.
        
        Args:
            ticket_id (int): The ticket to reply to
            
        Request Body:
            text (str): Message content (markdown supported)
            
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
                author_id=g.user.id,
                is_admin=False
            )
            
            return success_response(result, status_code=201)
            
        except TicketNotFoundError as e:
            return error_response(str(e), "ticket", 404)
        except TicketPermissionError as e:
            return error_response(str(e), "ticket", 403)
        except TicketOperationError as e:
            return error_response(str(e), "ticket", 400)
        except Exception as e:
            logger.error(
                "Failed to create ticket message",
                extra={
                    "context": {
                        "user_id": get_current_user_id(),
                        "ticket_id": ticket_id,
                        "error": str(e)
                    }
                }
            )
            return error_response("Failed to create message", "message", 500)
