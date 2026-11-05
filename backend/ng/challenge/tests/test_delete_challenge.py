import pytest
from ...core.utils import utc_now
from ...core import BusinessLogicError
from ..models import Challenge
from ...challenge.models.ContainerBlueprint import ContainerBlueprint
from ...notifications.models import Notification
from ...event.models.Event import Event
from ...support.models.Ticket import Ticket
from ...scoring.models.Attempt import Attempt
from ...scoring.models import HintRedemption
from ...feedback.models.Feedback import Feedback
from ..controllers.admin.delete_challenge import delete_challenge
from ..models import Hint
from ..models import ChallengeTag
from ..models import ChallengeVariable
from ..models import Question
from ..models import ChallengeYaml

@pytest.fixture(autouse=True)
def default_environment(request, set_environment):
    """Automatically run all tests in this file in development environment mode, except for the excluded tests"""
    excluded_tests = {
        "test_delete_challenge_production",
        "test_delete_challenge_staging",
    }

    if request.node.name in excluded_tests:
        yield
    else:
        with set_environment("development"):
            yield

@pytest.mark.db
def test_delete_challenge_production(challenge, set_environment):
    """Test that deleting a challenge in production raises an error."""
    with set_environment("production"):
        with pytest.raises(
            BusinessLogicError,
            match="Challenge deletion is not allowed in production."
        ):
            delete_challenge(challenge)

def test_delete_challenge_staging(challenge, db_session, set_environment):
    """Test that deleting a challenge in staging is allowed."""
    with set_environment("staging"):
        event = db_session.get(Event, challenge.event_id)
        assert challenge in event.challenges

        delete_challenge(challenge)

        db_session.refresh(event)
        assert challenge not in event.challenges
        assert db_session.get(Challenge, challenge.id) is None

def test_delete_challenge_from_event (challenge, db_session):
    """Test that deleting a challenge removes it from the event."""
    event = db_session.get(Event, challenge.event_id)
    assert challenge in event.challenges

    # Delete the challenge
    delete_challenge(challenge)

    # Refresh the event from the database
    db_session.refresh(event)
    assert challenge not in event.challenges
    assert db_session.get(Challenge, challenge.id) is None

def test_delete_challenge_related_blueprints(challenge, db_session):
    """Test that deleting a challenge removes related blueprints and container instances."""
    # Create a blueprint related to the challenge
    blueprint = ContainerBlueprint.create_container_blueprint(
        challenge_id=challenge.id,
        name="existing_service",
        image="nginx:latest",
        hostname="web",
    )

    challenge.blueprints = [blueprint]
    db_session.add(challenge)
    db_session.commit()

    # Delete the challenge
    delete_challenge(challenge)

    # Check that the challenge is deleted
    assert db_session.get(Challenge, challenge.id) is None

    # Check that related objects are deleted
    assert db_session.get(ContainerBlueprint, blueprint.id) is None

def test_delete_challenge_related_ticket(challenge, user, db_session):
    """Test that a challenge can be deleted and all related objects are removed."""
    # Create related ticket
    # Can't use the fixture for tickets because it doesn't specify challenge
    ticket = Ticket.create_ticket(
        subject="Test Ticket",
        challenge_id=challenge.id,
        author_id=user.id,
        event_id=challenge.event_id,
        commit=False
    )
    db_session.add(ticket)
    db_session.commit()

    ticket_id = ticket.id
    challenge_id = challenge.id

    # Delete the challenge
    delete_challenge(challenge)

    # Check that the challenge is deleted
    assert db_session.get(Challenge, challenge_id) is None

    # Check that related objects are deleted
    assert db_session.get(Ticket, ticket_id) is None

def test_delete_challenge_related_notifications(challenge, user, notification_factory, db_session):
    """Test that deleting a challenge removes related notifications."""
    # Create a notification related to the challenge
    notification = notification_factory(
        recipient_id=user.id,
        challenge_id=challenge.id,
        event_id=challenge.event_id,
        commit=False
    )
    db_session.add(notification)
    db_session.commit()

    notification_id = notification.id
    challenge_id = challenge.id

    # Delete the challenge
    delete_challenge(challenge)

    # Check that the challenge is deleted
    assert db_session.get(Challenge, challenge_id) is None

    # Check that related notifications are deleted
    assert db_session.get(Notification, notification_id) is None

def test_delete_challenge_related_hint_redemptions(challenge, hint_factory, hint_redemption_factory, user, team_factory, db_session):
    """Test that deleting a challenge deletes hint redemptions"""
    team = team_factory(event=challenge.event, members=[user])
    hint = hint_factory(challenge_id=challenge.id)
    redemption = hint_redemption_factory(
        hint_id=hint.id,
        user_id=user.id,
        team_id=team.id
    )

    redemption_id = redemption.id

    # Delete the challenge
    delete_challenge(challenge)

    # Verify hint redemption is deleted
    assert db_session.get(HintRedemption, redemption_id) is None

def test_delete_challenge_related_attempts(
    challenge,
    user,
    team_factory,
    question_factory,
    attempt_factory,
    db_session
):
    """Test that deleting a challenge removes related attempts."""

    team = team_factory(event_id = challenge.event_id, members = [user])
    team.set_start_timestamp(utc_now())

    # Create a question related to the challenge
    question = question_factory(
        challenge=challenge,
    )

    # Create an attempt related to the challenge
    attempt = attempt_factory(
        user_id=user.id,
        team_id=team.id,
        event_id=challenge.event_id,
        challenge_id=challenge.id,
        question_id=question.id,
        submission = question.answer,
        is_correct = True,
        points = 100,
    )

    challenge_id = challenge.id
    attempt_id = attempt.id

    # Delete the challenge
    delete_challenge(challenge)

    # Check that the challenge is deleted
    assert db_session.get(Challenge, challenge_id) is None

    # Check that related attempts are deleted
    assert db_session.get(Attempt, attempt_id) is None

def test_delete_challenge_related_feedback(challenge, user, feedback_factory, db_session):
    """Test that deleting a challenge removes related feedback."""
    # Create feedback related to the challenge
    feedback = feedback_factory(
        user_id=user.id,
        challenge_id=challenge.id,
        event_id=challenge.event_id,
    )

    challenge_id = challenge.id
    feedback_id = feedback.id

    # Delete the challenge
    delete_challenge(challenge)

    # Check that the challenge is deleted
    assert db_session.get(Challenge, challenge_id) is None

    # Check that related feedback is deleted
    assert db_session.get(Feedback, feedback_id) is None

def test_delete_challenge_cascades_yaml(challenge, db_session):
    """Test that deleting a challenge cascades to its ChallengeYaml record."""
    yaml = ChallengeYaml(
        challenge_id=challenge.id,
        body="test yaml content",
    )
    db_session.add(yaml)
    db_session.commit()

    # Verify YAML exists
    assert challenge.yaml is not None

    # Delete the challenge
    delete_challenge(challenge)

    # Verify YAML is deleted
    assert db_session.get(ChallengeYaml, yaml.id) is None

def test_delete_challenge_cascades_hints(challenge, hint_factory, db_session):
    """Test that deleting a challenge cascades to its Hint records."""
    # Create a hint related to the challenge
    hint = hint_factory(challenge_id=challenge.id)

    # Verify hint exists
    assert hint in challenge.hints

    # Delete the challenge
    delete_challenge(challenge)

    # Verify the hint is deleted
    assert db_session.get(Hint, hint.id) is None

def test_delete_challenge_cascades_tags(challenge, db_session):
    """Test that deleting a challenge cascades to its ChallengeTag records."""
    tag = ChallengeTag(
        challenge_id=challenge.id,
        name="test_tag"
    )
    db_session.add(tag)
    db_session.commit()

    # Verify tag exists
    assert tag in challenge.tags

    # Delete the challenge
    delete_challenge(challenge)

    # Verify tag is deleted
    assert db_session.get(ChallengeTag, tag.id) is None

def test_delete_challenge_cascades_questions(challenge_factory, db_session):
    """Test that deleting a challenge cascades to its Question records."""
    challenge = challenge_factory()

    question_ids = [
        question.id for question in challenge.questions
    ]

    # Verify Question records exist
    assert db_session.query(Question).filter(
        Question.challenge_id == challenge.id
    ).count() == 2

    # Delete the challenge
    delete_challenge(challenge)

    # Verify Question records are deleted
    for question_id in question_ids:
        assert db_session.query(Question).filter(
            Question.id == question_id
        ).first() is None

def test_delete_challenge_cascades_variables(challenge, variable_factory, db_session):
    """Test that deleting a challenge cascades to its ChallengeVariable records."""
    # Create a variable related to the challenge
    variable = variable_factory(challenge=challenge)

    # Verify variable exists
    assert variable in challenge.variables

    # Delete the challenge
    delete_challenge(challenge)

    # Verify the challenge variable is deleted
    assert db_session.get(ChallengeVariable, variable.id) is None
