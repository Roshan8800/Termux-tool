import pytest
import os
import asyncio
from glob import glob
from termux_cyber_framework.adapters.cli.main import build_use_case

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

@pytest.mark.asyncio
async def test_end_to_end_whois_command(cleanup_files):
    """
    Tests the full end-to-end flow with a real command ('whois google.com').
    This test verifies that the command is executed and that log and report
    files are created correctly on the filesystem.
    """
    # Arrange
    # Build the full use case with all real adapters
    use_case = build_use_case()
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
