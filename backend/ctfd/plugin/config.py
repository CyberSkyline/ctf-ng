"""
/backend/ctfd/plugin/config.py
Defines static, system wide config values and constants
"""

# Team Config (fallback)
MAX_TEAM_SIZE = 8

# Database Field Length Limits
TEAM_NAME_MAX_LENGTH = 128
EVENT_NAME_MAX_LENGTH = 256
EVENT_DESCRIPTION_MAX_LENGTH = 1000
TEAM_ROLE_MAX_LENGTH = 50
INVITE_CODE_MAX_LENGTH = 32

# Invite Code Config
INVITE_CODE_LENGTH = 8
INVITE_CODE_GENERATION_ATTEMPTS = 10

# Admin Operation Confirmations
ADMIN_RESET_CONFIRMATION = "--confirm-reset"
ADMIN_EVENT_RESET_CONFIRMATION = "--delete-event"

# Health Check Thresholds
EMPTY_TEAMS_WARNING_THRESHOLD = 0.5
