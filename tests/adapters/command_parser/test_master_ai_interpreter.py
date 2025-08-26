import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from rich.console import Console

from termux_cyber_framework.adapters.command_parser.master_ai_interpreter import MasterAIInterpreter
from termux_cyber_framework.agents.config_manager_agent import ConfigManagerAgent
from termux_cyber_framework.core.use_cases.ports import AIProcessingPort

@pytest.fixture
def mock_ai_service():
    """Provides a mock AIProcessingPort with a configurable api_key attribute."""
    service = MagicMock(spec=AIProcessingPort)
    service.api_key = None  # Start with no key by default
    service.model = None
    service.interpret_master_command = AsyncMock()
    return service

@pytest.fixture
def mock_config_manager():
    """Provides a mock ConfigManagerAgent."""
    return MagicMock(spec=ConfigManagerAgent)

@pytest.fixture
def mock_console():
    """Provides a mock rich.console.Console."""
    return MagicMock(spec=Console)

@pytest.fixture
def interpreter(mock_ai_service, mock_config_manager, mock_console):
    """Provides a MasterAIInterpreter instance with mocked dependencies."""
    # We patch the setup flow to avoid actual user input during tests
    with patch.object(MasterAIInterpreter, '_setup_api_key_flow', return_value=None) as mock_setup_flow:
        instance = MasterAIInterpreter(
            ai_service=mock_ai_service,
            config_manager=mock_config_manager,
            console=mock_console
        )
        instance.mock_setup_flow = mock_setup_flow
        yield instance

def test_init_with_no_api_key_triggers_setup_flow(interpreter, mock_ai_service):
    """
    Test that if the AI service has no API key, the setup flow is triggered.
    """
    # The setup flow is mocked in the fixture, so we just check if it was called.
    assert interpreter.mock_setup_flow.called

def test_init_with_api_key_does_not_trigger_setup_flow(mock_ai_service, mock_config_manager, mock_console):
    """
    Test that if the AI service already has an API key, the setup flow is not triggered.
    """
    mock_ai_service.api_key = "pre-existing-key"
    with patch.object(MasterAIInterpreter, '_setup_api_key_flow') as mock_setup_flow:
        MasterAIInterpreter(
            ai_service=mock_ai_service,
            config_manager=mock_config_manager,
            console=mock_console
        )
        assert not mock_setup_flow.called

@pytest.mark.asyncio
async def test_interpret_delegates_to_ai_service(interpreter, mock_ai_service):
    """
    Test that the interpret method correctly calls the central AI service.
    """
    # Arrange
    user_input = "scan example.com"
    expected_response = {"intent": "run_tool", "parameters": {}}
    mock_ai_service.interpret_master_command.return_value = expected_response
    # Pretend the model is loaded for this test
    mock_ai_service.model = MagicMock()

    # Act
    result = await interpreter.interpret(user_input)

    # Assert
    mock_ai_service.interpret_master_command.assert_called_once_with(user_input)
    assert result == expected_response

@pytest.mark.asyncio
async def test_interpret_returns_error_if_model_is_not_loaded(interpreter, mock_ai_service):
    """
    Test that an error is returned if the AI model is not available.
    """
    # Arrange
    user_input = "scan example.com"
    mock_ai_service.model = None # Ensure model is not loaded

    # Act
    result = await interpreter.interpret(user_input)

    # Assert
    assert result["intent"] == "error"
    assert "disabled" in result["parameters"]["message"]
    mock_ai_service.interpret_master_command.assert_not_called()
