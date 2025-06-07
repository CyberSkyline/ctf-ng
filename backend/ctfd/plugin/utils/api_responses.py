# /plugin/utils/api_responses.py

from typing import Any


def serialize_model_for_api(obj):
    """Serialize model objects for JSON API responses."""
    if obj is None:
        return None

    # Handle datetime serialization
    if hasattr(obj, "isoformat"):
        return obj.isoformat()

    # Handle model objects
    if hasattr(obj, "__dict__"):
        result = {}
        for key, value in obj.__dict__.items():
            if key.startswith("_"):
                continue
            if hasattr(value, "isoformat"):
                result[key] = value.isoformat()
            elif hasattr(value, "value"):  # enum
                result[key] = value.value
            elif hasattr(value, "__dict__"):  # nested model
                result[key] = serialize_model_for_api(value)
            elif isinstance(value, list):  # list of models
                result[key] = [serialize_model_for_api(item) for item in value]
            else:
                result[key] = value
        return result

    return obj


def success_response(data: dict[str, Any], status_code: int = 200) -> tuple[dict[str, Any], int]:
    clean_data = {k: v for k, v in data.items() if k not in ["success", "error"]}

    serialized_data = {}
    for key, value in clean_data.items():
        serialized_data[key] = serialize_model_for_api(value)

    return {"success": True, "data": serialized_data}, status_code


def error_response(error_message: str, field: str = "general", status_code: int = 400) -> tuple[dict[str, Any], int]:
    return {"success": False, "errors": {field: error_message}}, status_code


def controller_response(
    result: dict[str, Any], success_status: int = 200, error_field: str = "general"
) -> tuple[dict[str, Any], int]:
    if result.get("success"):
        return success_response(result, success_status)
    else:
        error_msg = result.get("error", "Unknown error occurred")
        return error_response(error_msg, error_field, 400)
