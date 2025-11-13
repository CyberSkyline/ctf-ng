import base64
import binascii
import pytest

from ..controllers.admin import import_challenge_from_yaml
from ...core.exceptions import ValidationError
from ..models import Challenge
from ...event.models.Event import Event


class TestImportChallengeFromYaml:
    """
    Integration tests for importing challenges from YAML.

    These tests use real database operations, the actual parser, model creation
    methods, and notification service to test the full integration.
    """

    @pytest.fixture()
    def test_event(self, db_session):
        """Create a test event in the database"""
        event = Event(name="Test Event", description="Test Description")
        db_session.add(event)
        db_session.commit()
        return event

    @pytest.mark.parametrize("invalid_yaml,expected_error", [
        # Property testing candidate: Could generate random invalid YAML strings
        # to test parser robustness more thoroughly
        ("invalid: yaml: content: [", "Invalid YAML format"),
        ("", "Invalid YAML format"),
        ("not yaml at all", "Invalid YAML format"),
        ("version: 3\nservices:\n  invalid: [", "Invalid YAML format"),
        ("challenge:\n  name: [unclosed", "Invalid YAML format"),
    ])
    def test_import_challenge_invalid_yaml_formats(self, test_event, invalid_yaml, expected_error):
        """Test that invalid YAML formats raise appropriate errors using real parser"""

        with pytest.raises(ValidationError, match=expected_error):
            import_challenge_from_yaml(test_event, invalid_yaml)

    def test_import_minimal_challenge_success(self, test_event):
        """Test successful import of a minimal challenge using real components"""
        yaml_content = """
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
        """

        # Act
        result = import_challenge_from_yaml(test_event, yaml_content)

        # Assert - verify challenge was created in database
        assert result.name == "Minimal Challenge"
        assert result.description == "A minimal test challenge"
        assert result.summary == "Just the basics"
        assert result.event_id == test_event.id
        assert result.icon is None

        # Verify it exists in database
        db_challenge = Challenge.query.get(result.id)
        assert db_challenge is not None
        assert db_challenge.name == "Minimal Challenge"

        # Verify YAML was stored
        assert db_challenge.yaml is not None
        assert db_challenge.yaml.body == yaml_content

    def test_import_challenge_with_hints(self, test_event):
        """Test importing a challenge with hints using real database operations"""
        yaml_content = """
        x-challenge:
          name: Challenge with Hints
          description: A challenge that has hints
          summary: Test hints functionality
          questions:
            - name: sample_question
              body: What is 2 + 2?
              points: 10
              answer: "4"
              max_attempts: 3
          hints:
            - name: first_hint
              body: This is the first hint
              preview: First hint preview
              deduction: 10
            - name: second_hint
              body: This is the second hint
              preview: Second hint preview
              deduction: 15
        """

        # Act
        result = import_challenge_from_yaml(test_event, yaml_content)

        # Assert - verify hints were created
        assert len(result.hints) == 2

        hint_names = [hint.name for hint in result.hints]
        assert "first_hint" in hint_names
        assert "second_hint" in hint_names

        first_hint = next(h for h in result.hints if h.name == "first_hint")
        assert first_hint.body == "This is the first hint"
        assert first_hint.preview == "First hint preview"
        assert first_hint.deduction == 10

    def test_import_challenge_with_tags(self, test_event):
        """Test importing a challenge with tags"""
        yaml_content = """
        x-challenge:
          name: Tagged Challenge
          description: A challenge with tags
          summary: Test tags
          questions:
            - name: sample_question
              body: What is 2 + 2?
              points: 10
              answer: "4"
              max_attempts: 3
          tags: ["web", "beginner", "sql"]
        """

        # Act
        result = import_challenge_from_yaml(test_event, yaml_content)

        # Assert - verify tags were created
        assert len(result.tags) == 3
        tag_names = [tag.name for tag in result.tags]
        assert "web" in tag_names
        assert "beginner" in tag_names
        assert "sql" in tag_names

    @pytest.mark.parametrize("answer_type,answer_data,expected_answer,expected_var_id", [
        # Test string answers
        ("string", "flag{simple_string}", "flag{simple_string}", None),
        ("string", "flag{special!@#$%}", "flag{special!@#$%}", None),
    ])
    def test_import_challenge_string_answers(self, test_event, answer_type,
                                           answer_data, expected_answer, expected_var_id):
        """Test importing challenges with different string answer types"""
        yaml_content = f"""
        x-challenge:
          name: String Answer Test
          description: Testing string answers
          summary: String answers
          questions:
            - name: test_question
              body: What's the flag?
              points: 100
              placeholder: "flag{{...}}"
              max_attempts: 3
              answer: "{answer_data}"
        """

        # Act
        result = import_challenge_from_yaml(test_event, yaml_content)

        # Assert
        assert len(result.questions) == 1
        question = result.questions[0]
        assert question.answer == expected_answer
        assert question.answer_variable_id == expected_var_id

    def test_import_challenge_template_answer_with_variable(self, test_event):
        """Test importing challenge with template answers that reference variables"""
        yaml_content = """
        x-challenge:
          name: Template Answer Test
          description: Testing template answers
          summary: Template answers
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
              placeholder: "key{...}"
              max_attempts: 5
              answer: *secret_key
            - name: flag_question
              body: What's the complete flag?
              points: 100
              placeholder: "flag{...}"
              max_attempts: 3
              answer: *flag_suffix
        """

        # Act
        result = import_challenge_from_yaml(test_event, yaml_content)

        # Assert - verify variables were created
        assert len(result.variables) == 2
        var_names = [var.name for var in result.variables]
        assert "secret_key" in var_names
        assert "flag_suffix" in var_names

        # Verify questions reference variables correctly
        assert len(result.questions) == 2
        for question in result.questions:
            assert question.answer is None  # Template answers don't have direct answers
            assert question.answer_variable_id is not None  # But they reference variables

    def test_import_challenge_template_answer_missing_variable(self, test_event):
        """Test that template answers referencing missing variables raise errors"""
        yaml_content = """
        version: "3"
        challenge:
          name: Bad Template Test
          description: Template with missing variable
          summary: Should fail
          questions:
            - name: bad_question
              body: This will fail
              points: 50
              answer: *nonexistent_variable
        """

        # Act & Assert
        with pytest.raises(ValidationError, match="Invalid YAML format"):
            import_challenge_from_yaml(test_event, yaml_content)

    @pytest.mark.parametrize("service_config", [
        # Property testing candidate: Could generate random valid service configurations
        # to test container blueprint creation more thoroughly
        {
            "image": "nginx:1.20",
            "hostname": "web-server",
            "environment": {"ENV": "production", "PORT": "80"},
            "mem_limit": "256m",
            "cpus": "0.5",
            "user": "nginx"
        },
        {
            "image": "alpine:latest",
            "hostname": "minimal-service",
            "environment": {},
            "mem_limit": None,
            "cpus": None,
            "user": None
        }
    ])
    def test_import_challenge_with_services(self, test_event, service_config):
        """Test importing challenges with container services"""
        env_yaml = str(service_config["environment"]).replace("'", '"') if service_config["environment"] else "{}"

        yaml_content = f"""
services:
  test_service:
    image: {service_config["image"]}
    hostname: {service_config["hostname"]}
    environment: {env_yaml}
        """

        if service_config.get("mem_limit"):
            yaml_content += f'\n    mem_limit: "{service_config["mem_limit"]}"'
        if service_config.get("cpus"):
            yaml_content += f'\n    cpus: "{service_config["cpus"]}"'
        if service_config.get("user"):
            yaml_content += f'\n    user: {service_config["user"]}'

        yaml_content += """
x-challenge:
  name: Service Test Challenge
  description: Testing services
  summary: Container services
  questions:
    - name: sample_question
      body: What is 2 + 2?
      points: 10
      answer: "4"
      max_attempts: 3
        """
        print(yaml_content)

        # Act
        result = import_challenge_from_yaml(test_event, yaml_content)

        # Assert - verify container blueprint was created
        assert len(result.blueprints) == 1
        blueprint = result.blueprints[0]
        assert blueprint.image == service_config["image"]
        assert blueprint.hostname == service_config["hostname"]

        # Check optional fields
        if service_config.get("mem_limit"):
            assert blueprint.mem_limit == service_config["mem_limit"]
        if service_config.get("cpus"):
            assert blueprint.cpus == float(service_config["cpus"])
        if service_config.get("user"):
            assert blueprint.user == service_config["user"]

    def test_import_complete_challenge(self, test_event):
        """Test importing a complete challenge with all components"""
        yaml_content = """
        services:
          web:
            image: nginx:latest
            hostname: web-server
            environment:
              DATABASE_URL: "postgresql://user:pass@db/ctf"
            mem_limit: "512m"
            cpus: "1.0"
          database:
            image: postgres:13
            hostname: db-server
            environment:
              POSTGRES_DB: "ctf"
              POSTGRES_USER: "ctfuser"
        x-challenge:
          name: Complete Challenge
          description: A fully featured challenge
          summary: Everything included
          icon: TbCompleteIcon
          hints:
            - name: web_hint
              body: Look at the web application
              preview: Web hint
              deduction: 5
            - name: db_hint
              body: Check the database
              preview: Database hint
              deduction: 10
          tags: ["web", "sql", "advanced"]
          variables:
            db_password:
              default: &db_password "default_pass"
              template: "fake.lexify('?'*12)"
            secret_flag:
              default: &secret_flag "flag{default}"
              template: "fake.hexify('flag{' + '^'*8 + '}')"
          questions:
            - name: user_flag
              body: Find the user flag
              points: 50
              placeholder: "user{...}"
              max_attempts: 10
              answer: "user{simple_flag}"
            - name: root_flag
              body: Get the root flag
              points: 100
              placeholder: "flag{...}"
              max_attempts: 5
              answer: *secret_flag
        """

        # Act
        result = import_challenge_from_yaml(test_event, yaml_content)

        # Assert all components were created correctly
        assert result.name == "Complete Challenge"
        assert result.description == "A fully featured challenge"
        assert result.icon == "TbCompleteIcon"

        # Check hints
        assert len(result.hints) == 2
        hint_names = [h.name for h in result.hints]
        assert "web_hint" in hint_names
        assert "db_hint" in hint_names

        # Check tags
        assert len(result.tags) == 3
        tag_names = [t.name for t in result.tags]
        assert set(tag_names) == {"web", "sql", "advanced"}

        # Check variables
        assert len(result.variables) == 2
        var_names = [v.name for v in result.variables]
        assert "db_password" in var_names
        assert "secret_flag" in var_names

        # Check questions
        assert len(result.questions) == 2
        user_question = next(q for q in result.questions if q.name == "user_flag")
        assert user_question.answer == "user{simple_flag}"
        assert user_question.answer_variable_id is None

        root_question = next(q for q in result.questions if q.name == "root_flag")
        assert root_question.answer is None
        assert root_question.answer_variable_id is not None

        # Check services
        assert len(result.blueprints) == 2
        hostnames = [b.hostname for b in result.blueprints]
        assert "web-server" in hostnames
        assert "db-server" in hostnames

    def test_import_challenge_database_rollback_on_error(self, test_event):
        """Test that database operations are rolled back when errors occur"""
        # Get initial challenge count
        initial_count = Challenge.query.filter_by(event_id=test_event.id).count()

        # Invalid YAML that will cause an error after some processing
        yaml_content = """
        version: "3"
        challenge:
          name: Will Fail Challenge
          description: This will fail
          questions:
            - name: bad_question
              body: This question references a missing variable
              points: 50
              answer:
                template:
                  variable: missing_variable
        """
        # Act & Assert
        with pytest.raises(ValidationError):
            import_challenge_from_yaml(test_event, yaml_content)

        # Verify no challenge was created (rollback worked)
        final_count = Challenge.query.filter_by(event_id=test_event.id).count()
        assert final_count == initial_count
