#!/usr/bin/env python3
"""
/plugin/tests/fixtures/reset_database.py
Database Reset Utility
Safely clears all custom plugin data while leaving ctfd core data intact.

Clears:
- all team members (ng_team_members)
- all custom teams (ng_teams)
- all user extensions (ng_users)
- all custom events (ng_events)

keeps
- ctfd core users, challenges, submissions, etc.
- All original ctfd functionality.
"""

import sys
import os

plugin_path = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.append(plugin_path)

from CTFd.models import db  # noqa: E402
from plugin.event.models.Event import Event  # noqa: E402
from plugin.team.models.Team import Team  # noqa: E402
from plugin.user.models.User import User  # noqa: E402
from plugin.team.models.TeamMember import TeamMember  # noqa: E402


def reset_plugin_data():
    """
    Reset all plugin specific data.
    """
    try:
        print(" Starting database reset...")

        team_members_count = TeamMember.query.count()
        if team_members_count > 0:
            TeamMember.query.delete()
            print(f"    Deleted {team_members_count} team members")
        else:
            print("   No team members to delete")

        teams_count = Team.query.count()
        if teams_count > 0:
            Team.query.delete()
            print(f"    Deleted {teams_count} teams")
        else:
            print("     No teams to delete")

        users_count = User.query.count()
        if users_count > 0:
            User.query.delete()
            print(f"    Deleted {users_count} user extensions")
        else:
            print("     No user extensions to delete")

        events_count = Event.query.count()
        if events_count > 0:
            Event.query.delete()
            print(f"    Deleted {events_count} events")
        else:
            print("     No events to delete")

        db.session.commit()

        print(" Database reset completed successfully!")
        print(" Plugin tables are now empty and ready for fresh data")

        return True

    except (ImportError, AttributeError) as e:
        print(f" Error with module imports: {str(e)}")
        db.session.rollback()
        return False
    except Exception as e:
        # Broad catch needed for unknown database errors during destructive operations
        print(f" Error during reset: {str(e)}")
        db.session.rollback()
        return False


def confirm_reset():
    """
    Confirm the database reset.
    """
    print("  DATABASE RESET WARNING")
    print("This will delete ALL plugin data:")
    print("  - All events")
    print("  - All teams")
    print("  - All team members")
    print("  - All user extensions")
    print()
    print("CTFd core data (users, challenges, etc.) will not be affected.")
    print()

    response = input("Are you sure you want to continue? (type 'yes' to confirm): ")

    if response.lower() == "yes":
        return True
    else:
        print(" Reset cancelled")
        return False


def show_current_data():
    """
    Show the current data counts before reset.
    """
    try:
        events_count = Event.query.count()
        teams_count = Team.query.count()
        users_count = User.query.count()
        team_members_count = TeamMember.query.count()

        print(" Current Plugin Data:")
        print(f"  - Events: {events_count}")
        print(f"  - Teams: {teams_count}")
        print(f"  - User Extensions: {users_count}")
        print(f"  - Team Members: {team_members_count}")
        print()

        if events_count == 0 and teams_count == 0 and users_count == 0 and team_members_count == 0:
            print(" Database is already empty!")
            return False

        return True

    except (ImportError, AttributeError) as e:
        print(f" Error with module imports: {str(e)}")
        return False
    except Exception as e:
        # Broad catch needed for unknown database errors during data inspection
        print(f" Error checking current data: {str(e)}")
        return False


if __name__ == "__main__":
    print("  CTFd Plugin Database Reset Utility")
    print("=" * 50)

    has_data = show_current_data()

    if not has_data:
        print("Nothing to reset. Exiting.")
        sys.exit(0)

    if confirm_reset():
        success = reset_plugin_data()

        if success:
            print()
            print(" What's next:")
            print("  - Run tests to create sample data")
            print("  - Use seed_data.py to generate test scenarios")
            print("  - Start fresh with your plugin development")
        else:
            print(" Reset failed. Check the error message above.")
            sys.exit(1)

    print()
    print("Reset utility finished")
