"""
Tests for support API endpoints
"""

import json
import pytest
from datetime import datetime

from CTFd.models import Users

from ...permissions.models.Role import Role
from ...user.models.User import User as NgUser
from ...notifications.models import Notification
from ...permissions.models.enums import RoleEnum
from ...permissions.controllers import assign_role_to_user
from ..models.TicketAttachment import TicketAttachment

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

        # Verify ticket data is serialized properly
        ticket_data = data["data"]["ticket"]
        assert isinstance(ticket_data, dict)
        assert ticket_data["id"] == ticket_with_messages.id

    def test_get_ticket_details_includes_names(self, logged_in_client, user, event, challenge, team_factory):
        """Test getting ticket details includes event_name and challenge_name"""
        team = team_factory(event=event, members=[user])

        # Create ticket with event and challenge
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
        ticket_id = response.get_json()["data"]["id"]

        # Get ticket details
        response = logged_in_client.get(f"/ng/support/me/tickets/{ticket_id}")
        assert response.status_code == 200

        data = response.get_json()
        ticket_data = data["data"]["ticket"]

        # Verify names are included
        assert ticket_data["event_name"] == event.name
        assert ticket_data["team_name"] == team.name
        assert ticket_data["challenge_name"] == challenge.name

    def test_get_my_ticket_not_found(self, logged_in_client):
        """Test getting non-existent ticket"""
        response = logged_in_client.get("/ng/support/me/tickets/999999")

        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False

    def test_add_message_to_ticket(self, logged_in_client, ticket):
        """Test adding message to ticket"""
        response = logged_in_client.post(
            f"/ng/support/me/tickets/{ticket.id}/add_message",
            json={"text": "Here's additional information"},
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["text"] == "Here's additional information"

    def test_add_message_empty_text(self, logged_in_client, ticket):
        """Test adding message with empty text"""
        response = logged_in_client.post(
            f"/ng/support/me/tickets/{ticket.id}/add_message",
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
            (f"/ng/support/me/tickets/{ticket.id}/add_message", "POST", {"text": "test"}),
            (f"/ng/support/me/tickets/{ticket.id}/close", "POST", {}),
        ]

        for endpoint, method, json_data in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json=json_data)

            assert response.status_code in [401,403]


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

    def test_admin_tickets_include_author_and_assigned_names(self, admin_client, user, admin, event, challenge, team_factory, ticket_factory):
        """Test that admin ticket list includes author_name and assigned_to_name"""
        team = team_factory(event=event, members=[user])

        # Create a ticket with assignment
        ticket = ticket_factory(
            subject="Test ticket with assignment",
            author_id=user.id,
            event_id=event.id,
            team_id=team.id,
            challenge_id=challenge.id
        )
        # Assign the ticket
        ticket.assign_to_user(admin.id)

        # Get all tickets via admin endpoint
        response = admin_client.get("/ng/admin/support/tickets")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

        # Find our test ticket
        test_ticket = next(t for t in data["data"] if t["subject"] == "Test ticket with assignment")

        # Verify all name enrichments are present
        assert test_ticket["author_name"] == user.name
        assert test_ticket["assigned_to_name"] == admin.name
        assert test_ticket["event_name"] == event.name
        assert test_ticket["team_name"] == team.name
        assert test_ticket["challenge_name"] == challenge.name

        # Verify IDs are also present
        assert test_ticket["author_id"] == user.id
        assert test_ticket["assigned_to"] == admin.id
        assert test_ticket["event_id"] == event.id
        assert test_ticket["team_id"] == team.id
        assert test_ticket["challenge_id"] == challenge.id

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
            f"/ng/admin/support/tickets/{closed_ticket.id}/add_message",
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

        # Verify tags are full objects with id, name, and color
        for tag in data["data"]["tags"]:
            assert "id" in tag
            assert "name" in tag
            assert "color" in tag
            assert isinstance(tag["id"], int)
            assert isinstance(tag["name"], str)

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

    def test_assign_ticket_to_non_support_user_fails(self, admin_client, ticket, user, db_session):
        """
        Test that assigning a ticket to a non-support user fails with validation error
        """
        # Try to assign ticket to regular user (not admin/support)
        response = admin_client.put(
            f"/ng/admin/support/tickets/{ticket.id}/assign",
            json={"user_id": user.id},
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        # Check error message in response
        response_str = str(data)
        assert "ADMIN" in response_str or "SUPPORT" in response_str or "role" in response_str.lower()

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

    def test_user_creates_ticket_support_staff_do_not_get_notification(
        self,
        logged_in_client,
        user,
        admin,
        db_session,
    ):
        """
        Test that when a user creates a ticket, support staff do not receive DB notifications
        (only WebSocket refetch events are sent)
        """
        Role.create_role(RoleEnum.SUPPORT)

        support_user_ctfd = Users(name="supportuser", email="support@example.com", password="password")
        support_user_ctfd.verified = True
        db_session.add(support_user_ctfd)
        db_session.flush()

        NgUser.create_user(user_id=support_user_ctfd.id, commit=False)
        assign_role_to_user(support_user_ctfd.id, RoleEnum.SUPPORT)
        db_session.flush()

        # Create ticket
        response = logged_in_client.post(
            "/ng/support/tickets/create",
            json={
                "subject": "Need help with login",
                "text": "I can't log in",
            },
        )

        assert response.status_code == 201
        ticket_id = response.get_json()["data"]["id"]

        admin_notifications = Notification.query.filter_by(
            recipient_id=admin.id,
            ticket_id=ticket_id
        ).all()

        assert len(admin_notifications) == 0

        support_notifications = Notification.query.filter_by(
            recipient_id=support_user_ctfd.id,
            ticket_id=ticket_id
        ).all()

        assert len(support_notifications) == 0

    def test_admin_replies_without_assignment_user_gets_notification(
        self,
        admin_client,
        user,
        admin,
        ticket,
        db_session,
    ):
        """
        Test that when an admin replies to a ticket WITHOUT being assigned,
        the user still receives a notification
        """
        # Admin replies without being assigned
        response = admin_client.post(
            f"/ng/admin/support/tickets/{ticket.id}/add_message",
            json={"text": "I can help you with this"},
        )

        assert response.status_code == 201

        # Check that user got notification
        user_notifications = Notification.query.filter_by(
            recipient_id=user.id,
            ticket_id=ticket.id,
            sender_id=admin.id
        ).all()

        assert len(user_notifications) >= 1
        notification = user_notifications[-1]  # Get most recent
        assert notification.type.value == "ticket_message"
        assert notification.title == "Support Ticket Update"
        assert "replied" in notification.message.lower()

    def test_user_replies_to_assigned_ticket_admin_gets_notification(
        self,
        logged_in_client,
        user,
        admin,
        assigned_ticket,
        db_session,
    ):
        """
        Test that when a user replies to an assigned ticket,
        the assigned admin receives a notification
        """
        # User replies to assigned ticket
        response = logged_in_client.post(
            f"/ng/support/me/tickets/{assigned_ticket.id}/add_message",
            json={"text": "Thanks for the help!"},
        )

        assert response.status_code == 201

        # Check that assigned admin got notification
        # NOTE: ONLY SUPPORT admins can be assigned in the first place
        admin_notifications = Notification.query.filter_by(
            recipient_id=admin.id,
            ticket_id=assigned_ticket.id,
            sender_id=user.id
        ).all()

        assert len(admin_notifications) >= 1
        notification = admin_notifications[-1]
        assert notification.type.value == "ticket_message"
        assert notification.sender_id == user.id

    def test_assigned_ticket_only_notifies_assigned_admin_not_all(
        self,
        logged_in_client,
        user,
        admin,
        ticket,
        db_session,
    ):
        """
        Test that when a ticket IS assigned, user replies only notify
        the ASSIGNED admin, NOT all admins
        """
        # Create second admin
        admin2_ctfd = Users(name="admin2", email="admin2@example.com", password="password", type="admin")
        admin2_ctfd.verified = True
        db_session.add(admin2_ctfd)
        db_session.flush()

        NgUser.create_user(user_id=admin2_ctfd.id, commit=False)
        assign_role_to_user(admin2_ctfd.id, RoleEnum.ADMIN)
        db_session.flush()

        # Assign ticket to admin (not admin2)
        ticket.assign_to_user(admin.id)
        db_session.commit()

        # User replies to assigned ticket
        response = logged_in_client.post(
            f"/ng/support/me/tickets/{ticket.id}/add_message",
            json={"text": "Thanks for helping!"},
        )

        assert response.status_code == 201

        # Check that ASSIGNED admin got notification
        admin_notifications = Notification.query.filter_by(
            recipient_id=admin.id,
            ticket_id=ticket.id,
        ).filter(
            Notification.type == "ticket_message"
        ).all()
        assert len(admin_notifications) >= 1

        # Check that OTHER admin did NOT get notification
        admin2_notifications = Notification.query.filter_by(
            recipient_id=admin2_ctfd.id,
            ticket_id=ticket.id,
        ).filter(
            Notification.type == "ticket_message"
        ).all()
        assert len(admin2_notifications) == 0  # Should be ZERO!

    def test_muted_ticket_does_not_send_notifications(
        self,
        logged_in_client,
        user,
        admin,
        ticket,
        db_session,
    ):
        """
        Test that muted tickets do NOT send notifications when users reply
        """
        # Mute the ticket
        ticket.toggle_mute(True)
        db_session.commit()

        # User replies to muted ticket
        response = logged_in_client.post(
            f"/ng/support/me/tickets/{ticket.id}/add_message",
            json={"text": "Hello? Anyone there?"},
        )

        assert response.status_code == 201

        # Check that NO notifications were created
        admin_notifications = Notification.query.filter_by(
            recipient_id=admin.id,
            ticket_id=ticket.id,
        ).filter(
            Notification.type == "ticket_message"
        ).all()

        assert len(admin_notifications) == 0  # No notifications

    def test_admin_assigns_self_then_replies_user_gets_notification(
        self,
        admin_client,
        user,
        admin,
        ticket,
        db_session,
    ):
        """
        Test the full flow: admin assigns ticket to themselves, then replies
        """
        # Admin assigns ticket to themselves
        assign_response = admin_client.put(
            f"/ng/admin/support/tickets/{ticket.id}/assign",
            json={"user_id": admin.id},
        )
        assert assign_response.status_code == 200

        # Check admin got assignment notification
        assignment_notifications = Notification.query.filter_by(
            recipient_id=admin.id,
            ticket_id=ticket.id,
        ).filter(
            Notification.type == "ticket_assigned"
        ).all()
        assert len(assignment_notifications) == 1

        # Admin replies to ticket
        reply_response = admin_client.post(
            f"/ng/admin/support/tickets/{ticket.id}/add_message",
            json={"text": "I've been assigned and I'm here to help"},
        )
        assert reply_response.status_code == 201

        # Check that user got reply notification
        reply_notifications = Notification.query.filter_by(
            recipient_id=user.id,
            ticket_id=ticket.id,
            sender_id=admin.id
        ).filter(
            Notification.type == "ticket_message"
        ).all()

        assert len(reply_notifications) >= 1
        notification = reply_notifications[-1]
        assert "replied" in notification.message.lower()

    def test_admin_closes_ticket_user_gets_notification(
        self,
        admin_client,
        user,
        admin,
        ticket,
        db_session,
    ):
        """
        Test that when an admin closes a ticket, the user receives a notification
        """
        # Admin closes ticket
        response = admin_client.put(
            f"/ng/admin/support/tickets/{ticket.id}/close",
            json={"closed": True},
        )

        assert response.status_code == 200

        # Check that user got notification
        user_notifications = Notification.query.filter_by(
            recipient_id=user.id,
            ticket_id=ticket.id,
        ).filter(
            Notification.type == "ticket_status_change"
        ).all()

        assert len(user_notifications) >= 1
        notification = user_notifications[-1]
        assert notification.title == "Ticket Status Changed"
        assert "closed" in notification.message.lower()
        assert notification.sender_id == admin.id

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

    def test_admin_ticket_tags_serialization(self, admin_client, ticket, ticket_tag_factory):
        """
        Test that admin ticket details return full tag objects instead of just names
        """
        # Create tags with specific colors
        tag1 = ticket_tag_factory(name="urgent", color="#ff0000", description="High priority issues")
        tag2 = ticket_tag_factory(name="backend", color="#00ff00", description="Backend related")
        tag3 = ticket_tag_factory(name="database", color=None, description="Database issues")  # Test null color

        # Set tags on ticket
        admin_client.put(
            f"/ng/admin/support/tickets/{ticket.id}/tag",
            json={"tag_ids": [tag1.id, tag2.id, tag3.id]},
        )

        # Get ticket details
        response = admin_client.get(f"/ng/admin/support/tickets/{ticket.id}")
        assert response.status_code == 200

        data = response.get_json()
        assert data["success"] is True

        ticket_data = data["data"]["ticket"]
        tags = ticket_data["tags"]

        # Verify we have 3 tags
        assert len(tags) == 3

        # Verify each tag has the correct structure
        for tag in tags:
            assert "id" in tag
            assert "name" in tag
            assert "color" in tag
            assert isinstance(tag["id"], int)
            assert isinstance(tag["name"], str)
            # Color can be string or None
            assert tag["color"] is None or isinstance(tag["color"], str)

        # Verify specific tag data
        tag_names = {tag["name"]: tag for tag in tags}

        assert tag_names["urgent"]["id"] == tag1.id
        assert tag_names["urgent"]["color"] == "#ff0000"

        assert tag_names["backend"]["id"] == tag2.id
        assert tag_names["backend"]["color"] == "#00ff00"

        assert tag_names["database"]["id"] == tag3.id
        assert tag_names["database"]["color"] is None

    def test_user_ticket_details_do_not_include_tags(self, logged_in_client, ticket_with_tags):
        """
        Test that regular users don't get tag data (admin-only field)
        """
        response = logged_in_client.get(f"/ng/support/me/tickets/{ticket_with_tags.id}")
        assert response.status_code == 200

        data = response.get_json()
        ticket_data = data["data"]["ticket"]

        # Regular users should not see tags (admin-only field)
        assert "tags" not in ticket_data

    def test_get_ticket_includes_empty_attachments_list(self, logged_in_client, ticket):
        """
        Test that get_ticket includes empty attachments array when no attachments exist
        """
        response = logged_in_client.get(f"/ng/support/me/tickets/{ticket.id}")
        assert response.status_code == 200

        data = response.get_json()
        assert "attachments" in data["data"]
        assert isinstance(data["data"]["attachments"], list)
        assert len(data["data"]["attachments"]) == 0

    def test_get_ticket_includes_attachments(self, logged_in_client, ticket, user, db_session):
        """
        Test that get_ticket includes attachments when they exist
        """
        TicketAttachment.create_attachment(
            ticket_id=ticket.id,
            s3_key=f"support-tickets/{ticket.id}/first.webp",
            bucket_name="test-bucket",
            filename="first.webp",
            file_size=1024,
            content_type="image/webp",
            uploaded_by=user.id,
        )

        TicketAttachment.create_attachment(
            ticket_id=ticket.id,
            s3_key=f"support-tickets/{ticket.id}/second.webp",
            bucket_name="test-bucket",
            filename="second.webp",
            file_size=2048,
            content_type="image/webp",
            uploaded_by=user.id,
        )

        response = logged_in_client.get(f"/ng/support/me/tickets/{ticket.id}")
        assert response.status_code == 200

        data = response.get_json()
        assert "attachments" in data["data"]
        assert len(data["data"]["attachments"]) == 2

        for attachment_data in data["data"]["attachments"]:
            assert "id" in attachment_data
            assert "ticket_id" in attachment_data
            assert "s3_key" in attachment_data
            assert "bucket_name" in attachment_data
            assert "filename" in attachment_data
            assert "file_size" in attachment_data
            assert "content_type" in attachment_data
            assert "uploaded_by" in attachment_data
            assert "uploaded_at" in attachment_data
            assert "image_url" in attachment_data  # Should have presigned URL

        # Verify order (oldest first)
        assert data["data"]["attachments"][0]["filename"] == "first.webp"
        assert data["data"]["attachments"][1]["filename"] == "second.webp"

    def test_admin_get_ticket_includes_attachments(self, admin_client, ticket, user, db_session):
        """
        Test that admin can see attachments on any ticket
        """
        TicketAttachment.create_attachment(
            ticket_id=ticket.id,
            s3_key=f"support-tickets/{ticket.id}/admin-view.webp",
            bucket_name="test-bucket",
            filename="admin-view.webp",
            file_size=512,
            content_type="image/webp",
            uploaded_by=user.id,
        )

        response = admin_client.get(f"/ng/admin/support/tickets/{ticket.id}")
        assert response.status_code == 200

        data = response.get_json()
        assert "attachments" in data["data"]
        assert len(data["data"]["attachments"]) == 1
        assert data["data"]["attachments"][0]["filename"] == "admin-view.webp"


