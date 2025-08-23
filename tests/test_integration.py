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
    yield
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
    """
    mock_runner = MockCommandRunner({
        "pkg install whois -y": {"returncode": 0, "stdout": "whois installed"},
        "whois google.com": {"returncode": 0, "stdout": "Registrant Organization: Google LLC"}
    })
    config = Config(allow_system_install=True)
    consent_service = MockSecurityComplianceAgent(consent_to_give=True)
    execution_history = MockExecutionHistory()
    agent_system = build_agent_system(
        command_runner=mock_runner,
        config=config,
        consent_service=consent_service,
        execution_history=execution_history,
        parser=MockAIInterpreter()
    )
    orchestrator = agent_system["orchestrator"]
    command = "whois google.com"
    result = await orchestrator.execute(command)

    assert result.success is True
    assert "Google LLC" in result.output

@pytest.mark.skip(reason="This test makes real API calls and is disabled to avoid credential/quota issues in CI.")
@pytest.mark.asyncio
async def test_end_to_end_with_real_ai(cleanup_files):
    """
    Tests the full end-to-end flow with the real AI interpreter.
    """
    mock_runner = MockCommandRunner({
        "nmap -sV example.com": {"returncode": 0, "stdout": "Nmap scan report for example.com"}
    })
    config = Config(allow_system_install=True)
    consent_service = MockSecurityComplianceAgent(consent_to_give=True)
    execution_history = MockExecutionHistory()
    agent_system = build_agent_system(
        command_runner=mock_runner,
        config=config,
        consent_service=consent_service,
        execution_history=execution_history
    )
    orchestrator = agent_system["orchestrator"]
    command = "scan example.com with nmap"
    result = await orchestrator.execute(command)
    assert result.success is True
    assert result.command.tool_name == "nmap"


@pytest.mark.asyncio
async def test_end_to_end_git_install_command(cleanup_files, cleanup_cloned_tools):
    """
    Tests the full end-to-end flow for a tool installed via Git.
    """
    mock_runner = MockCommandRunner({
        "git clone https://github.com/sqlmapproject/sqlmap.git tools/sqlmap": {"returncode": 0},
        "python3 tools/sqlmap/sqlmap.py --version --batch --threads 1": {"returncode": 0, "stdout": "1.8.3"}
    })
    config = Config(allow_system_install=True)
    consent_service = MockSecurityComplianceAgent(consent_to_give=True)
    execution_history = MockExecutionHistory()
    agent_system = build_agent_system(
        command_runner=mock_runner,
        config=config,
        consent_service=consent_service,
        execution_history=execution_history,
        parser=MockAIInterpreter()
    )
    orchestrator = agent_system["orchestrator"]
    command = "sqlmap --version"
    result = await orchestrator.execute(command)
    assert result.success is True
    assert re.search(r"\d+\.\d+", result.output)


@pytest.mark.asyncio
async def test_system_install_disallowed(cleanup_files, monkeypatch):
    """
    Tests that a system-level installation is blocked when disallowed by policy.
    """
    monkeypatch.setattr("shutil.which", lambda x: None)
    mock_runner = MockCommandRunner()
    config = Config(allow_system_install=False)
    consent_service = MockSecurityComplianceAgent(consent_to_give=True)
    execution_history = MockExecutionHistory()
    agent_system = build_agent_system(
        command_runner=mock_runner,
        config=config,
        consent_service=consent_service,
        execution_history=execution_history,
        parser=MockAIInterpreter()
    )
    orchestrator = agent_system["orchestrator"]
    command = "whois google.com"
    result = await orchestrator.execute(command)
    assert result.success is False
    assert "Failed to install tool 'whois'" in result.error.message


@pytest.mark.asyncio
async def test_install_logging(cleanup_files, monkeypatch):
    """
    Tests that installation output is logged correctly.
    """
    def mock_which(cmd):
        if cmd == "whois":
            return None
        return f"/usr/bin/{cmd}"
    monkeypatch.setattr("shutil.which", mock_which)
    monkeypatch.setattr("os.geteuid", lambda: 1000)
    mock_runner = MockCommandRunner({
        "sudo apt-get update": {"returncode": 0},
        "sudo apt-get install whois -y": {"returncode": 0, "stdout": "installing whois...", "stderr": "some warning"},
        "whois google.com": {"returncode": 0, "stdout": "Registrant Organization: Google LLC"}
    })
    config = Config(allow_system_install=True)
    consent_service = MockSecurityComplianceAgent(consent_to_give=True)
    execution_history = MockExecutionHistory()
    agent_system = build_agent_system(
        command_runner=mock_runner,
        config=config,
        consent_service=consent_service,
        execution_history=execution_history,
        parser=MockAIInterpreter()
    )
    orchestrator = agent_system["orchestrator"]
    command = "whois google.com"
    await orchestrator.execute(command)
    log_file = "logs/install-whois.log"
    assert os.path.exists(log_file)
    with open(log_file, 'r') as f:
        log_content = f.read()
    assert "installing whois..." in log_content


@pytest.mark.asyncio
async def test_dry_run_flag(cleanup_files):
    """
    Tests that the --dry-run flag prevents execution.
    """
    mock_runner = MockCommandRunner()
    config = Config(dry_run=True)
    consent_service = MockSecurityComplianceAgent(consent_to_give=True)
    execution_history = MockExecutionHistory()
    agent_system = build_agent_system(
        command_runner=mock_runner,
        config=config,
        consent_service=consent_service,
        execution_history=execution_history,
        parser=MockAIInterpreter()
    )
    orchestrator = agent_system["orchestrator"]
    command = "whois google.com"
    result = await orchestrator.execute(command)
    assert result.success is True
    assert "Dry run: command not executed" in result.output
    assert mock_runner.call_count == 0


@pytest.mark.asyncio
async def test_end_to_end_ping_command(cleanup_files):
    """
    Tests the end-to-end flow for a system command like 'ping'.
    """
    mock_runner = MockCommandRunner({
        "ping -c 4 google.com": {"returncode": 0, "stdout": "64 bytes from ..."}
    })
    config = Config(allow_system_install=True)
    consent_service = MockSecurityComplianceAgent(consent_to_give=True)
    execution_history = MockExecutionHistory()
    agent_system = build_agent_system(
        command_runner=mock_runner,
        config=config,
        consent_service=consent_service,
        execution_history=execution_history,
        parser=MockAIInterpreter()
    )
    orchestrator = agent_system["orchestrator"]
    command = "ping -c 4 google.com"
    result = await orchestrator.execute(command)
    assert result.success is True
    assert "64 bytes from" in result.output
