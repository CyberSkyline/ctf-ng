"""
Tests for the ManualPointAward model
"""

import pytest
from unittest.mock import patch
from datetime import datetime

from ..models.ManualPointAward import ManualPointAward
from ..models.ScoreEvent import ScoreEvent
from ..models.Score import Score


@pytest.fixture(autouse=True)
def clear_score_cache():
    """Clear the memoize cache before each test"""
    from ...core.utils.cache import _cache

    _cache.clear()
    yield
    _cache.clear()


class TestManualPointAwardRepr:
    """Test the ManualPointAward model string representation"""

    def test_repr(self, db_session, admin, team_with_member, event):
        try:
            award = ManualPointAward.create_award(
                admin_id=admin.id, team_id=team_with_member.id, points=100, reason="Good performance", event_id=event.id
            )
        except Exception as e:
            if hasattr(e, "errors"):
                print(f"Validation errors: {e.errors}")
            raise
        expected = f"<ManualPointAward {award.id}: team={team_with_member.id} points=100>"
        assert repr(award) == expected


class TestCreateAward:
    """Test the create_award method"""

    def test_create_award_positive_points(self, db_session, admin, team_with_member, score, event):
        """Test creating an award with positive points"""
        award = ManualPointAward.create_award(
            admin_id=admin.id,
            team_id=team_with_member.id,
            points=100,
            reason="Excellent sportsmanship",
            event_id=event.id,
        )

        assert award.admin_id == admin.id
        assert award.team_id == team_with_member.id
        assert award.points == 100
        assert award.reason == "Excellent sportsmanship"
        assert isinstance(award.timestamp, datetime)

        # Should have created a score event
        assert award.score_event_id is not None
        score_event = ScoreEvent.query.get(award.score_event_id)
        assert score_event is not None
        assert score_event.points == 100

        # Score should be updated
        db_session.refresh(score)
        assert score.points == 100

        # Verify it's persisted
        found_award = ManualPointAward.query.filter_by(id=award.id).first()
        assert found_award is not None

    def test_create_award_negative_points(self, db_session, admin, team_with_member, score, event):
        """Test creating an award with negative points (penalty)"""
        # Set initial points
        score.points = 200
        db_session.commit()

        award = ManualPointAward.create_award(
            admin_id=admin.id, team_id=team_with_member.id, points=-50, reason="Violation of rules", event_id=event.id
        )

        assert award.points == -50
        assert award.reason == "Violation of rules"

        # Score should be reduced
        db_session.refresh(score)
        assert score.points == 150

    def test_create_award_with_timestamp(self, db_session, admin, team_with_member, event):
        """Test creating an award with custom timestamp"""
        custom_time = datetime(2024, 1, 1, 12, 0, 0)

        award = ManualPointAward.create_award(
            admin_id=admin.id,
            team_id=team_with_member.id,
            points=100,
            reason="Test award",
            event_id=event.id,
            timestamp=custom_time,
        )

        assert award.timestamp == custom_time

    def test_create_award_no_commit(self, db_session, admin, team_with_member, event):
        """Test creating an award without committing"""
        with patch.object(db_session, "commit") as mock_commit:
            award = ManualPointAward.create_award(
                admin_id=admin.id,
                team_id=team_with_member.id,
                points=100,
                reason="Test award",
                event_id=event.id,
                commit=False,
            )
            mock_commit.assert_not_called()

        # Should still be in session
        assert award in db_session

    def test_create_award_with_commit(self, db_session, admin, team_with_member, event):
        """Test creating an award with commit"""
        with patch.object(db_session, "commit") as mock_commit:
            ManualPointAward.create_award(
                admin_id=admin.id,
                team_id=team_with_member.id,
                points=100,
                reason="Test award",
                event_id=event.id,
                commit=True,
            )
            mock_commit.assert_called_once()

    def test_create_award_zero_points_fails(self, db_session, admin, team_with_member, event):
        """Test that creating an award with zero points fails"""
        from ...core.exceptions import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            ManualPointAward.create_award(
                admin_id=admin.id, team_id=team_with_member.id, points=0, reason="Test award", event_id=event.id
            )

        assert "points" in exc_info.value.errors
        assert "Points cannot be zero" in exc_info.value.errors["points"]

    def test_create_award_non_admin_fails(self, db_session, user, team_with_member, event):
        """Test that non-admin cannot create awards"""
        from ...core.exceptions import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            ManualPointAward.create_award(
                admin_id=user.id,  # Regular user, not admin
                team_id=team_with_member.id,
                points=100,
                reason="Test award",
                event_id=event.id,
            )

        assert "admin_id" in exc_info.value.errors
        assert "must be an admin" in exc_info.value.errors["admin_id"]

    def test_create_award_invalid_team_fails(self, db_session, admin, event):
        """Test that creating an award with invalid team fails"""
        from ...core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            ManualPointAward.create_award(
                admin_id=admin.id,
                team_id=999999,  # Non-existent
                points=100,
                reason="Test award",
                event_id=event.id,
            )

    def test_create_award_creates_score_if_needed(self, db_session, admin, team_factory, event_factory, user_factory):
        """Test that creating an award automatically creates a score if one doesn't exist"""
        # Create a different event and team without score
        other_event = event_factory()
        captain = user_factory(name="NoScoreCaptain", email="noscorecapt@example.com")
        team_without_score = team_factory(event=other_event, members=[captain])

        # Delete the auto-created score
        score = Score.query.filter_by(team_id=team_without_score.id, event_id=other_event.id).first()
        if score:
            db_session.delete(score)
            db_session.commit()

        # Verify no score exists
        score = Score.query.filter_by(team_id=team_without_score.id, event_id=other_event.id).first()
        assert score is None

        # Create the award - should succeed and create a score
        award = ManualPointAward.create_award(
            admin_id=admin.id,
            team_id=team_without_score.id,
            points=100,
            reason="Test award",
            event_id=other_event.id,
        )

        # Verify award was created
        assert award is not None
        assert award.points == 100

        # Verify score was created automatically
        score = Score.query.filter_by(team_id=team_without_score.id, event_id=other_event.id).first()
        assert score is not None
        assert score.points == 100


class TestDeleteAward:
    """Test the delete_award method"""

    def test_delete_award_with_score_event(self, db_session, admin, team_with_member, score, event):
        """Test that deleting an award deletes its score event"""
        # Create an award
        award = ManualPointAward.create_award(
            admin_id=admin.id, team_id=team_with_member.id, points=100, reason="Test award", event_id=event.id
        )

        score_event_id = award.score_event_id
        assert score_event_id is not None

        # Score should be increased
        db_session.refresh(score)
        assert score.points == 100

        # Delete the award
        award.delete_award()

        # Award should be deleted
        assert ManualPointAward.query.get(award.id) is None

        # Score event should also be deleted
        assert ScoreEvent.query.get(score_event_id) is None

        # Score should be adjusted back to 0
        db_session.refresh(score)
        assert score.points == 0

    def test_delete_award_no_commit(self, db_session, admin, team_with_member, event):
        """Test deleting an award without committing"""
        award = ManualPointAward.create_award(
            admin_id=admin.id, team_id=team_with_member.id, points=100, reason="Test award", event_id=event.id
        )

        with patch.object(db_session, "commit") as mock_commit:
            award.delete_award(commit=False)
            mock_commit.assert_not_called()

    def test_delete_award_with_commit(self, db_session, admin, team_with_member, event):
        """Test deleting an award with commit"""
        award = ManualPointAward.create_award(
            admin_id=admin.id, team_id=team_with_member.id, points=100, reason="Test award", event_id=event.id
        )

        with patch.object(db_session, "commit") as mock_commit:
            award.delete_award(commit=True)
            mock_commit.assert_called_once()


class TestFindFilteredAwards:
    """Test the find_filtered_awards method"""

    def test_find_by_team_id(self, db_session, admin, team_with_member, team_factory, event, user_factory):
        """Test filtering awards by team_id"""
        # Create another team
        other_captain = user_factory(name="FilterCapt1", email="filtercapt1@example.com")
        other_team = team_factory(event=event, members=[other_captain])

        # Create awards for different teams
        ManualPointAward.create_award(
            admin_id=admin.id, team_id=team_with_member.id, points=100, reason="Award 1", event_id=event.id
        )
        ManualPointAward.create_award(
            admin_id=admin.id, team_id=other_team.id, points=200, reason="Award 2", event_id=event.id
        )

        # Find awards for specific team
        awards = ManualPointAward.find_filtered_awards(team_id=team_with_member.id)

        assert len(awards) == 1
        assert awards[0].team_id == team_with_member.id

    def test_find_by_admin_id(self, db_session, admin, user, team_with_member, event):
        """Test filtering awards by admin_id"""
        # Create another admin
        from CTFd.models import Users

        other_admin = Users(name="admin2", email="admin2@example.com", password="password", type="admin")
        other_admin.verified = True
        db_session.add(other_admin)
        db_session.commit()

        # Create awards by different admins
        ManualPointAward.create_award(
            admin_id=admin.id, team_id=team_with_member.id, points=100, reason="Award 1", event_id=event.id
        )
        ManualPointAward.create_award(
            admin_id=other_admin.id, team_id=team_with_member.id, points=200, reason="Award 2", event_id=event.id
        )

        # Find awards by specific admin
        awards = ManualPointAward.find_filtered_awards(admin_id=admin.id)

        assert len(awards) == 1
        assert awards[0].admin_id == admin.id

    def test_find_by_event_id(self, db_session, admin, team_with_member, team_factory, event, event_factory, user_factory):
        """Test filtering awards by event_id"""
        # Create another event and team
        other_event = event_factory()
        other_captain = user_factory(name="FilterCapt2", email="filtercapt2@example.com")
        other_team = team_factory(event=other_event, members=[other_captain])

        # Create awards for teams in different events
        award1 = ManualPointAward.create_award(
            admin_id=admin.id, team_id=team_with_member.id, points=100, reason="Award 1", event_id=event.id
        )
        ManualPointAward.create_award(
            admin_id=admin.id, team_id=other_team.id, points=200, reason="Award 2", event_id=other_event.id
        )

        # Find awards for specific event
        awards = ManualPointAward.find_filtered_awards(event_id=event.id)

        assert len(awards) == 1
        assert awards[0].id == award1.id

    def test_find_with_limit(self, db_session, admin, team_with_member, event):
        """Test limiting results"""
        # Create multiple awards
        for i in range(5):
            ManualPointAward.create_award(
                admin_id=admin.id,
                team_id=team_with_member.id,
                points=(i + 1) * 10,
                reason=f"Award {i}",
                event_id=event.id,
            )

        # Find with limit
        awards = ManualPointAward.find_filtered_awards(team_id=team_with_member.id, limit=3)

        assert len(awards) == 3

    def test_find_ordered_by_timestamp_desc(self, db_session, admin, team_with_member, event):
        """Test that awards are ordered by timestamp descending"""
        # Create awards with different timestamps
        ManualPointAward.create_award(
            admin_id=admin.id,
            team_id=team_with_member.id,
            points=10,
            reason="Award 1",
            event_id=event.id,
            timestamp=datetime(2024, 1, 1, 10, 0, 0),
        )
        ManualPointAward.create_award(
            admin_id=admin.id,
            team_id=team_with_member.id,
            points=20,
            reason="Award 2",
            event_id=event.id,
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
        )
        ManualPointAward.create_award(
            admin_id=admin.id,
            team_id=team_with_member.id,
            points=30,
            reason="Award 3",
            event_id=event.id,
            timestamp=datetime(2024, 1, 1, 11, 0, 0),
        )

        awards = ManualPointAward.find_filtered_awards(team_id=team_with_member.id)

        # Should be ordered by timestamp descending
        assert len(awards) == 3
        assert awards[0].points == 20  # 12:00
        assert awards[1].points == 30  # 11:00
        assert awards[2].points == 10  # 10:00


class TestManualPointAwardSerialization:
    """Test the serialize method"""

    def test_serialize_basic(self, db_session, admin, team_with_member, event):
        """Test basic serialization"""
        award = ManualPointAward.create_award(
            admin_id=admin.id, team_id=team_with_member.id, points=100, reason="Test award", event_id=event.id
        )

        data = award.serialize()

        assert data["id"] == award.id
        assert data["admin_id"] == admin.id
        assert data["team_id"] == team_with_member.id
        assert data["points"] == 100
        assert data["reason"] == "Test award"
        assert data["score_event_id"] == award.score_event_id
        assert isinstance(data["timestamp"], str)
        assert data["timestamp"].endswith("Z")

    def test_serialize_with_admin_fields(self, db_session, admin, team_with_member, event):
        """Test serialization with admin fields"""
        award = ManualPointAward.create_award(
            admin_id=admin.id, team_id=team_with_member.id, points=100, reason="Test award", event_id=event.id
        )

        data = award.serialize(include_admin_fields=True)

        # Should include admin name
        assert "admin_name" in data
        assert data["admin_name"] == admin.name


class TestManualPointAwardValidation:
    """Test the validate method"""

    def test_validate_valid_data(self, db_session, admin, team_with_member):
        """Test validation with valid data"""
        data = ManualPointAward.validate(
            {"admin_id": admin.id, "team_id": team_with_member.id, "points": 100, "reason": "Good work"}
        )

        assert data["admin_id"] == admin.id
        assert data["team_id"] == team_with_member.id
        assert data["points"] == 100
        assert data["reason"] == "Good work"

    def test_validate_missing_admin_id(self, db_session, team_with_member):
        """Test validation fails with missing admin_id"""
        from ...core.exceptions import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            ManualPointAward.validate({"team_id": team_with_member.id, "points": 100, "reason": "Test award"})

        assert "admin_id" in exc_info.value.errors
        assert "Admin Id is required" in exc_info.value.errors["admin_id"]

    def test_validate_non_admin_user(self, db_session, user, team_with_member):
        """Test validation fails with non-admin user"""
        from ...core.exceptions import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            ManualPointAward.validate(
                {
                    "admin_id": user.id,  # Regular user
                    "team_id": team_with_member.id,
                    "points": 100,
                    "reason": "Test award",
                }
            )

        assert "admin_id" in exc_info.value.errors
        assert "must be an admin" in exc_info.value.errors["admin_id"]

    def test_validate_missing_points(self, db_session, admin, team_with_member):
        """Test validation fails with missing points"""
        from ...core.exceptions import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            ManualPointAward.validate({"admin_id": admin.id, "team_id": team_with_member.id, "reason": "Test award"})

        assert "points" in exc_info.value.errors
        assert "Points is required" in exc_info.value.errors["points"]

    def test_validate_zero_points(self, db_session, admin, team_with_member):
        """Test validation fails with zero points"""
        from ...core.exceptions import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            ManualPointAward.validate(
                {"admin_id": admin.id, "team_id": team_with_member.id, "points": 0, "reason": "Test award"}
            )

        assert "points" in exc_info.value.errors
        assert "Points cannot be zero" in exc_info.value.errors["points"]

    def test_validate_non_integer_points(self, db_session, admin, team_with_member):
        """Test validation fails with non-integer points"""
        from ...core.exceptions import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            ManualPointAward.validate(
                {
                    "admin_id": admin.id,
                    "team_id": team_with_member.id,
                    "points": "not a number",
                    "reason": "Test award",
                }
            )

        assert "points" in exc_info.value.errors
        assert "Points must be a valid integer" in exc_info.value.errors["points"]

    def test_validate_missing_reason(self, db_session, admin, team_with_member):
        """Test validation fails with missing reason"""
        from ...core.exceptions import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            ManualPointAward.validate({"admin_id": admin.id, "team_id": team_with_member.id, "points": 100})

        assert "reason" in exc_info.value.errors

    def test_validate_empty_reason(self, db_session, admin, team_with_member):
        """Test validation fails with empty reason"""
        from ...core.exceptions import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            ManualPointAward.validate(
                {
                    "admin_id": admin.id,
                    "team_id": team_with_member.id,
                    "points": 100,
                    "reason": "   ",  # Empty after strip
                }
            )

        assert "reason" in exc_info.value.errors


class TestManualPointAwardRelationships:
    """Test the relationships"""

    def test_admin_relationship(self, db_session, admin, team_with_member, event):
        """Test the admin relationship"""
        award = ManualPointAward.create_award(
            admin_id=admin.id, team_id=team_with_member.id, points=100, reason="Test award", event_id=event.id
        )

        assert award.admin == admin

    def test_team_relationship(self, db_session, admin, team_with_member, event):
        """Test the team relationship"""
        award = ManualPointAward.create_award(
            admin_id=admin.id, team_id=team_with_member.id, points=100, reason="Test award", event_id=event.id
        )

        assert award.team == team_with_member

    def test_score_event_relationship(self, db_session, admin, team_with_member, score, event):
        """Test the score_event relationship"""
        # Create award
        award = ManualPointAward.create_award(
            admin_id=admin.id, team_id=team_with_member.id, points=100, reason="Test award", event_id=event.id
        )

        assert award.score_event is not None
        assert award.score_event.points == 100
