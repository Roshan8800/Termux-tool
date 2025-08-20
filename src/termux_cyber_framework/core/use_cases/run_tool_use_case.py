from typing import Dict
from termux_cyber_framework.core.domain.models import Report, Command, Error
from termux_cyber_framework.core.use_cases.ports import (
    CommandParserPort,
    ToolInstallerPort,
    ToolRunnerPort,
    ReportGeneratorPort
)

class RunToolUseCase:
    """
    Orchestrates the entire process of running a command from user input,
    using tool-specific adapters.
    """

    def __init__(
        self,
        parser: CommandParserPort,
        tool_installer: ToolInstallerPort,
        tool_runners: Dict[str, ToolRunnerPort], # A registry of tool-specific runners
        report_generator: ReportGeneratorPort,
        fallback_runner: ToolRunnerPort # A generic runner for tools without a specific adapter
    ):
        self.parser = parser
        self.tool_installer = tool_installer
        self.tool_runners = tool_runners
        self.report_generator = report_generator
        self.fallback_runner = fallback_runner

    async def execute(self, user_input: str) -> Report:
        """
        Executes the full workflow: parse, find tool, install if needed,
        select the correct runner, execute, and generate a report.

        Args:
            user_input: The raw natural language input from the user.

        Returns:
            The final Report object.
        """
        try:
            # 1. Parse the command
            command = await self.parser.parse_command(user_input)

            # 2. Find the tool definition
            tool = self.tool_installer.find_tool(command.tool_name)
            if not tool:
                raise ValueError(f"Tool '{command.tool_name}' is not defined in the tool registry.")

            # 3. Ensure the tool is installed
            if not self.tool_installer.check_if_installed(tool):
                print(f"[*] Tool '{tool.name}' is not installed. Attempting to install...")
                if not self.tool_installer.install_tool(tool):
                    raise RuntimeError(f"Failed to install tool '{tool.name}'.")
                print(f"[+] Tool '{tool.name}' installed successfully.")

            # 4. Select the appropriate tool runner (specific or fallback)
            runner = self.tool_runners.get(tool.name.lower(), self.fallback_runner)
            print(f"[*] Using runner: {runner.__class__.__name__}")

            # 5. Execute the command
            report = runner.run(tool, command)

        except (ValueError, RuntimeError) as e:
            # Create a generic error report if a step above fails
            command = Command(tool_name="framework", args=[], raw_command=user_input)
            error = Error(message=str(e))
            report = Report(command=command, success=False, output="", error=error)

        # 6. Generate the output via the report generator port
        self.report_generator.generate(report)

        return report # Return the report for any further programmatic use
