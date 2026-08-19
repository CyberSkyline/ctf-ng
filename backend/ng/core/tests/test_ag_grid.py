"""Tests for the ag-grid sort/filter -> SQLAlchemy translator."""

from datetime import datetime

import pytest
from sqlalchemy import func

from ...event.models.Event import Event
from ...team.models.Team import Team
from ...team.models.TeamMember import TeamMember
from ..utils.ag_grid import apply_filter_model, apply_sort_model, paginate

COLUMN_MAP = {
    "id": Team.id,
    "name": Team.name,
    "event_name": Event.name,
    "member_count": Team.member_count,
    "start_timestamp": Team.start_timestamp,
    "ranked": Team.ranked,
    "invite_code": Team.invite_code,
}


def base_query():
    return Team.query.join(Event, Team.event_id == Event.id)


def names(query):
    return [t.name for t in query.all()]


@pytest.fixture
def grid_teams(db_session, event_factory, user_factory, team_factory):
    """Three teams with distinct names, events, member counts, start timestamps."""
    event_a = event_factory(name="Alpha Event")
    event_b = event_factory(name="Bravo Event")
    ua = user_factory(name="UA", email="ua@example.com")
    ub = user_factory(name="UB", email="ub@example.com")
    uc = user_factory(name="UC", email="uc@example.com")

    apple = team_factory(event=event_a, name="Apple", members=[ua])
    banana = team_factory(event=event_a, name="Banana", members=[ub, uc])
    cherry = team_factory(event=event_b, name="Cherry", members=[ua, ub, uc])

    apple.start_timestamp = datetime(2024, 1, 10)
    banana.start_timestamp = datetime(2024, 6, 15)
    cherry.start_timestamp = None
    apple.ranked, banana.ranked, cherry.ranked = True, True, False
    db_session.commit()

    return {"apple": apple, "banana": banana, "cherry": cherry}


class Test_Filter:
    def test_text_contains(self, grid_teams):
        fm = {"name": {"filterType": "text", "type": "contains", "filter": "an"}}
        assert names(apply_filter_model(base_query(), fm, COLUMN_MAP)) == ["Banana"]

    def test_text_starts_with_is_case_insensitive(self, grid_teams):
        fm = {"name": {"filterType": "text", "type": "startsWith", "filter": "a"}}
        assert names(apply_filter_model(base_query(), fm, COLUMN_MAP)) == ["Apple"]

    def test_not_contains_excludes_matches(self, grid_teams):
        fm = {"name": {"filterType": "text", "type": "notContains", "filter": "an"}}
        assert sorted(names(apply_filter_model(base_query(), fm, COLUMN_MAP))) == ["Apple", "Cherry"]

    def test_contains_escapes_like_wildcards(self, event_factory, user_factory, team_factory):
        # "%" is a literal here, not a LIKE wildcard, so "5000 off" must not match.
        event = event_factory(name="Zeta Event")
        u1 = user_factory(name="ZU1", email="zu1@example.com")
        u2 = user_factory(name="ZU2", email="zu2@example.com")
        team_factory(event=event, name="50% off", members=[u1])
        team_factory(event=event, name="5000 off", members=[u2])
        fm = {"name": {"filterType": "text", "type": "contains", "filter": "50%"}}
        assert names(apply_filter_model(base_query(), fm, COLUMN_MAP)) == ["50% off"]

    def test_number_equals_on_id(self, grid_teams):
        fm = {"id": {"filterType": "number", "type": "equals", "filter": grid_teams["banana"].id}}
        assert names(apply_filter_model(base_query(), fm, COLUMN_MAP)) == ["Banana"]

    def test_number_greater_than_member_count(self, grid_teams):
        fm = {"member_count": {"filterType": "number", "type": "greaterThan", "filter": 1}}
        assert sorted(names(apply_filter_model(base_query(), fm, COLUMN_MAP))) == ["Banana", "Cherry"]

    def test_number_in_range_member_count(self, grid_teams):
        fm = {"member_count": {"filterType": "number", "type": "inRange", "filter": 2, "filterTo": 3}}
        assert sorted(names(apply_filter_model(base_query(), fm, COLUMN_MAP))) == ["Banana", "Cherry"]

    def test_event_name_filter_via_join(self, grid_teams):
        fm = {"event_name": {"filterType": "text", "type": "equals", "filter": "Bravo Event"}}
        assert names(apply_filter_model(base_query(), fm, COLUMN_MAP)) == ["Cherry"]

    def test_date_in_range(self, grid_teams):
        fm = {
            "start_timestamp": {
                "filterType": "date",
                "type": "inRange",
                "dateFrom": "2024-01-01 00:00:00",
                "dateTo": "2024-03-01 00:00:00",
            }
        }
        assert names(apply_filter_model(base_query(), fm, COLUMN_MAP)) == ["Apple"]

    def test_date_blank(self, grid_teams):
        fm = {"start_timestamp": {"filterType": "date", "type": "blank"}}
        assert names(apply_filter_model(base_query(), fm, COLUMN_MAP)) == ["Cherry"]

    def test_combined_or(self, grid_teams):
        fm = {
            "name": {
                "filterType": "text",
                "operator": "OR",
                "conditions": [
                    {"filterType": "text", "type": "contains", "filter": "app"},
                    {"filterType": "text", "type": "contains", "filter": "err"},
                ],
            }
        }
        assert sorted(names(apply_filter_model(base_query(), fm, COLUMN_MAP))) == ["Apple", "Cherry"]

    def test_unmapped_field_ignored(self, grid_teams):
        fm = {"seed": {"filterType": "text", "type": "contains", "filter": "abc"}}
        assert len(apply_filter_model(base_query(), fm, COLUMN_MAP).all()) == 3

    def test_not_equal_excludes_matching_name(self, grid_teams):
        fm = {"name": {"filterType": "text", "type": "notEqual", "filter": "Banana"}}
        assert sorted(names(apply_filter_model(base_query(), fm, COLUMN_MAP))) == ["Apple", "Cherry"]

    def test_greater_than_or_equal_member_count(self, grid_teams):
        fm = {"member_count": {"filterType": "number", "type": "greaterThanOrEqual", "filter": 2}}
        assert sorted(names(apply_filter_model(base_query(), fm, COLUMN_MAP))) == ["Banana", "Cherry"]

    def test_less_than_member_count(self, grid_teams):
        fm = {"member_count": {"filterType": "number", "type": "lessThan", "filter": 2}}
        assert names(apply_filter_model(base_query(), fm, COLUMN_MAP)) == ["Apple"]

    def test_less_than_or_equal_member_count(self, grid_teams):
        fm = {"member_count": {"filterType": "number", "type": "lessThanOrEqual", "filter": 1}}
        assert names(apply_filter_model(base_query(), fm, COLUMN_MAP)) == ["Apple"]

    def test_ends_with(self, grid_teams):
        fm = {"name": {"filterType": "text", "type": "endsWith", "filter": "e"}}
        assert names(apply_filter_model(base_query(), fm, COLUMN_MAP)) == ["Apple"]

    def test_boolean_true(self, grid_teams):
        fm = {"ranked": {"filterType": "text", "type": "true"}}
        assert sorted(names(apply_filter_model(base_query(), fm, COLUMN_MAP))) == ["Apple", "Banana"]

    def test_boolean_false(self, grid_teams):
        fm = {"ranked": {"filterType": "text", "type": "false"}}
        assert names(apply_filter_model(base_query(), fm, COLUMN_MAP)) == ["Cherry"]

    def test_date_equals(self, grid_teams):
        fm = {"start_timestamp": {"filterType": "date", "type": "equals", "dateFrom": "2024-01-10 00:00:00"}}
        assert names(apply_filter_model(base_query(), fm, COLUMN_MAP)) == ["Apple"]

    def test_date_not_equal(self, grid_teams):
        # NULL rows count as "not equal" too, matching ag-grid's blank-cell semantics.
        fm = {"start_timestamp": {"filterType": "date", "type": "notEqual", "dateFrom": "2024-01-10 00:00:00"}}
        assert sorted(names(apply_filter_model(base_query(), fm, COLUMN_MAP))) == ["Banana", "Cherry"]

    def test_date_less_than(self, grid_teams):
        fm = {"start_timestamp": {"filterType": "date", "type": "lessThan", "dateFrom": "2024-06-01 00:00:00"}}
        assert names(apply_filter_model(base_query(), fm, COLUMN_MAP)) == ["Apple"]

    def test_date_greater_than(self, grid_teams):
        fm = {"start_timestamp": {"filterType": "date", "type": "greaterThan", "dateFrom": "2024-03-01 00:00:00"}}
        assert names(apply_filter_model(base_query(), fm, COLUMN_MAP)) == ["Banana"]

    def test_date_not_blank(self, grid_teams):
        fm = {"start_timestamp": {"filterType": "date", "type": "notBlank"}}
        assert sorted(names(apply_filter_model(base_query(), fm, COLUMN_MAP))) == ["Apple", "Banana"]

    def test_having_clause_for_aggregate_column(self, grid_teams):
        # Aggregate expressions must filter via HAVING, not WHERE.
        aggregate_map = {**COLUMN_MAP, "member_total": func.count(TeamMember.id)}
        query = (
            Team.query
            .join(Event, Team.event_id == Event.id)
            .outerjoin(TeamMember, TeamMember.team_id == Team.id)
            .group_by(Team.id)
        )
        fm = {"member_total": {"filterType": "number", "type": "greaterThan", "filter": 1}}
        assert sorted(names(apply_filter_model(query, fm, aggregate_map))) == ["Banana", "Cherry"]


class Test_Invalid_Input:
    def test_non_dict_filter_model_is_ignored(self, grid_teams):
        assert len(apply_filter_model(base_query(), None, COLUMN_MAP).all()) == 3
        assert len(apply_filter_model(base_query(), ["not", "a", "dict"], COLUMN_MAP).all()) == 3

    def test_non_dict_filter_condition_is_ignored(self, grid_teams):
        fm = {"name": "not-a-condition-dict"}
        assert len(apply_filter_model(base_query(), fm, COLUMN_MAP).all()) == 3

    def test_unknown_filter_type_is_ignored(self, grid_teams):
        fm = {"name": {"filterType": "text", "type": "bogus", "filter": "an"}}
        assert len(apply_filter_model(base_query(), fm, COLUMN_MAP).all()) == 3

    def test_invalid_condition_in_combined_filter_is_skipped(self, grid_teams):
        fm = {
            "name": {
                "filterType": "text",
                "operator": "OR",
                "conditions": [
                    "not-a-dict",
                    {"filterType": "text", "type": "contains", "filter": "an"},
                ],
            }
        }
        assert names(apply_filter_model(base_query(), fm, COLUMN_MAP)) == ["Banana"]

    def test_malformed_date_string_is_ignored(self, grid_teams):
        fm = {"start_timestamp": {"filterType": "date", "type": "equals", "dateFrom": "not-a-date"}}
        assert len(apply_filter_model(base_query(), fm, COLUMN_MAP).all()) == 3

    def test_non_list_sort_model_falls_back_to_tiebreaker(self, grid_teams):
        ids = [t.id for t in apply_sort_model(base_query(), None, COLUMN_MAP, Team.id).all()]
        assert ids == sorted(ids)

    def test_non_dict_sort_item_is_ignored(self, grid_teams):
        sm = ["not-a-dict", {"colId": "name", "sort": "desc"}]
        assert names(apply_sort_model(base_query(), sm, COLUMN_MAP, Team.id)) == ["Cherry", "Banana", "Apple"]


class Test_Sort:
    def test_sort_desc(self, grid_teams):
        sm = [{"colId": "name", "sort": "desc"}]
        assert names(apply_sort_model(base_query(), sm, COLUMN_MAP, Team.id)) == ["Cherry", "Banana", "Apple"]

    def test_tiebreaker_orders_ties_by_id(self, grid_teams):
        # Apple and Banana share an event, so event_name ties -> tiebreaker (id asc) decides.
        sm = [{"colId": "event_name", "sort": "asc"}]
        ids = [t.id for t in apply_sort_model(base_query(), sm, COLUMN_MAP, Team.id).all()]
        assert ids == sorted(ids)

    def test_unmapped_sort_field_ignored(self, grid_teams):
        sm = [{"colId": "seed", "sort": "desc"}]
        ids = [t.id for t in apply_sort_model(base_query(), sm, COLUMN_MAP, Team.id).all()]
        assert ids == sorted(ids)  # falls back to tiebreaker only


class Test_Paginate:
    def test_slice_and_total(self, grid_teams):
        query = apply_sort_model(base_query(), [{"colId": "name", "sort": "asc"}], COLUMN_MAP, Team.id)
        rows, total = paginate(query, 0, 2)
        assert total == 3
        assert [t.name for t in rows] == ["Apple", "Banana"]

        query = apply_sort_model(base_query(), [{"colId": "name", "sort": "asc"}], COLUMN_MAP, Team.id)
        rows, total = paginate(query, 2, 4)
        assert total == 3
        assert [t.name for t in rows] == ["Cherry"]
