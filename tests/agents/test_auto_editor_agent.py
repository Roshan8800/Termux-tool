import pytest
from unittest.mock import patch, MagicMock, mock_open, AsyncMock

# Mock the genai module before it's imported by the agent
import sys
mock_genai = MagicMock()
sys.modules['google.generativeai'] = mock_genai

from termux_cyber_framework.agents.auto_editor_agent import AutoEditorAgent
from termux_cyber_framework.core.domain.models import Command, Error

@pytest.fixture
def agent():
    """Fixture to create an AutoEditorAgent with a mocked AI model."""
    agent = AutoEditorAgent(api_key="fake_key")
    agent.model = MagicMock()
    agent.model.generate_content_async = AsyncMock()
    return agent

@pytest.mark.asyncio
async def test_patch_script_success_python(agent):
    """Test successful patching of a Python script."""
    # Arrange
    script_path = "/path/to/test.py"
    original_content = "print 'hello'"
    patched_content = "print('hello')"
    error = Error(message="SyntaxError: Missing parentheses in call to 'print'")
    command = Command(tool_name="test.py", args=[], raw_command="test command")

    # Mock the AI response
    mock_response = MagicMock()
    mock_response.text = f"```python\n{patched_content}\n```"
    agent.model.generate_content_async.return_value = mock_response

    # Mock file operations
    with patch("builtins.open", mock_open(read_data=original_content)) as mock_file:
        # Act
        success = await agent.patch_script(script_path, error, command)

        # Assert
        assert success is True
        agent.model.generate_content_async.assert_called_once()
        mock_file.assert_called_with(script_path, 'w')
        mock_file().write.assert_called_once_with(patched_content)

@pytest.mark.asyncio
async def test_patch_script_invalid_python_syntax(agent):
    """Test that patching fails if the AI returns invalid Python syntax."""
    # Arrange
    script_path = "/path/to/test.py"
    original_content = "print 'hello'"
    invalid_patch = "print 'hello' again" # Still invalid syntax
    error = Error(message="SyntaxError")
    command = Command(tool_name="test.py", args=[], raw_command="test command")

    mock_response = MagicMock()
    mock_response.text = invalid_patch
    agent.model.generate_content_async.return_value = mock_response

    with patch("builtins.open", mock_open(read_data=original_content)):
        # Act
        success = await agent.patch_script(script_path, error, command)

        # Assert
        assert success is False

@pytest.mark.asyncio
async def test_patch_script_file_not_found(agent):
    """Test that patching fails if the script file doesn't exist."""
    # Arrange
    script_path = "/path/to/nonexistent.py"
    error = Error(message="Some error")
    command = Command(tool_name="nonexistent.py", args=[], raw_command="test command")

    with patch("builtins.open", mock_open()) as mock_file:
        mock_file.side_effect = FileNotFoundError

        # Act
        success = await agent.patch_script(script_path, error, command)

        # Assert
        assert success is False
        agent.model.generate_content_async.assert_not_called()

@pytest.mark.asyncio
async def test_patch_script_shell_success(agent):
    """Test successful patching of a shell script with shellcheck validation."""
    # Arrange
    script_path = "/path/to/test.sh"
    original_content = "echo hello"
    patched_content = "echo 'hello'"
    error = Error(message="Some error")
    command = Command(tool_name="test.sh", args=[], raw_command="test command")

    mock_response = MagicMock()
    mock_response.text = patched_content
    agent.model.generate_content_async.return_value = mock_response

    # Mock shellcheck subprocess
    mock_process = MagicMock()
    mock_process.returncode = 0 # 0 means success
    with patch("subprocess.run", return_value=mock_process) as mock_subprocess, \
         patch("builtins.open", mock_open(read_data=original_content)) as mock_file:
        # Act
        success = await agent.patch_script(script_path, error, command)

        # Assert
        assert success is True
        mock_subprocess.assert_called_once()
        mock_file().write.assert_called_once_with(patched_content)

@pytest.mark.asyncio
async def test_patch_script_shell_fail_validation(agent):
    """Test that patching fails if shellcheck finds critical errors."""
    # Arrange
    script_path = "/path/to/test.sh"
    original_content = "echo hello"
    patched_content = "ecoh 'hello'" # Typo
    error = Error(message="Some error")
    command = Command(tool_name="test.sh", args=[], raw_command="test command")

    mock_response = MagicMock()
    mock_response.text = patched_content
    agent.model.generate_content_async.return_value = mock_response

    mock_process = MagicMock()
    mock_process.returncode = 2 # 2 means error
    with patch("subprocess.run", return_value=mock_process), \
         patch("builtins.open", mock_open(read_data=original_content)) as mock_file:
        # Act
        success = await agent.patch_script(script_path, error, command)

        # Assert
        assert success is False
        mock_file().write.assert_not_called()
