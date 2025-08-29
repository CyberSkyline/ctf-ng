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

# ============ ADMIN EVENT ENDPOINTS ============
ADMIN_LIST_EVENTS_DOC = {
    "description": "Get all events (public and private) for admin management",
    "responses": {
        200: "Success - Returns list of all events",
        404: "Not found - No events found",
        **ADMIN_REQUIRED_RESPONSES,
    },
}

ADMIN_CREATE_EVENT_DOC = {
    "description": "Create a new event with scheduling and configuration options",
    "params": {
        "name": {
            "description": "Event name (256 character max length)",
            "in": "body",
            "required": True,
            "type": "string",
            "example": "New CTF Event"
        },
        "description": {
            "description": "Event description (1000 character max length)",
            "in": "body",
            "required": False,
            "type": "string",
            "example": "Description of the new event"
        },
        "start_time": {
            "description": "Event start time in ISO format",
            "in": "body",
            "required": False,
            "type": "string",
            "example": "2023-10-01T00:00:00Z"
        },
        "end_time": {
            "description": "Event end time in ISO format",
            "in": "body",
            "required": False,
            "type": "string",
            "example": "2023-10-31T23:59:59Z"
        }
    },
    "responses": {
        201: "Success - Event created successfully",
        400: "Bad request - Validation failed or name conflict",
        **ADMIN_REQUIRED_RESPONSES,
    },
}

ADMIN_GET_EVENT_DOC = {
    "description": "Get detailed information about a specific event",
    "responses": {
        200: "Success - Returns event details",
        404: "Not found - Event does not exist",
        **ADMIN_REQUIRED_RESPONSES,
    },
}

ADMIN_UPDATE_EVENT_DOC = {
    "description": "Update an existing event's configuration and settings",
    "params": {
        "name": {
            "description": "Updated event name (256 character max length)",
            "in": "body",
            "required": False,
            "type": "string",
            "example": "Updated Event Name"
        },
        "description": {
            "description": "Updated event description (1000 character max length)",
            "in": "body",
            "required": False,
            "type": "string",
            "example": "Updated description of the event"
        },
        "start_time": {
            "description": "Updated event start time in ISO format",
            "in": "body",
            "required": False,
            "type": "string",
            "example": "2023-10-01T00:00:00Z"
        },
        "end_time": {
            "description": "Updated event end time in ISO format",
            "in": "body",
            "required": False,
            "type": "string",
            "example": "2023-10-31T23:59:59Z"
        }
    },
    "responses": {
        200: "Success - Event updated successfully",
        400: "Bad request - Validation failed",
        404: "Not found - Event does not exist",
        **ADMIN_REQUIRED_RESPONSES,
    },
}

ADMIN_REGISTER_USER_DOC = {
    "description": "Register a user for an event using invite code or team name",
    "params": {
        "invite_code": {
            "description": "Invite code for joining an existing team",
            "in": "body",
            "required": False,
            "type": "string",
            "example": "xchfg459fghj"
        },
        "team_name": {
            "description": "Name for creating a new team",
            "in": "body",
            "required": False,
            "type": "string",
            "example": "My Team"
        }
    },
    "responses": {
        200: "Success - User registered for event",
        400: "Bad request - Missing invite_code or team_name",
        404: "Not found - Event or user does not exist",
        **ADMIN_REQUIRED_RESPONSES,
    },
}

ADMIN_CREATE_CHALLENGE_DOC = {
    "description": "Create a challenge for an event using YAML configuration",
    "params": {
        "name": {
            "description": "Challenge name",
            "in": "body",
            "required": True,
            "type": "string",
            "example": "Web Security Challenge"
        },
        "description": {
            "description": "Challenge description and instructions",
            "in": "body",
            "required": True,
            "type": "string",
            "example": "Find the vulnerability in this web application"
        },
        "value": {
            "description": "Point value for the challenge",
            "in": "body",
            "required": True,
            "type": "integer",
            "example": 100
        },
        "category": {
            "description": "Challenge category",
            "in": "body",
            "required": True,
            "type": "string",
            "example": "Web"
        }
    },
    "responses": {
        200: "Success - Challenge created successfully",
        400: "Bad request - Invalid challenge data",
        404: "Not found - Event does not exist",
        **ADMIN_REQUIRED_RESPONSES,
    },
}

START_EVENT_DOC = {
    "description": "Manually start an event and notify all participants",
    "responses": {
        200: "Success - Event started and notifications sent",
        400: "Bad request - Event has already started",
        404: "Not found - Event does not exist",
        **ADMIN_REQUIRED_RESPONSES,
    },
}

END_EVENT_DOC = {
    "description": "Manually end an event and notify all participants",
    "responses": {
        200: "Success - Event ended and notifications sent",
        400: "Bad request - Event is already ended",
        404: "Not found - Event does not exist",
        **ADMIN_REQUIRED_RESPONSES,
    },
}

# ============ USER EVENT ENDPOINTS ============
USER_LIST_EVENTS_DOC = {
    "description": "Get all public events available to users",
    "responses": {
        200: "Success - Returns list of public events",
        **AUTH_REQUIRED_RESPONSES,
    },
}

USER_GET_EVENT_DOC = {
    "description": "Get details of a specific event",
    "responses": {
        200: "Success - Returns event details",
        **AUTH_REQUIRED_RESPONSES,
        404: "Not found - Event does not exist",
    },
}

# ============ EVENT PARTICIPATION ENDPOINTS ============
CHECK_ELIGIBILITY_DOC = {
    "description": "Check if the current user is eligible to register for an event",
    "responses": {
        200: "Success - Returns eligibility status and details",
        **AUTH_REQUIRED_RESPONSES,
        404: "Not found - Event does not exist",
    },
}

REGISTER_FOR_EVENT_DOC = {
    "description": "Register for an event (creates demographic entry)",
    "params": {
        "invite_code": {
            "description": "Invite code for joining an existing team (mutually exclusive with team_name)",
            "in": "body",
            "required": False,
            "type": "string",
            "example": "xchfg459fghj"
        },
        "team_name": {
            "description": "Name for creating a new team (mutually exclusive with invite_code)",
            "in": "body",
            "required": False,
            "type": "string",
            "example": "My Team"
        }
    },
    "responses": {
        201: "Success - Registered for event",
        400: "Bad request - Already registered, registration not allowed, or missing/invalid parameters",
        **AUTH_REQUIRED_RESPONSES,
        404: "Not found - Event does not exist",
    },
}

# ============ TEAM MANAGEMENT ENDPOINTS ============
GET_MY_TEAM_DOC = {
    "description": "Get current user's team information for an event",
    "responses": {
        200: "Success - Returns team details",
        **AUTH_REQUIRED_RESPONSES,
        404: "Not found - Event does not exist or user not in a team",
    },
}

GET_TEAM_MEMBERS_DOC = {
    "description": "Get all members of the current user's team",
    "responses": {
        200: "Success - Returns list of team members",
        **AUTH_REQUIRED_RESPONSES,
        404: "Not found - Event does not exist or user not in a team",
    },
}

UPDATE_TEAM_NAME_DOC = {
    "description": "Update the team name (requires team captain privileges)",
    "params": {
        "name": {
            "description": "New team name (128 character max length)",
            "in": "body",
            "required": True,
            "type": "string",
            "example": "Elite Hackers"
        }
    },
    "responses": {
        200: "Success - Team name updated",
        400: "Bad request - Invalid team name or team name already exists",
        **AUTH_REQUIRED_RESPONSES,
        403: "Forbidden - Only team captain can update team name",
        404: "Not found - Event does not exist or user not in a team",
    },
}

KICK_TEAM_MEMBER_DOC = {
    "description": "Remove a member from the team (requires team captain privileges)",
    "params": {
        "user_id": {
            "description": "User ID of team member to remove",
            "in": "body",
            "required": True,
            "type": "integer",
            "example": 123
        }
    },
    "responses": {
        200: "Success - Member removed from team",
        400: "Bad request - Cannot kick yourself or invalid user_id",
        **AUTH_REQUIRED_RESPONSES,
        403: "Forbidden - Only team captain can kick members",
        404: "Not found - Event, team, or user not found",
    },
}

PROMOTE_TEAM_MEMBER_DOC = {
    "description": "Promote a team member to captain (requires team captain privileges)",
    "params": {
        "user_id": {
            "description": "User ID of team member to promote",
            "in": "body",
            "required": True,
            "type": "integer",
            "example": 123
        }
    },
    "responses": {
        200: "Success - Member promoted to captain",
        400: "Bad request - Cannot promote yourself or invalid user_id",
        **AUTH_REQUIRED_RESPONSES,
        403: "Forbidden - Only team captain can promote members",
        404: "Not found - Event, team, or user not found",
    },
}

LEAVE_TEAM_DOC = {
    "description": "Leave the current team. If captain leaves and other members exist, oldest member becomes captain.",
    "responses": {
        200: "Success - Left team successfully",
        400: "Bad request - Cannot leave team or team constraints violated",
        **AUTH_REQUIRED_RESPONSES,
        404: "Not found - Event does not exist or user not in a team",
    },
}

# ============ CHALLENGE ENDPOINTS ============
LIST_CHALLENGES_DOC = {
    "description": "Get all challenges in an event",
    "responses": {
        200: "Success - Returns list of challenges",
        **AUTH_REQUIRED_RESPONSES,
        404: "Not found - Event does not exist",
    },
}

GET_CHALLENGE_DOC = {
    "description": "Get detailed information about a specific challenge including questions and hints",
    "responses": {
        200: "Success - Returns challenge details with questions and hints",
        **AUTH_REQUIRED_RESPONSES,
        404: "Not found - Event or challenge does not exist",
    },
}

GET_CHALLENGE_PROGRESS_DOC = {
    "description": "Get progress status for all challenges in an event for the current user's team",
    "responses": {
        200: "Success - Returns progress for all challenges including points scored, questions solved, completion status",
        **AUTH_REQUIRED_RESPONSES,
        404: "Not found - Event does not exist or user not in a team",
    },
}

START_CHALLENGE_CONTAINERS_DOC = {
    "description": "Start containers for a specific challenge",
    "responses": {
        200: "Success - Containers started, returns connection details",
        400: "Bad request - Challenge does not support containers or containers already running",
        **AUTH_REQUIRED_RESPONSES,
        404: "Not found - Event or challenge does not exist",
    },
}
