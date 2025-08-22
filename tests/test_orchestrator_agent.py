import pytest
from unittest.mock import AsyncMock
from typing import Optional, List, Dict
from datetime import datetime
from termux_cyber_framework.core.domain.models import Command, Tool, ExecutionResult, Error, InstallInfo, Remediation
from termux_cyber_framework.core.domain.config import Config
from termux_cyber_framework.core.domain.run_paths import RunPaths
from termux_cyber_framework.core.use_cases.ports import (
    ToolInstallerPort,
    ToolRunnerPort,
    ReportGeneratorPort,
    ErrorFixerPort,
    ToolAdapterPort,
    LoggerPort,
    DoctorPort,
    AuditLoggerPort,
    ConsentPort
)
from termux_cyber_framework.core.use_cases.orchestrator_agent import OrchestratorAgent
from termux_cyber_framework.adapters.command_parser.regex_parser import RegexCommandParserAdapter
from tests.mocks import MockAuditLogger, MockExecutionHistory

# --- Mock Adapters for Testing ---

class MockDoctor(DoctorPort):
    def diagnose(self, error: Error, command: Command) -> list[Remediation]:
        return []

class MockConsentService(ConsentPort):
    def __init__(self, consent_to_give: bool = True):
        self.consent_to_give = consent_to_give

    def get_consent(self, command: Command) -> bool:
        return self.consent_to_give

class MockLogger(LoggerPort):
    def log(self, message: str, level: str = "INFO"):
        pass

class MockToolAdapter(ToolAdapterPort):
    def __init__(self, runner: ToolRunnerPort, tool: Tool):
        self._runner = runner
        self._tool = tool
        self.install_called = False

    def find_tool(self, name: str) -> Optional[Tool]:
        if name == self._tool.name:
            return self._tool
        return None

    def check_if_installed(self, tool: Tool) -> bool:
        return self._tool.is_installed

    def install_tool(self, tool: Tool) -> bool:
        self.install_called = True
        self._tool.is_installed = True
        return True

    def run(self, tool: Tool, command: Command, paths: RunPaths) -> ExecutionResult:
        return self._runner.run(tool, command, paths)

class MockToolRunner(ToolRunnerPort):
    def __init__(self, runner_name: str, fail_on_first_run: bool = False):
        self.runner_name = runner_name
        self.call_count = 0
        self.fail_on_first_run = fail_on_first_run

    def run(self, tool: Tool, command: Command, paths: RunPaths) -> ExecutionResult:
        self.call_count += 1
        now = datetime.now()
        if self.fail_on_first_run and self.call_count == 1:
            return ExecutionResult(
                command=command,
                success=False,
                output="Permission denied",
                error=Error(message="Permission denied"),
                start_time=now,
                end_time=now,
                output_log_file=str(paths.output_log_file)
            )
        return ExecutionResult(
            command=command,
            success=True,
            output=f"Executed by {self.runner_name}",
            error=None,
            start_time=now,
            end_time=now,
            output_log_file=str(paths.output_log_file)
        )

class MockReportGenerator(ReportGeneratorPort):
    def prepare_report_paths(self, tool_name: str) -> RunPaths:
        return RunPaths(summary_file="summary.json", output_log_file="run.log")

    def generate(self, result: ExecutionResult, paths: RunPaths) -> None:
        pass

class MockErrorFixer(ErrorFixerPort):
    async def suggest_fix(self, error: Error, command: Command) -> Optional[Command]:
        return None # Default to no fix

class MockErrorAnalystAgent:
    async def analyze_error(self, command: Command, error: Error) -> str:
        return "Mock AI analysis of the error."

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
    whois_runner = MockToolRunner("WhoisRunner")

    nmap_adapter = MockToolAdapter(nmap_runner, nmap_tool)
    whois_adapter = MockToolAdapter(whois_runner, whois_tool)

    tool_adapters = {
        "nmap": nmap_adapter,
        "whois": whois_adapter
    }

    report_generators = [MockReportGenerator()]
    error_analyst = MockErrorAnalystAgent()
    logger = MockLogger()

    config = Config(allow_system_install=True)
    audit_logger = MockAuditLogger()
    consent_service = MockConsentService()
    execution_history = MockExecutionHistory()
    orchestrator = OrchestratorAgent(
        parser=RegexCommandParserAdapter(),
        tool_adapters=tool_adapters,
        report_generators=report_generators,
        error_analyst=error_analyst,
        logger=logger,
        config=config,
        audit_logger=audit_logger,
        consent_service=consent_service,
        execution_history=execution_history
    )
    return orchestrator, tool_adapters, report_generators, error_analyst, nmap_runner, whois_runner

# --- Test Cases ---

@pytest.mark.asyncio
async def test_uses_specific_runner_when_available(setup):
    orchestrator, _, _, _, nmap_runner, whois_runner = setup
    await orchestrator.execute("nmap -sV localhost")
    assert nmap_runner.call_count == 1
    assert whois_runner.call_count == 0

@pytest.mark.asyncio
async def test_installs_tool_if_not_installed(setup, whois_tool):
    orchestrator, tool_adapters, _, _, _, _ = setup
    whois_tool.is_installed = False # Override installed status
    whois_adapter = tool_adapters["whois"]
    await orchestrator.execute("whois google.com")
    assert whois_adapter.install_called is True

@pytest.mark.asyncio
async def test_install_tool_fails(setup, whois_tool):
    orchestrator, tool_adapters, _, _, _, _ = setup
    whois_tool.is_installed = False # Override installed status
    whois_adapter = tool_adapters["whois"]
    whois_adapter.install_tool = lambda tool: False

    result = await orchestrator.execute("whois google.com")

    assert result.success is False
    assert "Failed to install tool" in result.error.message

@pytest.mark.asyncio
async def test_error_analyst_is_called_on_failure(nmap_tool):
    """
    Tests that the ErrorAnalystAgent is called when a command fails.
    """
    # Arrange
    nmap_runner = MockToolRunner("NmapRunner", fail_on_first_run=True)
    nmap_adapter = MockToolAdapter(nmap_runner, nmap_tool)
    tool_adapters = {"nmap": nmap_adapter}
    report_generators = [MockReportGenerator()]
    error_analyst = MockErrorAnalystAgent()

    # Spy on the analyze_error method
    error_analyst.analyze_error = AsyncMock(wraps=error_analyst.analyze_error)

    config = Config(allow_system_install=True)
    audit_logger = MockAuditLogger()
    consent_service = MockConsentService()
    execution_history = MockExecutionHistory()

    orchestrator = OrchestratorAgent(
        parser=RegexCommandParserAdapter(),
        tool_adapters=tool_adapters,
        report_generators=report_generators,
        error_analyst=error_analyst,
        logger=MockLogger(),
        config=config,
        audit_logger=audit_logger,
        consent_service=consent_service,
        execution_history=execution_history
    )

    # Act
    result = await orchestrator.execute("nmap -p 80 localhost")

    # Assert
    assert result.success is False
    assert result.error.ai_analysis == "Mock AI analysis of the error."
    error_analyst.analyze_error.assert_called_once()
