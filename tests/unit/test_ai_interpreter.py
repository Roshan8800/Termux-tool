import pytest
from unittest.mock import AsyncMock, MagicMock
from termux_cyber_framework.adapters.command_parser.ai_interpreter import AIInterpreter
from termux_cyber_framework.core.domain.models import Command

@pytest.fixture
def mock_generative_model():
    """Fixture to mock the genai.GenerativeModel."""
    mock_model = MagicMock()
    # Mock the async method
    mock_model.generate_content_async = AsyncMock()
    return mock_model

@pytest.fixture
def ai_interpreter(tmp_path, mock_generative_model):
    """Fixture to create an AIInterpreter with a mocked model."""
    tool_catalog_path = tmp_path / "tool_catalog.json"
    with open(tool_catalog_path, "w") as f:
        f.write('[{"name": "nmap", "description": "Network scanner"}]')

    # Patch the genai.GenerativeModel to return our mock
    import termux_cyber_framework.adapters.command_parser.ai_interpreter as ai_interpreter_module
    original_generative_model = ai_interpreter_module.genai.GenerativeModel
    ai_interpreter_module.genai.GenerativeModel = MagicMock(return_value=mock_generative_model)

    interpreter = AIInterpreter(tool_catalog_path=str(tool_catalog_path), api_key="test_key")

    # Restore the original after the test
    yield interpreter
    ai_interpreter_module.genai.GenerativeModel = original_generative_model


@pytest.mark.asyncio
async def test_parse_command_success(ai_interpreter, mock_generative_model):
    # Arrange
    mock_response = MagicMock()
    mock_response.text = '{"tool": "nmap", "args": ["-sV", "localhost"]}'
    mock_generative_model.generate_content_async.return_value = mock_response

    # Act
    command = await ai_interpreter.parse_command("scan localhost with nmap")

    # Assert
    assert isinstance(command, Command)
    assert command.tool_name == "nmap"
    assert command.args == ["-sV", "localhost"]
    assert command.raw_command == "scan localhost with nmap"
    mock_generative_model.generate_content_async.assert_called_once()

@pytest.mark.asyncio
async def test_parse_command_json_fails(ai_interpreter, mock_generative_model):
    # Arrange
    mock_response = MagicMock()
    mock_response.text = 'this is not json'
    mock_generative_model.generate_content_async.return_value = mock_response

    # Act
    command = await ai_interpreter.parse_command("scan localhost with nmap")

    # Assert
    # Should fall back to simple parsing
    assert command.tool_name == "scan"
    assert command.args == ["localhost", "with", "nmap"]
