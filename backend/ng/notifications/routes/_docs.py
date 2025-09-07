"""
Notification API Documentation
Centralized documentation for all notification related endpoints
"""

# ============ COMMON RESPONSES ============
COMMON_RESPONSES = {
    200: "Success - Operation completed successfully",
    201: "Success - Resource created successfully",
    400: "Bad request - Invalid data or validation failed",
    401: "Unauthorized - Authentication required",
    403: "Forbidden - Insufficient permissions",
    404: "Not found - Resource does not exist",
    500: "Internal server error",
}

AUTH_REQUIRED_RESPONSES = {
    200: COMMON_RESPONSES[200],
    401: COMMON_RESPONSES[401],
    500: COMMON_RESPONSES[500],
}

ADMIN_REQUIRED_RESPONSES = {
    200: COMMON_RESPONSES[200],
    400: COMMON_RESPONSES[400],
    401: COMMON_RESPONSES[401],
    403: "Forbidden - Admin access required",
    500: COMMON_RESPONSES[500],
}

# ============ USER NOTIFICATION ENDPOINTS ============
GET_MY_NOTIFICATIONS_DOC = {
    "description": "Get my notifications with optional read status filter",
    "params": {
        "is_read": {
            "description": "Filter by read status (true/false)",
            "required": False,
            "type": "string",
            "example": "false"
        }
    },
    "responses": {
        200: "Success - Returns list of notifications",
        **AUTH_REQUIRED_RESPONSES,
    },
}

GET_UNREAD_COUNT_DOC = {
    "description": "Get count of unread notifications for the current user",
    "responses": {
        200: "Success - Returns unread notification count",
        **AUTH_REQUIRED_RESPONSES,
    },
}

MARK_NOTIFICATION_READ_DOC = {
    "description": "Mark a specific notification as read",
    "responses": {
        200: "Success - Notification marked as read",
        403: "Forbidden - Cannot mark other users' notifications as read",
        404: "Not found - Notification does not exist",
        **AUTH_REQUIRED_RESPONSES,
    },
}

MARK_ALL_READ_DOC = {
    "description": "Mark all notifications as read for the current user",
    "responses": {
        200:
        "Success - All notifications marked as read, returns count of updated notifications",
        **AUTH_REQUIRED_RESPONSES,
    },
}

GET_ACTIVE_ANNOUNCEMENTS_DOC = {
    "description": "Get active announcements (system-wide or event-specific)",
    "params": {
        "event_id": {
            "description": "Filter by event (optional)",
            "required": False,
            "type": "integer",
            "example": 1
        }
    },
    "responses": {
        200: "Success - Returns list of active announcements",
        **AUTH_REQUIRED_RESPONSES,
    },
}

# ============ ADMIN NOTIFICATION ENDPOINTS ============
SEND_SYSTEM_ANNOUNCEMENT_DOC = {
    "description": "Send system-wide announcement to all users",
    "params": {
        "title": {
            "description": "Announcement title",
            "in": "body",
            "required": True,
            "type": "string",
            "example": "System Maintenance"
        },
        "message": {
            "description": "Announcement message content",
            "in": "body",
            "required": True,
            "type": "string",
            "example": "The system will be under maintenance from 2-4 PM UTC"
        }
    },
    "responses": {
        200: "Success - System announcement sent",
        400: "Bad request - Invalid title or message",
        **ADMIN_REQUIRED_RESPONSES,
    },
}

SEND_EVENT_ANNOUNCEMENT_DOC = {
    "description": "Send announcement to all participants in a specific event",
    "params": {
        "title": {
            "description": "Announcement title",
            "in": "body",
            "required": True,
            "type": "string",
            "example": "Event Update"
        },
        "message": {
            "description": "Announcement message content",
            "in": "body",
            "required": True,
            "type": "string",
            "example": "New challenge has been released!"
        },
        "type": {
            "description":
            "Announcement type (general, event_update, event_start, event_end, leaderboard_update)",
            "in": "body",
            "required": False,
            "type": "string",
            "example": "event_update",
            "default": "event_update"
        }
    },
    "responses": {
        200: "Success - Event announcement sent to all participants",
        400: "Bad request - Invalid announcement data or type",
        404: "Not found - Event does not exist",
        **ADMIN_REQUIRED_RESPONSES,
    },
}

GET_ALL_ANNOUNCEMENTS_DOC = {
    "description":
    "Get all announcements for admin management (includes expired)",
    "responses": {
        200: "Success - Returns list of all announcements",
        **ADMIN_REQUIRED_RESPONSES,
    },
}
