"""
Tests for support API endpoints
"""

import json
import pytest
from datetime import datetime


class TestUserSupportEndpoints:
    """Tests for user support API endpoints"""

    def test_create_ticket_with_event_id(self, logged_in_client, user, event, team_factory):
        """Test creating a support ticket with optional event id association"""
        # Create a team for the user in this event
        team_factory(event=event, members=[user])

        response = logged_in_client.post(
            "/ng/support/tickets/create",
            json={
                "subject": "Need help with challenge",
                "text": "I can't submit my flag",
                "event_id": event.id,
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["subject"] == "Need help with challenge"
        assert data["data"]["author_id"] == user.id
        assert data["data"]["event_id"] == event.id
        assert data["data"]["status"] == "open"

    def test_create_ticket_minimal(self, logged_in_client):
        """Test creating ticket with minimal data - no event/team/challenge"""
        response = logged_in_client.post(
            "/ng/support/tickets/create",
            json={
                "subject": "Simple question",
                "text": "How do I get started?",
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        ticket = data["data"]
        assert ticket["subject"] == "Simple question"
        assert ticket["event_id"] is None
        assert ticket["team_id"] is None
        assert ticket["challenge_id"] is None
        # Should not have any name fields since no IDs provided
        assert "event_name" not in ticket
        assert "team_name" not in ticket
        assert "challenge_name" not in ticket

    def test_create_ticket_missing_fields(self, logged_in_client):
        """Test creating ticket without required fields"""
        response = logged_in_client.post(
            "/ng/support/tickets/create",
            json={"subject": "Missing text"},
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_create_ticket_empty_subject(self, logged_in_client):
        """Test creating ticket with empty subject"""
        response = logged_in_client.post(
            "/ng/support/tickets/create",
            json={
                "subject": "   ",
                "text": "Some text",
            },
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_get_my_tickets_all(self, logged_in_client, multiple_tickets, user):
        """Test getting all user's tickets"""
        response = logged_in_client.get("/ng/support/me/tickets")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        # Should only see tickets created by the user
        assert all(t["author_id"] == user.id for t in data["data"])

    def test_get_my_tickets_filtered(self, logged_in_client, multiple_tickets, user):
        """Test getting filtered tickets"""
        # Get only open tickets
        response = logged_in_client.get("/ng/support/me/tickets?status=open")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert all(t["status"] == "open" for t in data["data"])

    def test_get_my_ticket_details(self, logged_in_client, ticket_with_messages):
        """Test getting specific ticket details"""
        response = logged_in_client.get(f"/ng/support/me/tickets/{ticket_with_messages.id}")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "ticket" in data["data"]
        assert "messages" in data["data"]
        assert len(data["data"]["messages"]) == 2

    def test_get_my_ticket_not_found(self, logged_in_client):
        """Test getting non-existent ticket"""
        response = logged_in_client.get("/ng/support/me/tickets/999999")

        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False

    def test_add_message_to_ticket(self, logged_in_client, ticket):
        """Test adding message to ticket"""
        response = logged_in_client.post(
            f"/ng/support/me/tickets/{ticket.id}",
            json={"text": "Here's additional information"},
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["text"] == "Here's additional information"

    def test_add_message_empty_text(self, logged_in_client, ticket):
        """Test adding message with empty text"""
        response = logged_in_client.post(
            f"/ng/support/me/tickets/{ticket.id}",
            json={"text": "   "},
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_close_my_ticket(self, logged_in_client, ticket):
        """Test closing own ticket"""
        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        response = logged_in_client.post(
            f"/ng/support/me/tickets/{ticket.id}/close",
            data={"nonce": nonce},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["status"] == "closed"

    def test_close_already_closed_ticket(self, logged_in_client, closed_ticket):
        """Test closing already closed ticket"""
        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        response = logged_in_client.post(
            f"/ng/support/me/tickets/{closed_ticket.id}/close",
            data={"nonce": nonce},
        )

        # Should still succeed (idempotent)
        assert response.status_code == 200

    def test_unauthenticated_requests(self, client, ticket):
        """Test that unauthenticated requests fail"""
        endpoints = [
            ("/ng/support/tickets/create", "POST", {"subject": "test", "text": "test"}),
            ("/ng/support/me/tickets", "GET", None),
            (f"/ng/support/me/tickets/{ticket.id}", "GET", None),
            (f"/ng/support/me/tickets/{ticket.id}", "POST", {"text": "test"}),
            (f"/ng/support/me/tickets/{ticket.id}/close", "POST", {}),
        ]

        for endpoint, method, json_data in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json=json_data)

            assert response.status_code in [302, 403]


class TestAdminSupportEndpoints:
    """Tests for admin support API endpoints"""

    def test_get_all_tickets(self, admin_client, multiple_tickets):
        """Test getting all tickets as admin"""
        response = admin_client.get("/ng/admin/support/tickets")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) >= 4

    def test_get_tickets_filtered(self, admin_client, multiple_tickets, admin):
        """Test getting filtered tickets"""
        # Filter by status
        response = admin_client.get("/ng/admin/support/tickets?status=open")
        data = response.get_json()
        assert all(t["status"] == "open" for t in data["data"])

        # Filter by assigned user
        response = admin_client.get(f"/ng/admin/support/tickets?assigned_to={admin.id}")
        data = response.get_json()
        assert all(t["assigned_to"] == admin.id for t in data["data"])

    def test_get_any_ticket_details(self, admin_client, ticket_with_messages):
        """Test admin can get any ticket details"""
        response = admin_client.get(f"/ng/admin/support/tickets/{ticket_with_messages.id}")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "ticket" in data["data"]
        assert "messages" in data["data"]

    def test_admin_add_message_reopens_ticket(self, admin_client, closed_ticket, admin):
        """Test admin message reopens closed ticket"""
        response = admin_client.post(
            f"/ng/admin/support/tickets/{closed_ticket.id}",
            json={"text": "I'm reopening this to help"},
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True

        # Check ticket was reopened
        ticket_response = admin_client.get(f"/ng/admin/support/tickets/{closed_ticket.id}")
        ticket_data = ticket_response.get_json()
        assert ticket_data["data"]["ticket"]["status"] == "open"

    def test_create_tag(self, admin_client):
        """Test creating a new tag"""
        response = admin_client.post(
            "/ng/admin/support/tags",
            json={
                "name": "security-issue",
                "color": "#FF0000",
                "description": "Security related issues",
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["name"] == "security-issue"

    def test_create_tag_duplicate_name(self, admin_client, ticket_tag):
        """Test creating tag with duplicate name"""
        response = admin_client.post(
            "/ng/admin/support/tags",
            json={
                "name": ticket_tag.name,
                "color": "#00FF00",
            },
        )

        assert response.status_code == 409
        data = response.get_json()
        assert data["success"] is False

    def test_update_tag(self, admin_client):
        """Test updating a tag"""
        # First create a tag
        create_response = admin_client.post(
            "/ng/admin/support/tags",
            json={"name": "original-tag", "color": "#FF0000"},
        )
        assert create_response.status_code == 201
        tag_id = create_response.get_json()["data"]["id"]

        # Now update it
        response = admin_client.put(
            f"/ng/admin/support/tags/{tag_id}",
            json={
                "name": "updated-bug",
                "color": "#00FF00",
            },
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["name"] == "updated-bug"

    def test_get_all_tags(self, admin_client, ticket_tag_factory):
        """Test getting all tags"""
        # Create some tags
        ticket_tag_factory(name="alpha")
        ticket_tag_factory(name="beta")

        response = admin_client.get("/ng/admin/support/tags")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) >= 2
        # Should be alphabetically ordered
        names = [tag["name"] for tag in data["data"]]
        assert names == sorted(names)

    def test_set_ticket_tags(self, admin_client, ticket, ticket_tag_factory):
        """Test setting tags on a ticket"""
        tag1 = ticket_tag_factory(name="priority-high")
        tag2 = ticket_tag_factory(name="needs-review")

        response = admin_client.put(
            f"/ng/admin/support/tickets/{ticket.id}/tag",
            json={"tag_ids": [tag1.id, tag2.id]},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]["tags"]) == 2

    def test_assign_ticket(self, admin_client, ticket, admin):
        """Test assigning ticket to user"""
        response = admin_client.put(
            f"/ng/admin/support/tickets/{ticket.id}/assign",
            json={"user_id": admin.id},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["assigned_to"] == admin.id

    def test_unassign_ticket(self, admin_client, assigned_ticket):
        """Test unassigning ticket"""
        response = admin_client.put(
            f"/ng/admin/support/tickets/{assigned_ticket.id}/unassign",
            json={}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["assigned_to"] is None

    def test_toggle_ticket_status(self, admin_client, ticket):
        """Test closing/reopening ticket"""
        # Close ticket
        response = admin_client.put(
            f"/ng/admin/support/tickets/{ticket.id}/close",
            json={"closed": True},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["status"] == "closed"

        # Reopen ticket
        response = admin_client.put(
            f"/ng/admin/support/tickets/{ticket.id}/close",
            json={"closed": False},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["status"] == "open"

    def test_toggle_ticket_mute(self, admin_client, ticket):
        """Test muting/unmuting ticket"""
        # Mute ticket
        response = admin_client.put(
            f"/ng/admin/support/tickets/{ticket.id}/mute",
            json={"muted": True},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["muted"] is True

        # Unmute ticket
        response = admin_client.put(
            f"/ng/admin/support/tickets/{ticket.id}/mute",
            json={"muted": False},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["muted"] is False

    def test_update_ticket_event(self, admin_client, ticket, event_factory, team_factory, user):
        """Test updating ticket's event and team"""
        new_event = event_factory()
        new_team = team_factory(event=new_event, members=[user])

        response = admin_client.put(
            f"/ng/admin/support/tickets/{ticket.id}/event",
            json={
                "event_id": new_event.id,
                "team_id": new_team.id,
            },
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["event_id"] == new_event.id
        assert data["data"]["team_id"] == new_team.id

    def test_update_ticket_challenge(self, admin_client, ticket, challenge):
        """Test updating ticket's challenge"""
        response = admin_client.put(
            f"/ng/admin/support/tickets/{ticket.id}/challenge",
            json={"challenge_id": challenge.id},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["challenge_id"] == challenge.id

    def test_non_admin_access_fails(self, logged_in_client, ticket):
        """Test that non-admin cannot access admin endpoints"""
        endpoints = [
            ("/ng/admin/support/tickets", "GET"),
            (f"/ng/admin/support/tickets/{ticket.id}", "GET"),
            ("/ng/admin/support/tags", "GET"),
            ("/ng/admin/support/tags", "POST"),
        ]

        for endpoint, method in endpoints:
            if method == "GET":
                response = logged_in_client.get(endpoint)
            else:
                response = logged_in_client.post(endpoint, json={})

            assert response.status_code in [302, 403]

    def test_create_ticket_without_team_id(self, logged_in_client, user, event_factory, team_factory):
        """
        Test creating ticket without team_id - it should be auto-derived
        """
        event = event_factory(name="Test Event for Auto Team", public=True)
        team_factory(event=event, members=[user])

        response = logged_in_client.post(
            "/ng/support/tickets/create",
            json={
                "subject": "Auto-derived team ticket",
                "text": "This should work without team_id",
                "event_id": event.id,
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["subject"] == "Auto-derived team ticket"
        assert data["data"]["author_id"] == user.id
        assert data["data"]["event_id"] == event.id
        # Team ID should be automatically set
        assert data["data"]["team_id"] is not None

    def test_create_ticket_without_team_membership_fails(self, logged_in_client, user, event_factory):
        """
        Test creating ticket fails when user is not in event team
        """
        event = event_factory(name="Test Event No Team", public=True)
        # User is not in any team for this event

        response = logged_in_client.post(
            "/ng/support/tickets/create",
            json={
                "subject": "Should fail",
                "text": "User not in team",
                "event_id": event.id,
            },
        )

        assert response.status_code == 404  # Team not found for user+event

    def test_ticket_list_includes_names(self, logged_in_client, user, event, challenge, team_factory):
        """
        Test that ticket list includes event_name, team_name, and challenge_name
        """
        team = team_factory(event=event, members=[user])

        # Create ticket with challenge
        response = logged_in_client.post(
            "/ng/support/tickets/create",
            json={
                "subject": "Challenge question",
                "text": "Need help with this challenge",
                "event_id": event.id,
                "challenge_id": challenge.id,
            },
        )
        assert response.status_code == 201

        # Get ticket list
        response = logged_in_client.get("/ng/support/me/tickets")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

        # Find our ticket
        ticket = next(t for t in data["data"] if t["subject"] == "Challenge question")
        assert ticket["challenge_id"] == challenge.id
        assert ticket["challenge_name"] == challenge.name
        assert ticket["event_id"] == event.id
        assert ticket["event_name"] == event.name
        assert ticket["team_id"] == team.id
        assert ticket["team_name"] == team.name

    def test_ticket_list_without_challenge(self, logged_in_client, user, event, team_factory):
        """
        Test that ticket list includes event_name and team_name but not challenge_name when no challenge_id
        """
        team = team_factory(event=event, members=[user])

        # Create ticket without challenge
        response = logged_in_client.post(
            "/ng/support/tickets/create",
            json={
                "subject": "General question",
                "text": "Not related to any challenge",
                "event_id": event.id,
            },
        )
        assert response.status_code == 201

        # Get ticket list
        response = logged_in_client.get("/ng/support/me/tickets")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

        # Find our ticket
        ticket = next(t for t in data["data"] if t["subject"] == "General question")
        assert ticket["challenge_id"] is None
        assert ticket["event_id"] == event.id
        assert ticket["event_name"] == event.name
        assert ticket["team_id"] == team.id
        assert ticket["team_name"] == team.name
        # Should not have challenge_name since no challenge_id
        assert "challenge_name" not in ticket


