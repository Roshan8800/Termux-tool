import pytest
from unittest.mock import MagicMock
from termux_cyber_framework.agents.system_resource_agent import SystemResourceAgent
from tests.mocks import MockCommandRunner

def test_get_available_storage_success():
    """
    Tests that available storage is correctly parsed and converted to MB
    on a successful command run.
    """
    # Arrange
    # Mock output for `df -k .` where available space is 30000000 KB
    mock_output = """Filesystem     1K-blocks     Used Available Use% Mounted on
/dev/root      60000000 30000000 30000000  50% /
"""
    mock_runner = MockCommandRunner({
        "df -k .": {"returncode": 0, "stdout": mock_output}
    })
    agent = SystemResourceAgent(command_runner=mock_runner)

    # Act
    available_mb = agent.get_available_storage_mb()

    # Assert
    # 30000000 KB / 1024 = 29296.875 MB
    assert available_mb == 29296

def test_get_available_storage_failure_on_error():
    """
    Tests that the method returns None if the command fails.
    """
    # Arrange
    mock_runner = MockCommandRunner({
        "df -k .": {"returncode": 1, "stderr": "df: command failed"}
    })
    agent = SystemResourceAgent(command_runner=mock_runner)

    # Act
    available_mb = agent.get_available_storage_mb()

    # Assert
    assert available_mb is None

def test_get_available_storage_malformed_output():
    """
    Tests that the method returns None if the output is not as expected.
    """
    # Arrange
    mock_output = "This is not valid df output"
    mock_runner = MockCommandRunner({
        "df -k .": {"returncode": 0, "stdout": mock_output}
    })
    agent = SystemResourceAgent(command_runner=mock_runner)

    # Act
    available_mb = agent.get_available_storage_mb()

    # Assert
    assert available_mb is None
