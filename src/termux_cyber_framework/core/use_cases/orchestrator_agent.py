import os
from typing import Dict, Optional
from datetime import datetime
from termux_cyber_framework.core.domain.models import ExecutionResult, Command, Error, Tool, InstallInfo
from termux_cyber_framework.core.domain.config import Config
from termux_cyber_framework.core.domain.run_paths import RunPaths
from termux_cyber_framework.adapters.persistence.execution_history import ExecutionHistory
from termux_cyber_framework.core.use_cases.ports import (
    CommandParserPort,
    ToolAdapterPort,
    ReportGeneratorPort,
    ErrorFixerPort,
    List,
    LoggerPort,
    DoctorPort,
    AuditLoggerPort,
    ConsentPort,
    LogLevel
)
from termux_cyber_framework.agents.error_analyst_agent import ErrorAnalystAgent
from termux_cyber_framework.agents.tool_installer_agent import ToolInstallerAgent
from termux_cyber_framework.agents.security_advisor_agent import SecurityAdvisorAgent


class OrchestratorAgent:
    """
    Acts as the brain of the system, orchestrating the entire process of
    running a command from user input.
    """
    def __init__(
        self,
        parser: CommandParserPort,
        tool_adapters: Dict[str, ToolAdapterPort],
        report_generators: List[ReportGeneratorPort],
        error_analyst: ErrorAnalystAgent,
        tool_installer: ToolInstallerAgent,
        security_advisor: SecurityAdvisorAgent,
        logger: LoggerPort,
        config: Config,
        audit_logger: AuditLoggerPort,
        consent_service: ConsentPort,
        execution_history: ExecutionHistory
    ):
        self.parser = parser
        self.tool_adapters = tool_adapters
        self.report_generators = report_generators
        self.error_analyst = error_analyst
        self.tool_installer = tool_installer
        self.security_advisor = security_advisor
        self.logger = logger
        self.config = config
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

        tool = adapter.find_tool(command.tool_name)
        if not tool:
            raise ValueError(f"Tool '{command.tool_name}' not found by adapter.")

        # Delegate installation to the ToolInstallerAgent
        self.tool_installer.install_if_needed(tool)

        self.logger.log(f"Using adapter '{adapter.__class__.__name__}' for command '{command.tool_name}'.")

        # This is a bit of a hack. We'll use the paths from the first generator.
        # A better solution would be to have a shared path generation mechanism.
        paths = self.report_generators[0].prepare_report_paths(command.tool_name) if self.report_generators else None

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

        result = adapter.run(tool, command, paths)
        result.paths = paths
        result.output_log_file = str(paths.output_log_file)

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

            consent_given = self.consent_service.get_consent(command)
            if not self.config.dry_run and not consent_given:
                self.logger.log("User did not provide consent. Aborting.", level=LogLevel.WARNING)
                error = Error(message="User did not provide consent.")
                now = datetime.now()
                return ExecutionResult(
                    command=command,
                    success=False,
                    output="",
                    error=error,
                    start_time=now,
                    end_time=now,
                    consent_given=False
                )

            result = await self._run_command_flow(command)
            result.consent_given = consent_given

            # If the command fails, consult the error analyst. Otherwise, get security advice.
            if not result.success and result.error:
                self.logger.log("Command failed. Consulting Error Analyst Agent...", level=LogLevel.WARNING)
                analysis = await self.error_analyst.analyze_error(result.command, result.error)
                result.error.ai_analysis = analysis
                self.logger.log(f"Error analysis received:\n{analysis}", level=LogLevel.DEBUG)
            elif result.success:
                self.logger.log("Command successful. Consulting Security Advisor Agent...", level=LogLevel.INFO)
                advice = await self.security_advisor.provide_advice(result)
                result.ai_advice = advice
                self.logger.log(f"Security advice received: {advice}", level=LogLevel.DEBUG)

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

        self.logger.log("Generating reports.")
        paths = result.paths

        artifact_paths = []
        if paths:
            for report_generator in self.report_generators:
                report_generator.generate(result, paths)

            # Add all generated report files to artifacts
            artifact_paths.append(os.path.join(paths.run_dir, f"{paths.base_filename}.txt"))
            artifact_paths.append(os.path.join(paths.run_dir, f"{paths.base_filename}.json"))
            if paths.output_log_file:
                artifact_paths.append(str(paths.output_log_file))

        self.audit_logger.append({
            "session_id": self.config.session_id,
            "consent_hash": self.config.consent_hash,
            "command": result.command.raw_command,
            "tool": result.command.tool_name,
            "exit_code": result.error.error_code if result.error else 0,
            "error_message": result.error.message if result.error else None,
            "artifact_paths": artifact_paths
        })

        self.execution_history.append(result)

        return result
