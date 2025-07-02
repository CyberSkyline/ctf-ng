"""
Unit tests for admin domain validation
"""

import pytest
from ...core.exceptions import ValidationError
from ...core.validation import validate_admin_reset, validate_admin_event_reset
from ... import config


class TestAdminValidation:
    """Test admin operation validations."""

    def test_admin_reset_confirmation_required(self):
        """Test that admin reset requires specific confirmation."""

        with pytest.raises(ValidationError) as exc_info:
            validate_admin_reset({})
        assert "confirmation" in exc_info.value.errors

        with pytest.raises(ValidationError) as exc_info:
            validate_admin_reset({"confirm": "yes please"})
        assert "confirmation" in exc_info.value.errors

        result = validate_admin_reset({"confirm": config.ADMIN_RESET_CONFIRMATION})
        assert result is not None

    def test_admin_event_reset_confirmation_required(self):
        """Test that event reset requires specific confirmation."""

        with pytest.raises(ValidationError) as exc_info:
            validate_admin_event_reset({})
        assert "confirmation" in exc_info.value.errors

        result = validate_admin_event_reset({"confirm": config.ADMIN_EVENT_RESET_CONFIRMATION})
        assert result is not None
