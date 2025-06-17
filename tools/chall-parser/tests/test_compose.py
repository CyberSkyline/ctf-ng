from typing import cast
import pytest
from parser.compose import (
    ComposeFile, Network, ComposeResourceName, ServicesDict, NetworksDict, Service, ChallengeInfo
    
)
from parser.compose.validators import validate_compose_name_pattern

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
            questions=[]
        )
        compose = ComposeFile(challenge=challenge)
        assert compose.challenge.name == "Test Challenge"
        assert compose.services is None
        assert compose.networks is None

    def test_compose_file_with_all_sections(self):
        """Test ComposeFile with all possible sections."""
        challenge = ChallengeInfo(
            name="Full Test",
            description="Testing all sections",
            questions=[]
        )
        
        services = {
            ComposeResourceName("web"): Service(image="nginx", hostname="web"),
            ComposeResourceName("db"): Service(image="postgres", hostname="db")
        }
        
        networks = {
            ComposeResourceName("frontend"): Network(internal=True),
            ComposeResourceName("backend"): Network(internal=True)
        }
        
        compose = ComposeFile(
            challenge=challenge,
            services=cast(ServicesDict, services),
            networks=cast(NetworksDict, networks)
        )
        
        assert len(compose.services) == 2
        assert compose.networks is not None
        assert len(compose.networks) == 2
        assert compose.challenge.name == "Full Test"

class TestComposeNameValidation:
    def test_compose_name_pattern_validator_edge_cases(self):
        """Test edge cases for compose name pattern validation."""
        # Test with empty dict
        validate_compose_name_pattern(None, type('obj', (), {'name': 'test'})(), {})
        
        # Test with valid patterns
        valid_names = {
            "a": "value",
            "1": "value", 
            "a-b": "value",
            "a_b": "value",
            "a.b": "value",
            "a1b2c3": "value"
        }
        validate_compose_name_pattern(None, type('obj', (), {'name': 'test'})(), valid_names)

    def test_invalid_compose_names(self):
        """Test that invalid compose names are rejected."""
        invalid_dict = {
            "service with spaces": "value",
            "service@special": "value"
        }
        
        class MockInstance:
            pass
        
        class MockAttribute:
            name = "services"
        
        with pytest.raises(ValueError, match="must match pattern"):
            validate_compose_name_pattern(MockInstance(), MockAttribute(), invalid_dict)