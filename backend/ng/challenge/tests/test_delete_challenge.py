import pytest
from ...core.utils import utc_now
from ..models import Challenge
from ...challenge.models.ContainerBlueprint import ContainerBlueprint
from ...notifications.models import Notification
from ...event.models.Event import Event
from ...support.models.Ticket import Ticket
from ...scoring.models.Attempt import Attempt
from ...feedback.models.Feedback import Feedback
from ..controllers.admin.delete_challenge import delete_challenge

@pytest.mark.db
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

    # Delete the challenge
    delete_challenge(challenge)

    # Check that the challenge is deleted
    assert db_session.get(Challenge, challenge.id) is None

    # Check that related objects are deleted
    assert db_session.get(Ticket, ticket.id) is None

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

    # Delete the challenge
    delete_challenge(challenge)

    # Check that the challenge is deleted
    assert db_session.get(Challenge, challenge.id) is None

    # Check that related notifications are deleted
    assert db_session.get(Notification, notification.id) is None

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

    # Delete the challenge
    delete_challenge(challenge)

    # Check that the challenge is deleted
    assert db_session.get(Challenge, challenge.id) is None

    # Check that related attempts are deleted
    assert db_session.get(Attempt, attempt.id) is None

def test_delete_challenge_related_feedback(challenge, user, feedback_factory, db_session):
    """Test that deleting a challenge removes related feedback."""
    # Create feedback related to the challenge
    feedback = feedback_factory(
        user_id=user.id,
        challenge_id=challenge.id,
        event_id=challenge.event_id,
    )

    # Delete the challenge
    delete_challenge(challenge)

    # Check that the challenge is deleted
    assert db_session.get(Challenge, challenge.id) is None

    # Check that related feedback is deleted
    assert db_session.get(Feedback, feedback.id) is None
