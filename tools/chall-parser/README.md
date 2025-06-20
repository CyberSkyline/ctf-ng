# Challenge Parser

A Docker Compose parser with CTF challenge extensions that supports templated variables and challenge metadata.

## Usage

The `chall-check` CLI tool provides commands to validate, inspect, and test CTF challenge Docker Compose files.

### Installation

```bash
# Install the parser
pip install -e .

# Or run directly
python -m parser.cli
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

### Exit Codes

- `0`: Success/Valid
- `1`: Validation error or invalid file

## Specification

Below is a complete example demonstrating all features of the challenge specification:

```yaml
# Complete Challenge Specification Example
x-challenge:
  # Required: Name of the challenge displayed to participants
  name: "Advanced Web Exploitation"
  
  # Required: Detailed description shown to participants
  description: |
    This challenge involves exploiting a vulnerable web application to retrieve
    multiple flags. You'll need to use SQL injection, XSS, and privilege escalation
    techniques to complete all objectives.
  
  # Optional: Tabler icon name with Tb prefix
  icon: "TbShieldAlt"
  
  # Required: List of questions/objectives for the challenge
  questions:
    - name: "SQL Injection Flag"
      question: "What is the flag hidden in the users table?"
      points: 150
      answer: "CTF\\{sql_1nj3ct10n_m4st3r\\}"  # Regex pattern
      max_attempts: 5
    
    - name: "Admin Panel Flag" 
      question: "What flag is displayed on the admin dashboard?"
      points: 200
      answer: "CTF\\{4dm1n_p4n3l_h4ck3d\\}"
      max_attempts: 3
    
    - name: "Privilege Escalation Flag"
      question: "What is the root flag on the server?"
      points: 300
      answer: "CTF\\{pr1v_3sc_c0mpl3t3\\}"
      max_attempts: 2
  
  # Optional: Hints that participants can unlock (with point deductions)
  hints:
    # Text hint
    - hint:
        type: text
        content: |
          Look for SQL injection vulnerabilities in the login form.
          Try using single quotes to break the SQL syntax.
      preview: "Database interaction hint"
      deduction: 25
    
    # Simple string hint
    - hint: "The admin panel might be accessible at /admin or /dashboard"
      preview: "Admin panel location"
      deduction: 30
    
    - hint:
        type: text
        content: "Check for SUID binaries or writable system files for privilege escalation"
      preview: "System exploitation hint"
      deduction: 50
  
  # Optional: Challenge summary/overview
  summary: |
    A multi-stage web exploitation challenge covering SQL injection,
    cross-site scripting, and Linux privilege escalation techniques.
  
  # Optional: Template definitions for reusable values
  templates:
    # Define reusable templates with anchors
    database-flag: &db_flag_template "fake.bothify('CTF{sql_??_####}', letters='ABCDEF')"
    admin-flag: &admin_flag_template "fake.bothify('CTF{admin_####}', letters='0123456789')"
  
  # Optional: Variable definitions with templates and defaults
  variables:
    # Database flag variable
    db_flag:
      template: *db_flag_template
      default: &db_flag_default "CTF{sql_1nj3ct10n_m4st3r}"
    
    # Admin panel flag
    admin_flag:
      template: *admin_flag_template  
      default: &admin_flag_default "CTF{4dm1n_p4n3l_h4ck3d}"
    
    # Database credentials
    db_password:
      template: "fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)"
      default: &db_pass_default "SecureP4ss!"
    
    # Random port for database
    db_port:
      template: "fake.port_number()"
      default: &db_port_default "3306"
  
  # Optional: Challenge categories/tags
  tags:
    - "web"
    - "sql-injection" 
    - "privilege-escalation"
    - "hard"

# Standard Docker Compose services using templated variables
services:
  # Web application service
  web:
    # Required fields
    image: "nginx:alpine"
    hostname: "web-server"
    
    # Optional networking
    networks:
      - "challenge-net"
    
    # Environment variables using templated values
    environment:
      DB_HOST: "database"
      DB_PORT: *db_port_default
      DB_PASSWORD: *db_pass_default
      FLAG_1: *db_flag_default
      FLAG_2: *admin_flag_default
    
    # Resource limits
    mem_limit: "256m"
    cpus: "0.5"
    
    # Security capabilities
    cap_add:
      - "NET_ADMIN"
  
  # Database service
  database:
    image: "mysql:8.0"
    hostname: "db-server"
    
    networks:
      - "challenge-net"
    
    environment:
      MYSQL_ROOT_PASSWORD: *db_pass_default
      MYSQL_DATABASE: "challenge_db"
      MYSQL_USER: "webapp"
      MYSQL_PASSWORD: "webapp123"
      # Flag hidden in database
      HIDDEN_FLAG: *db_flag_default
    
    # Resource constraints
    mem_limit: "512m"
    memswap_limit: "1g"
    cpus: "1.0"
  
  # Vulnerable application service  
  app:
    image: "vulnerable-webapp:latest"
    hostname: "app-server"
    
    # Command override
    command: 
      - "/start.sh"
      - "--debug"
    
    # Custom entrypoint
    entrypoint:
      - "/entrypoint.sh"
      - "webapp"
    
    networks:
      - "challenge-net"
    
    environment:
      APP_ENV: "production"
      SECRET_KEY: "dont_use_in_real_life" 
      ADMIN_FLAG: *admin_flag_default
      DB_CONNECTION: "mysql://webapp:webapp123@database:3306/challenge_db"
    
    # User context
    user: "webapp"

# Network definitions
networks:
  challenge-net:
    # Required: Internal-only network
    internal: true
```

## Data Types Reference

### ChallengeInfo
- **name**: `str` - Challenge title (required)
- **description**: `str` - Challenge description (required) 
- **questions**: `list[Question]` - List of questions/objectives (required)
- **icon**: `str | None` - Tabler icon name
- **hints**: `list[Hint] | None` - Available hints
- **summary**: `str | None` - Challenge overview
- **template**: `dict[str, str] | None` - Template definitions
- **variables**: `dict[str, Variable] | None` - Variable definitions with templates
- **tags**: `list[str] | None` - Challenge categories/tags

### Question
- **name**: `str` - Unique question identifier
- **question**: `str` - Question text displayed to participants
- **points**: `int` - Points awarded for correct answer
- **answer**: `str` - Regex pattern for valid answers
- **max_attempts**: `int` - Maximum submission attempts allowed

### Hint
- **hint**: `TextHint | str` - Hint content (text object or simple string)
- **preview**: `str` - Brief hint description shown before unlock
- **deduction**: `int` - Points deducted when hint is used

### TextHint
- **type**: `Literal['text']` - Hint type identifier
- **content**: `str` - Full hint text content

### Variable
- **template**: `Template` - Faker template for generating random values
- **default**: `str` - Default value with YAML anchor for referencing

### Service (Docker Compose)
- **image**: `str` - Container image (required)
- **hostname**: `str` - Container hostname (required)
- **command**: `str | list[str] | None` - Override container command
- **entrypoint**: `str | list[str] | None` - Override container entrypoint
- **environment**: `dict[str, Template | str] | list[str] | None` - Environment variables
- **networks**: `list[str] | dict[str, None] | None` - Network attachments
- **user**: `str | None` - User context for container
- **mem_limit**: `int | str | None` - Memory limit
- **cpus**: `float | str | None` - CPU allocation
- **cap_add**: `list[Literal['NET_ADMIN', 'SYS_PTRACE']] | None` - Linux capabilities

### Network
- **internal**: `Literal[True]` - Must be internal-only network (required)

## Template System

The template system uses [Python Faker](https://faker.readthedocs.io/) for generating randomized values:

```yaml
variables:
  random_flag:
    template: "fake.bothify('CTF{????-####}', letters='ABCDEF')"
    default: &flag_ref "CTF{ABCD-1234}"
  
  user_agent:
    template: "fake.user_agent()"
    default: &ua_ref "Mozilla/5.0 (compatible; Bot/1.0)"

services:
  web:
    environment:
      FLAG: *flag_ref
      USER_AGENT: *ua_ref
```

Common Faker methods:
- `fake.bothify('CTF{????-####}')` - Mixed letters and numbers
- `fake.password(length=12)` - Secure passwords
- `fake.port_number()` - Random port numbers
- `fake.ipv4()` - IP addresses
- `fake.user_agent()` - Browser user agents
- `fake.uuid4()` - UUID values