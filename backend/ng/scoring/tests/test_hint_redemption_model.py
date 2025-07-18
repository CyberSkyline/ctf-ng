"""
Tests for the HintRedemption model
"""

import pytest
from unittest.mock import patch
from datetime import datetime

from ..models.HintRedemption import HintRedemption
from ..models.ScoreEvent import ScoreEvent
from ..models.Score import Score


@pytest.fixture(autouse=True)
def clear_score_cache():
    """Clear the memoize cache before each test"""
    from ...core.utils.cache import _cache

    _cache.clear()
    yield
    _cache.clear()


class TestHintRedemptionRepr:
    """Test the HintRedemption model string representation"""

    def test_repr(self, db_session, hint_redemption_factory, user, team_with_member, hint):
        redemption = hint_redemption_factory(hint_id=hint.id, user_id=user.id, team_id=team_with_member.id, points=-20)
        expected = f"<HintRedemption {redemption.id}: team={team_with_member.id} hint={hint.id}>"
        assert repr(redemption) == expected


class TestCreateRedemption:
    """Test the create_redemption method"""

    def test_create_redemption_defaults(self, db_session, hint, user, team_with_member, score, event, challenge):
        """Test creating a hint redemption with default values"""
        try:
            redemption = HintRedemption.create_redemption(
                hint_id=hint.id,
                user_id=user.id,
                team_id=team_with_member.id,
                event_id=event.id,
                challenge_id=challenge.id,
            )
        except Exception as e:
            if hasattr(e, "errors"):
                print(f"Validation errors: {e.errors}")
            raise

        assert redemption.hint_id == hint.id
        assert redemption.user_id == user.id
        assert redemption.team_id == team_with_member.id
        assert redemption.points == -hint.deduction  # Should be negative
        assert isinstance(redemption.timestamp, datetime)

        # Should have created a score event
        assert redemption.score_event_id is not None
        score_event = ScoreEvent.query.get(redemption.score_event_id)
        assert score_event is not None
        assert score_event.points == -hint.deduction

        # Score should be updated
        db_session.refresh(score)
        assert score.points == -hint.deduction

        # Verify it's persisted
        found_redemption = HintRedemption.query.filter_by(id=redemption.id).first()
        assert found_redemption is not None

    def test_create_redemption_zero_deduction(self, db_session, user, team_with_member, event, challenge):
        """Test creating a redemption for a hint with zero deduction"""
        from ...challenge.models.Hint import Hint

        # Create hint with zero deduction
        free_hint = Hint(challenge_id=challenge.id, preview="Free hint", body="This is a free hint", deduction=0)
        db_session.add(free_hint)
        db_session.commit()

        redemption = HintRedemption.create_redemption(
            hint_id=free_hint.id,
            user_id=user.id,
            team_id=team_with_member.id,
            event_id=event.id,
            challenge_id=challenge.id,
        )

        assert redemption.points == 0
        # Should NOT have created a score event for zero points
        assert redemption.score_event_id is None

    def test_create_redemption_with_timestamp(self, db_session, hint, user, team_with_member, event, challenge):
        """Test creating a redemption with custom timestamp"""
        custom_time = datetime(2024, 1, 1, 12, 0, 0)

        redemption = HintRedemption.create_redemption(
            hint_id=hint.id,
            user_id=user.id,
            team_id=team_with_member.id,
            event_id=event.id,
            challenge_id=challenge.id,
            timestamp=custom_time,
        )

        assert redemption.timestamp == custom_time

    def test_create_redemption_no_commit(self, db_session, hint, user, team_with_member, event, challenge):
        """Test creating a redemption without committing"""
        with patch.object(db_session, "commit") as mock_commit:
            redemption = HintRedemption.create_redemption(
                hint_id=hint.id,
                user_id=user.id,
                team_id=team_with_member.id,
                event_id=event.id,
                challenge_id=challenge.id,
                commit=False,
            )
            mock_commit.assert_not_called()

        # Should still be in session
        assert redemption in db_session

    def test_create_redemption_with_commit(self, db_session, hint, user, team_with_member, event, challenge):
        """Test creating a redemption with commit"""
        with patch.object(db_session, "commit") as mock_commit:
            HintRedemption.create_redemption(
                hint_id=hint.id,
                user_id=user.id,
                team_id=team_with_member.id,
                event_id=event.id,
                challenge_id=challenge.id,
                commit=True,
            )
            mock_commit.assert_called_once()

    def test_create_redemption_already_redeemed_fails(self, db_session, hint, user, team_with_member, event, challenge):
        """Test that redeeming same hint twice fails"""
        from ...core.exceptions import BusinessLogicError

        # First redemption should succeed
        HintRedemption.create_redemption(
            hint_id=hint.id, user_id=user.id, team_id=team_with_member.id, event_id=event.id, challenge_id=challenge.id
        )

        # Second redemption should fail
        with pytest.raises(BusinessLogicError) as exc_info:
            HintRedemption.create_redemption(
                hint_id=hint.id,
                user_id=user.id,
                team_id=team_with_member.id,
                event_id=event.id,
                challenge_id=challenge.id,
            )

        assert "already been redeemed" in str(exc_info.value)

    def test_create_redemption_invalid_hint_fails(self, db_session, user, team_with_member, event, challenge):
        """Test that creating a redemption with invalid hint fails"""
        from ...core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            HintRedemption.create_redemption(
                hint_id=999999,  # Non-existent
                user_id=user.id,
                team_id=team_with_member.id,
                event_id=event.id,
                challenge_id=challenge.id,
            )

    def test_create_redemption_for_locked_event_fails(self, db_session, hint, user, locked_event, challenge):
        """Test that creating a redemption for locked event fails"""
        from ...core.exceptions import BusinessLogicError
        from ...team.models.Team import Team

        # Create a team for the locked event
        locked_team = Team.create_team_with_captain(
            name="Locked Team", event_id=locked_event.id, captain_id=user.id, invite_code="locked123"
        )

        with pytest.raises(BusinessLogicError) as exc_info:
            HintRedemption.create_redemption(
                hint_id=hint.id,
                user_id=user.id,
                team_id=locked_team.id,
                event_id=locked_event.id,
                challenge_id=challenge.id,
            )

        assert "Cannot redeem hints for a locked event" in str(exc_info.value)


class TestDeleteRedemption:
    """Test the delete_redemption method"""

    def test_delete_redemption_with_score_event(
        self, db_session, hint, user, team_with_member, score, event, challenge
    ):
        """Test that deleting a redemption deletes its score event"""
        # Create a redemption
        redemption = HintRedemption.create_redemption(
            hint_id=hint.id, user_id=user.id, team_id=team_with_member.id, event_id=event.id, challenge_id=challenge.id
        )

        score_event_id = redemption.score_event_id
        assert score_event_id is not None

        # Score should be negative
        db_session.refresh(score)
        assert score.points == -hint.deduction

        # Delete the redemption
        redemption.delete_redemption()

        # Redemption should be deleted
        assert HintRedemption.query.get(redemption.id) is None

        # Score event should also be deleted
        assert ScoreEvent.query.get(score_event_id) is None

        # Score should be adjusted back to 0
        db_session.refresh(score)
        assert score.points == 0

    def test_delete_redemption_without_score_event(self, db_session, user, team_with_member, event, challenge):
        """Test deleting a redemption with no score event (zero deduction)"""
        from ...challenge.models.Hint import Hint

        # Create hint with zero deduction
        free_hint = Hint(challenge_id=challenge.id, preview="Free hint", body="This is a free hint", deduction=0)
        db_session.add(free_hint)
        db_session.commit()

        # Create redemption
        redemption = HintRedemption.create_redemption(
            hint_id=free_hint.id,
            user_id=user.id,
            team_id=team_with_member.id,
            event_id=event.id,
            challenge_id=challenge.id,
        )

        assert redemption.score_event_id is None
        redemption_id = redemption.id

        # Delete the redemption
        redemption.delete_redemption()

        # Redemption should be deleted
        assert HintRedemption.query.get(redemption_id) is None

    def test_delete_redemption_no_commit(self, db_session, hint_redemption_factory, user, team_with_member, hint):
        """Test deleting a redemption without committing"""
        redemption = hint_redemption_factory(hint_id=hint.id, user_id=user.id, team_id=team_with_member.id)

        with patch.object(db_session, "commit") as mock_commit:
            redemption.delete_redemption(commit=False)
            mock_commit.assert_not_called()

    def test_delete_redemption_with_commit(self, db_session, hint_redemption_factory, user, team_with_member, hint):
        """Test deleting a redemption with commit"""
        redemption = hint_redemption_factory(hint_id=hint.id, user_id=user.id, team_id=team_with_member.id)

        with patch.object(db_session, "commit") as mock_commit:
            redemption.delete_redemption(commit=True)
            mock_commit.assert_called_once()


class TestFindByTeamAndHint:
    """Test the find_by_team_and_hint method"""

    def test_find_existing_redemption(self, db_session, hint_redemption_factory, team_with_member, hint, user):
        """Test finding an existing redemption"""
        redemption = hint_redemption_factory(hint_id=hint.id, team_id=team_with_member.id, user_id=user.id, points=-20)

        found = HintRedemption.find_by_team_and_hint(team_with_member.id, hint.id)
        assert found is not None
        assert found.id == redemption.id

    def test_find_nonexistent_redemption(self, db_session, team_with_member, hint):
        """Test finding a non-existent redemption"""
        found = HintRedemption.find_by_team_and_hint(team_with_member.id, hint.id)
        assert found is None


class TestFindFilteredRedemptions:
    """Test the find_filtered_redemptions method"""

    def test_find_by_team_id(
        self, db_session, hint_redemption_factory, user, team_with_member, team_factory, event, hint
    ):
        """Test filtering redemptions by team_id"""
        # Create another team
        other_team = team_factory(event=event)

        # Create redemptions for different teams
        hint_redemption_factory(hint_id=hint.id, user_id=user.id, team_id=team_with_member.id)
        hint_redemption_factory(hint_id=hint.id, user_id=user.id, team_id=other_team.id)

        # Find redemptions for specific team
        redemptions = HintRedemption.find_filtered_redemptions(team_id=team_with_member.id)

        assert len(redemptions) == 1
        assert redemptions[0].team_id == team_with_member.id

    def test_find_by_hint_id(self, db_session, hint_redemption_factory, user, team_with_member, hint, challenge):
        """Test filtering redemptions by hint_id"""
        from ...challenge.models.Hint import Hint

        # Create another hint
        other_hint = Hint(challenge_id=challenge.id, preview="Another hint", body="This is another hint", deduction=10)
        db_session.add(other_hint)
        db_session.commit()

        # Create redemptions for different hints
        hint_redemption_factory(hint_id=hint.id, user_id=user.id, team_id=team_with_member.id)
        hint_redemption_factory(hint_id=other_hint.id, user_id=user.id, team_id=team_with_member.id)

        # Find redemptions for specific hint
        redemptions = HintRedemption.find_filtered_redemptions(hint_id=hint.id)

        assert len(redemptions) == 1
        assert redemptions[0].hint_id == hint.id

    def test_find_by_challenge_id(self, db_session, hint_redemption_factory, user, team_with_member, hint, challenge):
        """Test filtering redemptions by challenge_id"""
        from ...challenge.models.Challenge import Challenge
        from ...challenge.models.Hint import Hint

        # Create another challenge and hint
        other_challenge = Challenge(
            name="Other Challenge", description="Another challenge", icon="icon2", summary="Summary 2"
        )
        db_session.add(other_challenge)
        db_session.commit()

        other_hint = Hint(
            challenge_id=other_challenge.id,
            preview="Other challenge hint",
            body="This is another challenge hint",
            deduction=15,
        )
        db_session.add(other_hint)
        db_session.commit()

        # Create redemptions for different challenges
        hint_redemption_factory(hint_id=hint.id, user_id=user.id, team_id=team_with_member.id)
        hint_redemption_factory(hint_id=other_hint.id, user_id=user.id, team_id=team_with_member.id)

        # Find redemptions for specific challenge
        redemptions = HintRedemption.find_filtered_redemptions(challenge_id=challenge.id)

        assert len(redemptions) == 1
        assert redemptions[0].hint.challenge_id == challenge.id

    def test_find_by_user_id(self, db_session, hint_redemption_factory, user, admin, team_with_member, hint, challenge):
        """Test filtering redemptions by user_id"""
        from ...challenge.models.Hint import Hint

        # Create another hint to avoid unique constraint
        other_hint = Hint(challenge_id=challenge.id, preview="Second hint", body="This is a second hint", deduction=10)
        db_session.add(other_hint)
        db_session.commit()

        # Create redemptions for different users
        hint_redemption_factory(hint_id=hint.id, user_id=user.id, team_id=team_with_member.id)
        hint_redemption_factory(hint_id=other_hint.id, user_id=admin.id, team_id=team_with_member.id)

        # Find redemptions for specific user
        redemptions = HintRedemption.find_filtered_redemptions(user_id=user.id)

        assert len(redemptions) == 1
        assert redemptions[0].user_id == user.id

    def test_find_ordered_by_timestamp_desc(
        self, db_session, hint_redemption_factory, user, team_with_member, hint, challenge
    ):
        """Test that redemptions are ordered by timestamp descending"""
        from ...challenge.models.Hint import Hint

        # Create multiple hints to avoid unique constraint
        hints = []
        for i in range(3):
            h = Hint(challenge_id=challenge.id, preview=f"Hint {i}", body=f"This is hint {i}", deduction=10 * (i + 1))
            db_session.add(h)
            hints.append(h)
        db_session.commit()

        # Create redemptions with different timestamps
        hint_redemption_factory(
            hint_id=hints[0].id, user_id=user.id, team_id=team_with_member.id, timestamp=datetime(2024, 1, 1, 10, 0, 0)
        )
        hint_redemption_factory(
            hint_id=hints[1].id, user_id=user.id, team_id=team_with_member.id, timestamp=datetime(2024, 1, 1, 12, 0, 0)
        )
        hint_redemption_factory(
            hint_id=hints[2].id, user_id=user.id, team_id=team_with_member.id, timestamp=datetime(2024, 1, 1, 11, 0, 0)
        )

        redemptions = HintRedemption.find_filtered_redemptions(user_id=user.id)

        # Should be ordered by timestamp descending
        assert len(redemptions) == 3
        assert redemptions[0].timestamp == datetime(2024, 1, 1, 12, 0, 0)
        assert redemptions[1].timestamp == datetime(2024, 1, 1, 11, 0, 0)
        assert redemptions[2].timestamp == datetime(2024, 1, 1, 10, 0, 0)


class TestHintRedemptionSerialization:
    """Test the serialize method"""

    def test_serialize_basic(self, db_session, hint_redemption_factory, user, team_with_member, hint):
        """Test basic serialization"""
        redemption = hint_redemption_factory(hint_id=hint.id, user_id=user.id, team_id=team_with_member.id, points=-20)

        data = redemption.serialize()

        assert data["id"] == redemption.id
        assert data["hint_id"] == hint.id
        assert data["user_id"] == user.id
        assert data["team_id"] == team_with_member.id
        assert data["points"] == -20
        assert data["score_event_id"] is None
        assert isinstance(data["timestamp"], str)
        assert data["timestamp"].endswith("Z")

    def test_serialize_with_admin_fields(self, db_session, hint_redemption_factory, user, team_with_member, hint):
        """Test serialization with admin fields (currently same as basic)"""
        redemption = hint_redemption_factory(hint_id=hint.id, user_id=user.id, team_id=team_with_member.id, points=-20)

        data = redemption.serialize(include_admin_fields=True)

        # Currently no additional admin fields
        assert "id" in data
        assert "hint_id" in data
        assert "points" in data


class TestHintRedemptionValidation:
    """Test the validate method"""

    def test_validate_valid_data(self, db_session, hint, user, team_with_member):
        """Test validation with valid data"""
        data = HintRedemption.validate(
            {"hint_id": hint.id, "user_id": user.id, "team_id": team_with_member.id, "points": -20}
        )

        assert data["hint_id"] == hint.id
        assert data["user_id"] == user.id
        assert data["team_id"] == team_with_member.id
        assert data["points"] == -20

    def test_validate_positive_points_fails(self, db_session, hint, user, team_with_member):
        """Test validation fails with positive points"""
        from ...core.exceptions import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            HintRedemption.validate(
                {
                    "hint_id": hint.id,
                    "user_id": user.id,
                    "team_id": team_with_member.id,
                    "points": 20,  # Positive
                }
            )

        assert "points" in exc_info.value.errors
        assert "must be zero or negative" in exc_info.value.errors["points"]

    def test_validate_zero_points(self, db_session, hint, user, team_with_member):
        """Test validation passes with zero points"""
        data = HintRedemption.validate(
            {"hint_id": hint.id, "user_id": user.id, "team_id": team_with_member.id, "points": 0}
        )

        assert data["points"] == 0

    def test_validate_missing_points(self, db_session, hint, user, team_with_member):
        """Test validation fails with missing points"""
        from ...core.exceptions import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            HintRedemption.validate({"hint_id": hint.id, "user_id": user.id, "team_id": team_with_member.id})

        assert "points" in exc_info.value.errors
        assert "Points value is required" in exc_info.value.errors["points"]

    def test_validate_non_integer_points(self, db_session, hint, user, team_with_member):
        """Test validation fails with non-integer points"""
        from ...core.exceptions import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            HintRedemption.validate(
                {
                    "hint_id": hint.id,
                    "user_id": user.id,
                    "team_id": team_with_member.id,
                    "points": "not a number",  # Non-numeric string
                }
            )

        assert "points" in exc_info.value.errors
        assert "Points must be a valid integer" in exc_info.value.errors["points"]


class TestValidateRedemptionAllowed:
    """Test the validate_redemption_allowed method"""

    def test_validate_redemption_allowed_success(self, db_session, hint, user, team_with_member, event, challenge):
        """Test validation passes for valid redemption"""
        # Should not raise any exception
        HintRedemption.validate_redemption_allowed(
            user_id=user.id, team_id=team_with_member.id, hint_id=hint.id, event_id=event.id, challenge_id=challenge.id
        )

    def test_validate_redemption_locked_event(self, db_session, hint, user, locked_event, challenge):
        """Test validation fails for locked event"""
        from ...core.exceptions import BusinessLogicError
        from ...team.models.Team import Team

        # Create team for locked event
        locked_team = Team.create_team_with_captain(
            name="Locked Team", event_id=locked_event.id, captain_id=user.id, invite_code="locked123"
        )

        with pytest.raises(BusinessLogicError) as exc_info:
            HintRedemption.validate_redemption_allowed(
                user_id=user.id,
                team_id=locked_team.id,
                hint_id=hint.id,
                event_id=locked_event.id,
                challenge_id=challenge.id,
            )

        assert "Cannot redeem hints for a locked event" in str(exc_info.value)

    def test_validate_redemption_not_team_member(self, db_session, hint, admin, team_with_member, event, challenge):
        """Test validation fails when user is not team member"""
        from ...core.exceptions import BusinessLogicError

        with pytest.raises(BusinessLogicError) as exc_info:
            HintRedemption.validate_redemption_allowed(
                user_id=admin.id,  # Admin is not member of team_with_member
                team_id=team_with_member.id,
                hint_id=hint.id,
                event_id=event.id,
                challenge_id=challenge.id,
            )

        assert "User is not a member of this team" in str(exc_info.value)

    def test_validate_redemption_already_redeemed(self, db_session, hint, user, team_with_member, event, challenge):
        """Test validation fails when hint already redeemed"""
        from ...core.exceptions import BusinessLogicError

        # Create initial redemption
        HintRedemption.create_redemption(
            hint_id=hint.id, user_id=user.id, team_id=team_with_member.id, event_id=event.id, challenge_id=challenge.id
        )

        # Try to validate another redemption
        with pytest.raises(BusinessLogicError) as exc_info:
            HintRedemption.validate_redemption_allowed(
                user_id=user.id,
                team_id=team_with_member.id,
                hint_id=hint.id,
                event_id=event.id,
                challenge_id=challenge.id,
            )

        assert "already been redeemed" in str(exc_info.value)


class TestHintRedemptionRelationships:
    """Test the relationships"""

    def test_hint_relationship(self, db_session, hint_redemption_factory, user, team_with_member, hint):
        """Test the hint relationship"""
        redemption = hint_redemption_factory(hint_id=hint.id, user_id=user.id, team_id=team_with_member.id)

        assert redemption.hint == hint

    def test_user_relationship(self, db_session, hint_redemption_factory, user, team_with_member, hint):
        """Test the user relationship"""
        redemption = hint_redemption_factory(hint_id=hint.id, user_id=user.id, team_id=team_with_member.id)

        assert redemption.user.id == user.id

    def test_team_relationship(self, db_session, hint_redemption_factory, user, team_with_member, hint):
        """Test the team relationship"""
        redemption = hint_redemption_factory(hint_id=hint.id, user_id=user.id, team_id=team_with_member.id)

        assert redemption.team == team_with_member

    def test_score_event_relationship(self, db_session, hint, user, team_with_member, score, event, challenge):
        """Test the score_event relationship"""
        # Create redemption with deduction
        redemption = HintRedemption.create_redemption(
            hint_id=hint.id, user_id=user.id, team_id=team_with_member.id, event_id=event.id, challenge_id=challenge.id
        )

        assert redemption.score_event is not None
        assert redemption.score_event.points == -hint.deduction
