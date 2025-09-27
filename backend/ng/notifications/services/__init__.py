"""
Notification Service Package
"""

from .email_templates import TicketEmailTemplates
from .notification_service import NotificationService
from .email_service import get_email_service, AWSEmailService

__all__ = [
    "NotificationService",
    "get_email_service",
    "AWSEmailService",
    "TicketEmailTemplates",
]
