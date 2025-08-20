import asyncio
import typer
import os
from termux_cyber_framework.core.use_cases.run_tool_use_case import RunToolUseCase
from termux_cyber_framework.core.command_runner import CommandRunner
from termux_cyber_framework.core.domain.config import Config
from termux_cyber_framework.adapters.command_parser.rules_parser import RulesParserAdapter
from termux_cyber_framework.adapters.tool_catalog.json_catalog import JsonCatalogAdapter
from termux_cyber_framework.core.use_cases.tool_installer import ToolInstaller
from termux_cyber_framework.adapters.tool_installer.git_installer import GitInstallerAdapter
from termux_cyber_framework.adapters.tool_installer.pip_installer import PipInstallerAdapter
from termux_cyber_framework.adapters.tool_installer.pkg_installer import PkgInstallerAdapter
from termux_cyber_framework.adapters.tool_runner.generic_runner import GenericRunner
from termux_cyber_framework.adapters.report_generator.json_reporter import JsonReporter
from termux_cyber_framework.adapters.audit_logger.file_audit_logger import FileAuditLogger
from termux_cyber_framework.adapters.error_fixer.simple_ai_fixer import SimpleAiFixerAdapter
from termux_cyber_framework.adapters.logger.file_logger import FileLoggerAdapter
from termux_cyber_framework.adapters.doctor.regex_doctor import RegexDoctorAdapter
from termux_cyber_framework.adapters.logger.install_logger import InstallLogger
from termux_cyber_framework.core.use_cases.consent.consent_service import ConsentService
from typing import Optional

app = typer.Typer(
    name="tcf",
    help="A natural language-powered cybersecurity framework for Termux."
)

def build_use_case(command_runner: Optional[CommandRunner] = None, config: Optional[Config] = None, consent_service: Optional[ConsentService] = None) -> RunToolUseCase:
    """
    Composition Root: Constructs and wires all adapters and use cases.
    """
    # --- Adapters Initialization ---

    config = config or Config()
    command_runner = command_runner or CommandRunner()
    consent_service = consent_service or ConsentService()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    manifest_path = os.path.join(base_dir, "..", "tool_installer", "tools.json")
    parser_rules_path = os.path.join(base_dir, "..", "..", "config", "parser_rules.json")
    doctor_rules_path = os.path.join(base_dir, "..", "..", "config", "doctor_rules.json")

    # Ports -> Adapters
    command_parser = RulesParserAdapter(rules_path=parser_rules_path)
    tool_catalog = JsonCatalogAdapter(manifest_path=manifest_path)

    install_logger = InstallLogger()
    installers = {
        "git": GitInstallerAdapter(command_runner, install_logger),
        "pip": PipInstallerAdapter(command_runner, install_logger),
        "pkg": PkgInstallerAdapter(command_runner, install_logger),
    }
    tool_installer = ToolInstaller(catalog=tool_catalog, installers=installers)

    tool_runners = {} # Will be populated based on the catalog
    for tool in tool_catalog.get_tools():
        if tool.adapter_class:
            try:
                module_path, class_name = tool.adapter_class.rsplit('.', 1)
                module = __import__(module_path, fromlist=[class_name])
                adapter_class = getattr(module, class_name)
                tool_runners[tool.name.lower()] = adapter_class(command_runner=command_runner)
            except (ImportError, AttributeError) as e:
                print(f"[-] Warning: Could not load adapter for '{tool.name}': {e}")

    report_generator = JsonReporter()
    audit_logger = FileAuditLogger()
    error_fixer = SimpleAiFixerAdapter()
    fallback_runner = GenericRunner(command_runner=command_runner)
    logger = FileLoggerAdapter()
    doctor = RegexDoctorAdapter(
        rules_path=doctor_rules_path,
        command_runner=command_runner,
        logger=logger
    )

    # --- Use Case Construction ---

    return RunToolUseCase(
        parser=command_parser,
        tool_installer=tool_installer,
        tool_runners=tool_runners,
        report_generator=report_generator,
        fallback_runner=fallback_runner,
        error_fixer=error_fixer,
        logger=logger,
        config=config,
        doctor=doctor,
        audit_logger=audit_logger,
        consent_service=consent_service
    )

@app.command()
def run(
    command: str = typer.Argument(..., help="The command to run in natural language.")
):
    """
    Runs a command by parsing it, ensuring the tool is installed,
    and executing it using the best available runner.
    """
    use_case = build_use_case()

    async def main():
        await use_case.execute(command)

    asyncio.run(main())

if __name__ == "__main__":
    app()
