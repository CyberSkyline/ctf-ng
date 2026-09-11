"""
Tests for the JSON logger's record formatting.
"""

import json
import logging
import sys

from ..utils.logger import JSONFormatter, format_traceback


def formatted(record) -> dict:
    """Run a record through the JSON formatter and parse the result."""

    return json.loads(JSONFormatter().format(record))


def make_record(**kwargs) -> logging.LogRecord:
    """Build a log record the way `logger.error(...)` would."""

    defaults = {
        "name": "test",
        "level": logging.ERROR,
        "pathname": __file__,
        "lineno": 1,
        "msg": "something failed",
        "args": (),
        "exc_info": None,
    }

    return logging.LogRecord(**{**defaults, **kwargs})


def test_traceback_is_recorded_for_exc_info():
    """
    Test that a record carrying exc_info keeps its traceback. The formatter
    builds the entry field by field, so the traceback is dropped unless it is
    read out explicitly.
    """
    try:
        raise ValueError("the specific failure")
    except ValueError:
        record = make_record(exc_info=sys.exc_info())

    trace = formatted(record)["trace"]

    assert "ValueError: the specific failure" in trace
    assert "test_traceback_is_recorded_for_exc_info" in trace


def test_explicit_trace_wins_over_exc_info():
    """
    Test that a trace supplied on the record is kept as-is, so the existing
    callers that pass their own trace are unaffected
    """
    try:
        raise ValueError("ignored")
    except ValueError:
        record = make_record(exc_info=sys.exc_info())

    record.trace = "supplied by the caller"

    assert formatted(record)["trace"] == "supplied by the caller"


def test_no_trace_without_an_exception():
    """
    Test that an ordinary record carries no trace field
    """
    assert "trace" not in formatted(make_record())


def test_format_traceback_without_an_exception():
    """
    Test that formatting outside of an exception handler yields nothing rather
    than raising
    """
    assert format_traceback() == ""


def test_format_traceback_limits_frames():
    """
    Test that only the frames nearest the failure are kept
    """
    def depth_3():
        raise RuntimeError("deep")

    def depth_2():
        depth_3()

    def depth_1():
        depth_2()

    try:
        depth_1()
    except RuntimeError:
        trace = format_traceback(limit=1)

    assert "depth_3" in trace
    assert "depth_1" not in trace
    assert "RuntimeError: deep" in trace
