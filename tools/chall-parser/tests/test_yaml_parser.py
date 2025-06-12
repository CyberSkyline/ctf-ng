import pytest
import tempfile
from pathlib import Path
from parser.challenge_info import ChallengeInfo
from parser.yaml_parser import ComposeYamlParser, parse_compose_string, parse_compose_file
from parser.compose import ComposeFile, ComposeResourceName
from parser.service import Service

class TestComposeYamlParser:
    def test_parse_basic_compose(self, caplog):
        """Test parsing a basic compose file."""
        yaml_content = """
x-challenge:
  name: Basic Challenge
  description: A simple challenge to test parsing
  icon: puzzle
  questions:
    - name: flag
      question: What is the flag?
      points: 100
      answer: CTF{test_flag}
      max_attempts: 3
  hints:
    - hint: Check the logs
      preview: Log hint
      deduction: 10
  tags:
    - test
    - beginner
services:
  web:
    image: nginx:latest
    hostname: web-server
    networks:
      - boop
networks:
  boop:
    internal: true
"""
        caplog.set_level("DEBUG")
        parser = ComposeYamlParser()
        compose = parser.parse_string(yaml_content)
        
        assert compose.services is not None
        assert "web" in compose.services
        web_service = compose.services[ComposeResourceName("web")]
        assert web_service.image == "nginx:latest"
        assert web_service.hostname == "web-server"

    def test_parse_compose_with_challenge(self):
        """Test parsing a compose file with x-challenge extension."""
        yaml_content = """
services:
  challenge:
    image: myapp:latest
    hostname: challenge-server
x-challenge:
  name: Web Challenge
  description: Find the hidden flag
  icon: globe
  questions:
    - name: flag
      question: What is the flag?
      points: 100
      answer: CTF{test_flag}
      max_attempts: 5
  hints:
    - hint: Check the environment variables
      preview: Environment hint
      deduction: 10
  tags:
    - web
    - beginner
"""
        
        compose = parse_compose_string(yaml_content)
        
        assert compose.challenge is not None
        assert compose.challenge.name == "Web Challenge"
        assert len(compose.challenge.questions) == 1
        assert compose.challenge.questions[0].points == 100

    def test_parse_compose_with_templates(self):
        """Test parsing a compose file with template variables."""
        yaml_content = """
x-challenge:
  name: Template Challenge
  description: Use templates to set the flag
  icon: puzzle
  questions:
    - name: flag_question
      question: What is the flag?
      points: 100
      answer: CTF{template_flag}
      max_attempts: 3
  variables:
    flag:
      template: "fake.bothify('CTF{????-####}')"
      default: &flag_var default_flag
services:
  app:
    image: myapp:latest
    hostname: app-server
    environment:
      FLAG: *flag_var
"""
        
        parser = ComposeYamlParser()
        compose = parser.parse_string(yaml_content)
        
        assert compose.services is not None
        assert "app" in compose.services
        # Template rewriting should have occurred

    def test_parse_file(self):
        """Test parsing from a file."""
        yaml_content = """
x-challenge:
    name: File Challenge
    description: Find the hidden file
    icon: file
    hints:
    questions:
    - name: file_question
      question: What is the content of the file?
      points: 50
      answer: CTF{file_content}
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
            compose = parse_compose_file(temp_path)
            assert compose.services is not None
            assert "web" in compose.services
        finally:
            temp_path.unlink()

    def test_to_yaml(self):
        """Test converting ComposeFile back to YAML."""
        compose = ComposeFile(
            challenge=ChallengeInfo("Web Challenge", "Find the hidden flag", icon="globe", questions=[], hints=[], tags=[]),
            services={
                ComposeResourceName("web"): Service(
                    image="nginx:latest",
                    hostname="web-server"
                )
            }
        )
        
        parser = ComposeYamlParser()
        yaml_output = parser.to_yaml(compose)
        
        assert "nginx:latest" in yaml_output
        assert "web-server" in yaml_output

    def test_file_not_found(self):
        """Test error handling for missing files."""
        with pytest.raises(FileNotFoundError):
            parse_compose_file("nonexistent.yml")

    def test_invalid_yaml(self):
        """Test error handling for invalid YAML."""
        invalid_yaml = """
services:
  web:
    image: nginx:latest
    hostname: web-server
  invalid: [unclosed list
"""
        
        with pytest.raises(Exception):  # Could be various YAML parsing exceptions
            parse_compose_string(invalid_yaml)
