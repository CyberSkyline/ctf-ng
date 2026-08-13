"""
Tests for ContainerInstance's admin grid query and single-deployment lookup.
"""

from ..models.ContainerInstance import ContainerInstance
from ...challenge.models.ContainerBlueprint import ContainerBlueprint


def make_blueprint(challenge, db_session, **kwargs):
    defaults = {
        "image": "test-image",
        "hostname": "test-host",
        "challenge_id": challenge.id,
    }
    defaults.update(kwargs)
    blueprint = ContainerBlueprint(**defaults)
    db_session.add(blueprint)
    db_session.commit()
    return blueprint


def make_instance(blueprint, team, db_session, **kwargs):
    defaults = {
        "blueprint": blueprint.id,
        "team_id": team.id,
        "hostip": "127.0.0.1",
        "dockerid": f"docker-{blueprint.id}-{team.id}-{db_session.query(ContainerInstance).count()}",
    }
    defaults.update(kwargs)
    instance = ContainerInstance(**defaults)
    db_session.add(instance)
    db_session.commit()
    return instance


class Test_Deployments:
    def build_deployments(self, db_session, event_factory, challenge_factory, team_factory, user_factory):
        """Build three deployments across two challenges and two events.

        challenge_x/team_one has 2 instances from 2 blueprints.
        challenge_x/team_two has 1 instance.
        challenge_y/team_three has 1 instance, in a different event.
        """
        event_a = event_factory(name="Alpha Event")
        event_b = event_factory(name="Bravo Event")

        challenge_x = challenge_factory(event=event_a, name="Challenge X")
        challenge_y = challenge_factory(event=event_b, name="Challenge Y")

        u1 = user_factory(name="U1", email="u1@example.com")
        u2 = user_factory(name="U2", email="u2@example.com")
        u3 = user_factory(name="U3", email="u3@example.com")

        team_one = team_factory(event=event_a, name="Team One", members=[u1])
        team_two = team_factory(event=event_a, name="Team Two", members=[u2])
        team_three = team_factory(event=event_b, name="Team Three", members=[u3])

        bp_x1 = make_blueprint(challenge_x, db_session, name="x1")
        bp_x2 = make_blueprint(challenge_x, db_session, name="x2")
        bp_y1 = make_blueprint(challenge_y, db_session, name="y1")

        i1 = make_instance(bp_x1, team_one, db_session)
        make_instance(bp_x2, team_one, db_session)
        make_instance(bp_x1, team_two, db_session)
        make_instance(bp_y1, team_three, db_session)

        return {
            "challenge_x": challenge_x,
            "challenge_y": challenge_y,
            "team_one": team_one,
            "team_two": team_two,
            "team_three": team_three,
            "first_instance_id": i1.id,
        }

    def test_filter_by_challenge_name(self, db_session, event_factory, challenge_factory, team_factory, user_factory):
        self.build_deployments(db_session, event_factory, challenge_factory, team_factory, user_factory)

        fm = {"challenge_name": {"filterType": "text", "type": "equals", "filter": "Challenge X"}}
        rows, total = ContainerInstance.find_deployments_paginated([], fm, 0, 100)

        assert total == 2
        assert {r.team_name for r in rows} == {"Team One", "Team Two"}

    def test_filter_by_team_name(self, db_session, event_factory, challenge_factory, team_factory, user_factory):
        self.build_deployments(db_session, event_factory, challenge_factory, team_factory, user_factory)

        fm = {"team_name": {"filterType": "text", "type": "equals", "filter": "Team Three"}}
        rows, total = ContainerInstance.find_deployments_paginated([], fm, 0, 100)

        assert total == 1
        assert rows[0].event_name == "Bravo Event"

    def test_filter_by_event_name(self, db_session, event_factory, challenge_factory, team_factory, user_factory):
        self.build_deployments(db_session, event_factory, challenge_factory, team_factory, user_factory)

        fm = {"event_name": {"filterType": "text", "type": "equals", "filter": "Bravo Event"}}
        rows, total = ContainerInstance.find_deployments_paginated([], fm, 0, 100)

        assert total == 1
        assert rows[0].team_name == "Team Three"

    def test_filter_by_containers_uses_having(
        self, db_session, event_factory, challenge_factory, team_factory, user_factory,
    ):
        self.build_deployments(db_session, event_factory, challenge_factory, team_factory, user_factory)

        fm = {"containers": {"filterType": "number", "type": "equals", "filter": 2}}
        rows, total = ContainerInstance.find_deployments_paginated([], fm, 0, 100)

        assert total == 1
        assert rows[0].team_name == "Team One"

    def test_sort_by_containers_uses_composite_tiebreaker(
        self, db_session, event_factory, challenge_factory, team_factory, user_factory,
    ):
        self.build_deployments(db_session, event_factory, challenge_factory, team_factory, user_factory)

        sm = [{"colId": "containers", "sort": "desc"}]
        rows, total = ContainerInstance.find_deployments_paginated(sm, {}, 0, 100)

        assert total == 3
        # team_one has 2 containers. team_two and team_three tie at 1 and fall back to insertion order.
        assert [r.team_name for r in rows] == ["Team One", "Team Two", "Team Three"]
        assert [r.containers for r in rows] == [2, 1, 1]

    def test_pagination_slices_deterministically(
        self, db_session, event_factory, challenge_factory, team_factory, user_factory,
    ):
        self.build_deployments(db_session, event_factory, challenge_factory, team_factory, user_factory)

        sm = [{"colId": "containers", "sort": "desc"}]
        first_page, total = ContainerInstance.find_deployments_paginated(sm, {}, 0, 2)
        second_page, _ = ContainerInstance.find_deployments_paginated(sm, {}, 2, 4)

        assert total == 3
        assert [r.team_name for r in first_page] == ["Team One", "Team Two"]
        assert [r.team_name for r in second_page] == ["Team Three"]

    def test_find_deployment_resolves_group_from_any_member_instance(
        self, db_session, event_factory, challenge_factory, team_factory, user_factory,
    ):
        data = self.build_deployments(db_session, event_factory, challenge_factory, team_factory, user_factory)

        deployment = ContainerInstance.find_deployment(data["first_instance_id"])

        assert deployment is not None
        assert deployment.challenge_name == "Challenge X"
        assert deployment.team_name == "Team One"
        assert deployment.containers == 2

    def test_find_deployment_returns_none_for_unknown_instance(self, db_session):
        assert ContainerInstance.find_deployment(999999) is None
