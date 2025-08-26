from rich.console import Console
from rich.panel import Panel
from rich.text import Text

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

def display_error(message: str):
    """Displays a generic error message."""
    console.print(Panel(message, title="[bold red]Error[/bold red]", border_style="red", expand=False))
