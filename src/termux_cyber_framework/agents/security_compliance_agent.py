import json
import os
from datetime import datetime
from termux_cyber_framework.core.domain.models import Command
from termux_cyber_framework.core.use_cases.ports import ConsentPort
from rich.console import Console
from rich.panel import Panel

class SecurityComplianceAgent(ConsentPort):
    """
    An agent responsible for ensuring user consent and security compliance.
    It checks for dangerous commands and obtains explicit user approval.
    """
    DANGEROUS_TOOLS = ["sqlmap", "nmap"]  # Example of tools that require explicit consent

    def __init__(self, log_file="reports/consent_log.json"):
        self.log_file = log_file
        self.console = Console()
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

    def get_consent(self, command: Command) -> bool:
        """
        Checks if a command is dangerous and prompts the user for consent if it is.
        """
        if command.tool_name in self.DANGEROUS_TOOLS:
            message = (
                f"[bold]AI Selected Tool:[/bold] {command.tool_name}\n"
                f"[bold]Full Command:[/bold] {' '.join([command.tool_name] + command.args)}"
            )
            panel = Panel(
                message,
                title="[bold yellow]Potentially Dangerous Command[/bold yellow]",
                subtitle="Please review and confirm to proceed.",
                border_style="yellow"
            )
            self.console.print(panel)
            response = self.console.input("[bold]Do you want to execute this command? (y/N):[/bold] ")
            consent_given = response.lower() == 'y'
        else:
            # For non-dangerous commands, we can assume consent is given.
            consent_given = True

        self._log_consent(command, consent_given)
        return consent_given

    def _log_consent(self, command: Command, consent_given: bool):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command.raw_command,
            "tool_used": command.tool_name,
            "ai_interpretation": command.ai_interpretation,
            "consent_given": consent_given,
        }

        log_data = []
        if os.path.exists(self.log_file):
            with open(self.log_file, "r") as f:
                try:
                    log_data = json.load(f)
                except json.JSONDecodeError:
                    log_data = []

        log_data.append(log_entry)

        with open(self.log_file, "w") as f:
            json.dump(log_data, f, indent=4)
