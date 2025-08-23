import pytest
import os
import shutil
import asyncio
import re
import json
from glob import glob
from termux_cyber_framework.adapters.cli.main import build_agent_system
from termux_cyber_framework.core.domain.config import Config
from .mocks import MockCommandRunner, MockSecurityComplianceAgent, MockExecutionHistory, MockAIInterpreter
from termux_cyber_framework.core.domain.models import ExecutionResult

@pytest.fixture
def cleanup_files():
    """A pytest fixture to clean up log and report files after a test run."""
    # Run the test
    yield
    # Teardown: remove files created during the test
    print("\n[*] Cleaning up generated files...")
    files_to_remove = glob("logs/*.log") + glob("reports/*.json")
    for f in files_to_remove:
        try:
            os.remove(f)
            print(f"    - Removed {f}")
        except OSError as e:
            print(f"    - Error removing file {f}: {e.strerror}")

@pytest.fixture
def cleanup_cloned_tools():
    """A pytest fixture to clean up cloned tool directories."""
    yield
    print("\n[*] Cleaning up cloned tools...")
    if os.path.exists("tools"):
        shutil.rmtree("tools")
        print("    - Removed tools directory")


@pytest.mark.asyncio
async def test_end_to_end_whois_command_with_mock_ai(cleanup_files):
    """
    Tests the full end-to-end flow with a real command ('whois google.com').
    This test verifies that the command is executed and that log and report
    files are created correctly on the filesystem.
    """
    # Arrange
    # Build the full use case with all real adapters
    mock_runner = MockCommandRunner({
        "pkg install whois -y": {"returncode": 0, "stdout": "whois installed"},
        "whois google.com": {"returncode": 0, "stdout": "Registrant Organization: Google LLC"}
    })
    config = Config(allow_system_install=True)
    consent_service = MockSecurityComplianceAgent(consent_to_give=True)
    execution_history = MockExecutionHistory()
    orchestrator = build_agent_system(
        command_runner=mock_runner,
        config=config,
        consent_service=consent_service,
        execution_history=execution_history,
        parser=MockAIInterpreter()
    )
    command = "whois google.com"

    # Act
    # Execute the command through the orchestrator
    result = await orchestrator.execute(command)

    # Assert
    # 1. Assert the command was successful
    assert result.success is True
    assert result.error is None
    assert "Google LLC" in result.output # Check for expected content in the output

    # 2. Assert that a log file was created and contains expected content
    assert result.paths.output_log_file and os.path.exists(result.paths.output_log_file)
    with open(result.paths.output_log_file, 'r') as f:
        log_content = f.read()
    assert "Registrant Organization: Google LLC" in log_content

    # 3. Assert that report files were created and contain expected content
    txt_summary_path = os.path.join(result.paths.run_dir, f"{result.paths.base_filename}.txt")
    json_summary_path = os.path.join(result.paths.run_dir, f"{result.paths.base_filename}.json")

    assert os.path.exists(txt_summary_path)
    assert os.path.exists(json_summary_path)

    with open(txt_summary_path, 'r') as f:
        report_content = f.read()
    assert "Tool Used: whois" in report_content
    assert "Status: Success" in report_content

    with open(json_summary_path, 'r') as f:
        json_report = json.load(f)
    assert json_report["tool_used"] == "whois"
    assert json_report["status"] == "Success"

    # 4. Assert that an audit log event was created
    audit_log_path = "logs/audit.log"
    assert os.path.exists(audit_log_path)
    with open(audit_log_path, 'r') as f:
        audit_event = json.loads(f.readline())
    assert audit_event["tool"] == "whois"
    assert audit_event["command"] == "whois google.com"

    # 5. Assert that the execution history was updated
    assert len(execution_history.history) == 1
    assert execution_history.history[0].command.tool_name == "whois"


@pytest.mark.skip(reason="This test makes real API calls and is disabled to avoid credential/quota issues in CI.")
@pytest.mark.asyncio
async def test_end_to_end_with_real_ai(cleanup_files):
    """
    Tests the full end-to-end flow with the real AI interpreter.
    """
    # Arrange
    mock_runner = MockCommandRunner({
        "nmap -sV example.com": {"returncode": 0, "stdout": "Nmap scan report for example.com"}
    })
    config = Config(allow_system_install=True)
    consent_service = MockSecurityComplianceAgent(consent_to_give=True)
    execution_history = MockExecutionHistory()
    orchestrator = build_agent_system(
        command_runner=mock_runner,
        config=config,
        consent_service=consent_service,
        execution_history=execution_history
    )
    command = "scan example.com with nmap"

    # Act
    result = await orchestrator.execute(command)

    # Assert
    assert result.success is True
    assert result.command.tool_name == "nmap"


@pytest.mark.asyncio
async def test_end_to_end_git_install_command(cleanup_files, cleanup_cloned_tools):
    """
    Tests the full end-to-end flow for a tool installed via Git.
    This test verifies that the tool is cloned and then executed.
    """
    # Arrange
    mock_runner = MockCommandRunner({
        "git clone https://github.com/sqlmapproject/sqlmap.git tools/sqlmap": {"returncode": 0},
        "python3 tools/sqlmap/sqlmap.py --version --batch --threads 1": {"returncode": 0, "stdout": "1.8.3"}
    })
    config = Config(allow_system_install=True)
    consent_service = MockSecurityComplianceAgent(consent_to_give=True)
    execution_history = MockExecutionHistory()
    orchestrator = build_agent_system(
        command_runner=mock_runner,
        config=config,
        consent_service=consent_service,
        execution_history=execution_history,
        parser=MockAIInterpreter()
    )
    # Using --version is a simple, non-intrusive way to check if sqlmap runs.
    command = "sqlmap --version"

    # Act
    result = await orchestrator.execute(command)

    # Assert
    # 1. Assert that the command was successful
    assert result.success is True
    assert result.error is None
    # Check for a version string in the output
    assert re.search(r"\d+\.\d+", result.output)

    # 3. Assert log and report files were created
    assert result.paths.output_log_file and os.path.exists(result.paths.output_log_file)
    txt_summary_path = os.path.join(result.paths.run_dir, f"{result.paths.base_filename}.txt")
    json_summary_path = os.path.join(result.paths.run_dir, f"{result.paths.base_filename}.json")
    assert os.path.exists(txt_summary_path)
    assert os.path.exists(json_summary_path)

    # 4. Assert that an audit log event was created
    audit_log_path = "logs/audit.log"
    assert os.path.exists(audit_log_path)
    with open(audit_log_path, 'r') as f:
        # We need to read all lines to find the correct audit event
        for line in f:
            audit_event = json.loads(line)
            if audit_event["tool"] == "sqlmap":
                assert audit_event["command"] == "sqlmap --version"
                break

    # 5. Assert that the execution history was updated
    assert len(execution_history.history) == 1
    assert execution_history.history[0].command.tool_name == "sqlmap"


@pytest.mark.asyncio
async def test_system_install_disallowed(cleanup_files, monkeypatch):
    """
    Tests that a system-level installation is blocked when disallowed by policy.
    """
    # Arrange
    # Mock shutil.which to simulate the tool not being installed
    monkeypatch.setattr("shutil.which", lambda x: None)

    mock_runner = MockCommandRunner()
    config = Config(allow_system_install=False)
    consent_service = MockSecurityComplianceAgent(consent_to_give=True)
    execution_history = MockExecutionHistory()
    orchestrator = build_agent_system(
        command_runner=mock_runner,
        config=config,
        consent_service=consent_service,
        execution_history=execution_history,
        parser=MockAIInterpreter()
    )
    command = "whois google.com"

    # Act
    result = await orchestrator.execute(command)

    # Assert
    assert result.success is False
    assert result.error is not None
    assert "Failed to install tool 'whois'" in result.error.message


@pytest.mark.asyncio
async def test_install_logging(cleanup_files, monkeypatch):
    """
    Tests that installation output is logged correctly.
    """
    # Arrange
    # Mock shutil.which to simulate the tool not being installed, but the package manager being present.
    def mock_which(cmd):
        if cmd == "whois":
            return None
        return f"/usr/bin/{cmd}"
    monkeypatch.setattr("shutil.which", mock_which)
    monkeypatch.setattr("os.geteuid", lambda: 1000) # run as non-root to trigger sudo

    mock_runner = MockCommandRunner({
                "sudo apt-get update": {"returncode": 0},
                "sudo apt-get install whois -y": {"returncode": 0, "stdout": "installing whois...", "stderr": "some warning"},
            "whois google.com": {"returncode": 0, "stdout": "Registrant Organization: Google LLC"}
    })
    config = Config(allow_system_install=True)
    consent_service = MockSecurityComplianceAgent(consent_to_give=True)
    execution_history = MockExecutionHistory()
    orchestrator = build_agent_system(
        command_runner=mock_runner,
        config=config,
        consent_service=consent_service,
        execution_history=execution_history,
        parser=MockAIInterpreter()
    )
    command = "whois google.com"

    # Act
    await orchestrator.execute(command)

    # Assert
    log_file = "logs/install-whois.log"
    assert os.path.exists(log_file)
    with open(log_file, 'r') as f:
        log_content = f.read()
    assert "installing whois..." in log_content
    assert "some warning" in log_content


@pytest.mark.asyncio
async def test_dry_run_flag(cleanup_files):
    """
    Tests that the --dry-run flag prevents execution.
    """
    # Arrange
    mock_runner = MockCommandRunner()
    config = Config(dry_run=True)
    consent_service = MockSecurityComplianceAgent(consent_to_give=True)
    execution_history = MockExecutionHistory()
    orchestrator = build_agent_system(
        command_runner=mock_runner,
        config=config,
        consent_service=consent_service,
        execution_history=execution_history,
        parser=MockAIInterpreter()
    )
    command = "whois google.com"

    # Act
    result = await orchestrator.execute(command)

    # Assert
    assert result.success is True
    assert "Dry run: command not executed" in result.output
    assert mock_runner.call_count == 0


@pytest.mark.asyncio
async def test_end_to_end_ping_command(cleanup_files):
    """
    Tests the end-to-end flow for a system command like 'ping'.
    """
    # Arrange
    mock_runner = MockCommandRunner({
        "ping -c 4 google.com": {"returncode": 0, "stdout": "64 bytes from ..."}
    })
    config = Config(allow_system_install=True)
    consent_service = MockSecurityComplianceAgent(consent_to_give=True)
    execution_history = MockExecutionHistory()
    orchestrator = build_agent_system(
        command_runner=mock_runner,
        config=config,
        consent_service=consent_service,
        execution_history=execution_history,
        parser=MockAIInterpreter()
    )
    command = "ping -c 4 google.com"

    # Act
    result = await orchestrator.execute(command)

    # Assert
    assert result.success is True
    assert result.error is None
    assert "64 bytes from" in result.output
    assert result.command.tool_name == "ping"
