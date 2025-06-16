"""
Command Line Interface for CTF Challenge Parser

This module provides a CLI tool for parsing and validating Docker Compose files
with CTF challenge extensions using Typer.
"""

import sys
import logging
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
import typer
from cattrs import ClassValidationError

from .yaml_parser import parse_compose_file, parse_compose_string
from .compose import ComposeFile
from .challenge_info import ChallengeInfo

app = typer.Typer(
    name="chall-parser",
    add_completion=False
)

console = Console()

def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stderr)]
    )

def format_validation_error(error: Exception) -> str:
    """Format validation errors in a user-friendly way."""
    if isinstance(error, ClassValidationError):
        errors = []
        for exc in error.exceptions:
            if hasattr(exc, '__notes__'):
                for note in exc.__notes__:
                    errors.append(f"  • {note}")
            else:
                errors.append(f"  • {str(exc)}")
        return "Validation errors:\n" + "\n".join(errors)
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
        
        for question in challenge.questions:
            questions_table.add_row(
                question.name,
                str(question.points),
                str(question.max_attempts),
                question.question
            )
        
        console.print(questions_table)
        console.print()
    
    # Display hints
    if challenge.hints:
        hints_table = Table(title="Hints", show_header=True)
        hints_table.add_column("Preview", style="bold blue")
        hints_table.add_column("Deduction", justify="right", style="red")
        hints_table.add_column("Type", style="cyan")
        
        for hint in challenge.hints:
            hint_type = "text" if hasattr(hint.hint, 'type') else "string"
            hints_table.add_row(
                hint.preview,
                str(hint.deduction),
                hint_type
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

@app.command()
def validate(
    file_path: Path = typer.Argument(..., help="Path to the challenge compose file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    show_summary: bool = typer.Option(True, "--summary/--no-summary", help="Show challenge summary"),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table, json, yaml")
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
                import json
                from .yaml_parser import ComposeYamlParser
                parser = ComposeYamlParser()
                data = parser.converter.unstructure(compose)
                console.print(Syntax(json.dumps(data, indent=2), "json"))
            elif output_format == "yaml":
                from .yaml_parser import ComposeYamlParser
                parser = ComposeYamlParser()
                yaml_output = parser.to_yaml(compose)
                console.print(Syntax(yaml_output, "yaml"))
        
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
    file_path: Optional[Path] = typer.Argument(None, help="Path to the challenge compose file"),
    stdin: bool = typer.Option(False, "--stdin", help="Read from stdin instead of file")
):
    """
    Quick validation check (exit code only).
    
    Performs validation and returns appropriate exit codes:
    - 0: Valid
    - 1: Invalid/Error
    """
    try:
        if stdin:
            import sys
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

@app.command()
def info(
    file_path: Path = typer.Argument(..., help="Path to the challenge compose file"),
    field: Optional[str] = typer.Option(None, "--field", help="Show specific field (name, description, questions, etc.)")
):
    """
    Show information about a challenge.
    
    Display detailed information about the challenge configuration.
    Use --field to show only a specific field.
    """
    try:
        compose = parse_compose_file(file_path)
        challenge = compose.challenge
        
        if field:
            if hasattr(challenge, field):
                value = getattr(challenge, field)
                if value is not None:
                    if isinstance(value, (list, dict)):
                        import json
                        console.print(json.dumps(value, indent=2, default=str))
                    else:
                        console.print(str(value))
                else:
                    console.print(f"[yellow]Field '{field}' is not set[/yellow]")
            else:
                console.print(f"[red]Unknown field: {field}[/red]")
                available_fields = [attr for attr in dir(challenge) if not attr.startswith('_')]
                console.print(f"Available fields: {', '.join(available_fields)}")
                raise typer.Exit(1)
        else:
            display_challenge_summary(challenge)
        
    except Exception as e:
        console.print(f"[red]Error: {format_validation_error(e)}[/red]")
        raise typer.Exit(1)

@app.command()
def template_test(
    file_path: Path = typer.Argument(..., help="Path to the challenge compose file"),
    variable: Optional[str] = typer.Option(None, "--variable", "-var", help="Test specific variable template"),
    count: int = typer.Option(5, "--count", "-c", help="Number of template evaluations to show")
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
    version: bool = typer.Option(False, "--version", help="Show version and exit")
):
    """
    CTF Challenge Parser - Validate and parse Docker Compose files with CTF extensions.
    
    This tool helps validate challenge configurations, ensuring proper format
    """
    if version:
        console.print("chall-parser version 0.1.0")
        raise typer.Exit(0)

if __name__ == "__main__":
    app()
