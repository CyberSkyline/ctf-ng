"""
Support Ticket API Documentation (User-Facing)
Centralized documentation for all support related endpoints
accessible by a standard authenticated user.
"""

# ============ Common Response Models for Users ============
USER_TICKET_RESPONSES = {
    200: "Success - Operation completed successfully",
    201: "Success - Resource created successfully",
    400: "Bad request - Invalid data or validation failed",
    401: "Unauthorized - Authentication required",
    403: "Forbidden - You do not have permission to perform this action on this ticket",
    404: "Not found - The requested ticket or resource does not exist",
    500: "Internal server error",
}

# ============ User Ticket Endpoints ============
GET_MY_TICKETS_DOC = {
    "description": "Get a list of the current user's support tickets, with optional status filtering.",
    "responses": {
        200: "Success - Returns a list of the user's support tickets.",
        **USER_TICKET_RESPONSES,
    },
}

CREATE_NEW_TICKET_DOC = {
    "description": "Create a new support ticket. The current user will be the author.",
    "responses": {
        201: "Success - The ticket was created successfully.",
        **USER_TICKET_RESPONSES,
    },
}

GET_MY_TICKET_DETAILS_DOC = {
    "description": "Get the full details and message history for one of the current user's tickets.",
    "responses": {
        200: "Success - Returns the complete ticket details and message thread.",
        **USER_TICKET_RESPONSES,
    },
}

UPDATE_MY_TICKET_DOC = {
    "description": "Update the subject of a ticket that the current user owns.",
    "responses": {
        200: "Success - The ticket subject was updated.",
        **USER_TICKET_RESPONSES,
    },
}

CREATE_TICKET_REPLY_DOC = {
    "description": "Add a new reply message to a ticket thread the user is part of.",
    "responses": {
        201: "Success - The reply was added to the ticket.",
        **USER_TICKET_RESPONSES,
    },
}
