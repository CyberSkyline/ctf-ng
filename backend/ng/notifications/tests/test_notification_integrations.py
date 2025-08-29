"""
Tests for notification service integrations across the codebase
"""

import base64
import pytest
from unittest.mock import patch, Mock, call

from ..models import Notification
from ..models import AnnouncementType

from ...core.exceptions import BusinessLogicError

from ...scoring.controllers.user_actions.redeem_hint import redeem_hint
from ...scoring.controllers.user_actions.submit_answer import submit_answer
from ...event.controllers.admin.manage_event_lifecycle import start_event, end_event
from ...support.controllers.admin_actions.update_ticket_assignment import assign_ticket
from ...scoring.controllers.admin_actions.award_manual_points import award_manual_points
from ...support.controllers.admin_actions.update_ticket_status import update_ticket_status
from ...support.controllers.all_actions.create_ticket_message import create_ticket_message
from ...event.controllers.admin.import_challenge_from_yaml import import_challenge_from_yaml


class TestScoringIntegrations:
    """
    Test notification integrations in scoring domain
    """
    @patch(
            'ng.scoring.controllers.user_actions.submit_answer.NotificationService'
            )
    def test_submit_answer_broadcasts_attempt(
            self,
            mock_notification_service,
            db_session,
            user,
            team_with_member,
            event,
            challenge,
            question,
            score
            ):
        """
        Test that submitting an answer broadcasts attempt update
        """
        submit_answer(
                event = event,
                challenge = challenge,
                question = question,
                team = team_with_member,
                current_user = user,
                submission = question.answer,
                )

        mock_notification_service.broadcast_attempt_update.assert_called_once_with(
                event_id = event.id,
                team_id = team_with_member.id,
                challenge_id = challenge.id,
                question_id = question.id,
                )

    @patch(
            'ng.scoring.controllers.user_actions.redeem_hint.NotificationService'
            )
    def test_redeem_hint_broadcasts(
            self,
            mock_notification_service,
            db_session,
            user,
            team_with_member,
            event,
            challenge,
            hint
            ):
        """
        Test that redeeming a hint broadcasts to team
        """
        redeem_hint(
                event = event,
                challenge = challenge,
                hint = hint,
                team = team_with_member,
                current_user = user,
                )

        mock_notification_service.broadcast_hint_redeemed.assert_called_once_with(
                event_id = event.id,
                team_id = team_with_member.id,
                challenge_id = challenge.id,
                )

    @patch(
            'ng.scoring.controllers.admin_actions.award_manual_points.NotificationService'
            )
    def test_award_manual_points_broadcasts_leaderboard(
            self,
            mock_notification_service,
            db_session,
            admin,
            team_with_member,
            event,
            score
            ):
        """
        Test that awarding manual points broadcasts leaderboard update
        """
        award_manual_points(
                event = event,
                team = team_with_member,
                score = score,
                points = 100,
                reason = "Good work!",
                admin_id = admin.id,
                )

        mock_notification_service._emit_refetch.assert_called_once_with(
                path = f"/ng/events/{event.id}/leaderboard",
                room = f"event_{event.id}"
                )


class TestSupportIntegrations:
    """
    Test notification integrations in support domain
    """
    @patch(
            'ng.support.controllers.all_actions.create_ticket_message.NotificationService'
            )
    def test_ticket_message_creates_notification(
            self,
            mock_notification_service,
            db_session,
            admin,
            user,
            ticket
            ):
        """
        Test that ticket messages create notifications
        """
        create_ticket_message(
                text = "Here's your answer",
                author_id = admin.id,
                ticket = ticket,
                is_admin = True,
                )

        mock_notification_service.notify_ticket_reply.assert_called_once_with(
                ticket_id = ticket.id,
                author_id = admin.id,
                recipient_id = ticket.author_id,
                is_admin_reply = True,
                )

    @patch(
            'ng.support.controllers.admin_actions.update_ticket_status.NotificationService'
            )
    def test_ticket_status_change_notifies_author(
            self,
            mock_notification_service,
            db_session,
            admin,
            ticket
            ):
        """
        Test that changing ticket status notifies the author
        """
        update_ticket_status(
                closed = True,
                ticket = ticket,
                current_user = admin,
                )

        mock_notification_service.notify_ticket_status_change.assert_called_once_with(
                ticket_id = ticket.id,
                recipient_id = ticket.author_id,
                new_status = "closed",
                changed_by_id = admin.id,
                )

    @patch(
            'ng.support.controllers.admin_actions.update_ticket_status.NotificationService'
            )
    def test_ticket_reopen_notifies_author(
            self,
            mock_notification_service,
            db_session,
            admin,
            ticket
            ):
        """
        Test that reopening ticket notifies the author
        """
        ticket.close_ticket(commit = True)

        update_ticket_status(
                closed = False,
                ticket = ticket,
                current_user = admin,
                )

        mock_notification_service.notify_ticket_status_change.assert_called_once_with(
                ticket_id = ticket.id,
                recipient_id = ticket.author_id,
                new_status = "reopened",
                changed_by_id = admin.id,
                )

    @patch(
            'ng.support.controllers.admin_actions.update_ticket_assignment.NotificationService'
            )
    def test_ticket_assignment_notifies_assignee(
            self,
            mock_notification_service,
            db_session,
            admin,
            ticket
            ):
        """
        Test that assigning a ticket notifies the assignee
        """
        assign_ticket(
                user = admin,
                ticket = ticket,
                )

        mock_notification_service.notify_ticket_assigned.assert_called_once_with(
                ticket_id = ticket.id,
                assigned_to_id = admin.id,
                assigned_by_id = admin.id,
                )


class TestEventIntegrations:
    """
    Test notification integrations in event domain
    """
    @patch(
            'ng.event.controllers.admin.manage_event_lifecycle.NotificationService'
            )
    def test_start_event_sends_announcement(
            self,
            mock_notification_service,
            db_session,
            event
            ):
        """
        Test that starting an event sends announcement
        """
        event.locked = True
        db_session.commit()

        start_event(event)

        mock_notification_service.send_event_announcement.assert_called_once_with(
                event_id = event.id,
                announcement_type = AnnouncementType.EVENT_START,
                title = f"{event.name} Has Started!",
                message = "The competition is now live. Good luck!",
                sender_id = None,
                )

    @patch(
            'ng.event.controllers.admin.manage_event_lifecycle.NotificationService'
            )
    def test_start_event_already_started_raises_error(
            self,
            mock_notification_service,
            db_session,
            event
            ):
        """
        Test that starting an already started event raises error
        """
        event.locked = False
        db_session.commit()

        with pytest.raises(BusinessLogicError) as exc_info:
            start_event(event)

        assert "already started" in str(exc_info.value)

        mock_notification_service.send_event_announcement.assert_not_called()

    @patch(
            'ng.event.controllers.admin.manage_event_lifecycle.NotificationService'
            )
    def test_end_event_sends_announcement(
            self,
            mock_notification_service,
            db_session,
            event
            ):
        """
        Test that ending an event sends announcement
        """
        event.locked = False
        db_session.commit()

        end_event(event)

        mock_notification_service.send_event_announcement.assert_called_once_with(
                event_id = event.id,
                announcement_type = AnnouncementType.EVENT_END,
                title = f"{event.name} Has Ended",
                message = "Thank you for participating!",
                sender_id = None,
                )

    @patch(
            'ng.event.controllers.admin.manage_event_lifecycle.NotificationService'
            )
    def test_end_event_already_ended_raises_error(
            self,
            mock_notification_service,
            db_session,
            event
            ):
        """
        Test that ending an already ended event raises error
        """
        event.locked = True
        db_session.commit()

        with pytest.raises(BusinessLogicError) as exc_info:
            end_event(event)

        assert "already ended" in str(exc_info.value)

        mock_notification_service.send_event_announcement.assert_not_called()

    @patch(
            'ng.event.controllers.admin.import_challenge_from_yaml.NotificationService'
            )
    def test_import_challenge_notifies_participants(
            self,
            mock_notification_service,
            db_session,
            event
            ):
        """
        Test that importing a challenge notifies participants
        """
        yaml_content = """
x-challenge:
  name: Test Challenge
  description: Test description
  summary: Test summary
  questions:
    - name: q1
      body: What is the flag?
      answer: FLAG{test}
      points: 100
      placeholder: "Enter flag here"
      max_attempts: 3
"""

        encoded_yaml = base64.urlsafe_b64encode(yaml_content.encode('utf-8')
                                                ).decode('utf-8')

        json_data = {"yaml": encoded_yaml}

        challenge = import_challenge_from_yaml(event, json_data)

        mock_notification_service.notify_challenge_released.assert_called_once_with(
                event_id = event.id,
                challenge_id = challenge.id,
                challenge_name = challenge.name,
                )


class TestIntegrationWithRealService:
    """
    Integration tests that verify the full flow with real NotificationService
    """
    def test_ticket_reply_creates_stored_notification_and_websocket(
            self,
            db_session,
            admin,
            user,
            ticket
            ):
        """
        Test that ticket reply creates both stored notification and WebSocket event
        """
        with patch('ng.notifications.services.notification_service.emit_event'
                   ) as mock_emit:
            create_ticket_message(
                    text = "Admin response",
                    author_id = admin.id,
                    ticket = ticket,
                    is_admin = True,
                    )
            notifications = Notification.find_filtered_notifications(
                    recipient_id = ticket.author_id
                    )
            assert len(notifications) == 1
            assert notifications[0].title == "Support Ticket Update"
            assert "Admin replied" in notifications[0].message

            assert mock_emit.call_count == 2

            calls = mock_emit.call_args_list

            notification_call = next(
                    (c for c in calls if c[1]['event_name'] == 'notification'),
                    None
                    )
            assert notification_call is not None
            assert notification_call[1]['room'] == f"user_{ticket.author_id}"

            refetch_call = next(
                    (c for c in calls if c[1]['event_name'] == 'refetch'),
                    None
                    )
            assert refetch_call is not None
            assert refetch_call[1]['data'][
                    'path'] == f"/ng/support/tickets/{ticket.id}"
            assert refetch_call[1]['room'] == f"ticket_{ticket.id}"

    def test_attempt_submission_only_websocket_no_stored(
            self,
            db_session,
            user,
            team_with_member,
            event,
            challenge,
            question,
            score
            ):
        """
        Test that attempt submission only sends WebSocket, no stored notification
        """
        with patch('ng.notifications.services.notification_service.emit_event'
                   ) as mock_emit:
            submit_answer(
                    event = event,
                    challenge = challenge,
                    question = question,
                    team = team_with_member,
                    current_user = user,
                    submission = question.answer,
                    )

            notifications = Notification.find_filtered_notifications(
                    recipient_id = user.id
                    )
            assert len(notifications) == 0
            assert mock_emit.call_count == 2

            calls = mock_emit.call_args_list

            challenge_call = next(
                    (
                            c for c in calls if
                            f"/ng/events/{event.id}/challenges/{challenge.id}"
                            in str(c)
                            ),
                    None
                    )
            assert challenge_call is not None

            leaderboard_call = next(
                    (
                            c for c in calls
                            if f"/ng/events/{event.id}/leaderboard" in str(c)
                            ),
                    None
                    )
            assert leaderboard_call is not None
