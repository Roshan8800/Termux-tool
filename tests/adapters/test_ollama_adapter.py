import pytest
import subprocess
from unittest.mock import MagicMock
from termux_cyber_framework.adapters.ollama_adapter import OllamaAdapter
from tests.mocks import MockCommandRunner

@pytest.fixture
def mock_command_runner():
    return MockCommandRunner()

@pytest.fixture
def ollama_adapter(mock_command_runner):
    return OllamaAdapter(mock_command_runner)

def test_start_server_when_not_running(ollama_adapter, mock_command_runner):
    # Arrange: Server is not running
    mock_command_runner.mock_results = {
        "pgrep -f ollama serve": {"returncode": 1, "exception": subprocess.CalledProcessError(1, "pgrep")}
    }

    # Act
    success = ollama_adapter.start_server()

    # Assert
    assert success is True
    assert "nohup ollama serve" in mock_command_runner.last_command

def test_start_server_when_already_running(ollama_adapter, mock_command_runner):
    # Arrange: Server is already running
    mock_command_runner.mock_results = {
        "pgrep -f ollama serve": {"returncode": 0, "stdout": "12345"}
    }

    # Act
    success = ollama_adapter.start_server()

    # Assert
    assert success is True
    # The 'run' command for starting the server should not have been called
    assert "nohup" not in str(mock_command_runner.last_command)

def test_is_server_running_true(ollama_adapter, mock_command_runner):
    # Arrange
    mock_command_runner.mock_results["pgrep -f ollama serve"] = {"returncode": 0, "stdout": "12345"}

    # Act & Assert
    assert ollama_adapter.is_server_running() is True

def test_is_server_running_false(ollama_adapter, mock_command_runner):
    # Arrange
    mock_command_runner.mock_results["pgrep -f ollama serve"] = {"returncode": 1, "exception": subprocess.CalledProcessError(1, "pgrep")}

    # Act & Assert
    assert ollama_adapter.is_server_running() is False

def test_pull_model_success(ollama_adapter, mock_command_runner):
    # Arrange
    mock_command_runner.mock_results["ollama pull llama3"] = {"returncode": 0, "stdout": "success"}

    # Act & Assert
    assert ollama_adapter.pull_model("llama3") is True
    assert mock_command_runner.last_command == ["ollama", "pull", "llama3"]

def test_pull_model_failure(ollama_adapter, mock_command_runner):
    # Arrange
    mock_command_runner.mock_results["ollama pull badmodel"] = {"returncode": 1, "exception": subprocess.CalledProcessError(1, "ollama")}

    # Act & Assert
    assert ollama_adapter.pull_model("badmodel") is False

def test_list_models_success(ollama_adapter, mock_command_runner):
    # Arrange
    mock_output = """NAME            ID              SIZE    MODIFIED
llama3:8b       703cf65e6a91    4.7 GB  11 days ago
gemma:2b        f0e096bbd6a1    1.7 GB  2 weeks ago
"""
    mock_command_runner.mock_results["ollama list"] = {"returncode": 0, "stdout": mock_output}

    # Act
    models = ollama_adapter.list_models()

    # Assert
    assert models == ["llama3:8b", "gemma:2b"]

def test_list_models_empty(ollama_adapter, mock_command_runner):
    # Arrange
    mock_output = "NAME            ID              SIZE    MODIFIED"
    mock_command_runner.mock_results["ollama list"] = {"returncode": 0, "stdout": mock_output}

    # Act
    models = ollama_adapter.list_models()

    # Assert
    assert models == []

def test_list_models_failure(ollama_adapter, mock_command_runner):
    # Arrange
    mock_command_runner.mock_results["ollama list"] = {"returncode": 1, "exception": subprocess.CalledProcessError(1, "ollama")}

    # Act
    models = ollama_adapter.list_models()

    # Assert
    assert models == []
