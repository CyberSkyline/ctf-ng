"""
Tests the check that keeps a duplicate off uq_feedback_user_event_challenge.

The upsert controllers look for existing feedback and update it, so this guard
is the backstop for a caller that goes straight to the model: it answers a
duplicate with a 409 rather than letting the constraint raise, which the error
handler would report as a server failure.
"""

import pytest

from ...core.exceptions import ConflictError
from ..models.Feedback import Feedback


@pytest.mark.db
class TestFeedbackConflict:
    def test_a_second_challenge_feedback_conflicts(
        self, db_session, event_factory, user_factory, challenge_factory
    ):
        event = event_factory()
        user = user_factory()
        challenge = challenge_factory(event=event)
        Feedback.create_feedback(
            user_id=user.id,
            event_id=event.id,
            challenge_id=challenge.id,
            feedback_data={"rating": 5},
        )

        with pytest.raises(ConflictError):
            Feedback.create_feedback(
                user_id=user.id,
                event_id=event.id,
                challenge_id=challenge.id,
                feedback_data={"rating": 4},
            )

    def test_event_level_feedback_is_not_deduplicated(self, db_session, event_factory, user_factory):
        """
        SQL counts NULLs as distinct, so the constraint never fires without a
        challenge_id. The guard matches it rather than inventing a stricter
        rule, and the upsert controller is what keeps duplicates from arising.
        """
        event = event_factory()
        user = user_factory()
        Feedback.create_feedback(user_id=user.id, event_id=event.id, feedback_data={"rating": 5})

        second = Feedback.create_feedback(
            user_id=user.id, event_id=event.id, feedback_data={"rating": 4}
        )

        assert second.id is not None
