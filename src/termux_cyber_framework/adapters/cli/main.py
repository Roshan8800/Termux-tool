import asyncio
import typer
import os
import sys
from typing import Optional

from termux_cyber_framework.core.use_cases.orchestrator_agent import OrchestratorAgent
from termux_cyber_framework.core.command_runner import CommandRunner
from termux_cyber_framework.core.domain.config import Config
from termux_cyber_framework.agents.security_compliance_agent import SecurityComplianceAgent
from termux_cyber_framework.adapters.command_parser.ai_interpreter import AIInterpreter
from termux_cyber_framework.core.plugin_manager import PluginManager
from termux_cyber_framework.adapters.report_generator.txt_reporter import TxtReporter
from termux_cyber_framework.adapters.report_generator.json_reporter import JsonReporter
from termux_cyber_framework.adapters.persistence.execution_history import ExecutionHistory
from termux_cyber_framework.adapters.audit_logger.file_audit_logger import FileAuditLogger
from termux_cyber_framework.agents.logger_agent import LoggerAgent
from termux_cyber_framework.agents.error_analyst_agent import ErrorAnalystAgent
from termux_cyber_framework.agents.error_fixer_agent import ErrorFixerAgent
from termux_cyber_framework.agents.tool_installer_agent import ToolInstallerAgent
from termux_cyber_framework.agents.security_advisor_agent import SecurityAdvisorAgent
from termux_cyber_framework.agents.network_agent import NetworkAgent
from termux_cyber_framework.agents.doctor_agent import DoctorAgent
from termux_cyber_framework.agents.config_manager_agent import ConfigManagerAgent
from termux_cyber_framework.agents.update_agent import UpdateAgent
from termux_cyber_framework.agents.file_manager_agent import FileManagerAgent
from termux_cyber_framework.agents.dependency_auditor_agent import DependencyAuditorAgent
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
    consent_service: Optional[SecurityComplianceAgent] = None,
    execution_history: Optional[ExecutionHistory] = None,
    parser: Optional[CommandParserPort] = None
) -> OrchestratorAgent:
    """
    Composition Root: Constructs and wires all agents and components.
    """
    # --- Foundational Agents & Adapters ---
    config = config or Config()
    command_runner = command_runner or CommandRunner()
    consent_service = consent_service or SecurityComplianceAgent()
    execution_history = execution_history or ExecutionHistory()
    logger = LoggerAgent()
    file_manager = FileManagerAgent(logger=logger)
    audit_logger = FileAuditLogger(file_manager=file_manager)

    # Correctly locate the project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    tool_catalog_path = os.path.join(project_root, "data", "tool_catalog.json")
    config_path = os.path.join(project_root, "config", "config.json")

    # --- Agent Construction ---
    config_manager = ConfigManagerAgent(file_manager=file_manager, config_path=config_path)
    api_key = config_manager.get_api_key("google_gemini") or os.getenv("GOOGLE_API_KEY")

    command_parser = parser or AIInterpreter(tool_catalog_path=tool_catalog_path)
    install_logger = InstallLogger()
    installers = {
        "git": GitInstallerAdapter(command_runner, install_logger),
        "pip": PipInstallerAdapter(command_runner, install_logger),
        "pkg": PkgInstallerAdapter(command_runner, install_logger)
    }
    plugin_manager = PluginManager(config=config, command_runner=command_runner, logger=logger, installers=installers)
    tool_adapters = plugin_manager.load_plugins()

    report_generators = [
        TxtReporter(file_manager=file_manager),
        JsonReporter(file_manager=file_manager)
    ]

    error_analyst = ErrorAnalystAgent(api_key=api_key)
    error_fixer = ErrorFixerAgent(api_key=api_key)
    security_advisor = SecurityAdvisorAgent(api_key=api_key)
    network_agent = NetworkAgent(logger=logger)
    tool_installer = ToolInstallerAgent(installers=installers, logger=logger, config=config)
    update_agent = UpdateAgent(logger=logger, audit_logger=audit_logger)

    return OrchestratorAgent(
        parser=command_parser,
        tool_adapters=tool_adapters,
        report_generators=report_generators,
        error_analyst=error_analyst,
        error_fixer=error_fixer,
        tool_installer=tool_installer,
        security_advisor=security_advisor,
        network_agent=network_agent,
        update_agent=update_agent,
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

def run_health_checks():
    """Initializes and runs the DoctorAgent to perform system health checks."""
    logger = LoggerAgent()
    file_manager = FileManagerAgent(logger=logger)

    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
        config_paths = [
            os.path.join(project_root, "config", "config.json"),
            os.path.join(project_root, "data", "tool_catalog.json")
        ]
        tool_catalog_path = os.path.join(project_root, "data", "tool_catalog.json")
        config_path = os.path.join(project_root, "config", "config.json")

        config_manager = ConfigManagerAgent(file_manager=file_manager, config_path=config_path)
        doctor = DoctorAgent(
            logger=logger,
            config_manager=config_manager,
            file_manager=file_manager,
            config_paths=config_paths,
            tool_catalog_path=tool_catalog_path
        )
        doctor.run_checks()
    except (FileNotFoundError, ValueError) as e:
        error_panel = Panel(
            f"[bold]A critical error occurred during system health checks:[/bold]\n\n[red]{e}[/red]\n\nPlease resolve the issue and try again.",
            title="[bold red]System Health Check Failed[/bold red]",
            border_style="red",
            expand=False
        )
        console.print(error_panel)
        raise typer.Exit(code=1)


@app.command()
def audit():
    """
    Runs a dependency audit to check for potential conflicts.
    """
    logger = LoggerAgent()
    agent = DependencyAuditorAgent(logger=logger)
    findings = agent.run_audit()

    if not findings:
        console.print("[bold green]Dependency audit complete. No issues found.[/bold green]")
        return

    console.print("\n[bold yellow]Dependency audit found the following potential issues:[/bold yellow]")
    for finding in findings:
        color = "yellow" if finding.get("level") == "WARNING" else "red"
        panel = Panel(
            f"{finding.get('message')}",
            title=f"[bold {color}]{finding.get('level')}[/bold {color}]",
            border_style=color,
            expand=False
        )
        console.print(panel)


@app.command()
def set_key(
    service: str = typer.Argument(..., help="The name of the service (e.g., 'google_gemini', 'open_router')."),
    key: str = typer.Argument(..., help="The API key value.")
):
    """
    Sets and saves an API key for a given service in the config file.
    """
    from termux_cyber_framework.agents.config_manager_agent import ConfigManagerAgent

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    config_path = os.path.join(project_root, "config", "config.json")

    logger = LoggerAgent()
    file_manager = FileManagerAgent(logger=logger)
    agent = ConfigManagerAgent(file_manager=file_manager, config_path=config_path)
    agent.set_api_key(service, key)

    console.print(f"[bold green]API key for '{service}' has been set successfully.[/bold green]")


@app.command()
def update():
    """
    Checks for and applies updates to the framework and its tools.
    """
    orchestrator = build_agent_system()

    async def main():
        result_message = await orchestrator.update_system()
        console.print(f"[bold yellow]{result_message}[/bold yellow]")

    asyncio.run(main())


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
        result = await orchestrator.execute(command)
        if result and result.ai_advice:
            console.print(Panel(result.ai_advice, title="[bold blue]Security Advisor[/bold blue]", border_style="blue", expand=False))

    asyncio.run(main())

@app.command()
def shell():
    """
    Starts an interactive shell session to run multiple commands.
    """
    console.print("[bold green]Starting interactive shell...[/bold green]")
    console.print("Type ':help' for a list of commands, or ':exit' to quit.")

    orchestrator = build_agent_system()

    while True:
        try:
            command_str = console.input("[bold cyan]cyber-ai>[/bold cyan] ")

            if not command_str.strip():
                continue

            if command_str.lower() == ':exit':
                console.print("[bold yellow]Exiting shell.[/bold yellow]")
                break

            if command_str.lower() == ':help':
                console.print("\n[bold]Available Meta-Commands:[/bold]")
                console.print("  :help   - Show this help message")
                console.print("  :exit   - Exit the interactive shell\n")
                continue

            async def main():
                result = await orchestrator.execute(command_str)
                if result and result.ai_advice:
                    console.print(Panel(result.ai_advice, title="[bold blue]Security Advisor[/bold blue]", border_style="blue", expand=False))

            asyncio.run(main())

        except KeyboardInterrupt:
            console.print("\n[bold yellow]Use ':exit' to quit.[/bold yellow]")
        except Exception as e:
            console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")


if __name__ == "__main__":
    display_welcome()
    run_health_checks()
    app()
