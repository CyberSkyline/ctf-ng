# Copyright 2025 Cyber Skyline

# Permission is hereby granted, free of charge, to any person obtaining a 
# copy of this software and associated documentation files (the “Software”), 
# to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS 
# IN THE SOFTWARE.
"""
Docker Compose File Structure for CTF Challenges

This module defines a simplified Docker Compose file structure specifically designed
for CTF challenge deployment. It enforces security constraints and validation while
supporting the x-challenge extension for CTF-specific metadata.
"""

from typing import Literal, NewType, Dict
import attr
import attr.validators as v

from cyber_skyline.chall_parser.compose.service import Service
from cyber_skyline.chall_parser.compose.challenge_info import ChallengeInfo
from cyber_skyline.chall_parser.compose.validators import validate_compose_name_pattern

@attr.s
class Network:
    """Represents a Docker Compose network configuration for CTF challenges.
    
    This is a heavily simplified network definition that only supports internal networks.
    External network access is explicitly disabled for security reasons.
    """
    internal: Literal[True] = attr.ib(validator=v.in_([True]))  # All networks must be internal (no external access)

# Custom types for pattern-validated dictionaries
# These provide type safety while enforcing naming constraints
ComposeResourceName = NewType('ComposeResourceName', str)
ServicesDict = Dict[ComposeResourceName, Service]
NetworksDict = Dict[ComposeResourceName, Network]

@attr.s
class ComposeFile:
    """Main Docker Compose file structure for CTF challenges.
    
    This represents a complete compose.yml file with CTF-specific extensions.
    The design prioritizes security and simplicity over full Docker Compose compatibility.
    """
    
    # CTF-specific extension - this is the core purpose of our custom format
    challenge: ChallengeInfo = attr.ib() # Required x-challenge block with CTF metadata
    # Every compose file must define challenge information since this is
    # specifically for CTF challenge deployment, not general Docker orchestration
    
    # Core Docker Compose sections with security constraints
    services: ServicesDict = attr.ib(
        default=None, 
        validator=v.optional(validate_compose_name_pattern)
    )
    # Container services that make up the challenge infrastructure
    # - Names must follow Docker naming conventions
    # - Each service is constrained to CTF-appropriate configurations
    # TODO: Consider if we should require at least one service

    networks: NetworksDict | None = attr.ib(
        default=None,
        validator=v.optional(validate_compose_name_pattern)
    )
    # Network definitions for service communication
    # - All networks are internal-only for security
    # - Names must follow Docker naming conventions
    # - Optional since simple challenges might not need custom networking

# Deliberately excluded Docker Compose features:
# - volumes: Persistent storage could be a security risk and complexity issue
# - secrets: We handle secrets through our own variable system
# - configs: Configuration is handled through environment variables and templates

# Design Decisions:
#
# 1. Security First: Many standard Docker Compose features are excluded
#    to reduce attack surface. External network access, volume mounts,
#    and privileged operations are not supported.
#
# 2. CTF-Specific: The required challenge field makes this format
#    specifically for CTF challenges, not general container orchestration.
#
# 3. Validation: All resource names are validated to prevent injection
#    attacks and ensure cross-platform compatibility.
#
# 4. Simplicity: Only essential Docker Compose features are supported
#    to reduce complexity and potential configuration errors.
#
# Usage example:
# challenge:
#   name: "Web Security Challenge"
#   description: "Find the SQL injection vulnerability"
#   questions:
#     - name: "flag"
#       question: "What is the admin password?"
#       points: 100
#       answer: "admin123"
#       max_attempts: 5
#
# services:
#   web:
#     image: "challenge/web-vuln:latest"
#     hostname: "web-server"
#     environment:
#       - "DB_HOST=database"
#   database:
#     image: "postgres:13"
#     hostname: "db-server"
#     environment:
#       - "POSTGRES_PASSWORD=secret"
#
# networks:
#   challenge-net:
#     internal: true
#   database:
#     image: "postgres:13"
#     hostname: "db-server"
#     environment:
#       - "POSTGRES_PASSWORD=secret"
#
# networks:
#   challenge-net:
#     internal: true

