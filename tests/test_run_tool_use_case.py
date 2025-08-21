import pytest
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
from termux_cyber_framework.core.use_cases.run_tool_use_case import RunToolUseCase
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

    report_generator = MockReportGenerator()
    error_fixer = MockErrorFixer()
    logger = MockLogger()

    config = Config(allow_system_install=True)
    doctor = MockDoctor()
    audit_logger = MockAuditLogger()
    consent_service = MockConsentService()
    execution_history = MockExecutionHistory()
    use_case = RunToolUseCase(
        parser=RegexCommandParserAdapter(), # Using the real regex parser
        tool_adapters=tool_adapters,
        report_generator=report_generator,
        error_fixer=error_fixer,
        logger=logger,
        config=config,
        doctor=doctor,
        audit_logger=audit_logger,
        consent_service=consent_service,
        execution_history=execution_history
    )
    return use_case, tool_adapters, report_generator, error_fixer, nmap_runner, whois_runner

# --- Test Cases ---

@pytest.mark.asyncio
async def test_uses_specific_runner_when_available(setup):
    use_case, _, _, _, nmap_runner, whois_runner = setup
    await use_case.execute("nmap -sV localhost")
    assert nmap_runner.call_count == 1
    assert whois_runner.call_count == 0

@pytest.mark.asyncio
async def test_installs_tool_if_not_installed(setup, whois_tool):
    use_case, tool_adapters, _, _, _, _ = setup
    whois_tool.is_installed = False # Override installed status
    whois_adapter = tool_adapters["whois"]
    await use_case.execute("whois google.com")
    assert whois_adapter.install_called is True

@pytest.mark.asyncio
async def test_install_tool_fails(setup, whois_tool):
    use_case, tool_adapters, _, _, _, _ = setup
    whois_tool.is_installed = False # Override installed status
    whois_adapter = tool_adapters["whois"]
    whois_adapter.install_tool = lambda tool: False

    result = await use_case.execute("whois google.com")

    assert result.success is False
    assert "Failed to install tool" in result.error.message

@pytest.mark.asyncio
async def test_orchestrator_attempts_to_fix_and_rerun_on_failure(nmap_tool):
    """
    Tests the self-healing flow: first run fails, fixer is called, command is re-run.
    """
    # Arrange
    nmap_runner = MockToolRunner("NmapRunner", fail_on_first_run=True)
    sudo_runner = MockToolRunner("SudoRunner")

    nmap_adapter = MockToolAdapter(nmap_runner, nmap_tool)
    sudo_tool = Tool(name="sudo", description="Sudo", install_info=InstallInfo(method="pkg", source="sudo"), run_command="sudo", is_installed=True)
    sudo_adapter = MockToolAdapter(sudo_runner, sudo_tool)

    tool_adapters = {"nmap": nmap_adapter, "sudo": sudo_adapter}
    report_generator = MockReportGenerator()

    fixed_command = Command(tool_name="sudo", args=["nmap"], raw_command="sudo nmap")
    error_fixer = MockErrorFixer()
    async def suggest_fix_async(error, command):
        error_fixer.suggest_fix_called = True
        return fixed_command
    error_fixer.suggest_fix = suggest_fix_async

    config = Config(allow_system_install=True)
    doctor = MockDoctor()
    audit_logger = MockAuditLogger()
    consent_service = MockConsentService()
    execution_history = MockExecutionHistory()
    use_case = RunToolUseCase(
        parser=RegexCommandParserAdapter(),
        tool_adapters=tool_adapters,
        report_generator=report_generator,
        error_fixer=error_fixer,
        logger=MockLogger(),
        config=config,
        doctor=doctor,
        audit_logger=audit_logger,
        consent_service=consent_service,
        execution_history=execution_history
    )

    # Act
    final_report = await use_case.execute("nmap -p 80 localhost")

    # Assert
    assert error_fixer.suggest_fix_called is True
    assert nmap_runner.call_count == 1
    assert sudo_runner.call_count == 1
    assert final_report.success is True
    assert "Executed by SudoRunner" in final_report.output

@pytest.mark.asyncio
async def test_doctor_retry(nmap_tool):
    """
    Tests that the doctor is called on failure and a fix is attempted.
    """
    # Arrange
    nmap_runner = MockToolRunner("NmapRunner", fail_on_first_run=True)
    nmap_adapter = MockToolAdapter(nmap_runner, nmap_tool)
    tool_adapters = {"nmap": nmap_adapter}

    report_generator = MockReportGenerator()
    error_fixer = MockErrorFixer()
    doctor = MockDoctor()

    fix_command = Command(tool_name="echo", args=["hello"], raw_command="echo hello")
    remediation = Remediation(description="A test fix", command=fix_command)
    doctor.diagnose = lambda error, command: [remediation]

    config = Config(allow_system_install=True)
    audit_logger = MockAuditLogger()
    consent_service = MockConsentService()
    execution_history = MockExecutionHistory()
    use_case = RunToolUseCase(
        parser=RegexCommandParserAdapter(),
        tool_adapters=tool_adapters,
        report_generator=report_generator,
        error_fixer=error_fixer,
        logger=MockLogger(),
        config=config,
        doctor=doctor,
        audit_logger=audit_logger,
        consent_service=consent_service,
        execution_history=execution_history
    )

    # Act
    final_report = await use_case.execute("nmap -p 80 localhost")

    # Assert
    assert nmap_runner.call_count == 1
    assert final_report.success is False
