import pytest
from datetime import datetime, timedelta
from ...core.utils import utc_now
from ...certificate.services.certificate_service import local_date
from ..models.Event import Event


pytestmark = pytest.mark.db


class Test_Local_Date:
    def test_converts_timestamp_to_requested_zone(self):
        # 06:00 UTC on January 2 is still January 1 in Pacific time (PST, UTC-8)
        assert local_date(datetime(2025, 1, 2, 6, 0), "America/Los_Angeles") == {"year": 2025, "month": 1, "day": 1}

    def test_bad_timezone_falls_back_to_default(self):
        # a garbage zone must not raise, it falls back to the default (America/New_York, 01:00 EST on January 2)
        assert local_date(datetime(2025, 1, 2, 6, 0), "Not/AZone") == {"year": 2025, "month": 1, "day": 2}


class Test_Event_Certificate_Update:
    def test_admin_update_flips_has_certificate(self, admin_client, event_factory):
        event = event_factory()

        before = admin_client.get(f"/ng/events/{event.id}")
        assert before.json["data"]["has_certificate"] is False

        update = admin_client.put(
            f"/ng/admin/events/{event.id}",
            json={"name": event.name, "certificate_template": "evergreen/evergreen.typ"},
        )
        assert update.status_code == 200

        after = admin_client.get(f"/ng/events/{event.id}")
        assert after.json["data"]["has_certificate"] is True

    def test_filename_hidden_from_non_admin(self, logged_in_client, admin_client, event_factory):
        event = event_factory()
        admin_client.put(
            f"/ng/admin/events/{event.id}",
            json={"name": event.name, "certificate_template": "evergreen/evergreen.typ"},
        )

        response = logged_in_client.get(f"/ng/events/{event.id}")
        assert "certificate_template" not in response.json["data"]

    def test_rejects_path_outside_templates(self, admin_client, event_factory):
        event = event_factory()

        response = admin_client.put(
            f"/ng/admin/events/{event.id}",
            json={"name": event.name, "certificate_template": "../../config.py"},
        )
        assert response.status_code == 400

    def test_rejects_non_template_file(self, admin_client, event_factory):
        event = event_factory()

        response = admin_client.put(
            f"/ng/admin/events/{event.id}",
            json={"name": event.name, "certificate_template": "cisa.svg"},
        )
        assert response.status_code == 400


def _end_event(team, event, offset):
    """Give the event and team paired start/end windows that end `offset` from now."""
    now = utc_now().replace(tzinfo=None)
    event.update_event(start_time=now - timedelta(days=1), end_time=now + offset)
    team.set_end_time(now + offset)


class Test_Event_Certificate_Render:
    def test_event_certificate_renders_after_event_ends(self, started_player_client, team_with_members):
        event = Event.find_by_id(team_with_members.event_id)
        event.update_event(certificate_template="evergreen/evergreen.typ")
        _end_event(team_with_members, event, -timedelta(hours=1))

        response = started_player_client.get(f"/ng/events/{event.id}/certificate")
        assert response.status_code == 200
        assert response.data.startswith(b"%PDF-")
        assert response.headers["Cache-Control"] == "private, max-age=86400"

    def test_bad_timezone_param_still_renders(self, started_player_client, team_with_members):
        event = Event.find_by_id(team_with_members.event_id)
        event.update_event(certificate_template="evergreen/evergreen.typ")
        _end_event(team_with_members, event, -timedelta(hours=1))

        response = started_player_client.get(f"/ng/events/{event.id}/certificate?tz=Not/AZone")
        assert response.status_code == 200
        assert response.data.startswith(b"%PDF-")

    def test_no_certificate_configured_returns_404(self, started_player_client, team_with_members):
        response = started_player_client.get(f"/ng/events/{team_with_members.event_id}/certificate")
        assert response.status_code == 404

    def test_event_not_over_returns_400(self, started_player_client, team_with_members):
        event = Event.find_by_id(team_with_members.event_id)
        event.update_event(certificate_template="evergreen/evergreen.typ")
        _end_event(team_with_members, event, timedelta(days=1))

        response = started_player_client.get(f"/ng/events/{event.id}/certificate")
        assert response.status_code == 400

    def test_team_never_started_returns_400(self, team_member_client, team_with_members):
        # a team that never played did not participate, so it gets no certificate
        event = Event.find_by_id(team_with_members.event_id)
        event.update_event(certificate_template="evergreen/evergreen.typ")
        _end_event(team_with_members, event, -timedelta(hours=1))

        response = team_member_client.get(f"/ng/events/{event.id}/certificate")
        assert response.status_code == 400

    def test_event_without_deadline_returns_400(self, started_player_client, team_with_members):
        Event.find_by_id(team_with_members.event_id).update_event(certificate_template="evergreen/evergreen.typ")

        response = started_player_client.get(f"/ng/events/{team_with_members.event_id}/certificate")
        assert response.status_code == 400

    def test_event_without_team_window_returns_400(self, started_player_client, team_with_members):
        # the cert dates from the team window, so an event with no time limit issues none
        now = utc_now().replace(tzinfo=None)
        event = Event.find_by_id(team_with_members.event_id)
        event.update_event(
            certificate_template="evergreen/evergreen.typ",
            start_time=now - timedelta(days=1),
            end_time=now - timedelta(hours=1),
        )

        response = started_player_client.get(f"/ng/events/{event.id}/certificate")
        assert response.status_code == 400

    def test_practice_event_blocks_event_certificate(self, started_player_client, team_with_members):
        event_id = team_with_members.event_id
        Event.find_by_id(event_id).update_event(certificate_template="evergreen/evergreen.typ", practice=True)

        response = started_player_client.get(f"/ng/events/{event_id}/certificate")
        assert response.status_code == 404

    def test_non_practice_event_blocks_challenge_certificate(self, started_player_client, team_with_members, challenge_factory):
        event = Event.find_by_id(team_with_members.event_id)
        event.update_event(certificate_template="evergreen/evergreen.typ")
        challenge = challenge_factory(event=event)

        response = started_player_client.get(f"/ng/events/{event.id}/challenges/{challenge.id}/certificate")
        assert response.status_code == 404

    def test_incomplete_challenge_returns_400(self, started_player_client, team_with_members, challenge_factory):
        event = Event.find_by_id(team_with_members.event_id)
        event.update_event(certificate_template="evergreen/evergreen.typ", practice=True)
        challenge = challenge_factory(event=event)

        response = started_player_client.get(f"/ng/events/{event.id}/challenges/{challenge.id}/certificate")
        assert response.status_code == 400

    def test_completed_challenge_renders_pdf(self, started_player_client, team_with_members, challenge_factory, attempt_factory):
        event = Event.find_by_id(team_with_members.event_id)
        event.update_event(certificate_template="evergreen/evergreen.typ", practice=True)
        challenge = challenge_factory(event=event)
        for question in challenge.questions:
            attempt_factory(
                team_id=team_with_members.id,
                event_id=event.id,
                challenge_id=challenge.id,
                question_id=question.id,
                is_correct=True,
            )

        response = started_player_client.get(f"/ng/events/{event.id}/challenges/{challenge.id}/certificate")
        assert response.status_code == 200
        assert response.data.startswith(b"%PDF-")
        assert response.headers["Cache-Control"] == "private, max-age=86400"
