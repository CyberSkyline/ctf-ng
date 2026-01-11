# Copyright 2025 Cyber Skyline

# Permission is hereby granted, free of charge, to any person obtaining a 
# copy of this software and associated documentation files (the “Software”), 
# to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS 
# IN THE SOFTWARE.
import pytest
from attrs import define, field
from cyber_skyline.chall_parser.compose.validators import validate_tabler_icon, validate_compose_name_pattern, validate_template_evals
from cyber_skyline.chall_parser.template import Template
from cyber_skyline.chall_parser.compose.types import ComposeResourceName

@define
class MockChallengeWithIcon:
    """Mock class for testing icon validation."""
    icon: str | None = field(validator=validate_tabler_icon)

@define
class MockVariableWithTemplate:
    """Mock class for testing template validation."""
    template: Template = field(validator=validate_template_evals)

class TestTablerIconValidator:
    def test_valid_icons_with_tb_prefix(self):
        """Test that valid Tabler icons with Tb prefix pass validation."""
        valid_icons = ['TbShield', 'TbLock', 'TbGlobe', 'TbTerminal', 'TbStar']
        
        for icon in valid_icons:
            challenge = MockChallengeWithIcon(icon=icon)
            assert challenge.icon == icon

    def test_none_icon(self):
        """Test that None is allowed for optional icon fields."""
        challenge = MockChallengeWithIcon(icon=None)
        assert challenge.icon is None

    def test_invalid_icon_without_tb_prefix(self):
        """Test that icons without Tb prefix are rejected."""
        invalid_icons = ['shield', 'lock', 'globe', 'tabler-shield', 'ti-lock']
        
        for icon in invalid_icons:
            with pytest.raises(ValueError, match="must start with 'Tb' prefix"):
                MockChallengeWithIcon(icon=icon)

    def test_invalid_icon_type(self):
        """Test that non-string values are rejected."""
        with pytest.raises(ValueError, match="Icon name must be a string"):
            MockChallengeWithIcon(icon=123) # type: ignore

    def test_empty_string_icon(self):
        """Test that empty strings are rejected."""
        with pytest.raises(ValueError, match="must start with 'Tb' prefix"):
            MockChallengeWithIcon(icon="")

    def test_case_sensitive_validation(self):
        """Test that validation is case sensitive."""
        # These should fail because they don't have proper "Tb" prefix
        invalid_cases = ['tb', 'TB', 'tB', 'tbShield']
        
        for icon in invalid_cases:
            with pytest.raises(ValueError, match="must start with 'Tb' prefix"):
                MockChallengeWithIcon(icon=icon)

    def test_tb_prefix_with_additional_text(self):
        """Test that icons starting with Tb followed by other text are valid."""
        valid_icons = [
            'Tb',  # Just the prefix
            'TbIcon',
            'TbShieldCheck',
            'TbLockOpen',
            'TbSomeVeryLongIconName'
        ]
        
        for icon in valid_icons:
            challenge = MockChallengeWithIcon(icon=icon)
            assert challenge.icon == icon

class TestComposeNameValidator:
    def test_valid_compose_names(self):
        """Test that valid compose resource names pass validation."""
        valid_dict: dict[ComposeResourceName, str] = {
            ComposeResourceName("web-service"): "value",
            ComposeResourceName("db_service"): "value", 
            ComposeResourceName("service123"): "value",
            ComposeResourceName("my.service"): "value",
            ComposeResourceName("a"): "value",
        }
        
        class MockInstance:
            pass
        
        class MockAttribute:
            name = "test_field"
        
        for key in valid_dict.keys():
            validate_compose_name_pattern(MockInstance(), MockAttribute(), key)

    def test_invalid_compose_names(self):
        """Test that invalid compose resource names are rejected."""
        invalid_cases = [
            {ComposeResourceName("service with spaces"): "value"},
            {ComposeResourceName("service@special"): "value"},
            {ComposeResourceName("service/slash"): "value"},
            {ComposeResourceName(""): "value"},
        ]
        
        class MockInstance:
            pass
        
        class MockAttribute:
            name = "test_field"
        
        for invalid_dict in invalid_cases:
            for key in invalid_dict.keys():
                with pytest.raises(ValueError, match="must match pattern"):
                    validate_compose_name_pattern(MockInstance(), MockAttribute(), key)

class TestTemplateValidator:
    def test_valid_template(self):
        """Test that valid templates pass validation."""
        template = Template("fake.name()", "test_var")
        variable = MockVariableWithTemplate(template=template)
        assert variable.template == template

    def test_invalid_template_type(self):
        """Test that non-Template objects are rejected."""
        with pytest.raises(ValueError, match="Expected Template object"):
            MockVariableWithTemplate(template="not a template") # type: ignore

    def test_template_eval_error(self):
        """Test that templates with evaluation errors are caught."""
        bad_template = Template("invalid_function()", "test_var")
        with pytest.raises(ValueError, match="Template evaluation failed"):
            MockVariableWithTemplate(template=bad_template)
