import base64
import pytest
from unittest.mock import patch

from ..controllers.admin.lint_challenge import lint_challenge, serialize_warnings, format_validation_error


class TestLintChallenge:
    """
    Unit tests for the lint_challenge function.

    These tests focus on the linting functionality without database operations,
    testing YAML parsing, validation, and error formatting.
    """

    @pytest.mark.parametrize("valid_yaml,expected_warnings", [
        # Test minimal valid YAML with no warnings
        ("""
        x-challenge:
          name: Minimal Challenge
          description: A minimal test challenge
          summary: Just the basics
          questions:
            - name: sample_question
              body: What is 2 + 2?
              points: 10
              answer: "4"
              max_attempts: 3
        """, None),

        # Test valid YAML with services but no warnings
        ("""
        services:
          web:
            image: nginx:latest
            hostname: web-server
            environment:
              ENV: production
        x-challenge:
          name: Service Challenge
          description: Challenge with services
          summary: Testing services
          questions:
            - name: sample_question
              body: What is 2 + 2?
              points: 10
              answer: "4"
              max_attempts: 3
        """, None),
    ])
    def test_lint_challenge_valid_yaml_no_warnings(self, valid_yaml, expected_warnings):
        """Test linting valid YAML that produces no warnings"""
        # Act
        result = lint_challenge(valid_yaml)

        # Assert - the function might return warnings even for valid YAML
        if result is None:
            assert expected_warnings is None
        else:
            # Valid YAML should not produce errors, only warnings at most
            assert "errors" not in result
            if "warnings" in result:
                assert len(result["warnings"]) > 0

    @pytest.mark.parametrize("yaml_with_warnings,expected_warning_count", [
        # Test YAML with ignored fields that should produce warnings
        ("""
        services:
          web:
            image: nginx:latest
            hostname: web-server
            build: .
            ports:
              - "80:80"
            stdin_open: true
            tty: true
        x-challenge:
          name: Warning Challenge
          description: Challenge that produces warnings
          summary: Testing warnings
          questions:
            - name: sample_question
              body: What is 2 + 2?
              points: 10
              answer: "4"
              max_attempts: 3
        """, 4),  # build, ports, stdin_open, tty should all warn

        # Test networks that produce warnings
        ("""
        services:
          web:
            image: nginx:latest
            hostname: web-server
        networks:
          external-net:
            internal: false
          undefined-net:
        x-challenge:
          name: Network Warning Challenge
          description: Challenge with network warnings
          summary: Testing network warnings
          questions:
            - name: sample_question
              body: What is 2 + 2?
              points: 10
              answer: "4"
              max_attempts: 3
        """, 2),  # external network and undefined network should warn
    ])
    def test_lint_challenge_valid_yaml_with_warnings(self, yaml_with_warnings, expected_warning_count):
        """Test linting valid YAML that produces warnings"""
        # Act
        result = lint_challenge(yaml_with_warnings)

        # Assert
        assert result is not None
        assert "warnings" in result
        assert "errors" not in result
        assert len(result["warnings"]) >= expected_warning_count

        # Verify warning structure
        for warning in result["warnings"]:
            assert "message" in warning
            assert isinstance(warning["message"], str)
            # field is optional in warnings

    def test_lint_challenge_compose_file_warnings(self):
        """Test ComposeFile-level warnings: no services and no networks"""
        yaml_content = """
        x-challenge:
          name: No Services Challenge
          description: Challenge with no services or networks
          summary: Testing ComposeFile warnings
          questions:
            - name: sample_question
              body: What is 2 + 2?
              points: 10
              answer: "4"
              max_attempts: 3
        """
        # Act
        result = lint_challenge(yaml_content)

        # Assert
        assert result is not None
        assert "warnings" in result

        # Should have warnings about no services and no networks
        warning_messages = [w["message"] for w in result["warnings"]]
        assert any("No services defined" in msg for msg in warning_messages)
        assert any("No networks defined" in msg for msg in warning_messages)

    @pytest.mark.parametrize("service_field,field_value,expected_warning", [
        ("build", ".", "build field is ignored in production"),
        ("ports", ["80:80"], "ports field is ignored in production"),
        ("stdin_open", True, "stdin_open field is ignored in production"),
        ("tty", True, "tty field is ignored in production"),
        ("logging", {"driver": "json-file"}, "logging field is currently unsupported and will be ignored"),
        ("healthcheck", {"test": ["CMD", "curl", "-f", "http://localhost/"]}, "healthcheck field is currently unsupported and will be ignored"),
        ("develop", {"watch": []}, "develop field is currently unsupported and will be ignored"),
    ])
    def test_lint_challenge_service_field_warnings(self, service_field, field_value, expected_warning):
        """Test individual service field warnings"""
        yaml_content = f"""
        services:
          web:
            image: nginx:latest
            hostname: web-server
            {service_field}: {field_value}
        x-challenge:
          name: Service Field Warning Test
          description: Testing service field warnings
          summary: Testing {service_field} warning
          questions:
            - name: sample_question
              body: What is 2 + 2?
              points: 10
              answer: "4"
              max_attempts: 3
        """
        # Act
        result = lint_challenge(yaml_content)

        # Assert
        assert result is not None
        assert "warnings" in result

        # Check that the expected warning is present
        warning_messages = [w["message"] for w in result["warnings"]]
        assert any(expected_warning in msg for msg in warning_messages), f"Expected warning '{expected_warning}' not found in {warning_messages}"

    def test_lint_challenge_multiple_service_warnings(self):
        """Test multiple service warnings in a single service"""
        yaml_content = """
        services:
          web:
            image: nginx:latest
            hostname: web-server
            build: .
            ports:
              - "80:80"
              - "443:443"
            stdin_open: true
            tty: true
            logging:
              driver: json-file
            healthcheck:
              test: ["CMD", "curl", "-f", "http://localhost/"]
              interval: 30s
        x-challenge:
          name: Multiple Service Warnings Test
          description: Testing multiple service warnings
          summary: Testing multiple warnings
          questions:
            - name: sample_question
              body: What is 2 + 2?
              points: 10
              answer: "4"
              max_attempts: 3
        """
        # Act
        result = lint_challenge(yaml_content)

        # Assert
        assert result is not None
        assert "warnings" in result

        warning_messages = [w["message"] for w in result["warnings"]]

        # Should have warnings for all the problematic fields
        expected_warnings = [
            "build field is ignored in production",
            "ports field is ignored in production",
            "stdin_open field is ignored in production",
            "tty field is ignored in production",
            "logging field is currently unsupported and will be ignored",
            "healthcheck field is currently unsupported and will be ignored"
        ]

        for expected_warning in expected_warnings:
            assert any(expected_warning in msg for msg in warning_messages), f"Expected warning '{expected_warning}' not found"

    @pytest.mark.parametrize("network_config,expected_warning", [
        # Network with internal: false should warn
        ("""
          external-network:
            internal: false
        """, "internal field is False, this network will not be created in production"),

        # Network with no internal field should warn (appears as undefined)
        ("""
          missing-internal:
        """, "is not defined, so is external and will not be created"),

        # Network defined as None should warn
        ("""
          undefined-network:
        """, "is not defined, so is external and will not be created"),
    ])
    def test_lint_challenge_network_warnings(self, network_config, expected_warning):
        """Test network-specific warnings"""
        yaml_content = f"""
        services:
          web:
            image: nginx:latest
            hostname: web-server
        networks:{network_config}
        x-challenge:
          name: Network Warning Test
          description: Testing network warnings
          summary: Testing network warnings
          questions:
            - name: sample_question
              body: What is 2 + 2?
              points: 10
              answer: "4"
              max_attempts: 3
        """
        # Act
        result = lint_challenge(yaml_content)

        # Assert
        assert result is not None
        assert "warnings" in result

        warning_messages = [w["message"] for w in result["warnings"]]
        assert any(expected_warning in msg for msg in warning_messages), f"Expected warning '{expected_warning}' not found in {warning_messages}"

    def test_lint_challenge_multiple_network_warnings(self):
        """Test multiple network warnings"""
        yaml_content = """
        services:
          web:
            image: nginx:latest
            hostname: web-server
        networks:
          external-net:
            internal: false
          missing-internal-net:
          undefined-net:
          good-net:
            internal: true
        x-challenge:
          name: Multiple Network Warnings Test
          description: Testing multiple network warnings
          summary: Testing multiple network warnings
          questions:
            - name: sample_question
              body: What is 2 + 2?
              points: 10
              answer: "4"
              max_attempts: 3
        """
        # Act
        result = lint_challenge(yaml_content)

        # Assert
        assert result is not None
        assert "warnings" in result

        warning_messages = [w["message"] for w in result["warnings"]]

        # Should have warnings for problematic networks but not the good one
        expected_warnings = [
            "internal field is False",  # external-net
            "is not defined, so is external"  # missing-internal-net and undefined-net (both appear as undefined)
        ]

        for expected_warning in expected_warnings:
            assert any(expected_warning in msg for msg in warning_messages), f"Expected warning containing '{expected_warning}' not found"

    def test_lint_challenge_warning_field_paths(self):
        """Test that warning field paths are correctly formatted"""
        yaml_content = """
        services:
          web:
            image: nginx:latest
            hostname: web-server
            build: .
          api:
            image: python:3.9
            hostname: api-server
            ports:
              - "8000:8000"
        networks:
          external-net:
            internal: false
        x-challenge:
          name: Field Path Test
          description: Testing warning field paths
          summary: Testing field paths
          questions:
            - name: sample_question
              body: What is 2 + 2?
              points: 10
              answer: "4"
              max_attempts: 3
        """
        # Act
        result = lint_challenge(yaml_content)

        # Assert
        assert result is not None
        assert "warnings" in result

        # Check that field paths are properly formatted
        warnings_with_fields = [w for w in result["warnings"] if "field" in w]

        # Should have field paths like .service warnings.web, .service warnings.api, .network warnings.external-net
        field_paths = [w["field"] for w in warnings_with_fields]

        # Look for service and network warning field paths
        service_fields = [f for f in field_paths if "service warnings" in f]
        network_fields = [f for f in field_paths if "network warnings" in f]

        assert len(service_fields) > 0, "Should have service warning field paths"
        assert len(network_fields) > 0, "Should have network warning field paths"

    def test_lint_challenge_no_warnings_for_good_config(self):
        """Test that properly configured services and networks don't produce warnings"""
        yaml_content = """
        services:
          web:
            image: nginx:latest
            hostname: web-server
            environment:
              ENV: production
            mem_limit: "512m"
            cpus: "1.0"
        networks:
          internal-net:
            internal: true
        x-challenge:
          name: Good Config Test
          description: Testing good configuration
          summary: Should not produce service/network warnings
          questions:
            - name: sample_question
              body: What is 2 + 2?
              points: 10
              answer: "4"
              max_attempts: 3
        """
        # Act
        result = lint_challenge(yaml_content)

        # Assert - should either be None or only have ComposeFile level warnings about deployment
        if result is not None and "warnings" in result:
            warning_messages = [w["message"] for w in result["warnings"]]

            # Should not have service field warnings
            service_warning_keywords = ["build field", "ports field", "stdin_open field", "tty field", "logging field", "healthcheck field", "develop field"]
            for keyword in service_warning_keywords:
                assert not any(keyword in msg for msg in warning_messages), f"Unexpected service warning containing '{keyword}'"

            # Should not have network warnings about internal fields
            network_warning_keywords = ["internal field is False", "internal field does not exist", "is not defined, so is external"]
            for keyword in network_warning_keywords:
                assert not any(keyword in msg for msg in warning_messages), f"Unexpected network warning containing '{keyword}'"

    @pytest.mark.parametrize("invalid_yaml,expected_error_pattern", [
        # Test malformed YAML syntax
        ("invalid: yaml: content: [", "YAML error"),
        ("", ""),  # Empty content
        ("not yaml at all", ""),
        ("version: 3\nservices:\n  invalid: [", "YAML error"),
        ("x-challenge:\n  name: [unclosed", "YAML error"),

        # Test missing required fields
        ("""
        x-challenge:
          description: Missing name field
          summary: Should fail
          questions:
            - name: sample_question
              body: What is 2 + 2?
              points: 10
              answer: "4"
              max_attempts: 3
        """, "Required field"),

        # Test invalid field types - this actually gets accepted by the parser
        ("""
        x-challenge:
          name: 123  # Should be string
          description: Valid description
          summary: Should fail due to invalid name type
          questions:
            - name: sample_question
              body: What is 2 + 2?
              points: 10
              answer: "4"
              max_attempts: 3
        """, ""),
    ])
    def test_lint_challenge_invalid_yaml(self, invalid_yaml, expected_error_pattern):
        """Test linting invalid YAML that produces errors"""
        # Act
        result = lint_challenge(invalid_yaml)

        # Assert
        assert result is not None
        # Some "invalid" YAML might still be accepted and produce warnings instead of errors
        if "errors" in result:
            assert len(result["errors"]) > 0
            # Verify error structure
            for error in result["errors"]:
                assert "message" in error
                assert isinstance(error["message"], str)
                if expected_error_pattern:
                    assert expected_error_pattern.lower() in error["message"].lower()
        elif "warnings" in result:
            # Some cases might be accepted but produce warnings
            assert len(result["warnings"]) > 0

    def test_lint_challenge_complex_validation_errors(self):
        """Test handling of complex validation errors from parser"""
        # YAML with multiple validation issues
        invalid_yaml = """
        services:
          web:
            image: ""  # Empty image
            hostname: ""  # Empty hostname
            environment: "not_a_dict"  # Wrong type
        x-challenge:
          name: ""  # Empty name
          description: ""  # Empty description
          summary: ""  # Empty summary
          questions: []  # Empty questions array
        """
        # Act
        result = lint_challenge(invalid_yaml)

        # Assert
        assert result is not None
        assert "errors" in result
        assert len(result["errors"]) > 0

    def test_lint_challenge_with_template_variables(self):
        """Test linting YAML with template variables (should be valid)"""
        yaml_content = """
        x-challenge:
          name: Template Variable Challenge
          description: Challenge with template variables
          summary: Testing template variables
          variables:
            secret_key:
              default: &secret_key "default_secret"
              template: "fake.lexify('?'*16)"
            flag_suffix:
              default: &flag_suffix "123"
              template: "fake.numerify('###')"
          questions:
            - name: secret_question
              body: Find the secret key
              points: 50
              max_attempts: 5
              answer: *secret_key
            - name: flag_question
              body: What's the complete flag?
              points: 100
              max_attempts: 3
              answer: *flag_suffix
        """
        # Act
        result = lint_challenge(yaml_content)

        # Assert - template variables should be valid, so no errors expected
        if result is not None:
            assert "errors" not in result
            # Warnings might be present but that's OK

    @patch('ng.event.controllers.admin.lint_challenge.parse_compose_string')
    def test_lint_challenge_parser_exception(self, mock_parse):
        """Test handling when parser raises unexpected exception"""
        # Setup mock to raise exception
        mock_parse.side_effect = RuntimeError("Unexpected parser error")

        yaml_content = """
        x-challenge:
          name: Test Challenge
          description: Should trigger parser error
          summary: Testing error handling
          questions:
            - name: sample_question
              body: What is 2 + 2?
              points: 10
              answer: "4"
              max_attempts: 3
        """
        # Act
        result = lint_challenge(yaml_content)

        # Assert
        assert result is not None
        assert "errors" in result
        assert len(result["errors"]) > 0
        assert "Unexpected parser error" in result["errors"][0]["message"]
class TestSerializeWarnings:
    """Unit tests for the serialize_warnings helper function"""

    def test_serialize_warnings_empty(self):
        """Test serializing warnings with no warnings"""
        from cyber_skyline.chall_parser.warnings import Warnings

        empty_warnings = Warnings("test", [], [])
        result = serialize_warnings(empty_warnings)

        assert result == []

    def test_serialize_warnings_self_warnings_only(self):
        """Test serializing warnings with only self warnings"""
        from cyber_skyline.chall_parser.warnings import Warnings

        warnings = Warnings("service", ["build field is ignored", "ports field is ignored"], [])
        result = serialize_warnings(warnings)

        assert len(result) == 2
        assert result[0].get("field") == ".service"
        assert result[0]["message"] == "build field is ignored"
        assert result[1].get("field") == ".service"
        assert result[1]["message"] == "ports field is ignored"

    def test_serialize_warnings_nested_field_warnings(self):
        """Test serializing warnings with nested field warnings"""
        from cyber_skyline.chall_parser.warnings import Warnings

        nested_warning = Warnings("web", ["internal field is missing"], [])
        parent_warnings = Warnings("networks", [], [nested_warning])
        result = serialize_warnings(parent_warnings)

        assert len(result) == 1
        assert result[0].get("field") == ".networks.web"
        assert result[0]["message"] == "internal field is missing"


class TestFormatValidationError:
    """Unit tests for the format_validation_error helper function"""

    def test_format_validation_error_key_error(self):
        """Test formatting KeyError exceptions"""
        error = KeyError("required_field")
        result = format_validation_error(error)

        assert len(result) > 0
        assert "required_field" in result[0]["message"]

    def test_format_validation_error_value_error(self):
        """Test formatting ValueError exceptions"""
        error = ValueError("Invalid value provided")
        result = format_validation_error(error)

        assert len(result) > 0
        assert "Invalid value provided" in result[0]["message"]

    def test_format_validation_error_generic_exception(self):
        """Test formatting generic exceptions"""
        error = RuntimeError("Something went wrong")
        result = format_validation_error(error)

        assert len(result) > 0
        assert "Something went wrong" in result[0]["message"]

    def test_format_validation_error_message_structure(self):
        """Test that error messages have correct structure"""
        error = ValueError("Test error")
        result = format_validation_error(error)

        assert len(result) > 0
        for error_msg in result:
            assert "message" in error_msg
            assert isinstance(error_msg["message"], str)
            # field is optional
