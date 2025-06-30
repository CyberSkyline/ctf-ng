"""
Unit tests for core domain logic
"""

from datetime import datetime


def success_response(data, status_code=200):
    if isinstance(data, dict):
        filtered_data = {k: v for k, v in data.items() if k not in ["success", "error"]}
    else:
        filtered_data = data

    return {"success": True, "data": filtered_data}, status_code


def error_response(message, field="general", status_code=400):
    return {"success": False, "errors": {field: message}}, status_code


def serialize_model_for_api(obj, is_admin_request=False):
    if obj is None:
        return None

    if isinstance(obj, datetime):
        return obj.isoformat()

    if hasattr(obj, "serialize"):
        serialized = obj.serialize(include_admin_fields=is_admin_request)
        return serialize_model_for_api(serialized, is_admin_request)

    if isinstance(obj, dict):
        return {k: serialize_model_for_api(v, is_admin_request) for k, v in obj.items()}

    if isinstance(obj, list):
        return [serialize_model_for_api(item, is_admin_request) for item in obj]

    if hasattr(obj, "value"):  # Enum handling
        return obj.value

    return obj


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
        """Test serialization of model-like objects with .serialize() method."""

        class MockModel:
            def __init__(self):
                self.id = 1
                self.name = "Test"
                self._internal = "hidden"
                self.created_at = datetime(2024, 1, 1, 12, 0, 0)

            def serialize(self, include_admin_fields=False):
                data = {
                    "id": self.id,
                    "name": self.name,
                    "created_at": self.created_at,
                }
                if include_admin_fields:
                    data["_internal"] = self._internal
                return data

        mock_model = MockModel()

        result = serialize_model_for_api(mock_model, is_admin_request=False)
        assert result["id"] == 1
        assert result["name"] == "Test"
        assert "_internal" not in result
        assert result["created_at"] == "2024-01-01T12:00:00"

        admin_result = serialize_model_for_api(mock_model, is_admin_request=True)
        assert admin_result["id"] == 1
        assert admin_result["name"] == "Test"
        assert admin_result["_internal"] == "hidden"
        assert admin_result["created_at"] == "2024-01-01T12:00:00"

    def test_serialize_enum_fields(self):
        """Test serialization of enum fields."""
        from ....team.models.enums import TeamRole

        class MockModel:
            def __init__(self):
                self.id = 1
                self.role = TeamRole.CAPTAIN

            def serialize(self, include_admin_fields=False):
                return {
                    "id": self.id,
                    "role": self.role,
                }

        mock_model = MockModel()

        result = serialize_model_for_api(mock_model, is_admin_request=False)

        assert result["id"] == 1
        assert result["role"] == "captain"

    def test_serialize_nested_objects(self):
        """Test serialization of nested objects."""

        class NestedMock:
            def __init__(self):
                self.id = 5
                self.name = "Nested"

            def serialize(self, include_admin_fields=False):
                return {"id": self.id, "name": self.name}

        class MainMock:
            def __init__(self):
                self.id = 1
                self.nested = NestedMock()

            def serialize(self, include_admin_fields=False):
                return {"id": self.id, "nested": self.nested}

        main_mock = MainMock()
        result = serialize_model_for_api(main_mock, is_admin_request=False)

        assert result["id"] == 1
        assert result["nested"]["id"] == 5
        assert result["nested"]["name"] == "Nested"

    def test_serialize_list_of_objects(self):
        """Test serialization of lists containing objects."""

        class ItemMock:
            def __init__(self, item_id, name):
                self.id = item_id
                self.name = name

            def serialize(self, include_admin_fields=False):
                return {"id": self.id, "name": self.name}

        class MainMock:
            def __init__(self):
                self.id = 1
                self.items = [ItemMock(1, "Item 1"), ItemMock(2, "Item 2")]

            def serialize(self, include_admin_fields=False):
                return {"id": self.id, "items": self.items}

        main_mock = MainMock()
        result = serialize_model_for_api(main_mock, is_admin_request=False)

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
