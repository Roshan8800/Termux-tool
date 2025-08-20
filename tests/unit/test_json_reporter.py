import pytest
import json
import os
from datetime import datetime
from termux_cyber_framework.adapters.report_generator.json_reporter import JsonReporter
from termux_cyber_framework.core.domain.models import ExecutionResult, Command, Error

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

def test_json_reporter_creates_files(tmp_path, execution_result):
    # Arrange
    reporter = JsonReporter(reports_dir=str(tmp_path))

    # Act
    paths = reporter.prepare_report_paths(execution_result.command.tool_name)
    reporter.generate(execution_result, paths)

    # Assert
    assert os.path.exists(paths.summary_file)
    assert os.path.exists(paths.output_log_file)

    with open(paths.summary_file, 'r') as f:
        summary_data = json.load(f)
    assert summary_data["success"] is True

    with open(paths.output_log_file, 'r') as f:
        log_content = f.read()
    assert "Test output" in log_content
