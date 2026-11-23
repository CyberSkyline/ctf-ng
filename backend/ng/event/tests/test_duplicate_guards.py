"""
Tests the checks that keep a duplicate off the database constraints.

A conflict the caller can resolve answers 409. Reaching the constraint itself
means a check was missed, which the error handler reports as a 500, so these
pin the checks that keep ordinary duplicates out of Sentry.
"""

import pytest

from ...core.exceptions import ConflictError
from ..models.Demographic import Demographic
from ..models.Event import Event


@pytest.mark.db
class TestEventNameConflict:
    def test_a_taken_event_name_conflicts(self, db_session, event_factory):
        existing = event_factory()

        with pytest.raises(ConflictError):
            Event.create_event(name=existing.name)

    def test_a_free_event_name_is_created(self, db_session, event_factory):
        event_factory(name="Qualifier")

        event = Event.create_event(name="Finals")

        assert event.id is not None


@pytest.mark.db
class TestDemographicConflict:
    def test_registering_twice_for_an_event_conflicts(self, db_session, event_factory, user_factory):
        event = event_factory()
        user = user_factory()
        Demographic.create_demographic(user_id=user.id, event_id=event.id)

        with pytest.raises(ConflictError):
            Demographic.create_demographic(user_id=user.id, event_id=event.id)

    def test_the_same_user_can_register_for_a_second_event(self, db_session, event_factory, user_factory):
        first, second = event_factory(), event_factory()
        user = user_factory()
        Demographic.create_demographic(user_id=user.id, event_id=first.id)

        registration = Demographic.create_demographic(user_id=user.id, event_id=second.id)

        assert registration.event_id == second.id
