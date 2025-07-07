"""
User API Documentation
Centralized documentation for all user related endpoints
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
    403: "Forbidden - Admin access required",
    404: COMMON_RESPONSES[404],
    500: COMMON_RESPONSES[500],
}

# ============ ADMIN USER MANAGEMENT ============
LIST_ALL_USERS_DOC = {
    "description": "Get a comprehensive list of all users with extended details including team counts and registration info (Admin only)",
    "responses": {
        200: "Success - Returns list of all users with detailed information",
        403: "Forbidden - Admin access required",
        500: "Internal Server Error",
    },
}

GET_USER_DETAILS_DOC = {
    "description": "Get detailed information for a specific user including team participation and account details (Admin only)",
    "responses": {
        200: "Success - Returns user details with team counts and registration info",
        403: "Forbidden - Admin access required",
        404: "Not found - User does not exist",
        500: "Internal Server Error",
    },
}

# ============ CURRENT USER ENDPOINTS ============
GET_MY_TEAMS_DOC = {
    "description": "Get current user's team memberships across all events with event details and team information",
    "responses": {
        200: "Success - Returns user teams across all events with join dates and team details",
        403: "Forbidden - User not authenticated",
        500: "Internal Server Error",
    },
}

GET_MY_EVENT_TEAM_DOC = {
    "description": "Get current user's team membership details within a specific event including team and event information",
    "responses": {
        200: "Success - Returns user team in specified event or null if not in a team",
        403: "Forbidden - User not authenticated",
        404: "Not found - Event does not exist",
        500: "Internal Server Error",
    },
}

GET_MY_ELIGIBILITY_DOC = {
    "description": "Check if current user is eligible to join a team in the specified event (not already in another team)",
    "responses": {
        200: "Success - Returns eligibility status with reasons if not eligible",
        400: "Bad request - User already in a team for this event",
        403: "Forbidden - User not authenticated",
        500: "Internal Server Error",
    },
}

# ============ ADMIN USER DATA ACCESS ============
GET_USER_TEAMS_DOC = {
    "description": "Get any user's team memberships across all events with detailed team and event information (Admin only)",
    "responses": {
        200: "Success - Returns user teams with join dates and team details",
        403: "Forbidden - Admin access required",
        404: "Not found - User does not exist",
        500: "Internal Server Error",
    },
}
