"""
Defines static, system wide config values and constants
"""

# Team Model Field Length Limits
MAX_TEAM_SIZE = 8
TEAM_NAME_MAX_LENGTH = 128
TEAM_ROLE_MAX_LENGTH = 50

# Event Model Field Length Limits
EVENT_NAME_MAX_LENGTH = 256
EVENT_DESCRIPTION_MAX_LENGTH = 1000

# Invite Code Config
INVITE_CODE_LENGTH = 8
INVITE_CODE_GENERATION_ATTEMPTS = 10
INVITE_CODE_MAX_LENGTH = 32

# Support Model Fields Length Limits
TICKET_SUBJECT_MAX_LENGTH = 128
TICKET_MESSAGE_MAX_LENGTH = 4096
TICKET_TAG_NAME_MAX_LENGTH = 50
TICKET_TAG_DESCRIPTION_MAX_LENGTH = 200
TICKET_TAG_COLOR_MAX_LENGTH = 7 # Hex color code like #FF0000

# Support ticket attachment upload config
TICKET_ATTACHMENT_MAX_SIZE = 5 * 1024 * 1024  # 5MB in bytes
TICKET_ATTACHMENT_ALLOWED_TYPES = ['image/png', 'image/jpeg', 'image/webp']
TICKET_ATTACHMENT_S3_KEY_MAX_LENGTH = 512
TICKET_ATTACHMENT_BUCKET_NAME_MAX_LENGTH = 256
TICKET_ATTACHMENT_FILENAME_MAX_LENGTH = 256
TICKET_ATTACHMENT_CONTENT_TYPE_MAX_LENGTH = 128
S3_TICKET_ATTACHMENTS_PREFIX = "support-tickets"

# Support ticket attachment download endpoints
TICKET_ATTACHMENT_DOWNLOAD_PATH = "/ng/support/attachments"

# Public file upload configuration
PUBLIC_FILE_ALLOWED_FOLDERS = {
    'sponsor-logos': ['image/png', 'image/jpeg', 'image/webp', 'image/svg+xml'],
    'event-cards': ['image/png', 'image/jpeg', 'image/webp', 'image/svg+xml'],
    'favicons': ['image/x-icon', 'image/png', 'image/jpeg', 'image/webp', 'image/svg+xml']
}

# Auto-numbering configuration for file uploads
# Maximum number to try when auto-numbering duplicate filenames (e.g., file_1.png, file_2.png, etc)
PUBLIC_FILE_AUTO_NUMBER_MAX_ATTEMPTS = 999

# S3 URL expiration configuration
S3_UPLOAD_URL_EXPIRATION = 3600
S3_DOWNLOAD_URL_EXPIRATION = 600

# Scoring Cache Config & Model Length Limits
LEADERBOARD_CACHE_TIMEOUT = 60  # Seconds
MAX_SUBMISSION_LENGTH = 4096
MANUAL_AWARD_REASON_MAX_LENGTH = 512
DEFAULT_LEADERBOARD_LIMIT = 100
DEFAULT_SCORE_HISTORY_LIMIT = 50
MAX_LEADERBOARD_LIMIT = 1000
MAX_SCORE_HISTORY_LIMIT = 500

# Hint Model Field Length Limits
MAX_HINT_PREVIEW_LENGTH = 256
MAX_HINT_BODY_LENGTH = 1024
MAX_HINT_NAME_LENGTH = 128

NOTIFICATIONS_TITLE_MAX_LENGTH = 200
NOTIFICATIONS_MESSAGE_MAX_LENGTH = 1000

# Docker host config
# This will eventually be an array but just single host for mvp
DOCKER_HOST = "172.17.0.1"

# This is a place holder vnc image
# Default credentials for consol/debian-xfce-vnc: VNC password and root password are both "vncpassword"
# See README.md "Default Container Credentials" section for more details
NOVNC_CONTAINER = "consol/debian-xfce-vnc"
NOVNC_PORT = 8080
# For Testing
CTFD_BASE_URL = "http://localhost:8001"

CONTAINER_REGISTRY_USER = ""
CONTAINER_REGISTRY_PASSWORD = ""

# Email notification URL paths - Frontend routes
TICKET_URL_PATH = "/support"
ADMIN_TICKET_URL_PATH = "/admin/tickets"
