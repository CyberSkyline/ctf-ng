#!/usr/bin/env python3
"""
/plugin/tests/fixtures/reset_database.py
Database Reset Utility
Safely clears all custom plugin data while leaving ctfd core data intact.

Clears:
- all team memberships (ng_team_members)
- all custom teams (ng_teams)
- all user extensions (ng_users)
- all custom worlds (ng_worlds)

keeps
- ctfd core users, challenges, submissions, etc.
- All original ctfd functionality.
"""

import sys
import os

plugin_path = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.append(plugin_path)

from CTFd.models import db  # noqa: E402
from models.World import World  # noqa: E402
from models.Team import Team  # noqa: E402
from models.User import User  # noqa: E402
from models.TeamMember import TeamMember  # noqa: E402


def reset_plugin_data():
    """
    Reset all plugin specific data.
    """
    try:
        print(" Starting database reset...")

        memberships_count = TeamMember.query.count()
        if memberships_count > 0:
            TeamMember.query.delete()
            print(f"    Deleted {memberships_count} team memberships")
        else:
            print("    No team memberships to delete")

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

        worlds_count = World.query.count()
        if worlds_count > 0:
            World.query.delete()
            print(f"    Deleted {worlds_count} worlds")
        else:
            print("     No worlds to delete")

        db.session.commit()

        print(" Database reset completed successfully!")
        print(" Plugin tables are now empty and ready for fresh data")

        return True

    except Exception as e:
        print(f" Error during reset: {str(e)}")
        db.session.rollback()
        return False


def confirm_reset():
    """
    Confirm the database reset.
    """
    print("  DATABASE RESET WARNING")
    print("This will delete ALL plugin data:")
    print("  - All worlds")
    print("  - All teams")
    print("  - All team memberships")
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
        worlds_count = World.query.count()
        teams_count = Team.query.count()
        users_count = User.query.count()
        memberships_count = TeamMember.query.count()

        print(" Current Plugin Data:")
        print(f"  - Worlds: {worlds_count}")
        print(f"  - Teams: {teams_count}")
        print(f"  - User Extensions: {users_count}")
        print(f"  - Team Memberships: {memberships_count}")
        print()

        if worlds_count == 0 and teams_count == 0 and users_count == 0 and memberships_count == 0:
            print("✨ Database is already empty!")
            return False

        return True

    except Exception as e:
        print(f"❌ Error checking current data: {str(e)}")
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
