"""
Unit tests for support domain validation
"""

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Get current UTC datetime. Replacement for deprecated datetime.utcnow()."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class ValidationError(Exception):
    def __init__(self, message, errors=None):
        self.message = message
        self.errors = errors or {}
        super().__init__(message)


class TestTicketValidation:
    """Test ticket validation logic."""

    def test_ticket_subject_validation(self):
        """Test ticket subject validation rules."""

        def validate_ticket_subject(subject):
            errors = []

            if not subject or not subject.strip():
                errors.append("Subject is required")
            elif len(subject.strip()) < 5:
                errors.append("Subject must be at least 5 characters")
            elif len(subject) > 200:
                errors.append("Subject must be less than 200 characters")

            return errors

        assert validate_ticket_subject("") == ["Subject is required"]
        assert validate_ticket_subject("Hi") == ["Subject must be at least 5 characters"]
        assert validate_ticket_subject("A" * 201) == ["Subject must be less than 200 characters"]
        assert validate_ticket_subject("Valid ticket subject") == []

    def test_attachment_validation(self):
        """Test ticket attachment validation logic."""

        def validate_attachment(filename, size_bytes):
            errors = []
            max_size = 10 * 1024 * 1024  # 10MB
            allowed_extensions = [
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".pdf",
                ".txt",
                ".log",
            ]

            if size_bytes > max_size:
                errors.append(f"File size must be less than {max_size // (1024 * 1024)}MB")

            extension = filename.lower().split(".")[-1] if "." in filename else ""
            if f".{extension}" not in allowed_extensions:
                errors.append(f"File type .{extension} not allowed")

            return errors

        assert validate_attachment("test.exe", 1024) == ["File type .exe not allowed"]
        assert validate_attachment("test.jpg", 15 * 1024 * 1024) == ["File size must be less than 10MB"]
        assert validate_attachment("test.pdf", 1024) == []

    def test_ticket_status_validation(self):
        """Test ticket status validation rules."""
        valid_statuses = ["open", "in_progress", "resolved", "closed", "escalated"]

        def validate_status(status):
            if status not in valid_statuses:
                return False, f"Invalid status: {status}"
            return True, None

        assert validate_status("open")[0] is True
        assert validate_status("invalid")[0] is False
        assert "Invalid status" in validate_status("invalid")[1]
