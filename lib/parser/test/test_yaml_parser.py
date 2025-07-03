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
import logging
import pathlib
import re
from cattrs import ClassValidationError
from cyber_skyline.chall_parser.compose.answer import Answer
import pytest
import tempfile
from pathlib import Path
from cyber_skyline.chall_parser.compose.challenge_info import ChallengeInfo, TextBody
from cyber_skyline.chall_parser.rewriter import Template
from cyber_skyline.chall_parser.yaml_parser import ComposeYamlParser, parse_compose_string, parse_compose_file
from cyber_skyline.chall_parser.compose import ComposeFile, ComposeResourceName
from cyber_skyline.chall_parser.compose.service import Service

class TestComposeYamlParser:
    def test_parse_basic_compose(self, caplog):
        """Test parsing a basic compose file."""
        yaml_content = """
x-challenge:
  name: Basic Challenge
  description: A simple challenge to test parsing
  icon: TbPuzzle
  questions:
    - name: flag
      body: What is the flag?
      points: 100
      answer: CTF{test_flag}
      max_attempts: 3
  hints:
    - body: Check the logs
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
  icon: TbGlobe
  questions:
    - name: flag
      body: What is the flag?
      points: 100
      answer: CTF{test_flag}
      max_attempts: 5
  hints:
    - body: Check the environment variables
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

    def test_parse_compose_with_templates(self, caplog):
        """Test parsing a compose file with template variables."""
        yaml_content = """
x-challenge:
  name: Template Challenge
  description: Use templates to set the flag
  icon: TbPuzzle
  questions:
    - name: flag_question
      body: What is the flag?
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
        caplog.set_level("DEBUG")
        parser = ComposeYamlParser()
        compose = parser.parse_string(yaml_content)
        
        assert compose.services is not None
        assert "app" in compose.services
        assert compose.challenge.variables is not None
        assert "flag" in compose.challenge.variables
        flag_var = compose.challenge.variables["flag"]
        flag_tmpl_validator = re.compile(r"CTF\{[a-zA-Z]{4}-[0-9]{4}\}")
        assert flag_tmpl_validator.fullmatch(str(flag_var.template.eval()))

    def test_parse_compose_with_bad_templates(self, caplog):
        """Test parsing a compose file with template variables."""
        yaml_content = """
x-challenge:
  name: Template Challenge
  description: Use templates to set the flag
  icon: puzzle
  questions:
    - name: flag_question
      body: What is the flag?
      points: 100
      answer: CTF{template_flag}
      max_attempts: 3
  variables:
    flag:
      template: "fake.bothify('CTF{????-####}'"
      default: &flag_var default_flag
services:
  app:
    image: myapp:latest
    hostname: app-server
    environment:
      FLAG: *flag_var
"""
        caplog.set_level("DEBUG")
        parser = ComposeYamlParser()
        with pytest.RaisesGroup(ClassValidationError):
          parser.parse_string(yaml_content)

    def test_parse_file(self):
        """Test parsing from a file."""
        yaml_content = """
x-challenge:
    name: File Challenge
    description: Find the hidden file
    icon: TbFile
    hints:
    questions:
    - name: file_question
      body: What is the content of the file?
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
            challenge=ChallengeInfo("Web Challenge", "Find the hidden flag", icon="TbGlobe", questions=[], hints=[], tags=[]),
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

    def test_complex_challenge(self):
        """Test parsing a complex challenge with multiple services and networks."""
        chall_file = pathlib.Path(__file__).parent.resolve() / "../../../examples/complex_chall.yml"
        compose = parse_compose_file(chall_file)
        
        # Validate challenge metadata
        assert compose.challenge is not None
        assert compose.challenge.name == "Advanced Web Exploitation"
        
        expected_description = (
            "This challenge involves exploiting a vulnerable web application to retrieve\n"
            "multiple flags. You'll need to use SQL injection, XSS, and privilege escalation\n"
            "techniques to complete all objectives.\n"
        )
        assert compose.challenge.description == expected_description
        assert compose.challenge.icon == "TbShieldAlt"
        
        # Validate template definitions
        assert compose.challenge.templates is not None
        assert "database-flag" in compose.challenge.templates
        assert "admin-flag" in compose.challenge.templates
        
        # Validate variables
        assert compose.challenge.variables is not None
        assert len(compose.challenge.variables) == 4
        
        # Database flag variable
        assert "db_flag" in compose.challenge.variables
        db_flag_var = compose.challenge.variables["db_flag"]
        assert db_flag_var.default == "CTF{sql_1nj3ct10n_m4st3r}"
        # Template should evaluate to something like CTF{sql_XX_####}
        db_flag_eval = str(db_flag_var.template.eval())
        assert db_flag_eval.startswith("CTF{sql_")
        assert db_flag_eval.endswith("}")
        
        # Admin flag variable
        assert "admin_flag" in compose.challenge.variables
        admin_flag_var = compose.challenge.variables["admin_flag"]
        assert admin_flag_var.default == "CTF{4dm1n_p4n3l_h4ck3d}"
        admin_flag_eval = str(admin_flag_var.template.eval())
        assert admin_flag_eval.startswith("CTF{admin_")
        
        # Database password variable
        assert "db_password" in compose.challenge.variables
        db_pass_var = compose.challenge.variables["db_password"]
        assert db_pass_var.default == "SecureP4ss!"
        # Template should generate a 12-character password
        db_pass_eval = str(db_pass_var.template.eval())
        assert len(db_pass_eval) == 12
        
        # Database port variable
        assert "db_port" in compose.challenge.variables
        db_port_var = compose.challenge.variables["db_port"]
        assert db_port_var.default == "3306"
        # Template should generate a valid port number
        db_port_eval = db_port_var.template.eval()
        assert isinstance(db_port_eval, int)
        assert 1 <= db_port_eval <= 65535
        
        # Validate questions
        assert compose.challenge.questions is not None
        assert len(compose.challenge.questions) == 4
        
        # First question - SQL Injection
        sql_question = compose.challenge.questions[0]
        assert sql_question.name == "SQL Injection Flag"
        assert sql_question.body == "What is the flag hidden in the users table?"
        assert sql_question.points == 150
        assert sql_question.answer == db_flag_var.template
        assert sql_question.max_attempts == 5
        
        # Second question - Admin Panel
        admin_question = compose.challenge.questions[1]
        assert admin_question.name == "Admin Panel Flag"
        assert admin_question.body == "What flag is displayed on the admin dashboard?"
        assert admin_question.points == 200
        assert admin_question.answer == admin_flag_var.template
        assert admin_question.max_attempts == 3
        
        # Third question - Privilege Escalation
        priv_question = compose.challenge.questions[2]
        assert priv_question.name == "Privilege Escalation Flag"
        assert priv_question.body == "What is the root flag on the server?"
        assert priv_question.points == 300
        assert isinstance(priv_question.answer, Answer)
        assert priv_question.answer.body == "CTF\\{pr1v_3sc_c0mpl3t3\\}"
        assert priv_question.answer.test_cases
        assert len(priv_question.answer.test_cases) == 1
        assert priv_question.answer.test_cases[0].answer == "CTF{pr1v_3sc_c0mpl3t3}"
        assert priv_question.answer.test_cases[0].correct
        assert priv_question.max_attempts == 2

        # Fourth question - Complex Regex
        complex_question = compose.challenge.questions[3]
        assert complex_question.name == "Complex Regex"
        assert complex_question.body == "what is a valid flag?"
        assert complex_question.points == 100
        assert isinstance(complex_question.answer, Answer)
        assert complex_question.answer.body == "CTF\\{[a-zA-Z0-9_]+\\}"
        assert complex_question.answer.test_cases
        assert len(complex_question.answer.test_cases) == 2
        assert complex_question.answer.test_cases[0].answer == "CTF{valid_flag_123}"
        assert complex_question.answer.test_cases[0].correct
        assert complex_question.answer.test_cases[1].answer == "CTF{invalid flag}"
        assert not complex_question.answer.test_cases[1].correct
        assert complex_question.max_attempts == 4

        # Validate hints
        assert compose.challenge.hints is not None
        assert len(compose.challenge.hints) == 3
        
        # First hint - Text hint
        db_hint = compose.challenge.hints[0]
        assert isinstance(db_hint.body, TextBody)
        assert db_hint.body.type == "text"
        expected_db_content = (
            "Look for SQL injection vulnerabilities in the login form.\n"
            "Try using single quotes to break the SQL syntax.\n"
        )
        assert isinstance(db_hint.body, TextBody)
        assert db_hint.body.content == expected_db_content
        assert db_hint.preview == "Database interaction hint"
        assert db_hint.deduction == 25
        
        # Second hint - Simple string
        admin_hint = compose.challenge.hints[1]
        assert isinstance(admin_hint.body, str)
        assert admin_hint.body == "The admin panel might be accessible at /admin or /dashboard"
        assert admin_hint.preview == "Admin panel location"
        assert admin_hint.deduction == 30
        
        # Third hint - Text hint for privilege escalation
        priv_hint = compose.challenge.hints[2]
        assert isinstance(priv_hint.body, TextBody)
        assert priv_hint.body.type == "text"
        assert priv_hint.body.content == "Check for SUID binaries or writable system files for privilege escalation"
        assert priv_hint.preview == "System exploitation hint"
        assert priv_hint.deduction == 50
        
        # Validate summary
        expected_summary = (
            "A multi-stage web exploitation challenge covering SQL injection,\n"
            "cross-site scripting, and Linux privilege escalation techniques.\n"
        )
        assert compose.challenge.summary == expected_summary
        
        # Validate tags
        assert compose.challenge.tags is not None
        expected_tags = ["web", "sql-injection", "privilege-escalation", "hard"]
        assert compose.challenge.tags == expected_tags
        
        # Validate services
        assert compose.services is not None
        assert len(compose.services) == 3
        
        # Web service validation
        assert "web" in compose.services
        web_service = compose.services[ComposeResourceName("web")]
        assert web_service.image == "nginx:alpine"
        assert web_service.hostname == "web-server"
        assert web_service.networks == ["challenge-net"]
        assert web_service.mem_limit == "256m"
        assert web_service.cpus == "0.5"
        assert web_service.cap_add == ["NET_ADMIN"]
        
        # Web service environment
        assert web_service.environment is not None
        web_env = web_service.environment
        assert isinstance(web_env, dict)
        assert web_env["DB_HOST"] == "database"
        
        # These should be template evaluations, not static defaults
        # DB_PORT should be a template-generated port number
        db_port_from_env = web_env["DB_PORT"]
        assert isinstance(db_port_from_env, Template)
        db_port_eval = db_port_from_env.eval()
        assert isinstance(db_port_eval, int)
        assert 1 <= db_port_eval <= 65535
        
        # DB_PASSWORD should be template-generated
        db_password_from_env = web_env["DB_PASSWORD"]
        assert isinstance(db_password_from_env, Template)
        db_pass_eval = str(db_password_from_env.eval())
        assert len(db_pass_eval) == 12
        
        # FLAG_1 should be template-generated
        flag1_from_env = web_env["FLAG_1"]
        assert isinstance(flag1_from_env, Template)
        flag1_eval = str(flag1_from_env.eval())
        assert flag1_eval.startswith("CTF{sql_")
        assert flag1_eval.endswith("}")
        
        # FLAG_2 should be template-generated  
        flag2_from_env = web_env["FLAG_2"]
        assert isinstance(flag2_from_env, Template)
        flag2_eval = str(flag2_from_env.eval())
        assert flag2_eval.startswith("CTF{admin_")
            
        
        # Database service validation
        assert "database" in compose.services
        db_service = compose.services[ComposeResourceName("database")]
        assert db_service.image == "mysql:8.0"
        assert db_service.hostname == "db-server"
        assert db_service.networks == ["challenge-net"]
        assert db_service.mem_limit == "512m"
        assert db_service.memswap_limit == "1g"
        assert db_service.cpus == "1.0"
        
        # Database service environment
        assert db_service.environment is not None
        db_env = db_service.environment
        assert isinstance(db_env, dict)
        
        # These should be template evaluations, not static defaults
        mysql_root_pass = db_env["MYSQL_ROOT_PASSWORD"]
        assert isinstance(mysql_root_pass, Template)
        root_pass_eval = str(mysql_root_pass.eval())
        assert len(root_pass_eval) == 12

            
        assert db_env["MYSQL_DATABASE"] == "challenge_db"
        assert db_env["MYSQL_USER"] == "webapp"
        assert db_env["MYSQL_PASSWORD"] == "webapp123"
        
        # HIDDEN_FLAG should be template-generated
        hidden_flag = db_env["HIDDEN_FLAG"]
        assert isinstance(hidden_flag, Template)
        hidden_flag_eval = str(hidden_flag.eval())
        assert hidden_flag_eval.startswith("CTF{sql_")
        assert hidden_flag_eval.endswith("}")
        
        # App service validation
        assert "app" in compose.services
        app_service = compose.services[ComposeResourceName("app")]
        assert app_service.image == "vulnerable-webapp:latest"
        assert app_service.hostname == "app-server"
        assert app_service.networks == ["challenge-net"]
        assert app_service.user == "webapp"
        
        # App service command and entrypoint
        assert app_service.command == ["/start.sh", "--debug"]
        assert app_service.entrypoint == ["/entrypoint.sh", "webapp"]
        
        # App service environment
        assert app_service.environment is not None
        app_env = app_service.environment
        assert isinstance(app_env, dict)
        assert app_env["APP_ENV"] == "production"
        assert app_env["SECRET_KEY"] == "dont_use_in_real_life"
        
        # ADMIN_FLAG should be template-generated
        admin_flag_env = app_env["ADMIN_FLAG"]
        assert isinstance(admin_flag_env, Template)
        admin_flag_eval = str(admin_flag_env.eval())
        assert admin_flag_eval.startswith("CTF{admin_")

        
        # DB_CONNECTION should contain template-evaluated password
        db_connection = app_env["DB_CONNECTION"]
        assert isinstance(db_connection, str)
        assert "mysql://webapp:webapp123@database:3306/challenge_db" == db_connection

    def test_parser_converter_setup(self):
        """Test that the parser converter is set up correctly."""
        parser = ComposeYamlParser()
        assert parser.converter is not None

    def test_parse_minimal_challenge(self):
        """Test parsing minimal valid challenge."""
        yaml_content = """
x-challenge:
  name: Minimal
  description: Minimal challenge
  questions: []
services:
  app:
    image: test:latest
    hostname: test-host
"""
        compose = parse_compose_string(yaml_content)
        assert compose.challenge.name == "Minimal"
        assert len(compose.challenge.questions) == 0

    def test_parse_challenge_with_all_hint_types(self):
        """Test parsing challenge with different hint types."""
        yaml_content = """
x-challenge:
  name: Hint Test
  description: Testing hint types
  questions: []
  hints:
    - body:
        type: text
        content: Structured text hint
      preview: Structured hint
      deduction: 15
    - body: Simple string hint
      preview: Simple hint 
      deduction: 5
services:
  app:
    image: test:latest
    hostname: test-host
"""
        compose = parse_compose_string(yaml_content)
        assert isinstance(compose.challenge.hints, list)
        assert len(compose.challenge.hints) == 2

    def test_parse_error_handling(self):
        """Test various parsing error conditions."""
        # Missing required challenge fields
        invalid_yaml = """
x-challenge:
  name: Missing Description
services:
  app:
    image: test:latest
    hostname: test-host
"""
        with pytest.raises(Exception):
            parse_compose_string(invalid_yaml)

    def test_template_evaluation_in_parsed_file(self):
        """Test that templates are properly evaluated after parsing."""
        yaml_content = """
x-challenge:
  name: Template Test
  description: Testing templates
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
        compose = parse_compose_string(yaml_content)
        
        # Check that variables contain templates
        assert compose.challenge.variables is not None
        assert "test_var" in compose.challenge.variables
        test_var = compose.challenge.variables["test_var"]
        result = test_var.template.eval()
        assert isinstance(result, str)

    def test_yaml_stream_parsing(self):
        """Test parsing from a stream."""
        import io
        yaml_content = """
x-challenge:
  name: Stream Test
  description: Testing stream parsing
  questions: []
services:
  app:
    image: test:latest
    hostname: test-host
"""
        stream = io.StringIO(yaml_content)
        parser = ComposeYamlParser()
        compose = parser.parse_stream(stream)
        assert compose.challenge.name == "Stream Test"

    def test_to_yaml_roundtrip(self):
        """Test that YAML output can be parsed back."""
        original_yaml = """
x-challenge:
  name: Roundtrip Test
  description: Testing YAML roundtrip
  questions: []
services:
  app:
    image: test:latest
    hostname: test-host
"""
        # Parse original
        compose = parse_compose_string(original_yaml)
        
        # Convert to YAML
        parser = ComposeYamlParser()
        yaml_output = parser.to_yaml(compose)
        
        # Parse the output
        compose2 = parse_compose_string(yaml_output)
        
        assert compose2.challenge.name == compose.challenge.name
        assert compose2.challenge.description == compose.challenge.description

    def test_parser_logging(self, caplog):
        """Test that parser logging works correctly."""
        caplog.set_level(logging.DEBUG)
        yaml_content = """
x-challenge:
  name: Logging Test
  description: Testing logging
  questions: []
services:
  app:
    image: test:latest
    hostname: test-host
"""
        parse_compose_string(yaml_content)
        assert "Starting YAML parsing" in caplog.text

    def test_invalid_variable_missing_template(self):
        """Test error when variable is missing template key."""
        yaml_content = """
x-challenge:
  name: Invalid Variable Test
  description: Testing invalid variable configuration
  icon: TbPuzzle
  questions: []
  variables:
    bad_var:
      default: &bad_var "default_value"
      # missing template key
services:
  app:
    image: test:latest
    hostname: test-host
    environment:
      BAD_VAR: *bad_var
"""
        # Should raise an error during parsing due to missing template
        with pytest.raises(ValueError, match="Variable 'bad_var' must have a 'template' key"):
            parse_compose_string(yaml_content)

    def test_invalid_variable_missing_default(self):
        """Test error when variable is missing default key."""
        yaml_content = """
x-challenge:
  name: Invalid Variable Test
  description: Testing invalid variable configuration
  icon: TbPuzzle
  questions: []
  variables:
    bad_var:
      template: "fake.word()"
      # missing default key
services:
  app:
    image: test:latest
    hostname: test-host
"""
        # Should fail during YAML processing due to missing default
        with pytest.raises(ValueError, match="Variable 'bad_var' must have a 'default' key"):
            parse_compose_string(yaml_content)

    def test_invalid_variable_no_anchor(self):
        """Test error when variable default has no anchor."""
        yaml_content = """
x-challenge:
  name: Invalid Variable Test
  description: Testing invalid variable configuration
  icon: TbPuzzle
  questions: []
  variables:
    bad_var:
      template: "fake.word()"
      default: "no_anchor_value"  # missing anchor
services:
  app:
    image: test:latest
    hostname: test-host
"""
        # Should fail during YAML processing due to missing anchor
        with pytest.raises(Exception):
            parse_compose_string(yaml_content)

    def test_invalid_template_syntax(self):
        """Test error when template has invalid Python syntax."""
        yaml_content = """
x-challenge:
  name: Invalid Template Test
  description: Testing invalid template syntax
  icon: TbPuzzle
  questions: []
  variables:
    bad_template:
      template: "fake.invalid_function("  # invalid syntax - missing closing paren
      default: &bad_val "default"
services:
  app:
    image: test:latest
    hostname: test-host
    environment:
      BAD_VAR: *bad_val
"""
        with pytest.raises((ClassValidationError, Exception)):
            parse_compose_string(yaml_content)

    def test_invalid_template_nonexistent_faker_method(self):
        """Test error when template uses non-existent Faker method."""
        yaml_content = """
x-challenge:
  name: Invalid Template Test
  description: Testing invalid Faker method
  icon: TbPuzzle
  questions: []
  variables:
    bad_method:
      template: "fake.nonexistent_method()"
      default: &bad_val "default"
services:
  app:
    image: test:latest
    hostname: test-host
    environment:
      BAD_VAR: *bad_val
"""
        parser = ComposeYamlParser()
        
        # Should fail to parse because template fails to evaluate
        with pytest.raises(ClassValidationError):
            parser.parse_string(yaml_content)

    def test_missing_challenge_block(self):
        """Test error when x-challenge block is missing."""
        yaml_content = """
services:
  app:
    image: test:latest
    hostname: test-host
"""
        with pytest.raises(Exception):  # Should fail - challenge is required
            parse_compose_string(yaml_content)

    def test_invalid_challenge_missing_required_fields(self):
        """Test error when challenge is missing required fields."""
        yaml_content = """
x-challenge:
  name: Test Challenge
  # missing description and questions
services:
  app:
    image: test:latest
    hostname: test-host
"""
        with pytest.raises(Exception):
            parse_compose_string(yaml_content)

    def test_invalid_service_missing_required_fields(self):
        """Test error when service is missing required fields."""
        yaml_content = """
x-challenge:
  name: Test Challenge
  description: Testing service validation
  questions: []
services:
  bad_service:
    image: test:latest
    # missing hostname
"""
        with pytest.raises(Exception):
            parse_compose_string(yaml_content)

    def test_invalid_icon_prefix(self):
        """Test error when icon doesn't have Tb prefix."""
        yaml_content = """
x-challenge:
  name: Test Challenge
  description: Testing icon validation
  icon: invalid-icon  # doesn't start with Tb
  questions: []
services:
  app:
    image: test:latest
    hostname: test-host
"""
        with pytest.raises((ClassValidationError, ValueError)):
            parse_compose_string(yaml_content)

    def test_invalid_service_names(self):
        """Test error when service names contain invalid characters."""
        yaml_content = """
x-challenge:
  name: Test Challenge
  description: Testing service name validation
  questions: []
services:
  "service with spaces":
    image: test:latest
    hostname: test-host
"""
        with pytest.raises(Exception):  # Should fail validation
            parse_compose_string(yaml_content)

    def test_invalid_network_configuration(self):
        """Test error when network is not internal."""
        yaml_content = """
x-challenge:
  name: Test Challenge
  description: Testing network validation
  questions: []
services:
  app:
    image: test:latest
    hostname: test-host
    networks:
      - external_net
networks:
  external_net:
    internal: false  # Should be true
"""
        with pytest.raises(Exception):  # Should fail - networks must be internal
            parse_compose_string(yaml_content)

    def test_invalid_question_types(self):
        """Test error when question fields have wrong types."""
        yaml_content = """
x-challenge:
  name: Test Challenge
  description: Testing question validation
  questions:
    - name: 123  # should be string
      body: "What is the flag?"
      points: "invalid"  # should be int
      answer: "CTF{test}"
      max_attempts: 5
services:
  app:
    image: test:latest
    hostname: test-host
"""
        with pytest.raises(Exception):
            parse_compose_string(yaml_content)



    def test_invalid_challenge_key(self):
        """Test error when challenge key is invalid."""
        yaml_content = """
scan-challenge:
  name: Test Challenge
  description: Testing question validation
  questions:
    - name: 123  # should be string
      body: "What is the flag?"
      points: "invalid"  # should be int
      answer: "CTF{test}"
      max_attempts: 5
services:
  app:
    image: test:latest
    hostname: test-host
"""
        with pytest.raises(Exception):
            parse_compose_string(yaml_content)

    def test_answer_template_validation(self, caplog):
        """Test that answer templates are validated."""
        yaml_content = """
x-challenge:
  name: Test Challenge
  description: Testing answer template validation
  variables:
    test_var:
      template: "fake.word()"
      default: &test_val "default_word"
  questions:
    - name: flag
      body: "What is the flag?"
      points: 100
      answer: *test_val  # should be a template
      max_attempts: 5
services:
  app:
    image: test:latest
    hostname: test-host
"""
        caplog.set_level("DEBUG")
        chall = parse_compose_string(yaml_content)
        assert chall.challenge is not None
        assert chall.challenge.variables is not None
        assert "test_var" in chall.challenge.variables
        assert chall.challenge.variables["test_var"].default == "default_word"
        assert chall.challenge.variables["test_var"].template is not None
        assert isinstance(chall.challenge.variables["test_var"].template, Template)
        assert not isinstance(chall.challenge.questions[0].answer, str)
        assert isinstance(chall.challenge.questions[0].answer, Template)
        assert chall.challenge.variables["test_var"].template == chall.challenge.questions[0].answer

