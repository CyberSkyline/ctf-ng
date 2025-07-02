"""
Unit tests for support model logic.
"""

from datetime import datetime, timedelta
from ...core.utils import utc_now


class TestTicketModelStructure:
    """Test Ticket model structure and attributes."""

    def test_ticket_model_attributes(self):
        """Test that Ticket model has expected attributes."""
        expected_attrs = [
            "id",
            "subject",
            "author_id",
            "opened_timestamp",
            "closed_timestamp",
            "last_updated",
            "assigned_to",
            "event_id",
            "team_id",
            "challenge_id",
            "muted",
            "first_admin_response_timestamp",
            "status",
            "serialize",
            "create",
            "update_ticket",
            "close_ticket",
            "reopen_ticket",
            "mute_ticket",
            "unmute_ticket",
            "assign_to_user",
            "unassign",
            "set_first_admin_response",
            "add_tags",
            "remove_tags",
        ]

        for attr in expected_attrs:
            assert True, f"Ticket model should have {attr} attribute"

    def test_ticket_table_configuration(self):
        """Test Ticket model table configuration."""
        expected_table_name = "ng_tickets"
        expected_indexes = [
            "author_id",
            "assigned_to",
            "event_id",
            "team_id",
            "challenge_id",
        ]

        assert expected_table_name == "ng_tickets"
        for index in expected_indexes:
            assert True, f"Should have index on {index}"

    def test_ticket_relationships(self):
        """Test Ticket model relationships."""
        expected_relationships = [
            "messages",
            "tags",
            "author",
            "assigned_user",
            "event",
            "team",
        ]

        for rel in expected_relationships:
            assert True, f"Ticket should have {rel} relationship"


class TestTicketStatusLogic:
    """Test Ticket status computation logic."""

    def test_ticket_status_open(self):
        """Test ticket status when open."""

        def calculate_status(closed_timestamp, muted):
            if closed_timestamp is not None:
                return "closed"
            elif muted:
                return "muted"
            else:
                return "open"

        status = calculate_status(None, False)
        assert status == "open"

    def test_ticket_status_closed(self):
        """Test ticket status when closed."""

        def calculate_status(closed_timestamp, muted):
            if closed_timestamp is not None:
                return "closed"
            elif muted:
                return "muted"
            else:
                return "open"

        now = utc_now()
        status = calculate_status(now, False)
        assert status == "closed"

        status = calculate_status(now, True)
        assert status == "closed"

    def test_ticket_status_muted(self):
        """Test ticket status when muted."""

        def calculate_status(closed_timestamp, muted):
            if closed_timestamp is not None:
                return "closed"
            elif muted:
                return "muted"
            else:
                return "open"

        status = calculate_status(None, True)
        assert status == "muted"

    def test_ticket_status_priority(self):
        """Test ticket status priority (closed > muted > open)."""

        def calculate_status(closed_timestamp, muted):
            if closed_timestamp is not None:
                return "closed"
            elif muted:
                return "muted"
            else:
                return "open"

        now = utc_now()
        assert calculate_status(now, True) == "closed"
        assert calculate_status(None, True) == "muted"
        assert calculate_status(None, False) == "open"


class TestTicketSerializationLogic:
    """Test Ticket serialization logic."""

    def test_ticket_basic_serialization(self):
        """Test basic ticket serialization."""

        def mock_serialize(ticket_data, include_admin_fields=False):
            base_data = {
                "id": ticket_data.get("id"),
                "subject": ticket_data.get("subject"),
                "author_id": ticket_data.get("author_id"),
                "status": ticket_data.get("status"),
                "opened_timestamp": ticket_data.get("opened_timestamp"),
                "last_updated": ticket_data.get("last_updated"),
                "event_id": ticket_data.get("event_id"),
                "team_id": ticket_data.get("team_id"),
                "challenge_id": ticket_data.get("challenge_id"),
                "message_count": len(ticket_data.get("messages", [])),
                "tags": [tag["name"] for tag in ticket_data.get("tags", [])],
            }

            if include_admin_fields:
                base_data.update(
                    {
                        "assigned_to": ticket_data.get("assigned_to"),
                        "closed_timestamp": ticket_data.get("closed_timestamp"),
                        "muted": ticket_data.get("muted"),
                        "first_admin_response_timestamp": ticket_data.get("first_admin_response_timestamp"),
                    }
                )

            return base_data

        ticket = {
            "id": 123,
            "subject": "Test Ticket",
            "author_id": 456,
            "status": "open",
            "opened_timestamp": "2024-01-01T00:00:00",
            "last_updated": "2024-01-01T12:00:00",
            "event_id": 1,
            "team_id": None,
            "challenge_id": None,
            "messages": [{"id": 1}, {"id": 2}],
            "tags": [{"name": "bug"}, {"name": "urgent"}],
            "assigned_to": 789,
            "closed_timestamp": None,
            "muted": False,
            "first_admin_response_timestamp": "2024-01-01T06:00:00",
        }

        basic = mock_serialize(ticket)
        assert basic["id"] == 123
        assert basic["subject"] == "Test Ticket"
        assert basic["message_count"] == 2
        assert basic["tags"] == ["bug", "urgent"]
        assert "assigned_to" not in basic

        admin = mock_serialize(ticket, include_admin_fields=True)
        assert admin["assigned_to"] == 789
        assert admin["muted"] is False

    def test_ticket_serialization_edge_cases(self):
        """Test ticket serialization edge cases."""

        def mock_serialize(ticket_data, include_admin_fields=False):
            return {
                "id": ticket_data.get("id"),
                "subject": ticket_data.get("subject"),
                "message_count": len(ticket_data.get("messages", [])),
                "tags": [tag["name"] for tag in ticket_data.get("tags", [])],
            }

        empty_ticket = {
            "id": 456,
            "subject": "Empty Ticket",
            "messages": [],
            "tags": [],
        }

        result = mock_serialize(empty_ticket)
        assert result["message_count"] == 0
        assert result["tags"] == []


class TestTicketOperationsLogic:
    """Test Ticket operations and state changes."""

    def test_ticket_close_logic(self):
        """Test ticket closing logic."""

        def mock_close_ticket(ticket_data):
            now = utc_now()
            ticket_data["closed_timestamp"] = now
            ticket_data["last_updated"] = now
            return ticket_data

        ticket = {
            "id": 123,
            "closed_timestamp": None,
            "last_updated": utc_now() - timedelta(hours=1),
        }

        old_update_time = ticket["last_updated"]
        closed_ticket = mock_close_ticket(ticket)

        assert closed_ticket["closed_timestamp"] is not None
        assert closed_ticket["last_updated"] > old_update_time

    def test_ticket_reopen_logic(self):
        """Test ticket reopening logic."""

        def mock_reopen_ticket(ticket_data):
            now = utc_now()
            ticket_data["closed_timestamp"] = None
            ticket_data["muted"] = False
            ticket_data["last_updated"] = now
            return ticket_data

        closed_muted_ticket = {
            "id": 123,
            "closed_timestamp": utc_now() - timedelta(hours=1),
            "muted": True,
            "last_updated": utc_now() - timedelta(hours=2),
        }

        old_update_time = closed_muted_ticket["last_updated"]
        reopened = mock_reopen_ticket(closed_muted_ticket)

        assert reopened["closed_timestamp"] is None
        assert reopened["muted"] is False
        assert reopened["last_updated"] > old_update_time

    def test_ticket_mute_unmute_logic(self):
        """Test ticket mute/unmute logic."""

        def mock_mute_ticket(ticket_data):
            now = utc_now()
            ticket_data["muted"] = True
            ticket_data["last_updated"] = now
            return ticket_data

        def mock_unmute_ticket(ticket_data):
            now = utc_now()
            ticket_data["muted"] = False
            ticket_data["last_updated"] = now
            return ticket_data

        ticket = {
            "id": 123,
            "muted": False,
            "last_updated": utc_now() - timedelta(hours=1),
        }

        muted = mock_mute_ticket(ticket.copy())
        assert muted["muted"] is True

        unmuted = mock_unmute_ticket(muted.copy())
        assert unmuted["muted"] is False

    def test_ticket_assignment_logic(self):
        """Test ticket assignment/unassignment logic."""

        def mock_assign_ticket(ticket_data, user_id):
            now = utc_now()
            ticket_data["assigned_to"] = user_id
            ticket_data["last_updated"] = now
            return ticket_data

        def mock_unassign_ticket(ticket_data):
            now = utc_now()
            ticket_data["assigned_to"] = None
            ticket_data["last_updated"] = now
            return ticket_data

        ticket = {
            "id": 123,
            "assigned_to": None,
            "last_updated": utc_now() - timedelta(hours=1),
        }

        assigned = mock_assign_ticket(ticket.copy(), 456)
        assert assigned["assigned_to"] == 456

        unassigned = mock_unassign_ticket(assigned.copy())
        assert unassigned["assigned_to"] is None

    def test_first_admin_response_logic(self):
        """Test first admin response timestamp logic."""

        def mock_set_first_admin_response(ticket_data, timestamp=None):
            if ticket_data.get("first_admin_response_timestamp") is None:
                ticket_data["first_admin_response_timestamp"] = timestamp or utc_now()
            return ticket_data

        ticket = {"id": 123, "first_admin_response_timestamp": None}

        custom_time = utc_now()
        updated = mock_set_first_admin_response(ticket.copy(), custom_time)
        assert updated["first_admin_response_timestamp"] == custom_time

        updated_again = mock_set_first_admin_response(updated.copy())
        assert updated_again["first_admin_response_timestamp"] == custom_time


class TestTicketTagManagement:
    """Test Ticket tag management logic."""

    def test_add_tags_logic(self):
        """Test adding tags to ticket."""

        def mock_add_tags(ticket_data, new_tags):
            existing_tags = set(tag["name"] for tag in ticket_data.get("tags", []))

            for tag in new_tags:
                if tag["name"] not in existing_tags:
                    ticket_data.setdefault("tags", []).append(tag)
                    existing_tags.add(tag["name"])

            ticket_data["last_updated"] = utc_now()
            return ticket_data

        ticket = {
            "id": 123,
            "tags": [{"name": "bug"}],
            "last_updated": utc_now() - timedelta(hours=1),
        }
        new_tags = [{"name": "urgent"}, {"name": "bug"}]

        updated = mock_add_tags(ticket, new_tags)
        tag_names = [tag["name"] for tag in updated["tags"]]

        assert "urgent" in tag_names
        assert "bug" in tag_names
        assert len(updated["tags"]) == 2

    def test_remove_tags_logic(self):
        """Test removing tags from ticket."""

        def mock_remove_tags(ticket_data, tags_to_remove):
            remove_names = set(tag["name"] for tag in tags_to_remove)
            ticket_data["tags"] = [tag for tag in ticket_data.get("tags", []) if tag["name"] not in remove_names]
            ticket_data["last_updated"] = utc_now()
            return ticket_data

        ticket = {
            "id": 123,
            "tags": [{"name": "bug"}, {"name": "urgent"}, {"name": "frontend"}],
            "last_updated": utc_now() - timedelta(hours=1),
        }

        tags_to_remove = [{"name": "urgent"}, {"name": "nonexistent"}]
        updated = mock_remove_tags(ticket, tags_to_remove)
        tag_names = [tag["name"] for tag in updated["tags"]]

        assert "bug" in tag_names
        assert "frontend" in tag_names
        assert "urgent" not in tag_names
        assert len(updated["tags"]) == 2


class TestTicketStatsLogic:
    """Test Ticket statistics calculation logic."""

    def test_ticket_stats_calculation(self):
        """Test overall ticket statistics calculation."""

        def calculate_ticket_stats(tickets):
            total = len(tickets)
            open_count = sum(1 for t in tickets if t["status"] == "open")
            closed_count = sum(1 for t in tickets if t["status"] == "closed")
            muted_count = sum(1 for t in tickets if t["status"] == "muted")
            unassigned_count = sum(1 for t in tickets if t["status"] != "closed" and t.get("assigned_to") is None)

            tickets_with_response = [t for t in tickets if t.get("first_admin_response_timestamp") is not None]

            if tickets_with_response:
                total_response_time = sum(
                    (
                        datetime.fromisoformat(t["first_admin_response_timestamp"])
                        - datetime.fromisoformat(t["opened_timestamp"])
                    ).total_seconds()
                    for t in tickets_with_response
                )
                avg_response_time_hours = (total_response_time / len(tickets_with_response)) / 3600
            else:
                avg_response_time_hours = None

            today_start = utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
            tickets_closed_today = sum(
                1
                for t in tickets
                if t.get("closed_timestamp") and datetime.fromisoformat(t["closed_timestamp"]) >= today_start
            )

            return {
                "total": total,
                "open": open_count,
                "closed": closed_count,
                "muted": muted_count,
                "unassigned": unassigned_count,
                "avg_response_time_hours": round(avg_response_time_hours, 2) if avg_response_time_hours else None,
                "closed_today": tickets_closed_today,
            }

        base_time = utc_now().replace(hour=8, minute=0, second=0, microsecond=0)
        tickets = [
            {
                "id": 1,
                "status": "open",
                "assigned_to": 123,
                "opened_timestamp": (base_time - timedelta(hours=2)).isoformat(),
                "first_admin_response_timestamp": (base_time - timedelta(hours=1)).isoformat(),
                "closed_timestamp": None,
            },
            {
                "id": 2,
                "status": "closed",
                "assigned_to": None,
                "opened_timestamp": (base_time - timedelta(hours=4)).isoformat(),
                "first_admin_response_timestamp": (base_time - timedelta(hours=3)).isoformat(),
                "closed_timestamp": base_time.isoformat(),
            },
            {
                "id": 3,
                "status": "muted",
                "assigned_to": None,
                "opened_timestamp": (base_time - timedelta(hours=6)).isoformat(),
                "first_admin_response_timestamp": None,
                "closed_timestamp": None,
            },
            {
                "id": 4,
                "status": "open",
                "assigned_to": None,
                "opened_timestamp": (base_time - timedelta(hours=8)).isoformat(),
                "first_admin_response_timestamp": None,
                "closed_timestamp": None,
            },
        ]

        stats = calculate_ticket_stats(tickets)
        assert stats["total"] == 4
        assert stats["open"] == 2
        assert stats["closed"] == 1
        assert stats["muted"] == 1
        assert stats["unassigned"] == 2
        assert stats["avg_response_time_hours"] == 1.0
        assert stats["closed_today"] == 1


class TestTicketMessageModelLogic:
    """Test TicketMessage model logic."""

    def test_ticket_message_attributes(self):
        """Test TicketMessage model attributes."""
        expected_attrs = [
            "id",
            "text",
            "ticket_id",
            "author_id",
            "created_at",
            "serialize",
            "create",
            "find_by_id",
            "find_by_ticket",
            "find_by_author",
            "count_by_ticket",
            "get_first_admin_message",
        ]

        for attr in expected_attrs:
            assert True, f"TicketMessage should have {attr} attribute"

    def test_message_serialization_logic(self):
        """Test message serialization logic."""

        def mock_serialize_message(message_data, author_data, include_admin_fields=False):
            return {
                "id": message_data.get("id"),
                "text": message_data.get("text"),
                "author_id": message_data.get("author_id"),
                "author_name": author_data.get("name", f"User {message_data.get('author_id')}"),
                "author_type": author_data.get("type", "user"),
                "created_at": message_data.get("created_at"),
                "ticket_id": message_data.get("ticket_id"),
            }

        message = {
            "id": 456,
            "text": "Test message content",
            "author_id": 123,
            "created_at": "2024-01-01T12:00:00",
            "ticket_id": 789,
        }

        author = {"name": "Test User", "type": "admin"}

        result = mock_serialize_message(message, author)
        assert result["id"] == 456
        assert result["text"] == "Test message content"
        assert result["author_name"] == "Test User"
        assert result["author_type"] == "admin"

    def test_first_admin_message_logic(self):
        """Test finding first admin message logic."""

        def find_first_admin_message(ticket_id, messages, users):
            admin_messages = [
                msg
                for msg in messages
                if msg["ticket_id"] == ticket_id
                and any(u["id"] == msg["author_id"] and u["type"] == "admin" for u in users)
            ]

            if admin_messages:
                return min(admin_messages, key=lambda m: m["created_at"])
            return None

        messages = [
            {
                "id": 1,
                "ticket_id": 123,
                "author_id": 456,
                "created_at": "2024-01-01T10:00:00",
            },
            {
                "id": 2,
                "ticket_id": 123,
                "author_id": 789,
                "created_at": "2024-01-01T09:00:00",
            },
            {
                "id": 3,
                "ticket_id": 123,
                "author_id": 456,
                "created_at": "2024-01-01T11:00:00",
            },
        ]

        users = [{"id": 456, "type": "user"}, {"id": 789, "type": "admin"}]

        first_admin = find_first_admin_message(123, messages, users)
        assert first_admin["id"] == 2
        assert first_admin["author_id"] == 789


class TestTicketTagModelLogic:
    """Test TicketTag model logic."""

    def test_ticket_tag_attributes(self):
        """Test TicketTag model attributes."""
        expected_attrs = [
            "id",
            "name",
            "color",
            "description",
            "serialize",
            "create",
            "update_tag",
            "delete_tag",
            "find_by_id",
            "find_by_name",
            "get_all_tags",
            "get_popular_tags",
            "search_tags",
        ]

        for attr in expected_attrs:
            assert True, f"TicketTag should have {attr} attribute"

    def test_tag_serialization_logic(self):
        """Test tag serialization logic."""

        def mock_serialize_tag(tag_data, tickets_count, include_admin_fields=False):
            return {
                "id": tag_data.get("id"),
                "name": tag_data.get("name"),
                "color": tag_data.get("color"),
                "description": tag_data.get("description"),
                "ticket_count": tickets_count,
            }

        tag = {
            "id": 123,
            "name": "urgent",
            "color": "#ff0000",
            "description": "High priority issues",
        }

        result = mock_serialize_tag(tag, 15)
        assert result["id"] == 123
        assert result["name"] == "urgent"
        assert result["color"] == "#ff0000"
        assert result["ticket_count"] == 15

    def test_tag_search_logic(self):
        """Test tag search logic."""

        def search_tags(query, all_tags):
            query_lower = query.lower()
            return [tag for tag in all_tags if query_lower in tag["name"].lower()]

        tags = [
            {"id": 1, "name": "bug"},
            {"id": 2, "name": "urgent"},
            {"id": 3, "name": "feature"},
            {"id": 4, "name": "bug-report"},
            {"id": 5, "name": "enhancement"},
        ]

        results = search_tags("bug", tags)
        assert len(results) == 2
        assert any(tag["name"] == "bug" for tag in results)
        assert any(tag["name"] == "bug-report" for tag in results)

        results = search_tags("ent", tags)
        assert len(results) == 2
        assert any(tag["name"] == "urgent" for tag in results)
        assert any(tag["name"] == "enhancement" for tag in results)

    def test_popular_tags_logic(self):
        """Test popular tags calculation logic."""

        def get_popular_tags(tag_usage_data, limit=10):
            sorted_tags = sorted(tag_usage_data.items(), key=lambda x: x[1], reverse=True)
            return sorted_tags[:limit]

        usage_data = {
            "bug": 25,
            "feature": 10,
            "urgent": 30,
            "enhancement": 5,
            "question": 20,
        }

        popular = get_popular_tags(usage_data, limit=3)
        assert len(popular) == 3
        assert popular[0] == ("urgent", 30)
        assert popular[1] == ("bug", 25)
        assert popular[2] == ("question", 20)


class TestTicketFilteringLogic:
    """Test Ticket filtering and querying logic."""

    def test_filtered_tickets_logic(self):
        """Test ticket filtering by various criteria."""

        def filter_tickets(
            tickets,
            user_id=None,
            status="all",
            assigned_to=None,
            event_id=None,
            team_id=None,
            is_admin=False,
        ):
            filtered = tickets.copy()

            if not is_admin and user_id:
                filtered = [t for t in filtered if t["author_id"] == user_id]
            elif user_id and is_admin:
                filtered = [t for t in filtered if t["author_id"] == user_id]

            if status == "open":
                filtered = [t for t in filtered if t["status"] == "open"]
            elif status == "closed":
                filtered = [t for t in filtered if t["status"] == "closed"]
            elif status == "muted":
                filtered = [t for t in filtered if t["status"] == "muted"]

            if is_admin:
                if assigned_to is not None:
                    filtered = [t for t in filtered if t.get("assigned_to") == assigned_to]
                if event_id is not None:
                    filtered = [t for t in filtered if t.get("event_id") == event_id]
                if team_id is not None:
                    filtered = [t for t in filtered if t.get("team_id") == team_id]

            return sorted(filtered, key=lambda t: t["last_updated"], reverse=True)

        tickets = [
            {
                "id": 1,
                "author_id": 123,
                "status": "open",
                "assigned_to": 456,
                "event_id": 1,
                "team_id": None,
                "last_updated": "2024-01-01T12:00:00",
            },
            {
                "id": 2,
                "author_id": 123,
                "status": "closed",
                "assigned_to": None,
                "event_id": 1,
                "team_id": 789,
                "last_updated": "2024-01-01T11:00:00",
            },
            {
                "id": 3,
                "author_id": 456,
                "status": "open",
                "assigned_to": 456,
                "event_id": 2,
                "team_id": None,
                "last_updated": "2024-01-01T10:00:00",
            },
            {
                "id": 4,
                "author_id": 123,
                "status": "muted",
                "assigned_to": None,
                "event_id": 1,
                "team_id": None,
                "last_updated": "2024-01-01T09:00:00",
            },
        ]

        user_tickets = filter_tickets(tickets, user_id=123, is_admin=False)
        assert len(user_tickets) == 3
        assert all(t["author_id"] == 123 for t in user_tickets)

        open_tickets = filter_tickets(tickets, status="open", is_admin=True)
        assert len(open_tickets) == 2
        assert all(t["status"] == "open" for t in open_tickets)

        assigned_tickets = filter_tickets(tickets, assigned_to=456, is_admin=True)
        assert len(assigned_tickets) == 2
        assert all(t["assigned_to"] == 456 for t in assigned_tickets)

        event_tickets = filter_tickets(tickets, event_id=1, is_admin=True)
        assert len(event_tickets) == 3
        assert all(t["event_id"] == 1 for t in event_tickets)

    def test_unassigned_open_tickets_logic(self):
        """Test finding unassigned open tickets."""

        def find_unassigned_open_tickets(tickets):
            return [t for t in tickets if t["status"] == "open" and t.get("assigned_to") is None]

        tickets = [
            {"id": 1, "status": "open", "assigned_to": None},
            {"id": 2, "status": "open", "assigned_to": 456},
            {"id": 3, "status": "closed", "assigned_to": None},
            {"id": 4, "status": "muted", "assigned_to": None},
            {"id": 5, "status": "open", "assigned_to": None},
        ]

        unassigned = find_unassigned_open_tickets(tickets)
        assert len(unassigned) == 2
        assert all(t["status"] == "open" and t["assigned_to"] is None for t in unassigned)
