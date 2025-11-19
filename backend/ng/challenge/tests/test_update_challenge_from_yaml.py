import base64
import pytest

from ..models import ContainerBlueprint

from ..controllers.admin import update_challenge_from_yaml
from ..models import Challenge, ChallengeYaml, ChallengeTag, Question, ChallengeVariable, Hint
from ...core.exceptions import ValidationError
from ...event.models.Event import Event


class TestUpdateChallengeFromYaml:
    """
    Integration tests for updating challenges from YAML.

    These tests use real database operations, the actual parser, and model creation
    methods to test the full integration of the update functionality.
    """

    @pytest.fixture()
    def test_event(self, db_session):
        """Create a test event in the database"""
        event = Event(name="Test Event", description="Test Description")
        db_session.add(event)
        db_session.commit()
        return event

    @pytest.fixture()
    def existing_challenge(self, db_session, test_event) -> Challenge:
        """Create an existing challenge with YAML in the database"""
        challenge = Challenge(
            event_id=test_event.id,
            name="Original Challenge",
            description="Original description",
            summary="Original summary",
            icon=None
        )
        db_session.add(challenge)
        db_session.flush()  # Get the ID

        # Add YAML
        yaml_content = """
        version: "3"
        challenge:
          name: Original Challenge
          description: Original description
        """
        challenge_yaml = ChallengeYaml(
            challenge_id=challenge.id,
            body=yaml_content
        )
        db_session.add(challenge_yaml)
        db_session.commit()
        return challenge

    @pytest.mark.parametrize("invalid_yaml", [
        # Property testing candidate: Could generate random invalid YAML strings
        # to test parser robustness during updates
        "invalid: yaml: [",
        "",
        "not: yaml: at: all",
        "version: invalid\nchallenge:\n  name: [unclosed",
    ])
    def test_update_challenge_invalid_yaml(self, db_session, existing_challenge: Challenge, invalid_yaml):
        """Test updating with invalid YAML formats"""
        with pytest.raises(ValidationError, match="Invalid YAML format"):
            update_challenge_from_yaml(existing_challenge, invalid_yaml)

    def test_update_challenge_basic_fields(self, db_session, existing_challenge: Challenge):
        """Test updating basic challenge fields"""
        yaml_content = """
        x-challenge:
          name: Updated Challenge Name
          description: Updated description text
          summary: Updated summary text
          icon: TbUpdatedIcon
          questions:
            - name: sample_question
              body: What is 2 + 2?
              points: 10
              answer: "4"
              max_attempts: 3
        """
        # Act
        result = update_challenge_from_yaml(existing_challenge, yaml_content)

        # Assert - verify fields were updated
        assert result.name == "Updated Challenge Name"
        assert result.description == "Updated description text"
        assert result.summary == "Updated summary text"
        assert result.icon == "TbUpdatedIcon"

        # Verify YAML body was updated
        db_session.refresh(result)
        assert result.yaml.body == yaml_content

    def test_update_challenge_cannot_remove_existing_hints(self, db_session, existing_challenge: Challenge):
        """Test that existing hints cannot be removed during update"""
        # Add a hint to existing challenge
        hint = Hint(
            challenge_id=existing_challenge.id,
            name="existing_hint",
            body="Existing hint text",
            preview="Preview",
            deduction=10,
            index=0
        )
        db_session.add(hint)
        db_session.commit()

        # Try to update without the hint
        yaml_content = """
        x-challenge:
          name: Updated Challenge Name
          description: Updated description text
          summary: Updated summary text
          icon: TbUpdatedIcon
          questions:
            - name: sample_question
              body: What is 2 + 2?
              points: 10
              answer: "4"
              max_attempts: 3
          hints: []
        """

        with pytest.raises(ValidationError, match="Cannot remove existing hints"):
            update_challenge_from_yaml(existing_challenge, yaml_content)

    def test_update_challenge_cannot_remove_existing_questions(self, db_session, existing_challenge: Challenge):
        """Test that existing questions cannot be removed during update"""
        # Add a question to existing challenge
        question = Question(
            challenge_id=existing_challenge.id,
            name="existing_question",
            body="What is the flag?",
            points=100,
            max_attempts=3,
            answer="flag{test}",
            index=0
        )
        db_session.add(question)
        db_session.commit()

        # Try to update without the question
        yaml_content = """
        x-challenge:
          name: Updated Challenge Name
          description: Updated description text
          summary: Updated summary text
          icon: TbUpdatedIcon
          questions:
            - name: sample_question
              body: What is 2 + 2?
              points: 10
              answer: "4"
              max_attempts: 3
        """

        with pytest.raises(ValidationError, match="Cannot remove existing questions"):
            update_challenge_from_yaml(existing_challenge, yaml_content)

    def test_update_challenge_cannot_remove_existing_services(self, db_session, existing_challenge: Challenge):
        """Test that existing questions cannot be removed during update"""
        # Add a question to existing challenge
        container_blueprint = ContainerBlueprint.create_container_blueprint(
            challenge_id=existing_challenge.id,
            name="existing_service",
            image="nginx:latest",
            hostname="web",
        )

        # Try to update without the service
        yaml_content = """
        x-challenge:
          name: Updated Challenge Name
          description: Updated description text
          summary: Updated summary text
          icon: TbUpdatedIcon
          questions:
            - name: sample_question
              body: What is 2 + 2?
              points: 10
              answer: "4"
              max_attempts: 3
        """

        with pytest.raises(ValidationError, match="Cannot remove existing services"):
            update_challenge_from_yaml(existing_challenge, yaml_content)

    @pytest.mark.parametrize("existing_tags,new_tags,expected_final_tags", [
        # Property testing candidate: Could generate random tag combinations
        # to test tag management logic more thoroughly
        (["web", "easy"], ["web", "easy", "new"], ["web", "easy", "new"]),  # Add one tag
        (["web", "easy"], ["web"], ["web"]),  # Remove one tag
        (["old1", "old2"], ["new1", "new2"], ["new1", "new2"]),  # Replace all tags
        ([], ["new"], ["new"]),  # Add to empty
        (["existing"], [], []),  # Remove all
    ])
    def test_update_challenge_tag_management(self, db_session, existing_challenge: Challenge,
                                           existing_tags, new_tags, expected_final_tags):
        """Test tag addition and removal during updates"""
        # Add existing tags
        for tag_name in existing_tags:
            tag = ChallengeTag(challenge_id=existing_challenge.id, name=tag_name)
            db_session.add(tag)
        db_session.commit()

        # Create YAML with new tags
        tags_yaml = str(new_tags).replace("'", '"') if new_tags else "[]"
        yaml_content = f"""
        x-challenge:
          name: Updated Challenge Name
          description: Updated description text
          summary: Updated summary text
          icon: TbUpdatedIcon
          questions:
            - name: sample_question
              body: What is 2 + 2?
              points: 10
              answer: "4"
              max_attempts: 3
          tags: {tags_yaml}
        """

        # Act
        result = update_challenge_from_yaml(existing_challenge, yaml_content)

        # Assert - verify final tag state
        db_session.refresh(result)
        actual_tags = [tag.name for tag in result.tags]
        assert sorted(actual_tags) == sorted(expected_final_tags)

    def test_update_challenge_add_new_service(self, db_session, existing_challenge: Challenge):
        """Test adding a new container service during update"""
        yaml_content = """
        services:
          web:
            image: nginx:latest
            hostname: web-server
            environment:
              ENV: production
            mem_limit: "512m"
            cpus: "1.0"
        x-challenge:
          name: Updated Challenge Name
          description: Updated description text
          summary: Updated summary text
          icon: TbUpdatedIcon
          questions:
            - name: sample_question
              body: What is 2 + 2?
              points: 10
              answer: "4"
              max_attempts: 3
        """

        # Act
        result = update_challenge_from_yaml(existing_challenge, yaml_content)

        # Assert - verify service was added
        db_session.refresh(result)
        assert len(result.blueprints) == 1
        blueprint = result.blueprints[0]
        assert blueprint.image == "nginx:latest"
        assert blueprint.hostname == "web-server"
        assert blueprint.mem_limit == "512m"
        assert blueprint.cpus == 1.0

    def test_update_challenge_with_variables_and_template_answers(self, db_session, existing_challenge: Challenge):
        """Test updating challenge with variables and template-based answers"""
        yaml_content = """
        x-challenge:
          name: Updated Challenge Name
          description: Updated description text
          summary: Updated summary text
          icon: TbUpdatedIcon
          variables:
            secret_key:
              default: &secret_key "default_secret"
              template: "fake.lexify('?'*16)"
            flag_value:
              default: &flag_value "default_flag"
              template: "fake.hexify('flag{' + '^'*8 + '}')"
          questions:
            - name: secret_question
              body: "What is the secret key?"
              points: 50
              max_attempts: 3
              answer: *secret_key
            - name: flag_question
              body: "What is the flag?"
              points: 100
              max_attempts: 5
              answer: *flag_value
        """

        # Act
        result = update_challenge_from_yaml(existing_challenge, yaml_content)

        # Assert - verify variables and questions were created correctly
        db_session.refresh(result)

        # Check variables
        assert len(result.variables) == 2
        var_names = [var.name for var in result.variables]
        assert "secret_key" in var_names
        assert "flag_value" in var_names

        # Check questions
        assert len(result.questions) == 2
        for question in result.questions:
            assert question.answer is None  # Template answers don't have direct answers
            assert question.answer_variable_id is not None  # But they reference variables

    def test_update_challenge_database_rollback_on_parser_error(self, db_session, existing_challenge: Challenge):
        """Test that database changes are rolled back when parser fails"""
        # Get initial state
        initial_name = existing_challenge.name

        # Invalid YAML that will cause parser to fail
        invalid_yaml = "invalid: yaml: structure: ["

        # Act & Assert
        with pytest.raises(ValidationError):
            update_challenge_from_yaml(existing_challenge, invalid_yaml)

        # Verify challenge was not modified
        db_session.refresh(existing_challenge)
        assert existing_challenge.name == initial_name
