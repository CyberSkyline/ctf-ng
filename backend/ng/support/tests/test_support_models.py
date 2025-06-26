"""
Unit tests for support model logic without database dependencies.
/backend/ng/support/tests/test_support_models.py
"""

from datetime import datetime, timedelta
from ..models.Ticket import Ticket
from ..models.TicketMessage import TicketMessage
from ..models.TicketTag import TicketTag
from ..validators import (
    validate_ticket_creation,
    validate_ticket_message,
    validate_tag_creation
)


class TestTicketModelLogic:
    """Test Ticket model properties and methods."""

    def test_ticket_status_computation(self):
        """Test that ticket status is correctly computed from fields."""
        ticket = Ticket()
        
        # Default state - should be open
        ticket.closed_timestamp = None
        ticket.muted = False
        assert ticket.status == "open"
        
        # Closed state
        ticket.closed_timestamp = datetime.utcnow()
        ticket.muted = False
        assert ticket.status == "closed"
        
        # Muted state (takes precedence over open but not closed)
        ticket.closed_timestamp = None
        ticket.muted = True
        assert ticket.status == "muted"
        
        # Closed takes precedence over muted
        ticket.closed_timestamp = datetime.utcnow()
        ticket.muted = True
        assert ticket.status == "closed"

    def test_ticket_repr_method(self):
        """Test the string representation of Ticket model."""
        ticket = Ticket()
        ticket.id = 42
        ticket.subject = "Test Subject"
        
        repr_str = repr(ticket)
        assert "Ticket 42" in repr_str
        assert "Test Subject" in repr_str

    def test_ticket_serialization(self):
        """Test ticket serialization with and without admin fields."""
        ticket = Ticket()
        ticket.id = 1
        ticket.subject = "Test Ticket"
        ticket.author_id = 10
        ticket.opened_timestamp = datetime(2024, 1, 1, 12, 0, 0)
        ticket.last_updated = datetime(2024, 1, 1, 12, 30, 0)
        ticket.assigned_to = 20
        ticket.closed_timestamp = None
        ticket.muted = False
        ticket.tags = []
        ticket.messages = []
        
        # User serialization
        user_data = ticket.serialize(include_admin_fields=False)
        assert "id" in user_data
        assert "subject" in user_data
        assert "author_id" in user_data
        assert "status" in user_data
        assert "assigned_to" not in user_data  # Admin field
        assert "muted" not in user_data  # Admin field
        
        # Admin serialization
        admin_data = ticket.serialize(include_admin_fields=True)
        assert "assigned_to" in admin_data
        assert "muted" in admin_data
        assert "first_admin_response_timestamp" in admin_data

    def test_ticket_message_count_in_serialization(self):
        """Test that message count is included in serialization."""
        ticket = Ticket()
        ticket.messages = [TicketMessage(), TicketMessage(), TicketMessage()]
        
        data = ticket.serialize()
        assert data["message_count"] == 3


class TestTicketMessageModelLogic:
    """Test TicketMessage model properties and methods."""

    def test_message_repr_method(self):
        """Test the string representation of TicketMessage model."""
        message = TicketMessage()
        message.id = 10
        message.ticket_id = 5
        
        repr_str = repr(message)
        assert "TicketMessage 10" in repr_str
        assert "Ticket 5" in repr_str

    def test_message_text_length_limit(self):
        """Test that message text has proper length validation."""
        # Valid length
        valid_data = {"text": "A" * 4096}
        is_valid, errors = validate_ticket_message(valid_data)
        assert is_valid
        
        # Too long
        invalid_data = {"text": "A" * 4097}
        is_valid, errors = validate_ticket_message(invalid_data)
        assert not is_valid
        assert "text" in errors
        assert "4096" in errors["text"]


class TestTicketTagModelLogic:
    """Test TicketTag model properties and methods."""

    def test_tag_repr_method(self):
        """Test the string representation of TicketTag model."""
        tag = TicketTag()
        tag.name = "bug"
        
        repr_str = repr(tag)
        assert "TicketTag" in repr_str
        assert "bug" in repr_str

    def test_tag_color_validation(self):
        """Test that tag color must be valid hex code."""
        # Valid hex color
        valid_data = {"name": "test", "color": "#FF0000"}
        is_valid, errors = validate_tag_creation(valid_data)
        assert is_valid
        
        # Invalid hex color - too short
        invalid_data = {"name": "test", "color": "#FFF"}
        is_valid, errors = validate_tag_creation(invalid_data)
        assert not is_valid
        assert "color" in errors
        
        # Invalid hex color - no hash
        invalid_data = {"name": "test", "color": "FF0000"}
        is_valid, errors = validate_tag_creation(invalid_data)
        assert not is_valid
        assert "color" in errors

    def test_tag_serialization_includes_ticket_count(self):
        """Test that tag serialization includes ticket count."""
        tag = TicketTag()
        tag.id = 1
        tag.name = "urgent"
        tag.color = "#FF0000"
        tag.description = "Urgent issues"
        tag.tickets = [Ticket(), Ticket()]  # Mock tickets
        
        data = tag.serialize()
        assert data["id"] == 1
        assert data["name"] == "urgent"
        assert data["color"] == "#FF0000"
        assert data["description"] == "Urgent issues"
        assert data["ticket_count"] == 2


class TestTicketBusinessRules:
    """Test ticket-related business rules."""

    def test_ticket_subject_validation(self):
        """Test ticket subject length validation."""
        # Empty subject
        invalid_data = {"subject": ""}
        is_valid, errors = validate_ticket_creation(invalid_data)
        assert not is_valid
        assert "subject" in errors
        
        # Subject too long
        invalid_data = {"subject": "A" * 129}
        is_valid, errors = validate_ticket_creation(invalid_data)
        assert not is_valid
        assert "subject" in errors
        assert "128" in errors["subject"]
        
        # Valid subject
        valid_data = {"subject": "Valid ticket subject"}
        is_valid, errors = validate_ticket_creation(valid_data)
        assert is_valid

    def test_ticket_tag_validation(self):
        """Test ticket tag IDs validation."""
        # Valid tag IDs
        valid_data = {"subject": "Test", "tag_ids": [1, 2, 3]}
        is_valid, errors = validate_ticket_creation(valid_data)
        assert is_valid
        
        # Invalid tag IDs - not a list
        invalid_data = {"subject": "Test", "tag_ids": "not a list"}
        is_valid, errors = validate_ticket_creation(invalid_data)
        assert not is_valid
        assert "tag_ids" in errors
        
        # Invalid tag IDs - negative numbers
        invalid_data = {"subject": "Test", "tag_ids": [1, -1, 3]}
        is_valid, errors = validate_ticket_creation(invalid_data)
        assert not is_valid
        assert "tag_ids[1]" in errors

    def test_ticket_association_validation(self):
        """Test optional association field validation."""
        # All valid associations
        valid_data = {
            "subject": "Test",
            "event_id": 1,
            "team_id": 2,
            "challenge_id": 3
        }
        is_valid, errors = validate_ticket_creation(valid_data)
        assert is_valid
        
        # Invalid event_id
        invalid_data = {"subject": "Test", "event_id": -1}
        is_valid, errors = validate_ticket_creation(invalid_data)
        assert not is_valid
        assert "event_id" in errors

    def test_response_time_tracking_logic(self):
        """Test logic for tracking admin response times."""
        ticket = Ticket()
        ticket.opened_timestamp = datetime(2024, 1, 1, 10, 0, 0)
        ticket.first_admin_response_timestamp = None
        
        # No response yet
        assert ticket.first_admin_response_timestamp is None
        
        # Simulate setting first admin response
        response_time = datetime(2024, 1, 1, 10, 30, 0)
        ticket.first_admin_response_timestamp = response_time
        
        # Calculate response time
        response_delta = ticket.first_admin_response_timestamp - ticket.opened_timestamp
        assert response_delta.total_seconds() == 1800  # 30 minutes

    def test_ticket_lifecycle_timestamps(self):
        """Test ticket lifecycle timestamp management."""
        ticket = Ticket()
        
        # New ticket
        ticket.opened_timestamp = datetime.utcnow()
        ticket.closed_timestamp = None
        ticket.last_updated = ticket.opened_timestamp
        assert ticket.status == "open"
        
        # Update ticket
        update_time = datetime.utcnow() + timedelta(minutes=5)
        ticket.last_updated = update_time
        assert ticket.last_updated > ticket.opened_timestamp
        
        # Close ticket
        close_time = datetime.utcnow() + timedelta(minutes=10)
        ticket.closed_timestamp = close_time
        assert ticket.status == "closed"
        assert ticket.closed_timestamp > ticket.opened_timestamp
