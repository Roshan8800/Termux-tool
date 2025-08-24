from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from termux_cyber_framework.core.domain.models import ExecutionResult

console = Console()

def display_welcome():
    """Displays a welcome banner."""
    welcome_message = Text("Termux Cyber Framework", style="bold green")
    creator_message = Text("Created by Roshan", style="italic cyan")
    disclaimer = Text(
        "This tool is for educational purposes only. "
        "Unauthorized use is strictly prohibited.",
        style="bold red"
    )

    panel_content = Text.assemble(
        welcome_message, "\n",
        creator_message, "\n\n",
        disclaimer
    )

    console.print(Panel(panel_content, title="[bold]Welcome[/bold]", expand=False, border_style="blue"))

def display_execution_result(result: ExecutionResult):
    """Displays the result of a command execution in a structured format."""
    if not result:
        display_error("Received an empty result object.")
        return

    # Determine panel style based on success or failure
    border_style = "green" if result.success else "red"
    title = "[bold green]Execution Successful[/bold green]" if result.success else "[bold red]Execution Failed[/bold red]"

    # Main content table
    table = Table(box=None, show_header=False, expand=True)
    table.add_column(style="bold cyan")
    table.add_column()

    table.add_row("Tool:", result.command.tool_name)
    table.add_row("Command:", result.command.raw_command)
    table.add_row("Success:", str(result.success))

    if result.consent_given is not None:
        table.add_row("Consent Given:", str(result.consent_given))

    # Panel for the main execution details
    console.print(Panel(table, title=title, border_style=border_style, expand=False))

    # Display output if available
    if result.output:
        console.print(Panel(result.output.strip(), title="[bold]Output[/bold]", border_style="blue", expand=True))

    # Display error details if the command failed
    if not result.success and result.error:
        error_panel_content = f"Message: {result.error.message}"
        if result.error.error_code is not None:
            error_panel_content += f"\nExit Code: {result.error.error_code}"
        if result.error.ai_analysis:
            error_panel_content += f"\n\n[bold]AI Analysis:[/bold]\n{result.error.ai_analysis}"

        console.print(Panel(error_panel_content, title="[bold red]Error Details[/bold red]", border_style="red", expand=False))

    # Display AI security advice if available
    if result.ai_advice:
        console.print(Panel(result.ai_advice, title="[bold green]Security Advisor[/bold green]", border_style="green", expand=False))

    # Display paths to report files
    if result.paths and (result.paths.report_files or result.output_log_file):
        path_info = ""
        if result.output_log_file:
            path_info += f"Output Log: {result.output_log_file}\n"
        if result.paths.report_files:
            for f in result.paths.report_files:
                 path_info += f"Report File: {f}\n"
        console.print(Panel(path_info.strip(), title="[bold]Artifacts[/bold]", border_style="yellow", expand=False))


def display_error(message: str):
    """Displays a generic error message."""
    console.print(Panel(message, title="[bold red]Error[/bold red]", border_style="red", expand=False))
