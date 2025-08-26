import pytest
import os
import shutil
import asyncio
import re
from glob import glob
from unittest.mock import MagicMock
from termux_cyber_framework.adapters.cli.main import build_agent_system
from termux_cyber_framework.core.domain.config import Config
from .mocks import MockCommandRunner, MockSecurityComplianceAgent, MockExecutionHistory, MockAIInterpreter, MockInstallLogger
from termux_cyber_framework.services.pentestgpt_service_manager import PentestGptServiceManager

# Fixture to clean up generated files
@pytest.fixture(scope="function")
def cleanup_files():
    """Cleans up log and report files after a test run."""
    yield
    # ... (cleanup logic)

# Fixture to clean up cloned tools
@pytest.fixture(scope="function")
def cleanup_cloned_tools():
    """Cleans up cloned tool directories."""
    yield
    # ... (cleanup logic)

# Central fixture to build the agent system with mocks
@pytest.fixture
def mocked_agent_system(monkeypatch, request):
    """
    Builds the agent system with specified mocks.
    This uses pytest's indirect parametrization.
    """
    # Default mocks
    mocks = {
        "CommandRunner": MockCommandRunner(),
        "SecurityComplianceAgent": MockSecurityComplianceAgent(consent_to_give=True),
        "ExecutionHistory": MockExecutionHistory(),
        "MasterAIInterpreter": MockAIInterpreter(),
        "AIInterpreter": MockAIInterpreter(),
        "PentestGptServiceManager": MagicMock(spec=PentestGptServiceManager),
        "Config": Config()
    }

    # Update mocks with any provided by the test function via decorator
    if hasattr(request, "param"):
        mocks.update(request.param)

    # Apply patches
    monkeypatch.setattr("termux_cyber_framework.adapters.cli.main.CommandRunner", lambda: mocks["CommandRunner"])
    monkeypatch.setattr("termux_cyber_framework.adapters.cli.main.SecurityComplianceAgent", lambda: mocks["SecurityComplianceAgent"])
    monkeypatch.setattr("termux_cyber_framework.adapters.cli.main.ExecutionHistory", lambda: mocks["ExecutionHistory"])
    # The real CentralAIService is used, so we don't mock it unless specified.
    # We now mock the agents that *use* the service.
    monkeypatch.setattr("termux_cyber_framework.adapters.cli.main.MasterAIInterpreter", lambda ai_service, config_manager, console: mocks["MasterAIInterpreter"])
    monkeypatch.setattr("termux_cyber_framework.adapters.cli.main.AIInterpreter", lambda ai_service, tool_catalog: mocks["AIInterpreter"])
    monkeypatch.setattr("termux_cyber_framework.adapters.cli.main.PentestGptServiceManager", lambda command_runner: mocks["PentestGptServiceManager"])
    if mocks.get("InstallLogger"):
        mock_logger_instance = MockInstallLogger()
        mocks["InstallLogger"] = mock_logger_instance
        monkeypatch.setattr("termux_cyber_framework.adapters.cli.main.InstallLogger", lambda: mock_logger_instance)

    agent_system = build_agent_system(config=mocks["Config"])
    agent_system["mocks"] = mocks
    return agent_system


# ... (rest of the tests are unchanged)
@pytest.mark.asyncio
@pytest.mark.parametrize("mocked_agent_system", [{"CommandRunner": MockCommandRunner({"pkg install whois -y": {"returncode": 0, "stdout": "whois installed"},"whois google.com": {"returncode": 0, "stdout": "Registrant Organization: Google LLC"}}), "Config": Config(allow_system_install=True)}], indirect=True)
async def test_end_to_end_whois_command_with_mock_ai(mocked_agent_system, cleanup_files):
    orchestrator = mocked_agent_system["orchestrator"]
    result = await orchestrator.handle_input("whois google.com")
    assert result.success is True
    assert "Google LLC" in result.output

@pytest.mark.asyncio
@pytest.mark.parametrize("mocked_agent_system", [{"CommandRunner": MockCommandRunner({"git clone https://github.com/sqlmapproject/sqlmap.git tools/sqlmap": {"returncode": 0},"python3 tools/sqlmap/sqlmap.py --version --batch --threads 1": {"returncode": 0, "stdout": "1.8.3"}}), "Config": Config(allow_system_install=True)}], indirect=True)
async def test_end_to_end_git_install_command(mocked_agent_system, cleanup_files, cleanup_cloned_tools):
    orchestrator = mocked_agent_system["orchestrator"]
    result = await orchestrator.handle_input("sqlmap --version")
    assert result.success is True
    assert re.search(r"\d+\.\d+", result.output)

@pytest.mark.asyncio
@pytest.mark.parametrize("mocked_agent_system", [{"Config": Config(allow_system_install=False)}], indirect=True)
async def test_system_install_disallowed(mocked_agent_system, cleanup_files, monkeypatch):
    monkeypatch.setattr("shutil.which", lambda x: None)
    orchestrator = mocked_agent_system["orchestrator"]
    result = await orchestrator.handle_input("whois google.com")
    assert result.success is False
    assert "System-level installation for 'whois' is not allowed by policy" in result.error.message

@pytest.mark.asyncio
@pytest.mark.parametrize("mocked_agent_system", [{"CommandRunner": MockCommandRunner({"sudo apt-get update": {"returncode": 0},"sudo apt-get install whois -y": {"returncode": 0, "stdout": "installing whois...", "stderr": "some warning"},"whois google.com": {"returncode": 0, "stdout": "Registrant Organization: Google LLC"}}), "Config": Config(allow_system_install=True), "InstallLogger": "tests.mocks.MockInstallLogger"}], indirect=True)
async def test_install_logging(mocked_agent_system, cleanup_files, monkeypatch):
    monkeypatch.setattr("shutil.which", lambda cmd: None if cmd == "whois" else f"/usr/bin/{cmd}")
    monkeypatch.setattr("os.geteuid", lambda: 1000)
    orchestrator = mocked_agent_system["orchestrator"]
    mock_install_logger = mocked_agent_system["mocks"]["InstallLogger"]
    await orchestrator.handle_input("whois google.com")
    assert "whois" in mock_install_logger.logs
    assert any("installing whois..." in log for log in mock_install_logger.logs["whois"])

@pytest.mark.asyncio
@pytest.mark.parametrize("mocked_agent_system", [{"Config": Config(dry_run=True), "CommandRunner": MockCommandRunner()}], indirect=True)
async def test_dry_run_flag(mocked_agent_system, cleanup_files):
    orchestrator = mocked_agent_system["orchestrator"]
    mock_runner = mocked_agent_system["mocks"]["CommandRunner"]
    result = await orchestrator.handle_input("whois google.com")
    assert result.success is True
    assert "Dry run: command not executed" in result.output
    assert mock_runner.call_count == 0

@pytest.mark.asyncio
@pytest.mark.parametrize("mocked_agent_system", [{"CommandRunner": MockCommandRunner({"ping -c 4 google.com": {"returncode": 0, "stdout": "64 bytes from ..."}})}], indirect=True)
async def test_end_to_end_ping_command(mocked_agent_system, cleanup_files):
    orchestrator = mocked_agent_system["orchestrator"]
    result = await orchestrator.handle_input("ping -c 4 google.com")
    assert result.success is True
    assert "64 bytes from" in result.output
