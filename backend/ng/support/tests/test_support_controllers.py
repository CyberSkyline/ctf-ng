"""
Controller tests for support domain
"""

import pytest
from flask import g

from ...core.exceptions import ValidationError, NotFoundError
from ..models.Ticket import Ticket
from ..models.TicketMessage import TicketMessage
from ..models.TicketTag import TicketTag


class TestUserActionControllers:
    """Test suite for user action controllers."""

    def test_create_ticket_controller(self, app, db_session, user, event, ticket_tag_factory):
        """Test the create ticket controller creates ticket in database."""
        from ..controllers.user_actions.create_ticket import create_ticket
        
        tag = ticket_tag_factory(name="test-tag")
        
        with app.test_request_context():
            result = create_ticket(
                subject="New ticket from controller",
                author_id=user.id,
                event_id=event.id,
                tag_ids=[tag.id]
            )
            
            assert isinstance(result, dict)
            assert result["subject"] == "New ticket from controller"
            assert result["author_id"] == user.id
            assert result["event_id"] == event.id
            assert len(result["tags"]) == 1
            assert result["tags"][0]["name"] == "test-tag"
            
            created_ticket = Ticket.find_by_id(result["id"])
            assert created_ticket is not None
            assert created_ticket.subject == "New ticket from controller"
            assert created_ticket.author_id == user.id
            assert created_ticket.event_id == event.id
            assert created_ticket.status == "open"
            assert len(created_ticket.tags) == 1
            assert created_ticket.tags[0].name == "test-tag"


class TestAllActionControllers:
    """Tests for controllers available to all users."""

    def test_list_tickets_controller_user(self, app, multiple_tickets, user):
        """Test listing tickets as a regular user."""
        from ..controllers.all_actions.list_tickets import list_tickets
        
        with app.test_request_context():

            result = list_tickets(
                user_id=user.id,
                status="all",
                is_admin=False
            )
            
            assert isinstance(result, list)
            assert all(isinstance(t, Ticket) for t in result)
            assert all(t.author_id == user.id for t in result)

            user_ticket_count = Ticket.query.filter_by(author_id=user.id).count()
            assert len(result) == user_ticket_count

            for ticket in result:
                assert hasattr(ticket, 'subject')
                assert hasattr(ticket, 'status')
                assert hasattr(ticket, 'created_at')

    def test_list_tickets_controller_admin(self, app, multiple_tickets):
        """Test listing tickets as an admin."""
        from ..controllers.all_actions.list_tickets import list_tickets
        
        with app.test_request_context():

            result = list_tickets(
                status="all",
                is_admin=True
            )
            
            assert isinstance(result, list)
            assert len(result) >= 4
            
            total_tickets = Ticket.query.count()
            assert len(result) == total_tickets

            author_ids = set(t.author_id for t in result)
            assert len(author_ids) > 1

    def test_list_tickets_filtered(self, app, multiple_tickets):
        """Test listing tickets with filters."""
        from ..controllers.all_actions.list_tickets import list_tickets
        
        with app.test_request_context():
            open_tickets = list_tickets(status="open", is_admin=True)
            assert all(t.status == "open" for t in open_tickets)
            
            closed_tickets = list_tickets(status="closed", is_admin=True)
            assert all(t.status == "closed" for t in closed_tickets)

    def test_get_ticket_controller(self, app, ticket_with_messages, user):
        """Test getting ticket details retrieves actual data."""
        from ..controllers.all_actions.get_ticket import get_ticket
        
        with app.test_request_context():
            result = get_ticket(
                ticket_id=ticket_with_messages.id,
                user_id=user.id,
                is_admin=False
            )
            
            assert isinstance(result, dict)
            assert "ticket" in result
            assert "messages" in result
            assert result["ticket"]["id"] == ticket_with_messages.id
            assert len(result["messages"]) == 2
            
            db_ticket = Ticket.find_by_id(ticket_with_messages.id)
            assert result["ticket"]["subject"] == db_ticket.subject
            assert result["ticket"]["status"] == db_ticket.status
            
            db_messages = db_ticket.messages
            assert len(result["messages"]) == len(db_messages)
            for i, msg in enumerate(result["messages"]):
                assert msg["text"] == db_messages[i].text
                assert msg["author_id"] == db_messages[i].author_id

    def test_get_ticket_not_found(self, app, user):
        """Test getting non-existent ticket."""
        from ..controllers.all_actions.get_ticket import get_ticket
        
        with app.test_request_context():
            with pytest.raises(NotFoundError):
                get_ticket(
                    ticket_id=99999,
                    user_id=user.id,
                    is_admin=False
                )

    def test_create_ticket_message_controller(self, app, ticket, user):
        """Test creating a ticket message saves to database."""
        from ..controllers.all_actions.create_ticket_message import create_ticket_message
        
        initial_message_count = len(ticket.messages)
        initial_update_time = ticket.last_updated
        
        with app.test_request_context():
            result = create_ticket_message(
                ticket_id=ticket.id,
                text="New message content",
                user_id=user.id,
                is_admin=False
            )
            
            assert isinstance(result, dict)
            assert "message" in result
            assert result["message"]["text"] == "New message content"
            assert "ticket_reopened" in result
            assert result["ticket_reopened"] is False
            
            db_session.refresh(ticket)
            assert len(ticket.messages) == initial_message_count + 1
            new_message = ticket.messages[-1]
            assert new_message.text == "New message content"
            assert new_message.author_id == user.id
            assert new_message.is_admin_message is False
            
            assert ticket.last_updated > initial_update_time

    def test_create_message_reopens_closed_ticket(self, app, closed_ticket, admin, db_session):
        """Test admin message reopens closed ticket."""
        from ..controllers.all_actions.create_ticket_message import create_ticket_message
        
        assert closed_ticket.status == "closed"
        assert closed_ticket.closed_timestamp is not None
        
        with app.test_request_context():
            result = create_ticket_message(
                ticket_id=closed_ticket.id,
                text="Admin follow-up",
                user_id=admin.id,
                is_admin=True
            )
            
            assert result["ticket_reopened"] is True
            
            db_session.refresh(closed_ticket)
            assert closed_ticket.status == "open"
            assert closed_ticket.closed_timestamp is None
            
            admin_message = closed_ticket.messages[-1]
            assert admin_message.text == "Admin follow-up"
            assert admin_message.is_admin_message is True

    def test_update_ticket_controller(self, app, ticket, user, db_session):
        """Test updating a ticket."""
        from ..controllers.all_actions.update_ticket import update_ticket
        
        original_subject = ticket.subject
        
        with app.test_request_context():
            result = update_ticket(
                ticket_id=ticket.id,
                user_id=user.id,
                is_admin=False,
                subject="Updated subject"
            )
            
            assert isinstance(result, dict)
            assert result["ticket"]["subject"] == "Updated subject"
            
            db_session.refresh(ticket)
            assert ticket.subject == "Updated subject"
            assert ticket.subject != original_subject

    def test_update_ticket_admin_fields(self, app, ticket, admin, db_session):
        """Test admin updating ticket with admin fields."""
        from ..controllers.all_actions.update_ticket import update_ticket
        
        assert ticket.muted is False
        assert ticket.event_id is not None
        
        with app.test_request_context():
            result = update_ticket(
                ticket_id=ticket.id,
                user_id=admin.id,
                is_admin=True,
                subject="Admin update",
                muted=True,
                event_id=None
            )
            
            assert result["ticket"]["subject"] == "Admin update"
            assert result["ticket"]["muted"] is True
            
            db_session.refresh(ticket)
            assert ticket.subject == "Admin update"
            assert ticket.muted is True
            assert ticket.event_id is None


class TestAdminActionControllers:
    """Tests for admin action controllers."""

    def test_assign_ticket_controller(self, app, ticket, admin, db_session):
        """Test assigning a ticket updates database."""
        from ..controllers.admin_actions.assign_ticket import assign_ticket
        
        assert ticket.assigned_to is None
        
        with app.test_request_context():
            result = assign_ticket(
                ticket_id=ticket.id,
                assignee_id=admin.id
            )
            
            assert isinstance(result, dict)
            assert result["ticket"]["assigned_to"] == admin.id
            assert "assigned_user_name" in result
            assert result["assigned_user_name"] == admin.display_name
            
            db_session.refresh(ticket)
            assert ticket.assigned_to == admin.id

    def test_unassign_ticket_controller(self, app, assigned_ticket, db_session):
        """Test unassigning a ticket."""
        from ..controllers.admin_actions.unassign_ticket import unassign_ticket
        
        assert assigned_ticket.assigned_to is not None
        original_assignee = assigned_ticket.assigned_to
        
        with app.test_request_context():
            result = unassign_ticket(ticket_id=assigned_ticket.id)
            
            assert isinstance(result, dict)
            assert result["ticket"]["assigned_to"] is None
            
            db_session.refresh(assigned_ticket)
            assert assigned_ticket.assigned_to is None
            assert assigned_ticket.assigned_to != original_assignee

    def test_close_ticket_controller(self, app, ticket, db_session):
        """Test closing a ticket sets status and timestamp."""
        from ..controllers.admin_actions.close_ticket import close_ticket
        
        assert ticket.status == "open"
        assert ticket.closed_timestamp is None
        
        with app.test_request_context():
            result = close_ticket(ticket_id=ticket.id)
            
            assert isinstance(result, dict)
            assert result["ticket"]["status"] == "closed"
            
            db_session.refresh(ticket)
            assert ticket.status == "closed"
            assert ticket.closed_timestamp is not None

    def test_reopen_ticket_controller(self, app, closed_ticket, db_session):
        """Test reopening a ticket clears closed timestamp."""
        from ..controllers.admin_actions.reopen_ticket import reopen_ticket
        
        assert closed_ticket.status == "closed"
        assert closed_ticket.closed_timestamp is not None
        
        with app.test_request_context():
            result = reopen_ticket(ticket_id=closed_ticket.id)
            
            assert isinstance(result, dict)
            assert result["ticket"]["status"] == "open"
            
            db_session.refresh(closed_ticket)
            assert closed_ticket.status == "open"
            assert closed_ticket.closed_timestamp is None

    def test_get_ticket_statistics_controller(self, app, multiple_tickets):
        """Test getting ticket statistics reflects actual database counts."""
        from ..controllers.admin_actions.get_ticket_statistics import get_ticket_statistics
        
        total_count = Ticket.query.count()
        open_count = Ticket.query.filter_by(closed_timestamp=None, muted=False).count()
        closed_count = Ticket.query.filter(Ticket.closed_timestamp.isnot(None)).count()
        
        with app.test_request_context():
            result = get_ticket_statistics()
            
            assert isinstance(result, dict)
            assert "stats" in result
            stats = result["stats"]
            assert "total" in stats
            assert "open" in stats
            assert "closed" in stats
            assert "muted" in stats
            assert "unassigned" in stats
            assert "avg_response_time_hours" in stats
            
            assert stats["total"] == total_count
            assert stats["open"] == open_count
            assert stats["closed"] == closed_count
            assert stats["open"] + stats["closed"] == stats["total"]


class TestTagManagementControllers:
    """Tests for tag management controllers."""

    def test_create_tag_controller(self, app, db_session):
        """Test creating a tag saves to database."""
        from ..controllers.admin_actions.tag_management import create_tag
        
        with app.test_request_context():
            result = create_tag(
                name="new-tag",
                description="Test tag"
            )
            
            assert isinstance(result, dict)
            assert result["tag"]["name"] == "new-tag"
            assert result["tag"]["description"] == "Test tag"
            
            created_tag = TicketTag.find_by_id(result["tag"]["id"])
            assert created_tag is not None
            assert created_tag.name == "new-tag"
            assert created_tag.color == "#123456"
            assert created_tag.description == "Test tag"

    def test_create_duplicate_tag(self, app, ticket_tag):
        """Test creating duplicate tag fails."""
        from ..controllers.admin_actions.tag_management import create_tag
        
        with app.test_request_context():
            with pytest.raises(ValidationError) as exc_info:
                create_tag(name="bug") 
            assert "already exists" in str(exc_info.value)

    def test_update_tag_controller(self, app, ticket_tag, db_session):
        """Test updating a tag modifies database."""
        from ..controllers.admin_actions.tag_management import update_tag
        
        original_color = ticket_tag.color
        original_description = ticket_tag.description
        
        with app.test_request_context():
            result = update_tag(
                tag_id=ticket_tag.id,
                color="#FFFFFF",
                description="Updated description"
            )
            
            assert isinstance(result, dict)
            assert result["tag"]["color"] == "#FFFFFF"
            assert result["tag"]["description"] == "Updated description"

            db_session.refresh(ticket_tag)
            assert ticket_tag.color == "#FFFFFF"
            assert ticket_tag.color != original_color
            assert ticket_tag.description == "Updated description"
            assert ticket_tag.description != original_description

    def test_delete_tag_controller(self, app, ticket_tag_factory, db_session):
        """Test deleting a tag removes from database."""
        from ..controllers.admin_actions.tag_management import delete_tag
        
        tag = ticket_tag_factory(name="to-delete")
        tag_id = tag.id
        
        assert TicketTag.find_by_id(tag_id) is not None
        
        with app.test_request_context():
            result = delete_tag(tag_id=tag_id)
            
            assert result["success"] is True
            
            db_session.expire_all()
            assert TicketTag.find_by_id(tag_id) is None

    def test_list_tags_controller(self, app, ticket_tag_factory, db_session):
        """Test listing all tags retrieves from database."""
        from ..controllers.admin_actions.tag_management import list_tags
        
        tag1 = ticket_tag_factory(name="tag1")
        tag2 = ticket_tag_factory(name="tag2")
        
        with app.test_request_context():
            result = list_tags()
            
            assert isinstance(result, dict)
            assert "tags" in result
            assert len(result["tags"]) >= 2
            
            tag_names = [tag["name"] for tag in result["tags"]]
            assert "tag1" in tag_names
            assert "tag2" in tag_names

            db_tag_count = TicketTag.query.count()
            assert len(result["tags"]) == db_tag_count

    def test_add_tags_to_ticket_controller(self, app, ticket, ticket_tag_factory, db_session):
        """Test adding tags to a ticket updates database."""
        from ..controllers.admin_actions.tag_management import add_tags_to_ticket
        
        tag1 = ticket_tag_factory(name="add-tag-1")
        tag2 = ticket_tag_factory(name="add-tag-2")
        
        assert len(ticket.tags) == 0
        
        with app.test_request_context():
            result = add_tags_to_ticket(
                ticket_id=ticket.id,
                tag_ids=[tag1.id, tag2.id]
            )
            
            assert isinstance(result, dict)
            assert len(result["ticket"]["tags"]) == 2
            
            db_session.refresh(ticket)
            assert len(ticket.tags) == 2
            tag_names = [tag.name for tag in ticket.tags]
            assert "add-tag-1" in tag_names
            assert "add-tag-2" in tag_names

    def test_remove_tags_from_ticket_controller(self, app, ticket_with_tags, db_session):
        """Test removing tags from a ticket updates database."""
        from ..controllers.admin_actions.tag_management import remove_tags_from_ticket
        
        initial_tag_count = len(ticket_with_tags.tags)
        tag_to_remove = ticket_with_tags.tags[0]
        tag_to_keep = ticket_with_tags.tags[1]
        
        with app.test_request_context():
            result = remove_tags_from_ticket(
                ticket_id=ticket_with_tags.id,
                tag_ids=[tag_to_remove.id]
            )
            
            assert isinstance(result, dict)
            assert len(result["ticket"]["tags"]) == initial_tag_count - 1

            db_session.refresh(ticket_with_tags)
            assert len(ticket_with_tags.tags) == initial_tag_count - 1
            assert tag_to_remove not in ticket_with_tags.tags
            assert tag_to_keep in ticket_with_tags.tags

