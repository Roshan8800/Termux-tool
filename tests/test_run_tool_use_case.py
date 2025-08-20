import pytest
from typing import Optional, List, Dict
from termux_cyber_framework.core.domain.models import Command, Tool, Report, Error
from termux_cyber_framework.core.use_cases.ports import (
    ToolInstallerPort,
    ToolRunnerPort,
    ReportGeneratorPort,
    ErrorFixerPort
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
    def __init__(self, runner_name: str, fail_on_first_run: bool = False):
        self.runner_name = runner_name
        self.call_count = 0
        self.fail_on_first_run = fail_on_first_run

    def run(self, tool: Tool, command: Command) -> Report:
        self.call_count += 1
        if self.fail_on_first_run and self.call_count == 1:
            return Report(
                command=command,
                success=False,
                output="Permission denied",
                error=Error(message="Permission denied")
            )
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

class MockErrorFixer(ErrorFixerPort):
    def __init__(self, fix_to_suggest: Optional[Command] = None):
        self.suggest_fix_called = False
        self.fix_to_suggest = fix_to_suggest

    async def suggest_fix(self, error: Error, command: Command) -> Optional[Command]:
        self.suggest_fix_called = True
        return self.fix_to_suggest

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
    installer = MockToolInstaller(tools=[nmap_tool])
    report_generator = MockReportGenerator()
    nmap_runner = MockToolRunner("NmapRunner")
    fallback_runner = MockToolRunner("FallbackRunner")
    error_fixer = MockErrorFixer()
    runners_registry = {"nmap": nmap_runner}

    use_case = RunToolUseCase(SimpleCommandParserAdapter(), installer, runners_registry, report_generator, fallback_runner, error_fixer)
    await use_case.execute("nmap -sV localhost")

    assert nmap_runner.call_count == 1
    assert fallback_runner.call_count == 0
    assert report_generator.generate_called_with is not None

@pytest.mark.asyncio
async def test_uses_fallback_runner_when_specific_is_not_available(whois_tool):
    """Tests that the fallback runner is used for tools not in the registry."""
    installer = MockToolInstaller(tools=[whois_tool])
    report_generator = MockReportGenerator()
    nmap_runner = MockToolRunner("NmapRunner")
    fallback_runner = MockToolRunner("FallbackRunner")
    error_fixer = MockErrorFixer()
    runners_registry = {"nmap": nmap_runner}

    use_case = RunToolUseCase(SimpleCommandParserAdapter(), installer, runners_registry, report_generator, fallback_runner, error_fixer)
    await use_case.execute("whois google.com")

    assert nmap_runner.call_count == 0
    assert fallback_runner.call_count == 1
    assert report_generator.generate_called_with is not None

@pytest.mark.asyncio
async def test_installs_tool_if_not_installed(nmap_tool):
    """Tests that the install port is called for a non-installed tool."""
    nmap_tool.is_installed = False
    installer = MockToolInstaller(tools=[nmap_tool])
    report_generator = MockReportGenerator()
    fallback_runner = MockToolRunner("FallbackRunner")
    error_fixer = MockErrorFixer()

    use_case = RunToolUseCase(SimpleCommandParserAdapter(), installer, {}, report_generator, fallback_runner, error_fixer)
    await use_case.execute("nmap localhost")

    assert installer.install_called_for is not None
    assert installer.install_called_for.name == "nmap"
    assert fallback_runner.call_count == 1

@pytest.mark.asyncio
async def test_orchestrator_attempts_to_fix_and_rerun_on_failure(nmap_tool):
    """
    Tests the full self-healing flow: the first run fails, the fixer is called,
    and the command is successfully re-run.
    """
    installer = MockToolInstaller(tools=[nmap_tool])
    report_generator = MockReportGenerator()
    failing_runner = MockToolRunner("NmapRunner", fail_on_first_run=True)
    fixed_command = Command(tool_name="sudo", args=["nmap"], raw_command="sudo nmap")
    error_fixer = MockErrorFixer(fix_to_suggest=fixed_command)
    sudo_runner = MockToolRunner("SudoRunner")
    runners_registry = {"nmap": failing_runner, "sudo": sudo_runner}

    use_case = RunToolUseCase(SimpleCommandParserAdapter(), installer, runners_registry, report_generator, failing_runner, error_fixer)
    final_report = await use_case.execute("nmap -p 80 localhost")

    assert error_fixer.suggest_fix_called is True
    assert failing_runner.call_count == 1
    assert sudo_runner.call_count == 1
    assert final_report.success is True
    assert "Executed by SudoRunner" in final_report.output
    assert report_generator.generate_called_with is final_report
