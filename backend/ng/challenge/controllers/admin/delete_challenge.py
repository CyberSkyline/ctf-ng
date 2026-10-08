from CTFd.models import db
from ...models import Challenge
from ....containers.models.ContainerInstance import ContainerInstance
from ....notifications.models import Notification
from ....event.models.Event import Event
from ....support.models.Ticket import Ticket
from ....scoring.models.Attempt import Attempt
from ....feedback.models.Feedback import Feedback
from ....core import BusinessLogicError
from flask import current_app as app

def delete_challenge(challenge: Challenge):
    """
    Delete a specific challenge and all its linked objects. DEV mode only
    """

    # Only allow deletion of challenges in DEV mode
    if not app.debug:
        raise BusinessLogicError("Challenge deletion is only allowed in DEV mode.")

    # Delete Challenge on Event
    event = db.session.get(Event, challenge.event_id)
    if not event:
        raise BusinessLogicError(f"Event with ID {challenge.event_id} does not exist.")

    # Delete Deployment for each team in the event associated with the challenge
    # call the regular delete instead on blueprint
    for blueprint in challenge.blueprints:
        instances = db.session.scalars(
            db.select(ContainerInstance).where(
                ContainerInstance.blueprint == blueprint.id
            )
        ).all()

        for instance in instances:
            instance.delete(remove_docker_ctr=True, commit=False)

    # Delete tickets associated with the challenge
    tickets = db.session.scalars(
        db.select(Ticket).where(
            Ticket.challenge_id == challenge.id
        )
    ).all()

    for ticket in tickets:
        db.session.delete(ticket)

    # Delete all notifications related to the challenge or related to the tickets we deleted
    '''
    The notification model has a challenge_id field but the notif is not actually linked to the challenge in any way.
    I've included it as a condition here in case we properly utilize it in the future
    '''
    notifications = db.session.scalars(
        db.select(Notification).where(
            db.or_(
                Notification.challenge_id == challenge.id,
                Notification.ticket_id.in_(
                    db.select(Ticket.id).where(
                        Ticket.challenge_id == challenge.id
                    )
                ),
            )
        )
    ).all()

    for notification in notifications:
        db.session.delete(notification)

    # Delete attempt scoring
    attempts = db.session.scalars(
        db.select(Attempt).where(
            Attempt.challenge_id == challenge.id
        )
    ).all()

    for attempt in attempts:
        db.session.delete(attempt)

    # Delete Challenge Feedback
    feedbacks = db.session.scalars(
        db.select(Feedback).where(
            Feedback.challenge_id == challenge.id
        )
    ).all()

    for feedback in feedbacks:
        db.session.delete(feedback)


    # Delete the challenge itself. This will cascade to most of it's properties
    db.session.delete(challenge)

    # Save all changes
    db.session.commit()
