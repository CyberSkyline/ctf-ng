"""
Support Ticket RESTX Documentation
"""

# ============ COMMON RESPONSES ============
COMMON_RESPONSES = {
    200: "Success - Operation completed successfully",
    201: "Success - Resource created successfully",
    400: "Bad request - Invalid data or validation failed",
    401: "Unauthorized - Authentication required",
    403: "Forbidden - Insufficient permissions",
    404: "Not found - Resource does not exist",
    409: "Conflict - Resource already exists",
    500: "Internal server error",
}

AUTH_REQUIRED_RESPONSES = {
    401: COMMON_RESPONSES[401],
    500: COMMON_RESPONSES[500],
}

ADMIN_REQUIRED_RESPONSES = {
    403: "Forbidden - Admin access required",
    500: COMMON_RESPONSES[500],
}

# ============ USER SUPPORT ENDPOINTS ============
CREATE_TICKET_DOC = {
    "description": "Create a new support ticket with initial message",
    "params": {
        "subject": "Ticket subject line (128 character max length)",
        "text": "Initial message text",
        "event_id": "Event ID to associate ticket with",
        "team_id": "Team ID to associate ticket with",
        "challenge_id": "Challenge ID to associate ticket with"
    },
    "responses": {
        201:
        "Success - Ticket created with initial message",
        400:
        "Bad request - Missing required fields (subject, text) or invalid associations",
        **AUTH_REQUIRED_RESPONSES,
        404:
        "Not found - Event, team, or challenge association not found",
    },
}

LIST_MY_TICKETS_DOC = {
    "description":
    """
    Get all support tickets created by the current user with optional status filter.

    Note: This endpoint requires a JSON request body.
    Swagger UI does not support parameter testing for GET requests that require JSON request bodies.

    Request Body (JSON):
    - 'status' (optional, string): Filter by ticket status. Options: 'all', 'open', 'closed'. Default: 'all'

    Manual Testing:

    curl -X GET '/ng/support/me/tickets' \\
      -H 'Content-Type: application/json' \\
      -d '{"status": "open"}'

    """,
    "responses": {
        200: "Success - Returns list of user's tickets",
        400: "Bad request - Invalid status filter (must be: all, open, closed)",
        **AUTH_REQUIRED_RESPONSES,
    },
}

GET_MY_TICKET_DOC = {
    "description":
    "Get a specific ticket with all messages (user must own the ticket)",
    "params": {
        "ticket_id": "Ticket ID"
    },
    "responses": {
        200: "Success - Returns ticket details and message thread",
        **AUTH_REQUIRED_RESPONSES,
        403: "Forbidden - You can only access your own tickets",
        404: "Not found - Ticket does not exist",
    },
}

ADD_MESSAGE_DOC = {
    "description": "Add a new message to an existing support ticket thread",
    "params": {
        "ticket_id": "Ticket ID",
        "text": "Message content (4096 character max length)"
    },
    "responses": {
        201: "Success - Message added to ticket thread",
        400: "Bad request - Missing message text",
        **AUTH_REQUIRED_RESPONSES,
        403: "Forbidden - You can only message on your own tickets",
        404: "Not found - Ticket does not exist",
    },
}

CLOSE_MY_TICKET_DOC = {
    "description": "Close a support ticket (user must own the ticket)",
    "params": {
        "ticket_id": "Ticket ID"
    },
    "responses": {
        200: "Success - Ticket closed",
        400: "Bad request - Ticket is already closed",
        **AUTH_REQUIRED_RESPONSES,
        403: "Forbidden - You can only close your own tickets",
        404: "Not found - Ticket does not exist",
    },
}

# ============ ADMIN SUPPORT ENDPOINTS ============
LIST_TICKETS_DOC = {
    "description": """Get all support tickets with optional filters (Admin only).

    Note: This endpoint requires a JSON request body.
    Swagger UI does not support interactive parameter testing for GET requests that require JSON request bodies.

    Request Body (JSON):
    - `user_id` (optional, int): Filter by ticket author ID
    - `status` (optional, str): Filter by ticket status. Options: 'all', 'open', 'closed'. Default: 'all'
    - `assigned_to` (optional, int): Filter by assigned user ID
    - `event_id` (optional, int): Filter by event ID
    - `team_id` (optional, int): Filter by team ID

    Manual Testing:

    curl -X GET '/ng/admin/support/tickets' \\
      -H 'Content-Type: application/json' \\
      -d '{"status": "open", "user_id": 123, "assigned_to": 456}'

    """,
    "responses": {
        200: "Success - Returns filtered list of tickets",
        400: "Bad request - Invalid filter parameters",
        **ADMIN_REQUIRED_RESPONSES,
    },
}

GET_TICKET_DOC = {
    "description": "Get any support ticket with all messages (Admin only)",
    "params": {
        "ticket_id": "Ticket ID"
    },
    "responses": {
        200: "Success - Returns ticket details and message thread",
        **ADMIN_REQUIRED_RESPONSES,
        404: "Not found - Ticket does not exist",
    },
}

ADD_ADMIN_MESSAGE_DOC = {
    "description":
    "Add admin message to any ticket (reopens closed tickets) (Admin only)",
    "params": {
        "ticket_id": "Ticket ID",
        "text": "Message content (4096 character max length)"
    },
    "responses": {
        201: "Success - Message added and ticket reopened if necessary",
        400: "Bad request - Missing message text",
        **ADMIN_REQUIRED_RESPONSES,
        404: "Not found - Ticket does not exist",
    },
}

SET_TICKET_TAGS_DOC = {
    "description":
    "Set tags on a ticket (replaces all existing tags) (Admin only)",
    "params": {
        "ticket_id": "Ticket ID",
        "tag_ids": "Array of tag IDs to assign (empty array to clear all tags)"
    },
    "responses": {
        200: "Success - Tags updated",
        400: "Bad request - Invalid tag_ids array",
        **ADMIN_REQUIRED_RESPONSES,
        404: "Not found - Ticket or tag IDs not found",
    },
}

ASSIGN_TICKET_DOC = {
    "description": "Assign a ticket to a user (Admin only)",
    "params": {
        "ticket_id": "Ticket ID",
        "user_id": "User ID to assign ticket to"
    },
    "responses": {
        200: "Success - Assignment updated",
        400: "Bad request - Invalid user_id or already assigned",
        **ADMIN_REQUIRED_RESPONSES,
        404: "Not found - Ticket or user not found",
    },
}

UNASSIGN_TICKET_DOC = {
    "description": "Unassign a ticket from any user (Admin only)",
    "params": {
        "ticket_id": "Ticket ID"
    },
    "responses": {
        200: "Success - Ticket unassigned",
        **ADMIN_REQUIRED_RESPONSES,
        404: "Not found - Ticket does not exist",
    },
}

UPDATE_STATUS_DOC = {
    "description": "Toggle ticket open/closed status (Admin only)",
    "params": {
        "ticket_id": "Ticket ID",
        "closed": "Whether to close the ticket"
    },
    "responses": {
        200: "Success - Status updated",
        400: "Bad request - Missing or invalid closed boolean",
        **ADMIN_REQUIRED_RESPONSES,
        404: "Not found - Ticket does not exist",
    },
}

UPDATE_MUTE_DOC = {
    "description": "Toggle ticket mute status (Admin only)",
    "params": {
        "ticket_id": "Ticket ID",
        "muted": "Whether to mute the ticket"
    },
    "responses": {
        200: "Success - Mute status updated",
        400: "Bad request - Missing or invalid muted boolean",
        **ADMIN_REQUIRED_RESPONSES,
        404: "Not found - Ticket does not exist",
    },
}

SET_TICKET_EVENT_DOC = {
    "description": "Set ticket's event and team association (Admin only)",
    "params": {
        "ticket_id": "Ticket ID",
        "event_id": "Event ID to associate with ticket",
        "team_id": "Team ID to associate with ticket"
    },
    "responses": {
        200:
        "Success - Event/team association updated",
        400:
        "Bad request - Team does not belong to specified event",
        **ADMIN_REQUIRED_RESPONSES,
        404:
        "Not found - Ticket, event, or team not found",
    },
}

REMOVE_TICKET_EVENT_DOC = {
    "description": "Remove ticket's event and team association (Admin only)",
    "params": {
        "ticket_id": "Ticket ID"
    },
    "responses": {
        200: "Success - Event/team association removed",
        **ADMIN_REQUIRED_RESPONSES,
        404: "Not found - Ticket does not exist",
    },
}

SET_TICKET_CHALLENGE_DOC = {
    "description": "Set ticket's challenge association (Admin only)",
    "params": {
        "ticket_id": "Ticket ID",
        "challenge_id": "Challenge ID to associate with ticket"
    },
    "responses": {
        200: "Success - Challenge association updated",
        400: "Bad request - Invalid challenge_id",
        **ADMIN_REQUIRED_RESPONSES,
        404: "Not found - Ticket or challenge not found",
    },
}

REMOVE_TICKET_CHALLENGE_DOC = {
    "description": "Remove ticket's challenge association (Admin only)",
    "params": {
        "ticket_id": "Ticket ID"
    },
    "responses": {
        200: "Success - Challenge association removed",
        **ADMIN_REQUIRED_RESPONSES,
        404: "Not found - Ticket does not exist",
    },
}

LIST_TAGS_DOC = {
    "description": "Get all available support ticket tags (Admin only)",
    "responses": {
        200: "Success - Returns list of all tags ordered by name",
        **ADMIN_REQUIRED_RESPONSES,
    },
}

CREATE_TAG_DOC = {
    "description": "Create a new support ticket tag (Admin only)",
    "params": {
        "name": "Tag name (50 character max length, must be unique)",
        "color": "Tag color (hex color code e.g #FFFFFF)",
        "description": "Tag description (200 character max length)"
    },
    "responses": {
        201: "Success - Tag created",
        400: "Bad request - Missing name or invalid color format",
        **ADMIN_REQUIRED_RESPONSES,
        409: "Conflict - Tag name already exists",
    },
}

UPDATE_TAG_DOC = {
    "description": "Update an existing support ticket tag (Admin only)",
    "params": {
        "ticket_tag_id": "Tag ID",
        "name": "Tag name (50 character max length)",
        "color": "Tag color (hex color code e.g #FF0000)",
        "description": "Tag description (200 character max length)"
    },
    "responses": {
        200: "Success - Tag updated",
        400: "Bad request - Invalid name or color format",
        **ADMIN_REQUIRED_RESPONSES,
        404: "Not found - Tag does not exist",
        409: "Conflict - Tag name already exists",
    },
}
