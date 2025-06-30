"""
Generates unique invite codes for teams.
"""

import secrets
import string
import uuid

from ... import config
from ..models.Team import Team

INVITE_CODE_GENERATION_ATTEMPTS = config.INVITE_CODE_GENERATION_ATTEMPTS
INVITE_CODE_LENGTH = config.INVITE_CODE_LENGTH
INVITE_CODE_MAX_LENGTH = config.INVITE_CODE_MAX_LENGTH


# Internal use only (_ prefix); generates a unique team invite code.
def _generate_invite_code(length: int = INVITE_CODE_LENGTH) -> str:
    characters = string.ascii_uppercase + string.digits
    characters = (
        characters.replace("0", "").replace("O", "").replace("1", "").replace("I", "")
    )  # Remove confusing chars like 0/O and 1/I

    for attempt in range(INVITE_CODE_GENERATION_ATTEMPTS):
        code = "".join(secrets.choice(characters) for _ in range(length))
        if Team.is_invite_code_unique(code):
            return code

    while True:
        uuid_code = str(uuid.uuid4()).replace("-", "").upper()[:length]
        if Team.is_invite_code_unique(uuid_code):
            return uuid_code

        length += 1
        if length > INVITE_CODE_MAX_LENGTH:  # Prevents runaway
            raise RuntimeError(f"Unable to generate unique invite code (tried up to {length} characters)")
