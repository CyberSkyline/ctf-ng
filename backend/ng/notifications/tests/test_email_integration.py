"""
Integration tests for email notifications in support ticket workflows
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

from ...support.controllers import (
    create_ticket_message,
    create_ticket,
)
from ..services import (
    get_email_service,
    NotificationService,
)


@pytest.mark.db
class TestEmailNotificationIntegration:
    """
    Test the email notification flow for support tickets
    """
    @pytest.fixture(autouse = True)
    def reset_email_service(self):
        """
        Reset the global email service between tests
        """
        from ..services import email_service as email_service_module
        email_service_module._email_service = None
        yield
        email_service_module._email_service = None

    def test_new_ticket_sends_email(
        self,
        app,
        db_session,
        user,
        event,
        team_factory
    ):
        """
        Test that creating a new ticket sends an email notification
        """
        with app.app_context():
            team_factory(event = event, members = [user])

            app.config['AWS_SES_ACCESS_KEY_ID'] = 'test_key'
            app.config['AWS_SES_SECRET_ACCESS_KEY'] = 'test_secret'
            app.config['AWS_SES_REGION'] = 'us-east-2'
            app.config['AWS_SES_FROM_EMAIL'] = 'test@example.com'
            app.config['SUPPORT_TEAM_INBOX_EMAILS'
                       ] = 'team@example.com,admin@example.com'
            app.config['SERVER_DOMAIN'] = 'http://localhost:8000'

            with patch('ng.notifications.services.email_service.boto3.client'
                       ) as mock_boto_client:
                mock_ses = MagicMock()
                mock_boto_client.return_value = mock_ses
                mock_ses.get_send_quota.return_value = {'SentLast24Hours': 0}
                mock_ses.send_email.return_value = {
                    'MessageId': 'test-message-id'
                }

                ticket = create_ticket(
                    subject = "Test Issue",
                    text = "I need help with something",
                    current_user = user,
                    event_id = event.id
                )

                mock_ses.send_email.assert_called_once()
                call_args = mock_ses.send_email.call_args[1]

                assert call_args['Source'] == 'test@example.com'
                assert call_args['Destination']['ToAddresses'] == [
                    'team@example.com',
                    'admin@example.com'
                ]
                assert 'Test Issue' in call_args['Message']['Subject']['Data'
                                                                       ]
                assert 'New support ticket' in call_args['Message']['Body'][
                    'Html']['Data']
                assert str(ticket.id
                           ) in call_args['Message']['Body']['Html']['Data']

    def test_ticket_reply_sends_email(
        self,
        app,
        db_session,
        user,
        admin,
        ticket_factory
    ):
        """
        Test that replying to a ticket sends an email notification
        """
        with app.app_context():
            app.config['AWS_SES_ACCESS_KEY_ID'] = 'test_key'
            app.config['AWS_SES_SECRET_ACCESS_KEY'] = 'test_secret'
            app.config['AWS_SES_REGION'] = 'us-east-1'
            app.config['AWS_SES_FROM_EMAIL'] = 'test@example.com'
            app.config['SUPPORT_TEAM_INBOX_EMAILS'] = 'team@example.com'
            app.config['SERVER_DOMAIN'] = 'http://localhost:8000'

            ticket = ticket_factory(
                subject = "User's ticket",
                author_id = user.id
            )

            with patch('ng.notifications.services.email_service.boto3.client'
                       ) as mock_boto_client:
                mock_ses = MagicMock()
                mock_boto_client.return_value = mock_ses
                mock_ses.get_send_quota.return_value = {'SentLast24Hours': 0}
                mock_ses.send_email.return_value = {
                    'MessageId': 'test-message-id'
                }

                create_ticket_message(
                    text = "Thanks for your report, I'll look into this",
                    author_id = admin.id,
                    ticket = ticket,
                    is_admin = True
                )

                mock_ses.send_email.assert_called_once()
                call_args = mock_ses.send_email.call_args[1]

                assert call_args['Source'] == 'test@example.com'
                assert call_args['Destination']['ToAddresses'] == [
                    'team@example.com'
                ]
                assert 'Admin reply' in call_args['Message']['Body']['Html'][
                    'Data']
                assert str(ticket.id
                           ) in call_args['Message']['Body']['Html']['Data']

    def test_email_not_sent_when_not_configured(
        self,
        app,
        db_session,
        user,
        event,
        team_factory
    ):
        """
        Test that emails are not sent when AWS SES is not configured
        """
        with app.app_context():
            team_factory(event = event, members = [user])

            app.config['AWS_SES_ACCESS_KEY_ID'] = None
            app.config['AWS_SES_SECRET_ACCESS_KEY'] = None
            app.config['SUPPORT_TEAM_INBOX_EMAILS'] = 'team@example.com'

            with patch('ng.notifications.services.email_service.logger'
                       ) as mock_logger:
                create_ticket(
                    subject = "Test Issue",
                    text = "I need help with something",
                    current_user = user,
                    event_id = event.id
                )

                mock_logger.debug.assert_called_with(
                    "AWS SES not configured - would send email: %s to %s",
                    "New Support Ticket: Test Issue",
                    ['team@example.com']
                )

    def test_email_service_graceful_failure(
        self,
        app,
        db_session,
        user,
        event,
        team_factory
    ):
        """
        Test that email service failures don't crash the application
        """
        with app.app_context():
            team_factory(event = event, members = [user])

            app.config['AWS_SES_ACCESS_KEY_ID'] = 'test_key'
            app.config['AWS_SES_SECRET_ACCESS_KEY'] = 'test_secret'
            app.config['AWS_SES_REGION'] = 'us-east-1'
            app.config['AWS_SES_FROM_EMAIL'] = 'test@example.com'
            app.config['SUPPORT_TEAM_INBOX_EMAILS'] = 'team@example.com'

            with patch('ng.notifications.services.email_service.boto3.client'
                       ) as mock_boto_client:
                mock_ses = MagicMock()
                mock_boto_client.return_value = mock_ses
                mock_ses.get_send_quota.return_value = {'SentLast24Hours': 0}
                mock_ses.send_email.side_effect = Exception("AWS Error")

                with patch('ng.notifications.services.email_service.logger'
                           ) as mock_logger:
                    # Should not crash
                    ticket = create_ticket(
                        subject = "Test Issue",
                        text = "I need help with something",
                        current_user = user,
                        event_id = event.id
                    )

                    assert ticket.id is not None
                    assert ticket.subject == "Test Issue"

                    mock_logger.error.assert_called()
                    error_call = mock_logger.error.call_args[0]
                    assert "Unexpected error sending email" in error_call[0]

    def test_multiple_team_emails(
        self,
        app,
        db_session,
        user,
        event,
        team_factory
    ):
        """
        Test that emails are sent to multiple team inbox addresses
        """
        with app.app_context():
            team_factory(event = event, members = [user])

            app.config['AWS_SES_ACCESS_KEY_ID'] = 'test_key'
            app.config['AWS_SES_SECRET_ACCESS_KEY'] = 'test_secret'
            app.config['AWS_SES_REGION'] = 'us-east-1'
            app.config['AWS_SES_FROM_EMAIL'] = 'test@example.com'
            app.config[
                'SUPPORT_TEAM_INBOX_EMAILS'
            ] = 'team1@example.com, team2@example.com ,team3@example.com'
            app.config['SERVER_DOMAIN'] = 'http://localhost:8000'

            with patch('ng.notifications.services.email_service.boto3.client'
                       ) as mock_boto_client:
                mock_ses = MagicMock()
                mock_boto_client.return_value = mock_ses
                mock_ses.get_send_quota.return_value = {'SentLast24Hours': 0}
                mock_ses.send_email.return_value = {
                    'MessageId': 'test-message-id'
                }

                create_ticket(
                    subject = "Test Issue",
                    text = "I need help with something",
                    current_user = user,
                    event_id = event.id
                )

                mock_ses.send_email.assert_called_once()
                call_args = mock_ses.send_email.call_args[1]

                expected_emails = [
                    'team1@example.com',
                    'team2@example.com',
                    'team3@example.com'
                ]
                assert call_args['Destination']['ToAddresses'
                                                ] == expected_emails

    def test_email_template_content(
        self,
        app,
        db_session,
        user,
        event,
        team_factory
    ):
        """
        Test that email templates contain the correct content
        """
        with app.app_context():
            team_factory(event = event, members = [user])

            app.config['AWS_SES_ACCESS_KEY_ID'] = 'test_key'
            app.config['AWS_SES_SECRET_ACCESS_KEY'] = 'test_secret'
            app.config['AWS_SES_REGION'] = 'us-east-1'
            app.config['AWS_SES_FROM_EMAIL'] = 'test@example.com'
            app.config['SUPPORT_TEAM_INBOX_EMAILS'] = 'team@example.com'
            app.config['SERVER_DOMAIN'] = 'http://localhost:8000'

            with patch('ng.notifications.services.email_service.boto3.client'
                       ) as mock_boto_client:
                mock_ses = MagicMock()
                mock_boto_client.return_value = mock_ses
                mock_ses.get_send_quota.return_value = {'SentLast24Hours': 0}
                mock_ses.send_email.return_value = {
                    'MessageId': 'test-message-id'
                }

                ticket = create_ticket(
                    subject = "Bug in login system",
                    text = "Users cannot log in",
                    current_user = user,
                    event_id = event.id
                )

                mock_ses.send_email.assert_called_once()
                call_args = mock_ses.send_email.call_args[1]

                subject = call_args['Message']['Subject']['Data']
                assert "New Support Ticket: Bug in login system" in subject

                html_body = call_args['Message']['Body']['Html']['Data']
                assert f"#{ticket.id}" in html_body
                assert "Bug in login system" in html_body
                assert user.name in html_body

                text_body = call_args['Message']['Body']['Text']['Data']
                assert f"#{ticket.id}" in text_body
                assert "Bug in login system" in text_body

    @patch(
        'ng.notifications.services.notification_service.get_email_service'
    )
    def test_notification_service_integration(
        self,
        mock_get_email_service,
        app,
        db_session
    ):
        """
        Test NotificationService email integration directly
        """
        with app.app_context():
            mock_email_service = MagicMock()
            mock_get_email_service.return_value = mock_email_service
            mock_email_service.is_configured.return_value = True
            mock_email_service.send_email.return_value = True

            app.config['SUPPORT_TEAM_INBOX_EMAILS'] = 'team@example.com'

            ticket_data = {
                'id': 123,
                'subject': 'Test Ticket',
                'author_name': 'Test User',
                'opened_timestamp': datetime.now().isoformat() + 'Z',
                'status': 'open'
            }

            NotificationService._send_ticket_email(ticket_data, "new_ticket")

            mock_email_service.send_email.assert_called_once()
            call_kwargs = mock_email_service.send_email.call_args[1]

            assert call_kwargs['to_emails'] == ['team@example.com']
            assert 'New Support Ticket: Test Ticket' in call_kwargs['subject'
                                                                    ]
            assert call_kwargs['html_body']
            assert call_kwargs['text_body']
