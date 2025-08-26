import pytest
import subprocess
from unittest.mock import MagicMock, AsyncMock, patch
from termux_cyber_framework.agents.auto_editor_agent import AutoEditorAgent
from termux_cyber_framework.agents.file_manager_agent import FileManagerAgent
from termux_cyber_framework.core.use_cases.ports import AIProcessingPort
from termux_cyber_framework.core.domain.models import Command, Error

@pytest.fixture
def mock_ai_service():
    """Provides a mock AIProcessingPort."""
    service = MagicMock(spec=AIProcessingPort)
    service.generate_script_patch = AsyncMock()
    return service

@pytest.fixture
def mock_file_manager():
    """Provides a mock FileManagerAgent."""
    return MagicMock(spec=FileManagerAgent)

@pytest.fixture
def agent(mock_ai_service, mock_file_manager):
    """Provides an AutoEditorAgent instance with mocked dependencies."""
    return AutoEditorAgent(ai_service=mock_ai_service, file_manager=mock_file_manager)

@pytest.mark.asyncio
@patch('subprocess.run')
async def test_patch_script_success(mock_subprocess_run, agent, mock_ai_service, mock_file_manager):
    # Arrange
    script_path = "/path/to/script.py"
    script_content = "print('hello world')"
    error = Error(message="SyntaxError: invalid syntax")
    command = Command(tool_name="python", args=[script_path], raw_command="python /path/to/script.py")
    patch_diff = "--- a/script.py\n+++ b/script.py\n@@ -1 +1 @@\n-print('hello world')\n+print('hello, world')"

    mock_file_manager.read_file.return_value = script_content
    mock_ai_service.generate_script_patch.return_value = patch_diff
    mock_subprocess_run.return_value = MagicMock(returncode=0)

    # Act
    success = await agent.patch_script(script_path, error, command)

    # Assert
    assert success is True
    mock_file_manager.read_file.assert_called_once_with(script_path)
    mock_ai_service.generate_script_patch.assert_called_once_with(script_content, error, command)
    mock_subprocess_run.assert_called_once_with(
        ['patch', script_path],
        input=patch_diff,
        text=True,
        capture_output=True,
        check=True
    )

@pytest.mark.asyncio
async def test_patch_script_no_content(agent, mock_file_manager):
    # Arrange
    script_path = "/path/to/script.py"
    mock_file_manager.read_file.return_value = None  # Simulate file not found or empty

    # Act
    success = await agent.patch_script(script_path, Error(message=""), Command(tool_name="", raw_command=""))

    # Assert
    assert success is False

@pytest.mark.asyncio
async def test_patch_script_no_patch_generated(agent, mock_ai_service, mock_file_manager):
    # Arrange
    script_path = "/path/to/script.py"
    mock_file_manager.read_file.return_value = "content"
    mock_ai_service.generate_script_patch.return_value = ""  # AI returns no patch

    # Act
    success = await agent.patch_script(script_path, Error(message=""), Command(tool_name="", raw_command=""))

    # Assert
    assert success is False

@pytest.mark.asyncio
@patch('subprocess.run')
async def test_patch_script_patching_fails(mock_subprocess_run, agent, mock_ai_service, mock_file_manager):
    # Arrange
    script_path = "/path/to/script.py"
    mock_file_manager.read_file.return_value = "content"
    mock_ai_service.generate_script_patch.return_value = "a patch"
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(1, "patch")

    # Act
    success = await agent.patch_script(script_path, Error(message=""), Command(tool_name="", raw_command=""))

    # Assert
    assert success is False
