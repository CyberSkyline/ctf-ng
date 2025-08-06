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
    "responses": {
        201: "Success - Ticket created with initial message",
        400: "Bad request - Missing required fields (subject, text) or invalid associations",
        **AUTH_REQUIRED_RESPONSES,
        404: "Not found - Event, team, or challenge association not found",
    },
}

LIST_MY_TICKETS_DOC = {
    "description": "Get all support tickets created by the current user with optional status filter",
    "responses": {
        200: "Success - Returns list of user's tickets",
        400: "Bad request - Invalid status filter (must be: all, open, closed)",
        **AUTH_REQUIRED_RESPONSES,
    },
}

GET_MY_TICKET_DOC = {
    "description": "Get a specific ticket with all messages (user must own the ticket)",
    "responses": {
        200: "Success - Returns ticket details and message thread",
        **AUTH_REQUIRED_RESPONSES,
        403: "Forbidden - You can only access your own tickets",
        404: "Not found - Ticket does not exist",
    },
}

ADD_MESSAGE_DOC = {
    "description": "Add a new message to an existing support ticket thread",
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
    "description": "Get all support tickets with optional filters (Admin only)",
    "responses": {
        200: "Success - Returns filtered list of tickets",
        400: "Bad request - Invalid filter parameters",
        **ADMIN_REQUIRED_RESPONSES,
    },
}

GET_TICKET_DOC = {
    "description": "Get any support ticket with all messages (Admin only)",
    "responses": {
        200: "Success - Returns ticket details and message thread",
        **ADMIN_REQUIRED_RESPONSES,
        404: "Not found - Ticket does not exist",
    },
}

ADD_ADMIN_MESSAGE_DOC = {
    "description": "Add admin message to any ticket (reopens closed tickets) (Admin only)",
    "responses": {
        201: "Success - Message added and ticket reopened if necessary",
        400: "Bad request - Missing message text",
        **ADMIN_REQUIRED_RESPONSES,
        404: "Not found - Ticket does not exist",
    },
}

SET_TICKET_TAGS_DOC = {
    "description": "Set tags on a ticket (replaces all existing tags) (Admin only)",
    "responses": {
        200: "Success - Tags updated",
        400: "Bad request - Invalid tag_ids array",
        **ADMIN_REQUIRED_RESPONSES,
        404: "Not found - Ticket or tag IDs not found",
    },
}

ASSIGN_TICKET_DOC = {
    "description": "Assign a ticket to a user (Admin only)",
    "responses": {
        200: "Success - Assignment updated",
        400: "Bad request - Invalid user_id or already assigned",
        **ADMIN_REQUIRED_RESPONSES,
        404: "Not found - Ticket or user not found",
    },
}

UNASSIGN_TICKET_DOC = {
    "description": "Unassign a ticket from any user (Admin only)",
    "responses": {
        200: "Success - Ticket unassigned",
        **ADMIN_REQUIRED_RESPONSES,
        404: "Not found - Ticket does not exist",
    },
}

UPDATE_STATUS_DOC = {
    "description": "Toggle ticket open/closed status (Admin only)",
    "responses": {
        200: "Success - Status updated",
        400: "Bad request - Missing or invalid closed boolean",
        **ADMIN_REQUIRED_RESPONSES,
        404: "Not found - Ticket does not exist",
    },
}

UPDATE_MUTE_DOC = {
    "description": "Toggle ticket mute status (Admin only)",
    "responses": {
        200: "Success - Mute status updated",
        400: "Bad request - Missing or invalid muted boolean",
        **ADMIN_REQUIRED_RESPONSES,
        404: "Not found - Ticket does not exist",
    },
}

SET_TICKET_EVENT_DOC = {
    "description": "Set ticket's event and team association (Admin only)",
    "responses": {
        200: "Success - Event/team association updated",
        400: "Bad request - Team does not belong to specified event",
        **ADMIN_REQUIRED_RESPONSES,
        404: "Not found - Ticket, event, or team not found",
    },
}

REMOVE_TICKET_EVENT_DOC = {
    "description": "Remove ticket's event and team association (Admin only)",
    "responses": {
        200: "Success - Event/team association removed",
        **ADMIN_REQUIRED_RESPONSES,
        404: "Not found - Ticket does not exist",
    },
}

SET_TICKET_CHALLENGE_DOC = {
    "description": "Set ticket's challenge association (Admin only)",
    "responses": {
        200: "Success - Challenge association updated",
        400: "Bad request - Invalid challenge_id",
        **ADMIN_REQUIRED_RESPONSES,
        404: "Not found - Ticket or challenge not found",
    },
}

REMOVE_TICKET_CHALLENGE_DOC = {
    "description": "Remove ticket's challenge association (Admin only)",
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
    "responses": {
        201: "Success - Tag created",
        400: "Bad request - Missing name or invalid color format",
        **ADMIN_REQUIRED_RESPONSES,
        409: "Conflict - Tag name already exists",
    },
}

UPDATE_TAG_DOC = {
    "description": "Update an existing support ticket tag (Admin only)",
    "responses": {
        200: "Success - Tag updated",
        400: "Bad request - Invalid name or color format",
        **ADMIN_REQUIRED_RESPONSES,
        404: "Not found - Tag does not exist",
        409: "Conflict - Tag name already exists",
    },
}
