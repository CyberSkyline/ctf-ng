import json
import os
import time
from datetime import UTC, datetime
from typing import cast
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import typst

from ...config import CERTIFICATES_DIR
from ...core.utils import utc_now
from ...core.utils.logger import get_logger
from ...core.exceptions import BusinessLogicError, NotFoundError
from ...event.controllers.user.get_challenge_progress import get_challenge_progress

from ...challenge.models.Challenge import Challenge
from ...event.models.Event import Event
from ...team.models.Team import Team
from ...user.models.User import User

logger = get_logger(__name__)

DEFAULT_TZ = "America/New_York"

# Convert dates into typst-readable JSON objects.
def local_date(dt: datetime, tz: str | None) -> dict[str, int]:
    # a missing or unrecognized IANA zone (e.g. a garbage ?tz= param) falls back to the default
    try:
        zone = ZoneInfo(tz or DEFAULT_TZ)
    except (ZoneInfoNotFoundError, ValueError):
        zone = ZoneInfo(DEFAULT_TZ)

    # if we get a naive timestamp, assume UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)

    local = dt.astimezone(zone)
    return {"year": local.year, "month": local.month, "day": local.day}

# Shared Typst compiler instance for certificate generation.
# Ensures that the parse trees and unchanging parts of documents are memoized and reused between compile runs.
compiler = typst.Compiler(
  root=CERTIFICATES_DIR,
  font_paths=[os.path.join(CERTIFICATES_DIR, 'fonts')]
)

class CertificateService:
    @staticmethod
    def render_certificate(user: User, team: Team, event: Event, challenge: Challenge | None = None, tz: str | None = None) -> bytes:
        # error if no certificate configured for the event
        if not event.certificate_file:
            raise NotFoundError("This event does not have a certificate.")

        if event.practice and challenge is None:
            # practice events issue certificates per challenge, so challenge must be passed.
            raise NotFoundError("This event issues certificates per challenge.")
        if not event.practice and challenge is not None:
            # don't allow per-challenge certs for competition challenges.
            # remove this gate if we want to allow this in the future.
            raise NotFoundError("This event does not issue per-challenge certificates.")

        progress = get_challenge_progress(event_id=event.id, team_id=team.id)

        if event.practice:
            # challenge must be fully solved, and the cert dates from that completion
            solved = next((p for p in progress if p["challenge_id"] == challenge.id and p["is_completed"]), None)
            cert_date = datetime.fromisoformat(solved["completed_at"]) if solved else None
        else:
            now = utc_now().replace(tzinfo=None)
            # team must have started and finished, if event has an end date it must also have passed
            available = (
                team.start_timestamp is not None
                and team.end_time is not None
                and team.end_time <= now
                and (event.end_time is None or event.end_time <= now)
            )
            cert_date = team.end_time if available else None

        if cert_date is None:
            raise BusinessLogicError("This certificate is not yet available.")

        # the template is the only consumer, so pass the fields it renders instead of whole serialized models
        data = {
            "user_name": user.ctfd_user.name,
            "event_name": event.name,
            "challenge": {"name": challenge.name, "summary": challenge.summary or ""} if challenge else None,
            "date": local_date(cert_date, tz),
            "time_limit_hours": round(event.time_limit_minutes / 60, 1) if event.time_limit_minutes else None,
            "challenges_attempted": [p["challenge_name"] for p in progress if p["num_questions_solved"] > 0],
        }

        start = time.perf_counter()

        # if the compile fails, will emit a 500 to the user and log to sentry via global error handling.
        # error message will be masked in prod.
        pdf = compiler.compile(
          os.path.join(CERTIFICATES_DIR, event.certificate_file),
          # validate against PDF/UA-1. (https://en.wikipedia.org/wiki/PDF/UA)
          # a document that does not meet accessibility standards will fail to compile.
          pdf_standards=["ua-1"],
          # available as sys.inputs.data inside the .typ compilation.
          sys_inputs={"data": json.dumps(data)}
        )

        logger.info(
            "Compiled certificate %s for user %s in %.1fms",
            event.certificate_file, user.id, (time.perf_counter() - start) * 1000
        )

        return cast(bytes, pdf)
