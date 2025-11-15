"""
Integration tests for player kicked notification emails
"""

import pytest
from unittest.mock import patch, MagicMock
from ..services import email_sender as email_sender_module
from ...notifications.models import Notification, NotificationType
from ...notifications.services.notification_service import NotificationService


@pytest.mark.db
class TestKickedPlayerEmailNotification:
    """
    Test email notifications when a player is kicked from a team
    """
    @pytest.fixture(autouse=True)
    def reset_email_service(self):
        """
        Reset the global email service between tests
        """
        email_sender_module._email_service = None
        yield
        email_sender_module._email_service = None

    @pytest.fixture
    def email_config(self, app):
        """
        Standard email configuration for tests
        """
        app.config['AWS_SES_ACCESS_KEY_ID'] = 'test_key'
        app.config['AWS_SES_SECRET_ACCESS_KEY'] = 'test_secret'
        app.config['AWS_DEFAULT_REGION'] = 'us-east-1'
        app.config['AWS_SES_FROM_EMAIL'] = 'noreply@ctf.com'
        app.config['SERVER_DOMAIN'] = 'http://localhost:8000'

    @pytest.fixture
    def mock_ses(self):
        """
        Mock AWS SES client for email tests
        """
        with patch('ng.emails.services.email_sender.boto3.client'
                   ) as mock_boto_client:
            mock_ses = MagicMock()
            mock_boto_client.return_value = mock_ses
            mock_ses.get_send_quota.return_value = {'SentLast24Hours': 0}
            mock_ses.send_email.return_value = {
                'MessageId': 'test-message-id'
            }
            yield mock_ses

    def test_admin_kicks_player_sends_email(
        self,
        app,
        db_session,
        user_factory,
        admin,
        event,
        team_factory,
        email_config,
        mock_ses
    ):
        """
        Test that email is sent when admin kicks a player from a team
        """
        with app.app_context():
            user1 = user_factory(name="Captain", email="captain@test.com")
            user2 = user_factory(name="Member", email="member@test.com")

            team = team_factory(
                event=event,
                members=[user1, user2]
            )

            NotificationService.notify_player_kicked_from_team(
                kicked_user_id=user2.ctfd_user.id,
                team_id=team.id,
                team_name=team.name,
                event_id=event.id,
                event_name=event.name,
                kicked_by_id=admin.id,
            )

            mock_ses.send_email.assert_called_once()
            call_args = mock_ses.send_email.call_args[1]

            recipient_emails = call_args['Destination']['ToAddresses']
            assert recipient_emails == [user2.ctfd_user.email]

            subject = call_args['Message']['Subject']['Data']
            assert f"Removed from Team: {team.name}" in subject

            html_body = call_args['Message']['Body']['Html']['Data']
            assert team.name in html_body
            assert event.name in html_body
            assert "admin" in html_body.lower()

    def test_captain_kicks_player_creates_notification(
        self,
        app,
        db_session,
        user_factory,
        event,
        team_factory,
        email_config,
        mock_ses
    ):
        """
        Test that DB notification and email are created when captain kicks a player
        """
        with app.app_context():
            captain = user_factory(name="Captain", email="captain@test.com")
            member = user_factory(name="Member", email="member@test.com")

            team = team_factory(
                event=event,
                members=[captain, member]
            )

            NotificationService.notify_player_kicked_from_team(
                kicked_user_id=member.ctfd_user.id,
                team_id=team.id,
                team_name=team.name,
                event_id=event.id,
                event_name=event.name,
                kicked_by_id=captain.ctfd_user.id,
            )

            notification = Notification.query.filter_by(
                recipient_id=member.ctfd_user.id,
                type=NotificationType.TEAM_MEMBER_KICKED
            ).first()

            assert notification is not None
            assert notification.team_id == team.id
            assert notification.event_id == event.id
            assert notification.sender_id == captain.ctfd_user.id
            assert "Removed from Team" in notification.title
            assert team.name in notification.message
            assert event.name in notification.message

            mock_ses.send_email.assert_called_once()
            call_args = mock_ses.send_email.call_args[1]
            assert call_args['Destination']['ToAddresses'] == [member.ctfd_user.email]
