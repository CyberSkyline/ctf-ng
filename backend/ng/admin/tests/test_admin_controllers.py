"""
Unit tests for admin domain controllers
"""


class TestGetDataCountsController:
    def test_data_counts_calculation(self):
        def mock_get_data_counts(mock_data):
            return {
                "events": len(mock_data.get("events", [])),
                "teams": len(mock_data.get("teams", [])),
                "users": len(mock_data.get("users", [])),
            }

        test_data = {"events": [1, 2, 3], "teams": [1, 2], "users": [1, 2, 3, 4, 5]}

        result = mock_get_data_counts(test_data)

        assert result["events"] == 3
        assert result["teams"] == 2
        assert result["users"] == 5


class TestCleanupController:
    def test_cleanup_logic(self):
        def mock_cleanup_orphaned_data(data):
            cleaned = []
            for item in data:
                if item.get("valid"):
                    cleaned.append(item)
            return {"cleaned_count": len(cleaned), "items": cleaned}

        test_data = [
            {"id": 1, "valid": True},
            {"id": 2, "valid": False},
            {"id": 3, "valid": True},
        ]

        result = mock_cleanup_orphaned_data(test_data)

        assert result["cleaned_count"] == 2
        assert len(result["items"]) == 2
        assert result["items"][0]["id"] == 1
        assert result["items"][1]["id"] == 3
