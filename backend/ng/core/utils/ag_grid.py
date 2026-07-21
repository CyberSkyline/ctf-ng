"""
Translate ag-grid sort/filter models into SQLAlchemy query operations.

Column map: ag-grid colId -> SQLAlchemy expression. Unmapped colIds are ignored.
"""

from datetime import datetime, timedelta

from sqlalchemy import and_, or_
from sqlalchemy.sql.functions import Function

def _like(v):
    """Escape LIKE metacharacters so ag-grid text filters match literally."""
    return v.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


# ag-grid filter type -> clause builder.
_OPS = {
    "true": lambda c, v, hi: c.is_(True),
    "false": lambda c, v, hi: c.is_(False),
    "equals": lambda c, v, hi: c == v,
    "notEqual": lambda c, v, hi: or_(c.is_(None), c != v),
    "greaterThan": lambda c, v, hi: c > v,
    "greaterThanOrEqual": lambda c, v, hi: c >= v,
    "lessThan": lambda c, v, hi: c < v,
    "lessThanOrEqual": lambda c, v, hi: c <= v,
    "inRange": lambda c, v, hi: c.between(v, hi) if hi is not None else c >= v,
    "contains": lambda c, v, hi: c.ilike(f"%{_like(v)}%", escape="\\"),
    "notContains": lambda c, v, hi: or_(c.is_(None), ~c.ilike(f"%{_like(v)}%", escape="\\")),
    "startsWith": lambda c, v, hi: c.ilike(f"{_like(v)}%", escape="\\"),
    "endsWith": lambda c, v, hi: c.ilike(f"%{_like(v)}", escape="\\"),
}


def _values(cond):
    """(value, upper bound) for a condition."""
    if cond.get("filterType") == "date":
        def parse(s):
            return datetime.strptime(s, "%Y-%m-%d %H:%M:%S") if s else None
        return parse(cond.get("dateFrom")), parse(cond.get("dateTo"))
    return cond.get("filter"), cond.get("filterTo")


def _date_clause(column, typ, start, end):
    """Compares against the whole day, not the exact instant."""
    if start is None:
        return None
    next_day = start + timedelta(days=1)
    if typ == "equals":
        return and_(column >= start, column < next_day)
    if typ == "notEqual":
        return or_(column.is_(None), column < start, column >= next_day)
    if typ == "lessThan":
        return column < start
    if typ == "greaterThan":
        return column >= next_day
    if typ == "inRange":
        return and_(column >= start, column < end + timedelta(days=1)) if end else None
    return None


def _clause(column, cond):
    typ = cond.get("type")
    if typ in ("blank", "notBlank"):
        # Text columns treat "" as blank too, not just NULL.
        is_blank = column.is_(None)
        if cond.get("filterType") == "text":
            is_blank = or_(is_blank, column == "")
        return is_blank if typ == "blank" else ~is_blank
    value, upper = _values(cond)
    if cond.get("filterType") == "date":
        return _date_clause(column, typ, value, upper)
    op = _OPS.get(typ)
    if op is None:
        return None
    return op(column, value, upper)


def apply_filter_model(query, filter_model, column_map):
    """Filter ``query`` by an ag-grid filter model. Unmapped colIds and malformed entries are ignored."""
    for col_id, model in (filter_model if isinstance(filter_model, dict) else {}).items():
        column = column_map.get(col_id)
        if column is None or not isinstance(model, dict):
            continue
        conditions = model.get("conditions") or [model]  # combined filter, or a single condition
        clauses = []
        for cond in conditions:
            if not isinstance(cond, dict):
                continue
            try:
                clause = _clause(column, cond)
            except (TypeError, ValueError, AttributeError):  # e.g. an unparsable date string
                clause = None
            if clause is not None:
                clauses.append(clause)
        if clauses:
            combine = or_ if model.get("operator") == "OR" else and_
            clause = combine(*clauses)
            query = query.having(clause) if isinstance(column, Function) else query.filter(clause)
    return query


def apply_sort_model(query, sort_model, column_map, tiebreaker):
    """Sort ``query`` by an ag-grid sort model. Always ends on ``tiebreaker`` for deterministic paging."""
    order = []
    for item in sort_model if isinstance(sort_model, list) else []:
        if not isinstance(item, dict):
            continue
        column = column_map.get(item.get("colId"))
        if column is not None:
            order.append(column.desc() if item.get("sort") == "desc" else column.asc())
    order.append(tiebreaker.asc())
    return query.order_by(None).order_by(*order)


def paginate(query, start_row, end_row):
    """Return ``(rows, total)`` for the ``[start_row, end_row)`` block."""
    total = query.order_by(None).count()
    rows = query.offset(start_row).limit(end_row - start_row).all()
    return rows, total
