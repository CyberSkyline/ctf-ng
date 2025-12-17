#!/usr/bin/env python3
import argparse
from datetime import timedelta
from CTFd import create_app, CTFdFlask
from CTFd.plugins.ng.team.models.Team import Team
from CTFd.plugins.ng.challenge.models.Challenge import Challenge
from CTFd.plugins.ng.containers.models.ContainerInstance import ContainerInstance
from CTFd.plugins.ng.containers.models.IndvidualContainer import IndvidualContainer
from CTFd.plugins.ng.core.utils import utc_now

parser = argparse.ArgumentParser(
    prog="stop-exhausted-teams",
    description="Stops containers for teams that have exhausted their time"
)

parser.add_argument("-d", "--days", action="store", default=1, type=int, help="Specifies how many days back to look for exhausted teams")

args = parser.parse_args()

app: CTFdFlask = create_app()


now = utc_now()
delta = timedelta(days=args.days)
query_end_date_start = now - delta

with app.app_context():
    res = Team.query.filter(Team.end_time >= query_end_date_start).all()
    for team in res:
        challenges = Challenge.query.filter(Challenge.event == team.event).all()
        for challenge in challenges:
            ContainerInstance.stop_instance_group(challenge.id, team.id)

        for member in team.members:
            workspace_ctr = IndvidualContainer.get_user_indvidual_container(member.user_id)
            workspace_ctr.disconnect_from_networks()
            workspace_ctr.stop()
