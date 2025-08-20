import asyncio
import typer
import os
from termux_cyber_framework.core.use_cases.run_tool_use_case import RunToolUseCase
from termux_cyber_framework.core.command_runner import CommandRunner
from termux_cyber_framework.core.domain.config import Config
from termux_cyber_framework.adapters.command_parser.rules_parser import RulesParserAdapter
from termux_cyber_framework.adapters.tool_runner.nmap_adapter import NmapAdapter
from termux_cyber_framework.adapters.tool_runner.sqlmap_adapter import SqlmapAdapter
from termux_cyber_framework.adapters.report_generator.txt_reporter import TxtReporter
from termux_cyber_framework.adapters.persistence.execution_history import ExecutionHistory

def build_use_case(command_runner: Optional[CommandRunner] = None, config: Optional[Config] = None, consent_service: Optional[ConsentService] = None) -> RunToolUseCase:
    """
    Composition Root: Constructs and wires all adapters and use cases.
    """
    # --- Adapters Initialization ---

    config = config or Config()
    command_runner = command_runner or CommandRunner()
    consent_service = consent_service or ConsentService()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    parser_rules_path = os.path.join(base_dir, "..", "..", "config", "parser_rules.json")
    doctor_rules_path = os.path.join(base_dir, "..", "..", "config", "doctor_rules.json")

    # Ports -> Adapters
    command_parser = RulesParserAdapter(rules_path=parser_rules_path)

    tool_adapters = {
        "nmap": NmapAdapter(command_runner),
        "sqlmap": SqlmapAdapter(command_runner),
    }

    report_generator = TxtReporter()
    audit_logger = FileAuditLogger()
    execution_history = ExecutionHistory()
    error_fixer = SimpleAiFixerAdapter()
    logger = FileLoggerAdapter()
    doctor = RegexDoctorAdapter(
        rules_path=doctor_rules_path,
        command_runner=command_runner,
        logger=logger
    )

    # --- Use Case Construction ---

    return RunToolUseCase(
        parser=command_parser,
        tool_adapters=tool_adapters,
        report_generator=report_generator,
        error_fixer=error_fixer,
        logger=logger,
        config=config,
        doctor=doctor,
        audit_logger=audit_logger,
        consent_service=consent_service,
        execution_history=execution_history
    )

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
    use_case = build_use_case(config=config)

    async def main():
        await use_case.execute(command)

    asyncio.run(main())

if __name__ == "__main__":
    app()
