"""
Event API Documentation
Centralized documentation for all event related endpoints
"""

# ============ COMMON RESPONSES ============
COMMON_RESPONSES = {
    200: "Success - Operation completed successfully",
    400: "Bad request - Invalid data or validation failed",
    401: "Unauthorized - Authentication required",
    403: "Forbidden - Insufficient permissions",
    404: "Not found - Resource does not exist",
    500: "Internal server error",
}

AUTH_REQUIRED_RESPONSES = {
    200: COMMON_RESPONSES[200],
    403: COMMON_RESPONSES[403],
    500: COMMON_RESPONSES[500],
}

ADMIN_REQUIRED_RESPONSES = {
    200: COMMON_RESPONSES[200],
    400: COMMON_RESPONSES[400],
    403: "Forbidden - Admin access required",
    500: COMMON_RESPONSES[500],
}

# ============ EVENT LIST ENDPOINTS ============
LIST_EVENTS_DOC = {
    "description": "Get list of all training events with statistics including team counts and member counts",
    "responses": {
        200: "Success - Returns list of events with team/member statistics",
        403: "Forbidden - User not authenticated",
        500: "Internal Server Error",
    },
}

CREATE_EVENT_DOC = {
    "description": "Create a new training event with optional scheduling and team size limits (Admin only)",
    "responses": {
        201: "Success - Event created successfully",
        400: "Bad request - Invalid data, validation failed, or name conflict",
        403: "Forbidden - Admin access required",
        409: "Conflict - Event name already exists",
        500: "Internal Server Error",
    },
}

# ============ EVENT DETAIL ENDPOINTS ============
GET_EVENT_DOC = {
    "description": "Get detailed information about a specific event including all associated teams",
    "responses": {
        200: "Success - Event details with teams returned",
        403: "Forbidden - User not authenticated",
        404: "Not found - Event does not exist",
        500: "Internal Server Error",
    },
}

UPDATE_EVENT_DOC = {
    "description": "Update event information including name, description, team size limits, and scheduling (Admin only)",
    "responses": {
        200: "Success - Event updated successfully",
        400: "Bad request - Invalid data, validation failed, or constraint violation",
        403: "Forbidden - Admin access required",
        404: "Not found - Event does not exist",
        409: "Conflict - Event name already exists",
        500: "Internal Server Error",
    },
}

# ============ EVENT TEAMS ENDPOINTS ============
GET_EVENT_TEAMS_DOC = {
    "description": "Get all teams participating in a specific event with member counts and team details",
    "responses": {
        200: "Success - Teams in event returned",
        403: "Forbidden - User not authenticated",
        404: "Not found - Event does not exist",
        500: "Internal Server Error",
    },
}
