import pytest
import json
import os
import unittest
from unittest.mock import MagicMock
from datetime import datetime
from termux_cyber_framework.adapters.report_generator.txt_reporter import TxtReporter
from termux_cyber_framework.core.domain.models import ExecutionResult, Command, Error
from termux_cyber_framework.agents.file_manager_agent import FileManagerAgent

@pytest.fixture
def execution_result():
    return ExecutionResult(
        command=Command(tool_name="test", args=[], raw_command="test"),
        success=True,
        output="Test output",
        error=None,
        start_time=datetime.now(),
        end_time=datetime.now()
    )

@pytest.fixture
def mock_file_manager():
    """Provides a mock FileManagerAgent."""
    # Create a mock that simulates file writing for verification
    mock = MagicMock(spec=FileManagerAgent)

    # We need to store what's "written" to verify it
    written_files = {}

    def write_file_side_effect(path, content):
        written_files[path] = content
        return True

    mock.write_file.side_effect = write_file_side_effect
    # Add a way to retrieve the written content for assertions
    mock.get_written_content = lambda path: written_files.get(path)

    return mock

def test_txt_reporter_creates_files(tmp_path, execution_result, mock_file_manager):
    # Arrange
    reporter = TxtReporter(file_manager=mock_file_manager, reports_dir=str(tmp_path))

    # Act
    paths = reporter.prepare_report_paths(execution_result.command.tool_name)
    reporter.generate(execution_result, paths)

    # Assert
    summary_file = os.path.join(paths.run_dir, f"{paths.base_filename}.txt")

    # Check that the file manager was called to write the files
    mock_file_manager.write_file.assert_any_call(summary_file, unittest.mock.ANY)
    mock_file_manager.write_file.assert_any_call(paths.output_log_file, "Test output")

    # Check the content of the summary file
    summary_content = mock_file_manager.get_written_content(summary_file)
    assert "Status: Success" in summary_content
    assert "Test output" in mock_file_manager.get_written_content(paths.output_log_file)
