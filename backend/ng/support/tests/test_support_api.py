"""
API Tests for support ticket endpoints
/backend/ng/support/tests/test_support_api.py
"""

import time
import pytest
from CTFd.models import db as _db
from tests.helpers import gen_user
from ..models.Ticket import Ticket
from ..models.TicketMessage import TicketMessage
from ..models.TicketTag import TicketTag
from ....core.testing.helpers import login_as

pytestmark = pytest.mark.db


def test_tickets_endpoint_requires_authentication(client):
    """Check that ticket endpoints require authentication."""
    response = client.get("/ng/support/tickets")
    assert response.status_code == 302
    assert response.location is not None


def test_create_ticket(logged_in_client):
    """Test creating a support ticket."""
    data = {
        "subject": "Test Support Request"
    }
    response = logged_in_client.post("/ng/support/tickets", json=data)
    
    assert response.status_code == 201
    response_data = response.get_json()
    assert response_data["success"]
    assert response_data["data"]["ticket"]["subject"] == "Test Support Request"
    assert response_data["data"]["ticket"]["status"] == "open"


def test_create_ticket_with_associations(logged_in_client, event, team):
    """Test creating a ticket with event and team associations."""
    data = {
        "subject": "Event Team Support",
        "event_id": event.id,
        "team_id": team.id,
        "challenge_id": 123
    }
    response = logged_in_client.post("/ng/support/tickets", json=data)
    
    assert response.status_code == 201
    response_data = response.get_json()
    ticket = response_data["data"]["ticket"]
    assert ticket["event_id"] == event.id
    assert ticket["team_id"] == team.id
    assert ticket["challenge_id"] == 123


def test_create_ticket_validation(logged_in_client):
    """Test ticket creation validation."""
    # Empty subject
    data = {"subject": ""}
    response = logged_in_client.post("/ng/support/tickets", json=data)
    assert response.status_code == 400
    assert not response.get_json()["success"]
    
    # Subject too long
    data = {"subject": "A" * 129}
    response = logged_in_client.post("/ng/support/tickets", json=data)
    assert response.status_code == 400


def test_list_user_tickets(logged_in_client, normal_user):
    """Test that users see only their own tickets."""
    # Create some tickets
    ticket1 = Ticket.create(subject="My Ticket 1", author_id=normal_user.id)
    ticket2 = Ticket.create(subject="My Ticket 2", author_id=normal_user.id)
    
    # Create another user's ticket
    other_user = gen_user(_db, name="other", email="other@example.com")
    Ticket.create(subject="Other's Ticket", author_id=other_user.id)
    
    response = logged_in_client.get("/ng/support/tickets")
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["success"]
    tickets = data["data"]["tickets"]
    
    # Should only see own tickets
    assert len(tickets) == 2
    assert all(t["author_id"] == normal_user.id for t in tickets)


def test_list_tickets_with_status_filter(logged_in_client, normal_user):
    """Test ticket listing with status filters."""
    # Create tickets with different statuses
    open_ticket = Ticket.create(subject="Open", author_id=normal_user.id)
    closed_ticket = Ticket.create(subject="Closed", author_id=normal_user.id)
    closed_ticket.close_ticket()
    
    # Filter open tickets
    response = logged_in_client.get("/ng/support/tickets?status=open")
    data = response.get_json()
    assert len(data["data"]["tickets"]) == 1
    assert data["data"]["tickets"][0]["id"] == open_ticket.id
    
    # Filter closed tickets
    response = logged_in_client.get("/ng/support/tickets?status=closed")
    data = response.get_json()
    assert len(data["data"]["tickets"]) == 1
    assert data["data"]["tickets"][0]["id"] == closed_ticket.id


def test_get_ticket_details(logged_in_client, normal_user):
    """Test getting ticket details."""
    ticket = Ticket.create(subject="Detail Test", author_id=normal_user.id)
    TicketMessage.create("First message", ticket.id, normal_user.id)
    TicketMessage.create("Second message", ticket.id, normal_user.id)
    
    response = logged_in_client.get(f"/ng/support/tickets/{ticket.id}")
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["success"]
    ticket_data = data["data"]["ticket"]
    assert ticket_data["subject"] == "Detail Test"
    assert len(ticket_data["messages"]) == 2


def test_get_ticket_permission_denied(logged_in_client):
    """Test that users cannot view other's tickets."""
    other_user = gen_user(_db, name="other2", email="other2@example.com")
    ticket = Ticket.create(subject="Private", author_id=other_user.id)
    
    response = logged_in_client.get(f"/ng/support/tickets/{ticket.id}")
    assert response.status_code == 403


def test_update_ticket_subject(logged_in_client, normal_user):
    """Test updating ticket subject."""
    ticket = Ticket.create(subject="Original", author_id=normal_user.id)
    
    data = {"subject": "Updated Subject"}
    response = logged_in_client.patch(f"/ng/support/tickets/{ticket.id}", json=data)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"]
    assert data["data"]["ticket"]["subject"] == "Updated Subject"


def test_create_ticket_message(logged_in_client, normal_user):
    """Test replying to a ticket."""
    ticket = Ticket.create(subject="Message Test", author_id=normal_user.id)
    
    data = {"text": "This is my reply"}
    response = logged_in_client.post(f"/ng/support/tickets/{ticket.id}/messages", json=data)
    
    assert response.status_code == 201
    data = response.get_json()
    assert data["success"]
    assert data["data"]["message"]["text"] == "This is my reply"


def test_cannot_reply_to_closed_ticket(logged_in_client, normal_user):
    """Test that users cannot reply to closed tickets."""
    ticket = Ticket.create(subject="Closed", author_id=normal_user.id)
    ticket.close_ticket()
    
    data = {"text": "Cannot send this"}
    response = logged_in_client.post(f"/ng/support/tickets/{ticket.id}/messages", json=data)
    
    assert response.status_code == 400


# Admin endpoint tests
def test_admin_list_all_tickets(admin_client):
    """Test that admins can see all tickets."""
    user1 = gen_user(_db, name="user1", email="user1@example.com")
    user2 = gen_user(_db, name="user2", email="user2@example.com")
    
    Ticket.create(subject="User 1 Ticket", author_id=user1.id)
    Ticket.create(subject="User 2 Ticket", author_id=user2.id)
    
    response = admin_client.get("/ng/support/admin/tickets")
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["success"]
    assert len(data["data"]["tickets"]) >= 2


def test_admin_filter_tickets(admin_client, event, team):
    """Test admin ticket filtering."""
    user = gen_user(_db, name="test", email="test@example.com")
    
    # Create tickets with different properties
    ticket1 = Ticket.create(subject="Event Ticket", author_id=user.id, event_id=event.id)
    ticket2 = Ticket.create(subject="Team Ticket", author_id=user.id, team_id=team.id)
    ticket3 = Ticket.create(subject="Regular Ticket", author_id=user.id)
    
    # Filter by event
    response = admin_client.get(f"/ng/support/admin/tickets?event_id={event.id}")
    data = response.get_json()
    tickets = data["data"]["tickets"]
    assert any(t["id"] == ticket1.id for t in tickets)
    assert not any(t["id"] == ticket3.id for t in tickets)
    
    # Filter by team
    response = admin_client.get(f"/ng/support/admin/tickets?team_id={team.id}")
    data = response.get_json()
    tickets = data["data"]["tickets"]
    assert any(t["id"] == ticket2.id for t in tickets)


def test_admin_get_any_ticket(admin_client):
    """Test that admins can view any ticket."""
    user = gen_user(_db, name="anyuser", email="anyuser@example.com")
    ticket = Ticket.create(subject="Any User's Ticket", author_id=user.id)
    
    response = admin_client.get(f"/ng/support/admin/tickets/{ticket.id}")
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["success"]
    # Admin should see additional fields
    assert "assigned_to" in data["data"]["ticket"]
    assert "muted" in data["data"]["ticket"]


def test_admin_assign_ticket(admin_client):
    """Test admin ticket assignment."""
    user = gen_user(_db, name="author", email="author@example.com")
    assignee = gen_user(_db, name="assignee", email="assignee@example.com")
    
    ticket = Ticket.create(subject="Unassigned", author_id=user.id)
    
    data = {"user_id": assignee.id}
    response = admin_client.post(f"/ng/support/admin/tickets/{ticket.id}/assign", json=data)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"]
    assert data["data"]["ticket"]["assigned_to"] == assignee.id


def test_admin_close_ticket(admin_client):
    """Test admin closing a ticket."""
    user = gen_user(_db, name="closer", email="closer@example.com")
    ticket = Ticket.create(subject="To Close", author_id=user.id)
    
    response = admin_client.post(f"/ng/support/admin/tickets/{ticket.id}/close")
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"]
    
    # Verify ticket is closed
    updated_ticket = Ticket.find_by_id(ticket.id)
    assert updated_ticket.status == "closed"


def test_admin_reopen_ticket(admin_client):
    """Test admin reopening a ticket."""
    user = gen_user(_db, name="reopener", email="reopener@example.com")
    ticket = Ticket.create(subject="To Reopen", author_id=user.id)
    ticket.close_ticket()
    
    response = admin_client.post(f"/ng/support/admin/tickets/{ticket.id}/reopen")
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"]
    
    # Verify ticket is open
    updated_ticket = Ticket.find_by_id(ticket.id)
    assert updated_ticket.status == "open"


def test_admin_mute_unmute_ticket(admin_client):
    """Test admin muting and unmuting a ticket."""
    user = gen_user(_db, name="muter", email="muter@example.com")
    ticket = Ticket.create(subject="To Mute", author_id=user.id)
    
    # Mute
    response = admin_client.post(f"/ng/support/admin/tickets/{ticket.id}/mute")
    assert response.status_code == 200
    
    updated_ticket = Ticket.find_by_id(ticket.id)
    assert updated_ticket.status == "muted"
    
    # Unmute
    response = admin_client.delete(f"/ng/support/admin/tickets/{ticket.id}/mute")
    assert response.status_code == 200
    
    updated_ticket = Ticket.find_by_id(ticket.id)
    assert updated_ticket.status == "open"


def test_admin_ticket_statistics(admin_client):
    """Test getting ticket statistics."""
    response = admin_client.get("/ng/support/admin/tickets/statistics")
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"]
    
    stats = data["data"]["statistics"]
    assert "total" in stats
    assert "open" in stats
    assert "closed" in stats
    assert "muted" in stats
    assert "unassigned" in stats


# Tag management tests
def test_admin_create_tag(admin_client):
    """Test admin creating a tag."""
    data = {
        "name": "bug",
        "color": "#FF0000",
        "description": "Bug reports"
    }
    response = admin_client.post("/ng/support/admin/tags", json=data)
    
    assert response.status_code == 201
    data = response.get_json()
    assert data["success"]
    assert data["data"]["tag"]["name"] == "bug"


def test_admin_list_tags(admin_client):
    """Test listing all tags."""
    TicketTag.create("tag1", "#FF0000")
    TicketTag.create("tag2", "#00FF00")
    
    response = admin_client.get("/ng/support/admin/tags")
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"]
    assert len(data["data"]["tags"]) >= 2


def test_admin_update_tag(admin_client):
    """Test updating a tag."""
    tag = TicketTag.create("old-name", "#FF0000")
    
    data = {"name": "new-name", "color": "#00FF00"}
    response = admin_client.patch(f"/ng/support/admin/tags/{tag.id}", json=data)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"]
    assert data["data"]["tag"]["name"] == "new-name"


def test_admin_delete_tag(admin_client):
    """Test deleting a tag."""
    tag = TicketTag.create("to-delete")
    
    response = admin_client.delete(f"/ng/support/admin/tags/{tag.id}")
    
    assert response.status_code == 200
    
    # Verify deletion
    deleted_tag = TicketTag.find_by_id(tag.id)
    assert deleted_tag is None


def test_admin_manage_ticket_tags(admin_client):
    """Test adding and removing tags from tickets."""
    user = gen_user(_db, name="tagger", email="tagger@example.com")
    ticket = Ticket.create(subject="Tag Test", author_id=user.id)
    
    tag1 = TicketTag.create("urgent")
    tag2 = TicketTag.create("feature")
    
    # Add tags
    data = {"tag_ids": [tag1.id, tag2.id]}
    response = admin_client.post(f"/ng/support/admin/tickets/{ticket.id}/tags", json=data)
    
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["data"]["ticket"]["tags"]) == 2
    
    # Remove one tag
    data = {"tag_ids": [tag1.id]}
    response = admin_client.delete(f"/ng/support/admin/tickets/{ticket.id}/tags", json=data)
    
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["data"]["ticket"]["tags"]) == 1
    assert data["data"]["ticket"]["tags"][0] == "feature"


def test_regular_user_cannot_access_admin_endpoints(logged_in_client):
    """Test that regular users cannot access admin endpoints."""
    # All admin endpoints should redirect (302) for non-admin users
    endpoints = [
        "/ng/support/admin/tickets",
        "/ng/support/admin/tickets/statistics",
        "/ng/support/admin/tags"
    ]
    
    for endpoint in endpoints:
        response = logged_in_client.get(endpoint)
        assert response.status_code == 302
        assert response.location is not None


# Additional comprehensive tests

def test_ticket_with_tags_creation(logged_in_client):
    """Test creating a ticket with tags."""
    tag1 = TicketTag.create("help-needed")
    tag2 = TicketTag.create("question")
    
    data = {
        "subject": "Need help with challenge",
        "tag_ids": [tag1.id, tag2.id]
    }
    response = logged_in_client.post("/ng/support/tickets", json=data)
    
    assert response.status_code == 201
    data = response.get_json()
    assert len(data["data"]["ticket"]["tags"]) == 2
    assert "help-needed" in data["data"]["ticket"]["tags"]
    assert "question" in data["data"]["ticket"]["tags"]


def test_invalid_tag_creation_fails(logged_in_client):
    """Test that creating ticket with invalid tags fails."""
    data = {
        "subject": "Invalid tags test",
        "tag_ids": [9999, 10000]  # Non-existent tags
    }
    response = logged_in_client.post("/ng/support/tickets", json=data)
    
    assert response.status_code == 400
    assert not response.get_json()["success"]


def test_message_validation(logged_in_client, normal_user):
    """Test message creation validation."""
    ticket = Ticket.create(subject="Message validation", author_id=normal_user.id)
    
    # Empty message
    data = {"text": ""}
    response = logged_in_client.post(f"/ng/support/tickets/{ticket.id}/messages", json=data)
    assert response.status_code == 400
    
    # Message too long
    data = {"text": "A" * 4097}
    response = logged_in_client.post(f"/ng/support/tickets/{ticket.id}/messages", json=data)
    assert response.status_code == 400


def test_admin_reply_reopens_closed_ticket(admin_client):
    """Test that admin reply automatically reopens a closed ticket."""
    user = gen_user(_db, name="ticketuser", email="ticketuser@example.com")
    ticket = Ticket.create(subject="Will be reopened", author_id=user.id)
    ticket.close_ticket()
    
    data = {"text": "Admin reply should reopen this"}
    response = admin_client.post(f"/ng/support/admin/tickets/{ticket.id}/messages", json=data)
    
    assert response.status_code == 201
    data = response.get_json()
    assert data["data"]["ticket_reopened"]
    
    # Verify ticket is open
    updated_ticket = Ticket.find_by_id(ticket.id)
    assert updated_ticket.status == "open"


def test_first_admin_response_timestamp(admin_client, normal_user):
    """Test that first admin response timestamp is recorded."""
    ticket = Ticket.create(subject="Response timing test", author_id=normal_user.id)
    
    # Verify no admin response initially
    assert ticket.first_admin_response_timestamp is None
    
    # Admin replies
    data = {"text": "First admin response"}
    response = admin_client.post(f"/ng/support/admin/tickets/{ticket.id}/messages", json=data)
    assert response.status_code == 201
    
    # Check timestamp was set
    updated_ticket = Ticket.find_by_id(ticket.id)
    assert updated_ticket.first_admin_response_timestamp is not None
    
    # Second admin reply shouldn't change it
    original_timestamp = updated_ticket.first_admin_response_timestamp
    data = {"text": "Second admin response"}
    response = admin_client.post(f"/ng/support/admin/tickets/{ticket.id}/messages", json=data)
    assert response.status_code == 201
    
    updated_ticket = Ticket.find_by_id(ticket.id)
    assert updated_ticket.first_admin_response_timestamp == original_timestamp


def test_invalid_event_association(logged_in_client):
    """Test that creating ticket with invalid event fails."""
    data = {
        "subject": "Invalid event test",
        "event_id": 9999  # Non-existent event
    }
    response = logged_in_client.post("/ng/support/tickets", json=data)
    
    assert response.status_code == 400
    assert not response.get_json()["success"]


def test_invalid_team_association(logged_in_client):
    """Test that creating ticket with invalid team fails."""
    data = {
        "subject": "Invalid team test",
        "team_id": 9999  # Non-existent team
    }
    response = logged_in_client.post("/ng/support/tickets", json=data)
    
    assert response.status_code == 400
    assert not response.get_json()["success"]


def test_ticket_last_updated_changes(logged_in_client, normal_user):
    """Test that last_updated timestamp changes on updates."""
    ticket = Ticket.create(subject="Update timestamp test", author_id=normal_user.id)
    original_updated = ticket.last_updated
    
    # Wait a moment to ensure timestamp difference
    import time
    time.sleep(0.1)
    
    # Update subject
    data = {"subject": "Updated subject"}
    response = logged_in_client.patch(f"/ng/support/tickets/{ticket.id}", json=data)
    assert response.status_code == 200
    
    updated_ticket = Ticket.find_by_id(ticket.id)
    assert updated_ticket.last_updated > original_updated


def test_admin_can_update_associations(admin_client):
    """Test that admin can update ticket associations."""
    user = gen_user(_db, name="assocuser", email="assocuser@example.com")
    ticket = Ticket.create(subject="Association test", author_id=user.id)
    
    # Update associations
    data = {
        "subject": ticket.subject,
        "event_id": 0,  # Unassign from event
        "team_id": 0,   # Unassign from team
        "challenge_id": 999
    }
    response = admin_client.patch(f"/ng/support/admin/tickets/{ticket.id}", json=data)
    
    assert response.status_code == 200
    updated_ticket = Ticket.find_by_id(ticket.id)
    assert updated_ticket.event_id is None
    assert updated_ticket.team_id is None
    assert updated_ticket.challenge_id == 999


def test_unassigned_tickets_query(admin_client):
    """Test finding unassigned open tickets."""
    user = gen_user(_db, name="queryuser", email="queryuser@example.com")
    
    # Create various tickets
    unassigned_open = Ticket.create(subject="Unassigned Open", author_id=user.id)
    assigned_open = Ticket.create(subject="Assigned Open", author_id=user.id)
    assigned_open.assign_to_user(user.id)
    
    unassigned_closed = Ticket.create(subject="Unassigned Closed", author_id=user.id)
    unassigned_closed.close_ticket()
    
    # Query unassigned tickets through API
    response = admin_client.get("/ng/support/admin/tickets?status=open&assigned_to=")
    data = response.get_json()
    
    # Manual check since API doesn't have specific unassigned filter
    tickets = Ticket.find_unassigned_open_tickets()
    assert any(t.id == unassigned_open.id for t in tickets)
    assert not any(t.id == assigned_open.id for t in tickets)
    assert not any(t.id == unassigned_closed.id for t in tickets)
