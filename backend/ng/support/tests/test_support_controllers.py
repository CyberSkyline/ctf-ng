"""
Tests support controller business logic
/backend/ng/support/tests/test_support_controllers.py
"""

import time
import pytest
from datetime import datetime, timedelta
from tests.helpers import gen_user as gen_user_original
from ..controllers.create_ticket import create_ticket
from ..controllers.list_tickets import list_tickets
from ..controllers.get_ticket import get_ticket
from ..controllers.create_ticket_message import create_ticket_message
from ..controllers.update_ticket import update_ticket
from ..controllers.admin_ticket_operations import (
    assign_ticket, close_ticket, reopen_ticket, mute_ticket, unmute_ticket
)
from ..controllers.tag_management import create_tag, update_tag, delete_tag
from ..models.Ticket import Ticket
from ..models.TicketMessage import TicketMessage
from ..models.TicketTag import TicketTag
from ..exceptions import (
    TicketNotFoundError, TicketPermissionError, TicketValidationError,
    TicketOperationError, TagNotFoundError
)


class DBWrapper:
    def __init__(self, session):
        self.session = session


def gen_unique_user(db_wrapper):
    """Generate a user with unique email to avoid conflicts."""
    timestamp = str(int(time.time() * 1000000))
    return gen_user_original(db_wrapper, name=f"user_{timestamp}", email=f"user_{timestamp}@example.com")


@pytest.mark.db
def test_create_ticket_basic(db_session):
    """Test basic ticket creation."""
    db_wrapper = DBWrapper(db_session)
    user = gen_unique_user(db_wrapper)
    
    result = create_ticket(
        subject="Test Support Ticket",
        author_id=user.id
    )
    
    assert result["success"]
    assert "ticket" in result
    assert result["ticket"]["subject"] == "Test Support Ticket"
    assert result["ticket"]["author_id"] == user.id
    assert result["ticket"]["status"] == "open"


@pytest.mark.db
def test_create_ticket_with_associations(db_session, event, team):
    """Test ticket creation with event and team associations."""
    db_wrapper = DBWrapper(db_session)
    user = gen_unique_user(db_wrapper)
    
    result = create_ticket(
        subject="Event Team Ticket",
        author_id=user.id,
        event_id=event.id,
        team_id=team.id,
        challenge_id=123  # Placeholder challenge ID
    )
    
    assert result["success"]
    ticket = result["ticket"]
    assert ticket["event_id"] == event.id
    assert ticket["team_id"] == team.id
    assert ticket["challenge_id"] == 123


@pytest.mark.db
def test_create_ticket_with_tags(db_session):
    """Test ticket creation with tags."""
    db_wrapper = DBWrapper(db_session)
    user = gen_unique_user(db_wrapper)
    
    # Create tags first
    tag1 = TicketTag.create(name="bug", color="#FF0000")
    tag2 = TicketTag.create(name="urgent", color="#FFA500")
    
    result = create_ticket(
        subject="Tagged Ticket",
        author_id=user.id,
        tag_ids=[tag1.id, tag2.id]
    )
    
    assert result["success"]
    assert len(result["ticket"]["tags"]) == 2
    assert "bug" in result["ticket"]["tags"]
    assert "urgent" in result["ticket"]["tags"]


@pytest.mark.db
def test_create_ticket_with_invalid_tag_raises_error(db_session):
    """Test that creating ticket with invalid tag ID raises error."""
    db_wrapper = DBWrapper(db_session)
    user = gen_unique_user(db_wrapper)
    
    with pytest.raises(TagNotFoundError):
        create_ticket(
            subject="Invalid Tag Ticket",
            author_id=user.id,
            tag_ids=[99999]  # Non-existent tag
        )


@pytest.mark.db
def test_list_tickets_user_only_sees_own(db_session):
    """Test that users only see their own tickets."""
    db_wrapper = DBWrapper(db_session)
    user1 = gen_unique_user(db_wrapper)
    user2 = gen_unique_user(db_wrapper)
    
    # Create tickets for both users
    ticket1 = Ticket.create(subject="User 1 Ticket", author_id=user1.id)
    ticket2 = Ticket.create(subject="User 2 Ticket", author_id=user2.id)
    
    # User 1 should only see their ticket
    result = list_tickets(user_id=user1.id, is_admin=False)
    assert result["success"]
    assert len(result["tickets"]) == 1
    assert result["tickets"][0]["id"] == ticket1.id


@pytest.mark.db
def test_list_tickets_admin_sees_all(db_session):
    """Test that admins can see all tickets."""
    db_wrapper = DBWrapper(db_session)
    user1 = gen_unique_user(db_wrapper)
    user2 = gen_unique_user(db_wrapper)
    admin = gen_unique_user(db_wrapper)
    
    # Create tickets
    Ticket.create(subject="User 1 Ticket", author_id=user1.id)
    Ticket.create(subject="User 2 Ticket", author_id=user2.id)
    
    # Admin should see all tickets
    result = list_tickets(is_admin=True)
    assert result["success"]
    assert len(result["tickets"]) >= 2


@pytest.mark.db
def test_list_tickets_status_filter(db_session):
    """Test ticket listing with status filters."""
    db_wrapper = DBWrapper(db_session)
    user = gen_unique_user(db_wrapper)
    
    # Create tickets with different statuses
    open_ticket = Ticket.create(subject="Open Ticket", author_id=user.id)
    closed_ticket = Ticket.create(subject="Closed Ticket", author_id=user.id)
    closed_ticket.close_ticket()
    muted_ticket = Ticket.create(subject="Muted Ticket", author_id=user.id)
    muted_ticket.mute_ticket()
    
    # Test open filter
    result = list_tickets(user_id=user.id, status="open", is_admin=False)
    assert len(result["tickets"]) == 1
    assert result["tickets"][0]["id"] == open_ticket.id
    
    # Test closed filter
    result = list_tickets(user_id=user.id, status="closed", is_admin=False)
    assert len(result["tickets"]) == 1
    assert result["tickets"][0]["id"] == closed_ticket.id
    
    # Test muted filter
    result = list_tickets(user_id=user.id, status="muted", is_admin=False)
    assert len(result["tickets"]) == 1
    assert result["tickets"][0]["id"] == muted_ticket.id


@pytest.mark.db
def test_get_ticket_permission_check(db_session):
    """Test get ticket permission enforcement."""
    db_wrapper = DBWrapper(db_session)
    user1 = gen_unique_user(db_wrapper)
    user2 = gen_unique_user(db_wrapper)
    
    ticket = Ticket.create(subject="Private Ticket", author_id=user1.id)
    
    # Owner can view
    result = get_ticket(ticket.id, user1.id, is_admin=False)
    assert result["success"]
    
    # Non-owner cannot view
    with pytest.raises(TicketPermissionError):
        get_ticket(ticket.id, user2.id, is_admin=False)
    
    # Admin can view any ticket
    result = get_ticket(ticket.id, user2.id, is_admin=True)
    assert result["success"]


@pytest.mark.db
def test_get_ticket_includes_messages(db_session):
    """Test that get ticket includes all messages."""
    db_wrapper = DBWrapper(db_session)
    user = gen_unique_user(db_wrapper)
    
    ticket = Ticket.create(subject="Ticket with Messages", author_id=user.id)
    
    # Add messages
    TicketMessage.create("First message", ticket.id, user.id)
    TicketMessage.create("Second message", ticket.id, user.id)
    
    result = get_ticket(ticket.id, user.id, is_admin=False)
    assert result["success"]
    assert len(result["ticket"]["messages"]) == 2


@pytest.mark.db
def test_create_ticket_message_updates_ticket(db_session):
    """Test that creating a message updates ticket timestamp."""
    db_wrapper = DBWrapper(db_session)
    user = gen_unique_user(db_wrapper)
    
    ticket = Ticket.create(subject="Message Test", author_id=user.id)
    original_updated = ticket.last_updated
    
    # Wait a moment to ensure timestamp difference
    time.sleep(0.1)
    
    result = create_ticket_message(
        ticket_id=ticket.id,
        text="Test message",
        author_id=user.id,
        is_admin=False
    )
    
    assert result["success"]
    
    # Refresh ticket
    updated_ticket = Ticket.find_by_id(ticket.id)
    assert updated_ticket.last_updated > original_updated


@pytest.mark.db
def test_create_message_on_closed_ticket_as_user_fails(db_session):
    """Test that regular users cannot reply to closed tickets."""
    db_wrapper = DBWrapper(db_session)
    user = gen_unique_user(db_wrapper)
    
    ticket = Ticket.create(subject="Closed Ticket", author_id=user.id)
    ticket.close_ticket()
    
    with pytest.raises(TicketOperationError):
        create_ticket_message(
            ticket_id=ticket.id,
            text="Cannot reply",
            author_id=user.id,
            is_admin=False
        )


@pytest.mark.db
def test_admin_reply_reopens_closed_ticket(db_session):
    """Test that admin reply reopens a closed ticket."""
    db_wrapper = DBWrapper(db_session)
    user = gen_unique_user(db_wrapper)
    admin = gen_unique_user(db_wrapper)
    
    ticket = Ticket.create(subject="Closed Ticket", author_id=user.id)
    ticket.close_ticket()
    
    result = create_ticket_message(
        ticket_id=ticket.id,
        text="Admin reopening",
        author_id=admin.id,
        is_admin=True
    )
    
    assert result["success"]
    assert result["ticket_reopened"]
    
    # Verify ticket is reopened
    updated_ticket = Ticket.find_by_id(ticket.id)
    assert updated_ticket.status == "open"


@pytest.mark.db
def test_first_admin_response_timestamp(db_session):
    """Test that first admin response timestamp is set correctly."""
    db_wrapper = DBWrapper(db_session)
    user = gen_unique_user(db_wrapper)
    admin = gen_unique_user(db_wrapper)
    
    ticket = Ticket.create(subject="Admin Response Test", author_id=user.id)
    assert ticket.first_admin_response_timestamp is None
    
    # User message shouldn't set admin response time
    create_ticket_message(ticket.id, "User message", user.id, is_admin=False)
    ticket = Ticket.find_by_id(ticket.id)
    assert ticket.first_admin_response_timestamp is None
    
    # First admin message should set it
    before_response = datetime.utcnow()
    create_ticket_message(ticket.id, "Admin message", admin.id, is_admin=True)
    after_response = datetime.utcnow()
    
    ticket = Ticket.find_by_id(ticket.id)
    assert ticket.first_admin_response_timestamp is not None
    assert before_response <= ticket.first_admin_response_timestamp <= after_response
    
    # Second admin message shouldn't change it
    original_timestamp = ticket.first_admin_response_timestamp
    create_ticket_message(ticket.id, "Another admin message", admin.id, is_admin=True)
    
    ticket = Ticket.find_by_id(ticket.id)
    assert ticket.first_admin_response_timestamp == original_timestamp


@pytest.mark.db
def test_update_ticket_user_can_only_update_subject(db_session):
    """Test that users can only update subject of their tickets."""
    db_wrapper = DBWrapper(db_session)
    user = gen_unique_user(db_wrapper)
    
    ticket = Ticket.create(subject="Original Subject", author_id=user.id)
    
    result = update_ticket(
        ticket_id=ticket.id,
        actor_id=user.id,
        is_admin=False,
        subject="Updated Subject"
    )
    
    assert result["success"]
    assert result["ticket"]["subject"] == "Updated Subject"


@pytest.mark.db
def test_update_ticket_admin_can_update_associations(db_session, event, team):
    """Test that admins can update ticket associations."""
    db_wrapper = DBWrapper(db_session)
    user = gen_unique_user(db_wrapper)
    admin = gen_unique_user(db_wrapper)
    
    ticket = Ticket.create(subject="Test Ticket", author_id=user.id)
    
    result = update_ticket(
        ticket_id=ticket.id,
        actor_id=admin.id,
        is_admin=True,
        event_id=event.id,
        team_id=team.id,
        challenge_id=456
    )
    
    assert result["success"]
    assert result["ticket"]["event_id"] == event.id
    assert result["ticket"]["team_id"] == team.id
    assert result["ticket"]["challenge_id"] == 456


@pytest.mark.db
def test_assign_ticket(db_session):
    """Test ticket assignment."""
    db_wrapper = DBWrapper(db_session)
    user = gen_unique_user(db_wrapper)
    assignee = gen_unique_user(db_wrapper)
    admin = gen_unique_user(db_wrapper)
    
    ticket = Ticket.create(subject="Unassigned Ticket", author_id=user.id)
    
    result = assign_ticket(
        ticket_id=ticket.id,
        user_id=assignee.id,
        admin_id=admin.id
    )
    
    assert result["success"]
    assert result["ticket"]["assigned_to"] == assignee.id


@pytest.mark.db
def test_ticket_lifecycle_operations(db_session):
    """Test complete ticket lifecycle: open -> closed -> reopened."""
    db_wrapper = DBWrapper(db_session)
    user = gen_unique_user(db_wrapper)
    admin = gen_unique_user(db_wrapper)
    
    # Create open ticket
    ticket = Ticket.create(subject="Lifecycle Test", author_id=user.id)
    assert ticket.status == "open"
    
    # Close ticket
    result = close_ticket(ticket.id, admin.id)
    assert result["success"]
    
    ticket = Ticket.find_by_id(ticket.id)
    assert ticket.status == "closed"
    
    # Try to close again - should fail
    with pytest.raises(TicketValidationError):
        close_ticket(ticket.id, admin.id)
    
    # Reopen ticket
    result = reopen_ticket(ticket.id, admin.id)
    assert result["success"]
    
    ticket = Ticket.find_by_id(ticket.id)
    assert ticket.status == "open"


@pytest.mark.db
def test_mute_unmute_ticket(db_session):
    """Test muting and unmuting tickets."""
    db_wrapper = DBWrapper(db_session)
    user = gen_unique_user(db_wrapper)
    admin = gen_unique_user(db_wrapper)
    
    ticket = Ticket.create(subject="Mute Test", author_id=user.id)
    
    # Mute ticket
    result = mute_ticket(ticket.id, admin.id)
    assert result["success"]
    
    ticket = Ticket.find_by_id(ticket.id)
    assert ticket.status == "muted"
    
    # Unmute ticket
    result = unmute_ticket(ticket.id, admin.id)
    assert result["success"]
    
    ticket = Ticket.find_by_id(ticket.id)
    assert ticket.status == "open"


@pytest.mark.db
def test_tag_management(db_session):
    """Test tag creation, update, and deletion."""
    # Create tag
    result = create_tag(
        name="feature-request",
        color="#00FF00",
        description="Feature requests from users"
    )
    
    assert result["success"]
    tag_id = result["tag"]["id"]
    
    # Update tag
    result = update_tag(
        tag_id=tag_id,
        name="enhancement",
        color="#0000FF"
    )
    
    assert result["success"]
    assert result["tag"]["name"] == "enhancement"
    assert result["tag"]["color"] == "#0000FF"
    
    # Delete tag
    result = delete_tag(tag_id)
    assert result["success"]
    
    # Verify deletion
    tag = TicketTag.find_by_id(tag_id)
    assert tag is None


@pytest.mark.db
def test_tag_uniqueness_enforcement(db_session):
    """Test that tag names must be unique."""
    # Create first tag
    create_tag(name="unique-tag")
    
    # Try to create duplicate
    with pytest.raises(TicketValidationError):
        create_tag(name="unique-tag")


@pytest.mark.db
def test_ticket_tag_operations(db_session):
    """Test adding and removing tags from tickets."""
    db_wrapper = DBWrapper(db_session)
    user = gen_unique_user(db_wrapper)
    
    # Create ticket and tags
    ticket = Ticket.create(subject="Tag Operations Test", author_id=user.id)
    tag1 = TicketTag.create(name="tag1")
    tag2 = TicketTag.create(name="tag2")
    
    # Add tags
    ticket.add_tags([tag1, tag2])
    assert len(ticket.tags) == 2
    
    # Remove one tag
    ticket.remove_tags([tag1])
    assert len(ticket.tags) == 1
    assert ticket.tags[0].id == tag2.id
