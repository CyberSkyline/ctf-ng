"""
Utilities for creating and formatting standardized JSON API responses.
"""

from typing import Any
from datetime import datetime
from sqlalchemy.engine import Row


def serialize_model_for_api(obj: Any, is_admin_request: bool | None = False) -> Any:
    """
    Recursively serializes an object for API response with proper datetime handling.

    Handles:
    - SQLAlchemy models with .serialize() methods
    - SQLAlchemy Row objects from complex queries
    - Datetime objects (converts to UTC ISO format with Z suffix)
    - Enums
    - Lists and dictionaries (recursive)
    - Primitive types
    """
    if obj is None:
        return None

    if isinstance(obj, Row):
        return {key: serialize_model_for_api(value, is_admin_request) for key, value in obj._asdict().items()}

    if hasattr(obj, "serialize"):
        serialized_data = obj.serialize(include_admin_fields=is_admin_request)
        return serialize_model_for_api(serialized_data, is_admin_request)

    if isinstance(obj, datetime):
        if obj.tzinfo is None:
            return obj.isoformat() + "Z"
        else:
            utc_dt = obj.utctimetuple()
            return datetime(*utc_dt[:6]).isoformat() + "Z"

    if hasattr(obj, "value"):
        return obj.value

    if isinstance(obj, list):
        return [serialize_model_for_api(item, is_admin_request) for item in obj]

    if isinstance(obj, dict):
        return {key: serialize_model_for_api(value, is_admin_request) for key, value in obj.items()}

    return obj


# Success | Error | Responses
def success_response(data: dict[str, Any] | list[Any] | bool | None = None, status_code: int = 200) -> tuple[dict[str, Any], int]:
    from ...permissions.controllers.get_user_roles import get_user_roles
    from ...permissions.models.enums import RoleEnum
    serialized_data = serialize_model_for_api(data, is_admin_request=True if RoleEnum.ADMIN in get_user_roles() else False)

    return {"success": True, "data": serialized_data}, status_code


def error_response(error_message: str, field: str = "general", status_code: int = 400) -> tuple[dict[str, Any], int]:
    return {"success": False, "errors": {field: error_message}}, status_code
