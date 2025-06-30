"""
Unit tests for event domain controllers
"""

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Get current UTC datetime. Replacement for deprecated datetime.utcnow()."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
