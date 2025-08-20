from termux_cyber_framework.core.domain.models import Report, Command, Error
from termux_cyber_framework.core.use_cases.ports import CommandParserPort, ToolManagerPort, ToolRunnerPort

class RunToolUseCase:
    """
    This use case orchestrates the entire process of running a command from user input.
    """

    def __init__(
        self,
        parser: CommandParserPort,
        tool_manager: ToolManagerPort,
        tool_runner: ToolRunnerPort,
    ):
        """
        Initializes the use case with the necessary ports.

        Args:
            parser: The port for parsing natural language commands.
            tool_manager: The port for managing tools (finding, installing).
            tool_runner: The port for executing shell commands.
        """
        self.parser = parser
        self.tool_manager = tool_manager
        self.tool_runner = tool_runner

    async def execute(self, user_input: str) -> Report:
        """
        Executes the full workflow from parsing input to running the command.

        Args:
            user_input: The raw natural language input from the user.

        Returns:
            A Report object detailing the outcome of the execution.
        """
        try:
            # 1. Parse the natural language command
            command = await self.parser.parse_command(user_input)

            # 2. Find the required tool from the tool manager
            tool = self.tool_manager.find_tool(command.tool_name)
            if not tool:
                raise ValueError(f"Tool '{command.tool_name}' is not defined in the tool registry.")

            # 3. Check if the tool is installed, and install if not
            tool.is_installed = self.tool_manager.check_if_installed(tool)
            if not tool.is_installed:
                print(f"[*] Tool '{tool.name}' is not installed. Attempting to install...")
                install_success = self.tool_manager.install_tool(tool)
                if not install_success:
                    raise RuntimeError(f"Failed to install tool '{tool.name}'.")
                print(f"[+] Tool '{tool.name}' installed successfully.")
                tool.is_installed = True

            # 4. Run the command using the tool runner
            print(f"[*] Executing command for tool '{tool.name}'...")
            report = self.tool_runner.run_command(tool, command)

            if not report.success:
                print(f"[-] Command failed for tool '{tool.name}'.")
            else:
                print(f"[+] Command executed successfully.")

            return report

        except (ValueError, RuntimeError) as e:
            # If any step above fails, create an error report
            error_command = Command(tool_name="framework", args=[], raw_command=user_input)
            error = Error(message=str(e))
            return Report(command=error_command, success=False, output="", error=error)
