"""
Unit tests for support domain logic
"""

from datetime import datetime, timedelta, timezone


def utc_now() -> datetime:
    """Get current UTC datetime. Replacement for deprecated datetime.utcnow()."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class ValidationError(Exception):
    def __init__(self, message, errors=None):
        self.message = message
        self.errors = errors or {}
        super().__init__(message)


class TestTicketPriorityLogic:
    """Test ticket priority calculation algorithms."""

    def test_priority_scoring_calculation(self):
        """Test how ticket priority scores are calculated."""
        urgent_ticket = {"priority": "urgent", "created_hours_ago": 2}
        high_ticket = {"priority": "high", "created_hours_ago": 12}
        normal_ticket = {"priority": "normal", "created_hours_ago": 24}
        low_ticket = {"priority": "low", "created_hours_ago": 48}

        def calculate_priority_score(ticket):
            priority_weights = {"urgent": 100, "high": 75, "normal": 50, "low": 25}
            age_multiplier = max(1.0, ticket["created_hours_ago"] / 24.0)
            return priority_weights[ticket["priority"]] * age_multiplier

        urgent_score = calculate_priority_score(urgent_ticket)
        high_score = calculate_priority_score(high_ticket)
        normal_score = calculate_priority_score(normal_ticket)
        low_score = calculate_priority_score(low_ticket)

        assert urgent_score == 100.0  # 100 * max(1.0, 2/24) = 100 * 1.0
        assert high_score == 75.0  # 75 * max(1.0, 12/24) = 75 * 1.0
        assert normal_score == 50.0  # 50 * max(1.0, 24/24) = 50 * 1.0
        assert low_score == 50.0  # 25 * max(1.0, 48/24) = 25 * 2.0

    def test_ticket_aging_calculation(self):
        """Test calculation of ticket aging for priority adjustment."""
        now = utc_now()
        tickets = [
            {"id": 1, "created_at": now - timedelta(hours=1)},  # 1 hour old
            {"id": 2, "created_at": now - timedelta(hours=12)},  # 12 hours old
            {"id": 3, "created_at": now - timedelta(days=2)},  # 2 days old
            {"id": 4, "created_at": now - timedelta(days=7)},  # 1 week old
        ]

        def calculate_age_hours(ticket, current_time=now):
            return (current_time - ticket["created_at"]).total_seconds() / 3600

        ages = [calculate_age_hours(t) for t in tickets]

        assert abs(ages[0] - 1) < 0.1  # ~1 hour
        assert abs(ages[1] - 12) < 0.1  # ~12 hours
        assert abs(ages[2] - 48) < 0.1  # ~48 hours
        assert abs(ages[3] - 168) < 0.1  # ~168 hours


class TestTicketStatusWorkflow:
    """Test ticket status transition logic."""

    def test_valid_status_transitions(self):
        """Test that status transitions follow business rules."""
        valid_transitions = {
            "open": ["in_progress", "closed"],
            "in_progress": ["open", "resolved", "closed"],
            "resolved": ["closed", "open"],
            "closed": [],
        }

        def can_transition(from_status, to_status):
            return to_status in valid_transitions.get(from_status, [])

        # Valid transitions
        assert can_transition("open", "in_progress") is True
        assert can_transition("in_progress", "resolved") is True
        assert can_transition("resolved", "closed") is True
        assert can_transition("resolved", "open") is True  # Reopening

        # Invalid transitions
        assert can_transition("closed", "open") is False
        assert can_transition("open", "resolved") is False  # Must go through in_progress
        assert can_transition("closed", "in_progress") is False

    def test_auto_assignment_logic(self):
        """Test automatic ticket assignment algorithm."""
        support_agents = [
            {
                "id": 1,
                "name": "Agent A",
                "current_tickets": 3,
                "specialties": ["technical"],
            },
            {
                "id": 2,
                "name": "Agent B",
                "current_tickets": 1,
                "specialties": ["billing"],
            },
            {
                "id": 3,
                "name": "Agent C",
                "current_tickets": 5,
                "specialties": ["technical", "billing"],
            },
        ]

        def find_best_agent(ticket_type, agents):
            qualified_agents = [a for a in agents if ticket_type in a["specialties"]]
            if not qualified_agents:
                qualified_agents = agents  # Fallback to any agent

            return min(qualified_agents, key=lambda a: a["current_tickets"])

        technical_ticket_agent = find_best_agent("technical", support_agents)
        billing_ticket_agent = find_best_agent("billing", support_agents)

        assert technical_ticket_agent["id"] == 1  # Agent A has 3 tickets vs Agent C's 5
        assert billing_ticket_agent["id"] == 2  # Agent B has only 1 ticket


class TestTicketTagging:
    """Test ticket tagging and categorization logic."""

    def test_auto_tag_generation(self):
        """Test automatic tag generation from ticket content."""

        def generate_auto_tags(title, description):
            tags = []
            content = (title + " " + description).lower()

            if any(word in content for word in ["error", "bug", "crash", "broken"]):
                tags.append("bug")
            if any(word in content for word in ["login", "password", "auth"]):
                tags.append("authentication")
            if any(word in content for word in ["slow", "performance", "timeout"]):
                tags.append("performance")
            if any(word in content for word in ["payment", "billing", "charge"]):
                tags.append("billing")

            return tags

        bug_ticket = generate_auto_tags(
            "App crashes on startup",
            "The application throws an error when I try to start it",
        )
        auth_ticket = generate_auto_tags("Cannot login", "My password is not working")
        perf_ticket = generate_auto_tags("Site is slow", "Pages take forever to load, very slow performance")

        assert "bug" in bug_ticket
        assert "authentication" in auth_ticket
        assert "performance" in perf_ticket

    def test_tag_color_assignment(self):
        """Test automatic color assignment for tags."""

        def assign_tag_color(tag_name):
            color_map = {
                "bug": "#ff4444",  # Red
                "feature": "#44ff44",  # Green
                "authentication": "#4444ff",  # Blue
                "performance": "#ffaa44",  # Orange
                "billing": "#aa44ff",  # Purple
            }
            return color_map.get(tag_name, "#cccccc")  # Default gray

        assert assign_tag_color("bug") == "#ff4444"
        assert assign_tag_color("feature") == "#44ff44"
        assert assign_tag_color("unknown") == "#cccccc"


class TestTicketValidation:
    """Test ticket validation logic."""

    def test_ticket_subject_validation(self):
        """Test ticket subject validation rules."""

        def validate_ticket_subject(subject):
            errors = []

            if not subject or not subject.strip():
                errors.append("Subject is required")
            elif len(subject.strip()) < 5:
                errors.append("Subject must be at least 5 characters")
            elif len(subject) > 200:
                errors.append("Subject must be less than 200 characters")

            return errors

        assert validate_ticket_subject("") == ["Subject is required"]
        assert validate_ticket_subject("Hi") == ["Subject must be at least 5 characters"]
        assert validate_ticket_subject("A" * 201) == ["Subject must be less than 200 characters"]
        assert validate_ticket_subject("Valid ticket subject") == []

    def test_attachment_validation(self):
        """Test ticket attachment validation logic."""

        def validate_attachment(filename, size_bytes):
            errors = []
            max_size = 10 * 1024 * 1024  # 10MB
            allowed_extensions = [
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".pdf",
                ".txt",
                ".log",
            ]

            if size_bytes > max_size:
                errors.append(f"File size must be less than {max_size // (1024 * 1024)}MB")

            extension = filename.lower().split(".")[-1] if "." in filename else ""
            if f".{extension}" not in allowed_extensions:
                errors.append(f"File type .{extension} not allowed")

            return errors

        assert validate_attachment("test.exe", 1024) == ["File type .exe not allowed"]
        assert validate_attachment("test.jpg", 15 * 1024 * 1024) == ["File size must be less than 10MB"]
        assert validate_attachment("test.pdf", 1024) == []


class TestNotificationLogic:
    """Test ticket notification logic."""

    def test_notification_recipient_calculation(self):
        """Test calculation of who should receive notifications."""
        ticket = {
            "id": 123,
            "author_id": 1,
            "assigned_to": 2,
            "status": "in_progress",
            "watchers": [3, 4],
        }

        def get_notification_recipients(ticket, event_type):
            recipients = set()

            if event_type == "created":
                recipients.add(ticket["author_id"])  # Author
                if ticket.get("assigned_to"):
                    recipients.add(ticket["assigned_to"])  # Assignee

            elif event_type == "status_changed":
                recipients.add(ticket["author_id"])  # Author
                if ticket.get("assigned_to"):
                    recipients.add(ticket["assigned_to"])  # Assignee
                recipients.update(ticket.get("watchers", []))  # Watchers

            return list(recipients)

        created_recipients = get_notification_recipients(ticket, "created")
        status_recipients = get_notification_recipients(ticket, "status_changed")

        assert set(created_recipients) == {1, 2}
        assert set(status_recipients) == {1, 2, 3, 4}


class TestTicketPriorityAlgorithms:
    """Test ticket priority scoring and classification algorithms."""

    def test_ticket_priority_calculation(self):
        """Test comprehensive ticket priority scoring logic."""

        def calculate_ticket_priority(ticket_data):
            base_score = 0

            category_scores = {
                "technical_issue": 70,
                "account_problem": 60,
                "challenge_issue": 80,
                "platform_bug": 90,
                "feature_request": 30,
                "general_inquiry": 20,
            }

            category = ticket_data.get("category", "general_inquiry")
            base_score += category_scores.get(category, 40)

            severity_multipliers = {
                "critical": 2.0,  # Platform down, data loss
                "high": 1.5,  # Major functionality broken
                "medium": 1.0,  # Minor issues, workarounds exist
                "low": 0.7,  # Cosmetic issues, suggestions
            }

            severity = ticket_data.get("severity", "medium")
            base_score *= severity_multipliers.get(severity, 1.0)

            user_type = ticket_data.get("user_type", "regular")
            if user_type == "premium":
                base_score *= 1.3
            elif user_type == "admin":
                base_score *= 1.2

            if ticket_data.get("during_active_event", False):
                base_score *= 1.4

            created_hour = ticket_data.get("created_at", utc_now()).hour
            if created_hour < 9 or created_hour > 17:  # Outside 9-5
                base_score *= 0.9

            age_hours = ticket_data.get("age_hours", 0)
            if age_hours > 72:  # 3 days
                base_score *= 1.5
            elif age_hours > 24:  # 1 day
                base_score *= 1.2

            response_count = ticket_data.get("response_count", 0)
            if response_count > 5:
                base_score *= 0.8

            return round(base_score, 1)

        critical_ticket = {
            "category": "platform_bug",
            "severity": "critical",
            "user_type": "premium",
            "during_active_event": True,
            "created_at": utc_now().replace(hour=14),
            "age_hours": 1,
            "response_count": 1,
        }

        priority = calculate_ticket_priority(critical_ticket)
        # 90 * 2.0 * 1.3 * 1.4 * 1.0 * 1.0 = 327.6
        assert priority > 300

        low_ticket = {
            "category": "feature_request",
            "severity": "low",
            "user_type": "regular",
            "during_active_event": False,
            "created_at": utc_now().replace(hour=22),
            "age_hours": 2,
            "response_count": 8,
        }

        priority = calculate_ticket_priority(low_ticket)
        # 30 * 0.7 * 1.0 * 1.0 * 0.9 * 1.0 * 0.8 = 15.12
        assert priority < 20
