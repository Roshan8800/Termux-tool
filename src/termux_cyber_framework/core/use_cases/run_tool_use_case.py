from typing import Dict, Optional
from termux_cyber_framework.core.domain.models import Report, Command, Error, Tool, InstallInfo
from termux_cyber_framework.core.domain.config import Config
from termux_cyber_framework.core.use_cases.ports import (
    CommandParserPort,
    ToolInstallerPort,
    ToolRunnerPort,
    ReportGeneratorPort,
    ErrorFixerPort,
    LoggerPort,
    LogLevel
)


class RunToolUseCase:
    """
    Orchestrates the entire process of running a command from user input,
    using tool-specific adapters and an AI-powered error fixer.
    """

    def __init__(
        self,
        parser: CommandParserPort,
        tool_installer: ToolInstallerPort,
        tool_runners: Dict[str, ToolRunnerPort],
        report_generator: ReportGeneratorPort,
        fallback_runner: ToolRunnerPort,
        error_fixer: ErrorFixerPort,
        logger: LoggerPort,
        config: Config
    ):
        self.parser = parser
        self.tool_installer = tool_installer
        self.tool_runners = tool_runners
        self.report_generator = report_generator
        self.fallback_runner = fallback_runner
        self.error_fixer = error_fixer
        self.logger = logger
        self.config = config

    async def _run_command_flow(self, command: Command) -> Report:
        """Helper to run a single command and return its report."""
        self.logger.log(f"Finding tool '{command.tool_name}'.")
        tool = self.tool_installer.find_tool(command.tool_name)
        if not tool:
            if command.tool_name == 'sudo':
                # Create a temporary Tool object for sudo, as it's not in our manifest
                sudo_install_info = InstallInfo(method="system", source="sudo")
                tool = Tool(name='sudo', description='Run as superuser', install_info=sudo_install_info, run_command='sudo')
                self.logger.log("'sudo' command detected, creating a temporary tool definition.", level=LogLevel.DEBUG)
            else:
                self.logger.log(f"Tool '{command.tool_name}' is not defined in the manifest.", level=LogLevel.ERROR)
                raise ValueError(f"Tool '{command.tool_name}' is not defined.")

        if not self.tool_installer.check_if_installed(tool) and command.tool_name != 'sudo':
             self.logger.log(f"Tool '{tool.name}' is not installed. Attempting installation.")
             try:
                 if not self.tool_installer.install_tool(tool, self.config):
                     self.logger.log(f"Failed to install tool '{tool.name}'.", level=LogLevel.ERROR)
                     raise RuntimeError(f"Failed to install tool '{tool.name}'.")
             except PermissionError as e:
                 self.logger.log(f"Installation failed: {e}", level=LogLevel.ERROR)
                 raise RuntimeError(str(e)) from e
             self.logger.log(f"Tool '{tool.name}' installed successfully.")

        runner = self.tool_runners.get(tool.name.lower(), self.fallback_runner)
        self.logger.log(f"Using runner '{runner.__class__.__name__}' for command '{command.tool_name}'.")
        report = runner.run(tool, command)
        self.logger.log(f"Command execution finished. Success: {report.success}", level=LogLevel.DEBUG)
        return report


    async def execute(self, user_input: str) -> Report:
        """
        Executes the full workflow, now with an attempt to fix errors.
        """
        self.logger.log(f"Received new command: '{user_input}'.")
        try:
            command = await self.parser.parse_command(user_input)
            self.logger.log(f"Parsed command: Tool='{command.tool_name}', Args={command.args}", level=LogLevel.DEBUG)
            report = await self._run_command_flow(command)

            # If the first attempt fails, try to fix it
            if not report.success and report.error:
                self.logger.log("Initial command failed. Consulting AI error fixer...", level=LogLevel.WARNING)
                fixed_command = await self.error_fixer.suggest_fix(report.error, command)

                if fixed_command:
                    self.logger.log(f"AI suggests a fix: '{fixed_command.raw_command}'. Retrying...")
                    report = await self._run_command_flow(fixed_command)
                else:
                    self.logger.log("AI had no suggestion. Reporting initial failure.")

        except (ValueError, RuntimeError) as e:
            self.logger.log(f"A critical error occurred: {e}", level=LogLevel.ERROR)
            command = Command(tool_name="framework", args=[], raw_command=user_input)
            error = Error(message=str(e))
            report = Report(command=command, success=False, output="", error=error)

        self.logger.log("Generating report.")
        self.report_generator.generate(report)
        return report
