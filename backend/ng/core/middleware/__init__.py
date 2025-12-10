"""
Middleware System for the CTF-NG plugin.

This package provides a suite of decorators to handle authentication,
resource loading, and permission checking for API endpoints.
"""

from .error_handler import handle_exceptions
from .auth import (
    api_endpoint,
    user_endpoint,
    admin_endpoint,
    public_endpoint,
)
from .ownership_middleware import check_ownership
from .attachment_permission import check_attachment_ownership

__all__ = [
    # Core Decorators
    "handle_exceptions",
    "api_endpoint",
    "user_endpoint",
    "admin_endpoint",
    "public_endpoint",
    "check_ownership",
    "check_attachment_ownership",
]
