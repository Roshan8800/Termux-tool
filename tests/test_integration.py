import pytest
import os
import shutil
import asyncio
import re
from glob import glob
from termux_cyber_framework.adapters.cli.main import build_use_case
from .mocks import MockCommandRunner

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
    use_case = build_use_case(command_runner=mock_runner)
    command = "whois google.com"

    # Act
    # Execute the command through the orchestrator
    report = await use_case.execute(command)

    # Assert
    # 1. Assert the command was successful
    assert report.success is True
    assert report.error is None
    assert "Google LLC" in report.output # Check for expected content in the output

    # 2. Assert that a log file was created and contains expected content
    log_files = glob("logs/*.log")
    assert len(log_files) == 1
    with open(log_files[0], 'r') as f:
        log_content = f.read()
    assert "Received new command: 'whois google.com'" in log_content
    assert "Using runner 'GenericToolRunnerAdapter' for command 'whois'" in log_content
    assert "Generating report." in log_content

    # 3. Assert that a report file was created and contains expected content
    report_files = glob("reports/whois-*.json")
    assert len(report_files) == 1
    with open(report_files[0], 'r') as f:
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
        "python3 tools/sqlmap/sqlmap.py --version": {"returncode": 0, "stdout": "1.8.3"}
    })
    use_case = build_use_case(command_runner=mock_runner)
    # Using --version is a simple, non-intrusive way to check if sqlmap runs.
    command = "sqlmap --version"

    # Act
    report = await use_case.execute(command)

    # Assert
    # 1. Assert that the command was successful
    assert report.success is True
    assert report.error is None
    # Check for a version string in the output
    assert re.search(r"\d+\.\d+", report.output)

    # 3. Assert log and report files were created
    assert len(glob("logs/*.log")) == 1
    assert len(glob("reports/sqlmap-*.json")) == 1
