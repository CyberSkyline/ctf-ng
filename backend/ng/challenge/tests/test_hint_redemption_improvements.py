"""
Test cases for the improved hint redemption system.
Tests the complete flow: hiding/revealing hints based on redemption,
team-specific visibility, and proper API responses.
"""

import pytest
from unittest.mock import patch, MagicMock

from ..models.Hint import Hint
from ..models.Challenge import Challenge
from ...scoring.models import HintRedemption, Score
from ...scoring.controllers.user_actions.redeem_hint import redeem_hint


@pytest.mark.db
class TestHintVisibilityBeforeRedemption:
    """Test that hints are properly hidden before redemption."""

    def test_hint_body_hidden_before_redemption(self, db_session, challenge, team_with_member):
        """Test that hint body is hidden when not yet redeemed."""
        hint = Hint.create_hint(
            challenge_id=challenge.id,
            body="The secret is in the cookies",
            preview="Check the HTTP headers",
            deduction=20,
        )

        # Serialize for a team that hasn't redeemed
        serialized = hint.serialize(team=team_with_member)

        # Body should be None, preview should be visible
        assert serialized["body"] is None
        assert serialized["preview"] == "Check the HTTP headers"
        assert serialized["is_redeemed"] is False
        assert serialized["deduction"] == 20

    def test_multiple_teams_cannot_see_unredeemed_hints(
        self, db_session, challenge, team_factory, user_factory, event
    ):
        """Test that multiple teams cannot see hint bodies before redemption."""
        # Create users for teams
        user1 = user_factory(name="HintUser1", email="hintuser1@example.com")
        user2 = user_factory(name="HintUser2", email="hintuser2@example.com")

        team1 = team_factory(event=event, members=[user1])
        team2 = team_factory(event=event, members=[user2])

        hint = Hint.create_hint(
            challenge_id=challenge.id,
            body="Use SQL injection on the login form",
            preview="Database vulnerability",
            deduction=30,
        )

        # Neither team should see the body
        team1_view = hint.serialize(team=team1)
        team2_view = hint.serialize(team=team2)

        assert team1_view["body"] is None
        assert team2_view["body"] is None
        assert team1_view["is_redeemed"] is False
        assert team2_view["is_redeemed"] is False


@pytest.mark.db
class TestHintRedemptionFlow:
    """Test the complete hint redemption flow."""

    def test_successful_hint_redemption_reveals_body(
        self, db_session, challenge, team_with_member, user, event, score
    ):
        """Test that redeeming a hint reveals its body to that team only."""
        hint = Hint.create_hint(
            challenge_id=challenge.id,
            body="The flag format is FLAG{...}",
            preview="Flag format hint",
            deduction=15,
        )

        # Before redemption
        before = hint.serialize(team=team_with_member)
        assert before["body"] is None
        assert before["is_redeemed"] is False

        # Redeem the hint
        result = redeem_hint(
            event=event,
            challenge=challenge,
            hint=hint,
            team=team_with_member,
            current_user=user,
        )

        # Check the returned result
        assert result["body"] == "The flag format is FLAG{...}"
        assert result["is_redeemed"] is True
        assert result["preview"] == "Flag format hint"

        # After redemption, team should always see the body
        after = hint.serialize(team=team_with_member)
        assert after["body"] == "The flag format is FLAG{...}"
        assert after["is_redeemed"] is True

        # Check points were deducted
        db_session.refresh(score)
        assert score.points == -15

    def test_other_teams_cannot_see_redeemed_hints(
        self, db_session, challenge, team_with_member, team_factory, user_factory, user, event
    ):
        """Test that other teams cannot see hints redeemed by one team."""
        # Create user for other team
        other_user = user_factory(name="OtherTeamUser", email="otherteam@example.com")
        other_team = team_factory(event=event, members=[other_user])

        hint = Hint.create_hint(
            challenge_id=challenge.id,
            body="Check port 8080 for the admin panel",
            preview="Hidden service",
            deduction=25,
        )

        # Team 1 redeems the hint
        HintRedemption.create_redemption(
            hint_id=hint.id,
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
        )

        # Team 1 can see the body
        team1_view = hint.serialize(team=team_with_member)
        assert team1_view["body"] == "Check port 8080 for the admin panel"
        assert team1_view["is_redeemed"] is True

        # Other team CANNOT see the body
        other_team_view = hint.serialize(team=other_team)
        assert other_team_view["body"] is None
        assert other_team_view["is_redeemed"] is False
        assert other_team_view["preview"] == "Hidden service"  # Preview still visible

    def test_cannot_redeem_same_hint_twice(
        self, db_session, challenge, team_with_member, user, event
    ):
        """Test that a team cannot redeem the same hint twice."""
        hint = Hint.create_hint(
            challenge_id=challenge.id,
            body="Duplicate redemption test",
            preview="Test hint",
            deduction=10,
        )

        # First redemption succeeds
        first_result = redeem_hint(
            event=event,
            challenge=challenge,
            hint=hint,
            team=team_with_member,
            current_user=user,
        )
        assert first_result["is_redeemed"] is True

        # Second redemption should fail
        from ...core.exceptions import BusinessLogicError
        with pytest.raises(BusinessLogicError) as exc:
            redeem_hint(
                event=event,
                challenge=challenge,
                hint=hint,
                team=team_with_member,
                current_user=user,
            )
        assert "already been redeemed" in str(exc.value)


@pytest.mark.db
class TestChallengeRenderWithHintRedemption:
    """Test Challenge.render() with the improved hint system."""

    def test_challenge_render_shows_correct_hint_states(
        self, db_session, challenge, team_with_member, user
    ):
        """Test that Challenge.render() shows correct hint redemption states."""
        # Create 3 hints
        hints = []
        for i in range(3):
            hint = Hint.create_hint(
                challenge_id=challenge.id,
                body=f"Full body of hint {i+1}",
                preview=f"Preview of hint {i+1}",
                deduction=10 * (i+1),
            )
            hints.append(hint)

        # Redeem only the second hint (index 1)
        HintRedemption.create_redemption(
            hint_id=hints[1].id,
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
        )

        # Render the challenge
        rendered = challenge.render(team_with_member)

        # Check hints in rendered output
        rendered_hints = rendered["hints"]
        assert len(rendered_hints) == 3

        # Find each hint in the output
        for i, original_hint in enumerate(hints):
            rendered_hint = next(h for h in rendered_hints if h["id"] == original_hint.id)

            if i == 1:  # The redeemed hint
                assert rendered_hint["body"] == f"Full body of hint {i+1}"
                assert rendered_hint["is_redeemed"] is True
            else:  # Unredeemed hints
                assert rendered_hint["body"] is None
                assert rendered_hint["is_redeemed"] is False

            # All hints should show preview
            assert rendered_hint["preview"] == f"Preview of hint {i+1}"

    def test_challenge_render_for_different_teams(
        self, db_session, challenge, team_with_member, team_factory, user_factory, user, event
    ):
        """Test that different teams see different hint states in Challenge.render()."""
        # Create user for team2
        user2 = user_factory(name="Team2User", email="team2user@example.com")
        team2 = team_factory(event=event, members=[user2])

        # Create hints
        hint1 = Hint.create_hint(
            challenge_id=challenge.id,
            body="Team-specific body 1",
            preview="Hint 1",
            deduction=10,
        )
        hint2 = Hint.create_hint(
            challenge_id=challenge.id,
            body="Team-specific body 2",
            preview="Hint 2",
            deduction=20,
        )

        # Team 1 redeems hint1
        HintRedemption.create_redemption(
            hint_id=hint1.id,
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
        )

        # Team 2 redeems hint2
        HintRedemption.create_redemption(
            hint_id=hint2.id,
            user_id=user2.id,
            team_id=team2.id,
            challenge_id=challenge.id,
        )

        # Render for team 1
        team1_render = challenge.render(team_with_member)
        team1_hints = {h["id"]: h for h in team1_render["hints"]}

        # Team 1 sees hint1 body but not hint2 body
        assert team1_hints[hint1.id]["body"] == "Team-specific body 1"
        assert team1_hints[hint1.id]["is_redeemed"] is True
        assert team1_hints[hint2.id]["body"] is None
        assert team1_hints[hint2.id]["is_redeemed"] is False

        # Render for team 2
        team2_render = challenge.render(team2)
        team2_hints = {h["id"]: h for h in team2_render["hints"]}

        # Team 2 sees hint2 body but not hint1 body
        assert team2_hints[hint1.id]["body"] is None
        assert team2_hints[hint1.id]["is_redeemed"] is False
        assert team2_hints[hint2.id]["body"] == "Team-specific body 2"
        assert team2_hints[hint2.id]["is_redeemed"] is True


@pytest.mark.db
class TestHintRedemptionWithScoring:
    """Test hint redemption's impact on scoring."""

    def test_hint_redemption_deducts_points(
        self, db_session, challenge, team_with_member, user, event, score
    ):
        """Test that redeeming hints properly deducts points."""
        initial_points = 100
        score.points = initial_points
        db_session.commit()

        # Create hints with different deductions
        hint1 = Hint.create_hint(
            challenge_id=challenge.id,
            body="First hint",
            preview="Hint 1",
            deduction=10,
        )
        hint2 = Hint.create_hint(
            challenge_id=challenge.id,
            body="Second hint",
            preview="Hint 2",
            deduction=25,
        )

        # Redeem first hint
        redeem_hint(
            event=event,
            challenge=challenge,
            hint=hint1,
            team=team_with_member,
            current_user=user,
        )

        db_session.refresh(score)
        assert score.points == initial_points - 10

        # Redeem second hint
        redeem_hint(
            event=event,
            challenge=challenge,
            hint=hint2,
            team=team_with_member,
            current_user=user,
        )

        db_session.refresh(score)
        assert score.points == initial_points - 10 - 25

    def test_free_hint_no_deduction(
        self, db_session, challenge, team_with_member, user, event, score
    ):
        """Test that hints with zero deduction don't affect score."""
        initial_points = 50
        score.points = initial_points
        db_session.commit()

        # Create a free hint (zero deduction)
        # Note: This violates validation but testing edge case
        free_hint = Hint(
            challenge_id=challenge.id,
            body="Free hint body",
            preview="Free hint",
            deduction=0,
        )
        db_session.add(free_hint)
        db_session.commit()

        # Redeem the free hint
        result = redeem_hint(
            event=event,
            challenge=challenge,
            hint=free_hint,
            team=team_with_member,
            current_user=user,
        )

        # Score should not change
        db_session.refresh(score)
        assert score.points == initial_points

        # But hint should still be revealed
        assert result["body"] == "Free hint body"
        assert result["is_redeemed"] is True


@pytest.mark.db
class TestAdminHintVisibility:
    """Test admin visibility of hints."""

    def test_admin_sees_all_hint_bodies(
        self, db_session, challenge, team_with_member
    ):
        """Test that admins can see all hint bodies regardless of redemption."""
        hint = Hint.create_hint(
            challenge_id=challenge.id,
            body="Admin should see this",
            preview="Admin test",
            deduction=15,
        )

        # Admin serialization without team context
        admin_view = hint.serialize(include_admin_fields=True)

        assert admin_view["body"] == "Admin should see this"
        assert admin_view["preview"] == "Admin test"
        assert admin_view["is_redeemed"] is False  # No team context

    def test_admin_with_team_context_sees_redemption_state(
        self, db_session, challenge, team_with_member, user
    ):
        """Test that admin with team context sees actual redemption state."""
        hint = Hint.create_hint(
            challenge_id=challenge.id,
            body="Admin with team context",
            preview="Test",
            deduction=20,
        )

        # Create redemption
        HintRedemption.create_redemption(
            hint_id=hint.id,
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
        )

        # Admin view with team context
        admin_team_view = hint.serialize(
            team=team_with_member,
            include_admin_fields=True
        )

        assert admin_team_view["body"] == "Admin with team context"
        assert admin_team_view["is_redeemed"] is True  # Shows actual state


@pytest.mark.db
class TestHintRedemptionEdgeCases:
    """Test edge cases and error conditions."""

    def test_hint_redemption_for_wrong_challenge_fails(
        self, db_session, challenge, team_with_member, user, event
    ):
        """Test that hint redemption fails if hint doesn't belong to challenge."""
        # Create another challenge
        other_challenge = Challenge.create_challenge(
            name="Other Challenge",
            event_id=event.id,
        )

        # Create hint for the other challenge
        hint = Hint.create_hint(
            challenge_id=other_challenge.id,
            body="Wrong challenge hint",
            preview="Test",
            deduction=10,
        )

        # Try to redeem for wrong challenge
        from ...core.exceptions import BusinessLogicError
        with pytest.raises(BusinessLogicError) as exc:
            HintRedemption.create_redemption(
                hint_id=hint.id,
                user_id=user.id,
                team_id=team_with_member.id,
                challenge_id=challenge.id,  # Wrong challenge!
            )
        assert "does not belong to the specified challenge" in str(exc.value)

    def test_hint_visibility_after_event_ends(
        self, db_session, challenge, team_with_member, user, event
    ):
        """Test that hints remain visible after event ends if already redeemed."""
        hint = Hint.create_hint(
            challenge_id=challenge.id,
            body="Historical hint",
            preview="Old hint",
            deduction=15,
        )

        # Redeem hint while event is active
        HintRedemption.create_redemption(
            hint_id=hint.id,
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
        )

        # Simulate event ending (needs start_time before end_time due to constraint)
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        event.start_time = now - timedelta(hours=2)
        event.end_time = now - timedelta(hours=1)
        db_session.commit()

        # Team should still see the redeemed hint
        serialized = hint.serialize(team=team_with_member)
        assert serialized["body"] == "Historical hint"
        assert serialized["is_redeemed"] is True


@pytest.mark.db
class TestCompleteUserJourney:
    """Test a complete user journey through hint redemption."""

    def test_user_journey_progressive_hint_redemption(
        self, db_session, challenge, team_with_member, user, event, score
    ):
        """Test a realistic user journey with progressive hint redemption."""
        # User starts with some points
        score.points = 200
        db_session.commit()

        # Challenge has 3 hints of increasing value
        easy_hint = Hint.create_hint(
            challenge_id=challenge.id,
            body="Start by looking at the network traffic",
            preview="Where to begin?",
            deduction=5,
        )
        medium_hint = Hint.create_hint(
            challenge_id=challenge.id,
            body="The vulnerability is in the authentication header",
            preview="Authentication issue",
            deduction=15,
        )
        hard_hint = Hint.create_hint(
            challenge_id=challenge.id,
            body="Use base64 decode on the JWT token",
            preview="Decoding required",
            deduction=30,
        )

        # Step 1: User views challenge - sees all previews, no bodies
        initial_render = challenge.render(team_with_member)
        for hint_data in initial_render["hints"]:
            assert hint_data["body"] is None
            assert hint_data["is_redeemed"] is False
            assert hint_data["preview"] is not None

        # Step 2: User struggles, redeems easy hint
        easy_result = redeem_hint(
            event=event,
            challenge=challenge,
            hint=easy_hint,
            team=team_with_member,
            current_user=user,
        )

        assert easy_result["body"] == "Start by looking at the network traffic"
        db_session.refresh(score)
        assert score.points == 195  # 200 - 5

        # Step 3: User makes progress, needs more help, redeems medium hint
        medium_result = redeem_hint(
            event=event,
            challenge=challenge,
            hint=medium_hint,
            team=team_with_member,
            current_user=user,
        )

        assert medium_result["body"] == "The vulnerability is in the authentication header"
        db_session.refresh(score)
        assert score.points == 180  # 195 - 15

        # Step 4: User views challenge again - sees redeemed hints
        current_render = challenge.render(team_with_member)
        hints_by_id = {h["id"]: h for h in current_render["hints"]}

        assert hints_by_id[easy_hint.id]["is_redeemed"] is True
        assert hints_by_id[easy_hint.id]["body"] is not None

        assert hints_by_id[medium_hint.id]["is_redeemed"] is True
        assert hints_by_id[medium_hint.id]["body"] is not None

        assert hints_by_id[hard_hint.id]["is_redeemed"] is False
        assert hints_by_id[hard_hint.id]["body"] is None

        # Step 5: User completes challenge without needing the hard hint
        # Final score: 180 (saved 30 points by not using the hard hint)
        assert score.points == 180