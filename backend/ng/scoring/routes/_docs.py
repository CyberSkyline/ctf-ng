"""
Scoring RESTX Documentation
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
    401: COMMON_RESPONSES[401],
    500: COMMON_RESPONSES[500],
}

ADMIN_REQUIRED_RESPONSES = {
    403: "Forbidden - Admin access required",
    500: COMMON_RESPONSES[500],
}

# ============ USER SCORING ENDPOINTS ============
GET_LEADERBOARD_DOC = {
    "description": "Get the event leaderboard showing team rankings and scores with optional limit",
    "responses": {
        200: "Success - Returns ordered list of teams with scores and rankings",
        **AUTH_REQUIRED_RESPONSES,
        404: "Not found - Event does not exist or has no scores",
    },
}

GET_TEAM_SCORE_DOC = {
    "description": "Get current team score, rank, and optionally recent scoring history",
    "responses": {
        200: "Success - Returns team score, rank, and optional history",
        **AUTH_REQUIRED_RESPONSES,
        404: "Not found - Team not found in event or no score exists",
    },
}

SUBMIT_ANSWER_DOC = {
    "description": "Submit an answer to a challenge question for scoring",
    "responses": {
        201: COMMON_RESPONSES[201],
        400: "Bad request - Invalid submission, exceeded max attempts, or event locked",
        **AUTH_REQUIRED_RESPONSES,
        404: "Not found - Question, challenge, or team not found",
    },
}

REDEEM_HINT_DOC = {
    "description": "Redeem a hint for a challenge, deducting points from team score",
    "responses": {
        201: COMMON_RESPONSES[201],
        400: "Bad request - Hint already redeemed, event locked, or hint doesn't belong to challenge",
        **AUTH_REQUIRED_RESPONSES,
        404: "Not found - Hint, challenge, or team not found",
    },
}

# ============ ADMIN SCORING ENDPOINTS ============
AWARD_MANUAL_POINTS_DOC = {
    "description": "Award or deduct points manually with reason for audit trail (Admin only)",
    "responses": {
        201: COMMON_RESPONSES[201],
        400: "Bad request - Invalid points value (cannot be zero) or missing reason",
        **ADMIN_REQUIRED_RESPONSES,
        404: "Not found - Team has no score in the specified event",
    },
}

RECALCULATE_SCORE_DOC = {
    "description": "Recalculate a team's score from all score events (Admin only)",
    "responses": {
        200: "Success - Score recalculated with old/new values and difference",
        **ADMIN_REQUIRED_RESPONSES,
        404: "Not found - Team has no score in the specified event",
    },
}

GET_SCORE_HISTORY_DOC = {
    "description": "Get detailed scoring history for audit and debugging purposes (Admin only)",
    "responses": {
        200: "Success - Returns list of all score events with source details",
        400: "Bad request - Invalid limit parameter (must be 1-500)",
        **ADMIN_REQUIRED_RESPONSES,
    },
}
