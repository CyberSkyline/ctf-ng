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
import tempfile
from pathlib import Path
from typer.testing import CliRunner
from chall_check.cli import app
import pathlib

runner = CliRunner()

class TestCLI:
    def test_validate_complex_challenge(self):
        """Test validating a complex challenge compose file."""

        chall_file = pathlib.Path(__file__).parent.resolve() / "../../../examples/complex_chall.yml"
        result = runner.invoke(app, ["validate", str(chall_file)])
        assert result.exit_code == 0
        assert "Successfully validated" in result.stdout


    def test_validate_valid_file(self):
        """Test validating a valid compose file."""
        yaml_content = """
x-challenge:
  name: CLI Test Challenge
  description: Testing CLI validation
  icon: TbTest
  questions:
    - name: flag
      body: What is the flag?
      points: 100
      answer: CTF\\{test\\}
      max_attempts: 3
services:
  web:
    image: nginx:latest
    hostname: web-server
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(yaml_content)
            temp_path = Path(f.name)
        
        try:
            result = runner.invoke(app, ["validate", str(temp_path)])
            assert result.exit_code == 0
            assert "Successfully validated" in result.stdout
        finally:
            temp_path.unlink()

    def test_validate_invalid_file(self):
        """Test validating an invalid compose file."""
        yaml_content = """
x-challenge:
  name: Invalid Challenge
  # missing description and questions
services:
  web:
    image: nginx:latest
    # missing hostname
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(yaml_content)
            temp_path = Path(f.name)
        
        try:
            result = runner.invoke(app, ["validate", str(temp_path)])
            assert result.exit_code == 1
            assert "Validation Failed" in result.stdout
        finally:
            temp_path.unlink()

    def test_validate_nonexistent_file(self):
        """Test validating a non-existent file."""
        result = runner.invoke(app, ["validate", "nonexistent.yml"])
        assert result.exit_code == 1
        assert "File not found" in result.stdout

    def test_check_valid_file(self):
        """Test check command with valid file."""
        yaml_content = """
x-challenge:
  name: Check Test
  description: Testing check command
  questions: []
services:
  app:
    image: test:latest
    hostname: test-host
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(yaml_content)
            temp_path = Path(f.name)
        
        try:
            result = runner.invoke(app, ["check", str(temp_path)])
            assert result.stdout.strip() == ""  # Silent success
            assert result.stderr.strip() == ""  # No errors
            assert result.exit_code == 0
        finally:
            temp_path.unlink()

    def test_check_invalid_file(self):
        """Test check command with invalid file."""
        result = runner.invoke(app, ["check", "nonexistent.yml"])
        assert result.exit_code == 1
        assert result.stdout.strip() == ""  # Silent failure

    def test_info_specific_field(self):
        """Test info command with specific field."""
        yaml_content = """
x-challenge:
  name: Field Test Challenge
  description: Testing field extraction
  questions: []
services:
  app:
    image: test:latest
    hostname: test-host
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(yaml_content)
            temp_path = Path(f.name)
        
        try:
            result = runner.invoke(app, ["info", str(temp_path), "--field", "name"])
            assert result.exit_code == 0
            assert "Field Test Challenge" in result.stdout
        finally:
            temp_path.unlink()

    def test_render_command(self):
        """Test render command."""
        yaml_content = """
x-challenge:
  name: Template Test Challenge
  description: Testing template evaluation
  questions: []
  variables:
    test_var:
      template: "fake.word()"
      default: &test_val "default_word"
services:
  app:
    image: test:latest
    hostname: test-host
    environment:
      TEST_VALUE: *test_val
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(yaml_content)
            temp_path = Path(f.name)
        
        try:
            result = runner.invoke(app, ["render", str(temp_path)])
            assert result.exit_code == 0
            assert "test_var" in result.stdout
            assert "fake.word()" in result.stdout
        finally:
            temp_path.unlink()

    def test_version_flag(self):
        """Test version flag."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "chall-check version" in result.stdout

    def test_help_command(self):
        """Test help command."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "CTF Challenge Parser" in result.stdout

    def test_validate_with_different_formats(self):
        """Test validate command with different output formats."""
        yaml_content = """
x-challenge:
  name: Format Test
  description: Testing output formats
  questions: []
services:
  app:
    image: test:latest
    hostname: test-host
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(yaml_content)
            temp_path = Path(f.name)
        
        try:
            # Test JSON format
            result = runner.invoke(app, ["validate", str(temp_path), "--format", "json"])
            assert result.exit_code == 0
            
            # Test YAML format
            result = runner.invoke(app, ["validate", str(temp_path), "--format", "yaml"])
            assert result.exit_code == 0
            
        finally:
            temp_path.unlink()

    def test_validate_with_markdown(self):
        """Test validate command with different output formats."""
        yaml_content = """
x-challenge:
  name: Format Test
  description: Testing output formats
  questions: []
services:
  app:
    image: test:latest
    hostname: test-host
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(yaml_content)
            temp_path = Path(f.name)
        
        try:
            # Test Markdown format
            result = runner.invoke(app, ["validate", str(temp_path), "--format", "md"])
            assert result.exit_code == 0
            
        finally:
            temp_path.unlink()


    def test_validate_with_wrong_challenge_key(self, caplog):
        """Test validate command with different output formats."""
        yaml_content = """
scan-challenge:
  name: Format Test
  description: Testing output formats
  questions: []
services:
  app:
    image: test:latest
    hostname: test-host
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(yaml_content)
            temp_path = Path(f.name)
        
        try:
            result = runner.invoke(app, ["validate", str(temp_path)])
            assert result.exit_code == 1
            assert "Validation Failed" in result.stdout
            assert "Required field 'x-challenge' missing" in result.stdout
            
        finally:
            temp_path.unlink()
