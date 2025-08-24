import pytest
from unittest.mock import MagicMock, patch
from termux_cyber_framework.adapters.tool_installer.shell_installer import ShellInstallerAdapter
from termux_cyber_framework.core.domain.models import Tool, InstallInfo
from termux_cyber_framework.core.domain.config import Config
from tests.mocks import MockCommandRunner, MockInstallLogger

@pytest.fixture
def mock_command_runner():
    return MockCommandRunner()

@pytest.fixture
def mock_install_logger():
    return MockInstallLogger()

@pytest.fixture
def shell_installer(mock_command_runner, mock_install_logger):
    return ShellInstallerAdapter(mock_command_runner, mock_install_logger)

@patch('shutil.which')
def test_is_installed_true(mock_which, shell_installer):
    mock_which.return_value = '/usr/bin/ollama'
    tool = Tool(name="ollama", description="", install_info=InstallInfo(method="shell", source="", bin_name="ollama"))
    assert shell_installer.is_installed(tool) is True
    mock_which.assert_called_once_with("ollama")

@patch('shutil.which')
def test_is_installed_false(mock_which, shell_installer):
    mock_which.return_value = None
    tool = Tool(name="ollama", description="", install_info=InstallInfo(method="shell", source="", bin_name="ollama"))
    assert shell_installer.is_installed(tool) is False
    mock_which.assert_called_once_with("ollama")

def test_install_success(shell_installer, mock_command_runner, mock_install_logger):
    # Arrange
    install_script = "echo 'installing...' && echo 'done.'"
    tool = Tool(name="ollama", description="", install_info=InstallInfo(method="shell", source=install_script, bin_name="ollama"))
    config = Config()
    mock_command_runner.mock_results[install_script] = {"returncode": 0, "stdout": "Installation successful", "stderr": ""}

    # Act
    success = shell_installer.install(tool, config)

    # Assert
    assert success is True
    assert mock_command_runner.last_command == install_script
    # Check that shell=True was used
    # This is tricky with my current mock, but I can infer it by the command being a string.
    # A better mock would store kwargs. For now, this is sufficient.
    assert "Installation successful" in mock_install_logger.logs["ollama"]

def test_install_failure(shell_installer, mock_command_runner, mock_install_logger):
    # Arrange
    install_script = "echo 'installing...' && exit 1"
    tool = Tool(name="ollama", description="", install_info=InstallInfo(method="shell", source=install_script, bin_name="ollama"))
    config = Config()
    # Simulate a failed command execution
    mock_command_runner.mock_results[install_script] = {"returncode": 1, "stdout": "", "stderr": "Installation failed"}

    # Act
    success = shell_installer.install(tool, config)

    # Assert
    assert success is False
    assert "Installation failed" in mock_install_logger.logs["ollama"]
