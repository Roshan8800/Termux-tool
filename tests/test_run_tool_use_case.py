import pytest
from typing import Optional, List, Dict
from datetime import datetime
from termux_cyber_framework.core.domain.models import Command, Tool, ExecutionResult, Error, InstallInfo
from termux_cyber_framework.core.domain.config import Config
from termux_cyber_framework.core.use_cases.ports import (
    ToolInstallerPort,
    ToolRunnerPort,
    ReportGeneratorPort,
    ErrorFixerPort,
    LoggerPort,
    DoctorPort
)
from termux_cyber_framework.core.use_cases.run_tool_use_case import RunToolUseCase
from termux_cyber_framework.adapters.command_parser.regex_parser import RegexCommandParserAdapter

# --- Mock Adapters for Testing ---

class MockDoctor(DoctorPort):
    def detect_and_fix(self, result: ExecutionResult) -> List[dict]:
        return []

class MockLogger(LoggerPort):
    def log(self, message: str, level: str = "INFO"):
        pass

class MockDynamicToolManager(ToolInstallerPort):
    def __init__(self, tools: List[Tool], runners: Dict[str, ToolRunnerPort]):
        self._tools = {tool.name.lower(): tool for tool in tools}
        self._runners = runners
        self.install_called_for: Optional[Tool] = None

    def find_tool(self, name: str) -> Optional[Tool]:
        return self._tools.get(name.lower())

    def check_if_installed(self, tool: Tool) -> bool:
        return tool.is_installed

    def install_tool(self, tool: Tool, config: Config) -> bool:
        self.install_called_for = tool
        tool.is_installed = True
        return True

    # This method is part of the concrete adapter, but we mock it here
    # to control the runners available in the test.
    def load_tool_runners(self) -> Dict[str, ToolRunnerPort]:
        return self._runners

class MockToolRunner(ToolRunnerPort):
    def __init__(self, runner_name: str, fail_on_first_run: bool = False):
        self.runner_name = runner_name
        self.call_count = 0
        self.fail_on_first_run = fail_on_first_run

    def run(self, tool: Tool, command: Command) -> ExecutionResult:
        self.call_count += 1
        now = datetime.now()
        if self.fail_on_first_run and self.call_count == 1:
            return ExecutionResult(
                command=command,
                success=False,
                output="Permission denied",
                error=Error(message="Permission denied"),
                start_time=now,
                end_time=now
            )
        return ExecutionResult(
            command=command,
            success=True,
            output=f"Executed by {self.runner_name}",
            error=None,
            start_time=now,
            end_time=now
        )

class MockReportGenerator(ReportGeneratorPort):
    def __init__(self):
        self.generate_called_with: Optional[ExecutionResult] = None

    def generate(self, result: ExecutionResult) -> None:
        self.generate_called_with = result

class MockErrorFixer(ErrorFixerPort):
    async def suggest_fix(self, error: Error, command: Command) -> Optional[Command]:
        return None # Default to no fix

# --- Test Fixtures ---

@pytest.fixture
def nmap_tool():
    install_info = InstallInfo(method="pkg", source="nmap")
    return Tool(name="nmap", description="Nmap", install_info=install_info, run_command="nmap", is_installed=True)

@pytest.fixture
def whois_tool():
    install_info = InstallInfo(method="pkg", source="whois")
    return Tool(name="whois", description="Whois", install_info=install_info, run_command="whois", is_installed=True)

# --- Test Setup ---

@pytest.fixture
def setup(nmap_tool, whois_tool):
    """A general setup fixture to provide all necessary mocks."""
    nmap_runner = MockToolRunner("NmapRunner")
    fallback_runner = MockToolRunner("FallbackRunner")

    tool_manager = MockDynamicToolManager(
        tools=[nmap_tool, whois_tool],
        runners={"nmap": nmap_runner} # Only nmap has a specific runner
    )

    report_generator = MockReportGenerator()
    error_fixer = MockErrorFixer()
    logger = MockLogger()

    config = Config(allow_system_install=True)
    doctor = MockDoctor()
    use_case = RunToolUseCase(
        parser=RegexCommandParserAdapter(), # Using the real regex parser
        tool_installer=tool_manager,
        tool_runners=tool_manager.load_tool_runners(), # Dynamically load runners
        report_generator=report_generator,
        fallback_runner=fallback_runner,
        error_fixer=error_fixer,
        logger=logger,
        config=config,
        doctor=doctor
    )
    return use_case, tool_manager, report_generator, error_fixer, nmap_runner, fallback_runner

# --- Test Cases ---

@pytest.mark.asyncio
async def test_uses_specific_runner_when_available(setup):
    use_case, _, _, _, nmap_runner, fallback_runner = setup
    await use_case.execute("nmap -sV localhost")
    assert nmap_runner.call_count == 1
    assert fallback_runner.call_count == 0

@pytest.mark.asyncio
async def test_uses_fallback_runner_when_specific_is_not_available(setup):
    use_case, _, _, _, nmap_runner, fallback_runner = setup
    await use_case.execute("whois google.com")
    assert nmap_runner.call_count == 0
    assert fallback_runner.call_count == 1

@pytest.mark.asyncio
async def test_installs_tool_if_not_installed(setup, whois_tool):
    use_case, tool_manager, _, _, _, _ = setup
    whois_tool.is_installed = False # Override installed status
    await use_case.execute("whois google.com")
    assert tool_manager.install_called_for is not None
    assert tool_manager.install_called_for.name == "whois"

@pytest.mark.asyncio
async def test_orchestrator_attempts_to_fix_and_rerun_on_failure(nmap_tool):
    """
    Tests the self-healing flow: first run fails, fixer is called, command is re-run.
    """
    # Arrange
    # This runner is configured to fail on its first execution.
    nmap_runner = MockToolRunner("NmapRunner", fail_on_first_run=True)
    sudo_runner = MockToolRunner("SudoRunner")

    tool_manager = MockDynamicToolManager(
        tools=[nmap_tool],
        runners={"nmap": nmap_runner, "sudo": sudo_runner}
    )

    report_generator = MockReportGenerator()

    # This fixer will suggest a 'sudo' command when it sees the failure.
    fixed_command = Command(tool_name="sudo", args=["nmap"], raw_command="sudo nmap")
    error_fixer = MockErrorFixer()
    async def suggest_fix_async(error, command):
        error_fixer.suggest_fix_called = True
        return fixed_command
    error_fixer.suggest_fix = suggest_fix_async

    config = Config(allow_system_install=True)
    doctor = MockDoctor()
    use_case = RunToolUseCase(
        parser=RegexCommandParserAdapter(),
        tool_installer=tool_manager,
        tool_runners=tool_manager.load_tool_runners(),
        report_generator=report_generator,
        fallback_runner=MockToolRunner("Fallback"),
        error_fixer=error_fixer,
        logger=MockLogger(),
        config=config,
        doctor=doctor
    )

    # Act
    final_report = await use_case.execute("nmap -p 80 localhost")

    # Assert
    assert error_fixer.suggest_fix_called is True
    assert nmap_runner.call_count == 1   # The failing runner was called once.
    assert sudo_runner.call_count == 1   # The 'fix' runner was called once.
    assert final_report.success is True
    assert "Executed by SudoRunner" in final_report.output
