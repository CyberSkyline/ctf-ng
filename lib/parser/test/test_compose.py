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
from typing import cast
from cyber_skyline.chall_parser.compose.types import ComposeResourceName
import pytest
from cyber_skyline.chall_parser.compose import (
    ComposeFile, Network, ServicesDict, NetworksDict, Service, ChallengeInfo
    
)
from cyber_skyline.chall_parser.compose.validators import validate_compose_name_pattern

class TestNetwork:
    def test_network_requirements(self):
        """Test that networks must be internal."""
        network = Network(internal=True)
        assert network.internal is True

class TestComposeFile:
    def test_minimal_compose_file(self):
        """Test creating a minimal compose file."""
        challenge = ChallengeInfo(
            name="Test Challenge",
            description="A test challenge",
            questions=[],
        )
        services = {}
        compose = ComposeFile(challenge=challenge, services=services, networks=None)
        assert compose.challenge.name == "Test Challenge"
        assert compose.services == {}
        assert compose.networks is None

    def test_compose_file_with_all_sections(self):
        """Test ComposeFile with all possible sections."""
        challenge = ChallengeInfo(
            name="Full Test",
            description="Testing all sections",
            questions=[]
        )
        
        services = {
            ComposeResourceName("web"): Service(image="nginx", hostname="web", networks=[ComposeResourceName("frontend"), ComposeResourceName("competitor_net")]),
            ComposeResourceName("db"): Service(image="postgres", hostname="db", networks=[ComposeResourceName("backend"), ComposeResourceName("competitor_net")])
        }
        
        networks = {
            ComposeResourceName("frontend"): Network(internal=True),
            ComposeResourceName("backend"): Network(internal=True),
            ComposeResourceName("competitor_net"): Network(internal=True)
        }
        
        compose = ComposeFile(
            challenge=challenge,
            services=cast(ServicesDict, services),
            networks=cast(NetworksDict, networks)
        )
        
        assert len(compose.services) == 2
        assert compose.networks is not None
        assert len(compose.networks) == 3
        assert compose.challenge.name == "Full Test"

class TestComposeNameValidation:
    def test_compose_name_pattern_validator_edge_cases(self):
        """Test edge cases for compose name pattern validation."""
        
        # Test with valid patterns
        valid_names = {
            ComposeResourceName("a"): "value",
            ComposeResourceName("1"): "value", 
            ComposeResourceName("a-b"): "value",
            ComposeResourceName("a_b"): "value",
            ComposeResourceName("a.b"): "value",
            ComposeResourceName("a1b2c3"): "value"
        }
        for name in valid_names.keys():
            validate_compose_name_pattern(None, type('obj', (), {'name': 'test'})(), name)

    def test_invalid_compose_names(self):
        """Test that invalid compose names are rejected."""
        invalid_dict = {
            ComposeResourceName("service with spaces"): "value",
            ComposeResourceName("service@special"): "value"
        }
        
        class MockInstance:
            pass
        
        class MockAttribute:
            name = "services"
        
        for key in invalid_dict.keys():
            with pytest.raises(ValueError, match="must match pattern"):
                validate_compose_name_pattern(MockInstance(), MockAttribute(), key)