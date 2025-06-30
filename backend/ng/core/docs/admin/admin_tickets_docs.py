"""
API Documentation for Admin Support Ticket Routes
Centralizes all documentation for admin level ticket management
"""

# ============ Common Response Models for Admins ============
ADMIN_SUPPORT_RESPONSES = {
    200: "Success - Operation completed",
    201: "Success - Resource created",
    400: "Bad request - Invalid data or validation failed",
    403: "Forbidden - Admin access required",
    404: "Not found - The requested resource does not exist",
    409: "Conflict - A resource with this name already exists or a constraint was violated",
    500: "Internal server error",
}

ADMIN_TICKET_RESPONSES = {
    **ADMIN_SUPPORT_RESPONSES,
    404: "Not found - The specified ticket does not exist",
}

ADMIN_TAG_RESPONSES = {
    **ADMIN_SUPPORT_RESPONSES,
    404: "Not found - The specified tag does not exist",
}

# ============ Admin Ticket Management ============
ADMIN_GET_ALL_TICKETS_DOC = {
    "description": "Get a list of all support tickets in the system, with advanced filtering options (Admin only).",
    "responses": ADMIN_TICKET_RESPONSES,
}

ADMIN_GET_TICKET_DETAILS_DOC = {
    "description": "Get the full details, message history, and metadata for any ticket (Admin only).",
    "responses": ADMIN_TICKET_RESPONSES,
}

ADMIN_UPDATE_TICKET_DOC = {
    "description": "Update any ticket's metadata, such as its subject or associations (Admin only).",
    "responses": ADMIN_TICKET_RESPONSES,
}

ADMIN_CREATE_TICKET_MESSAGE_DOC = {
    "description": "Post a reply to any ticket as an administrator (Admin only).",
    "responses": {**ADMIN_TICKET_RESPONSES, 201: "Success - Message created"},
}

# ============ Admin Ticket Assignment & State ============
ADMIN_ASSIGN_TICKET_DOC = {
    "description": "Assign a ticket to a specific support user or admin (Admin only).",
    "responses": ADMIN_TICKET_RESPONSES,
}

ADMIN_UNASSIGN_TICKET_DOC = {
    "description": "Remove the current assignment from a ticket (Admin only).",
    "responses": ADMIN_TICKET_RESPONSES,
}

ADMIN_CLOSE_TICKET_DOC = {
    "description": "Close any support ticket (Admin only).",
    "responses": {
        **ADMIN_TICKET_RESPONSES,
        400: "Bad request - Ticket is already closed",
    },
}

ADMIN_REOPEN_TICKET_DOC = {
    "description": "Reopen a previously closed ticket (Admin only).",
    "responses": {
        **ADMIN_TICKET_RESPONSES,
        400: "Bad request - Ticket is not currently closed",
    },
}

# ============ Admin Tag Management ============
ADMIN_GET_ALL_TAGS_DOC = {
    "description": "Get a list of all available ticket tags (Admin only).",
    "responses": ADMIN_TAG_RESPONSES,
}

ADMIN_CREATE_TAG_DOC = {
    "description": "Create a new ticket tag for categorization (Admin only).",
    "responses": {**ADMIN_TAG_RESPONSES, 201: "Success - Tag created"},
}

ADMIN_UPDATE_TAG_DOC = {
    "description": "Update an existing tag's name, color, or description (Admin only).",
    "responses": ADMIN_TAG_RESPONSES,
}

ADMIN_DELETE_TAG_DOC = {
    "description": "Permanently delete a tag and remove it from all associated tickets (Admin only).",
    "responses": ADMIN_TAG_RESPONSES,
}

ADMIN_ADD_TAGS_TO_TICKET_DOC = {
    "description": "Add one or more tags to a ticket (Admin only).",
    "responses": ADMIN_TICKET_RESPONSES,
}

ADMIN_REMOVE_TAGS_FROM_TICKET_DOC = {
    "description": "Remove one or more tags from a ticket (Admin only).",
    "responses": ADMIN_TICKET_RESPONSES,
}

ADMIN_GET_TICKET_STATS_DOC = {
    "description": "Get comprehensive statistics about the ticket system (Admin only).",
    "responses": ADMIN_SUPPORT_RESPONSES,
}

LIST_TAGS_DOC = {
    "description": "Get all tags available in the system (Admin only).",
    "responses": ADMIN_SUPPORT_RESPONSES,
}
