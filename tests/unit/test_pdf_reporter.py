import pytest
import os
from unittest.mock import MagicMock
from termux_cyber_framework.adapters.report_generator.pdf_reporter import PdfReporter
from termux_cyber_framework.core.domain.models import ExecutionResult, Command, RunPaths

@pytest.fixture
def mock_file_manager():
    return MagicMock()

@pytest.fixture
def pdf_reporter(mock_file_manager):
    return PdfReporter(mock_file_manager)

@pytest.fixture
def successful_result():
    command = Command(tool_name="nmap", args=["-sV", "localhost"], raw_command="scan localhost")
    return ExecutionResult(
        command=command,
        success=True,
        output="Nmap scan report for localhost...",
        ai_advice="Consider running a vulnerability scan next."
    )

@pytest.fixture
def run_paths(tmp_path):
    run_dir = tmp_path / "reports"
    run_dir.mkdir()
    return RunPaths(run_dir=run_dir, base_filename="test_run_pdf")

def test_generate_pdf_report(pdf_reporter, successful_result, run_paths):
    # Act
    report_path = pdf_reporter.generate(successful_result, run_paths)

    # Assert
    expected_path = os.path.join(run_paths.run_dir, "test_run_pdf.pdf")

    # 1. Check if the returned path is correct
    assert report_path == expected_path

    # 2. Check if the file actually exists
    assert os.path.exists(expected_path)

    # 3. Check if the file is not empty (i.e., some content was written)
    assert os.path.getsize(expected_path) > 0
