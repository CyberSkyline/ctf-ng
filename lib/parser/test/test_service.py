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
from cyber_skyline.chall_parser.compose.service import Service
from cyber_skyline.chall_parser.rewriter import Template

class TestService:
    def test_minimal_service(self):
        """Test creating a service with only required fields."""
        service = Service(
            image="nginx:latest",
            hostname="web-server"
        )
        assert service.image == "nginx:latest"
        assert service.hostname == "web-server"

    def test_service_with_all_resource_constraints(self):
        """Test service with all possible resource constraints."""
        service = Service(
            image="app:latest",
            hostname="test-server",
            mem_limit="1g",
            memswap_limit="2g", 
            cpus="1.5"
        )
        assert service.mem_limit == "1g"
        assert service.memswap_limit == "2g"
        assert service.cpus == "1.5"

    def test_service_with_capabilities(self):
        """Test service with Linux capabilities."""
        service = Service(
            image="app:latest",
            hostname="test-server",
            cap_add=["NET_ADMIN", "SYS_PTRACE"]
        )
        assert service.cap_add is not None
        assert "NET_ADMIN" in service.cap_add
        assert "SYS_PTRACE" in service.cap_add

    def test_service_with_user(self):
        """Test service with user specification."""
        service = Service(
            image="app:latest",
            hostname="test-server",
            user="1000:1000"
        )
        assert service.user == "1000:1000"

    def test_service_with_ignored_fields(self):
        """Test that ignored fields are accepted but not processed."""
        service = Service(
            image="app:latest",
            hostname="test-server",
            build={"context": "."},
            ports=["80:80"],
            stdin_open=True,
            tty=True,
            logging={"driver": "json-file"},
            healthcheck={"test": "exit 0"},
            develop={"watch": []}
        )
        
        # These fields should be present but ignored
        assert service.build is not None
        assert service.ports is not None
        assert service.stdin_open is not None
        assert service.tty is not None
        assert service.logging is not None
        assert service.healthcheck is not None
        assert service.develop is not None

    def test_service_with_templates_in_environment(self):
        """Test service with Template objects in environment."""
        template = Template("fake.uuid4()", "session_id")
        service = Service(
            image="app:latest",
            hostname="test-server",
            environment={
                "STATIC_VAR": "static_value",
                "TEMPLATE_VAR": template
            }
        )
        
        assert service.environment is not None
        assert isinstance(service.environment, dict)
        assert "STATIC_VAR" in service.environment
        assert "TEMPLATE_VAR" in service.environment
        assert service.environment["STATIC_VAR"] == "static_value"
        assert isinstance(service.environment["TEMPLATE_VAR"], Template)

    def test_service_extensions_field(self):
        """Test service extensions field."""
        service = Service(
            image="app:latest",
            hostname="test-server",
            extensions={"x-custom": "custom_value"}
        )
        assert service.extensions is not None
        assert service.extensions["x-custom"] == "custom_value"

    def test_service_networking_options(self):
        """Test service networking configuration options."""
        # Test list form
        service1 = Service(
            image="app:latest",
            hostname="test-server",
            networks=["frontend", "backend"]
        )
        assert service1.networks == ["frontend", "backend"]

        # Test dict form
        service2 = Service(
            image="app:latest",
            hostname="test-server",
            networks={"frontend": None, "backend": None}
        )
        assert isinstance(service2.networks, dict)
        assert "frontend" in service2.networks
        assert "backend" in service2.networks

    def test_service_command_and_entrypoint(self):
        """Test command and entrypoint configuration."""
        service = Service(
            image="app:latest",
            hostname="test-server",
            command=["python", "app.py"],
            entrypoint=["/entrypoint.sh", "webapp"]
        )
        assert service.command == ["python", "app.py"]
        assert service.entrypoint == ["/entrypoint.sh", "webapp"]