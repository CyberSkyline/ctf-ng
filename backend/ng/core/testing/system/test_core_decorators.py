"""
Tests for middleware functionality.
"""

import pytest
from unittest.mock import Mock, patch


class TestApiEndpointDecorator:
    """Test api_endpoint decorator functionality using completely isolated unit tests."""

    def test_api_endpoint_auth_required_behavior(self):
        """Test that api_endpoint decorator with auth_required=True sets g.user when authenticated."""
        with patch.dict(
            "sys.modules",
            {
                "flask": Mock(),
                "flask.g": Mock(),
                "CTFd.utils.user": Mock(),
                "CTFd.utils.decorators": Mock(),
            },
        ):
            import importlib
            from ...middleware import auth as decorators

            importlib.reload(decorators)

            mock_g = Mock()
            mock_get_current_user = Mock()
            mock_user = Mock(id=1)
            mock_get_current_user.return_value = mock_user
            mock_authed_only = Mock(side_effect=lambda f: f)  # Pass through

            with patch.object(decorators, "g", mock_g):
                with patch.object(decorators, "get_current_user", mock_get_current_user):
                    with patch.object(decorators, "authed_only", mock_authed_only):
                        mock_func = Mock(return_value={"success": True})
                        decorated_func = decorators.api_endpoint(auth_required=True)(mock_func)

                        decorated_func()

                        assert mock_g.user == mock_user
                        mock_func.assert_called_once()

    def test_api_endpoint_auth_required_raises_permission_error(self):
        """Test that api_endpoint with auth_required raises PermissionError when no user."""
        with patch.dict(
            "sys.modules",
            {
                "flask": Mock(),
                "flask.g": Mock(),
                "CTFd.utils.user": Mock(),
                "CTFd.utils.decorators": Mock(),
            },
        ):
            import importlib
            from ...middleware import auth as decorators

            importlib.reload(decorators)

            mock_g = Mock()
            mock_get_current_user = Mock(return_value=None)
            mock_authed_only = Mock(side_effect=lambda f: f)
            mock_handle_exceptions = Mock(side_effect=lambda f: f)

            with patch.object(decorators, "g", mock_g):
                with patch.object(decorators, "get_current_user", mock_get_current_user):
                    with patch.object(decorators, "authed_only", mock_authed_only):
                        with patch.object(decorators, "handle_exceptions", mock_handle_exceptions):
                            mock_func = Mock()
                            decorated_func = decorators.api_endpoint(auth_required=True)(mock_func)

                            with pytest.raises(decorators.PermissionError) as exc_info:
                                decorated_func()

                            assert "Authentication is required" in str(exc_info.value)
                            mock_func.assert_not_called()

    def test_api_endpoint_json_required_behavior(self):
        """Test that api_endpoint with json_required=True sets g.json_data when valid JSON."""
        with patch.dict(
            "sys.modules",
            {
                "flask": Mock(),
                "flask.g": Mock(),
                "flask.request": Mock(),
                "CTFd.utils.decorators": Mock(),
            },
        ):
            import importlib
            from ...middleware import auth as decorators

            importlib.reload(decorators)

            mock_g = Mock()
            mock_request = Mock()
            mock_request.is_json = True
            mock_request.get_json.return_value = {"test": "data"}

            with patch.object(decorators, "g", mock_g):
                with patch.object(decorators, "request", mock_request):
                    mock_func = Mock(return_value={"success": True})
                    decorated_func = decorators.api_endpoint(auth_required=False, json_required=True)(mock_func)

                    decorated_func()

                    assert mock_g.json_data == {"test": "data"}
                    mock_func.assert_called_once()

    def test_api_endpoint_json_required_raises_validation_error_no_json(self):
        """Test that api_endpoint with json_required raises ValidationError for non-JSON requests."""
        with patch.dict(
            "sys.modules",
            {
                "flask": Mock(),
                "flask.g": Mock(),
                "flask.request": Mock(),
                "CTFd.utils.decorators": Mock(),
            },
        ):
            import importlib
            from ...middleware import auth as decorators

            importlib.reload(decorators)

            mock_request = Mock()
            mock_request.is_json = False
            mock_handle_exceptions = Mock(side_effect=lambda f: f)  # Pass through

            with patch.object(decorators, "request", mock_request):
                with patch.object(decorators, "handle_exceptions", mock_handle_exceptions):
                    mock_func = Mock()
                    decorated_func = decorators.api_endpoint(auth_required=False, json_required=True)(mock_func)

                    with pytest.raises(decorators.ValidationError) as exc_info:
                        decorated_func()

                    assert "JSON body" in str(exc_info.value)
                    mock_func.assert_not_called()

    def test_api_endpoint_json_required_raises_validation_error_empty_json(self):
        """Test that api_endpoint with json_required raises ValidationError for empty JSON."""
        with patch.dict(
            "sys.modules",
            {
                "flask": Mock(),
                "flask.g": Mock(),
                "flask.request": Mock(),
                "CTFd.utils.decorators": Mock(),
            },
        ):
            import importlib
            from ...middleware import auth as decorators

            importlib.reload(decorators)

            mock_request = Mock()
            mock_request.is_json = True
            mock_request.get_json.return_value = None
            mock_handle_exceptions = Mock(side_effect=lambda f: f)  # Pass through

            with patch.object(decorators, "request", mock_request):
                with patch.object(decorators, "handle_exceptions", mock_handle_exceptions):
                    mock_func = Mock()
                    decorated_func = decorators.api_endpoint(auth_required=False, json_required=True)(mock_func)

                    with pytest.raises(decorators.ValidationError) as exc_info:
                        decorated_func()

                    assert "malformed or empty" in str(exc_info.value)
                    mock_func.assert_not_called()

    def test_api_endpoint_with_validation_func(self):
        """Test that api_endpoint with validation_func validates and sets g.validated_data."""
        with patch.dict(
            "sys.modules",
            {
                "flask": Mock(),
                "flask.g": Mock(),
                "flask.request": Mock(),
                "CTFd.utils.decorators": Mock(),
            },
        ):
            import importlib
            from ...middleware import auth as decorators

            importlib.reload(decorators)

            mock_g = Mock()
            mock_request = Mock()
            mock_request.is_json = True
            mock_request.get_json.return_value = {"name": "Test Team"}

            mock_validation_func = Mock()
            mock_validation_func.return_value = {"name": "Test Team", "validated": True}

            with patch.object(decorators, "g", mock_g):
                with patch.object(decorators, "request", mock_request):
                    mock_func = Mock(return_value={"success": True})
                    decorated_func = decorators.api_endpoint(
                        auth_required=False,
                        json_required=True,
                        validation_func=mock_validation_func,
                    )(mock_func)

                    decorated_func()

                    assert mock_g.json_data == {"name": "Test Team"}
                    assert mock_g.validated_data == {
                        "name": "Test Team",
                        "validated": True,
                    }
                    mock_validation_func.assert_called_once_with({"name": "Test Team"})
                    mock_func.assert_called_once()


class TestConvenienceDecorators:
    """Test convenience decorator shortcuts."""

    def test_user_endpoint_decorator(self):
        """Test that user_endpoint is equivalent to api_endpoint with correct params."""
        with patch.dict(
            "sys.modules",
            {
                "flask": Mock(),
                "flask.g": Mock(),
                "CTFd.utils.user": Mock(),
                "CTFd.utils.decorators": Mock(),
            },
        ):
            import importlib
            from ...middleware import auth as decorators

            importlib.reload(decorators)

            mock_g = Mock()
            mock_get_current_user = Mock()
            mock_user = Mock(id=1)
            mock_get_current_user.return_value = mock_user
            mock_authed_only = Mock(side_effect=lambda f: f)

            with patch.object(decorators, "g", mock_g):
                with patch.object(decorators, "get_current_user", mock_get_current_user):
                    with patch.object(decorators, "authed_only", mock_authed_only):
                        mock_func = Mock(return_value={"success": True})
                        decorated_func = decorators.user_endpoint()(mock_func)

                        decorated_func()

                        assert mock_g.user == mock_user
                        mock_func.assert_called_once()

    def test_admin_endpoint_decorator(self):
        """Test that admin_endpoint uses admin requirements."""
        with patch.dict(
            "sys.modules",
            {
                "flask": Mock(),
                "flask.g": Mock(),
                "CTFd.utils.user": Mock(),
                "CTFd.utils.decorators": Mock(),
            },
        ):
            import importlib
            from ...middleware import auth as decorators

            importlib.reload(decorators)

            mock_g = Mock()
            mock_get_current_user = Mock()
            mock_user = Mock(id=1)
            mock_get_current_user.return_value = mock_user
            mock_admins_only = Mock(side_effect=lambda f: f)

            with patch.object(decorators, "g", mock_g):
                with patch.object(decorators, "get_current_user", mock_get_current_user):
                    with patch.object(decorators, "admins_only", mock_admins_only):
                        mock_func = Mock(return_value={"success": True})
                        decorated_func = decorators.admin_endpoint()(mock_func)

                        decorated_func()

                        mock_admins_only.assert_called_once()
                        mock_func.assert_called_once()

    def test_public_endpoint_decorator(self):
        """Test that public_endpoint requires no authentication."""
        with patch.dict(
            "sys.modules",
            {"flask": Mock(), "flask.g": Mock(), "CTFd.utils.decorators": Mock()},
        ):
            import importlib
            from ...middleware import auth as decorators

            importlib.reload(decorators)

            mock_func = Mock(return_value={"success": True})
            decorated_func = decorators.public_endpoint()(mock_func)

            result = decorated_func()

            mock_func.assert_called_once()
            assert result == {"success": True}


class TestErrorHandling:
    """Test error handling integration."""

    def test_handle_exceptions_decorator_catches_and_converts_errors(self):
        """Test that handle_exceptions decorator properly catches and converts exceptions."""
        with patch.dict("sys.modules", {"core.middleware.error_handler": Mock()}):
            import importlib
            from ...middleware import error_handler

            importlib.reload(error_handler)

            mock_error_response = Mock()
            mock_error_response.return_value = (
                {"success": False, "errors": {"not_found": "Test not found"}},
                404,
            )

            with patch.object(error_handler, "error_response", mock_error_response):

                def error_func():
                    from ...exceptions import NotFoundError

                    raise NotFoundError("Test not found")

                decorated_func = error_handler.handle_exceptions(error_func)

                result, status_code = decorated_func()

                assert result["success"] is False
                assert status_code == 404
                assert "not_found" in result["errors"]
                mock_error_response.assert_called_once()

    def test_decorators_preserve_function_metadata(self):
        """Test that decorators preserve function names and docstrings."""
        with patch.dict(
            "sys.modules",
            {
                "flask": Mock(),
                "flask.g": Mock(),
                "flask.request": Mock(),
                "CTFd.utils.user": Mock(),
                "CTFd.utils.decorators": Mock(),
            },
        ):
            import importlib
            from ...middleware import auth as decorators

            importlib.reload(decorators)

            def original_func():
                """Original docstring."""
                return {"success": True}

            api_decorated = decorators.api_endpoint()(original_func)
            assert api_decorated.__name__ == "original_func"

            user_decorated = decorators.user_endpoint()(original_func)
            assert user_decorated.__name__ == "original_func"


pytestmark = [pytest.mark.middleware]
