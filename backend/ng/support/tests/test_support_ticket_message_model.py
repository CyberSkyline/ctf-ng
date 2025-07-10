"""
Model tests for TicketMessage
"""

from unittest.mock import patch
from ..models.TicketMessage import TicketMessage


class TestTicketMessageRepr:
    def test_repr(self, ticket_with_messages):
        """Test the string representation of the model."""
        message = ticket_with_messages.messages[0]
        assert (
            f"<TicketMessage {message.id} on Ticket {ticket_with_messages.id}>"
            == repr(message)
        )


class TestCreateMessage:
    def test_create_message(self, db_session, ticket, user):
        """Test creating a message with the create method."""
        message = TicketMessage.create_message(
            text="This is a test message", ticket_id=ticket.id, author_id=user.id
        )

        refreshed_message = TicketMessage.find_by_id(message.id)
        assert refreshed_message is not None
        assert refreshed_message.text == "This is a test message"
        assert refreshed_message.ticket_id == ticket.id
        assert refreshed_message.author_id == user.id
        assert refreshed_message.created_at is not None

    def test_create_message_respects_commit_flag(self, db_session, ticket, user):
        """Test that create respects the commit flag."""
        with patch.object(db_session, "commit") as mock_commit:
            message = TicketMessage.create_message(
                text="No commit message",
                ticket_id=ticket.id,
                author_id=user.id,
                commit=False,
            )
            mock_commit.assert_not_called()
            assert message.text == "No commit message"

        with patch.object(db_session, "commit") as mock_commit:
            message = TicketMessage.create_message(
                text="With commit message",
                ticket_id=ticket.id,
                author_id=user.id,
                commit=True,
            )
            mock_commit.assert_called_once()


class TestFindByTicket:
    def test_find_by_ticket(self, ticket_with_messages):
        """Test finding messages by ticket."""
        messages = ticket_with_messages.messages

        assert len(messages) == 2
        assert messages[0].created_at <= messages[1].created_at


class TestFindByAuthor:
    def test_find_by_author(self, ticket_with_messages, user):
        """Test finding messages by author."""
        messages = [
            msg for msg in ticket_with_messages.messages if msg.author_id == user.id
        ]

        assert len(messages) >= 1
        assert all(msg.author_id == user.id for msg in messages)


class TestSerialize:
    def test_serialize_user_message(self, ticket_with_messages, user):
        """Test serialization of user message."""
        user_message = ticket_with_messages.messages[0]

        data = user_message.serialize()
        assert data["author_name"] == user.name
        assert data["author_type"] == "user"
        assert data["text"] == "I'm having an issue"

    def test_serialize_admin_message(self, ticket_with_messages, admin):
        """Test serialization of admin message."""
        admin_message = ticket_with_messages.messages[1]

        data = admin_message.serialize()
        assert data["author_name"] == admin.name
        assert data["author_type"] == "admin"
        assert data["text"] == "I'll help you"


class TestCountByTicket:
    def test_count_by_ticket(self, ticket_with_messages):
        """Test counting messages in a ticket."""
        count = len(ticket_with_messages.messages)
        assert count == 2


class TestDeleteByTicket:
    def test_delete_by_ticket(self, ticket_with_messages, db_session):
        """Test deleting all messages for a ticket."""
        ticket_id = ticket_with_messages.id
        initial_count = len(ticket_with_messages.messages)
        assert initial_count > 0

        deleted_count = TicketMessage.delete_by_ticket(ticket_id)
        assert deleted_count == initial_count

        db_session.expire(ticket_with_messages)
        remaining_count = len(ticket_with_messages.messages)
        assert remaining_count == 0
