"""
User API routes for support tickets
"""

from flask import request
from flask_restx import Namespace, Resource

from ...core.middleware import user_endpoint, check_ownership, check_attachment_ownership
from ...core.middleware.loaders import LoaderType, load_ticket, load_attachment
from ...core.utils import success_response, error_response
from ...user.models import User

from ..controllers import (
    create_ticket,
    close_my_ticket,
    list_tickets,
    get_ticket,
    create_ticket_message,
    download_attachment,
    upload_attachment,
)


support_user_namespace = Namespace("support", description="Support ticket operations for users")




@support_user_namespace.route("/tickets/create")
class Tickets(Resource):
    @user_endpoint(json_required=True)
    @support_user_namespace.doc(
        description="Create a new support ticket with initial message. Team ID is automatically derived from the user and event.",
        params={
            "subject": {
                "description": "Ticket subject line (128 character max length)",
                "required": True,
                "type": "string",
                "example": "Can't access my team dashboard"
            },
            "text": {
                "description": "Initial message text",
                "in": "body",
                "required": True,
                "type": "string",
                "example": "I'm getting a 404 error when trying to access the team dashboard. Can you help?"
            },
            "event_id": {
                "description": "Event ID to associate ticket with",
                "required": False,
                "type": "integer",
                "example": 1
            },
            "challenge_id": {
                "description": "Challenge ID to associate ticket with",
                "required": False,
                "type": "integer",
                "example": 15
            }
        },
        responses={
            201: "Success - Ticket created with initial message",
            400: "Bad request - Missing required fields (subject, text) or invalid associations, or user not in team for event",
            401: "Unauthorized - Authentication required",
            404: "Not found - Event, team, or challenge association not found",
            500: "Internal Server Error",
        },
    )
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
    @user_endpoint()
    @support_user_namespace.doc(
        description="Get all support tickets created by the current user with optional status filter.",
        params={
            "status": {
                "description": "Filter by ticket status. Options: 'all', 'open', 'closed'. Default: 'all'",
                "required": False,
                "type": "string",
                "example": "open"
            }
        },
        responses={
            200: "Success - Returns list of user's tickets",
            400: "Bad request - Invalid status filter (must be: all, open, closed)",
            401: "Unauthorized - Authentication required",
            500: "Internal Server Error",
        },
    )
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
    @user_endpoint()
    @load_ticket(LoaderType.PARAM)
    @check_ownership(resource_key="ticket", user_field="author_id")
    @support_user_namespace.doc(
        description="Get a specific ticket with all messages (user must own the ticket)",
        params={
            "ticket_id": {
                "description": "Ticket ID",
                "required": True,
                "type": "integer",
                "example": 123
            }
        },
        responses={
            200: "Success - Returns ticket details and message thread",
            401: "Unauthorized - Authentication required",
            403: "Forbidden - You can only access your own tickets",
            404: "Not found - Ticket does not exist",
            500: "Internal Server Error",
        },
    )
    def get(self, ticket_id: int, ticket, current_user: User, **kwargs):
        """
        Get ticket details with all messages
        """
        result = get_ticket(ticket=ticket)

        return success_response(result)

@support_user_namespace.route("/me/tickets/<int:ticket_id>/add_message")
class TicketMessage(Resource):
    @user_endpoint(json_required=True)
    @load_ticket(LoaderType.PARAM)
    @check_ownership(resource_key="ticket", user_field="author_id")
    @support_user_namespace.doc(
        description="Add a new message to an existing support ticket thread",
        params={
            "ticket_id": {
                "description": "Ticket ID",
                "required": True,
                "type": "integer",
                "example": 123
            },
            "text": {
                "description": "Message content (4096 character max length)",
                "in": "body",
                "required": True,
                "type": "string",
                "example": "Thanks for the quick response! That solved my issue."
            }
        },
        responses={
            201: "Success - Message added to ticket thread",
            400: "Bad request - Missing message text",
            401: "Unauthorized - Authentication required",
            403: "Forbidden - You can only message on your own tickets",
            404: "Not found - Ticket does not exist",
            500: "Internal Server Error",
        },
    )
    def post(self, ticket_id: int, ticket, current_user: User, json_data, **kwargs):
        """
        Add a new message to the ticket
        """
        message = create_ticket_message(
            text=json_data.get("text"),
            author_id=current_user.id,
            ticket=ticket,
            is_admin=False,
        )
        return success_response(message, status_code=201)


@support_user_namespace.route("/me/tickets/<int:ticket_id>/close")
class CloseMyTicket(Resource):
    @user_endpoint()
    @load_ticket(LoaderType.PARAM)
    @check_ownership(resource_key="ticket", user_field="author_id")
    @support_user_namespace.doc(
        description="Close a support ticket (user must own the ticket)",
        params={
            "ticket_id": {
                "description": "Ticket ID",
                "required": True,
                "type": "integer",
                "example": 123
            }
        },
        responses={
            200: "Success - Ticket closed",
            400: "Bad request - Ticket is already closed",
            401: "Unauthorized - Authentication required",
            403: "Forbidden - You can only close your own tickets",
            404: "Not found - Ticket does not exist",
            500: "Internal Server Error",
        },
    )
    def post(self, ticket_id: int, ticket, current_user: User, **kwargs):
        """
        Close user's own ticket
        """
        closed_ticket = close_my_ticket(
            ticket=ticket,
            current_user=current_user,
        )

        return success_response(closed_ticket)


@support_user_namespace.route("/me/tickets/<int:ticket_id>/upload")
class AttachmentUpload(Resource):
    @user_endpoint()
    @load_ticket(LoaderType.PARAM)
    @check_ownership(resource_key="ticket", user_field="author_id")
    @support_user_namespace.doc(
        description="Upload an image attachment to your support ticket",
        params={
            "ticket_id": {
                "description": "ID of the ticket to attach the image to",
                "required": True,
                "type": "integer",
                "in": "path",
                "example": 123
            },
            "file": {
                "description": "Image file to upload (PNG, JPEG, JPG, WebP formats supported, max 5MB)",
                "in": "formData",
                "required": True,
                "type": "file"
            }
        },
        responses={
            200: "Success - Image uploaded and attachment created",
            400: "Bad request - No file provided, invalid format, or file too large",
            401: "Unauthorized - Authentication required",
            403: "Forbidden - You can only upload to your own tickets",
            404: "Not found - Ticket does not exist",
            500: "Internal Server Error - Upload failed",
        },
        consumes=['multipart/form-data']
    )
    def post(self, ticket_id: int, ticket, current_user: User, **kwargs):
        """
        Upload image to ticket
        """
        if 'file' not in request.files:
            return error_response("No file provided", "file", 400)

        file = request.files['file']

        attachment = upload_attachment(
            file=file,
            ticket=ticket,
            uploaded_by=current_user.id,
        )

        return success_response(attachment)

@support_user_namespace.route("/me/attachments/<int:attachment_id>")
class AttachmentDownload(Resource):
    @user_endpoint()
    @load_attachment(LoaderType.PARAM)
    @check_attachment_ownership()
    @support_user_namespace.doc(
        description="Download an attachment from user support ticket via presigned S3 URL redirect",
        params={
            "attachment_id": {
                "description": "ID of the attachment to download",
                "required": True,
                "type": "integer",
                "in": "path",
                "example": 123
            }
        },
        responses={
            302: "Success - Redirect to presigned S3 URL for secure download (1 hour expiration)",
            401: "Unauthorized - Authentication required",
            403: "Forbidden - You can only download attachments from your own tickets",
            404: "Not found - Attachment does not exist or file missing in S3 storage",
            500: "Internal Server Error - Failed to generate presigned URL",
            503: "Service Unavailable - S3 storage not configured",
        }
    )
    def get(self, attachment_id: int, attachment, current_user: User, **kwargs):
        """
        Download attachment via presigned URL redirect
        """
        return download_attachment(attachment=attachment)