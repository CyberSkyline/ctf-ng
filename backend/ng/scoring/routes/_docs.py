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
    "params": {
        "limit": {
            "description": "Maximum number of teams to return on leaderboard",
            "required": False,
            "type": "integer",
            "example": 50,
            "default": 100
        }
    },
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
    "params": {
        "submission": {
            "description": "Answer submission text (4096 character max length)",
            "in": "body",
            "required": True,
            "type": "string",
            "example": "flag{example_answer}"
        }
    },
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
    "params": {
        "points": {
            "description": "Points to award (positive) or deduct (negative). Cannot be zero.",
            "in": "body",
            "required": True,
            "type": "integer",
            "example": 50
        },
        "reason": {
            "description": "Reason for manual point adjustment (512 character max length)",
            "in": "body",
            "required": True,
            "type": "string",
            "example": "Bonus points for creative solution"
        }
    },
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
    "params": {
        "limit": {
            "description": "Maximum number of score events to return",
            "required": False,
            "type": "integer",
            "example": 100,
            "default": 50
        }
    },
    "responses": {
        200: "Success - Returns list of all score events with source details",
        400: "Bad request - Invalid limit parameter (must be 1-500)",
        **ADMIN_REQUIRED_RESPONSES,
    },
}

GET_TEAM_SCORE_EVENTS_DOC = {
    "description": "Get team's score events timeline with embedded source data (attempts, hint redemptions, manual awards) and names (Admin only)",
    "responses": {
        200: {
            "description": "Success - Returns timeline of score events with embedded source data",
            "example": {
                "score_events": [
                    {
                        "id": 1,
                        "score_id": 10,
                        "team_id": 5,
                        "team_name": "Elite Hackers",
                        "points": 100,
                        "timestamp": "2025-01-15T10:30:00Z",
                        "source_type": "attempt",
                        "source": {
                            "id": 45,
                            "user_id": 12,
                            "user_name": "alice",
                            "team_id": 5,
                            "team_name": "Elite Hackers",
                            "challenge_id": 3,
                            "challenge_name": "Web Challenge 1",
                            "question_id": 7,
                            "question_name": "Find the flag",
                            "submission": "flag{found_it}",
                            "is_correct": True,
                            "points": 100,
                            "timestamp": "2025-01-15T10:30:00Z"
                        }
                    },
                    {
                        "id": 2,
                        "score_id": 10,
                        "team_id": 5,
                        "team_name": "Elite Hackers",
                        "points": -10,
                        "timestamp": "2025-01-15T10:35:00Z",
                        "source_type": "hint_redemption",
                        "source": {
                            "id": 23,
                            "hint_id": 8,
                            "hint_preview": "Check the headers",
                            "user_id": 12,
                            "user_name": "alice",
                            "team_id": 5,
                            "team_name": "Elite Hackers",
                            "points": -10,
                            "timestamp": "2025-01-15T10:35:00Z"
                        }
                    },
                    {
                        "id": 3,
                        "score_id": 10,
                        "team_id": 5,
                        "team_name": "Elite Hackers",
                        "points": 50,
                        "timestamp": "2025-01-15T11:00:00Z",
                        "source_type": "manual_award",
                        "source": {
                            "id": 3,
                            "admin_id": 1,
                            "admin_name": "admin",
                            "team_id": 5,
                            "team_name": "Elite Hackers",
                            "points": 50,
                            "reason": "Bonus for creative solution",
                            "timestamp": "2025-01-15T11:00:00Z"
                        }
                    }
                ]
            }
        },
        **ADMIN_REQUIRED_RESPONSES,
        404: "Not found - Event or team does not exist",
    },
}
