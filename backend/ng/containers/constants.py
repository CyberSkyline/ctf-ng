import re

DOCKER_RUNNING = "running"
DOCKER_BRIDGE = "bridge"
CHALLENGER_NET_NAME = "competitor_net"
DOCKER_MEM_REGEX = re.compile(r"([1-9][0-9]*)([bkmg]?)")
