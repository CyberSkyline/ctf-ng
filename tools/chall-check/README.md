# chall-check

A Docker Compose parser with CTF challenge extension that supports templated variables, challenge metadata, and validation. This project consists of two main components:

- **`cyber-skyline-chall-parser`** - Core parsing library for handling specialized challenge Docker Compose format
- **`cyber-skyline-chall-check`** - CLI validation tool for testing and inspecting challenge configurations

## Project Structure

This is part of the CTF-NG project with the following structure:

```
ctf-ng/
├── lib/parser/                    # Core parsing library (cyber-skyline-chall-parser)
└── tools/chall-check/             # CLI validation tool (cyber-skyline-chall-check)
```

## Usage

The `chall-check` CLI tool provides commands to validate, inspect, and test CTF challenge Docker Compose files.

### Installation

```bash
pip install cyber-skyline-chall-check
```

### Commands

#### `validate` - Validate Challenge Files

Validate a CTF challenge Docker Compose file and display a comprehensive summary.

```bash
# Basic validation with summary
chall-check validate challenge.yml

# Verbose output with detailed logging
chall-check validate challenge.yml --verbose

# Different output formats
chall-check validate challenge.yml --format json
chall-check validate challenge.yml --format yaml
chall-check validate challenge.yml --format table  # default

# Skip the summary display
chall-check validate challenge.yml --no-summary
```

**What it validates:**
- Required fields in challenge configuration
- Valid template syntax
- Service configuration compliance  
- Network security requirements

#### `check` - Quick Validation

Performs validation and returns only exit codes (useful for scripts and CI/CD).

```bash
# Check a file (silent output)
chall-check check challenge.yml
echo $?  # 0 = valid, 1 = invalid

# Check from stdin
cat challenge.yml | chall-check check --stdin
```

#### `info` - Show Challenge Information

Display detailed information about a challenge configuration.

```bash
# Show full challenge summary
chall-check info challenge.yml

# Show specific field
chall-check info challenge.yml --field name
chall-check info challenge.yml --field description
chall-check info challenge.yml --field questions
chall-check info challenge.yml --field variables
```

#### `render` - Test Template Variables

Test Faker template variable generation to preview what values will be generated.

```bash
# Test all variables (shows 5 generations each)
chall-check render challenge.yml

# Test specific variable
chall-check render challenge.yml --variable flag_suffix

# Generate more examples
chall-check render challenge.yml --count 10

# Test specific variable with custom count
chall-check render challenge.yml --variable username --count 3
```

#### Template Testing
```bash
$ chall-check render challenge.yml --variable username

username
Template: {{ fake.user_name() }}
Default:  admin
Generated values:
  1. johnsmith42
  2. alice_jones
  3. mike_wilson
  4. sarah_chen
  5. david_garcia
```

### Global Options

```bash
# Show version
chall-check --version

# Get help for any command
chall-check validate --help
chall-check render --help
```

### Python Library Usage

You can also use the parser library directly in Python:

```python
from cyber_skyline.chall_parser import parse_compose_file, parse_compose_string, ComposeYamlParser

# Parse from file
compose_file = parse_compose_file("challenge.yml")
challenge_info = compose_file.challenge

# Parse from string
yaml_content = """
x-challenge:
  name: "Test Challenge"
  description: "A test challenge"
  questions:
    - name: "flag"
      question: "What is the flag?"
      points: 100
      answer: "CTF{.*}"
      max_attempts: 5

services:
  web:
    image: "nginx:alpine"
    hostname: "web-server"
"""

compose_file = parse_compose_string(yaml_content)

# Access challenge metadata
print(f"Challenge: {compose_file.challenge.name}")
print(f"Services: {list(compose_file.services.keys())}")

# Use the parser class directly for more control
parser = ComposeYamlParser()
compose_file = parser.parse_file("challenge.yml")
yaml_output = parser.to_yaml(compose_file)
```

## Parser Library Features

The underlying `cyber-skyline-chall-parser` library provides:

### Core Components

- **`ComposeYamlParser`** - Main parser class with template rewriting capabilities
- **`ComposeFile`** - Root data structure representing the entire compose file
- **`ChallengeInfo`** - CTF-specific challenge metadata (questions, hints, variables)
- **`Service`** - Docker service definitions with security restrictions
- **`Template`** - Faker-based template system for dynamic value generation
- **`Rewriter`** - YAML event processor for template substitution

### Key Features

- **Template System**: Uses Python Faker for generating randomized values (flags, passwords, etc.)
- **Validation**: Comprehensive validation of challenge configurations and Docker settings
- **Type Safety**: Full type annotations and cattrs-based serialization
- **Error Handling**: Detailed error messages with location information

### Supported Docker Compose Features

The parser supports the following Docker Compose features:

**Supported:**
- Basic service definitions (`image`, `hostname`, `command`, `entrypoint`)
- Environment variables with template support
- Internal-only networking
- Resource limits (`mem_limit`, `cpus`)
- Limited Linux capabilities (`NET_ADMIN`, `SYS_PTRACE`)
- User specification

**Not Supported:**
- External network access
- Volume mounts
- Privileged containers
- Host networking
- External secrets/configs

**Ignored:**
- Build
- Ports
- TTY and stdin_open
- Develop, Logging, And Healthcheck

### Template System

Templates use [Python Faker](https://faker.readthedocs.io/) providers:

```python
from cyber_skyline.chall_parser.rewriter import Template

# Create templates programmatically
flag_template = Template("fake.bothify('CTF{????-####}', letters='ABCDEF')")
password_template = Template("fake.password(length=12)")

# Evaluate templates
flag_value = flag_template.eval()  # e.g., "CTF{ABCD-1234}"
password_value = password_template.eval()  # e.g., "P@ssw0rd123!"
```

## Architecture & Design

### Security Considerations

The parser intentionally restricts Docker Compose features to prevent common security issues in CTF environments:

1. **No External Network Access**: All networks must be `internal: true`
2. **No Volume Mounts**: Prevents file system access outside container
3. **Limited Capabilities**: Only specific Linux capabilities allowed
4. **Resource Limits**: Memory and CPU constraints required for resource management


### Exit Codes

- `0`: Success/Valid
- `1`: Validation error or invalid file

## Specification

The CTF Challenge format extends Docker Compose with a required `x-challenge` section containing CTF-specific metadata. Below is the complete specification based on the `ComposeFile` class structure:

### File Structure

```yaml
# Complete Challenge Specification
x-challenge:          # Required: CTF challenge metadata
  # ... challenge definition
  
services:             # Optional: Docker services (at least one recommended)
  # ... service definitions
 
networks:             # Optional: Internal-only network definitions
  # ... network definitions
```

### Root Level Fields

#### `x-challenge` (Required)
Contains all CTF-specific challenge information including questions, hints, and template variables.

#### `services` (Optional)
Dictionary of Docker services that make up the challenge infrastructure. Each service is constrained to CTF-appropriate configurations with security restrictions.

#### `networks` (Optional)
Dictionary of network definitions for service communication. All networks must be internal-only for security.

### Challenge Info Structure (`x-challenge`)

```yaml
x-challenge:
  # Optional fields
  icon: "TbFlag"                          # String: Tabler icon name (validated)
  summary: "Challenge overview"           # String: Brief challenge summary
  hints:                                  # List[Hint]: Available hints
    - body:                               # TextBody|String: Hint content
        type: text                        # Literal['text']: Hint type
        content: "Check the source code"   # String: Full hint text
      preview: "Code hint"                # String: Brief preview before unlock
      deduction: 10                       # Integer: Points deducted when used
    - body: "Simple string hint"          # String: Simple text hint
      preview: "General hint"             # String: Hint preview
      deduction: 5                        # Integer: Point deduction
  
  # Template system
  templates:                              # Dict[str, str]: Reusable template definitions
    flag-template: &flag_tmpl "fake.bothify('CTF{????-####}', letters='ABCDEF')"
    
  variables:                              # Dict[str, Variable]: Template variables
    db_password:                          # String: Variable name
      template: "fake.password(length=12)" # Template: Faker template string
      default: &db_pass "SecureP4ss!"     # String: Default value with YAML anchor
    session_id:
      template: "fake.uuid4()" # Template: Faker template string
      default: &session_id "01905492-7ea3-42e7-95b4-c0ac73c6912f"     # String: Default value with YAML anchor
  # Required fields 
  name: "Challenge Name"                    # String: Challenge title
  description: "Challenge description"      # String: Detailed description for participants

  questions:                               # List[Question]: Questions/objectives (required)
    - name: "flag 1"                       # String: Developer-facing identifier
      body: "What is the flag?"            # String: Question text for participants  
      points: 100                          # Integer: Points awarded for correct answer
      answer: "CTF\\{.*\\}"                # String|Answer|Template: Regex pattern or exact answer
      max_attempts: 5                      # Integer: Maximum submission attempts
    - name: "flag 2"                       # String: Developer-facing identifier
      body: "What is the flag?"            # String: Question text for participants  
      points: 100                          # Integer: Points awarded for correct answer
      answer:                              # String|Answer|Template: Regex pattern or exact answer
        body: "CTF\\{.*\\}"                # String: Regex pattern or exact answer
        test_cases:                        # List[AnswerTestCase]: List of Test Cases that must validate against the body
          - answer: "CTF{word}"            # String: Answer to the question
            correct: true                  # Boolean: Whether the Answer is Correct or Not
          - answer: "CTF"
            correct: false
      max_attempts: 5                      # Integer: Maximum submission attempts
    - name: "flag 3"                       # String: Developer-facing identifier
      body: "What is the session id?"            # String: Question text for participants  
      points: 100                          # Integer: Points awarded for correct answer
      answer: *session_id                  # String|Answer|Template: Regex pattern or exact answer
      max_attempts: 5                      # Integer: Maximum submission attempts
      
  tags: ["web", "beginner"]               # List[str]: Category tags
```

### Service Structure

```yaml
services:
  service_name:
    # Required fields
    image: "nginx:alpine"                  # String: Docker image
    hostname: "web-server"                # String: Container hostname
    
    # Core operational fields
    command: ["/start.sh", "--debug"]     # String|List[str]: Override default command
    entrypoint: "/entrypoint.sh"         # String|List[str]: Override default entrypoint
    
    # Environment configuration
    environment:                          # Dict[str, Template|str]|List[str]: Environment variables
      DB_HOST: "database"                 # String: Static value
      DB_PASSWORD: *db_pass               # Reference: YAML anchor reference
      SESSION_ID: *session_id # Template: Dynamic template
    # OR list format:
    # environment:
    #   - "DB_HOST=database"
    #   - "DEBUG=true"
    
    # Networking
    networks:                             # List[str]|Dict[str, None]: Network connections
      - "challenge-net"                   # List format: simple attachment
    # OR dict format:
    # networks:
    #   challenge-net: ~                  # Dict format: allows future expansion
    
    # Security and capabilities
    cap_add:                             # List[Literal['NET_ADMIN', 'SYS_PTRACE']]: Linux capabilities
      - "NET_ADMIN"                      # For network-related challenges
      - "SYS_PTRACE"                     # For debugging/reverse engineering
    
    # Resource constraints
    mem_limit: "512m"                    # String|int: Memory limit
    memswap_limit: "1g"                  # String|int: Memory + swap limit  
    cpus: "0.5"                          # String|float: CPU allocation
    
    # User context
    user: "1000:1000"                    # String: User to run container as
    
    # Ignored fields (supported but ignored in production)
    build: ~                             # Any: Build context (ignored)
    ports: ~                             # Any: Port mappings (ignored)
    stdin_open: ~                        # Any: Interactive mode (ignored)
    tty: ~                               # Any: TTY allocation (ignored)
    logging: ~                           # Any: Logging config (ignored)
    healthcheck: ~                       # Any: Health checks (ignored)
    develop: ~                           # Any: Development features (ignored)
```

### Network Structure

```yaml
networks:
  network_name:
    internal: true                       # Literal[True]: Must be internal-only (required)
```

### Template System

Templates use Python Faker library for dynamic value generation:

```yaml
# Template variable definition
variables:
  variable_name:
    template: "fake.method(args)"        # Faker template string
    default: &anchor "default_value"     # Default with YAML anchor

# Template usage in services
services:
  web:
    environment:
      VAR_NAME: *anchor                  # Reference default value
```

### Data Types Reference

- **`ComposeFile`**: Root structure containing challenge, services, and networks
- **`ChallengeInfo`**: CTF metadata with questions, hints, and variables
- **`Service`**: Docker service with security restrictions
- **`Network`**: Internal-only network definition
- **`Question`**: Challenge question with points and answer validation
- **`Hint`**: Player hint with preview and point deduction
- **`Variable`**: Template variable with Faker generation
- **`Template`**: Faker-based dynamic value generator

### Security Restrictions

The format intentionally excludes many Docker Compose features for security:

**Excluded Features:**
- External network access (all networks must be `internal: true`)
- Volume mounts (file system access prevention)
- Privileged containers
- Host networking
- External secrets/configs

**Resource Requirements:**
- Memory limits encouraged for resource management
- CPU limits for fair resource allocation
- User specification recommended (non-root preferred)

### Validation Rules

1. **Required Fields**: `x-challenge`, `x-challenge.name`, `x-challenge.description`, `x-challenge.questions`
2. **Network Security**: All networks must have `internal: true`
3. **Template Syntax**: All templates must be valid Faker expressions
4. **Icon Validation**: Icons must be valid Tabler icon names
5. **Answer Patterns**: Answer fields must be valid regex patterns or a variable



## Development

### Project Information

- **Author**: John Marsden (research@johnmarsden.dev)
- **Version**: 0.1.8 (both packages)
- **License**: MIT License
- **Copyright**: 2025 Cyber Skyline

### Building from Source

```bash
# Install development dependencies
cd tools/chall-check
pip install -e ".[dev]"

# Run tests
pytest

# Build packages
python -m build
```

### Testing

The project includes comprehensive test suites for both components:

```bash
# Test the parser library
cd lib/parser
pytest test/

# Test the CLI tool
cd tools/chall-check  
pytest test/
```

### Contributing

This is part of the CTF-NG research project. The parser is designed specifically for CTF challenge deployment with security and simplicity as primary concerns.

## License

MIT License - Copyright 2025 Cyber Skyline

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.


THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

