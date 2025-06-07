# /plugin/utils/api_responses.py

from typing import Dict, Any, Tuple


def success_response(data: Dict[str, Any], status_code: int = 200) -> Tuple[Dict[str, Any], int]:
    clean_data = {k: v for k, v in data.items() if k not in ["success", "error"]}

    return {"success": True, "data": clean_data}, status_code


def error_response(error_message: str, field: str = "general", status_code: int = 400) -> Tuple[Dict[str, Any], int]:
    return {"success": False, "errors": {field: error_message}}, status_code


def controller_response(
    result: Dict[str, Any], success_status: int = 200, error_field: str = "general"
) -> Tuple[Dict[str, Any], int]:
    if result.get("success"):
        return success_response(result, success_status)
    else:
        error_msg = result.get("error", "Unknown error occurred")
        return error_response(error_msg, error_field, 400)
