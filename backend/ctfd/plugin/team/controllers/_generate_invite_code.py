"""
/backend/ctfd/plugin/team/controllers/_generate_invite_code.py
Generates unique invite codes for teams.
"""

import secrets
import string
import uuid

from ... import config
from ...config import INVITE_CODE_GENERATION_ATTEMPTS
from ..models.Team import Team


# Internal use only (_ prefix); generates a unique team invite code.
def _generate_invite_code(length: int = config.INVITE_CODE_LENGTH) -> str:
    characters = string.ascii_uppercase + string.digits
    characters = (
        characters.replace("0", "").replace("O", "").replace("1", "").replace("I", "")
    )  # Remove confusing chars like 0/O and 1/I

    for attempt in range(INVITE_CODE_GENERATION_ATTEMPTS):
        code = "".join(secrets.choice(characters) for _ in range(length))
        if not Team.query.filter_by(invite_code=code).first():
            return code

    while True:
        uuid_code = str(uuid.uuid4()).replace("-", "").upper()[:length]
        if not Team.query.filter_by(invite_code=uuid_code).first():
            return uuid_code

        length += 1
        if length > config.INVITE_CODE_MAX_LENGTH:  # Prevents runaway
            raise RuntimeError(f"Unable to generate unique invite code (tried up to {length} characters)")
