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
Command Line Interface for CTF Challenge Parser

This module provides a CLI tool for parsing and validating Docker Compose files
with CTF challenge extensions using Typer.
"""

from enum import Enum
import sys
import logging
from pathlib import Path
from typing import Annotated, Optional
import attr
from cyber_skyline.chall_parser.compose.answer import Answer
from cyber_skyline.chall_parser.compose.challenge_info import TextBody
from cyber_skyline.chall_parser.rewriter import Template
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
import typer
from cattrs import ClassValidationError, transform_error
from cattrs.v import format_exception
import yaml
import json
from importlib.metadata import version as get_version
from cyber_skyline.chall_parser.yaml_parser import parse_compose_file, parse_compose_string, ComposeYamlParser
from cyber_skyline.chall_parser.compose import ComposeFile, ChallengeInfo

from chall_check.md import compose_to_markdown

app = typer.Typer(
    name="chall-check",
    add_completion=True
)

console = Console()

def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.CRITICAL
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stderr)]
    )

def format_parse_exceptions(error: BaseException, type: type | None) -> str:
    """Format parse exceptions for better readability."""
    if isinstance(error, KeyError):
        return f"Required field {str(error)} missing"
    elif isinstance(error, ValueError):
        return f"Value error: {str(error)}"
    elif isinstance(error, FileNotFoundError):
        return f"File not found: {str(error)}"
    elif isinstance(error, yaml.YAMLError):
        return f"YAML error: {str(error)}"
    return format_exception(error, type)
        

def format_validation_error(error: Exception) -> str:
    """Format validation errors in a user-friendly way using cattrs transform_error."""
    
    # Handle cattrs validation errors (ExceptionGroups) using transform_error
    if isinstance(error, (ExceptionGroup, ClassValidationError, Exception)):
        try:
            # Use cattrs' transform_error for proper ExceptionGroup handling
            error_messages = transform_error(error, format_exception=format_parse_exceptions)
            if error_messages:
                formatted_errors = []
                for msg in error_messages:
                    # Clean up the error message formatting
                    if msg.startswith("invalid value for type"):
                        formatted_errors.append(f"  • {msg}")
                    elif " @ " in msg:
                        # Split location from message for better formatting
                        parts = msg.split(" @ ", 1)
                        if len(parts) == 2:
                            formatted_errors.append(f"  • {parts[0]} (at {parts[1]})")
                        else:
                            formatted_errors.append(f"  • {msg}")
                    else:
                        formatted_errors.append(f"  • {msg}")
                
                return "Validation errors:\n" + "\n".join(formatted_errors)
        except Exception:
            # Fallback to original handling if transform_error fails
            pass
    
    # Fallback for ClassValidationError with __notes__ (PEP 678)
    if isinstance(error, ClassValidationError):
        errors = []
        
        # Handle the main exception
        if hasattr(error, '__notes__') and error.__notes__:
            for note in error.__notes__:
                errors.append(f"  • {note}")
        
        # Handle nested exceptions in the group
        if hasattr(error, 'exceptions'):
            for exc in error.exceptions:
                if hasattr(exc, '__notes__') and exc.__notes__:
                    for note in exc.__notes__:
                        errors.append(f"  • {note}")
                elif hasattr(exc, 'exceptions'):
                    # Handle nested ExceptionGroups recursively
                    for nested_exc in exc.exceptions: # type: ignore
                        if hasattr(nested_exc, '__notes__') and nested_exc.__notes__:
                            for note in nested_exc.__notes__:
                                errors.append(f"  • {note}")
                        else:
                            errors.append(f"  • {str(nested_exc)}")
                else:
                    errors.append(f"  • {str(exc)}")
        
        if errors:
            return "Validation errors:\n" + "\n".join(errors)
        else:
            return f"Validation error: {str(error)}"
    
    # Handle other common exceptions
    elif isinstance(error, ValueError):
        return f"Value error: {str(error)}"
    elif isinstance(error, FileNotFoundError):
        return f"File not found: {str(error)}"
    else:
        return f"Error: {str(error)}"

def display_challenge_summary(challenge: ChallengeInfo):
    """Display a formatted summary of the challenge information."""
    # Create challenge info table
    challenge_table = Table(title="Challenge Information", show_header=False)
    challenge_table.add_column("Field", style="bold cyan")
    challenge_table.add_column("Value", style="white")
    
    challenge_table.add_row("Name", challenge.name)
    challenge_table.add_row("Description", challenge.description)
    
    if challenge.icon:
        challenge_table.add_row("Icon", challenge.icon)
    
    if challenge.summary:
        challenge_table.add_row("Summary", challenge.summary)
    
    if challenge.tags:
        challenge_table.add_row("Tags", ", ".join(challenge.tags))
    
    console.print(challenge_table)
    console.print()
    
    # Display questions
    if challenge.questions:
        questions_table = Table(title="Questions", show_header=True)
        questions_table.add_column("Name", style="bold green")
        questions_table.add_column("Points", justify="right", style="yellow")
        questions_table.add_column("Max Attempts", justify="right", style="red")
        questions_table.add_column("Question", style="white")
        questions_table.add_column("Answer", style="blue")
        questions_table.add_column("Test Cases", style="magenta")
        
        for question in challenge.questions:
            test_cases = [""]
            answer = question.answer
            if isinstance(answer, Answer):
                if answer.test_cases:
                    test_cases = [f'{ ":white_heavy_check_mark:" if test_case.correct else ":cross_mark:" } {test_case.answer}' for test_case in answer.test_cases]
                answer = answer.body
            elif isinstance(answer, Template):
                answer = answer.eval_str
            
            test_cases = iter(test_cases)
            questions_table.add_row(
                question.name,
                str(question.points),
                str(question.max_attempts),
                question.body,
                answer,
                next(test_cases)
            )

            for test_case in test_cases:
                questions_table.add_row(
                    "",
                    "",
                    "",
                    "",
                    "",
                    test_case
                )

        console.print(questions_table)
        console.print()
    
    # Display hints
    if challenge.hints:
        hints_table = Table(title="Hints", show_header=True)
        hints_table.add_column("Preview", style="bold blue")
        hints_table.add_column("Deduction", justify="right", style="red")
        hints_table.add_column("Type", style="cyan")
        hints_table.add_column("Hint", style="white")
        
        for hint in challenge.hints:
            hint_type = "text" if isinstance(hint.body, TextBody) else "string"
            hints_table.add_row(
                hint.preview,
                str(hint.deduction),
                hint_type,
                hint.body.content if isinstance(hint.body, TextBody) else hint.body
            )
        
        console.print(hints_table)
        console.print()
    
    # Display variables
    if challenge.variables:
        variables_table = Table(title="Template Variables", show_header=True)
        variables_table.add_column("Name", style="bold magenta")
        variables_table.add_column("Template", style="cyan")
        variables_table.add_column("Default", style="white")
        
        for var_name, variable in challenge.variables.items():
            variables_table.add_row(
                var_name,
                variable.template.eval_str,
                variable.default
            )
        
        console.print(variables_table)

def display_services_summary(compose: ComposeFile):
    """Display a formatted summary of the services."""
    if not compose.services:
        console.print("[yellow]No services defined[/yellow]")
        return
    
    services_table = Table(title="Services", show_header=True)
    services_table.add_column("Name", style="bold green")
    services_table.add_column("Image", style="cyan")
    services_table.add_column("Hostname", style="white")
    services_table.add_column("Networks", style="blue")
    services_table.add_column("Resources", style="yellow")
    
    for service_name, service in compose.services.items():
        networks = ""
        if service.networks:
            if isinstance(service.networks, list):
                networks = ", ".join(service.networks)
            elif isinstance(service.networks, dict):
                networks = ", ".join(service.networks.keys())
        
        resources = []
        if service.mem_limit:
            resources.append(f"mem: {service.mem_limit}")
        if service.cpus:
            resources.append(f"cpu: {service.cpus}")
        resource_str = ", ".join(resources) if resources else "default"
        
        services_table.add_row(
            service_name,
            service.image,
            service.hostname,
            networks,
            resource_str
        )
    
    console.print(services_table)

class OutputFormat(str, Enum):
    TABLE = "table"
    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "md"

@app.command()
def validate(
    file_path: Annotated[Path, typer.Argument(help="Path to the challenge compose file")],
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose logging")] = False,
    show_summary: Annotated[bool, typer.Option("--summary/--no-summary", help="Show challenge summary")] = True,
    output_format: Annotated[OutputFormat, typer.Option("--format", "-f", help="Output format")] = OutputFormat.TABLE
):
    """
    Validate a CTF challenge Docker Compose file.
    
    This command parses and validates a challenge compose file, checking for:
    - Required fields in challenge configuration
    - Valid template syntax
    - Service configuration compliance
    - Network security requirements
    """
    setup_logging(verbose)
    
    try:
        # Parse the compose file
        with console.status("[bold green]Parsing compose file..."):
            compose = parse_compose_file(file_path)
        
        console.print(f"[bold green]✓[/bold green] Successfully validated: {file_path}")
        console.print()
        
        if show_summary:
            if output_format == "table":
                display_challenge_summary(compose.challenge)
                display_services_summary(compose)
            elif output_format == "json":
                parser = ComposeYamlParser()
                data = parser.converter.unstructure(compose)
                console.print(Syntax(json.dumps(data, indent=2), "json"))
            elif output_format == "yaml":
                parser = ComposeYamlParser()
                yaml_output = parser.to_yaml(compose)
                console.print(Syntax(yaml_output, "yaml"))
            elif output_format == "md":
                # Convert to Markdown format
                md_output = compose_to_markdown(compose)
                console.print(Syntax(md_output, "markdown"))
        
        typer.Exit(0)
        
    except Exception as e:
        error_msg = format_validation_error(e)
        
        # Create error panel
        error_panel = Panel(
            error_msg,
            title="[bold red]Validation Failed[/bold red]",
            border_style="red",
            expand=False
        )
        console.print(error_panel)
        
        if verbose:
            import traceback
            console.print("\n[bold red]Full traceback:[/bold red]")
            console.print(traceback.format_exc())
        
        raise typer.Exit(1)

@app.command()
def check(
    file_path: Annotated[Optional[Path], typer.Argument(help="Path to the challenge compose file")],
    stdin: Annotated[bool, typer.Option(help="Read from stdin instead of file")] = False
):
    """
    Quick validation check (exit code only).
    
    Performs validation and returns appropriate exit codes:
    - 0: Valid
    - 1: Invalid/Error
    """
    try:
        if stdin:
            yaml_content = sys.stdin.read()
            parse_compose_string(yaml_content)
        elif file_path:
            parse_compose_file(file_path)
        else:
            console.print("[red]Error: Must provide either file path or --stdin[/red]")
            raise typer.Exit(1)
        
        # Silent success
        raise typer.Exit(0)
    except typer.Exit:
        raise
    except Exception:
        raise typer.Exit(1)

class ChallengeField(Enum):
    """Enum for challenge fields to display."""
    _ignore_ = "ChallengeField field" 
    ChallengeField = vars()
    for field in attr.fields_dict(ChallengeInfo).keys():
        ChallengeField[field] = field

@app.command()
def info(
    file_path: Annotated[Path, typer.Argument(help="Path to the challenge compose file", show_default=False)],
    field: Annotated[Optional[ChallengeField], typer.Option(help="Show specific field (name, description, questions, etc.)")] = None
):
    """
    Show information about a challenge.
    
    Display detailed information about the challenge configuration.
    """
    try:
        compose = parse_compose_file(file_path)
        challenge = compose.challenge
        
        if field:
            if hasattr(challenge, field.value):
                value = getattr(challenge, field.value)
                if value is not None:
                    if isinstance(value, (list, dict)):
                        console.print(json.dumps(value, indent=2, default=str))
                    else:
                        console.print(str(value))
                else:
                    console.print(f"[yellow]Field '{field.value}' is not set[/yellow]")
            else:
                console.print(f"[red]Unknown field: {field.value}[/red]")
                available_fields = [attr.value for attr in ChallengeField]
                console.print(f"Available fields: {', '.join(available_fields)}")
                raise typer.Exit(1)
        else:
            display_challenge_summary(challenge)
        
    except Exception as e:
        console.print(f"[red]Error: {format_validation_error(e)}[/red]")
        raise typer.Exit(1)

@app.command()
def render(
    file_path: Annotated[Path, typer.Argument(help="Path to the challenge compose file")],
    variable: Annotated[Optional[str], typer.Option("--variable", "-var", help="Test specific variable template")] = None,
    count: Annotated[int, typer.Option("--count", "-c", help="Number of template evaluations to show")] = 5
):
    """
    Test template variable generation.
    
    Evaluate template variables to see what values they generate.
    Useful for testing Faker templates before deployment.
    """
    try:
        compose = parse_compose_file(file_path)
        
        if not compose.challenge.variables:
            console.print("[yellow]No template variables defined[/yellow]")
            raise typer.Exit(0)
        
        variables_to_test = {}
        if variable:
            if variable in compose.challenge.variables:
                variables_to_test[variable] = compose.challenge.variables[variable]
            else:
                console.print(f"[red]Variable '{variable}' not found[/red]")
                available = list(compose.challenge.variables.keys())
                console.print(f"Available variables: {', '.join(available)}")
                raise typer.Exit(1)
        else:
            variables_to_test = compose.challenge.variables
        
        for var_name, var_obj in variables_to_test.items():
            console.print(f"\n[bold cyan]{var_name}[/bold cyan]")
            console.print(f"Template: [yellow]{var_obj.template.eval_str}[/yellow]")
            console.print(f"Default:  [white]{var_obj.default}[/white]")
            console.print("Generated values:")
            
            for i in range(count):
                try:
                    value = var_obj.template.eval()
                    console.print(f"  {i+1}. {value}")
                except Exception as e:
                    console.print(f"  {i+1}. [red]Error: {e}[/red]")
        
    except Exception as e:
        console.print(f"[red]Error: {format_validation_error(e)}[/red]")
        raise typer.Exit(1)

@app.callback(invoke_without_command=True)
def main(
    version: Annotated[bool, typer.Option(help="Show version and exit")] = False
):
    """
    CTF Challenge Parser - Validate and parse Docker Compose files with CTF extensions.
    
    This tool helps validate challenge configurations, ensuring proper format
    """
    if version:
        version_str = get_version('cyber-skyline-chall-check')
        console.print(f"chall-check version {version_str}")
        raise typer.Exit(0)

if __name__ == "__main__":
    app()
