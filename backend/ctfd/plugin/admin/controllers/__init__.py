"""
/backend/ctfd/plugin/admin/controllers/__init__.py
Admin controller functions for system management and data operations.
"""

from .cleanup_orphaned_data import cleanup_orphaned_data
from .cleanup_headless_teams import cleanup_headless_teams
from .get_data_counts import get_data_counts
from .get_detailed_stats import get_detailed_stats
from .reset_all_plugin_data import reset_all_plugin_data
from .reset_event_data import reset_event_data

__all__ = [
    "cleanup_orphaned_data",
    "cleanup_headless_teams",
    "get_data_counts",
    "get_detailed_stats",
    "reset_all_plugin_data",
    "reset_event_data",
]
