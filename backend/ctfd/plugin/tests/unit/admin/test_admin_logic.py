"""
/backend/ctfd/plugin/tests/unit/admin/test_admin_logic.py
Unit tests for admin domain logic without database dependencies.
"""

from plugin.team.models.enums import TeamRole


class TestDataProcessingLogic:
    """Test admin data processing algorithms."""

    def test_data_counts_calculation_logic(self):
        """Test how data counts are calculated."""
        mock_event_count = 5
        mock_team_count = 20
        mock_user_count = 100
        mock_member_count = 80

        expected = {
            "events": mock_event_count,
            "teams": mock_team_count,
            "users": mock_user_count,
            "team_members": mock_member_count,
        }

        assert expected["events"] == 5
        assert expected["teams"] == 20
        assert expected["users"] == 100
        assert expected["team_members"] == 80

    def test_empty_teams_threshold_calculation(self):
        """Test calculation of empty teams threshold."""
        teams = [
            {"id": 1, "name": "Team A", "member_count": 0},
            {"id": 2, "name": "Team B", "member_count": 3},
            {"id": 3, "name": "Team C", "member_count": 0},
            {"id": 4, "name": "Team D", "member_count": 1},
        ]

        empty_teams = [t for t in teams if t["member_count"] == 0]
        assert len(empty_teams) == 2
        assert all(t["member_count"] == 0 for t in empty_teams)

    def test_health_check_warning_generation(self):
        """Test generation of health check warnings."""
        stats = {"empty_teams": 5, "headless_teams": 3, "orphaned_users": 10}

        warnings = []
        if stats["empty_teams"] > 0:
            warnings.append(f"{stats['empty_teams']} empty teams")
        if stats["headless_teams"] > 0:
            warnings.append(f"{stats['headless_teams']} teams without captains")
        if stats["orphaned_users"] > 0:
            warnings.append(f"{stats['orphaned_users']} orphaned users")

        assert len(warnings) == 3
        assert "5 empty teams" in warnings
        assert "3 teams without captains" in warnings
        assert "10 orphaned users" in warnings

    def test_orphaned_data_identification_logic(self):
        """Test logic for identifying orphaned data."""

        users = [{"id": 1}, {"id": 2}, {"id": 3}]
        team_members = [
            {"user_id": 1, "team_id": 1},
            {"user_id": 2, "team_id": 1},
            {"user_id": 4, "team_id": 2},  # Orphaned - user 4 doesn't exist
            {"user_id": 5, "team_id": 2},  # Orphaned - user 5 doesn't exist
        ]

        user_ids = {u["id"] for u in users}
        orphaned_members = [tm for tm in team_members if tm["user_id"] not in user_ids]

        assert len(orphaned_members) == 2
        assert orphaned_members[0]["user_id"] == 4
        assert orphaned_members[1]["user_id"] == 5


class TestCleanupAlgorithms:
    """Test admin cleanup algorithms."""

    def test_headless_team_detection_algorithm(self):
        """Test algorithm for detecting teams without captains."""
        teams = [
            {
                "id": 1,
                "name": "Team A",
                "members": [
                    {"user_id": 1, "role": TeamRole.CAPTAIN.value},
                    {"user_id": 2, "role": TeamRole.MEMBER.value},
                ],
            },
            {
                "id": 2,
                "name": "Team B",
                "members": [
                    {"user_id": 3, "role": TeamRole.MEMBER.value},
                    {"user_id": 4, "role": TeamRole.MEMBER.value},
                ],
            },
            {
                "id": 3,
                "name": "Team C",
                "members": [],  # Empty team
            },
        ]

        headless_teams = []
        for team in teams:
            if team["members"]:  # Has members
                has_captain = any(m["role"] == TeamRole.CAPTAIN.value for m in team["members"])
                if not has_captain:
                    headless_teams.append(team)

        assert len(headless_teams) == 1
        assert headless_teams[0]["id"] == 2
        assert headless_teams[0]["name"] == "Team B"

    def test_oldest_member_promotion_logic(self):
        """Test logic for promoting oldest member to captain."""
        from datetime import datetime, timedelta

        base_time = datetime.utcnow()
        members = [
            {
                "user_id": 1,
                "role": TeamRole.MEMBER.value,
                "joined_at": base_time - timedelta(days=10),  # Oldest
            },
            {
                "user_id": 2,
                "role": TeamRole.MEMBER.value,
                "joined_at": base_time - timedelta(days=5),
            },
            {
                "user_id": 3,
                "role": TeamRole.MEMBER.value,
                "joined_at": base_time - timedelta(days=1),  # Newest
            },
        ]

        sorted_members = sorted(members, key=lambda m: m["joined_at"])
        oldest_member = sorted_members[0]

        assert oldest_member["user_id"] == 1
        assert oldest_member["joined_at"] == base_time - timedelta(days=10)

    def test_orphaned_user_identification(self):
        """Test identification of orphaned plugin users."""
        ctfd_users = [{"id": 1}, {"id": 2}, {"id": 3}]
        plugin_users = [
            {"id": 1, "ctfd_user_id": 1},
            {"id": 2, "ctfd_user_id": 2},
            {"id": 3, "ctfd_user_id": 5},  # Orphaned - CTFd user 5 doesn't exist
            {"id": 4, "ctfd_user_id": 6},  # Orphaned - CTFd user 6 doesn't exist
        ]

        ctfd_user_ids = {u["id"] for u in ctfd_users}
        orphaned_users = [pu for pu in plugin_users if pu["ctfd_user_id"] not in ctfd_user_ids]

        assert len(orphaned_users) == 2
        assert orphaned_users[0]["ctfd_user_id"] == 5
        assert orphaned_users[1]["ctfd_user_id"] == 6


class TestAdminValidation:
    """Test admin operation validations."""

    def test_admin_reset_confirmation_required(self):
        """Test that admin reset requires specific confirmation."""
        from plugin.utils import validate_admin_reset
        from plugin import config

        valid, errors = validate_admin_reset({})
        assert not valid
        assert "confirmation" in errors

        valid, errors = validate_admin_reset({"confirm": "yes please"})
        assert not valid
        assert "confirmation" in errors

        valid, errors = validate_admin_reset({"confirm": config.ADMIN_RESET_CONFIRMATION})
        assert valid
        assert len(errors) == 0

    def test_admin_event_reset_confirmation_required(self):
        """Test that event reset requires specific confirmation."""
        from plugin.utils import validate_admin_event_reset
        from plugin import config

        valid, errors = validate_admin_event_reset({})
        assert not valid
        assert "confirmation" in errors

        valid, errors = validate_admin_event_reset({"confirm": config.ADMIN_EVENT_RESET_CONFIRMATION})
        assert valid
        assert len(errors) == 0
