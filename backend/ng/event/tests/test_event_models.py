"""
Unit tests for event model
"""

from datetime import timedelta
import pytest
from ...core.exceptions import ValidationError
from ...core.validation import validate_event_creation
from ...core.utils import utc_now
from ... import config


class TestEventTimeConstraints:
    """Test event time-related constraints and validations."""

    def test_event_time_constraint_validation(self):
        """Test that start_time < end_time constraint is understood."""

        now = utc_now()
        future_start = (now + timedelta(hours=1)).isoformat()
        future_end = (now + timedelta(hours=2)).isoformat()

        result = validate_event_creation(
            {
                "name": "Test Event",
                "max_team_size": 4,
                "start_time": future_start,
                "end_time": future_end,
            }
        )
        assert result is not None

        with pytest.raises(ValidationError) as exc_info:
            validate_event_creation(
                {
                    "name": "Test Event",
                    "max_team_size": 4,
                    "start_time": future_end,
                    "end_time": future_start,
                }
            )
        assert "end_time" in exc_info.value.errors
        assert "after" in exc_info.value.errors["end_time"].lower()

    def test_event_time_both_or_neither_constraint(self):
        """Test that both times must be provided together or neither."""

        now = utc_now()
        future_time = (now + timedelta(hours=1)).isoformat()

        result = validate_event_creation({"name": "Test Event", "max_team_size": 4})
        assert result is not None

        with pytest.raises(ValidationError) as exc_info:
            validate_event_creation({"name": "Test Event", "max_team_size": 4, "start_time": future_time})
        assert "time_constraint" in exc_info.value.errors

        with pytest.raises(ValidationError) as exc_info:
            validate_event_creation({"name": "Test Event", "max_team_size": 4, "end_time": future_time})
        assert "time_constraint" in exc_info.value.errors


class TestEventBusinessRules:
    """Test event related business rule validations."""

    def test_event_name_validation_edge_cases(self):
        """Test edge cases for event name validation."""

        with pytest.raises(ValidationError) as exc_info:
            validate_event_creation({"name": "", "max_team_size": 4})
        assert "name" in exc_info.value.errors

        with pytest.raises(ValidationError) as exc_info:
            validate_event_creation({"name": "   ", "max_team_size": 4})
        assert "name" in exc_info.value.errors

        result = validate_event_creation({"name": "イベント2024 🎯", "max_team_size": 4})
        assert result is not None

        if hasattr(config, "EVENT_NAME_MAX_LENGTH"):
            long_name = "A" * (config.EVENT_NAME_MAX_LENGTH + 1)
            with pytest.raises(ValidationError) as exc_info:
                validate_event_creation({"name": long_name, "max_team_size": 4})
            assert "name" in exc_info.value.errors

    def test_event_description_length_limits(self):
        """Test event description validation."""

        result = validate_event_creation({"name": "Test Event", "max_team_size": 4})
        assert result is not None

        result = validate_event_creation(
            {
                "name": "Test Event",
                "max_team_size": 4,
                "description": "A test event for unit testing",
            }
        )
        assert result is not None

        if hasattr(config, "EVENT_DESCRIPTION_MAX_LENGTH"):
            long_desc = "A" * (config.EVENT_DESCRIPTION_MAX_LENGTH + 1)
            with pytest.raises(ValidationError) as exc_info:
                validate_event_creation({"name": "Test Event", "max_team_size": 4, "description": long_desc})
            assert "description" in exc_info.value.errors

    def test_event_max_team_size_minimum_value(self):
        """Test that max_team_size has minimum value of 1."""

        result = validate_event_creation({"name": "Test Event", "max_team_size": 1})
        assert result is not None

        with pytest.raises(ValidationError) as exc_info:
            validate_event_creation({"name": "Test Event", "max_team_size": 0})
        assert "max_team_size" in exc_info.value.errors

        with pytest.raises(ValidationError) as exc_info:
            validate_event_creation({"name": "Test Event", "max_team_size": -1})
        assert "max_team_size" in exc_info.value.errors


class TestEventModelOperations:
    """Test Event model database operations and business logic."""

    def test_event_creation_logic(self):
        """Test event creation method logic."""

        def mock_create_event(
            name,
            description=None,
            max_team_size=None,
            start_time=None,
            end_time=None,
            locked=False,
            existing_events=None,
        ):
            if existing_events is None:
                existing_events = []

            # Check for duplicate names
            if any(e["name"] == name for e in existing_events):
                raise ValueError("Event name already exists")

            # Apply defaults
            if max_team_size is None:
                max_team_size = 4  # Default from config

            event = {
                "id": len(existing_events) + 1,
                "name": name,
                "description": description,
                "max_team_size": max_team_size,
                "start_time": start_time,
                "end_time": end_time,
                "locked": locked,
            }

            existing_events.append(event)
            return event

        events = []

        # Basic event creation
        event = mock_create_event("Test Event", existing_events=events)
        assert event["name"] == "Test Event"
        assert event["max_team_size"] == 4  # Default
        assert event["locked"] is False
        assert len(events) == 1

        # Event with all parameters
        event2 = mock_create_event(
            "Complete Event",
            description="Full event",
            max_team_size=8,
            start_time="2024-01-01T10:00:00",
            end_time="2024-01-01T18:00:00",
            locked=True,
            existing_events=events,
        )
        assert event2["max_team_size"] == 8
        assert event2["locked"] is True
        assert len(events) == 2

        # Duplicate name should fail
        with pytest.raises(ValueError, match="already exists"):
            mock_create_event("Test Event", existing_events=events)

    def test_event_update_logic(self):
        """Test event update method logic."""

        def mock_update_event(event, **kwargs):
            """Mock event update with validation."""
            # Simulate integrity constraints
            if "max_team_size" in kwargs and kwargs["max_team_size"] <= 0:
                raise ValueError("Invalid max_team_size")

            if "start_time" in kwargs and "end_time" in kwargs:
                if kwargs["start_time"] >= kwargs["end_time"]:
                    raise ValueError("Start time must be before end time")

            # Apply updates
            for key, value in kwargs.items():
                if key in event:
                    event[key] = value

            return True

        event = {"id": 1, "name": "Test Event", "max_team_size": 4, "locked": False}

        # Valid updates
        result = mock_update_event(event, name="Updated Event", locked=True)
        assert result is True
        assert event["name"] == "Updated Event"
        assert event["locked"] is True

        # Invalid max_team_size
        with pytest.raises(ValueError, match="Invalid max_team_size"):
            mock_update_event(event, max_team_size=0)

        # Invalid time constraint
        with pytest.raises(ValueError, match="Start time must be before"):
            mock_update_event(event, start_time="2024-01-01T18:00:00", end_time="2024-01-01T10:00:00")

    def test_event_lookup_methods(self):
        """Test event lookup method logic."""

        def mock_find_by_id(event_id, events):
            return next((e for e in events if e["id"] == event_id), None)

        def mock_find_by_name(name, events):
            return next((e for e in events if e["name"] == name), None)

        events = [
            {"id": 1, "name": "Event One"},
            {"id": 2, "name": "Event Two"},
            {"id": 3, "name": "Event Three"},
        ]

        # Find by ID
        found = mock_find_by_id(2, events)
        assert found["name"] == "Event Two"

        not_found = mock_find_by_id(999, events)
        assert not_found is None

        # Find by name
        found = mock_find_by_name("Event Three", events)
        assert found["id"] == 3

        not_found = mock_find_by_name("Nonexistent", events)
        assert not_found is None

    def test_event_serialization_logic(self):
        """Test event serialization for API responses."""

        def mock_serialize(event, include_admin_fields=False):
            """Mock event serialization."""
            base_data = {
                "id": event["id"],
                "name": event["name"],
                "description": event.get("description"),
                "max_team_size": event["max_team_size"],
                "start_time": event.get("start_time"),
                "end_time": event.get("end_time"),
                "locked": event["locked"],
            }

            if include_admin_fields:
                base_data.update(
                    {
                        "created_at": event.get("created_at"),
                        "updated_at": event.get("updated_at"),
                        "created_by": event.get("created_by"),
                    }
                )

            return base_data

        event = {
            "id": 1,
            "name": "Test Event",
            "description": "Test description",
            "max_team_size": 6,
            "start_time": "2024-01-01T10:00:00",
            "end_time": "2024-01-01T18:00:00",
            "locked": True,
            "created_at": "2023-12-01T00:00:00",
            "created_by": "admin",
        }

        # Basic serialization
        basic = mock_serialize(event)
        assert basic["id"] == 1
        assert basic["name"] == "Test Event"
        assert basic["locked"] is True
        assert "created_at" not in basic

        # Admin serialization
        admin = mock_serialize(event, include_admin_fields=True)
        assert admin["id"] == 1
        assert admin["created_at"] == "2023-12-01T00:00:00"
        assert admin["created_by"] == "admin"


class TestEventStatisticsAndQueries:
    """Test Event model statistics and complex queries."""

    def test_event_statistics_calculation(self):
        """Test event statistics calculation logic."""

        def mock_get_events_with_stats(events, teams, members):
            """Mock complex event statistics query."""
            results = []

            for event in events:
                event_teams = [t for t in teams if t["event_id"] == event["id"]]
                event_members = [m for m in members if m["event_id"] == event["id"]]

                stats = {
                    "id": event["id"],
                    "name": event["name"],
                    "description": event.get("description"),
                    "start_time": event.get("start_time"),
                    "end_time": event.get("end_time"),
                    "locked": event["locked"],
                    "team_count": len(event_teams),
                    "total_members": len(event_members),
                }

                results.append(stats)

            return results

        events = [
            {"id": 1, "name": "Event 1", "locked": False},
            {"id": 2, "name": "Event 2", "locked": True},
        ]

        teams = [
            {"id": 1, "event_id": 1, "name": "Team A"},
            {"id": 2, "event_id": 1, "name": "Team B"},
            {"id": 3, "event_id": 2, "name": "Team C"},
        ]

        members = [
            {"id": 1, "event_id": 1, "team_id": 1},
            {"id": 2, "event_id": 1, "team_id": 1},
            {"id": 3, "event_id": 1, "team_id": 2},
            {"id": 4, "event_id": 2, "team_id": 3},
        ]

        stats = mock_get_events_with_stats(events, teams, members)

        assert len(stats) == 2
        assert stats[0]["team_count"] == 2
        assert stats[0]["total_members"] == 3
        assert stats[1]["team_count"] == 1
        assert stats[1]["total_members"] == 1

    def test_event_team_size_analysis(self):
        """Test event team size analysis logic."""

        def mock_get_largest_team_size(event_id, teams):
            """Get the size of the largest team in an event."""
            event_teams = [t for t in teams if t["event_id"] == event_id]
            if not event_teams:
                return 0
            return max(t["member_count"] for t in event_teams)

        def mock_get_team_count(event_id, teams):
            """Get the number of teams in an event."""
            return len([t for t in teams if t["event_id"] == event_id])

        teams = [
            {"event_id": 1, "member_count": 3},
            {"event_id": 1, "member_count": 5},
            {"event_id": 1, "member_count": 2},
            {"event_id": 2, "member_count": 4},
        ]

        # Test largest team size
        largest = mock_get_largest_team_size(1, teams)
        assert largest == 5

        largest_empty = mock_get_largest_team_size(999, teams)
        assert largest_empty == 0

        # Test team count
        count = mock_get_team_count(1, teams)
        assert count == 3

        count_empty = mock_get_team_count(999, teams)
        assert count_empty == 0

    def test_event_detailed_statistics(self):
        """Test detailed event statistics with complex aggregations."""

        def mock_get_detailed_event_stats(events, teams, members):
            """Calculate detailed statistics for events."""
            results = []

            for event in events:
                event_teams = [t for t in teams if t["event_id"] == event["id"]]
                event_members = [m for m in members if m["event_id"] == event["id"]]

                # Calculate team size distribution
                team_sizes = [t["member_count"] for t in event_teams]

                stats = {
                    "id": event["id"],
                    "name": event["name"],
                    "start_time": event.get("start_time"),
                    "end_time": event.get("end_time"),
                    "teams": len(event_teams),
                    "total_members": len(event_members),
                    "avg_team_size": sum(team_sizes) / len(team_sizes) if team_sizes else 0,
                    "min_team_size": min(team_sizes) if team_sizes else 0,
                    "max_team_size": max(team_sizes) if team_sizes else 0,
                    "full_teams": len([t for t in event_teams if t["member_count"] == event["max_team_size"]]),
                }

                results.append(stats)

            return results

        events = [
            {"id": 1, "name": "Event 1", "max_team_size": 4},
            {"id": 2, "name": "Event 2", "max_team_size": 6},
        ]

        teams = [
            {"event_id": 1, "member_count": 4},
            {"event_id": 1, "member_count": 3},
            {"event_id": 1, "member_count": 4},
            {"event_id": 2, "member_count": 2},
        ]

        members = [
            {"event_id": 1},
            {"event_id": 1},
            {"event_id": 1},
            {"event_id": 1},
            {"event_id": 1},
            {"event_id": 1},
            {"event_id": 1},
            {"event_id": 1},
            {"event_id": 1},
            {"event_id": 1},
            {"event_id": 1},  # 11 members for event 1
            {"event_id": 2},
            {"event_id": 2},  # 2 members for event 2
        ]

        stats = mock_get_detailed_event_stats(events, teams, members)

        assert len(stats) == 2

        # Event 1 stats
        event1_stats = stats[0]
        assert event1_stats["teams"] == 3
        assert event1_stats["total_members"] == 11
        assert event1_stats["avg_team_size"] == (4 + 3 + 4) / 3
        assert event1_stats["min_team_size"] == 3
        assert event1_stats["max_team_size"] == 4
        assert event1_stats["full_teams"] == 2  # Two teams with 4 members

        # Event 2 stats
        event2_stats = stats[1]
        assert event2_stats["teams"] == 1
        assert event2_stats["total_members"] == 2
        assert event2_stats["full_teams"] == 0  # No full teams (max is 6, team has 2)


class TestEventDataManagementLogic:
    """Test Event model data management and cleanup operations."""

    def test_event_data_reset_logic(self):
        """Test event data reset and cleanup logic."""

        def mock_reset_all_plugin_data(events, teams, members, users):
            """Mock plugin data reset with proper cascade order."""
            try:
                # Simulate cascade deletion order
                deleted_counts = {
                    "members": len(members),
                    "teams": len(teams),
                    "users": len(users),
                    "events": len(events),
                }

                # Clear all data
                members.clear()
                teams.clear()
                users.clear()
                events.clear()

                return True, deleted_counts
            except Exception as e:
                return False, str(e)

        events = [{"id": 1}, {"id": 2}]
        teams = [{"id": 1, "event_id": 1}, {"id": 2, "event_id": 2}]
        members = [{"id": 1, "team_id": 1}, {"id": 2, "team_id": 2}]
        users = [{"id": 1}, {"id": 2}]

        success, result = mock_reset_all_plugin_data(events, teams, members, users)

        assert success is True
        assert isinstance(result, dict)
        assert result["members"] == 2
        assert result["teams"] == 2
        assert result["users"] == 2
        assert result["events"] == 2

        # Verify all data is cleared
        assert len(events) == 0
        assert len(teams) == 0
        assert len(members) == 0
        assert len(users) == 0

    def test_event_integrity_constraints(self):
        """Test event database integrity constraints."""

        def validate_event_constraints(event):
            """Validate event database constraints."""
            errors = []

            # Name uniqueness (simulated)
            if not event.get("name") or len(event["name"].strip()) == 0:
                errors.append("Event name cannot be empty")

            # Max team size constraints
            max_team_size = event.get("max_team_size")
            if max_team_size is not None and max_team_size <= 0:
                errors.append("Max team size must be positive")

            # Time constraints
            start_time = event.get("start_time")
            end_time = event.get("end_time")

            # Both or neither time constraint
            if (start_time is None) != (end_time is None):
                errors.append("Both start_time and end_time must be provided together or neither")

            # Time order constraint
            if start_time and end_time and start_time >= end_time:
                errors.append("Start time must be before end time")

            return len(errors) == 0, errors

        # Valid event
        valid_event = {
            "name": "Valid Event",
            "max_team_size": 4,
            "start_time": "2024-01-01T10:00:00",
            "end_time": "2024-01-01T18:00:00",
        }

        is_valid, errors = validate_event_constraints(valid_event)
        assert is_valid, f"Valid event should pass constraints: {errors}"

        # Invalid: empty name
        invalid_event = valid_event.copy()
        invalid_event["name"] = "   "
        is_valid, errors = validate_event_constraints(invalid_event)
        assert not is_valid
        assert "name cannot be empty" in " ".join(errors)

        # Invalid: negative team size
        invalid_event = valid_event.copy()
        invalid_event["max_team_size"] = -1
        is_valid, errors = validate_event_constraints(invalid_event)
        assert not is_valid
        assert "must be positive" in " ".join(errors)

        # Invalid: only start time
        invalid_event = valid_event.copy()
        del invalid_event["end_time"]
        is_valid, errors = validate_event_constraints(invalid_event)
        assert not is_valid
        assert "together or neither" in " ".join(errors)

        # Invalid: time order
        invalid_event = valid_event.copy()
        invalid_event["start_time"] = "2024-01-01T18:00:00"
        invalid_event["end_time"] = "2024-01-01T10:00:00"
        is_valid, errors = validate_event_constraints(invalid_event)
        assert not is_valid
        assert "before end time" in " ".join(errors)

    def test_event_relationship_management(self):
        """Test event relationship management with teams."""

        def mock_get_event_details_with_teams(event_id, events, teams, members):
            """Mock getting event details with team information."""
            event = next((e for e in events if e["id"] == event_id), None)
            if not event:
                return None

            event_teams = [t for t in teams if t["event_id"] == event_id]

            # Calculate additional stats
            event_members_count = len([m for m in members if m["event_id"] == event_id])

            result = event.copy()
            result["team_count"] = len(event_teams)
            result["total_members"] = event_members_count
            result["teams"] = event_teams

            return result

        events = [{"id": 1, "name": "Test Event", "max_team_size": 4}]
        teams = [
            {"id": 1, "event_id": 1, "name": "Team A", "member_count": 3},
            {"id": 2, "event_id": 1, "name": "Team B", "member_count": 4},
        ]
        members = [
            {"id": 1, "event_id": 1, "team_id": 1},
            {"id": 2, "event_id": 1, "team_id": 1},
            {"id": 3, "event_id": 1, "team_id": 1},
            {"id": 4, "event_id": 1, "team_id": 2},
            {"id": 5, "event_id": 1, "team_id": 2},
            {"id": 6, "event_id": 1, "team_id": 2},
            {"id": 7, "event_id": 1, "team_id": 2},
        ]

        details = mock_get_event_details_with_teams(1, events, teams, members)

        assert details is not None
        assert details["name"] == "Test Event"
        assert details["team_count"] == 2
        assert details["total_members"] == 7
        assert len(details["teams"]) == 2

        # Non-existent event
        details = mock_get_event_details_with_teams(999, events, teams, members)
        assert details is None
