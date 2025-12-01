#!/usr/bin/env python3
"""
Test script for email notifications
"""

import os
import sys
from pathlib import Path
from datetime import datetime


def setup_project_paths():
    """
    Set up project paths
    """
    script_dir = Path(__file__).parent.absolute()

    project_root = script_dir.parent.parent.parent

    ctfd_path = project_root / "external" / "CTFd"
    backend_path = project_root / "backend"

    if not ctfd_path.exists():
        raise FileNotFoundError(f"CTFd not found at {ctfd_path}")

    if not backend_path.exists():
        raise FileNotFoundError(f"Backend not found at {backend_path}")

    sys.path.insert(0, str(ctfd_path))
    sys.path.insert(0, str(backend_path))
    return project_root


def load_env_file(project_root):
    """
    Load environment variables from .env file
    """
    env_file = project_root / ".env.dev"

    if not env_file.exists():
        print(f"Environment file not found: {env_file}")
        return False

    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key] = value

    print(f"Loaded environment from {env_file}")
    return True


def test_email_configuration():
    """
    Test if email service is configured properly
    """
    try:
        project_root = setup_project_paths()

        if not load_env_file(project_root):
            print("Cannot proceed without environment configuration")
            return False

        from ng.core.tests.helpers import create_ctfd, destroy_ctfd
        from ng.emails.services.email_sender import get_email_service
        from ng.emails.services.email_templates import TicketEmailTemplates

    except ImportError as e:
        print(f"Import error: {e}")
        return False
    except FileNotFoundError as e:
        print(f"Path error: {e}")
        return False

    app = create_ctfd()

    try:
        with app.app_context():
            config_vars = {
                "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
                "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
                "AWS_DEFAULT_REGION": os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
                "AWS_SES_FROM_EMAIL": os.getenv("AWS_SES_FROM_EMAIL"),
                "ADMIN_SUPPORT_INBOX_EMAILS": os.getenv("ADMIN_SUPPORT_INBOX_EMAILS"),
                "SERVER_DOMAIN": os.getenv("SERVER_DOMAIN"),
            }

            for key, value in config_vars.items():
                app.config[key] = value

            print(f"AWS SES Access Key: {'SET' if app.config['AWS_ACCESS_KEY_ID'] else 'NOT SET'}")
            print(f"AWS SES Secret Key: {'SET' if app.config['AWS_SECRET_ACCESS_KEY'] else 'NOT SET'}")
            print(f"AWS Default Region: {app.config['AWS_DEFAULT_REGION']}")
            print(f"From Email: {app.config['AWS_SES_FROM_EMAIL']}")
            print(f"Admin Emails: {app.config['ADMIN_SUPPORT_INBOX_EMAILS']}")
            print(f"Server Domain: {app.config['SERVER_DOMAIN']}")

            email_service = get_email_service()
            print(f"AWS SES Configured: {'YES' if email_service.is_configured() else 'NO'}")

            if email_service.is_configured():
                ticket_data = {
                    "id": 999,
                    "subject": "TEST: Email Notification System",
                    "author_name": "Test User",
                    "opened_timestamp": datetime.now().isoformat() + "Z",
                    "status": "open",
                }

                subject, html_body, text_body = TicketEmailTemplates.new_ticket(ticket_data)
                print(f"Email Subject: {subject}")
                print(f"HTML Body: {len(html_body)} characters")
                print(f"Text Body: {len(text_body)} characters")

                team_emails_str = app.config["ADMIN_SUPPORT_INBOX_EMAILS"]
                if team_emails_str:
                    team_emails = [email.strip() for email in team_emails_str.split(",") if email.strip()]
                    print(f"Sending test email to: {team_emails}")

                    success = email_service.send_email(
                        to_emails=team_emails, subject=f"[TEST] {subject}", html_body=html_body, text_body=text_body
                    )

                    if success:
                        print("SUCCESS: Test email sent!")
                        return True
                    else:
                        print("FAILED: Could not send test email")
                        return False
                else:
                    print("No team emails configured - skipping send test")
                    return True
            else:
                print("AWS SES not configured - email notifications disabled")
                return True

    finally:
        destroy_ctfd(app)


def main():
    """
    Main function
    """
    try:
        success = test_email_configuration()
        if success:
            print("TEST COMPLETED SUCCESSFULLY!")
        else:
            print("TEST COMPLETED WITH ISSUES")

    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
