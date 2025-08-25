import asyncio
import typer
import os
import sys
import json
from typing import Optional, Dict, Any

from termux_cyber_framework.core.use_cases.orchestrator_agent import OrchestratorAgent
from termux_cyber_framework.core.command_runner import CommandRunner
from termux_cyber_framework.core.domain.config import Config
from termux_cyber_framework.agents.security_compliance_agent import SecurityComplianceAgent
from termux_cyber_framework.adapters.command_parser.ai_interpreter import AIInterpreter
from termux_cyber_framework.adapters.command_parser.master_ai_interpreter import MasterAIInterpreter
from termux_cyber_framework.core.plugin_manager import PluginManager
from termux_cyber_framework.adapters.report_generator.txt_reporter import TxtReporter
from termux_cyber_framework.adapters.report_generator.json_reporter import JsonReporter
from termux_cyber_framework.adapters.report_generator.markdown_reporter import MarkdownReporter
from termux_cyber_framework.adapters.report_generator.pdf_reporter import PdfReporter
from termux_cyber_framework.adapters.persistence.execution_history import ExecutionHistory
from termux_cyber_framework.adapters.audit_logger.file_audit_logger import FileAuditLogger
from termux_cyber_framework.agents.logger_agent import LoggerAgent
from termux_cyber_framework.agents.error_analyst_agent import ErrorAnalystAgent
from termux_cyber_framework.agents.error_fixer_agent import ErrorFixerAgent
from termux_cyber_framework.agents.tool_installer_agent import ToolInstallerAgent
from termux_cyber_framework.agents.security_advisor_agent import SecurityAdvisorAgent
from termux_cyber_framework.agents.network_agent import NetworkAgent
from termux_cyber_framework.agents.config_manager_agent import ConfigManagerAgent
from termux_cyber_framework.agents.update_agent import UpdateAgent
from termux_cyber_framework.agents.file_manager_agent import FileManagerAgent
from termux_cyber_framework.agents.dependency_auditor_agent import DependencyAuditorAgent
from termux_cyber_framework.agents.knowledge_agent import KnowledgeAgent
from termux_cyber_framework.agents.system_resource_agent import SystemResourceAgent
from termux_cyber_framework.agents.pentestgpt_agent import PentestGptAgent
from termux_cyber_framework.agents.doctor_agent import DoctorAgent
from termux_cyber_framework.adapters.ollama_adapter import OllamaAdapter
from termux_cyber_framework.adapters.tool_installer.git_installer import GitInstallerAdapter
from termux_cyber_framework.adapters.tool_installer.pip_installer import PipInstallerAdapter
from termux_cyber_framework.adapters.tool_installer.pkg_installer import PkgInstallerAdapter
from termux_cyber_framework.adapters.tool_installer.shell_installer import ShellInstallerAdapter
from termux_cyber_framework.adapters.logger.install_logger import InstallLogger
from termux_cyber_framework.adapters.cli.view import display_welcome, display_execution_result, display_error
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
app = typer.Typer(add_completion=False, help="A modular, AI-driven cybersecurity framework.")

# Global holder for the lazily-initialized agent system
_agent_system = None

def get_agent_system() -> Dict[str, Any]:
    """Lazily builds and returns the entire agent system."""
    global _agent_system
    if _agent_system is None:
        _agent_system = build_agent_system()
    return _agent_system

def handle_one_time_welcome():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    config_dir = os.path.join(project_root, "config")
    state_file = os.path.join(config_dir, ".first_run_complete")
    if not os.path.exists(state_file):
        display_welcome()
        if not os.path.exists(config_dir): os.makedirs(config_dir)
        with open(state_file, 'w') as f: f.write("done")

@app.command()
def run(command: str = typer.Argument(..., help="The command to run in natural language."), dry_run: bool = typer.Option(False, "--dry-run")):
    orchestrator = get_agent_system()["orchestrator"]
    orchestrator.config.dry_run = dry_run
    try:
        result = asyncio.run(orchestrator.handle_input(command))
        if hasattr(result, 'success'): display_execution_result(result)
        else: console.print(Panel(str(result), title="[bold green]Response[/bold green]", expand=False))
    except Exception as e:
        display_error(f"An unexpected error occurred in the CLI: {e}")

@app.command()
def shell():
    handle_one_time_welcome()
    orchestrator = get_agent_system()["orchestrator"]
    while True:
        try:
            command_str = console.input("[bold cyan]cyber-ai>[/bold cyan] ")
            if command_str.lower() in [":exit", "exit"]: break
            if command_str.lower() in [":help", "help"]:
                console.print("This shell accepts natural language commands. Try 'scan example.com', 'start pentest session' or 'what is SQL injection?'. Type ':exit' to quit.")
                continue
            if not command_str.strip(): continue
            result = asyncio.run(orchestrator.handle_input(command_str))
            if hasattr(result, 'success'): display_execution_result(result)
            else: console.print(Panel(str(result), title="[bold green]Response[/bold green]", expand=False))
        except KeyboardInterrupt:
            console.print("\nExiting shell.")
            break
        except Exception as e:
            display_error(f"An error occurred in the shell: {e}")

@app.command()
def doctor():
    """Runs a series of health checks to diagnose the framework's status."""
    console.print(Panel("Running System Health Checks", style="bold blue"))
    agent_system = get_agent_system()
    doctor_agent = agent_system["doctor_agent"]

    with console.status("[bold yellow]Performing checks...[/]"):
        results = asyncio.run(doctor_agent.run_health_checks())

    table = Table(title="System Health Report")
    table.add_column("Check", justify="left", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center", style="bold")
    table.add_column("Message", justify="left")

    for check in results:
        status_style = "green"
        if check['status'] == "WARN": status_style = "yellow"
        if check['status'] == "ERROR": status_style = "bold red"
        table.add_row(check['check'], f"[{status_style}]{check['status']}[/]", check['message'])

    console.print(table)

def main():
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] not in [cmd.name for cmd in app.registered_commands]):
        shell()
    else:
        app()

if __name__ == "__main__":
    main()

def build_agent_system(config: Optional[Config] = None) -> Dict[str, Any]:
    config = config or Config()
    logger = LoggerAgent()
    file_manager = FileManagerAgent(logger=logger)
    command_runner = CommandRunner()
    consent_service = SecurityComplianceAgent()
    execution_history = ExecutionHistory()
    audit_logger = FileAuditLogger(file_manager=file_manager)

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    tool_catalog_path = os.path.join(project_root, "data", "tool_catalog.json")
    llm_models_config_path = os.path.join(project_root, "config", "llm_models.json")
    config_path = os.path.join(project_root, "config", "config.json")

    with open(tool_catalog_path, 'r') as f:
        tool_catalog = json.load(f)

    config_manager = ConfigManagerAgent(file_manager=file_manager, config_path=config_path)
    api_key = config_manager.get_api_key("google_gemini") or os.getenv("GOOGLE_API_KEY")

    install_logger = InstallLogger()
    installers = {
        "git": GitInstallerAdapter(command_runner, install_logger),
        "pip": PipInstallerAdapter(command_runner, install_logger),
        "pkg": PkgInstallerAdapter(command_runner, install_logger),
        "shell": ShellInstallerAdapter(command_runner, install_logger)
    }
    tool_installer = ToolInstallerAgent(installers=installers, logger=logger, config=config)

    plugin_manager = PluginManager(config=config, command_runner=command_runner, logger=logger, installers=installers)
    tool_adapters = plugin_manager.load_plugins()
    report_generators = [
        TxtReporter(file_manager=file_manager),
        JsonReporter(file_manager=file_manager),
        MarkdownReporter(file_manager=file_manager),
        PdfReporter(file_manager=file_manager)
    ]

    master_interpreter = MasterAIInterpreter(api_key=api_key, config_manager=config_manager, console=console)
    tool_command_parser = AIInterpreter(tool_catalog_path=tool_catalog_path, api_key=api_key or "dummy_key")
    knowledge_agent = KnowledgeAgent(api_key=api_key, file_manager=file_manager, logger=logger, tool_catalog_path=tool_catalog_path)
    network_agent = NetworkAgent(logger=logger)
    dependency_auditor = DependencyAuditorAgent(logger=logger)
    system_resource_agent = SystemResourceAgent(command_runner=command_runner)

    ollama_adapter = OllamaAdapter(command_runner=command_runner)
    pentestgpt_agent = PentestGptAgent(
        console=console, system_resource_agent=system_resource_agent,
        tool_installer_agent=tool_installer, ollama_adapter=ollama_adapter,
        command_runner=command_runner, tool_catalog=tool_catalog,
        llm_models_config_path=llm_models_config_path
    )

    doctor_agent = DoctorAgent(
        tool_installer=tool_installer, config_manager=config_manager,
        master_interpreter=master_interpreter, tool_catalog_path=tool_catalog_path
    )

    error_analyst = ErrorAnalystAgent(api_key=api_key, knowledge_agent=knowledge_agent)
    error_fixer = ErrorFixerAgent(api_key=api_key)
    security_advisor = SecurityAdvisorAgent(api_key=api_key)
    update_agent = UpdateAgent(logger=logger, audit_logger=audit_logger)

    orchestrator = OrchestratorAgent(
        master_interpreter=master_interpreter, tool_command_parser=tool_command_parser,
        tool_adapters=tool_adapters, report_generators=report_generators,
        error_analyst=error_analyst, error_fixer=error_fixer,
        tool_installer=tool_installer, security_advisor=security_advisor,
        network_agent=network_agent, update_agent=update_agent,
        config_manager=config_manager, dependency_auditor=dependency_auditor,
        knowledge_agent=knowledge_agent, pentestgpt_agent=pentestgpt_agent,
        logger=logger, config=config, audit_logger=audit_logger,
        consent_service=consent_service, execution_history=execution_history
    )

    return {
        "orchestrator": orchestrator,
        "doctor_agent": doctor_agent
    }
