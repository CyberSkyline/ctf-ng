"""
Tests for notification link generation based on recipient role
"""

import pytest

from ..models.Notification import (
    Notification,
    NotificationType,
)
from ..services.notification_service import(
    generate_notification_link,
)


class TestNotificationLinkGeneration:
    def test_admin_receives_admin_ticket_link(
        self,
        notification_factory,
        admin,
        ticket_factory
    ):
        """
        Test that admin users receive admin panel ticket links
        """
        ticket = ticket_factory()
        notification = notification_factory(
            type=NotificationType.TICKET_MESSAGE,
            recipient_id=admin.id,
            ticket_id=ticket.id,
            title="Ticket Update",
            message=f"User replied to ticket #{ticket.id}"
        )

        link = generate_notification_link(notification)

        assert link == f"/admin/tickets?id={ticket.id}"

    def test_user_receives_user_ticket_link(
        self,
        notification_factory,
        user_factory,
        ticket_factory
    ):
        """
        Test that regular users receive user side ticket links
        """
        user = user_factory()
        ticket = ticket_factory(author_id=user.id)
        notification = notification_factory(
            type=NotificationType.TICKET_MESSAGE,
            recipient_id=user.ctfd_user.id,
            ticket_id=ticket.id,
            title="Ticket Update",
            message=f"Admin replied to ticket #{ticket.id}"
        )

        link = generate_notification_link(notification)

        assert link == f"/support/{ticket.id}"

    def test_ticket_message_includes_ticket_number(
        self,
        notification_factory,
        user_factory,
        ticket_factory
    ):
        """
        Test that ticket notifications include ticket number in message
        """
        user = user_factory()
        ticket = ticket_factory(author_id=user.id)
        notification = notification_factory(
            type=NotificationType.TICKET_MESSAGE,
            recipient_id=user.ctfd_user.id,
            ticket_id=ticket.id,
            title="Support Ticket Update",
            message=f"Admin replied to ticket #{ticket.id}"
        )

        assert f"#{ticket.id}" in notification.message

    def test_serialized_notification_includes_link(
        self,
        notification_factory,
        admin,
        ticket_factory
    ):
        """
        Test that serialized notification includes the link field
        """
        ticket = ticket_factory()
        notification = notification_factory(
            type=NotificationType.TICKET_MESSAGE,
            recipient_id=admin.id,
            ticket_id=ticket.id,
            title="Ticket Update",
            message=f"User replied to ticket #{ticket.id}"
        )

        serialized = notification.serialize()

        assert "link" in serialized
        assert serialized["link"] == f"/admin/tickets?id={ticket.id}"

    def test_notification_without_recipient_returns_none(
        self,
        ticket_factory
    ):
        """
        Test that notification without recipient returns None for link
        """
        ticket = ticket_factory()
        notification = Notification(
            type=NotificationType.TICKET_MESSAGE,
            recipient_id=99999,
            ticket_id=ticket.id,
            title="Test",
            message="Test message"
        )

        link = generate_notification_link(notification)

        assert link is None

    def test_team_kicked_notification_links_to_event(
        self,
        notification_factory,
        user_factory,
        event_factory
    ):
        """
        Test that team kicked notifications link to event page
        """
        user = user_factory()
        event = event_factory()
        notification = notification_factory(
            type=NotificationType.TEAM_MEMBER_KICKED,
            recipient_id=user.ctfd_user.id,
            event_id=event.id,
            title="Removed from Team",
            message="You have been removed from a team"
        )

        link = generate_notification_link(notification)

        assert link == f"/events/{event.id}"

    def test_ticket_assigned_notification_for_admin(
        self,
        notification_factory,
        admin,
        ticket_factory
    ):
        """
        Test ticket assigned notification links to admin panel
        """
        ticket = ticket_factory()
        notification = notification_factory(
            type=NotificationType.TICKET_ASSIGNED,
            recipient_id=admin.id,
            ticket_id=ticket.id,
            title="Ticket Assigned",
            message=f"Ticket #{ticket.id} has been assigned to you"
        )

        link = generate_notification_link(notification)

        assert link == f"/admin/tickets?id={ticket.id}"
        assert f"#{ticket.id}" in notification.message

    def test_ticket_status_change_notification(
        self,
        notification_factory,
        user_factory,
        ticket_factory
    ):
        """
        Test ticket status change notification includes number and link
        """
        user = user_factory()
        ticket = ticket_factory(author_id=user.id)
        notification = notification_factory(
            type=NotificationType.TICKET_STATUS_CHANGE,
            recipient_id=user.ctfd_user.id,
            ticket_id=ticket.id,
            title="Ticket Status Changed",
            message=f"Ticket #{ticket.id} was closed"
        )

        serialized = notification.serialize()

        assert f"#{ticket.id}" in notification.message
        assert serialized["link"] == f"/support/{ticket.id}"
