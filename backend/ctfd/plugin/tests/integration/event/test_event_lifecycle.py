"""
/backend/ctfd/plugin/tests/integration/event/test_event_lifecycle.py
Complete event lifecycle and management workflows.
"""

import time
import pytest
from datetime import datetime, timedelta
from tests.helpers import gen_user as gen_user_original
from plugin.event.controllers.create_event import create_event
from plugin.event.controllers.update_event import update_event
from plugin.event.controllers.list_events import list_events
from plugin.team.controllers.create_team import create_team
from plugin.team.controllers.join_team import join_team
from plugin.team.controllers.leave_team import leave_team
from plugin.event.models.Event import Event
from plugin.team.models.Team import Team
from plugin.team.models.TeamMember import TeamMember


class DBWrapper:
    def __init__(self, session):
        self.session = session


def gen_unique_user(db_wrapper):
    """Generate a user with unique email to avoid conflicts."""
    timestamp = str(int(time.time() * 1000000))
    return gen_user_original(db_wrapper, name=f"user_{timestamp}", email=f"user_{timestamp}@example.com")


@pytest.mark.db
def test_event_creation_with_teams_cascade(db_session):
    """Test event creation and its impact on team creation."""
    db_wrapper = DBWrapper(db_session)

    # Create event with specific constraints
    now = datetime.utcnow()
    start_time = now + timedelta(hours=1)
    end_time = now + timedelta(hours=5)

    event_result = create_event(
        name="Scheduled Event",
        description="Event with time constraints",
        max_team_size=4,
        start_time=start_time,
        end_time=end_time,
        locked=False,
    )

    assert event_result["success"]
    event_id = event_result["event"]["id"]

    captain1 = gen_unique_user(db_wrapper)
    captain2 = gen_unique_user(db_wrapper)

    team1_result = create_team("Team Alpha", event_id, captain1.id)
    team2_result = create_team("Team Beta", event_id, captain2.id)

    assert team1_result["success"]
    assert team2_result["success"]

    member1 = gen_unique_user(db_wrapper)
    member2 = gen_unique_user(db_wrapper)
    member3 = gen_unique_user(db_wrapper)
    member4 = gen_unique_user(db_wrapper)

    join_team(member1.id, team1_result["invite_code"])
    join_team(member2.id, team1_result["invite_code"])
    join_team(member3.id, team1_result["invite_code"])

    overfill_result = join_team(member4.id, team1_result["invite_code"])
    assert not overfill_result["success"]
    assert "full" in overfill_result["error"]


@pytest.mark.db
def test_event_locking_prevents_new_teams(db_session):
    """Test that locking an event prevents new team creation."""
    db_wrapper = DBWrapper(db_session)

    event_result = create_event(
        name="Lock Test Event",
        description="Event to test locking",
        max_team_size=5,
        locked=False,
    )

    assert event_result["success"]
    event_id = event_result["event"]["id"]

    captain1 = gen_unique_user(db_wrapper)
    team1_result = create_team("Pre-Lock Team", event_id, captain1.id)
    assert team1_result["success"]

    lock_result = update_event(event_id=event_id, locked=True)
    assert lock_result["success"]

    captain2 = gen_unique_user(db_wrapper)
    team2_result = create_team("Post-Lock Team", event_id, captain2.id)
    assert not team2_result["success"]
    assert "locked" in team2_result["error"]

    member = gen_unique_user(db_wrapper)
    join_team(member.id, team1_result["invite_code"])


@pytest.mark.db
def test_event_max_team_size_update_validation(db_session):
    """Test validation when updating event max_team_size with existing teams."""
    db_wrapper = DBWrapper(db_session)

    event_result = create_event(
        name="Size Update Event",
        description="Event for testing size updates",
        max_team_size=6,
        locked=False,
    )

    event_id = event_result["event"]["id"]

    captain = gen_unique_user(db_wrapper)
    team_result = create_team("Large Team", event_id, captain.id)

    members = [gen_unique_user(db_wrapper) for _ in range(3)]
    for member in members:
        join_result = join_team(member.id, team_result["invite_code"])
        assert join_result["success"]

    update_result = update_event(event_id=event_id, max_team_size=2)

    if update_result["success"]:
        new_member = gen_unique_user(db_wrapper)
        join_result = join_team(new_member.id, team_result["invite_code"])
        assert not join_result["success"]
    else:
        assert "team" in update_result["error"] or "size" in update_result["error"]


@pytest.mark.db
def test_event_time_constraint_updates(db_session):
    """Test updating event time constraints."""

    now = datetime.utcnow()
    original_start = now + timedelta(hours=2)
    original_end = now + timedelta(hours=6)

    event_result = create_event(
        name="Time Update Event",
        description="Event for testing time updates",
        max_team_size=4,
        start_time=original_start,
        end_time=original_end,
        locked=False,
    )

    event_id = event_result["event"]["id"]

    new_start = now + timedelta(hours=1)
    new_end = now + timedelta(hours=4)

    update_result = update_event(event_id=event_id, start_time=new_start, end_time=new_end)
    assert update_result["success"]

    single_update_result = update_event(event_id=event_id, start_time=now + timedelta(hours=3))
    assert single_update_result["success"]

    invalid_order_result = update_event(
        event_id=event_id,
        start_time=now + timedelta(hours=5),
        end_time=now + timedelta(hours=2),
    )

    if invalid_order_result["success"]:
        assert invalid_order_result["event"]["start_time"] is not None
    else:
        assert "time" in invalid_order_result["error"].lower()


@pytest.mark.db
def test_event_deletion_cleanup_cascade(db_session):
    """Test proper cleanup when event is deleted."""
    db_wrapper = DBWrapper(db_session)

    event_result = create_event(
        name="Deletion Test Event",
        description="Event to test deletion cascade",
        max_team_size=5,
        locked=False,
    )

    event_id = event_result["event"]["id"]

    captain1 = gen_unique_user(db_wrapper)
    captain2 = gen_unique_user(db_wrapper)
    member1 = gen_unique_user(db_wrapper)
    member2 = gen_unique_user(db_wrapper)

    team1_result = create_team("Team 1", event_id, captain1.id)
    team2_result = create_team("Team 2", event_id, captain2.id)

    join_team(member1.id, team1_result["invite_code"])
    join_team(member2.id, team2_result["invite_code"])

    teams_before = Team.query.filter_by(event_id=event_id).count()
    members_before = TeamMember.query.filter_by(event_id=event_id).count()

    assert teams_before == 2
    assert members_before == 4

    event = Event.query.get(event_id)

    TeamMember.query.filter_by(event_id=event_id).delete()
    Team.query.filter_by(event_id=event_id).delete()
    db_session.delete(event)
    db_session.commit()

    teams_after = Team.query.filter_by(event_id=event_id).count()
    members_after = TeamMember.query.filter_by(event_id=event_id).count()

    assert teams_after == 0
    assert members_after == 0


@pytest.mark.db
def test_multi_event_scenario_isolation(db_session):
    """Test complex scenario with multiple events and cross-event operations."""
    db_wrapper = DBWrapper(db_session)

    event1_result = create_event(
        name="Small Teams Event",
        description="Event with small teams",
        max_team_size=2,
        locked=False,
    )

    event2_result = create_event(
        name="Large Teams Event",
        description="Event with large teams",
        max_team_size=8,
        locked=False,
    )

    event3_result = create_event(
        name="Locked Event",
        description="Pre-locked event",
        max_team_size=4,
        locked=True,
    )

    event1_id = event1_result["event"]["id"]
    event2_id = event2_result["event"]["id"]
    event3_id = event3_result["event"]["id"]

    captain = gen_unique_user(db_wrapper)

    team1_result = create_team("Small Team", event1_id, captain.id)
    team2_result = create_team("Large Team", event2_id, captain.id)

    assert team1_result["success"]
    assert team2_result["success"]

    team3_result = create_team("Locked Team", event3_id, captain.id)
    assert not team3_result["success"]

    member1 = gen_unique_user(db_wrapper)
    member2 = gen_unique_user(db_wrapper)
    member3 = gen_unique_user(db_wrapper)

    join_result1 = join_team(member1.id, team1_result["invite_code"])
    assert join_result1["success"]

    overfill_result = join_team(member2.id, team1_result["invite_code"])
    assert not overfill_result["success"]

    join_result2 = join_team(member2.id, team2_result["invite_code"])
    join_result3 = join_team(member3.id, team2_result["invite_code"])
    assert join_result2["success"]
    assert join_result3["success"]

    leave_result = leave_team(captain.id, event1_id)
    assert not leave_result["success"]
    assert "cannot leave" in leave_result["error"].lower()

    captain_membership1 = TeamMember.query.filter_by(user_id=captain.id, event_id=event1_id).first()
    captain_membership2 = TeamMember.query.filter_by(user_id=captain.id, event_id=event2_id).first()
    assert captain_membership1 is not None
    assert captain_membership2 is not None

    team1_check = Team.query.get(team1_result["team"].id)
    assert team1_check is not None

    team2_check = Team.query.get(team2_result["team"].id)
    assert team2_check is not None


@pytest.mark.db
def test_event_listing_and_statistics(db_session):
    """Test event listing with statistics and filtering."""
    db_wrapper = DBWrapper(db_session)

    active_event = create_event(
        name="Active Event",
        description="Currently active event",
        max_team_size=5,
        locked=False,
    )

    create_event(name="Locked Event", description="Locked event", max_team_size=3, locked=True)

    captain1 = gen_unique_user(db_wrapper)
    captain2 = gen_unique_user(db_wrapper)

    create_team("Team A", active_event["event"]["id"], captain1.id)
    create_team("Team B", active_event["event"]["id"], captain2.id)

    events_result = list_events()
    assert events_result["success"]

    events = events_result["events"]
    assert len(events) >= 2

    active_found = None
    locked_found = None

    for event in events:
        if event["name"] == "Active Event":
            active_found = event
        elif event["name"] == "Locked Event":
            locked_found = event

    assert active_found is not None
    assert locked_found is not None

    assert active_found["team_count"] >= 2
    assert active_found["total_members"] >= 2
    assert active_found["locked"] is False

    assert locked_found["team_count"] == 0
    assert locked_found["total_members"] == 0
    assert locked_found["locked"] is True
