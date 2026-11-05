from CTFd.models import db
from ...models import Challenge
from ....containers.models.ContainerInstance import ContainerInstance
from ....notifications.models import Notification
from ....scoring.models import HintRedemption
from ...models import Hint
from ....event.models.Event import Event
from ....support.models.Ticket import Ticket
from ....scoring.models.Attempt import Attempt
from ....feedback.models.Feedback import Feedback
from ....core import BusinessLogicError
from ....core.utils.environment import get_environment

def delete_challenge(challenge: Challenge):
    """
    Delete a specific challenge and all its linked objects. DEV / STAGING only
    """
    environment = get_environment()

    # Only allow deletion of challenges in 'development' and 'staging', NOT production due to the wide destruction needed
    if environment == 'production':
        raise BusinessLogicError("Challenge deletion is not allowed in production.")

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

    # Delete all notifications related to the challenge or related to the tickets we deleted
    '''
    The notification model has a challenge_id field but the notif is not actually linked to the challenge in any way.
    I've included it as a condition here in case we properly utilize it in the future
    '''
    notification = db.delete(Notification).where(
        db.or_(
            Notification.challenge_id == challenge.id,
            Notification.ticket_id.in_(
                db.select(Ticket.id).where(
                    Ticket.challenge_id == challenge.id
                )
            ),
        )
    ).execution_options(synchronize_session=False)
    db.session.execute(notification)

    # Delete tickets associated with the challenge
    tickets = db.delete(Ticket).where(
        Ticket.challenge_id == challenge.id
    )
    db.session.execute(tickets)

    # Delete all HintRedemptions related to the challenge
    # Hints themselves will be deleted by cascade when the challenge is deleted
    hint_redemptions = db.delete(HintRedemption).where(
        HintRedemption.hint_id.in_(
            db.select(Hint.id).where(
                Hint.challenge_id == challenge.id
            )
        )
    ).execution_options(synchronize_session=False)
    db.session.execute(hint_redemptions)

    # Delete attempt scoring
    attempts = db.delete(Attempt).where(
        Attempt.challenge_id == challenge.id
    )
    db.session.execute(attempts)

    # Delete Challenge Feedback
    feedbacks = db.delete(Feedback).where(
        Feedback.challenge_id == challenge.id
    )
    db.session.execute(feedbacks)

    # Delete the challenge itself. This will cascade to most of it's properties
    db.session.delete(challenge)

    # Save all changes
    db.session.commit()
