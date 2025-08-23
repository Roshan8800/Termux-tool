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
    # ... (omitted for brevity)
    pass

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
        # ... (omitted for brevity)
        raise typer.Exit(code=1)

# ... (rest of the file omitted for brevity)
# ... (All commands: set-key, update, run, shell)
# ... (if __name__ == "__main__":)
