import pytest
from typing import Optional, List, Dict
from termux_cyber_framework.core.domain.models import Command, Tool, Report, Error
from termux_cyber_framework.core.use_cases.ports import (
    ToolInstallerPort,
    ToolRunnerPort,
    ReportGeneratorPort
)
from termux_cyber_framework.core.use_cases.run_tool_use_case import RunToolUseCase
from termux_cyber_framework.adapters.command_parser.simple_parser import SimpleCommandParserAdapter

# --- Mock Adapters for Testing ---

class MockToolInstaller(ToolInstallerPort):
    def __init__(self, tools: List[Tool]):
        self._tools = {tool.name.lower(): tool for tool in tools}
        self.install_called_for: Optional[Tool] = None

    def find_tool(self, name: str) -> Optional[Tool]:
        return self._tools.get(name.lower())

    def check_if_installed(self, tool: Tool) -> bool:
        return tool.is_installed

    def install_tool(self, tool: Tool) -> bool:
        self.install_called_for = tool
        tool.is_installed = True
        return True

class MockToolRunner(ToolRunnerPort):
    def __init__(self, runner_name: str):
        self.runner_name = runner_name
        self.run_called = False

    def run(self, tool: Tool, command: Command) -> Report:
        self.run_called = True
        return Report(
            command=command,
            success=True,
            output=f"Executed by {self.runner_name}",
            error=None
        )

class MockReportGenerator(ReportGeneratorPort):
    def __init__(self):
        self.generate_called_with: Optional[Report] = None

    def generate(self, report: Report) -> None:
        self.generate_called_with = report

# --- Test Fixtures ---

@pytest.fixture
def nmap_tool():
    return Tool(name="nmap", description="Nmap", install_command="pkg i nmap", run_command="nmap", is_installed=True)

@pytest.fixture
def whois_tool():
    return Tool(name="whois", description="Whois", install_command="pkg i whois", run_command="whois", is_installed=True)

# --- Test Cases ---

@pytest.mark.asyncio
async def test_uses_specific_runner_when_available(nmap_tool):
    """Tests that the correct tool-specific runner is selected from the registry."""
    # Arrange
    installer = MockToolInstaller(tools=[nmap_tool])
    report_generator = MockReportGenerator()

    nmap_runner = MockToolRunner("NmapRunner")
    fallback_runner = MockToolRunner("FallbackRunner")

    runners_registry = {"nmap": nmap_runner}

    use_case = RunToolUseCase(SimpleCommandParserAdapter(), installer, runners_registry, report_generator, fallback_runner)

    # Act
    await use_case.execute("nmap -sV localhost")

    # Assert
    assert nmap_runner.run_called is True
    assert fallback_runner.run_called is False
    assert report_generator.generate_called_with is not None

@pytest.mark.asyncio
async def test_uses_fallback_runner_when_specific_is_not_available(whois_tool):
    """Tests that the fallback runner is used for tools not in the registry."""
    # Arrange
    installer = MockToolInstaller(tools=[whois_tool])
    report_generator = MockReportGenerator()

    nmap_runner = MockToolRunner("NmapRunner")
    fallback_runner = MockToolRunner("FallbackRunner")

    runners_registry = {"nmap": nmap_runner} # No 'whois' runner

    use_case = RunToolUseCase(SimpleCommandParserAdapter(), installer, runners_registry, report_generator, fallback_runner)

    # Act
    await use_case.execute("whois google.com")

    # Assert
    assert nmap_runner.run_called is False
    assert fallback_runner.run_called is True
    assert report_generator.generate_called_with is not None

@pytest.mark.asyncio
async def test_installs_tool_if_not_installed(nmap_tool):
    """Tests that the install port is called for a non-installed tool."""
    # Arrange
    nmap_tool.is_installed = False
    installer = MockToolInstaller(tools=[nmap_tool])
    report_generator = MockReportGenerator()
    fallback_runner = MockToolRunner("FallbackRunner")

    use_case = RunToolUseCase(SimpleCommandParserAdapter(), installer, {}, report_generator, fallback_runner)

    # Act
    await use_case.execute("nmap localhost")

    # Assert
    assert installer.install_called_for is not None
    assert installer.install_called_for.name == "nmap"
    assert fallback_runner.run_called is True
    assert report_generator.generate_called_with.success is True
