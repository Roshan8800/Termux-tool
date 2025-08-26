import pytest
from unittest.mock import AsyncMock, MagicMock
from termux_cyber_framework.adapters.command_parser.ai_interpreter import AIInterpreter
from termux_cyber_framework.core.use_cases.ports import AIProcessingPort
from termux_cyber_framework.core.domain.models import Command

@pytest.fixture
def mock_ai_service():
    """Provides a mock AIProcessingPort."""
    service = MagicMock(spec=AIProcessingPort)
    service.interpret_tool_command = AsyncMock()
    return service

@pytest.fixture
def tool_catalog():
    """Provides a sample tool catalog."""
    return [{"name": "nmap", "description": "Network scanner"}]

@pytest.fixture
def ai_interpreter(mock_ai_service, tool_catalog):
    """Provides an AIInterpreter instance with a mocked AI service."""
    return AIInterpreter(ai_service=mock_ai_service, tool_catalog=tool_catalog)

@pytest.mark.asyncio
async def test_parse_command_success(ai_interpreter, mock_ai_service, tool_catalog):
    # Arrange
    user_input = "scan localhost with nmap"
    expected_command = Command(
        tool_name="nmap",
        args=["-sV", "localhost"],
        raw_command=user_input
    )
    mock_ai_service.interpret_tool_command.return_value = expected_command

    # Act
    command = await ai_interpreter.parse_command(user_input)

    # Assert
    mock_ai_service.interpret_tool_command.assert_called_once_with(user_input, tool_catalog)
    assert command == expected_command

@pytest.mark.asyncio
async def test_parse_command_fallback_on_exception(ai_interpreter, mock_ai_service, tool_catalog):
    # Arrange
    user_input = "scan localhost with nmap"
    mock_ai_service.interpret_tool_command.side_effect = Exception("AI service failed")

    # Act
    command = await ai_interpreter.parse_command(user_input)

    # Assert
    mock_ai_service.interpret_tool_command.assert_called_once_with(user_input, tool_catalog)
    # Verify that it falls back to simple parsing
    assert command.tool_name == "scan"
    assert command.args == ["localhost", "with", "nmap"]
    assert command.raw_command == user_input
