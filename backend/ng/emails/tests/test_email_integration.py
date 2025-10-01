"""
Integration tests for smart email routing in support ticket workflows
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

from ...support.controllers import (
    create_ticket_message,
    create_ticket,
)
from ..services import get_email_service
from ...notifications.services import NotificationService


@pytest.mark.db
class TestEmailSendingSmartRouting:
    """
    Test email routing based on ticket context
    """
    @pytest.fixture(autouse = True)
    def reset_email_service(self):
        """
        Reset the global email service between tests
        """
        from ..services import email_sender as email_sender_module
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
        app.config['AWS_SES_REGION'] = 'us-east-2'
        app.config['AWS_SES_FROM_EMAIL'] = 'noreply@ctf.com'
        app.config['ADMIN_SUPPORT_INBOX_EMAILS'
                   ] = 'admin@ctf.com,support@ctf.com'
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

    def test_new_ticket_goes_to_admin_inbox(
        self,
        app,
        db_session,
        user,
        event,
        team_factory,
        email_config,
        mock_ses
    ):
        """
        Test that new tickets go to ADMIN_SUPPORT_INBOX_EMAILS only
        """
        with app.app_context():
            team_factory(event = event, members = [user])

            create_ticket(
                subject = "Test Issue",
                text = "I need help with something",
                current_user = user,
                event_id = event.id
            )

            mock_ses.send_email.assert_called_once()
            call_args = mock_ses.send_email.call_args[1]

            recipient_emails = call_args['Destination']['ToAddresses']
            assert set(recipient_emails) == {
                'admin@ctf.com',
                'support@ctf.com'
            }
            assert 'New Support Ticket: Test Issue' in call_args['Message'][
                'Subject']['Data']

    def test_admin_reply_to_team_ticket_notifies_team_members(
        self,
        app,
        db_session,
        user,
        admin,
        event,
        team_factory,
        user_factory,
        email_config,
        mock_ses
    ):
        """
        Test that admin reply to team ticket goes to all team members
        """
        with app.app_context():
            user2 = user_factory(name = "User 2", email = "user2@test.com")
            user3 = user_factory(name = "User 3", email = "user3@test.com")

            team = team_factory(
                event = event,
                members = [user,
                           user2,
                           user3]
            )

            ticket = create_ticket(
                subject = "Team Issue",
                text = "Team needs help",
                current_user = user,
                event_id = event.id,
                team_id = team.id
            )
            mock_ses.reset_mock()

            create_ticket_message(
                text = "I'll help you with this",
                author_id = admin.id,
                ticket = ticket,
                is_admin = True
            )

            mock_ses.send_email.assert_called_once()
            call_args = mock_ses.send_email.call_args[1]

            recipient_emails = set(call_args['Destination']['ToAddresses'])
            expected_emails = {
                user.email,
                user2.ctfd_user.email,
                user3.ctfd_user.email
            }
            assert recipient_emails == expected_emails
            assert 'Admin Reply' in call_args['Message']['Body']['Html'][
                'Data']

    def test_admin_reply_to_non_team_ticket_notifies_author(
        self,
        app,
        db_session,
        user,
        admin,
        ticket_factory,
        email_config,
        mock_ses
    ):
        """
        Test that admin reply to non team ticket goes to ticket author
        """
        with app.app_context():
            ticket = ticket_factory(
                subject = "Individual Issue",
                author_id = user.id,
                team_id = None
            )

            create_ticket_message(
                text = "Let me look into this",
                author_id = admin.id,
                ticket = ticket,
                is_admin = True
            )

            mock_ses.send_email.assert_called_once()
            call_args = mock_ses.send_email.call_args[1]

            assert call_args['Destination']['ToAddresses'] == [user.email]

    def test_user_reply_to_assigned_ticket_notifies_assigned_admin(
        self,
        app,
        db_session,
        user,
        admin,
        ticket_factory,
        email_config,
        mock_ses
    ):
        """
        Test that user reply to assigned ticket goes to assigned admin
        """
        with app.app_context():
            ticket = ticket_factory(
                subject = "Assigned Issue",
                author_id = user.id
            )
            ticket.assign_to_user(admin.id, commit = True)

            create_ticket_message(
                text = "Thanks, here's more info",
                author_id = user.id,
                ticket = ticket,
                is_admin = False
            )

            mock_ses.send_email.assert_called_once()
            call_args = mock_ses.send_email.call_args[1]

            assert call_args['Destination']['ToAddresses'] == [admin.email]

    def test_user_reply_to_unassigned_ticket_goes_to_admin_inbox(
        self,
        app,
        db_session,
        user,
        ticket_factory,
        email_config,
        mock_ses
    ):
        """
        Test that user reply to unassigned ticket goes to admin inbox
        """
        with app.app_context():
            app.config['AWS_SES_ACCESS_KEY_ID'] = 'test_key'
            app.config['AWS_SES_SECRET_ACCESS_KEY'] = 'test_secret'
            app.config['AWS_SES_REGION'] = 'us-east-2'
            app.config['AWS_SES_FROM_EMAIL'] = 'noreply@ctf.com'
            app.config['ADMIN_SUPPORT_INBOX_EMAILS'
                       ] = 'admin@ctf.com,support@ctf.com'
            app.config['SERVER_DOMAIN'] = 'http://localhost:8000'

            from ..services import email_sender as email_sender_module
            email_sender_module._email_service = None

            ticket = ticket_factory(
                subject = "Unassigned Issue",
                author_id = user.id
            )

            create_ticket_message(
                text = "Any update on this?",
                author_id = user.id,
                ticket = ticket,
                is_admin = False
            )

            mock_ses.send_email.assert_called_once()
            call_args = mock_ses.send_email.call_args[1]

            recipient_emails = call_args['Destination']['ToAddresses']
            assert set(recipient_emails) == {
                'admin@ctf.com',
                'support@ctf.com'
            }

    def test_implicit_assignment_on_admin_reply(
        self,
        app,
        db_session,
        user,
        admin,
        ticket_factory,
        email_config,
        mock_ses
    ):
        """
        Test that admin reply to unassigned ticket auto assigns ticket
        """
        with app.app_context():
            ticket = ticket_factory(
                subject = "Unassigned Issue",
                author_id = user.id
            )

            assert ticket.assigned_to is None

            create_ticket_message(
                text = "I'll handle this",
                author_id = admin.id,
                ticket = ticket,
                is_admin = True
            )

            db_session.refresh(ticket)

            assert ticket.assigned_to == admin.id

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
            app.config['ADMIN_SUPPORT_INBOX_EMAILS'] = 'admin@ctf.com'

            with patch('ng.emails.services.email_sender.logger'
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
                    ['admin@ctf.com']
                )

    def test_multiple_admin_emails_for_new_tickets(
        self,
        app,
        db_session,
        user,
        event,
        team_factory,
        mock_ses
    ):
        """
        Test that new tickets go to multiple admin inbox addresses
        """
        with app.app_context():
            team_factory(event = event, members = [user])

            app.config['AWS_SES_ACCESS_KEY_ID'] = 'test_key'
            app.config['AWS_SES_SECRET_ACCESS_KEY'] = 'test_secret'
            app.config['AWS_SES_REGION'] = 'us-east-2'
            app.config['AWS_SES_FROM_EMAIL'] = 'noreply@ctf.com'
            app.config['ADMIN_SUPPORT_INBOX_EMAILS'
                       ] = 'admin1@ctf.com, admin2@ctf.com ,admin3@ctf.com'
            app.config['SERVER_DOMAIN'] = 'http://localhost:8000'

            create_ticket(
                subject = "Test Issue",
                text = "I need help with something",
                current_user = user,
                event_id = event.id
            )

            mock_ses.send_email.assert_called_once()
            call_args = mock_ses.send_email.call_args[1]

            expected_emails = {
                'admin1@ctf.com',
                'admin2@ctf.com',
                'admin3@ctf.com'
            }
            recipient_emails = call_args['Destination']['ToAddresses']
            assert set(recipient_emails) == expected_emails

    def test_email_service_graceful_failure(
        self,
        app,
        db_session,
        user,
        event,
        team_factory,
        email_config
    ):
        """
        Test that email service failures don't crash the application
        """
        with app.app_context():
            team_factory(event = event, members = [user])

            with patch('ng.emails.services.email_sender.boto3.client'
                       ) as mock_boto_client:
                mock_ses = MagicMock()
                mock_boto_client.return_value = mock_ses
                mock_ses.get_send_quota.return_value = {'SentLast24Hours': 0}
                mock_ses.send_email.side_effect = Exception("AWS Error")

                with patch('ng.emails.services.email_sender.logger'
                           ) as mock_logger:
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

    def test_no_emails_sent_when_no_recipients_found(
        self,
        app,
        db_session,
        user,
        ticket_factory,
        email_config,
        mock_ses
    ):
        """
        Test that no emails are sent when no recipients are configured
        """
        with app.app_context():
            app.config['ADMIN_SUPPORT_INBOX_EMAILS'] = ''

            ticket = ticket_factory(
                subject = "Orphaned Ticket",
                author_id = user.id
            )

            create_ticket_message(
                text = "Any update?",
                author_id = user.id,
                ticket = ticket,
                is_admin = False
            )

            mock_ses.send_email.assert_not_called()
