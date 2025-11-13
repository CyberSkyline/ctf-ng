"""
Test cases for the improved hint redemption system.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from ...challenge.models.Hint import Hint
from ...challenge.models.Challenge import Challenge
from ...core.exceptions import BusinessLogicError
from ..models import HintRedemption, Score
from ..controllers.user_actions.redeem_hint import redeem_hint


@pytest.mark.db
class TestHintVisibilityBeforeRedemption:
    """
    Test that hints are properly hidden before redemption
    """
    def test_hint_body_hidden_before_redemption(
        self,
        db_session,
        challenge,
        team_with_member
    ):
        """
        Test that hint body is hidden when not yet redeemed
        """
        hint = Hint.create_hint(
            name="Hint Name",
            challenge_id=challenge.id,
            body="The secret is in the cookies",
            preview="Check the HTTP headers",
            deduction=20,
            index=0,
        )

        serialized = hint.serialize(team = team_with_member)

        assert serialized["body"] is None
        assert serialized["preview"] == "Check the HTTP headers"
        assert serialized["is_redeemed"] is False
        assert serialized["deduction"] == 20

    def test_multiple_teams_cannot_see_unredeemed_hints(
        self,
        db_session,
        challenge,
        team_factory,
        user_factory,
        event
    ):
        """
        Test that multiple teams cannot see hint bodies before redemption
        """
        user1 = user_factory(name = "HintUser1", email = "hintuser1@example.com")
        user2 = user_factory(name = "HintUser2", email = "hintuser2@example.com")

        team1 = team_factory(event = event, members = [user1])
        team2 = team_factory(event = event, members = [user2])

        hint = Hint.create_hint(
            name = "Hint Name",
            challenge_id = challenge.id,
            body = "Use SQL injection on the login form",
            preview = "Database vulnerability",
            deduction = 30,
            index=0,
        )

        team1_view = hint.serialize(team = team1)
        team2_view = hint.serialize(team = team2)

        assert team1_view["body"] is None
        assert team2_view["body"] is None
        assert team1_view["is_redeemed"] is False
        assert team2_view["is_redeemed"] is False


@pytest.mark.db
class TestHintRedemptionFlow:
    """
    Test the complete hint redemption flow
    """
    def test_successful_hint_redemption_reveals_body(
        self,
        db_session,
        challenge,
        team_with_member,
        user,
        event,
        score
    ):
        """
        Test that redeeming a hint reveals its body to that team only
        """
        hint = Hint.create_hint(
            name="Hint Name",
            challenge_id=challenge.id,
            body="The flag format is FLAG{...}",
            preview="Flag format hint",
            deduction=15,
            index=0,
        )

        before = hint.serialize(team = team_with_member)
        assert before["body"] is None
        assert before["is_redeemed"] is False

        result = redeem_hint(
            challenge = challenge,
            hint = hint,
            team = team_with_member,
            current_user = user,
        )

        assert result["body"] == "The flag format is FLAG{...}"
        assert result["is_redeemed"] is True
        assert result["preview"] == "Flag format hint"

        after = hint.serialize(team = team_with_member)
        assert after["body"] == "The flag format is FLAG{...}"
        assert after["is_redeemed"] is True

        db_session.refresh(score)
        assert score.points == -15

    def test_other_teams_cannot_see_redeemed_hints(
        self,
        db_session,
        challenge,
        team_with_member,
        team_factory,
        user_factory,
        user,
        event
    ):
        """
        Test that other teams cannot see hints redeemed by one team
        """
        other_user = user_factory(
            name = "OtherTeamUser",
            email = "otherteam@example.com"
        )
        other_team = team_factory(event = event, members = [other_user])

        hint = Hint.create_hint(
            name="Hint Name",
            challenge_id = challenge.id,
            body = "Check port 8080 for the admin panel",
            preview = "Hidden service",
            deduction = 25,
            index=0,
        )

        HintRedemption.create_redemption(
            hint_id = hint.id,
            user_id = user.id,
            team_id = team_with_member.id,
            challenge_id = challenge.id,
        )

        team1_view = hint.serialize(team = team_with_member)
        assert team1_view["body"] == "Check port 8080 for the admin panel"
        assert team1_view["is_redeemed"] is True

        other_team_view = hint.serialize(team = other_team)
        assert other_team_view["body"] is None
        assert other_team_view["is_redeemed"] is False
        assert other_team_view["preview"] == "Hidden service"

    def test_cannot_redeem_same_hint_twice(
        self,
        db_session,
        challenge,
        team_with_member,
        user,
        event
    ):
        """
        Test that a team cannot redeem the same hint twice
        """
        hint = Hint.create_hint(
            name="Hint Name",
            challenge_id=challenge.id,
            body="Duplicate redemption test",
            preview="Test hint",
            deduction=10,
            index=0,
        )

        first_result = redeem_hint(
            challenge = challenge,
            hint = hint,
            team = team_with_member,
            current_user = user,
        )
        assert first_result["is_redeemed"] is True

        with pytest.raises(BusinessLogicError) as exc:
            redeem_hint(
                challenge = challenge,
                hint = hint,
                team = team_with_member,
                current_user = user,
            )
        assert "already been redeemed" in str(exc.value)


@pytest.mark.db
class TestChallengeRenderWithHintRedemption:
    """
    Test Challenge.render() with the improved hint system
    """
    def test_challenge_render_shows_correct_hint_states(
        self,
        db_session,
        challenge,
        team_with_member,
        user
    ):
        """
        Test that Challenge.render() shows correct hint redemption states
        """
        hints = []
        for i in range(3):
            hint = Hint.create_hint(
                name=f"Hint {i+1}",
                challenge_id=challenge.id,
                body=f"Full body of hint {i+1}",
                preview=f"Preview of hint {i+1}",
                deduction=10 * (i + 1),
                index=i,
            )
            hints.append(hint)

        HintRedemption.create_redemption(
            hint_id = hints[1].id,
            user_id = user.id,
            team_id = team_with_member.id,
            challenge_id = challenge.id,
        )

        rendered = challenge.render(team_with_member)

        rendered_hints = rendered["hints"]
        assert len(rendered_hints) == 3

        for i, original_hint in enumerate(hints):
            rendered_hint = next(
                h for h in rendered_hints if h["id"] == original_hint.id
            )

            if i == 1:
                assert rendered_hint["body"] == f"Full body of hint {i+1}"
                assert rendered_hint["is_redeemed"] is True
            else:
                assert rendered_hint["body"] is None
                assert rendered_hint["is_redeemed"] is False

            assert rendered_hint["preview"] == f"Preview of hint {i+1}"

    def test_challenge_render_for_different_teams(
        self,
        db_session,
        challenge,
        team_with_member,
        team_factory,
        user_factory,
        user,
        event
    ):
        """
        Test that different teams see different hint states in Challenge.render()
        """
        user2 = user_factory(name = "Team2User", email = "team2user@example.com")
        team2 = team_factory(event = event, members = [user2])

        hint1 = Hint.create_hint(
            name="Hint 1",
            challenge_id=challenge.id,
            body="Team-specific body 1",
            preview="Hint 1",
            deduction=10,
            index=0,
        )
        hint2 = Hint.create_hint(
            name="Hint 2",
            challenge_id=challenge.id,
            body="Team-specific body 2",
            preview="Hint 2",
            deduction=20,
            index=1,
        )

        HintRedemption.create_redemption(
            hint_id = hint1.id,
            user_id = user.id,
            team_id = team_with_member.id,
            challenge_id = challenge.id,
        )

        HintRedemption.create_redemption(
            hint_id = hint2.id,
            user_id = user2.id,
            team_id = team2.id,
            challenge_id = challenge.id,
        )

        team1_render = challenge.render(team_with_member)
        team1_hints = {h["id"]: h for h in team1_render["hints"]}

        assert team1_hints[hint1.id]["body"] == "Team-specific body 1"
        assert team1_hints[hint1.id]["is_redeemed"] is True
        assert team1_hints[hint2.id]["body"] is None
        assert team1_hints[hint2.id]["is_redeemed"] is False

        team2_render = challenge.render(team2)
        team2_hints = {h["id"]: h for h in team2_render["hints"]}

        assert team2_hints[hint1.id]["body"] is None
        assert team2_hints[hint1.id]["is_redeemed"] is False
        assert team2_hints[hint2.id]["body"] == "Team-specific body 2"
        assert team2_hints[hint2.id]["is_redeemed"] is True


@pytest.mark.db
class TestHintRedemptionWithScoring:
    """
    Test hint redemption's impact on scoring
    """
    def test_hint_redemption_deducts_points(
        self,
        db_session,
        challenge,
        team_with_member,
        user,
        event,
        score
    ):
        """
        Test that redeeming hints properly deducts points
        """
        initial_points = 100
        score.points = initial_points
        db_session.commit()

        hint1 = Hint.create_hint(
            name="Hint 1",
            challenge_id=challenge.id,
            body="First hint",
            preview="Hint 1",
            deduction=10,
            index=0,
        )
        hint2 = Hint.create_hint(
            name="Hint 2",
            challenge_id=challenge.id,
            body="Second hint",
            preview="Hint 2",
            deduction=25,
            index=1,
        )

        redeem_hint(
            challenge = challenge,
            hint = hint1,
            team = team_with_member,
            current_user = user,
        )

        db_session.refresh(score)
        assert score.points == initial_points - 10

        redeem_hint(
            challenge = challenge,
            hint = hint2,
            team = team_with_member,
            current_user = user,
        )

        db_session.refresh(score)
        assert score.points == initial_points - 10 - 25

    def test_free_hint_no_deduction(
        self,
        db_session,
        challenge,
        team_with_member,
        user,
        event,
        score
    ):
        """
        Test that hints with zero deduction don't affect score
        """
        initial_points = 50
        score.points = initial_points
        db_session.commit()

        free_hint = Hint(
            challenge_id = challenge.id,
            body = "Free hint body",
            preview = "Free hint",
            deduction = 0,
            index = 0,
        )
        db_session.add(free_hint)
        db_session.commit()

        result = redeem_hint(
            challenge = challenge,
            hint = free_hint,
            team = team_with_member,
            current_user = user,
        )

        db_session.refresh(score)
        assert score.points == initial_points

        assert result["body"] == "Free hint body"
        assert result["is_redeemed"] is True


@pytest.mark.db
class TestAdminHintVisibility:
    """
    Test admin visibility of hints
    """
    def test_admin_sees_all_hint_bodies(
        self,
        db_session,
        challenge,
        team_with_member
    ):
        """
        Test that admins can see all hint bodies regardless of redemption
        """
        hint = Hint.create_hint(
            name="Admin Hint",
            challenge_id=challenge.id,
            body="Admin should see this",
            preview="Admin test",
            deduction=15,
            index=0,
        )

        admin_view = hint.serialize(include_admin_fields = True)

        assert admin_view["body"] == "Admin should see this"
        assert admin_view["preview"] == "Admin test"
        assert admin_view["is_redeemed"] is False

    def test_admin_with_team_context_sees_redemption_state(
        self,
        db_session,
        challenge,
        team_with_member,
        user
    ):
        """
        Test that admin with team context sees actual redemption state
        """
        hint = Hint.create_hint(
            name="Admin with team context",
            challenge_id=challenge.id,
            body="Admin with team context",
            preview="Test",
            deduction=20,
            index=0,
        )

        HintRedemption.create_redemption(
            hint_id = hint.id,
            user_id = user.id,
            team_id = team_with_member.id,
            challenge_id = challenge.id,
        )

        admin_team_view = hint.serialize(
            team = team_with_member,
            include_admin_fields = True
        )

        assert admin_team_view["body"] == "Admin with team context"
        assert admin_team_view["is_redeemed"] is True


@pytest.mark.db
class TestHintRedemptionEdgeCases:
    """
    Test edge cases and error conditions
    """
    def test_hint_redemption_for_wrong_challenge_fails(
        self,
        db_session,
        challenge,
        team_with_member,
        user,
        event
    ):
        """
        Test that hint redemption fails if hint doesn't belong to challenge
        """
        other_challenge = Challenge.create_challenge(
            name = "Other Challenge",
            event_id = event.id,
        )

        hint = Hint.create_hint(
            name="Wrong Challenge Hint",
            challenge_id=other_challenge.id,
            body="Wrong challenge hint",
            preview="Test",
            deduction=10,
            index=0,
        )

        with pytest.raises(BusinessLogicError) as exc:
            HintRedemption.create_redemption(
                hint_id = hint.id,
                user_id = user.id,
                team_id = team_with_member.id,
                challenge_id = challenge.id,
            )
        assert "does not belong to the specified challenge" in str(exc.value)

    def test_hint_visibility_after_event_ends(
        self,
        db_session,
        challenge,
        team_with_member,
        user,
        event
    ):
        """
        Test that hints remain visible after event ends if already redeemed
        """
        hint = Hint.create_hint(
            name="Historical Hint",
            challenge_id=challenge.id,
            body="Historical hint",
            preview="Old hint",
            deduction=15,
            index=0,
        )

        HintRedemption.create_redemption(
            hint_id = hint.id,
            user_id = user.id,
            team_id = team_with_member.id,
            challenge_id = challenge.id,
        )

        now = datetime.utcnow()
        event.start_time = now - timedelta(hours = 2)
        event.end_time = now - timedelta(hours = 1)
        db_session.commit()

        serialized = hint.serialize(team = team_with_member)
        assert serialized["body"] == "Historical hint"
        assert serialized["is_redeemed"] is True


@pytest.mark.db
class TestCompleteUserJourney:
    """
    Test a complete user journey through hint redemption
    """
    def test_user_journey_progressive_hint_redemption(
        self,
        db_session,
        challenge,
        team_with_member,
        user,
        event,
        score
    ):
        """
        Test a realistic user journey with progressive hint redemption
        """
        score.points = 200
        db_session.commit()

        easy_hint = Hint.create_hint(
            name="Hint 1",
            challenge_id=challenge.id,
            body="Start by looking at the network traffic",
            preview="Where to begin?",
            deduction=5,
            index=0,
        )
        medium_hint = Hint.create_hint(
            name="Hint 2",
            challenge_id=challenge.id,
            body="The vulnerability is in the authentication header",
            preview="Authentication issue",
            deduction=15,
            index=1,
        )
        hard_hint = Hint.create_hint(
            name="Hint 3",
            challenge_id=challenge.id,
            body="Use base64 decode on the JWT token",
            preview="Decoding required",
            deduction=30,
            index=2,
        )

        initial_render = challenge.render(team_with_member)
        for hint_data in initial_render["hints"]:
            assert hint_data["body"] is None
            assert hint_data["is_redeemed"] is False
            assert hint_data["preview"] is not None

        easy_result = redeem_hint(
            challenge = challenge,
            hint = easy_hint,
            team = team_with_member,
            current_user = user,
        )

        assert easy_result["body"] == "Start by looking at the network traffic"
        db_session.refresh(score)
        assert score.points == 195

        medium_result = redeem_hint(
            challenge = challenge,
            hint = medium_hint,
            team = team_with_member,
            current_user = user,
        )

        assert medium_result[
            "body"] == "The vulnerability is in the authentication header"
        db_session.refresh(score)
        assert score.points == 180

        current_render = challenge.render(team_with_member)
        hints_by_id = {h["id"]: h for h in current_render["hints"]}

        assert hints_by_id[easy_hint.id]["is_redeemed"] is True
        assert hints_by_id[easy_hint.id]["body"] is not None

        assert hints_by_id[medium_hint.id]["is_redeemed"] is True
        assert hints_by_id[medium_hint.id]["body"] is not None

        assert hints_by_id[hard_hint.id]["is_redeemed"] is False
        assert hints_by_id[hard_hint.id]["body"] is None
        assert score.points == 180
