import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock
from rich.console import Console

# Mock the genai module at the top level to prevent real API calls
import sys
mock_genai = MagicMock()
sys.modules['google.generativeai'] = mock_genai

from termux_cyber_framework.adapters.command_parser.master_ai_interpreter import MasterAIInterpreter
from termux_cyber_framework.agents.config_manager_agent import ConfigManagerAgent

@pytest.fixture
def mock_config_manager():
    """Provides a mock ConfigManagerAgent."""
    return MagicMock(spec=ConfigManagerAgent)

@pytest.fixture
def mock_console():
    """Provides a mock rich Console."""
    return MagicMock(spec=Console)

@pytest.fixture
def agent(mock_config_manager, mock_console):
    """
    Provides a fully mocked MasterAIInterpreter instance for testing.
    This fixture patches the model and API key setup flows.
    """
    with patch('termux_cyber_framework.adapters.command_parser.master_ai_interpreter.MasterAIInterpreter._setup_api_key_flow', return_value="fake-key"), \
         patch('termux_cyber_framework.adapters.command_parser.master_ai_interpreter.MasterAIInterpreter._initialize_model') as mock_init_model:

        agent_instance = MasterAIInterpreter(
            api_key="fake-key",
            config_manager=mock_config_manager,
            console=mock_console
        )
        # Manually set a mock model instance for tests to use
        agent_instance.model = MagicMock()
        agent_instance.model.generate_content_async = AsyncMock()
        yield agent_instance

def test_init_handles_bad_api_key(mock_config_manager, mock_console):
    """Test that the agent initializes with model=None if the key is invalid."""
    # We test this by patching _initialize_model to simulate the failure
    with patch('termux_cyber_framework.adapters.command_parser.master_ai_interpreter.MasterAIInterpreter._initialize_model', lambda self: setattr(self, 'model', None)):
        agent = MasterAIInterpreter(
            api_key="bad-key",
            config_manager=mock_config_manager,
            console=mock_console
        )
        assert agent.model is None

@pytest.mark.asyncio
async def test_interpret_run_tool(agent):
    """Test interpreting a 'run_tool' command."""
    response_json = {"intent": "run_tool", "parameters": {"natural_language_command": "scan example.com"}}
    mock_response = MagicMock()
    mock_response.text = f"```json\n{json.dumps(response_json)}\n```"
    agent.model.generate_content_async.return_value = mock_response

    result = await agent.interpret("scan example.com")

    assert result == response_json

@pytest.mark.asyncio
async def test_interpret_set_api_key(agent):
    """Test interpreting a 'set_api_key' command."""
    response_json = {"intent": "set_api_key", "parameters": {"service": "google_gemini", "api_key": "123"}}
    mock_response = MagicMock()
    mock_response.text = json.dumps(response_json)
    agent.model.generate_content_async.return_value = mock_response

    result = await agent.interpret("set key to 123")

    assert result == response_json

@pytest.mark.asyncio
async def test_interpret_handles_api_error(agent):
    """Test that the interpreter returns an error on API failure."""
    agent.model.generate_content_async.side_effect = Exception("API Error")

    result = await agent.interpret("some command")

    assert result["intent"] == "error"
    assert "API Error" in result["parameters"]["message"]

@pytest.mark.asyncio
async def test_interpret_handles_invalid_json(agent):
    """Test that the interpreter returns an error for invalid JSON."""
    mock_response = MagicMock()
    mock_response.text = "this is not json"
    agent.model.generate_content_async.return_value = mock_response

    result = await agent.interpret("some command")

    assert result["intent"] == "error"
    assert "Failed to interpret command" in result["parameters"]["message"]
