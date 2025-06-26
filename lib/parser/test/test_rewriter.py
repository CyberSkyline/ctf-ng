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
import yaml
import io
from yaml import BaseLoader
from cyber_skyline.chall_parser.rewriter import Rewriter, Template

class TestRewriter:
    def test_rewriter_initialization(self):
        """Test that Rewriter initializes correctly."""
        yaml_content = "test: value"
        loader = BaseLoader(yaml_content)
        rewriter = Rewriter(loader)
        assert rewriter.loader == loader
        assert rewriter.anchors == {}

    def test_rewrite_variable_no_anchor_in_default(self):
        """Test that rewriter fails when default has no anchor."""
        yaml_content = """
variables:
  bad_var:
    template: "fake.word()"
    default: "no_anchor_value"  # missing anchor
"""
        loader = BaseLoader(yaml_content)
        rewriter = Rewriter(loader)
        
        # This should raise an error because anchor is required for rewriting
        with pytest.raises(ValueError, match="Default value must have an anchor"):
            list(rewriter.rewrite())

    def test_rewrite_without_variables_section(self):
        """Test rewriting YAML without variables section."""
        yaml_content = """
services:
  web:
    image: nginx
"""
        loader = BaseLoader(yaml_content)
        rewriter = Rewriter(loader)
        events = list(rewriter.rewrite())
        # Should pass through all events unchanged
        assert len(events) > 0

    def test_rewrite_empty_variables_section(self):
        """Test rewriting YAML with empty variables section."""
        yaml_content = """
variables:
services:
  web:
    image: nginx
"""
        loader = BaseLoader(yaml_content)
        rewriter = Rewriter(loader)
        events = list(rewriter.rewrite())
        # Should handle empty variables section
        assert len(events) > 0

    def test_resolve_alias_not_found(self):
        """Test alias resolution when anchor is not found."""
        yaml_content = "test: value"
        loader = BaseLoader(yaml_content)
        rewriter = Rewriter(loader)
        
        # Create a mock alias event
        from yaml import AliasEvent
        alias = AliasEvent(anchor="unknown")
        result = rewriter.resolve_alias(alias)
        assert result == alias

    def test_resolve_alias_invalid_type(self):
        """Test alias resolution when anchor points to non-scalar."""
        yaml_content = "test: value"
        loader = BaseLoader(yaml_content)
        rewriter = Rewriter(loader)
        
        # Mock an anchor that points to something other than ScalarEvent
        from yaml import MappingStartEvent, AliasEvent
        non_scalar_event = MappingStartEvent(anchor=None, tag=None, implicit=True)
        rewriter.anchors["bad_anchor"] = non_scalar_event # type: ignore
        
        alias = AliasEvent(anchor="bad_anchor")
        with pytest.raises(ValueError, match="does not point to a valid scalar event"):
            rewriter.resolve_alias(alias)

class TestTemplate:
    def test_template_initialization(self):
        """Test Template object initialization."""
        template = Template("fake.name()", "test_var")
        assert template.eval_str == "fake.name()"
        assert template.parent_variable == "test_var"

    def test_template_eval_success(self):
        """Test successful template evaluation."""
        template = Template("fake.name()", "test_var")
        result = template.eval()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_template_eval_empty(self):
        """Test template evaluation with empty string."""
        template = Template("", "test_var")
        result = template.eval()
        assert result is None

    def test_template_eval_invalid_syntax(self):
        """Test template evaluation with invalid Python syntax."""
        template = Template("fake.invalid_function(", "test_var")  # missing closing paren
        with pytest.raises(ValueError, match="Invalid template"):
            template.eval()

    def test_template_eval_nonexistent_function(self):
        """Test template evaluation with non-existent function."""
        template = Template("fake.nonexistent_method()", "test_var")
        with pytest.raises(ValueError, match="Invalid template"):
            template.eval()

    def test_template_eval_invalid_code(self):
        """Test template evaluation with malicious/invalid code."""
        template = Template("import os; os.system('echo bad')", "test_var")
        with pytest.raises(ValueError, match="Invalid template"):
            template.eval()

    def test_template_from_yaml_invalid_node_type(self):
        """Test Template.from_yaml with invalid node type."""
        from yaml.nodes import ScalarNode
        node = ScalarNode(tag="tag", value="value")
        with pytest.raises(yaml.YAMLError, match="Template must be a mapping"):
            Template.from_yaml(None, node)

    def test_template_from_yaml_missing_eval_key(self):
        """Test Template.from_yaml with missing 'eval' key."""
        from yaml.nodes import MappingNode, ScalarNode
        
        node = MappingNode(tag="tag", value=[
            (ScalarNode(tag="tag", value="variable"), ScalarNode(tag="tag", value="test"))
        ])
        with pytest.raises(yaml.YAMLError, match="Template must have a 'eval' key"):
            Template.from_yaml(None, node)

    def test_template_from_yaml_missing_variable_key(self):
        """Test Template.from_yaml with missing 'variable' key."""
        from yaml.nodes import MappingNode, ScalarNode
        
        node = MappingNode(tag="tag", value=[
            (ScalarNode(tag="tag", value="eval"), ScalarNode(tag="tag", value="fake.name()"))
        ])
        with pytest.raises(yaml.YAMLError, match="Template must have a 'variable' key"):
            Template.from_yaml(None, node)

    def test_template_from_yaml_missing_both_keys(self):
        """Test Template.from_yaml with both required keys missing."""
        from yaml.nodes import MappingNode, ScalarNode
        
        node = MappingNode(tag="tag", value=[
            (ScalarNode(tag="tag", value="other"), ScalarNode(tag="tag", value="value"))
        ])
        with pytest.raises(yaml.YAMLError, match="Template must have a 'eval' key"):
            Template.from_yaml(None, node)

    def test_template_yaml_roundtrip(self):
        """Test Template YAML serialization and deserialization."""
        template = Template("fake.name()", "test_var")
        
        # Test to_yaml
        dumper = yaml.Dumper(io.StringIO())
        node = Template.to_yaml(dumper, template)
        assert node.tag == "!template"
        
        # Test from_yaml
        reconstructed = Template.from_yaml(None, node)
        assert reconstructed.eval_str == template.eval_str
        assert reconstructed.parent_variable == template.parent_variable

    def test_template_from_yaml_with_extra_keys(self):
        """Test Template.from_yaml ignores extra keys but requires eval and variable."""
        from yaml.nodes import MappingNode, ScalarNode
        
        node = MappingNode(tag="tag", value=[
            (ScalarNode(tag="tag", value="eval"), ScalarNode(tag="tag", value="fake.name()")),
            (ScalarNode(tag="tag", value="variable"), ScalarNode(tag="tag", value="test_var")),
            (ScalarNode(tag="tag", value="extra"), ScalarNode(tag="tag", value="ignored"))
        ])
        
        template = Template.from_yaml(None, node)
        assert template.eval_str == "fake.name()"
        assert template.parent_variable == "test_var"

class TestRewriterIntegration:
    def test_rewrite_valid_variable_with_alias(self):
        """Test complete rewriting workflow with valid variable."""
        yaml_content = """
variables:
  flag:
    template: "fake.bothify('CTF{????-####}')"
    default: &flag_var "default_flag"
services:
  app:
    environment:
      FLAG: *flag_var
"""
        loader = BaseLoader(yaml_content)
        rewriter = Rewriter(loader)
        
        events = list(rewriter.rewrite())
        assert len(events) > 0
        
        # The events should contain the rewritten template
        event_values = [e.value if hasattr(e, 'value') else str(e) for e in events] # type: ignore
        assert 'variables' in event_values