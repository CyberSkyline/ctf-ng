"""
Support domain - API endpoint testing
"""

import json


class TestUserTicketEndpoints:
    """Tests for user ticket API endpoints."""

    def test_support_routes_loaded(self, app):
        """Test that support routes are registered."""
        ticket_routes = [rule for rule in app.url_map.iter_rules() if "tickets" in rule.rule or "support" in rule.rule]

        assert len(ticket_routes) > 0, "No support routes found"

    def test_get_my_tickets(self, logged_in_client, ticket_factory, user):
        """Test getting user's own tickets."""

        ticket1 = ticket_factory(subject="First Issue", author_id=user.id)
        ticket2 = ticket_factory(subject="Second Issue", author_id=user.id)

        response = logged_in_client.get("/ng/tickets")

        assert response.status_code == 200
        data = response.get_json()
        assert "success" in data
        assert data["success"] is True
        assert "data" in data
        assert "tickets" in data["data"]
        assert len(data["data"]["tickets"]) >= 2

        # TODO - Check that the tickets returned match. You can use .serialize to compare
        assert ticket1 is not None # placeholder
        assert ticket2 is not None # placeholder

    def test_get_my_tickets_filtered(self, logged_in_client, user, closed_ticket, muted_ticket, ticket):
        """Test getting filtered tickets."""

        response = logged_in_client.get("/ng/tickets?status=open")
        assert response.status_code == 200
        data = response.get_json()
        tickets = data["data"]["tickets"]
        assert all(t["status"] == "open" for t in tickets)

        response = logged_in_client.get("/ng/tickets?status=closed")
        assert response.status_code == 200
        data = response.get_json()
        tickets = data["data"]["tickets"]
        assert all(t["status"] == "closed" for t in tickets)

    def test_create_ticket(self, logged_in_client, event, team):
        """Test creating a new ticket."""
        ticket_data = {
            "subject": "I need help with a challenge",
            "event_id": event.id,
            "team_id": team.id
        }

        response = logged_in_client.post(
            "/ng/tickets",
            data=json.dumps(ticket_data),
            content_type="application/json"
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert "ticket" in data["data"]
        assert data["data"]["ticket"]["subject"] == ticket_data["subject"]
        assert data["data"]["ticket"]["event_id"] == event.id

    def test_create_ticket_with_tags(self, logged_in_client, ticket_tag_factory):
        """Test creating a ticket with tags."""

        tag1 = ticket_tag_factory(name="help-needed")
        tag2 = ticket_tag_factory(name="challenge-issue")

        ticket_data = {
            "subject": "Tagged ticket",
            "tag_ids": [tag1.id, tag2.id]
        }

        response = logged_in_client.post(
            "/ng/tickets",
            data=json.dumps(ticket_data),
            content_type="application/json"
        )

        assert response.status_code == 201
        data = response.get_json()
        assert len(data["data"]["ticket"]["tags"]) == 2

    def test_create_ticket_validation(self, logged_in_client):
        """Test ticket creation validation."""

        response = logged_in_client.post(
            "/ng/tickets",
            data=json.dumps({}),
            content_type="application/json"
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_get_ticket_details(self, logged_in_client, ticket_with_messages):
        """Test getting ticket details."""

        response = logged_in_client.get(f"/ng/tickets/{ticket_with_messages.id}")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "ticket" in data["data"]
        assert "messages" in data["data"]
        assert data["data"]["ticket"]["id"] == ticket_with_messages.id
        assert len(data["data"]["messages"]) == 2

    def test_get_ticket_details_no_access(self, logged_in_client, ticket_factory, admin):
        """Test accessing another user's ticket."""

        other_ticket = ticket_factory(subject="Admin's ticket", author_id=admin.id)

        response = logged_in_client.get(f"/ng/tickets/{other_ticket.id}")

        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False

    def test_update_ticket(self, logged_in_client, ticket):
        """Test updating own ticket."""
        update_data = {
            "subject": "Updated subject"
        }

        response = logged_in_client.patch(
            f"/ng/tickets/{ticket.id}",
            data=json.dumps(update_data),
            content_type="application/json"
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["ticket"]["subject"] == "Updated subject"

    def test_reply_to_ticket(self, logged_in_client, ticket):
        """Test adding a message to ticket."""

        message_data = {
            "text": "Here's some additional information"
        }

        response = logged_in_client.post(
            f"/ng/tickets/{ticket.id}/messages",
            data=json.dumps(message_data),
            content_type="application/json"
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert "message" in data["data"]
        assert data["data"]["message"]["text"] == message_data["text"]

    def test_reply_to_ticket_no_access(self, logged_in_client, ticket_factory, admin):
        """Test replying to another user's ticket."""

        other_ticket = ticket_factory(subject="Not my ticket", author_id=admin.id)

        response = logged_in_client.post(
            f"/ng/tickets/{other_ticket.id}/messages",
            data=json.dumps({"text": "Trying to reply"}),
            content_type="application/json"
        )

        assert response.status_code == 403


class TestAdminTicketEndpoints:
    """Tests for admin ticket API endpoints."""

    def test_admin_get_all_tickets(self, admin_client, multiple_tickets):
        """Test admin getting all tickets."""

        response = admin_client.get("/ng/admin/support/tickets")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "tickets" in data["data"]
        assert len(data["data"]["tickets"]) >= 4

    def test_admin_filter_tickets(self, admin_client, multiple_tickets, user):
        """Test admin filtering tickets."""

        response = admin_client.get("/ng/admin/support/tickets?status=open")
        assert response.status_code == 200
        data = response.get_json()
        assert all(t["status"] == "open" for t in data["data"]["tickets"])

        response = admin_client.get(f"/ng/admin/support/tickets?user_id={user.id}")
        assert response.status_code == 200
        data = response.get_json()
        assert all(t["author_id"] == user.id for t in data["data"]["tickets"])

    def test_admin_get_any_ticket(self, admin_client, ticket_with_messages):
        """Test admin getting any ticket details."""

        response = admin_client.get(f"/ng/admin/support/tickets/{ticket_with_messages.id}")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "ticket" in data["data"]
        assert "messages" in data["data"]

        assert "assigned_to" in data["data"]["ticket"]
        assert "muted" in data["data"]["ticket"]

    def test_admin_update_any_ticket(self, admin_client, ticket):
        """Test admin updating any ticket."""

        update_data = {
            "subject": "Admin updated this",
            "muted": True
        }

        response = admin_client.patch(
            f"/ng/admin/support/tickets/{ticket.id}",
            data=json.dumps(update_data),
            content_type="application/json"
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["ticket"]["subject"] == "Admin updated this"
        assert data["data"]["ticket"]["muted"] is True

    def test_admin_assign_ticket(self, admin_client, ticket, admin):
        """Test admin assigning ticket to themselves."""

        assign_data = {
            "user_id": admin.id
        }

        response = admin_client.post(
            f"/ng/admin/support/tickets/{ticket.id}/assign",
            data=json.dumps(assign_data),
            content_type="application/json"
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["ticket"]["assigned_to"] == admin.id

    def test_admin_unassign_ticket(self, admin_client, assigned_ticket):
        """Test admin unassigning ticket."""

        response = admin_client.post(f"/ng/admin/support/tickets/{assigned_ticket.id}/unassign")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["ticket"]["assigned_to"] is None

    def test_admin_close_ticket(self, admin_client, ticket):
        """Test admin closing ticket."""

        response = admin_client.post(f"/ng/admin/support/tickets/{ticket.id}/close")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["ticket"]["status"] == "closed"

    def test_admin_reopen_ticket(self, admin_client, closed_ticket):
        """Test admin reopening ticket."""

        response = admin_client.post(f"/ng/admin/support/tickets/{closed_ticket.id}/reopen")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["ticket"]["status"] == "open"

    def test_admin_reply_reopens_ticket(self, admin_client, closed_ticket):
        """Test admin reply to closed ticket reopens it."""

        message_data = {
            "text": "Following up on this"
        }

        response = admin_client.post(
            f"/ng/admin/support/tickets/{closed_ticket.id}/messages",
            data=json.dumps(message_data),
            content_type="application/json"
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["ticket_reopened"] is True


class TestTagManagementEndpoints:
    """Tests for tag management"""

    def test_admin_create_tag(self, admin_client):
        """Test admin creating a tag."""

        tag_data = {
            "name": "new",
            "description": "new tag"
        }

        response = admin_client.post(
            "/ng/admin/support/tags",
            data=json.dumps(tag_data),
            content_type="application/json"
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["tag"]["name"] == "new"

    def test_admin_list_tags(self, admin_client, ticket_tag_factory):
        """Test admin listing all tags."""

        ticket_tag_factory(name="test-tags1")
        ticket_tag_factory(name="test-tags2")

        response = admin_client.get("/ng/admin/support/tags")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "tags" in data["data"]
        assert len(data["data"]["tags"]) >= 2

    def test_admin_update_tag(self, admin_client, ticket_tag):
        """Test admin updating a tag."""

        update_data = {
            "color": "#00FF00",
            "description": "Updated bug reports"
        }

        response = admin_client.patch(
            f"/ng/admin/support/tags/{ticket_tag.id}",
            data=json.dumps(update_data),
            content_type="application/json"
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["tag"]["color"] == "#00FF00"

    def test_admin_delete_tag(self, admin_client, ticket_tag_factory):
        """Test admin deleting a tag."""

        tag = ticket_tag_factory(name="to-be-deleted")
        response = admin_client.delete(f"/ng/admin/support/tags/{tag.id}")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

    def test_admin_add_tags_to_ticket(self, admin_client, ticket, ticket_tag_factory):
        """Test admin adding tags to ticket."""

        tag1 = ticket_tag_factory(name="priority-high")
        tag2 = ticket_tag_factory(name="needs-review")

        tag_data = {
            "tag_ids": [tag1.id, tag2.id]
        }

        response = admin_client.post(
            f"/ng/admin/support/tickets/{ticket.id}/tags",
            data=json.dumps(tag_data),
            content_type="application/json"
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]["ticket"]["tags"]) == 2

    def test_admin_remove_tags_from_ticket(self, admin_client, ticket_with_tags):
        """Test admin removing tags from ticket."""

        tag_to_remove = ticket_with_tags.tags[0]

        tag_data = {
            "tag_ids": [tag_to_remove.id]
        }

        response = admin_client.delete(
            f"/ng/admin/support/tickets/{ticket_with_tags.id}/tags",
            data=json.dumps(tag_data),
            content_type="application/json"
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]["ticket"]["tags"]) == 1


class TestStatisticsEndpoints:
    def test_admin_get_ticket_stats(self, admin_client, multiple_tickets):
        """Test admin getting ticket statistics."""

        response = admin_client.get("/ng/admin/support/tickets/stats")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "stats" in data["data"]

        stats = data["data"]["stats"]
        assert "total" in stats
        assert "open" in stats
        assert "closed" in stats
        assert "muted" in stats
        assert "unassigned" in stats
        assert "avg_response_time_hours" in stats
        assert "closed_today" in stats
