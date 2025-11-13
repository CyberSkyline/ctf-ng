"""
Admin API routes for support tickets
"""

from flask import request
from flask_restx import Namespace, Resource

from ... import config
from ...core.middleware import admin_endpoint
from ...core.middleware.loaders import (
    LoaderType,
    load_ticket,
    load_ticket_tag,
    load_user,
    load_attachment,
)
from ...core.utils import success_response, error_response
from ...user.models import User

from ..controllers import (
    create_tag,
    update_tag,
    list_tags,
    set_ticket_tags,
    assign_ticket,
    unassign_ticket,
    update_ticket_status,
    update_ticket_mute,
    set_ticket_event,
    remove_ticket_event,
    set_ticket_challenge,
    remove_ticket_challenge,
    list_tickets,
    get_ticket,
    create_ticket_message,
    upload_ticket_attachment,
    download_attachment,
)


support_admin_namespace = Namespace("admin/support", description="Admin support ticket operations")


@support_admin_namespace.route("/tickets")
class AdminTickets(Resource):
    @admin_endpoint()
    @support_admin_namespace.doc(
        description="Get all support tickets with optional filters and enriched names (Admin only). Returns tickets with author_name, assigned_to_name, event_name, team_name, challenge_name, and full tag objects (with id, name, color).",
        params={
            "user_id": {
                "description": "Filter by ticket author ID",
                "required": False,
                "type": "integer",
                "example": 123
            },
            "status": {
                "description": "Filter by ticket status. Options: 'all', 'open', 'closed'. Default: 'all'",
                "required": False,
                "type": "string",
                "example": "open"
            },
            "assigned_to": {
                "description": "Filter by assigned user ID",
                "required": False,
                "type": "integer",
                "example": 456
            },
            "event_id": {
                "description": "Filter by event ID",
                "required": False,
                "type": "integer",
                "example": 1
            },
            "team_id": {
                "description": "Filter by team ID",
                "required": False,
                "type": "integer",
                "example": 42
            }
        },
        returns={
            200: "Success - Returns filtered list of tickets",
            400: "Bad request - Invalid filter parameters",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error",
        },
    )
    def get(self, current_user: User, **kwargs):
        """
        Get all tickets with optional filters
        """
        user_id = request.args.get("user_id", type = int)
        status = request.args.get("status", "all")
        assigned_to = request.args.get("assigned_to", type = int)
        event_id = request.args.get("event_id", type = int)
        team_id = request.args.get("team_id", type = int)

        tickets = list_tickets(
            user_id = user_id,
            status = status,
            assigned_to = assigned_to,
            event_id = event_id,
            team_id = team_id,
            is_admin = True,
        )

        return success_response(tickets)


@support_admin_namespace.route("/tickets/<int:ticket_id>")
class AdminTicket(Resource):
    @admin_endpoint()
    @load_ticket(LoaderType.PARAM)
    @support_admin_namespace.doc(
        description="Get any support ticket with all messages and full tag objects (Admin only)",
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
            403: "Forbidden - Admin access required",
            404: "Not found - Ticket does not exist",
            500: "Internal Server Error",
        },
    )
    def get(self, ticket_id: int, ticket, current_user: User, **kwargs):
        """
        Get any ticket with all messages
        """
        result = get_ticket(ticket=ticket)
        return success_response(result)


@support_admin_namespace.route("/tickets/<int:ticket_id>/add_message")
class AdminTicketMessage(Resource):
    @admin_endpoint(json_required=True)
    @load_ticket(LoaderType.PARAM)
    @support_admin_namespace.doc(
        description="Add admin message to any ticket (reopens closed tickets) (Admin only)",
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
                "example": "Hi there! I've reviewed your issue and here's the solution..."
            }
        },
        responses={
            201: "Success - Message added and ticket reopened if necessary",
            400: "Bad request - Missing message text",
            403: "Forbidden - Admin access required",
            404: "Not found - Ticket does not exist",
            500: "Internal Server Error",
        },
    )
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
    @admin_endpoint(json_required=True)
    @load_ticket(LoaderType.PARAM)
    @support_admin_namespace.doc(
        description="Set tags on a ticket (replaces all existing tags) (Admin only). Returns ticket with full tag objects containing id, name, and color.",
        params={
            "ticket_id": {
                "description": "Ticket ID",
                "required": True,
                "type": "integer",
                "example": 123
            },
            "tag_ids": {
                "description": "Array of tag IDs to assign (empty array to clear all tags)",
                "in": "body",
                "required": True,
                "type": "array",
                "example": [1, 3, 5]
            }
        },
        responses={
            200: "Success - Tags updated",
            400: "Bad request - Invalid tag_ids array",
            403: "Forbidden - Admin access required",
            404: "Not found - Ticket or tag IDs not found",
            500: "Internal Server Error",
        },
    )
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
    @admin_endpoint(json_required=True)
    @load_ticket(LoaderType.PARAM)
    @load_user(source=LoaderType.BODY)
    @support_admin_namespace.doc(
        description="Assign ticket to a user (Admin only)",
        params={
            "ticket_id": {
                "description": "Ticket ID",
                "required": True,
                "type": "integer",
                "example": 123
            },
            "user_id": {
                "description": "User ID to assign the ticket to",
                "in": "body",
                "required": True,
                "type": "integer",
                "example": 456
            }
        },
        responses={
            200: "Success - Assignment updated",
            400: "Bad request - Invalid user_id or already assigned",
            403: "Forbidden - Admin access required",
            404: "Not found - Ticket or user not found",
            500: "Internal Server Error",
        },
    )
    def put(self, ticket_id: int, ticket, user, current_user: User, json_data, **kwargs):
        """
        Assign ticket to a user
        """
        updated_ticket = assign_ticket(
            user=user,
            ticket=ticket,
        )
        return success_response(updated_ticket)


@support_admin_namespace.route("/tickets/<int:ticket_id>/unassign")
class AdminTicketUnassignment(Resource):
    @admin_endpoint(json_required=True)
    @load_ticket(LoaderType.PARAM)
    @support_admin_namespace.doc(
        description="Unassign a ticket from any user (Admin only)",
        params={
            "ticket_id": {
                "description": "Ticket ID",
                "required": True,
                "type": "integer",
                "example": 123
            }
        },
        responses={
            200: "Success - Ticket unassigned",
            403: "Forbidden - Admin access required",
            404: "Not found - Ticket does not exist",
            500: "Internal Server Error",
        },
    )
    def put(self, ticket_id: int, ticket, current_user: User, json_data, **kwargs):
        """
        Unassign ticket from any user (admin only)
        """
        updated_ticket = unassign_ticket(
            ticket=ticket,
        )
        return success_response(updated_ticket)


@support_admin_namespace.route("/tickets/<int:ticket_id>/close")
class AdminTicketStatus(Resource):
    @admin_endpoint(json_required=True)
    @load_ticket(LoaderType.PARAM)
    @support_admin_namespace.doc(
        description="Toggle ticket open/closed status (Admin only)",
        params={
            "ticket_id": {
                "description": "Ticket ID",
                "required": True,
                "type": "integer",
                "example": 123
            },
            "closed": {
                "description": "Whether to close the ticket",
                "required": True,
                "type": "boolean",
                "example": True
            }
        },
        responses={
            200: "Success - Status updated",
            400: "Bad request - Missing or invalid closed boolean",
            403: "Forbidden - Admin access required",
            404: "Not found - Ticket does not exist",
            500: "Internal Server Error",
        },
    )
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
    @admin_endpoint(json_required=True)
    @load_ticket(LoaderType.PARAM)
    @support_admin_namespace.doc(
        description="Toggle ticket mute status (Admin only)",
        params={
            "ticket_id": {
                "description": "Ticket ID",
                "required": True,
                "type": "integer",
                "example": 123
            },
            "muted": {
                "description": "Whether to mute the ticket",
                "required": True,
                "type": "boolean",
                "example": True
            }
        },
        responses={
            200: "Success - Mute status updated",
            400: "Bad request - Missing or invalid muted boolean",
            403: "Forbidden - Admin access required",
            404: "Not found - Ticket does not exist",
            500: "Internal Server Error",
        },
    )
    def put(self, ticket_id: int, ticket, current_user: User, json_data, **kwargs):
        """
        Toggle ticket mute status
        """
        updated_ticket = update_ticket_mute(
            muted=json_data.get("muted", False),
            ticket=ticket,
        )

        return success_response(updated_ticket)


@support_admin_namespace.route("/tickets/<int:ticket_id>/event")
class AdminTicketEvent(Resource):
    @admin_endpoint(json_required=True)
    @load_ticket(LoaderType.PARAM)
    @support_admin_namespace.doc(
        description="Set ticket's event and team association (Admin only). Team ID is automatically derived from the ticket author's team in the event.",
        params={
            "ticket_id": {
                "description": "Ticket ID",
                "required": True,
                "type": "integer",
                "example": 123
            },
            "event_id": {
                "description": "Event ID to associate with ticket",
                "required": True,
                "type": "integer",
                "example": 1
            }
        },
        responses={
            200: "Success - Event/team association updated",
            400: "Bad request - Invalid event_id",
            403: "Forbidden - Admin access required",
            404: "Not found - Ticket or event not found",
            500: "Internal Server Error",
        },
    )
    def put(self, ticket_id: int, ticket, current_user: User, json_data, **kwargs):
        """
        Set ticket event/team association
        """
        updated_ticket = set_ticket_event(
            event_id=json_data.get("event_id"),
            ticket=ticket,
        )
        return success_response(updated_ticket)


@support_admin_namespace.route("/tickets/<int:ticket_id>/event/remove")
class AdminTicketEventRemove(Resource):
    @admin_endpoint(json_required=True)
    @load_ticket(LoaderType.PARAM)
    @support_admin_namespace.doc(
        description="Remove ticket's event, team, and challenge association (Admin only). Since challenges must belong to events, removing the event also removes any challenge association to prevent data inconsistency.",
        params={
            "ticket_id": {
                "description": "Ticket ID",
                "required": True,
                "type": "integer",
                "example": 123
            }
        },
        responses={
            200: "Success - Event/team/challenge associations removed",
            403: "Forbidden - Admin access required",
            404: "Not found - Ticket does not exist",
            500: "Internal Server Error",
        },
    )
    def put(self, ticket_id: int, ticket, current_user: User, json_data, **kwargs):
        """
        Remove ticket event/team association
        """
        updated_ticket = remove_ticket_event(
            ticket=ticket,
        )
        return success_response(updated_ticket)


@support_admin_namespace.route("/tickets/<int:ticket_id>/challenge")
class AdminTicketChallenge(Resource):
    @admin_endpoint(json_required=True)
    @load_ticket(LoaderType.PARAM)
    @support_admin_namespace.doc(
        description="Set ticket's challenge association (Admin only)",
        params={
            "ticket_id": {
                "description": "Ticket ID",
                "required": True,
                "type": "integer",
                "example": 123
            },
            "challenge_id": {
                "description": "Challenge ID to associate with ticket",
                "required": True,
                "type": "integer",
                "example": 15
            }
        },
        responses={
            200: "Success - Challenge association updated",
            400: "Bad request - Invalid challenge_id",
            403: "Forbidden - Admin access required",
            404: "Not found - Ticket or challenge not found",
            500: "Internal Server Error",
        },
    )
    def put(self, ticket_id: int, ticket, current_user: User, json_data, **kwargs):
        """
        Set ticket challenge association
        """
        updated_ticket = set_ticket_challenge(
            challenge_id=json_data.get("challenge_id"),
            ticket=ticket,
        )
        return success_response(updated_ticket)


@support_admin_namespace.route("/tickets/<int:ticket_id>/challenge/remove")
class AdminTicketChallengeRemove(Resource):
    @admin_endpoint(json_required=True)
    @load_ticket(LoaderType.PARAM)
    @support_admin_namespace.doc(
        description="Remove ticket's challenge association (Admin only)",
        params={
            "ticket_id": {
                "description": "Ticket ID",
                "required": True,
                "type": "integer",
                "example": 123
            }
        },
        responses={
            200: "Success - Challenge association removed",
            403: "Forbidden - Admin access required",
            404: "Not found - Ticket does not exist",
            500: "Internal Server Error",
        },
    )
    def put(self, ticket_id: int, ticket, current_user: User, json_data, **kwargs):
        """
        Remove ticket challenge association
        """
        updated_ticket = remove_ticket_challenge(
            ticket=ticket,
        )
        return success_response(updated_ticket)


@support_admin_namespace.route("/tags")
class AdminTags(Resource):
    @admin_endpoint()
    @support_admin_namespace.doc(
        description="Get all available support ticket tags (Admin only)",
        responses={
            200: "Success - Returns list of all tags ordered by name",
            403: "Forbidden - Admin access required",
            500: "Internal Server Error",
        },
    )
    def get(self, current_user: User, **kwargs):
        """
        Get all ticket tags
        """
        tags = list_tags()
        return success_response(tags)

    @admin_endpoint(json_required=True)
    @support_admin_namespace.doc(
        description="Create a new support ticket tag (Admin only)",
        params={
            "name": {
                "description": "Tag name (50 character max length, must be unique)",
                "in": "body",
                "required": True,
                "type": "string",
                "example": "urgent"
            },
            "color": {
                "description": "Tag color (hex color code e.g #FFFFFF)",
                "in": "body",
                "required": False,
                "type": "string",
                "example": "#FF4444"
            },
            "description": {
                "description": "Tag description (200 character max length)",
                "in": "body",
                "required": False,
                "type": "string",
                "example": "High priority tickets that need immediate attention"
            }
        },
        responses={
            201: "Success - Tag created",
            400: "Bad request - Missing name or invalid color format",
            403: "Forbidden - Admin access required",
            409: "Conflict - Tag name already exists",
            500: "Internal Server Error",
        },
    )
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
    @admin_endpoint(json_required=True)
    @load_ticket_tag(LoaderType.PARAM)
    @support_admin_namespace.doc(
        description="Update an existing support ticket tag (Admin only)",
        params={
            "ticket_tag_id": {
                "description": "Tag ID",
                "required": True,
                "type": "integer",
                "example": 1
            },
            "name": {
                "description": "Tag name (50 character max length)",
                "in": "body",
                "required": False,
                "type": "string",
                "example": "high-priority"
            },
            "color": {
                "description": "Tag color (hex color code e.g #FF0000)",
                "in": "body",
                "required": False,
                "type": "string",
                "example": "#FF0000"
            },
            "description": {
                "description": "Tag description (200 character max length)",
                "in": "body",
                "required": False,
                "type": "string",
                "example": "Updated description for high priority tickets"
            }
        },
        responses={
            200: "Success - Tag updated",
            400: "Bad request - Invalid name or color format",
            403: "Forbidden - Admin access required",
            404: "Not found - Tag does not exist",
            409: "Conflict - Tag name already exists",
            500: "Internal Server Error",
        },
    )
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


@support_admin_namespace.route("/tickets/<int:ticket_id>/upload_image")
class AdminTicketImageUpload(Resource):
    @admin_endpoint()
    @load_ticket(LoaderType.PARAM)
    @support_admin_namespace.doc(
        description="Upload an image to any support ticket (Admin only, WebP only, max 5MB)",
        params={
            "ticket_id": {
                "description": "Ticket ID",
                "required": True,
                "type": "integer",
                "example": 123
            },
            "file": {
                "description": "Image file (WebP format, max 5MB)",
                "in": "formData",
                "required": True,
                "type": "file"
            }
        },
        responses={
            200: "Success - Image uploaded, returns image_url",
            400: "Bad request - Invalid file type or size",
            403: "Forbidden - Admin access required",
            404: "Not found - Ticket does not exist",
            500: "Internal Server Error",
        },
    )
    def post(self, ticket_id: int, ticket, current_user: User, **kwargs):
        """
        Upload image to any ticket (admin)
        """
        if 'file' not in request.files:
            return error_response("No file provided", "file", 400)

        file = request.files['file']

        attachment = upload_ticket_attachment(
            file=file,
            ticket=ticket,
            uploaded_by=current_user.id,
        )

        return success_response(attachment)


@support_admin_namespace.route("/attachments/<int:attachment_id>")
class AdminAttachmentDownload(Resource):
    @admin_endpoint()
    @load_attachment(LoaderType.PARAM)
    @support_admin_namespace.doc(
        description="Download any support ticket attachment",
        params={
            "attachment_id": {
                "description": "Attachment ID",
                "required": True,
                "type": "integer",
                "example": 123
            }
        },
        responses={
            200: "Success - File streamed from S3",
            403: "Forbidden - Admin access required",
            404: "Not found - Attachment does not exist or file missing in storage",
            500: "Internal Server Error",
        },
    )
    def get(self, attachment_id: int, attachment, current_user: User, **kwargs):
        """
        Download any attachment (admin access)
        """
        return download_attachment(attachment=attachment)

