#!/usr/bin/env python3
"""
/plugin/tests/fixtures/seed_data.py
Seed data
"""

import random
import string
from datetime import datetime, timedelta

from CTFd.models import db
from CTFd.models import Users as CTFdUsers
import sys
import os

plugin_path = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, plugin_path)

from plugin.event.models.Event import Event  # noqa: E402
from plugin.team.models.Team import Team  # noqa: E402
from plugin.user.models.User import User  # noqa: E402
from plugin.team.models.TeamMember import TeamMember  # noqa: E402


db.create_all()


class SeedDataGenerator:
    """Generates test data for the plugin."""

    def __init__(self):
        self.created_data = {
            "ctfd_users": [],
            "ng_users": [],
            "events": [],
            "teams": [],
            "team_members": [],
        }

    def generate_invite_code(self, length=6):
        """Generate a random invite code."""
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))

    def create_ctfd_users(self, count=6):
        """Create CTFd users for testing."""
        print(f"Creating {count} CTFd users...")

        # mario
        first_names = ["Mario", "Luigi", "Peach", "Daisy", "Toad", "Yoshi"]
        last_names = ["Bro", "Toadstool", "Koopa", "Troopa", "Kong", "Star"]

        for i in range(count):
            first = first_names[i % len(first_names)]
            last = last_names[i % len(last_names)]
            name = f"{first} {last}"
            email = f"{first.lower()}.{last.lower()}@example.com"

            ctfd_user = CTFdUsers(
                name=name,
                email=email,
                password="Password123!",
                type="user",
                verified=True,
            )
            db.session.add(ctfd_user)
            db.session.commit()
            self.created_data["ctfd_users"].append(ctfd_user)

        print(f" Created {count} CTFd users")

    def create_ng_users(self):
        """Create ng_user extensions for all CTFd users."""
        print("Creating ng_user extensions...")

        for ctfd_user in self.created_data["ctfd_users"]:
            ng_user = User(id=ctfd_user.id)
            db.session.add(ng_user)
            self.created_data["ng_users"].append(ng_user)

        db.session.commit()
        print(f" Created {len(self.created_data['ng_users'])} ng_user extensions")

    def create_events(self, count=2):
        """Create test events."""
        print(f"Creating {count} events...")

        event_data = [
            {
                "name": "Mushroom Kingdom",
                "description": "Classic Mario event with castles and pipes",
            },
            {
                "name": "Bowser's Castle",
                "description": "Dark fortress with lava and traps",
            },
        ]

        for i in range(count):
            data = event_data[i % len(event_data)]
            event = Event(name=data["name"], description=data["description"])
            db.session.add(event)
            db.session.commit()
            self.created_data["events"].append(event)

        print(f" Created {count} events")

    def create_teams(self, teams_per_event=2):
        """Create teams in each event."""
        print(f"Creating {teams_per_event} teams per event...")

        team_names = ["Super Stars", "Fire Flowers", "1-UP Squad", "Pipe Dreamers"]

        total_teams = 0
        for event in self.created_data["events"]:
            for i in range(teams_per_event):
                team_name = team_names[i % len(team_names)]
                invite_code = self.generate_invite_code()

                team = Team(
                    name=f"{team_name} ({event.name})",
                    event_id=event.id,
                    invite_code=invite_code,
                    max_team_size=4,
                )
                db.session.add(team)
                db.session.commit()
                self.created_data["teams"].append(team)
                total_teams += 1

        print(f" Created {total_teams} teams")

    def create_team_members(self):
        """Create team members."""
        print("Creating team members...")

        # assigning users to teams
        user_index = 0
        total_team_members = 0

        for team in self.created_data["teams"]:
            members_count = random.randint(2, 3)

            for _ in range(members_count):
                if user_index >= len(self.created_data["ng_users"]):
                    break

                ng_user = self.created_data["ng_users"][user_index]
                membership = TeamMember(
                    team_id=team.id,
                    user_id=ng_user.id,
                    event_id=team.event_id,
                    joined_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                )
                db.session.add(membership)
                self.created_data["team_members"].append(membership)
                total_team_members += 1
                user_index += 1

        db.session.commit()
        print(f" Created {total_team_members} team members")

    def generate_all_data(self, users=6, events=2, teams_per_event=2):
        """Generate complete test dataset."""
        print(" Starting seed data generation...")
        print("=" * 50)

        self.create_ctfd_users(users)
        self.create_ng_users()
        self.create_events(events)
        self.create_teams(teams_per_event)
        self.create_team_members()

        print("=" * 50)
        print(" Seed data generation completed")

        # Summary
        print(" Created:")
        print(f"   • {len(self.created_data['ctfd_users'])} CTFd users")
        print(f"   • {len(self.created_data['ng_users'])} ng_user extensions")
        print(f"   • {len(self.created_data['events'])} events")
        print(f"   • {len(self.created_data['teams'])} teams")
        print(f"   • {len(self.created_data['team_members'])} team members")


def demo_seed():
    """Generate quick demo seed data."""
    generator = SeedDataGenerator()
    generator.generate_all_data()


def clear_data():
    """Clear all plugin data."""
    print("  Clearing all plugin data...")

    TeamMember.query.delete()
    Team.query.delete()
    User.query.delete()
    Event.query.delete()

    db.session.commit()
    print("plugin data cleared")
