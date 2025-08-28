"""
Team Admin API Documentation
"""

# ============ COMMON RESPONSES ============
COMMON_RESPONSES = {
    200: "Success - Operation completed successfully",
    400: "Bad request - Invalid data or validation failed",
    404: "Not found - Resource does not exist",
    500: "Internal server error",
}

ADMIN_REQUIRED_RESPONSES = {
    403: "Forbidden - Admin access required",
    500: COMMON_RESPONSES[500],
}

# ============ TEAM ADMIN ENDPOINTS ============
GET_ALL_TEAMS_DOC = {
    "description": "Get all teams",
    "responses": {
        200: "Success",
        404: "No teams found",
        **ADMIN_REQUIRED_RESPONSES,
    },
}

GET_TEAM_DOC = {
    "description": "Get a team by ID",
    "responses": {
        200: "Success",
        404: "Team not found",
        **ADMIN_REQUIRED_RESPONSES,
    },
}

UPDATE_TEAM_DOC = {
    "description": "Update a team by ID",
    "params": {
        "json_data": {
            "description": "Updated team data",
            "in": "body",
            "required": True,
            "example": {
                "name": "New Team Name",
                "description": "Updated description"
            }
        }
    },
    "responses": {
        200: "Success",
        404: "Team not found",
        400: "Bad Request if validation fails",
        **ADMIN_REQUIRED_RESPONSES,
    },
}

GET_TEAM_MEMBERS_DOC = {
    "description": "Get all members of a team",
    "responses": {
        200: "Success",
        404: "Team not found",
        **ADMIN_REQUIRED_RESPONSES,
    },
}

KICK_TEAM_MEMBER_DOC = {
    "description": "Kick a user from a team",
    "params": {
        "user_id": {
            "description": "User ID to kick from the team",
            "in": "body",
            "required": True,
            "example": {
                "user_id": 123
            }
        }
    },
    "responses": {
        200: "Success",
        404: "Team or User not found",
        400: "Bad Request if user is not a member of the team",
        **ADMIN_REQUIRED_RESPONSES,
    },
}

PROMOTE_TEAM_MEMBER_DOC = {
    "description": "Promote a user to team leader",
    "params": {
        "user_id": {
            "description": "User ID to promote to team leader",
            "in": "body",
            "required": True,
            "example": {
                "user_id": 123
            }
        }
    },
    "responses": {
        200: "Success",
        404: "Team or User not found",
        400: "Bad Request if user is not a member of the team",
        **ADMIN_REQUIRED_RESPONSES,
    },
}