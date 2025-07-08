"""
Model tests for support domain
"""

import pytest
from datetime import datetime, timedelta
from ...core.exceptions import ValidationError
from ...core.utils import utc_now
from ..models.Ticket import Ticket
from ..models.TicketMessage import TicketMessage
from ..models.TicketTag import TicketTag


class TestTicketModel:
    """Tests for the Ticket model."""

    def test_repr(self, ticket):
        """Test the string representation of the model."""
        assert f"<Ticket {ticket.id}: {ticket.subject}>" == repr(ticket)

    def test_defaults(self):
        """Test the default values for a new instance."""

        ticket = Ticket()
        assert ticket.subject is None
        assert ticket.author_id is None
        assert ticket.opened_timestamp is None
        assert ticket.closed_timestamp is None
        assert ticket.assigned_to is None
        assert ticket.event_id is None
        assert ticket.team_id is None
        assert ticket.challenge_id is None
        assert ticket.muted is False
        assert ticket.first_admin_response_timestamp is None

    def test_status_property(self, ticket, closed_ticket, muted_ticket):
        """Test the computed status property."""

        assert ticket.status == "open"
        assert closed_ticket.status == "closed"
        assert muted_ticket.status == "muted"

    def test_create_ticket(self, db_session, user, event):
        """Test creating a ticket with the create method."""

        ticket = Ticket.create(
            subject="New Support Request",
            author_id=user.id,
            event_id=event.id
        )
        
        assert ticket.id is not None
        assert ticket.subject == "New Support Request"
        assert ticket.author_id == user.id
        assert ticket.event_id == event.id
        assert ticket.opened_timestamp is not None
        assert ticket.last_updated is not None
        assert ticket.status == "open"

    def test_close_ticket(self, ticket)
:
        """Test closing a ticket."""
        assert ticket.status == "open"
        assert ticket.closed_timestamp is None
        
        ticket.close_ticket()
        
        assert ticket.status == "closed"
        assert ticket.closed_timestamp is not None

    def test_reopen_ticket(self, closed_ticket):
        """Test reopening a closed ticket."""

        assert closed_ticket.status == "closed"
        
        closed_ticket.reopen_ticket()
        
        assert closed_ticket.status == "open"
        assert closed_ticket.closed_timestamp is None
        assert closed_ticket.muted is False

    def test_toggle_mute(self, ticket):
        """Test muting and unmuting a ticket."""

        assert ticket.muted is False
        
        ticket.toggle_mute(True)
        assert ticket.muted is True
        assert ticket.status == "muted"
        
        ticket.toggle_mute(False)
        assert ticket.muted is False
        assert ticket.status == "open"

    def test_assign_unassign_ticket(self, ticket, admin):
        """Test assigning and unassigning a ticket."""

        assert ticket.assigned_to is None
        
        ticket.assign_to_user(admin.id)
        assert ticket.assigned_to == admin.id
        
        ticket.unassign()
        assert ticket.assigned_to is None


    def test_find_by_methods(self, multiple_tickets, user, admin):
        """Test various find_by methods."""

        user_tickets = Ticket.find_by_author(user.id)
        assert len(user_tickets) >= 3
        
        assigned_tickets = Ticket.find_by_assigned_user(admin.id)
        assert len(assigned_tickets) >= 1
        
        open_tickets = Ticket.find_open_tickets()
        assert len(open_tickets) >= 2
        
        unassigned_tickets = Ticket.find_unassigned_open_tickets()
        assert len(unassigned_tickets) >= 1

    def test_find_filtered_tickets(self, multiple_tickets, user, admin):
        """Test filtered ticket search."""

        user_tickets = Ticket.find_filtered_tickets(
            user_id=user.id,
            status="all",
            is_admin=False
        )
        assert all(t.author_id == user.id for t in user_tickets)
        
        all_tickets = Ticket.find_filtered_tickets(
            status="all",
            is_admin=True
        )
        assert len(all_tickets) >= 4
        
        open_tickets = Ticket.find_filtered_tickets(
            status="open",
            is_admin=True
        )
        assert all(t.status == "open" for t in open_tickets)

    def test_serialize(self, ticket_with_messages, admin):
        """Test ticket serialization."""

        ticket = ticket_with_messages
        ticket.assign_to_user(admin.id)
        
        user_data = ticket.serialize(include_admin_fields=False)
        assert "id" in user_data
        assert "subject" in user_data
        assert "status" in user_data
        assert "message_count" in user_data
        assert "tags" in user_data
        assert "assigned_to" not in user_data
        assert "muted" not in user_data
        
        admin_data = ticket.serialize(include_admin_fields=True)
        assert "assigned_to" in admin_data
        assert "muted" in admin_data
        assert "first_admin_response_timestamp" in admin_data

    def test_get_ticket_stats(self, multiple_tickets):
        """Test ticket statistics."""

        stats = Ticket.get_ticket_stats()
        
        assert "total" in stats
        assert "open" in stats
        assert "closed" in stats
        assert "muted" in stats
        assert "unassigned" in stats
        assert "avg_response_time_hours" in stats
        assert "closed_today" in stats
        
        assert stats["total"] >= 4
        assert stats["open"] >= 2
        assert stats["closed"] >= 1
        assert stats["muted"] >= 1


class TestTicketMessageModel:
    """Tests for the TicketMessage model."""

    def test_repr(self, ticket_with_messages):
        """Test the string representation of the model."""

        message = ticket_with_messages.messages[0]
        assert f"<TicketMessage {message.id} on Ticket {ticket_with_messages.id}>" == repr(message)

    def test_create_message(self, db_session, ticket, user):
        """Test creating a message with the create method."""
        message = TicketMessage.create(
            text="This is a test message",
            ticket_id=ticket.id,
            author_id=user.id
        )
        
        assert message.id is not None
        assert message.text == "This is a test message"
        assert message.ticket_id == ticket.id
        assert message.author_id == user.id
        assert message.created_at is not None

    def test_find_by_ticket(self, ticket_with_messages):
        """Test finding messages by ticket."""

        messages = TicketMessage.find_by_ticket(ticket_with_messages.id)
        
        assert len(messages) == 2
        assert messages[0].created_at <= messages[1].created_at

    def test_find_by_author(self, ticket_with_messages, user):
        """Test finding messages by author."""
        messages = TicketMessage.find_by_author(user.id)
        
        assert len(messages) >= 1
        assert all(msg.author_id == user.id for msg in messages)


    def test_serialize(self, ticket_with_messages, user, admin):
        """Test message serialization."""

        user_message = ticket_with_messages.messages[0]
        admin_message = ticket_with_messages.messages[1]
        
        user_data = user_message.serialize()
        assert user_data["author_name"] == user.name
        assert user_data["author_type"] == "user"
        assert user_data["text"] == "I'm having an issue"

        admin_data = admin_message.serialize()
        assert admin_data["author_name"] == admin.name
        assert admin_data["author_type"] == "admin"
        assert admin_data["text"] == "I'll help you"


class TestTicketTagModel:
    """Tests for the TicketTag model."""

    def test_repr(self, ticket_tag):
        """Test the string representation of the model."""
        assert f"<TicketTag {ticket_tag.name}>" == repr(ticket_tag)

    def test_defaults(self):
        """Test the default values for a new instance."""
        tag = TicketTag()
        assert tag.name is None
        assert tag.color is None
        assert tag.description is None

    def test_create_tag(self, db_session):
        """Test creating a tag with the create method."""

        tag = TicketTag.create(
            name="test-tag",
            description="A test tag"
        )
        
        assert tag.id is not None
        assert tag.name == "test-tag"
        assert tag.description == "A test tag"

    def test_update_tag(self, ticket_tag):
        """Test updating tag properties."""
        ticket_tag.update_tag(
            description="Updated description"
        )
        
        assert ticket_tag.description == "Updated description"

    def test_find_by_name(self, ticket_tag):
        """Test finding a tag by name."""
        found_tag = TicketTag.find_by_name("bug")
        assert found_tag is not None
        assert found_tag.id == ticket_tag.id

    def test_get_all_tags(self, ticket_tag_factory):
        """Test getting all tags."""

        tags = [
            ticket_tag_factory(name="one"),
            ticket_tag_factory(name="two"),
            ticket_tag_factory(name="three")
        ]
        
        all_tags = TicketTag.get_all_tags()
        assert len(all_tags) >= 3
        
        tag_names = [tag.name for tag in all_tags]
        assert tag_names == sorted(tag_names)

    def test_search_tags(self, ticket_tag_factory):
        """Test searching tags by name."""

        ticket_tag_factory(name="critical")
        ticket_tag_factory(name="minor")
        ticket_tag_factory(name="feature")
        
        bug_tags = TicketTag.search_tags("minor")
        assert len(bug_tags) >= 2
        assert all("minor" in tag.name for tag in bug_tags)

    def test_serialize(self, ticket_with_tags):
        """Test tag serialization."""

        tag = ticket_with_tags.tags[0]
        data = tag.serialize()
        
        assert "id" in data
        assert "name" in data
        assert "color" in data
        assert "description" in data
        assert "ticket_count" in data
        assert data["ticket_count"] >= 1

