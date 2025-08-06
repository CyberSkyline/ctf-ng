"""
Tests for support controllers
"""

import pytest
from datetime import datetime

from ...core.exceptions import (
    BusinessLogicError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from ..controllers import (
    # User actions
    create_ticket,
    close_my_ticket,
    # Shared actions
    create_ticket_message,
    get_ticket,
    list_tickets,
    # Admin actions
    create_tag,
    update_tag,
    list_tags,
    set_ticket_tags,
    assign_ticket,
    unassign_ticket,
    update_ticket_status,
    update_ticket_mute,
    set_ticket_event,
    remove_ticket_event,
    set_ticket_challenge,
    remove_ticket_challenge,
)
from ..models import Ticket, TicketMessage, TicketTag


class TestCreateTicket:
    """Test the create_ticket controller"""

    def test_create_ticket_basic(self, db_session, user, event):
        """Test creating a basic ticket"""
        result = create_ticket(
            subject="Help with login",
            text="I cannot log in to my account",
            current_user=user,
            event_id=event.id,
        )

        assert isinstance(result, Ticket)
        assert result.subject == "Help with login"
        assert result.author_id == user.id
        assert result.event_id == event.id
        assert len(result.messages) == 1
        assert result.messages[0].text == "I cannot log in to my account"

    def test_create_ticket_with_associations(self, db_session, user, event, team_with_member, challenge):
        """Test creating ticket with all associations"""
        result = create_ticket(
            subject="Challenge issue",
            text="The flag is not working",
            current_user=user,
            event_id=event.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
        )

        assert result.event_id == event.id
        assert result.team_id == team_with_member.id
        assert result.challenge_id == challenge.id



class TestCloseMyTicket:
    """Test the close_my_ticket controller"""

    def test_close_my_ticket_success(self, db_session, ticket, user):
        """Test successfully closing own ticket"""
        assert ticket.status == "open"

        result = close_my_ticket(
            ticket=ticket, current_user=user
        )

        assert isinstance(result, Ticket)
        assert result.status == "closed"
        assert result.closed_timestamp is not None



class TestCreateTicketMessage:
    """Test the create_ticket_message controller"""

    def test_create_message_as_user(self, db_session, ticket, user):
        """Test creating message as regular user"""
        result = create_ticket_message(
            text="Additional information",
            author_id=user.id,
            ticket=ticket,
            is_admin=False,
        )

        assert isinstance(result, TicketMessage)
        assert result.text == "Additional information"
        assert result.author_id == user.id
        assert ticket.first_admin_response_timestamp is None

    def test_create_message_as_admin_reopens_ticket(self, db_session, closed_ticket, admin):
        """Test admin message reopens closed ticket"""
        assert closed_ticket.status == "closed"

        create_ticket_message(
            text="I've reopened this to help",
            author_id=admin.id,
            ticket=closed_ticket,
            is_admin=True,
        )

        assert closed_ticket.status == "open"
        assert closed_ticket.closed_timestamp is None

    def test_create_message_sets_first_admin_response(self, db_session, ticket, admin):
        """Test first admin message sets timestamp"""
        assert ticket.first_admin_response_timestamp is None

        create_ticket_message(
            text="I'll help you with this",
            author_id=admin.id,
            ticket=ticket,
            is_admin=True,
        )

        assert ticket.first_admin_response_timestamp is not None



class TestGetTicket:
    """Test the get_ticket controller"""

    def test_get_ticket_basic(self, db_session, ticket_with_messages):
        """Test getting ticket with messages"""
        result = get_ticket(
            ticket=ticket_with_messages
        )

        assert isinstance(result, dict)
        assert "ticket" in result
        assert "messages" in result
        assert result["ticket"] == ticket_with_messages
        assert len(result["messages"]) == 2


class TestListTickets:
    """Test the list_tickets controller"""

    def test_list_tickets_user_view(self, db_session, multiple_tickets, user):
        """Test listing tickets as regular user"""
        result = list_tickets(user_id=user.id, status="all", is_admin=False)

        assert isinstance(result, list)
        # Should only see own tickets
        assert all(t.author_id == user.id for t in result)

    def test_list_tickets_admin_view(self, db_session, multiple_tickets):
        """Test listing tickets as admin with filters"""
        # Test all tickets
        result = list_tickets(status="all", is_admin=True)
        assert len(result) >= 4

        # Test open tickets only
        result = list_tickets(status="open", is_admin=True)
        assert all(t.status == "open" for t in result)

        # Test closed tickets only
        result = list_tickets(status="closed", is_admin=True)
        assert all(t.status == "closed" for t in result)

    def test_list_tickets_with_filters(self, db_session, multiple_tickets, admin, event):
        """Test listing tickets with various admin filters"""
        # Filter by assigned user
        result = list_tickets(assigned_to=admin.id, is_admin=True)
        assert all(t.assigned_to == admin.id for t in result)

        # Filter by event
        result = list_tickets(event_id=event.id, is_admin=True)
        assert all(t.event_id == event.id for t in result)


class TestCreateTag:
    """Test the create_tag controller"""

    def test_create_tag_basic(self, db_session):
        """Test creating a basic tag"""
        result = create_tag(name="feature-request", color="#00FF00")

        assert isinstance(result, TicketTag)
        assert result.name == "feature-request"
        assert result.color == "#00FF00"

    def test_create_tag_with_description(self, db_session):
        """Test creating tag with all fields"""
        result = create_tag(
            name="critical",
            color="#FF0000",
            description="Critical issues requiring immediate attention",
        )

        assert result.description == "Critical issues requiring immediate attention"

    def test_create_tag_duplicate_name(self, db_session, ticket_tag):
        """Test creating tag with duplicate name fails"""
        with pytest.raises(ConflictError):
            create_tag(name=ticket_tag.name, color="#00FF00")


class TestUpdateTag:
    """Test the update_tag controller"""

    def test_update_tag_name(self, db_session, ticket_tag):
        """Test updating tag name"""
        result = update_tag(
            tag=ticket_tag, name="updated-bug"
        )

        assert result.name == "updated-bug"
        assert result.color == ticket_tag.color  # Unchanged

    def test_update_tag_multiple_fields(self, db_session, ticket_tag):
        """Test updating multiple tag fields"""
        result = update_tag(
            tag=ticket_tag,
            name="critical-bug",
            color="#FF00FF",
            description="Updated description",
        )

        assert result.name == "critical-bug"
        assert result.color == "#FF00FF"
        assert result.description == "Updated description"

    def test_update_tag_no_changes(self, db_session, ticket_tag):
        """Test update with no data doesn't error"""
        original_name = ticket_tag.name
        result = update_tag(tag=ticket_tag)

        assert result.name == original_name


class TestListTags:
    """Test the list_tags controller"""

    def test_list_tags_ordered(self, db_session, ticket_tag_factory):
        """Test listing tags returns ordered list"""
        # Create tags with different names
        ticket_tag_factory(name="alpha")
        ticket_tag_factory(name="charlie")
        ticket_tag_factory(name="bravo")

        result = list_tags()

        assert isinstance(result, list)
        assert len(result) >= 3
        # Should be alphabetically ordered
        tag_names = [tag.name for tag in result]
        assert tag_names == sorted(tag_names)


class TestSetTicketTags:
    """Test the set_ticket_tags controller"""

    def test_set_ticket_tags_basic(self, db_session, ticket, ticket_tag_factory):
        """Test setting tags on a ticket"""
        tag1 = ticket_tag_factory(name="urgent")
        tag2 = ticket_tag_factory(name="ui-issue")

        result = set_ticket_tags(
            tag_ids=[tag1.id, tag2.id], ticket=ticket
        )

        assert len(result.tags) == 2
        tag_names = {tag.name for tag in result.tags}
        assert tag_names == {"urgent", "ui-issue"}

    def test_set_ticket_tags_replace_existing(self, db_session, ticket_with_tags, ticket_tag_factory):
        """Test setting tags replaces existing tags"""
        new_tag = ticket_tag_factory(name="new-tag")

        result = set_ticket_tags(
            tag_ids=[new_tag.id],
            ticket=ticket_with_tags,
        )

        assert len(result.tags) == 1
        assert result.tags[0].name == "new-tag"

    def test_set_ticket_tags_clear_all(self, db_session, ticket_with_tags):
        """Test clearing all tags"""
        assert len(ticket_with_tags.tags) > 0

        result = set_ticket_tags(
            tag_ids=[], ticket=ticket_with_tags
        )

        assert len(result.tags) == 0


class TestAssignTicket:
    """Test the assign_ticket controller"""

    def test_assign_ticket(self, db_session, ticket, admin):
        """Test assigning ticket to user"""
        assert ticket.assigned_to is None

        result = assign_ticket(
            user=admin, ticket=ticket
        )

        assert result.assigned_to == admin.id


class TestUnassignTicket:
    """Test the unassign_ticket controller"""

    def test_unassign_ticket(self, db_session, assigned_ticket):
        """Test unassigning ticket"""
        assert assigned_ticket.assigned_to is not None

        result = unassign_ticket(
            ticket=assigned_ticket
        )

        assert result.assigned_to is None


class TestUpdateTicketStatus:
    """Test the update_ticket_status controller"""

    def test_close_ticket(self, db_session, ticket, admin):
        """Test closing an open ticket"""
        assert ticket.status == "open"

        result = update_ticket_status(
            closed=True, ticket=ticket, current_user=admin
        )

        assert result.status == "closed"
        assert result.closed_timestamp is not None

    def test_reopen_ticket(self, db_session, closed_ticket, admin):
        """Test reopening a closed ticket"""
        assert closed_ticket.status == "closed"

        result = update_ticket_status(
            closed=False,
            ticket=closed_ticket,
            current_user=admin,
        )

        assert result.status == "open"
        assert result.closed_timestamp is None



class TestUpdateTicketMute:
    """Test the update_ticket_mute controller"""

    def test_mute_ticket(self, db_session, ticket):
        """Test muting a ticket"""
        assert ticket.muted is False

        result = update_ticket_mute(
            muted=True, ticket=ticket
        )

        assert result.muted is True

    def test_unmute_ticket(self, db_session, muted_ticket):
        """Test unmuting a ticket"""
        assert muted_ticket.muted is True

        result = update_ticket_mute(
            muted=False, ticket=muted_ticket
        )

        assert result.muted is False


class TestSetTicketEvent:
    """Test the set_ticket_event controller"""

    def test_set_event_and_team(self, db_session, ticket, event_factory, team_factory, user):
        """Test setting ticket's event and team"""
        new_event = event_factory()
        new_team = team_factory(event=new_event, members=[user])

        result = set_ticket_event(
            event_id=new_event.id,
            team_id=new_team.id,
            ticket=ticket,
        )

        assert result.event_id == new_event.id
        assert result.team_id == new_team.id


class TestRemoveTicketEvent:
    """Test the remove_ticket_event controller"""

    def test_remove_event(self, db_session, ticket, event_factory, team_factory, user):
        """Test removing ticket's event association"""
        event = event_factory()
        team = team_factory(event=event, members=[user])

        set_ticket_event(event_id=event.id, team_id=team.id, ticket=ticket)

        db_session.refresh(ticket)
        assert ticket.event_id == event.id

        result = remove_ticket_event(ticket=ticket)

        db_session.refresh(result)
        assert result.event_id is None
        assert result.team_id is None


class TestSetTicketChallenge:
    """Test the set_ticket_challenge controller"""

    def test_set_challenge(self, db_session, ticket, challenge):
        """Test setting ticket's challenge"""
        result = set_ticket_challenge(
            challenge_id=challenge.id, ticket=ticket
        )

        assert result.challenge_id == challenge.id


class TestRemoveTicketChallenge:
    """Test the remove_ticket_challenge controller"""

    def test_remove_challenge(self, db_session, ticket, challenge):
        """Test removing ticket's challenge"""

        set_ticket_challenge(challenge_id=challenge.id, ticket=ticket)

        db_session.refresh(ticket)
        assert ticket.challenge_id == challenge.id

        result = remove_ticket_challenge(ticket=ticket)

        db_session.refresh(result)
        assert result.challenge_id is None


class TestControllerIntegration:
    """Integration tests for multiple controllers working together"""

    def test_complete_ticket_flow(self, db_session, user, admin, event, ticket_tag_factory):
        """Test complete ticket lifecycle"""
        # 1. Create ticket
        ticket = create_ticket(
            subject="Integration test ticket",
            text="Initial message",
            current_user=user,
            event_id=event.id,
        )
        assert ticket.status == "open"

        # 2. Admin assigns and tags ticket
        tag = ticket_tag_factory(name="needs-investigation")
        ticket = assign_ticket(
            user=admin, ticket=ticket
        )
        ticket = set_ticket_tags(
            tag_ids=[tag.id], ticket=ticket
        )
        assert ticket.assigned_to == admin.id
        assert len(ticket.tags) == 1

        # 3. Admin responds
        create_ticket_message(
            text="I'm looking into this",
            author_id=admin.id,
            ticket=ticket,
            is_admin=True,
        )
        assert ticket.first_admin_response_timestamp is not None

        # 4. User responds
        create_ticket_message(
            text="Thank you for the help",
            author_id=user.id,
            ticket=ticket,
            is_admin=False,
        )

        # 5. Admin closes ticket
        ticket = update_ticket_status(
            closed=True, ticket=ticket, current_user=admin
        )
        assert ticket.status == "closed"

        # 6. Verify final state
        result = get_ticket(ticket=ticket)
        assert len(result["messages"]) == 3
        assert result["ticket"].status == "closed"
        assert result["ticket"].assigned_to == admin.id
