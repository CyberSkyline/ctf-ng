"""
Event Registration API Documentation
"""

# ============ Common Response Models for Event Registration ============
EVENT_REG_RESPONSES = {
    200: "Success - Operation completed successfully",
    201: "Success - Resource created successfully",
    400: "Bad request - Invalid data or validation failed",
    401: "Unauthorized - Authentication required",
    403: "Forbidden - You do not have permission to perform this action",
    404: "Not found - The requested event or resource does not exist",
    409: "Conflict - User already registered or other constraint violation",
    500: "Internal server error",
}

ADMIN_EVENT_REG_RESPONSES = {
    **EVENT_REG_RESPONSES,
    403: "Forbidden - Admin access required",
}

# ============ User Event Registration Endpoints ============
GET_USER_DEMOGRAPHICS_DOC = {
    "description": "Get the current user's demographic information and registration status for a specific event.",
    "responses": {
        200: "Success - Returns user demographics and registration status for the event",
        **EVENT_REG_RESPONSES,
    },
}

JOIN_EVENT_DOC = {
    "description": "Join an event by either creating a new team or joining an existing team using an invite code.",
    "responses": {
        200: "Success - Successfully joined the event and team",
        400: "Bad request - Event registration closed, user already registered, or invalid team data",
        409: "Conflict - User already registered for this event or team name conflicts",
        **EVENT_REG_RESPONSES,
    },
}

# ============ Admin Event Registration Management ============
CREATE_EVENT_REGISTRATION_DOC = {
    "description": "Create or configure the registration period and settings for an event (Admin only).",
    "responses": {
        201: "Success - Event registration period created successfully",
        400: "Bad request - Invalid registration dates or missing event ID",
        409: "Conflict - Registration period already exists for this event",
        **ADMIN_EVENT_REG_RESPONSES,
    },
}
