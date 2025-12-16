#!/usr/bin/env python3
from CTFd import create_app, CTFdFlask
from CTFd.plugins.ng.team.models.Team import Team
from CTFd.plugins.ng.challenge.models.Challenge import Challenge
from CTFd.plugins.ng.containers.models.ContainerInstance import ContainerInstance
from CTFd.plugins.ng.core.utils import utc_now
from datetime import timedelta

app: CTFdFlask = create_app()


now = utc_now()
delta = timedelta(days=3)
query_end_date_start = now - delta

with app.app_context():
    res = Team.query.filter(Team.end_time >= query_end_date_start).all()
    for team in res:
        challenges = Challenge.query.filter(Challenge.event == team.event).all()
        for challenge in challenges:
            #ContainerInstance.stop_instance_group(challenge.id, team.id)
            ContainerInstance.delete_instance_group(challenge.id, team.id)
