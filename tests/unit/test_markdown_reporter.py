import pytest
import os
from unittest.mock import MagicMock
from termux_cyber_framework.adapters.report_generator.markdown_reporter import MarkdownReporter
from termux_cyber_framework.core.domain.models import ExecutionResult, Command, Error, RunPaths

@pytest.fixture
def mock_file_manager():
    return MagicMock()

@pytest.fixture
def markdown_reporter(mock_file_manager):
    return MarkdownReporter(mock_file_manager)

@pytest.fixture
def successful_result():
    command = Command(tool_name="nmap", args=["-sV", "localhost"], raw_command="scan localhost")
    return ExecutionResult(
        command=command,
        success=True,
        output="Nmap scan report...",
        ai_advice="Consider running a vulnerability scan next."
    )

@pytest.fixture
def failed_result():
    command = Command(tool_name="sqlmap", args=["-u", "test.com"], raw_command="sqlmap test.com")
    error = Error(message="SQL injection failed.", error_code=1, ai_analysis="The target may not be vulnerable.")
    return ExecutionResult(
        command=command,
        success=False,
        output="Some output before failure.",
        error=error
    )

@pytest.fixture
def run_paths(tmp_path):
    run_dir = tmp_path / "reports"
    run_dir.mkdir()
    return RunPaths(run_dir=run_dir, base_filename="test_run")

def test_generate_markdown_for_successful_result(markdown_reporter, successful_result, run_paths, mock_file_manager):
    # Act
    report_path = markdown_reporter.generate(successful_result, run_paths)

    # Assert
    expected_path = os.path.join(run_paths.run_dir, "test_run.md")
    assert report_path == expected_path

    # Check that write_file was called once
    mock_file_manager.write_file.assert_called_once()

    # Get the content that was written
    written_path, written_content = mock_file_manager.write_file.call_args[0]

    assert written_path == expected_path
    assert "# Execution Report" in written_content
    assert "## Command Details" in written_content
    assert "- **Tool:** `nmap`" in written_content
    assert "## Output" in written_content
    assert "```\nNmap scan report...\n```" in written_content
    assert "## AI Security Advisor" in written_content
    assert "> Consider running a vulnerability scan next." in written_content
    assert "Error Details" not in written_content

def test_generate_markdown_for_failed_result(markdown_reporter, failed_result, run_paths, mock_file_manager):
    # Act
    report_path = markdown_reporter.generate(failed_result, run_paths)

    # Assert
    expected_path = os.path.join(run_paths.run_dir, "test_run.md")
    assert report_path == expected_path

    # Get the content that was written
    written_path, written_content = mock_file_manager.write_file.call_args[0]

    assert written_path == expected_path
    assert "# Execution Report" in written_content
    assert "- **Status:** Failure" in written_content
    assert "## Error Details" in written_content
    assert "```\nSQL injection failed.\n```" in written_content
    assert "### AI Analysis" in written_content
    assert "> The target may not be vulnerable." in written_content
    assert "AI Security Advisor" not in written_content
