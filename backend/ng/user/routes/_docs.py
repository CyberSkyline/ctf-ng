"""
User RESTX Documentation
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

USER_REQUIRED_RESPONSES = {
    302: "Permission denied",
    500: COMMON_RESPONSES[500],
}

# ============ USER ENDPOINTS ============
GET_MY_USER_DOC = {
    "description": "Get my user information",
    "responses": {
        200: "Success",
        404: "User not found",
        **AUTH_REQUIRED_RESPONSES,
    },
}

GET_MY_EVENTS_DOC = {
    "description": "Get my events",
    "responses": {
        200: "Success",
        404: "Events not found",
        **AUTH_REQUIRED_RESPONSES,
    },
}

GET_MY_TEAMS_DOC = {
    "description": "Get my teams",
    "responses": {
        200: "Success",
        404: "Teams not found",
        **AUTH_REQUIRED_RESPONSES,
    },
}

# ============ ADMIN USER ENDPOINTS ============
GET_ALL_USERS_DOC = {
    "description": "Get all users",
    "responses": {
        200: "Success",
        **ADMIN_REQUIRED_RESPONSES,
    },
}

GET_USER_DOC = {
    "description": "Get a specific user by ID",
    "responses": {
        200: "User retrieved successfully",
        404: "User not found",
        **ADMIN_REQUIRED_RESPONSES,
    },
}

UPDATE_USER_DOC = {
    "description": "Update a specific user by ID",
    "params": {
        "json_data": {
            "description": "User data in JSON format",
            "in": "body",
            "required": True,
            "example": {
                "name": "new_username",
                "email": "new_email@example.com",
            }
        }
    },
    "responses": {
        200: "User updated successfully",
        404: "User not found",
        **ADMIN_REQUIRED_RESPONSES,
    },
}

DELETE_USER_DOC = {
    "description": "Delete a specific user by ID",
    "params": {
        "user_id": {
            "description": "ID of the user to delete",
            "in": "body",
            "required": True,
            "type": "integer",
            "example": {
                "user_id": 123
            }
        }
    },
    "responses": {
        200: "User deleted successfully",
        404: "User not found",
        **ADMIN_REQUIRED_RESPONSES,
    },
}

GET_USER_EVENTS_DOC = {
    "description": "Get events for a specific user",
    "responses": {
        200: "Events retrieved successfully",
        404: "User not found",
        **ADMIN_REQUIRED_RESPONSES,
    },
}

GET_USER_TEAMS_DOC = {
    "description": "Get teams for a specific user",
    "responses": {
        200: "Teams retrieved successfully",
        404: "User not found",
        **ADMIN_REQUIRED_RESPONSES,
    },
}
