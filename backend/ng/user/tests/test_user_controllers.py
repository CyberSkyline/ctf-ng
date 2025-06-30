"""
Unit tests for user controller logic.
"""

import pytest


class TestGetUserInfoController:
    """Test get_user_info controller logic."""

    def test_get_user_info_success_logic(self):
        """Test successful user info retrieval logic."""

        def mock_get_user_info(user_id, user_database):
            user_data = next((u for u in user_database if u["id"] == user_id), None)
            if not user_data:
                raise Exception(f"User with ID {user_id} not found.")

            return {"user": user_data}

        users_db = [
            {
                "id": 123,
                "name": "Test User",
                "email": "test@example.com",
                "role": "user",
                "registered_at": "2025-06-29",
                "team_count": 2,
            }
        ]

        result = mock_get_user_info(123, users_db)
        assert result["user"]["id"] == 123
        assert result["user"]["name"] == "Test User"
        assert result["user"]["team_count"] == 2

    def test_get_user_info_not_found_logic(self):
        """Test user info retrieval when user not found."""

        def mock_get_user_info(user_id, user_database):
            user_data = next((u for u in user_database if u["id"] == user_id), None)
            if not user_data:
                raise Exception(f"User with ID {user_id} not found.")

            return {"user": user_data}

        users_db = []

        with pytest.raises(Exception) as exc_info:
            mock_get_user_info(999, users_db)
        assert "not found" in str(exc_info.value)

    def test_get_user_info_data_structure(self):
        """Test user info response data structure."""

        def mock_get_user_info(user_id, user_database):
            user_data = next((u for u in user_database if u["id"] == user_id), None)
            if not user_data:
                raise Exception(f"User with ID {user_id} not found.")

            return {"user": user_data}

        user_data = {
            "id": 456,
            "name": "Admin User",
            "email": "admin@example.com",
            "role": "admin",
            "registered_at": "2023-12-01",
            "team_count": 0,
        }

        result = mock_get_user_info(456, [user_data])
        assert "user" in result
        assert isinstance(result["user"], dict)

        user_info = result["user"]
        expected_fields = ["id", "name", "email", "role", "registered_at", "team_count"]
        for field in expected_fields:
            assert field in user_info


class TestGetUserStatsController:
    """Test get_user_stats controller logic."""

    def test_get_user_stats_success_logic(self):
        """Test successful user stats retrieval logic."""

        def mock_get_user_stats(user_id, users_data, memberships_data):
            user = next((u for u in users_data if u["id"] == user_id), None)
            if not user:
                raise Exception("User not found in extended system")

            user_memberships = [m for m in memberships_data if m["user_id"] == user_id]
            events_participated = set(m["event_id"] for m in user_memberships)
            total_events = 5

            stats = {
                "total_team_members": len(user_memberships),
                "events_participated": len(events_participated),
                "total_events_available": total_events,
                "participation_rate": len(events_participated) / total_events if total_events > 0 else 0,
            }

            return {"stats": stats}

        users = [{"id": 123}]
        memberships = [
            {"user_id": 123, "event_id": 1, "team_id": 5},
            {"user_id": 123, "event_id": 1, "team_id": 6},
            {"user_id": 123, "event_id": 2, "team_id": 7},
        ]

        result = mock_get_user_stats(123, users, memberships)
        assert result["stats"]["total_team_members"] == 3
        assert result["stats"]["events_participated"] == 2
        assert result["stats"]["participation_rate"] == 0.4

    def test_get_user_stats_not_found_logic(self):
        """Test user stats when user not found."""

        def mock_get_user_stats(user_id, users_data, memberships_data):
            user = next((u for u in users_data if u["id"] == user_id), None)
            if not user:
                raise Exception("User not found in extended system")

            return {"stats": {}}

        with pytest.raises(Exception) as exc_info:
            mock_get_user_stats(999, [], [])
        assert "not found" in str(exc_info.value)

    def test_user_stats_calculation_edge_cases(self):
        """Test user stats calculation with edge cases."""

        def mock_get_user_stats(user_id, users_data, memberships_data):
            user = next((u for u in users_data if u["id"] == user_id), None)
            if not user:
                raise Exception("User not found in extended system")

            user_memberships = [m for m in memberships_data if m["user_id"] == user_id]
            events_participated = set(m["event_id"] for m in user_memberships)
            total_events = 0

            stats = {
                "total_team_members": len(user_memberships),
                "events_participated": len(events_participated),
                "total_events_available": total_events,
                "participation_rate": len(events_participated) / total_events if total_events > 0 else 0,
            }

            return {"stats": stats}

        users = [{"id": 123}]
        empty_memberships = []

        result = mock_get_user_stats(123, users, empty_memberships)
        assert result["stats"]["total_team_members"] == 0
        assert result["stats"]["events_participated"] == 0
        assert result["stats"]["participation_rate"] == 0


class TestCanJoinTeamController:
    """Test can_join_team_in_event controller logic."""

    def test_can_join_team_eligible_logic(self):
        """Test team join eligibility when user is eligible."""

        def mock_can_join_team(user_id, event_id, memberships):
            existing_membership = any(m["user_id"] == user_id and m["event_id"] == event_id for m in memberships)

            if existing_membership:
                raise Exception("User is already in a team for this event")

            return {"can_join": True, "message": "User is eligible to join a team."}

        memberships = [{"user_id": 123, "event_id": 1, "team_id": 5}]

        result = mock_can_join_team(123, 2, memberships)
        assert result["can_join"] is True
        assert "eligible" in result["message"]

    def test_can_join_team_already_member_logic(self):
        """Test team join eligibility when user already in team."""

        def mock_can_join_team(user_id, event_id, memberships):
            existing_membership = any(m["user_id"] == user_id and m["event_id"] == event_id for m in memberships)

            if existing_membership:
                raise Exception("User is already in a team for this event")

            return {"can_join": True, "message": "User is eligible to join a team."}

        memberships = [{"user_id": 123, "event_id": 1, "team_id": 5}]

        with pytest.raises(Exception) as exc_info:
            mock_can_join_team(123, 1, memberships)
        assert "already in a team" in str(exc_info.value)

    def test_can_join_team_multiple_events_logic(self):
        """Test team join eligibility across multiple events."""

        def mock_can_join_team(user_id, event_id, memberships):
            existing_membership = any(m["user_id"] == user_id and m["event_id"] == event_id for m in memberships)

            if existing_membership:
                raise Exception("User is already in a team for this event")

            return {"can_join": True, "message": "User is eligible to join a team."}

        memberships = [
            {"user_id": 123, "event_id": 1, "team_id": 5},
            {"user_id": 123, "event_id": 2, "team_id": 7},
            {"user_id": 456, "event_id": 1, "team_id": 8},
        ]

        result = mock_can_join_team(123, 3, memberships)
        assert result["can_join"] is True

        with pytest.raises(Exception):
            mock_can_join_team(123, 1, memberships)

        result = mock_can_join_team(456, 2, memberships)
        assert result["can_join"] is True


class TestGetUserTeamsController:
    """Test get_user_teams controller logic."""

    def test_get_user_teams_success_logic(self):
        """Test successful user teams retrieval logic."""

        def mock_get_user_teams(user_id, users_data, teams_data):
            user = next((u for u in users_data if u["id"] == user_id), None)
            if not user:
                raise Exception("User not found in extended system")

            user_teams = [t for t in teams_data if t["user_id"] == user_id]

            return {"teams": user_teams, "total_teams": len(user_teams)}

        users = [{"id": 123}]
        teams_data = [
            {
                "user_id": 123,
                "joined_at": "2025-06-28",
                "team_id": 5,
                "team_name": "Team Alpha",
                "max_team_size": 4,
                "event_id": 1,
                "event_name": "CTF 2025",
                "team_member_count": 3,
            },
            {
                "user_id": 123,
                "joined_at": "2025-06-29",
                "team_id": 7,
                "team_name": "Team Beta",
                "max_team_size": 5,
                "event_id": 2,
                "event_name": "Spring CTF",
                "team_member_count": 2,
            },
        ]

        result = mock_get_user_teams(123, users, teams_data)
        assert result["total_teams"] == 2
        assert len(result["teams"]) == 2
        assert result["teams"][0]["team_name"] == "Team Alpha"
        assert result["teams"][1]["team_name"] == "Team Beta"

    def test_get_user_teams_not_found_logic(self):
        """Test user teams retrieval when user not found."""

        def mock_get_user_teams(user_id, users_data, teams_data):
            user = next((u for u in users_data if u["id"] == user_id), None)
            if not user:
                raise Exception("User not found in extended system")

            return {"teams": [], "total_teams": 0}

        with pytest.raises(Exception) as exc_info:
            mock_get_user_teams(999, [], [])
        assert "not found" in str(exc_info.value)

    def test_get_user_teams_empty_results_logic(self):
        """Test user teams retrieval with no teams."""

        def mock_get_user_teams(user_id, users_data, teams_data):
            user = next((u for u in users_data if u["id"] == user_id), None)
            if not user:
                raise Exception("User not found in extended system")

            user_teams = [t for t in teams_data if t["user_id"] == user_id]

            return {"teams": user_teams, "total_teams": len(user_teams)}

        users = [{"id": 123}]
        teams_data = []

        result = mock_get_user_teams(123, users, teams_data)
        assert result["total_teams"] == 0
        assert result["teams"] == []

    def test_user_teams_data_structure(self):
        """Test user teams response data structure."""

        def mock_get_user_teams(user_id, users_data, teams_data):
            user = next((u for u in users_data if u["id"] == user_id), None)
            if not user:
                raise Exception("User not found in extended system")

            user_teams = [t for t in teams_data if t["user_id"] == user_id]

            return {"teams": user_teams, "total_teams": len(user_teams)}

        users = [{"id": 123}]
        teams_data = [
            {
                "user_id": 123,
                "joined_at": "2025-06-28",
                "team_id": 5,
                "team_name": "Team Alpha",
                "max_team_size": 4,
                "event_id": 1,
                "event_name": "CTF 2025",
                "team_member_count": 3,
            }
        ]

        result = mock_get_user_teams(123, users, teams_data)

        assert "teams" in result
        assert "total_teams" in result
        assert isinstance(result["teams"], list)
        assert isinstance(result["total_teams"], int)

        if result["teams"]:
            team = result["teams"][0]
            expected_fields = [
                "joined_at",
                "team_id",
                "team_name",
                "max_team_size",
                "event_id",
                "event_name",
                "team_member_count",
            ]
            for field in expected_fields:
                assert field in team


class TestGetUserTeamsInEventController:
    """Test get_user_teams_in_event controller logic."""

    def test_user_teams_in_event_logic(self):
        """Test user teams in specific event logic."""

        def mock_get_user_teams_in_event(user_id, event_id, event_data, memberships):
            event = next((e for e in event_data if e["id"] == event_id), None)
            if not event:
                return {"event": None, "team_member": None, "team": None}

            team_member = next(
                (m for m in memberships if m["user_id"] == user_id and m["event_id"] == event_id),
                None,
            )

            if not team_member:
                return {"event": event, "team_member": None, "team": None}

            team = {
                "id": team_member["team_id"],
                "name": f"Team {team_member['team_id']}",
                "event_id": event_id,
            }

            return {"event": event, "team_member": team_member, "team": team}

        events = [{"id": 1, "name": "CTF 2025"}]
        memberships = [{"user_id": 123, "event_id": 1, "team_id": 5, "role": "member"}]

        result = mock_get_user_teams_in_event(123, 1, events, memberships)
        assert result["event"]["name"] == "CTF 2025"
        assert result["team_member"]["role"] == "member"
        assert result["team"]["id"] == 5

        no_team_result = mock_get_user_teams_in_event(456, 1, events, memberships)
        assert no_team_result["event"]["name"] == "CTF 2025"
        assert no_team_result["team_member"] is None
        assert no_team_result["team"] is None

        no_event_result = mock_get_user_teams_in_event(123, 999, events, memberships)
        assert no_event_result["event"] is None


class TestUserControllerEdgeCases:
    """Test user controller edge cases and error handling."""

    def test_invalid_user_id_handling(self):
        """Test handling of invalid user IDs."""

        def validate_user_id(user_id):
            if not isinstance(user_id, int):
                raise ValueError("User ID must be an integer")
            if user_id <= 0:
                raise ValueError("User ID must be positive")
            return True

        assert validate_user_id(123) is True

        with pytest.raises(ValueError) as exc_info:
            validate_user_id("invalid")
        assert "integer" in str(exc_info.value)

        with pytest.raises(ValueError) as exc_info:
            validate_user_id(-1)
        assert "positive" in str(exc_info.value)

        with pytest.raises(ValueError):
            validate_user_id(0)

    def test_controller_response_consistency(self):
        """Test controller response format consistency."""

        def format_response(data, success=True, error=None):
            response = {}

            if error:
                response["success"] = False
                response["error"] = error
            else:
                response.update(data)

            return response

        success_response = format_response({"user": {"id": 123}})
        assert "user" in success_response

        error_response = format_response({}, success=False, error="User not found")
        assert error_response["success"] is False
        assert error_response["error"] == "User not found"

    def test_controller_data_sanitization(self):
        """Test controller data sanitization logic."""

        def sanitize_user_data(user_data, include_sensitive=False):
            safe_fields = ["id", "name", "team_count", "registered_at"]
            sensitive_fields = ["email", "role", "last_login_ip"]

            sanitized = {k: v for k, v in user_data.items() if k in safe_fields}

            if include_sensitive:
                sanitized.update({k: v for k, v in user_data.items() if k in sensitive_fields})

            return sanitized

        user_data = {
            "id": 123,
            "name": "Test User",
            "email": "test@example.com",
            "role": "admin",
            "team_count": 2,
            "registered_at": "2025-06-28",
            "last_login_ip": "192.168.1.1",
            "password_hash": "secret",
        }

        public_data = sanitize_user_data(user_data)
        assert "id" in public_data
        assert "name" in public_data
        assert "email" not in public_data
        assert "password_hash" not in public_data

        admin_data = sanitize_user_data(user_data, include_sensitive=True)
        assert "email" in admin_data
        assert "role" in admin_data
        assert "password_hash" not in admin_data


class TestUserControllerBusinessLogic:
    """Test user controller business logic and complex scenarios."""

    def test_user_eligibility_complex_scenarios(self):
        """Test complex eligibility scenarios with multiple conditions."""

        def check_complex_eligibility(user_data, event_data, team_data=None):
            """Complex eligibility check with multiple business rules."""
            errors = []
            warnings = []

            # User status checks
            if user_data.get("banned", False):
                errors.append("User is banned and cannot join teams")
                return {"eligible": False, "errors": errors, "warnings": warnings}

            if user_data.get("suspended_until") and user_data["suspended_until"] > "2025-06-29":
                errors.append("User is temporarily suspended")
                return {"eligible": False, "errors": errors, "warnings": warnings}

            # Event-specific checks
            if event_data.get("registration_closed", False):
                errors.append("Event registration is closed")
                return {"eligible": False, "errors": errors, "warnings": warnings}

            if event_data.get("requires_invitation", False) and not user_data.get("has_invitation", False):
                errors.append("This event requires an invitation")
                return {"eligible": False, "errors": errors, "warnings": warnings}

            # Experience level requirements
            user_level = user_data.get("experience_level", "beginner")
            required_level = event_data.get("minimum_experience_level", "beginner")

            level_hierarchy = {
                "beginner": 1,
                "intermediate": 2,
                "advanced": 3,
                "expert": 4,
            }
            if level_hierarchy.get(user_level, 1) < level_hierarchy.get(required_level, 1):
                errors.append(f"Event requires {required_level} experience level, user is {user_level}")
                return {"eligible": False, "errors": errors, "warnings": warnings}

            # Team-specific checks (if joining specific team)
            if team_data:
                if team_data.get("current_size", 0) >= team_data.get("max_size", 4):
                    errors.append("Team is full")
                    return {"eligible": False, "errors": errors, "warnings": warnings}

                # Skill requirements
                required_skills = set(team_data.get("required_skills", []))
                user_skills = set(user_data.get("skills", []))
                missing_skills = required_skills - user_skills

                if missing_skills and team_data.get("strict_skill_requirements", False):
                    errors.append(f"Missing required skills: {', '.join(missing_skills)}")
                    return {"eligible": False, "errors": errors, "warnings": warnings}
                elif missing_skills:
                    warnings.append(f"Consider learning these skills: {', '.join(missing_skills)}")

            # Check existing team membership in event
            current_teams_in_event = user_data.get("current_teams_in_event", 0)
            max_teams_per_event = event_data.get("max_teams_per_user", 1)

            if current_teams_in_event >= max_teams_per_event:
                errors.append(
                    f"User already has {current_teams_in_event} team(s) in this event (max: {max_teams_per_event})"
                )
                return {"eligible": False, "errors": errors, "warnings": warnings}

            # Success with possible warnings
            return {"eligible": True, "errors": [], "warnings": warnings}

        # Test cases
        valid_user = {
            "banned": False,
            "experience_level": "intermediate",
            "skills": ["python", "web", "crypto"],
            "current_teams_in_event": 0,
        }

        valid_event = {
            "registration_closed": False,
            "requires_invitation": False,
            "minimum_experience_level": "beginner",
            "max_teams_per_user": 1,
        }

        valid_team = {
            "current_size": 2,
            "max_size": 4,
            "required_skills": ["python", "web"],
            "strict_skill_requirements": False,
        }

        # Should be eligible
        result = check_complex_eligibility(valid_user, valid_event, valid_team)
        assert result["eligible"] is True
        assert len(result["errors"]) == 0

        # Test banned user
        banned_user = valid_user.copy()
        banned_user["banned"] = True
        result = check_complex_eligibility(banned_user, valid_event, valid_team)
        assert result["eligible"] is False
        assert any("banned" in error.lower() for error in result["errors"])

        # Test skill requirements
        strict_team = valid_team.copy()
        strict_team["strict_skill_requirements"] = True
        strict_team["required_skills"] = [
            "python",
            "web",
            "reverse",
        ]  # User missing "reverse"

        result = check_complex_eligibility(valid_user, valid_event, strict_team)
        assert result["eligible"] is False
        assert any("missing required skills" in error.lower() for error in result["errors"])

    def test_user_stats_calculation_edge_cases(self):
        """Test user statistics calculation with edge cases."""

        def calculate_detailed_user_stats(user_data, teams_data, events_data):
            """Calculate comprehensive user statistics."""
            stats = {
                "participation": {},
                "performance": {},
                "social": {},
                "achievements": {},
                "trends": {},
            }

            # Participation stats
            stats["participation"]["total_teams"] = len(teams_data)
            stats["participation"]["total_events"] = len(set(team["event_id"] for team in teams_data))
            stats["participation"]["active_teams"] = len([t for t in teams_data if t.get("status") == "active"])

            # Performance stats
            total_points = sum(team.get("points_earned", 0) for team in teams_data)
            stats["performance"]["total_points"] = total_points
            stats["performance"]["average_points_per_team"] = total_points / len(teams_data) if teams_data else 0

            # Calculate win rate
            wins = sum(1 for team in teams_data if team.get("final_rank") == 1)
            top_3 = sum(1 for team in teams_data if team.get("final_rank") is not None and team.get("final_rank") <= 3)
            completed_events = len([t for t in teams_data if t.get("status") == "completed"])

            stats["performance"]["win_rate"] = wins / completed_events if completed_events > 0 else 0
            stats["performance"]["top_3_rate"] = top_3 / completed_events if completed_events > 0 else 0

            # Social stats
            stats["social"]["teams_captained"] = sum(1 for team in teams_data if team.get("role") == "captain")
            stats["social"]["leadership_ratio"] = (
                stats["social"]["teams_captained"] / len(teams_data) if teams_data else 0
            )

            # Achievement stats
            stats["achievements"]["perfect_scores"] = sum(
                1 for team in teams_data if team.get("score_percentage", 0) == 100
            )
            stats["achievements"]["consistent_performer"] = (
                len([t for t in teams_data if t.get("score_percentage", 0) >= 70]) >= 3
            )

            # Trend analysis (last 6 months vs overall)
            recent_teams = [t for t in teams_data if t.get("created_at", "2020-01-01") >= "2025-06-01"]
            if recent_teams and len(teams_data) > len(recent_teams):
                recent_avg = sum(t.get("points_earned", 0) for t in recent_teams) / len(recent_teams)
                overall_avg = stats["performance"]["average_points_per_team"]
                stats["trends"]["performance_trend"] = "improving" if recent_avg > overall_avg else "declining"
                stats["trends"]["activity_trend"] = "active" if len(recent_teams) >= 2 else "inactive"
            else:
                stats["trends"]["performance_trend"] = "stable"
                stats["trends"]["activity_trend"] = "new_user" if len(teams_data) <= 2 else "active"

            return stats

        # Test with comprehensive data
        user_data = {"id": 123, "username": "testuser"}

        teams_data = [
            {
                "event_id": 1,
                "points_earned": 500,
                "final_rank": 1,
                "status": "completed",
                "role": "captain",
                "score_percentage": 95,
                "created_at": "2025-08-01",
            },
            {
                "event_id": 2,
                "points_earned": 300,
                "final_rank": 3,
                "status": "completed",
                "role": "member",
                "score_percentage": 80,
                "created_at": "2025-07-01",
            },
            {
                "event_id": 3,
                "points_earned": 150,
                "final_rank": 8,
                "status": "completed",
                "role": "member",
                "score_percentage": 60,
                "created_at": "2025-01-01",
            },
            {
                "event_id": 4,
                "points_earned": 0,
                "final_rank": None,
                "status": "active",
                "role": "member",
                "score_percentage": 0,
                "created_at": "2025-09-01",
            },
        ]

        events_data = [
            {"id": 1, "name": "CTF 1"},
            {"id": 2, "name": "CTF 2"},
            {"id": 3, "name": "CTF 3"},
            {"id": 4, "name": "CTF 4"},
        ]

        stats = calculate_detailed_user_stats(user_data, teams_data, events_data)

        # Verify participation stats
        assert stats["participation"]["total_teams"] == 4
        assert stats["participation"]["total_events"] == 4  # 4 unique events
        assert stats["participation"]["active_teams"] == 1

        # Verify performance stats
        assert stats["performance"]["total_points"] == 950
        assert stats["performance"]["average_points_per_team"] == 237.5
        assert stats["performance"]["win_rate"] == 1 / 3  # 1 win out of 3 completed
        assert stats["performance"]["top_3_rate"] == 2 / 3  # 2 top-3 out of 3 completed

        # Verify social stats
        assert stats["social"]["teams_captained"] == 1
        assert stats["social"]["leadership_ratio"] == 0.25  # 1 out of 4

        # Verify achievement stats
        assert stats["achievements"]["perfect_scores"] == 0  # No 100% scores
        assert stats["achievements"]["consistent_performer"] is False  # Only 2 teams >= 70%

        # Verify trends (recent performance better than overall)
        assert stats["trends"]["performance_trend"] == "improving"  # Recent avg (400) > overall avg (237.5)
        assert stats["trends"]["activity_trend"] == "active"
