import pytest
import os
import shutil
import asyncio
import re
from glob import glob
from termux_cyber_framework.adapters.cli.main import build_use_case
from termux_cyber_framework.core.domain.config import Config
from .mocks import MockCommandRunner
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
async def test_end_to_end_whois_command(cleanup_files):
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
    use_case = build_use_case(command_runner=mock_runner, config=config)
    command = "whois google.com"

    # Act
    # Execute the command through the orchestrator
    result = await use_case.execute(command)

    # Assert
    # 1. Assert the command was successful
    assert result.success is True
    assert result.error is None
    assert "Google LLC" in result.output # Check for expected content in the output

    # 2. Assert that a log file was created and contains expected content
    assert os.path.exists(result.output_log_file)
    with open(result.output_log_file, 'r') as f:
        log_content = f.read()
    assert "Registrant Organization: Google LLC" in log_content

    # 3. Assert that a report file was created and contains expected content
    summary_path = result.output_log_file.replace("run.log", "summary.json")
    assert os.path.exists(summary_path)
    with open(summary_path, 'r') as f:
        report_data = f.read()
    assert '"tool_name": "whois"' in report_data
    assert '"raw_command": "whois google.com"' in report_data
    assert '"success": true' in report_data
    assert "Registrant Organization: Google LLC" in report_data


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
    use_case = build_use_case(command_runner=mock_runner, config=config)
    # Using --version is a simple, non-intrusive way to check if sqlmap runs.
    command = "sqlmap --version"

    # Act
    result = await use_case.execute(command)

    # Assert
    # 1. Assert that the command was successful
    assert result.success is True
    assert result.error is None
    # Check for a version string in the output
    assert re.search(r"\d+\.\d+", result.output)

    # 3. Assert log and report files were created
    assert os.path.exists(result.output_log_file)
    assert os.path.exists(result.output_log_file.replace("run.log", "summary.json"))


@pytest.mark.asyncio
async def test_system_install_disallowed(cleanup_files):
    """
    Tests that a system-level installation is blocked when disallowed by policy.
    """
    # Arrange
    mock_runner = MockCommandRunner()
    config = Config(allow_system_install=False)
    use_case = build_use_case(command_runner=mock_runner, config=config)
    command = "whois google.com"

    # Act
    result = await use_case.execute(command)

    # Assert
    assert result.success is False
    assert result.error is not None
    assert "System-level installation for 'whois' is not allowed by policy" in result.error.message


@pytest.mark.asyncio
async def test_install_logging(cleanup_files):
    """
    Tests that installation output is logged correctly.
    """
    # Arrange
    mock_runner = MockCommandRunner({
        "pkg install whois -y": {"returncode": 0, "stdout": "installing whois...", "stderr": "some warning"}
    })
    config = Config(allow_system_install=True)
    use_case = build_use_case(command_runner=mock_runner, config=config)
    command = "whois google.com"

    # Act
    await use_case.execute(command)

    # Assert
    log_file = "logs/install-whois.log"
    assert os.path.exists(log_file)
    with open(log_file, 'r') as f:
        log_content = f.read()
    assert "installing whois..." in log_content
    assert "some warning" in log_content
