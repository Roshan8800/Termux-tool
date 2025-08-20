from typing import Dict, Optional
from datetime import datetime
from termux_cyber_framework.core.domain.models import ExecutionResult, Command, Error, Tool, InstallInfo
from termux_cyber_framework.core.domain.config import Config
from termux_cyber_framework.core.domain.run_paths import RunPaths
from termux_cyber_framework.core.use_cases.ports import (
    CommandParserPort,
    ToolAdapterPort,
    ReportGeneratorPort,
    ErrorFixerPort,
    LoggerPort,
    DoctorPort,
    AuditLoggerPort,
    ConsentPort,
    LogLevel
)


class RunToolUseCase:
    """
    Orchestrates the entire process of running a command from user input,
    using tool-specific adapters and an AI-powered error fixer.
    """

from termux_cyber_framework.adapters.persistence.execution_history import ExecutionHistory

    def __init__(
        self,
        parser: CommandParserPort,
        tool_adapters: Dict[str, ToolAdapterPort],
        report_generator: ReportGeneratorPort,
        error_fixer: ErrorFixerPort,
        logger: LoggerPort,
        config: Config,
        doctor: DoctorPort,
        audit_logger: AuditLoggerPort,
        consent_service: ConsentPort,
        execution_history: ExecutionHistory
    ):
        self.parser = parser
        self.tool_adapters = tool_adapters
        self.report_generator = report_generator
        self.error_fixer = error_fixer
        self.logger = logger
        self.config = config
        self.doctor = doctor
        self.audit_logger = audit_logger
        self.consent_service = consent_service
        self.execution_history = execution_history

    async def _run_command_flow(self, command: Command) -> ExecutionResult:
        """Helper to run a single command and return its report."""
        self.logger.log(f"Finding adapter for tool '{command.tool_name}'.")
        adapter = self.tool_adapters.get(command.tool_name.lower())
        if not adapter:
            self.logger.log(f"Tool '{command.tool_name}' is not supported.", level=LogLevel.ERROR)
            raise ValueError(f"Tool '{command.tool_name}' is not supported.")

        if not adapter.is_installed():
             self.logger.log(f"Tool '{command.tool_name}' is not installed. Attempting installation.")
             if not self.config.dry_run:
                 if not adapter.install(self.config):
                     self.logger.log(f"Failed to install tool '{command.tool_name}'.", level=LogLevel.ERROR)
                     raise RuntimeError(f"Failed to install tool '{command.tool_name}'.")
                 self.logger.log(f"Tool '{command.tool_name}' installed successfully.")
             else:
                self.logger.log(f"Dry run: Skipping installation of tool '{command.tool_name}'.", level=LogLevel.INFO)

        self.logger.log(f"Using adapter '{adapter.__class__.__name__}' for command '{command.tool_name}'.")

        paths = self.report_generator.prepare_report_paths(command.tool_name)

        if self.config.dry_run:
            self.logger.log(f"Dry run: Skipping execution of command '{command.raw_command}'.", level=LogLevel.INFO)
            now = datetime.now()
            return ExecutionResult(
                command=command,
                success=True,
                output="Dry run: command not executed.",
                error=None,
                start_time=now,
                end_time=now,
                output_log_file=str(paths.output_log_file)
            )

        result = adapter.run(command, paths)
        result.output_log_file = str(paths.output_log_file) # Set the log file path in the result

        self.logger.log(f"Command execution finished. Success: {result.success}", level=LogLevel.DEBUG)
        return result


    async def execute(self, user_input: str) -> ExecutionResult:
        """
        Executes the full workflow, now with an attempt to fix errors.
        """
        self.logger.log(f"Received new command: '{user_input}'.")
        try:
            command = await self.parser.parse_command(user_input)
            self.logger.log(f"Parsed command: Tool='{command.tool_name}', Args={command.args}", level=LogLevel.DEBUG)

            if not self.config.dry_run and not self.consent_service.get_consent(command):
                self.logger.log("User did not provide consent. Aborting.", level=LogLevel.WARNING)
                error = Error(message="User did not provide consent.")
                now = datetime.now()
                return ExecutionResult(
                    command=command,
                    success=False,
                    output="",
                    error=error,
                    start_time=now,
                    end_time=now
                )

            result = await self._run_command_flow(command)

            # If the first attempt fails, try to fix it
            if not result.success and result.error:
                self.logger.log("Initial command failed. Consulting AI error fixer...", level=LogLevel.WARNING)
                fixed_command = await self.error_fixer.suggest_fix(result.error, command)

                if fixed_command:
                    self.logger.log(f"AI suggests a fix: '{fixed_command.raw_command}'. Retrying...")
                    result = await self._run_command_flow(fixed_command)
                else:
                    self.logger.log("AI had no suggestion. Reporting initial failure.")

        except (ValueError, RuntimeError) as e:
            self.logger.log(f"A critical error occurred: {e}", level=LogLevel.ERROR)
            command = Command(tool_name="framework", args=[], raw_command=user_input)
            error = Error(message=str(e))
            now = datetime.now()
            result = ExecutionResult(
                command=command,
                success=False,
                output="",
                error=error,
                start_time=now,
                end_time=now
            )

        if not result.success:
            self.logger.log("Command failed, running doctor.", level=LogLevel.INFO)
            fixes = await self.doctor.detect_and_fix(result)
            if fixes:
                self.logger.log(f"Doctor found {len(fixes)} potential fixes.", level=LogLevel.INFO)
                # For now, we just log the fixes. A more advanced implementation
                # could present them to the user or attempt to re-run the command.

        self.logger.log("Generating report.")
        paths = self.report_generator.prepare_report_paths(result.command.tool_name)
        self.report_generator.generate(result, paths)

        self.audit_logger.append({
            "session_id": self.config.session_id,
            "consent_hash": self.config.consent_hash,
            "command": result.command.raw_command,
            "tool": result.command.tool_name,
            "exit_code": result.error.error_code if result.error else 0,
            "artifact_paths": [str(paths.summary_file), str(paths.output_log_file)]
        })

        self.execution_history.append(result)

        return result
