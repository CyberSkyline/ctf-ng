"""
/backend/ctf-ng/backend/ctfd/plugin/tests/unit/utils/test_api_responses.py
Unit tests for API response formatting utilities.
"""

from datetime import datetime
from unittest.mock import Mock

from plugin.utils.api_responses import (
    success_response,
    error_response,
    controller_response,
    serialize_model_for_api,
)


class TestSuccessResponse:
    """Test success response formatting."""

    def test_success_response_basic(self):
        """Test basic success response structure."""
        data = {"id": 1, "name": "Test"}
        response, status = success_response(data)

        assert response["success"] is True
        assert response["data"] == data
        assert status == 200
        assert "error" not in response

    def test_success_response_with_custom_status(self):
        """Test success response with custom status code."""
        data = {"created": True}
        response, status = success_response(data, status_code=201)

        assert response["success"] is True
        assert response["data"] == data
        assert status == 201

    def test_success_response_empty_data(self):
        """Test success response with empty data."""
        response, status = success_response({})

        assert response["success"] is True
        assert response["data"] == {}
        assert status == 200

    def test_success_response_filters_internal_fields(self):
        """Test that success response filters out internal fields."""
        data = {"id": 1, "name": "Test", "success": True, "error": "ignored"}
        response, status = success_response(data)

        assert response["success"] is True
        # Should filter out 'success' and 'error' from data
        assert "success" not in response["data"]
        assert "error" not in response["data"]
        assert response["data"]["id"] == 1
        assert response["data"]["name"] == "Test"


class TestErrorResponse:
    """Test error response formatting."""

    def test_error_response_basic(self):
        """Test basic error response structure."""
        message = "Something went wrong"
        response, status = error_response(message)

        assert response["success"] is False
        assert response["errors"]["general"] == message
        assert status == 400
        assert "data" not in response

    def test_error_response_with_custom_field(self):
        """Test error response with custom field name."""
        message = "Invalid email"
        response, status = error_response(message, field="email")

        assert response["success"] is False
        assert response["errors"]["email"] == message
        assert status == 400

    def test_error_response_with_status_code(self):
        """Test error response with custom status code."""
        message = "Not found"
        response, status = error_response(message, status_code=404)

        assert response["success"] is False
        assert response["errors"]["general"] == message
        assert status == 404


class TestControllerResponse:
    """Test controller response routing."""

    def test_controller_response_success_result(self):
        """Test controller response with successful controller result."""
        controller_result = {
            "success": True,
            "id": 1,
            "name": "Test Team",
            "message": "Team created successfully",
        }

        response, status = controller_response(controller_result)

        assert response["success"] is True
        assert response["data"]["id"] == 1
        assert response["data"]["name"] == "Test Team"
        assert status == 200

    def test_controller_response_error_result(self):
        """Test controller response with error controller result."""
        controller_result = {"success": False, "error": "Team not found"}

        response, status = controller_response(controller_result)

        # Should pass through error response structure
        assert response["success"] is False
        assert response["errors"]["general"] == "Team not found"
        assert status == 400

    def test_controller_response_with_custom_status(self):
        """Test controller response with custom success status."""
        controller_result = {"success": True, "id": 1, "created": True}

        response, status = controller_response(controller_result, success_status=201)

        assert response["success"] is True
        assert response["data"]["id"] == 1
        assert status == 201


class TestSerializeModelForApi:
    """Test model serialization for API responses."""

    def test_serialize_datetime_fields(self):
        """Test serialization of datetime fields."""
        dt = datetime(2024, 1, 1, 12, 0, 0)
        result = serialize_model_for_api(dt)
        assert result == "2024-01-01T12:00:00"

    def test_serialize_none_value(self):
        """Test serialization of None values."""
        result = serialize_model_for_api(None)
        assert result is None

    def test_serialize_model_object(self):
        """Test serialization of model-like objects."""

        class MockModel:
            def __init__(self):
                self.id = 1
                self.name = "Test"
                self._internal = "hidden"
                self.created_at = datetime(2024, 1, 1, 12, 0, 0)

        mock_model = MockModel()

        result = serialize_model_for_api(mock_model)

        assert result["id"] == 1
        assert result["name"] == "Test"
        assert "_internal" not in result
        assert result["created_at"] == "2024-01-01T12:00:00"

    def test_serialize_enum_fields(self):
        """Test serialization of enum fields."""
        from plugin.team.models.enums import TeamRole

        class MockModel:
            def __init__(self):
                self.id = 1
                self.role = TeamRole.CAPTAIN

        mock_model = MockModel()

        result = serialize_model_for_api(mock_model)

        assert result["id"] == 1
        assert result["role"] == "captain"

    def test_serialize_nested_objects(self):
        """Test serialization of nested objects."""
        nested_mock = Mock()
        nested_mock.__dict__ = {"id": 5, "name": "Nested"}

        main_mock = Mock()
        main_mock.__dict__ = {"id": 1, "nested": nested_mock}

        result = serialize_model_for_api(main_mock)

        assert result["id"] == 1
        assert result["nested"]["id"] == 5
        assert result["nested"]["name"] == "Nested"

    def test_serialize_list_of_objects(self):
        """Test serialization of lists containing objects."""
        item1 = Mock()
        item1.__dict__ = {"id": 1, "name": "Item 1"}

        item2 = Mock()
        item2.__dict__ = {"id": 2, "name": "Item 2"}

        main_mock = Mock()
        main_mock.__dict__ = {"id": 1, "items": [item1, item2]}

        result = serialize_model_for_api(main_mock)

        assert result["id"] == 1
        assert len(result["items"]) == 2
        assert result["items"][0]["id"] == 1
        assert result["items"][1]["id"] == 2

    def test_serialize_primitive_values(self):
        """Test that primitive values are returned as-is."""
        assert serialize_model_for_api("string") == "string"
        assert serialize_model_for_api(42) == 42
        assert serialize_model_for_api(True) is True
        assert serialize_model_for_api([1, 2, 3]) == [1, 2, 3]


class TestResponseFormatting:
    """Test response formatting consistency."""

    def test_success_response_structure_consistency(self):
        """Test that success responses have consistent structure."""
        responses = [
            success_response({"id": 1})[0],
            success_response({"count": 0})[0],
            success_response({})[0],
        ]

        for response in responses:
            assert "success" in response
            assert "data" in response
            assert response["success"] is True

            assert "errors" not in response

    def test_error_response_structure_consistency(self):
        """Test that error responses have consistent structure."""
        responses = [
            error_response("Simple error")[0],
            error_response("Field error", field="name")[0],
            error_response("Server error", status_code=500)[0],
        ]

        for response in responses:
            assert "success" in response
            assert "errors" in response
            assert response["success"] is False

            assert "data" not in response

    def test_controller_response_routing(self):
        """Test controller response properly routes success vs error."""
        # Success case
        success_result = {"success": True, "id": 1}
        response, status = controller_response(success_result)
        assert response["success"] is True
        assert "data" in response

        error_result = {"success": False, "error": "Failed"}
        response, status = controller_response(error_result)
        assert response["success"] is False
        assert "errors" in response
