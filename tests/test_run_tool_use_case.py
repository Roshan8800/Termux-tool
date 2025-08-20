import pytest
from typing import Optional, List
from termux_cyber_framework.core.domain.models import Command, Tool, Report, Error
from termux_cyber_framework.core.use_cases.ports import ToolManagerPort, ToolRunnerPort
from termux_cyber_framework.core.use_cases.run_tool_use_case import RunToolUseCase
from termux_cyber_framework.adapters.command_parser.simple_parser import SimpleCommandParserAdapter

# --- Mock Adapters for Testing ---

class MockToolManager(ToolManagerPort):
    def __init__(self, tools: List[Tool]):
        self._tools = {tool.name: tool for tool in tools}
        self.install_called_for: Optional[Tool] = None

    def find_tool(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def check_if_installed(self, tool: Tool) -> bool:
        # Control the installed state from the tool object itself for testing
        return tool.is_installed

    def install_tool(self, tool: Tool) -> bool:
        self.install_called_for = tool
        # Simulate successful installation
        tool.is_installed = True
        return True

class MockToolRunner(ToolRunnerPort):
    def run_command(self, tool: Tool, command: Command) -> Report:
        # Simulate a successful run
        return Report(
            command=command,
            success=True,
            output=f"Successfully executed {tool.name} with args: {' '.join(command.args)}",
            error=None
        )

# --- Test Cases ---

@pytest.fixture
def nmap_tool():
    return Tool(
        name="nmap",
        description="Network scanner",
        install_command="pkg install nmap",
        run_command="nmap",
        is_installed=True  # Assume installed by default
    )

@pytest.mark.asyncio
async def test_run_tool_success_scenario(nmap_tool):
    """Tests the successful execution of a command for an installed tool."""
    # Arrange
    tool_manager = MockToolManager(tools=[nmap_tool])
    tool_runner = MockToolRunner()
    parser = SimpleCommandParserAdapter()
    use_case = RunToolUseCase(parser, tool_manager, tool_runner)

    # Act
    report = await use_case.execute("nmap -sV 127.0.0.1")

    # Assert
    assert report.success is True
    assert report.command.tool_name == "nmap"
    assert report.command.args == ["-sV", "127.0.0.1"]
    assert "Successfully executed nmap" in report.output
    assert tool_manager.install_called_for is None # Install should not be called

@pytest.mark.asyncio
async def test_run_tool_installs_if_not_present(nmap_tool):
    """Tests that the use case attempts to install a tool if it's not installed."""
    # Arrange
    nmap_tool.is_installed = False # Mark as not installed
    tool_manager = MockToolManager(tools=[nmap_tool])
    tool_runner = MockToolRunner()
    parser = SimpleCommandParserAdapter()
    use_case = RunToolUseCase(parser, tool_manager, tool_runner)

    # Act
    await use_case.execute("nmap 127.0.0.1")

    # Assert
    assert tool_manager.install_called_for is not None
    assert tool_manager.install_called_for.name == "nmap"

@pytest.mark.asyncio
async def test_run_tool_handles_unknown_tool():
    """Tests that the use case returns an error report for an unknown tool."""
    # Arrange
    tool_manager = MockToolManager(tools=[]) # No tools registered
    tool_runner = MockToolRunner()
    parser = SimpleCommandParserAdapter()
    use_case = RunToolUseCase(parser, tool_manager, tool_runner)

    # Act
    report = await use_case.execute("unknown_tool --help")

    # Assert
    assert report.success is False
    assert report.error is not None
    assert "Tool 'unknown_tool' is not defined" in report.error.message
