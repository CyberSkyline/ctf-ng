"""
Team API Documentation
Centralized documentation for all team related endpoints.
"""

# ============ COMMON RESPONSES ============
COMMON_RESPONSES = {
    200: "Success - Operation completed successfully",
    400: "Bad request - Invalid data or validation failed",
    401: "Unauthorized - Authentication required",
    403: "Forbidden - Insufficient permissions",
    404: "Not found - Resource does not exist",
    409: "Conflict - Resource already exists or constraint violation",
    500: "Internal server error",
}

AUTH_REQUIRED_RESPONSES = {
    200: COMMON_RESPONSES[200],
    400: COMMON_RESPONSES[400],
    403: COMMON_RESPONSES[403],
    500: COMMON_RESPONSES[500],
}

CAPTAIN_ADMIN_RESPONSES = {
    200: COMMON_RESPONSES[200],
    400: COMMON_RESPONSES[400],
    403: "Forbidden - Captain or admin access required",
    404: COMMON_RESPONSES[404],
    500: COMMON_RESPONSES[500],
}

# ============ TEAM LIST ENDPOINTS ============
LIST_ALL_TEAMS_DOC = {
    "description": "Get comprehensive list of ALL teams in the system with event associations and member counts (Admin only)",
    "responses": {
        200: "Success - Returns list of all teams with event and member information",
        403: "Forbidden - Admin access required",
        500: "Internal Server Error",
    },
}

CREATE_TEAM_DOC = {
    "description": "Create a new team in a specific event with current user automatically becoming the captain",
    "responses": {
        201: "Success - Team created successfully with auto-generated invite code",
        400: "Bad request - Invalid data, event locked, or user already in team for this event",
        403: "Forbidden - User not authenticated",
        404: "Not found - Event does not exist",
        409: "Conflict - Team name already exists in this event",
        500: "Internal Server Error",
    },
}

# ============ TEAM DETAIL ENDPOINTS ============
GET_TEAM_DOC = {
    "description": "Get detailed information about a specific team including all members, event details, and team statistics",
    "responses": {
        200: "Success - Team details with members and event info returned",
        403: "Forbidden - User not authenticated",
        404: "Not found - Team does not exist",
        500: "Internal Server Error",
    },
}

UPDATE_TEAM_DOC = {
    "description": "Update team information such as name and settings (Captain or Admin only)",
    "responses": {
        200: "Success - Team updated successfully",
        400: "Bad request - Invalid data or empty team name",
        403: "Forbidden - Captain or admin access required",
        404: "Not found - Team does not exist",
        409: "Conflict - Team name already exists in event",
        500: "Internal Server Error",
    },
}

DISBAND_TEAM_DOC = {
    "description": "Permanently disband a team and remove all its members (Captain or Admin only)",
    "responses": {
        200: "Success - Team disbanded successfully",
        400: "Bad request - Cannot disband team due to event constraints",
        403: "Forbidden - Captain or admin access required",
        404: "Not found - Team does not exist",
        500: "Internal Server Error",
    },
}

# ============ TEAM MEMBERSHIP ENDPOINTS ============
JOIN_TEAM_DOC = {
    "description": "Join a team using its unique invite code",
    "responses": {
        200: "Success - Joined team successfully",
        400: "Bad request - Invalid invite code, team full, event locked, or user already in team",
        403: "Forbidden - User not authenticated",
        404: "Not found - Invalid invite code",
        500: "Internal Server Error",
    },
}

LEAVE_TEAM_DOC = {
    "description": "Leave current team in a specific event",
    "responses": {
        200: "Success - Left team successfully (may auto-disband if captain and last member)",
        400: "Bad request - Not in a team, event locked, or captains cannot leave teams with members",
        403: "Forbidden - User not authenticated",
        404: "Not found - User not in any team for this event",
        500: "Internal Server Error",
    },
}

# ============ TEAM CAPTAIN ENDPOINTS ============
GET_CAPTAIN_DOC = {
    "description": "Get information about the current captain of a team",
    "responses": {
        200: "Success - Captain information returned or indication of no captain",
        403: "Forbidden - User not authenticated",
        404: "Not found - Team does not exist",
        500: "Internal Server Error",
    },
}

TRANSFER_CAPTAINCY_DOC = {
    "description": "Transfer team captaincy to another team member (Captain or Admin only)",
    "responses": {
        200: "Success - Captain role transferred successfully",
        400: "Bad request - User is not a member of this team",
        403: "Forbidden - Captain or admin access required",
        404: "Not found - Team does not exist",
        500: "Internal Server Error",
    },
}

# ============ TEAM MEMBER MANAGEMENT ============
REMOVE_MEMBER_DOC = {
    "description": "Remove a member from the team with automatic invite code regeneration for security (Captain or Admin only)",
    "responses": {
        200: "Success - Member removed successfully (may auto-promote new captain if needed)",
        400: "Bad request - Cannot remove member due to event constraints or member role restrictions",
        403: "Forbidden - Captain or admin access required",
        404: "Not found - Team or member does not exist",
        500: "Internal Server Error",
    },
}
