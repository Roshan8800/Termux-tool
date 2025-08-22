import asyncio
import typer
import os
from typing import Optional
from termux_cyber_framework.core.use_cases.orchestrator_agent import OrchestratorAgent
from termux_cyber_framework.core.command_runner import CommandRunner
from termux_cyber_framework.core.domain.config import Config
from termux_cyber_framework.core.use_cases.consent.consent_service import ConsentService
from termux_cyber_framework.adapters.command_parser.ai_interpreter import AIInterpreter
from termux_cyber_framework.core.plugin_manager import PluginManager
from termux_cyber_framework.adapters.report_generator.txt_reporter import TxtReporter
from termux_cyber_framework.adapters.report_generator.json_reporter import JsonReporter
from termux_cyber_framework.adapters.persistence.execution_history import ExecutionHistory
from termux_cyber_framework.adapters.audit_logger.file_audit_logger import FileAuditLogger
from termux_cyber_framework.agents.logger_agent import LoggerAgent
from termux_cyber_framework.agents.error_analyst_agent import ErrorAnalystAgent
from termux_cyber_framework.adapters.tool_installer.git_installer import GitInstallerAdapter
from termux_cyber_framework.adapters.tool_installer.pip_installer import PipInstallerAdapter
from termux_cyber_framework.adapters.tool_installer.pkg_installer import PkgInstallerAdapter
from termux_cyber_framework.adapters.logger.install_logger import InstallLogger
from rich.console import Console
from rich.panel import Panel

console = Console()

app = typer.Typer(add_completion=False)

from termux_cyber_framework.core.use_cases.ports import CommandParserPort

def build_agent_system(
    command_runner: Optional[CommandRunner] = None,
    config: Optional[Config] = None,
    consent_service: Optional[ConsentService] = None,
    execution_history: Optional[ExecutionHistory] = None,
    parser: Optional[CommandParserPort] = None
) -> OrchestratorAgent:
    """
    Composition Root: Constructs and wires all agents and components.
    """
    # --- Adapters Initialization ---

    config = config or Config()
    command_runner = command_runner or CommandRunner()
    consent_service = consent_service or ConsentService()
    execution_history = execution_history or ExecutionHistory()
    logger = LoggerAgent()

    # Correctly locate the project root to find the data directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    tool_catalog_path = os.path.join(project_root, "data", "tool_catalog.json")
    doctor_rules_path = os.path.join(project_root, "src", "termux_cyber_framework", "config", "doctor_rules.json")

    # Ports -> Adapters
    command_parser = parser or AIInterpreter(tool_catalog_path=tool_catalog_path)

    # Create installer strategies
    install_logger = InstallLogger()
    installers = {
        "git": GitInstallerAdapter(command_runner, install_logger),
        "pip": PipInstallerAdapter(command_runner, install_logger),
        "pkg": PkgInstallerAdapter(command_runner, install_logger)
    }

    plugin_manager = PluginManager(config=config, command_runner=command_runner, logger=logger, installers=installers)
    tool_adapters = plugin_manager.load_plugins()

    report_generators = [TxtReporter(), JsonReporter()]
    audit_logger = FileAuditLogger()

    # --- Agent Construction ---
    # TODO: The API key should not be hardcoded.
    error_analyst = ErrorAnalystAgent(api_key="AIzaSyB8B_5EXGahUCGiII5xAhqmX0YroSmvVek")

    return OrchestratorAgent(
        parser=command_parser,
        tool_adapters=tool_adapters,
        report_generators=report_generators,
        error_analyst=error_analyst,
        logger=logger,
        config=config,
        audit_logger=audit_logger,
        consent_service=consent_service,
        execution_history=execution_history
    )

def display_welcome():
    """Displays the welcome message, logo, and disclaimer."""
    os.system('cls' if os.name == 'nt' else 'clear')

    logo = r"""
[bold blue]
  _____           _
 |  __ \         | |
 | |__) |___  ___| |_ _ __ ___  _ __
 |  _  // _ \/ __| __| '__/ _ \| '_ \
 | | \ \  __/\__ \ |_| | | (_) | | | |
 |_|  \_\___||___/\__|_|  \___/|_| |_|
[/bold blue]
    """

    console.print(logo)
    console.print("[bold]Welcome to the Termux Cyber Framework[/bold]")
    console.print("Created by [bold green]Roshan[/bold green]\n")

    disclaimer = """
    This tool is for educational purposes only. Do not use it to cause harm.
    I am not responsible for any misuse; responsibility rests with the user.
    """

    console.print(Panel(disclaimer, title="[bold yellow]Disclaimer[/bold yellow]", border_style="yellow"))
    console.print("")

@app.command()
def run(
    command: str = typer.Argument(..., help="The command to run in natural language."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Perform a dry run without executing any commands.")
):
    """
    Runs a command by parsing it, ensuring the tool is installed,
    and executing it using the best available runner.
    """
    config = Config(dry_run=dry_run)
    orchestrator = build_agent_system(config=config)

    async def main():
        await orchestrator.execute(command)

    asyncio.run(main())

if __name__ == "__main__":
    display_welcome()
    app()
