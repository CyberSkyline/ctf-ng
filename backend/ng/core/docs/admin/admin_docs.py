"""
Admin API Documentation
Centralized documentation for all admin endpoints
"""

# ============ COMMON RESPONSES ============
ADMIN_RESPONSES = {
    200: "Success - Operation completed successfully",
    400: "Bad request - Invalid data or validation failed",
    403: "Forbidden - Admin access required",
    404: "Not found - Resource does not exist",
    500: "Internal server error",
}

DESTRUCTIVE_RESPONSES = {
    200: "Success - Data reset/cleanup completed successfully",
    400: "Bad request - Missing or incorrect confirmation",
    403: "Forbidden - Admin access required",
    404: "Not found - Resource does not exist",
    500: "Internal error - Operation failed, data may be in inconsistent state",
}

# ============ STATISTICS ENDPOINTS ============
GET_DETAILED_STATS_DOC = {
    "description": "Get comprehensive system statistics including per-event breakdowns, empty teams, and data integrity warnings (Admin only)",
    "responses": {
        200: "Success - Returns detailed system statistics with per-event data and potential issues",
        403: "Forbidden - Admin access required",
        500: "Internal Server Error",
    },
}

GET_DATA_COUNTS_DOC = {
    "description": "Get basic data counts for all plugin entities including events, teams, users, and team members (Admin only)",
    "responses": {
        200: "Success - Returns counts of events, teams, users, and team members",
        403: "Forbidden - Admin access required",
        500: "Internal Server Error",
    },
}

# ============ DESTRUCTIVE OPERATIONS ============
RESET_ALL_DATA_DOC = {
    "description": "**DESTRUCTIVE**: Reset ALL plugin data - permanently deletes everything! Requires confirmation (Admin only)",
    "responses": {
        200: "Success - All plugin data reset successfully",
        400: "Bad request - Missing or incorrect confirmation phrase",
        403: "Forbidden - Admin access required",
        500: "Internal error - Reset failed, system may be in inconsistent state",
    },
}

RESET_EVENT_DATA_DOC = {
    "description": "**DESTRUCTIVE**: Reset all data for a specific event including teams and team members (Admin only)",
    "responses": {
        200: "Success - Event data reset successfully",
        400: "Bad request - Event does not exist or missing confirmation",
        403: "Forbidden - Admin access required",
        500: "Internal error - Reset failed, data may be in inconsistent state",
    },
}

# ============ CLEANUP OPERATIONS ============
CLEANUP_ORPHANED_DATA_DOC = {
    "description": "Clean up orphaned data such as users with no team associations (Admin only)",
    "responses": {
        200: "Success - Cleanup completed successfully with counts of cleaned data",
        403: "Forbidden - Admin access required",
        500: "Internal error - Cleanup failed",
    },
}

CLEANUP_HEADLESS_TEAMS_DOC = {
    "description": "Fix teams without captains by automatically promoting the oldest member to captain role (Admin only)",
    "responses": {
        200: "Success - Headless teams cleanup completed with count of fixed teams",
        403: "Forbidden - Admin access required",
        500: "Internal error - Cleanup failed",
    },
}

# ============ SYSTEM HEALTH ============
SYSTEM_HEALTH_DOC = {
    "description": "Check system health and data integrity with warnings for potential issues (Admin only)",
    "responses": {
        200: "Success - System health report with warnings and data integrity status",
        403: "Forbidden - Admin access required",
        500: "Internal Server Error",
    },
}
