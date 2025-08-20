import pytest
import json
from termux_cyber_framework.adapters.doctor.regex_doctor import RegexDoctorAdapter
from termux_cyber_framework.core.domain.models import ExecutionResult, Command, Error
from tests.mocks import MockCommandRunner

@pytest.fixture
def doctor_rules(tmp_path):
    rules = [
        {
            "id": "openssl_missing",
            "pattern": "openssl/ssl.h: No such file",
            "explain": "The OpenSSL development headers are missing.",
            "commands": ["pkg install -y openssl"],
            "require_confirm": False
        },
        {
            "id": "python_requests_missing",
            "pattern": "No module named 'requests'",
            "explain": "The 'requests' Python module is not installed.",
            "commands": ["pip install requests"],
            "require_confirm": True
        }
    ]
    rules_path = tmp_path / "doctor_rules.json"
    with open(rules_path, "w") as f:
        json.dump(rules, f)
    return str(rules_path)

@pytest.mark.asyncio
async def test_doctor_detects_and_applies_fix(doctor_rules):
    # Arrange
    error_output = "fatal error: openssl/ssl.h: No such file or directory"
    result = ExecutionResult(
        command=Command(tool_name="test", args=[], raw_command="test"),
        success=False,
        output="",
        error=Error(message=error_output),
        start_time="2025-08-20T12:00:00Z",
        end_time="2025-08-20T12:00:01Z"
    )
    mock_runner = MockCommandRunner()
    adapter = RegexDoctorAdapter(rules_path=doctor_rules, command_runner=mock_runner)

    # Act
    fixes = await adapter.detect_and_fix(result)

    # Assert
    assert len(fixes) == 1
    assert fixes[0]["id"] == "openssl_missing"
    assert fixes[0]["status"] == "applied"
    assert mock_runner.last_command == ["pkg", "install", "-y", "openssl"]

@pytest.mark.asyncio
async def test_doctor_detects_and_proposes_fix(doctor_rules):
    # Arrange
    error_output = "ModuleNotFoundError: No module named 'requests'"
    result = ExecutionResult(
        command=Command(tool_name="test", args=[], raw_command="test"),
        success=False,
        output="",
        error=Error(message=error_output),
        start_time="2025-08-20T12:00:00Z",
        end_time="2025-08-20T12:00:01Z"
    )
    mock_runner = MockCommandRunner()
    adapter = RegexDoctorAdapter(rules_path=doctor_rules, command_runner=mock_runner)

    # Act
    fixes = await adapter.detect_and_fix(result)

    # Assert
    assert len(fixes) == 1
    assert fixes[0]["id"] == "python_requests_missing"
    assert fixes[0]["status"] == "pending_user_confirm"
    assert mock_runner.call_count == 0

@pytest.mark.asyncio
async def test_doctor_no_match(doctor_rules):
    # Arrange
    error_output = "Some other error"
    result = ExecutionResult(
        command=Command(tool_name="test", args=[], raw_command="test"),
        success=False,
        output="",
        error=Error(message=error_output),
        start_time="2025-08-20T12:00:00Z",
        end_time="2025-08-20T12:00:01Z"
    )
    mock_runner = MockCommandRunner()
    adapter = RegexDoctorAdapter(rules_path=doctor_rules, command_runner=mock_runner)

    # Act
    fixes = await adapter.detect_and_fix(result)

    # Assert
    assert len(fixes) == 0

@pytest.fixture
def doctor_rules_multiple(tmp_path):
    rules = [
        {
            "id": "openssl_missing",
            "pattern": "openssl/ssl.h: No such file",
            "explain": "The OpenSSL development headers are missing.",
            "commands": ["pkg install -y openssl"],
            "require_confirm": False
        },
        {
            "id": "some_other_error",
            "pattern": "Some other error",
            "explain": "This is another error.",
            "commands": [],
            "require_confirm": True
        }
    ]
    rules_path = tmp_path / "doctor_rules.json"
    with open(rules_path, "w") as f:
        json.dump(rules, f)
    return str(rules_path)

@pytest.mark.asyncio
async def test_doctor_multiple_matches(doctor_rules_multiple):
    # Arrange
    error_output = "fatal error: openssl/ssl.h: No such file or directory\nSome other error"
    result = ExecutionResult(
        command=Command(tool_name="test", args=[], raw_command="test"),
        success=False,
        output="",
        error=Error(message=error_output),
        start_time="2025-08-20T12:00:00Z",
        end_time="2025-08-20T12:00:01Z"
    )
    mock_runner = MockCommandRunner()
    adapter = RegexDoctorAdapter(rules_path=doctor_rules_multiple, command_runner=mock_runner)

    # Act
    fixes = await adapter.detect_and_fix(result)

    # Assert
    assert len(fixes) == 2
    assert fixes[0]["id"] == "openssl_missing"
    assert fixes[1]["id"] == "some_other_error"

@pytest.mark.asyncio
async def test_doctor_match_in_output(doctor_rules):
    # Arrange
    output = "ModuleNotFoundError: No module named 'requests'"
    result = ExecutionResult(
        command=Command(tool_name="test", args=[], raw_command="test"),
        success=False,
        output=output,
        error=None,
        start_time="2025-08-20T12:00:00Z",
        end_time="2025-08-20T12:00:01Z"
    )
    mock_runner = MockCommandRunner()
    adapter = RegexDoctorAdapter(rules_path=doctor_rules, command_runner=mock_runner)

    # Act
    fixes = await adapter.detect_and_fix(result)

    # Assert
    assert len(fixes) == 1
    assert fixes[0]["id"] == "python_requests_missing"
