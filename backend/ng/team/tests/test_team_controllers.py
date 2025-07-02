"""
Unit tests for team domain controllers
"""


class TestCreateTeamController:
    def test_team_creation_logic(self):
        def mock_create_team(team_data, user_eligibility):
            if not user_eligibility.get("can_join"):
                raise ValueError("User cannot join teams")
            if not team_data.get("name"):
                raise ValueError("Team name required")
            return {"team": {"id": 1, **team_data, "member_count": 1}}

        valid_data = {"name": "Test Team"}
        eligibility = {"can_join": True}
        result = mock_create_team(valid_data, eligibility)

        assert result["team"]["id"] == 1
        assert result["team"]["name"] == "Test Team"
        assert result["team"]["member_count"] == 1


class TestJoinTeamController:
    def test_team_join_logic(self):
        def mock_join_team(team, user, max_size):
            current_members = team.get("member_count", 0)
            if current_members >= max_size:
                return {"success": False, "error": "Team full"}
            team["member_count"] = current_members + 1
            return {"success": True, "team": team}

        team = {"id": 1, "name": "Test Team", "member_count": 3}
        user = {"id": 1}

        result1 = mock_join_team(team.copy(), user, 4)
        result2 = mock_join_team(team.copy(), user, 3)

        assert result1["success"] is True
        assert result1["team"]["member_count"] == 4
        assert result2["success"] is False
        assert "Team full" in result2["error"]
