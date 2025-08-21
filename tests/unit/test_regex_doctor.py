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

def test_doctor_detects_and_proposes_fix(doctor_rules):
    # Arrange
    error_output = "ModuleNotFoundError: No module named 'requests'"
    command = Command(tool_name="test", args=[], raw_command="test")
    error = Error(message=error_output)

    mock_runner = MockCommandRunner()
    adapter = RegexDoctorAdapter(rules_path=doctor_rules, command_runner=mock_runner)

    # Act
    remediations = adapter.diagnose(error, command)

    # Assert
    assert len(remediations) == 1
    assert "The 'requests' Python module is not installed" in remediations[0].description
    assert remediations[0].command.tool_name == "pip"
    assert remediations[0].command.args == ["install", "requests"]
    assert mock_runner.call_count == 0

def test_doctor_no_match(doctor_rules):
    # Arrange
    error_output = "Some other error"
    command = Command(tool_name="test", args=[], raw_command="test")
    error = Error(message=error_output)

    mock_runner = MockCommandRunner()
    adapter = RegexDoctorAdapter(rules_path=doctor_rules, command_runner=mock_runner)

    # Act
    remediations = adapter.diagnose(error, command)

    # Assert
    assert len(remediations) == 0
