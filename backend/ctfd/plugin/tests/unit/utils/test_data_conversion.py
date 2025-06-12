"""
/backend/ctfd/plugin/tests/unit/utils/test_data_conversion.py
Unit tests for data conversion utilities.
"""

from datetime import datetime
from enum import Enum
from unittest.mock import Mock

from plugin.utils.data_conversion import rows_to_dicts, row_to_dict


class StatusEnum(Enum):
    """Test enum for conversion testing."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class TestRowsToDicts:
    """Test rows_to_dicts conversion utility."""

    def test_rows_to_dicts_empty_input(self):
        """Test conversion with empty input."""
        result = rows_to_dicts([])
        assert result == []
        assert isinstance(result, list)

    def test_rows_to_dicts_basic_conversion(self):
        """Test basic conversion of database rows."""
        mock_rows = []
        for i in range(3):
            row = Mock()
            row.id = i + 1
            row.name = f"Item {i + 1}"
            row.value = i * 10
            row._fields = ["id", "name", "value"]
            mock_rows.append(row)

        result = rows_to_dicts(mock_rows)

        assert len(result) == 3
        assert result[0] == {"id": 1, "name": "Item 1", "value": 0}
        assert result[1] == {"id": 2, "name": "Item 2", "value": 10}
        assert result[2] == {"id": 3, "name": "Item 3", "value": 20}

    def test_rows_to_dicts_field_mapping(self):
        """Test conversion with custom field mapping."""
        mock_row = Mock()
        mock_row.user_id = 42
        mock_row.team_name = "Alpha Team"
        mock_row.member_count = 5
        mock_row._fields = ["user_id", "team_name", "member_count"]

        result = rows_to_dicts([mock_row])

        assert len(result) == 1
        assert result[0]["user_id"] == 42
        assert result[0]["team_name"] == "Alpha Team"
        assert result[0]["member_count"] == 5

    def test_rows_to_dicts_with_none_values(self):
        """Test conversion handling None values."""
        mock_row = Mock()
        mock_row.id = 1
        mock_row.name = "Test"
        mock_row.optional_field = None
        mock_row.another_field = ""
        mock_row._fields = ["id", "name", "optional_field", "another_field"]

        result = rows_to_dicts([mock_row])

        assert result[0]["id"] == 1
        assert result[0]["name"] == "Test"
        assert result[0]["optional_field"] is None
        assert result[0]["another_field"] == ""


class TestRowToDict:
    """Test row_to_dict single row conversion."""

    def test_row_to_dict_single_row(self):
        """Test conversion of a single database row."""
        mock_row = Mock()
        mock_row.id = 100
        mock_row.title = "Test Title"
        mock_row.created_at = datetime(2024, 1, 1, 12, 0, 0)
        mock_row._fields = ["id", "title", "created_at"]

        result = row_to_dict(mock_row)

        assert isinstance(result, dict)
        assert result["id"] == 100
        assert result["title"] == "Test Title"
        assert result["created_at"] == datetime(2024, 1, 1, 12, 0, 0)

    def test_row_to_dict_with_nested_objects(self):
        """Test conversion with nested objects."""
        mock_team = Mock()
        mock_team.id = 10
        mock_team.name = "Team Alpha"

        mock_row = Mock()
        mock_row.id = 1
        mock_row.user_id = 5
        mock_row.team = mock_team
        mock_row._fields = ["id", "user_id", "team"]

        result = row_to_dict(mock_row)

        assert result["id"] == 1
        assert result["user_id"] == 5
        assert result["team"] == mock_team

    def test_row_to_dict_with_special_types(self):
        """Test conversion with special types like Enum."""
        mock_row = Mock()
        mock_row.id = 1
        mock_row.status = StatusEnum.ACTIVE
        mock_row.is_active = True
        mock_row.score = 95.5
        mock_row._fields = ["id", "status", "is_active", "score"]

        result = row_to_dict(mock_row)

        assert result["id"] == 1
        assert result["status"] == StatusEnum.ACTIVE
        assert result["is_active"] is True
        assert result["score"] == 95.5


class TestDataConversionEdgeCases:
    """Test edge cases in data conversion."""

    def test_empty_fields_list(self):
        """Test handling of rows with no fields."""
        mock_row = Mock()
        mock_row._fields = []

        result = row_to_dict(mock_row)
        assert result == {}

    def test_missing_attribute(self):
        """Test handling when field doesn't exist on row."""
        mock_row = Mock()
        mock_row.id = 1
        mock_row._fields = ["id", "missing_field"]

        try:
            result = row_to_dict(mock_row)
            assert "id" in result
        except AttributeError:
            pass

    def test_rows_with_different_fields(self):
        """Test converting rows with different field sets."""
        mock_row1 = Mock()
        mock_row1.id = 1
        mock_row1.type = "A"
        mock_row1.value_a = 100
        mock_row1._fields = ["id", "type", "value_a"]

        mock_row2 = Mock()
        mock_row2.id = 2
        mock_row2.type = "B"
        mock_row2.value_b = 200
        mock_row2._fields = ["id", "type", "value_b"]

        result = rows_to_dicts([mock_row1, mock_row2])

        assert len(result) == 2
        assert result[0]["type"] == "A"
        assert "value_a" in result[0]
        assert result[1]["type"] == "B"
        assert "value_b" in result[1]
