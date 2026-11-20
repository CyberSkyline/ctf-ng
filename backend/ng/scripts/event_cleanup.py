#!/usr/bin/env python3

import argparse
import contextlib
import io
import logging
import os
import re
import sys
import warnings
from datetime import UTC, datetime

from CTFd import create_app
from CTFd.models import db

if "SCRIPT" not in os.environ:
    raise OSError("This should only be run from a script. DO NOT run this manually.")

parser = argparse.ArgumentParser(description="Stop or remove the challenge containers for an event.")
event_arg = parser.add_mutually_exclusive_group(required=True)
event_arg.add_argument("--event-id", type=int, help="ID of the event")
event_arg.add_argument("--name", help="Name of the event (case-insensitive, partial match allowed)")
parser.add_argument("--stop", action="store_true", help="Stop the event's containers")
parser.add_argument("--prune", action="store_true", help="Remove the event's containers, networks and DB rows (overrides --stop)")
parser.add_argument("--allow-active", action="store_true", help="Allow stop or prune before the event has ended")
args = parser.parse_args()

# Names set by ContainerInstance: {team_id}-{name}-{challenge_id} and {name}-{team_id}-{challenge_id}
# Workspaces ({user_id}-indv) never match these
CONTAINER_NAME = re.compile(r"^(\d+)-.+-(\d+)$")
NETWORK_NAME = re.compile(r"^.+-(\d+)-(\d+)$")


def human_size(num):
    for unit in ("B", "KB", "MB", "GB"):
        if num < 1024:
            return f"{num:.1f}{unit}"
        num /= 1024
    return f"{num:.1f}TB"


warnings.filterwarnings("ignore")
logging.disable(logging.WARNING)
with contextlib.redirect_stdout(io.StringIO()):
    app = create_app()

with app.app_context():
    from CTFd.plugins.ng.containers.models.ContainerInstance import ContainerInstance
    from CTFd.plugins.ng.containers.utils.get_client import get_client
    from CTFd.plugins.ng.event.models.Event import Event
    # Imported after CTFd so gevent has already patched ssl, otherwise TLS connections fail
    from docker.errors import NotFound

    # Anything already gone is skipped, so the script is safe to rerun
    def ignore_missing(fn, *args, **kwargs):
        try:
            fn(*args, **kwargs)
        except NotFound:
            pass

    hosts = [host.strip() for host in (os.getenv("DOCKER_HOST") or "").split(",") if host.strip()]
    if not hosts:
        print("Error: DOCKER_HOST is not set.")
        sys.exit(1)

    if args.event_id is not None:
        event = db.session.get(Event, args.event_id)
        events = [event] if event else []
    else:
        events = Event.query.filter(Event.name.ilike(f"%{args.name}%")).order_by(Event.id).all()
        events = [event for event in events if event.name.lower() == args.name.lower()] or events

    if not events:
        print("Error: event not found.")
        sys.exit(1)

    if len(events) > 1:
        print("Error: more than one event matches, use --event-id instead:")
        for event in events:
            print(f"  {event.id}: {event.name}")
        sys.exit(1)

    event = events[0]
    team_ids = {team.id for team in event.teams}
    challenge_ids = {challenge.id for challenge in event.challenges}
    rows = ContainerInstance.query.filter(ContainerInstance.team_id.in_(team_ids)).all()

    def belongs_to_event(match):
        if not match:
            return False
        team_id, challenge_id = int(match[1]), int(match[2])
        return team_id in team_ids and challenge_id in challenge_ids

    for row in rows:
        if row.hostip not in hosts:
            print(f"Warning: {row.hostip} has containers for this event but is not in DOCKER_HOST, including it anyway.")
            hosts.append(row.hostip)

    apis = {host: get_client(host).api for host in hosts}
    containers = []
    networks = []

    for host, api in apis.items():
        for container in api.containers(all=True, size=True):
            name = container["Names"][0].lstrip("/")
            if belongs_to_event(CONTAINER_NAME.match(name)):
                containers.append({
                    "host": host,
                    "id": container["Id"],
                    "name": name,
                    "state": container["State"],
                    "size": container.get("SizeRw") or 0,
                })

        # Swarm networks show up on every host they're used on
        for network in api.networks():
            if belongs_to_event(NETWORK_NAME.match(network["Name"])):
                networks.append((host, network["Name"]))

    row_docker_ids = {row.dockerid for row in rows}
    container_ids = {container["id"] for container in containers}
    network_names = {name for _, name in networks}
    total_size = human_size(sum(container["size"] for container in containers))
    running = [container for container in containers if container["state"] == "running"]

    print(f"Event {event.id}: {event.name} (ends {event.end_time or 'never'})")
    print(f"Hosts: {', '.join(hosts)}\n")
    for container in sorted(containers, key=lambda c: (c["host"], c["name"])):
        no_row = "" if container["id"] in row_docker_ids else " (no DB row)"
        print(f"{container['host']:<16} {container['state']:<10} {human_size(container['size']):>9}  {container['name']}{no_row}")
    for name in sorted(network_names):
        print(f"network  {name}")

    print(f"\nFound {len(containers)} containers ({len(running)} running, {total_size}), "
          f"{len(network_names)} networks and {len(rows)} DB rows "
          f"({len(row_docker_ids - container_ids)} with no container).")

    # No flags just lists
    if not args.stop and not args.prune:
        sys.exit(0)

    if event.end_time and event.end_time > datetime.now(UTC).replace(tzinfo=None) and not args.allow_active:
        print(f"Error: event has not ended yet (ends {event.end_time}). Use --allow-active to clean up anyway.")
        sys.exit(1)

    if not args.prune:
        for container in running:
            ignore_missing(apis[container["host"]].stop, container["id"], timeout=5)
        print(f"\nDone: stopped {len(running)} containers.")
        sys.exit(0)

    for container in containers:
        ignore_missing(apis[container["host"]].remove_container, container["id"], force=True)

    ContainerInstance.query.filter(ContainerInstance.id.in_([row.id for row in rows])).delete(synchronize_session=False)
    db.session.commit()

    # Removing a container also frees its disk space
    # Workspaces can still be attached to challenge networks, so they're disconnected (not removed)
    # The swarm load balancer endpoint (lb-<network>) can't be disconnected and is skipped
    disconnected = 0
    for host, name in networks:
        try:
            attached = apis[host].inspect_network(name).get("Containers") or {}
        except NotFound:
            continue
        for container_id in attached:
            if container_id != f"lb-{name}":
                apis[host].disconnect_container_from_network(container_id, name, force=True)
                disconnected += 1
        ignore_missing(apis[host].remove_network, name)

    print(f"\nDone: removed {len(containers)} containers ({total_size}), {len(network_names)} networks and {len(rows)} DB rows.")
    if disconnected:
        print(f"Disconnected {disconnected} workspaces from the event's networks.")
