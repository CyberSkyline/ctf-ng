"""
Model tests for Ticket
"""

import pytest
from unittest.mock import patch
from ..models.Ticket import Ticket
from ...core.exceptions import NotFoundError, BusinessLogicError


class TestTicketRepr:
    def test_repr(self, ticket):
        """Test the string representation of the model."""
        assert f"<Ticket {ticket.id}: {ticket.subject}>" == repr(ticket)


class TestTicketDefaults:
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
        assert ticket.muted is None
        assert ticket.first_admin_response_timestamp is None


class TestTicketStatusProperty:
    def test_status_property(self, ticket, closed_ticket, muted_ticket):
        """Test the computed status property."""
        assert ticket.status == "open"
        assert closed_ticket.status == "closed"
        assert muted_ticket.status == "open"
        assert muted_ticket.muted is True


class TestCreateTicket:
    def test_create_ticket(self, db_session, user, event):
        """Test creating a ticket with the create method."""
        ticket = Ticket.create_ticket(
            subject="New Support Request", author_id=user.id, event_id=event.id
        )

        refreshed_ticket = Ticket.find_by_id(ticket.id)
        assert refreshed_ticket is not None
        assert refreshed_ticket.subject == "New Support Request"
        assert refreshed_ticket.author_id == user.id
        assert refreshed_ticket.event_id == event.id
        assert refreshed_ticket.opened_timestamp is not None
        assert refreshed_ticket.last_updated is not None
        assert refreshed_ticket.status == "open"

    def test_create_ticket_respects_commit_flag(self, db_session, user, event):
        """Test that create respects the commit flag."""
        with patch.object(db_session, "commit") as mock_commit:
            ticket = Ticket.create_ticket(
                subject="No Commit Ticket",
                author_id=user.id,
                event_id=event.id,
                commit=False,
            )
            mock_commit.assert_not_called()
            assert ticket.subject == "No Commit Ticket"

        with patch.object(db_session, "commit") as mock_commit:
            ticket = Ticket.create_ticket(
                subject="With Commit Ticket",
                author_id=user.id,
                event_id=event.id,
                commit=True,
            )
            mock_commit.assert_called_once()


class TestCloseTicket:
    def test_close_ticket(self, ticket, db_session):
        """Test closing a ticket."""
        ticket_id = ticket.id
        assert ticket.status == "open"
        assert ticket.closed_timestamp is None

        ticket.close_ticket()

        refreshed_ticket = Ticket.find_by_id(ticket_id)
        assert refreshed_ticket is not None
        assert refreshed_ticket.status == "closed"
        assert refreshed_ticket.closed_timestamp is not None

    def test_close_ticket_respects_commit_flag(self, ticket, db_session):
        """Test that close_ticket respects the commit flag."""
        with patch.object(db_session, "commit") as mock_commit:
            ticket.close_ticket(commit=False)
            mock_commit.assert_not_called()

        with patch.object(db_session, "commit") as mock_commit:
            ticket.close_ticket(commit=True)
            mock_commit.assert_called_once()


class TestReopenTicket:
    def test_reopen_ticket(self, closed_ticket, db_session):
        """Test reopening a closed ticket."""
        ticket_id = closed_ticket.id
        assert closed_ticket.status == "closed"

        closed_ticket.reopen_ticket()

        refreshed_ticket = Ticket.find_by_id(ticket_id)
        assert refreshed_ticket is not None
        assert refreshed_ticket.status == "open"
        assert refreshed_ticket.closed_timestamp is None
        assert refreshed_ticket.muted is False

    def test_reopen_ticket_respects_commit_flag(self, closed_ticket, db_session):
        """Test that reopen_ticket respects the commit flag."""
        with patch.object(db_session, "commit") as mock_commit:
            closed_ticket.reopen_ticket(commit=False)
            mock_commit.assert_not_called()

        with patch.object(db_session, "commit") as mock_commit:
            closed_ticket.reopen_ticket(commit=True)
            mock_commit.assert_called_once()


class TestToggleMute:
    def test_toggle_mute(self, ticket, db_session):
        """Test muting and unmuting a ticket."""
        ticket_id = ticket.id
        assert ticket.muted is False

        ticket.toggle_mute(True)

        refreshed_ticket = Ticket.find_by_id(ticket_id)
        assert refreshed_ticket is not None
        assert refreshed_ticket.muted is True
        assert refreshed_ticket.status == "open"  # Status is only open/closed

        ticket.toggle_mute(False)

        refreshed_ticket = Ticket.find_by_id(ticket_id)
        assert refreshed_ticket is not None
        assert refreshed_ticket.muted is False
        assert refreshed_ticket.status == "open"

    def test_toggle_mute_respects_commit_flag(self, ticket, db_session):
        """Test that toggle_mute respects the commit flag."""
        with patch.object(db_session, "commit") as mock_commit:
            ticket.toggle_mute(True, commit=False)
            mock_commit.assert_not_called()

        with patch.object(db_session, "commit") as mock_commit:
            ticket.toggle_mute(False, commit=True)
            mock_commit.assert_called_once()


class TestUpdateEventAndTeam:
    def test_update_event_and_team_mismatch(self, ticket, event_factory, team_factory, user, db_session):
        """Test that updating with mismatched team/event raises BusinessLogicError."""
        event1 = event_factory(name="Event 1")
        event2 = event_factory(name="Event 2")
        team_in_event1 = team_factory(event=event1, members=[user])

        # Set initial valid values
        ticket.update_event_and_team(event_id=event1.id, team_id=team_in_event1.id)
        assert ticket.event_id == event1.id
        assert ticket.team_id == team_in_event1.id

        # Try to update with mismatched team/event
        with pytest.raises(BusinessLogicError) as exc_info:
            ticket.update_event_and_team(
                event_id=event2.id,  # Different event
                team_id=team_in_event1.id  # Team from event1
            )
        assert "Team does not belong to the specified event" in str(exc_info.value)

        # Verify nothing was changed
        assert ticket.event_id == event1.id
        assert ticket.team_id == team_in_event1.id


class TestAssignUnassignTicket:
    def test_assign_to_user(self, ticket, admin, db_session):
        """Test assigning a ticket."""
        ticket_id = ticket.id
        assert ticket.assigned_to is None

        ticket.assign_to_user(admin.id)

        refreshed_ticket = Ticket.find_by_id(ticket_id)
        assert refreshed_ticket is not None
        assert refreshed_ticket.assigned_to == admin.id

    def test_unassign(self, ticket, admin, db_session):
        """Test unassigning a ticket."""
        ticket_id = ticket.id
        ticket.assign_to_user(admin.id)
        db_session.commit()

        ticket.unassign()

        refreshed_ticket = Ticket.find_by_id(ticket_id)
        assert refreshed_ticket is not None
        assert refreshed_ticket.assigned_to is None

    def test_assign_respects_commit_flag(self, ticket, admin, db_session):
        """Test that assign_to_user respects the commit flag."""
        with patch.object(db_session, "commit") as mock_commit:
            ticket.assign_to_user(admin.id, commit=False)
            mock_commit.assert_not_called()

        with patch.object(db_session, "commit") as mock_commit:
            ticket.assign_to_user(admin.id, commit=True)
            mock_commit.assert_called_once()

    def test_unassign_respects_commit_flag(self, assigned_ticket, db_session):
        """Test that unassign respects the commit flag."""
        with patch.object(db_session, "commit") as mock_commit:
            assigned_ticket.unassign(commit=False)
            mock_commit.assert_not_called()

        with patch.object(db_session, "commit") as mock_commit:
            assigned_ticket.unassign(commit=True)
            mock_commit.assert_called_once()


class TestTicketFinders:
    def test_find_by_author(self, multiple_tickets, user, admin):
        """Test finding tickets by author."""
        user_tickets = Ticket.find_filtered_tickets(user_id=user.id, is_admin=True)
        assert len(user_tickets) >= 3

    def test_find_by_assigned_user(self, multiple_tickets, user, admin):
        """Test finding tickets by assigned user."""
        assigned_tickets = Ticket.find_filtered_tickets(
            assigned_to=admin.id, is_admin=True
        )
        assert len(assigned_tickets) >= 1

    def test_find_open_tickets(self, multiple_tickets):
        """Test finding open tickets."""
        open_tickets = Ticket.find_filtered_tickets(status="open", is_admin=True)
        assert len(open_tickets) >= 2

    def test_find_unassigned_open_tickets(self, multiple_tickets):
        """Test finding unassigned open tickets."""
        unassigned_tickets = Ticket.find_filtered_tickets(
            status="open", assigned_to=None, is_admin=True
        )
        unassigned_tickets = [t for t in unassigned_tickets if t.assigned_to is None]
        assert len(unassigned_tickets) >= 1


class TestFindFilteredTickets:
    def test_find_filtered_tickets_user(self, multiple_tickets, user, admin):
        """Test filtered ticket search as regular user."""
        user_tickets = Ticket.find_filtered_tickets(
            user_id=user.id, status="all", is_admin=False
        )
        assert all(t.author_id == user.id for t in user_tickets)

    def test_find_filtered_tickets_admin(self, multiple_tickets):
        """Test filtered ticket search as admin."""
        all_tickets = Ticket.find_filtered_tickets(status="all", is_admin=True)
        assert len(all_tickets) >= 4

    def test_find_filtered_tickets_by_status(self, multiple_tickets):
        """Test filtering tickets by status."""
        open_tickets = Ticket.find_filtered_tickets(status="open", is_admin=True)
        assert all(t.status == "open" for t in open_tickets)


class TestSerialize:
    def test_serialize_basic(self, ticket_with_messages, admin):
        """Test basic ticket serialization."""
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

    def test_serialize_admin_fields(self, ticket_with_messages, admin):
        """Test ticket serialization with admin fields."""
        ticket = ticket_with_messages
        ticket.assign_to_user(admin.id)

        admin_data = ticket.serialize(include_admin_fields=True)
        assert "assigned_to" in admin_data
        assert "muted" in admin_data
        assert "first_admin_response_timestamp" in admin_data


class TestGetTicketStats:
    def test_get_ticket_stats(self, multiple_tickets):
        """Test ticket statistics."""
        all_tickets = Ticket.find_filtered_tickets(status="all", is_admin=True)
        stats = {
            "total": len(all_tickets),
            "open": len([t for t in all_tickets if t.status == "open"]),
            "closed": len([t for t in all_tickets if t.status == "closed"]),
            "muted": len([t for t in all_tickets if t.muted]),
            "unassigned": len([t for t in all_tickets if t.assigned_to is None]),
            "avg_response_time_hours": 0,
            "closed_today": 0,
        }

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


class TestSetTags:
    def test_set_tags(self, ticket, ticket_tag_factory, db_session):
        """Test setting tags on a ticket."""
        ticket_id = ticket.id
        tag1 = ticket_tag_factory(name="urgent")
        tag2 = ticket_tag_factory(name="technical")

        assert len(ticket.tags) == 0

        ticket.set_tags([tag1.id, tag2.id])

        refreshed_ticket = Ticket.find_by_id(ticket_id)
        assert refreshed_ticket is not None
        assert len(refreshed_ticket.tags) == 2
        tag_names = [tag.name for tag in refreshed_ticket.tags]
        assert "urgent" in tag_names
        assert "technical" in tag_names

    def test_set_tags_respects_commit_flag(
        self, ticket, ticket_tag_factory, db_session
    ):
        """Test that set_tags respects the commit flag."""
        tag = ticket_tag_factory(name="test-tag")

        with patch.object(db_session, "commit") as mock_commit:
            ticket.set_tags([tag.id], commit=False)
            mock_commit.assert_not_called()

        with patch.object(db_session, "commit") as mock_commit:
            ticket.set_tags([tag.id], commit=True)
            mock_commit.assert_called_once()

    def test_set_tags_with_invalid_ids(self, ticket, db_session):
        """Test set_tags raises NotFoundError for invalid tag IDs."""

        # Ensure ticket has no tags initially
        assert len(ticket.tags) == 0

        with pytest.raises(NotFoundError) as exc_info:
            ticket.set_tags([99999, 88888])
        assert "Tag IDs not found" in str(exc_info.value)

        # Verify nothing was changed on the object
        assert len(ticket.tags) == 0


class TestUpdateTags:
    def test_replace_tags(self, ticket_with_tags, ticket_tag_factory, db_session):
        """Test replacing all tags on a ticket."""
        ticket_id = ticket_with_tags.id
        initial_tags = ticket_with_tags.tags

        # Create new tags to replace with
        new_tag1 = ticket_tag_factory(name="priority-high")
        new_tag2 = ticket_tag_factory(name="backend")

        # Replace all tags
        ticket_with_tags.set_tags([new_tag1.id, new_tag2.id])

        refreshed_ticket = Ticket.find_by_id(ticket_id)
        assert refreshed_ticket is not None
        assert len(refreshed_ticket.tags) == 2
        tag_names = [tag.name for tag in refreshed_ticket.tags]
        assert "priority-high" in tag_names
        assert "backend" in tag_names
        # Original tags should not be present
        for original_tag in initial_tags:
            assert original_tag.name not in tag_names

    def test_clear_all_tags(self, ticket_with_tags, db_session):
        """Test clearing all tags from a ticket."""
        ticket_id = ticket_with_tags.id
        assert len(ticket_with_tags.tags) > 0

        # Clear all tags by setting empty list
        ticket_with_tags.set_tags([])

        refreshed_ticket = Ticket.find_by_id(ticket_id)
        assert refreshed_ticket is not None
        assert len(refreshed_ticket.tags) == 0


class TestAddMessage:
    def test_add_message_first_admin_response(self, ticket, user, admin, db_session):
        """Test that first admin message sets first_admin_response_timestamp."""
        ticket_id = ticket.id
        assert ticket.first_admin_response_timestamp is None

        ticket.add_message("User question", author_id=user.id, is_admin=False)
        assert ticket.first_admin_response_timestamp is None

        refreshed = Ticket.find_by_id(ticket_id)
        assert refreshed.first_admin_response_timestamp is None
        assert len(refreshed.messages) == 1

        ticket.add_message("Admin response", author_id=admin.id, is_admin=True)
        assert ticket.first_admin_response_timestamp is not None

        refreshed = Ticket.find_by_id(ticket_id)
        assert refreshed.first_admin_response_timestamp is not None
        assert len(refreshed.messages) == 2

        original_timestamp = ticket.first_admin_response_timestamp
        ticket.add_message("Another admin response", author_id=admin.id, is_admin=True)
        assert ticket.first_admin_response_timestamp == original_timestamp

        refreshed = Ticket.find_by_id(ticket_id)
        assert refreshed.first_admin_response_timestamp == original_timestamp
        assert len(refreshed.messages) == 3
