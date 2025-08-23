import pytest
from unittest.mock import AsyncMock, MagicMock
from termux_cyber_framework.agents.error_fixer_agent import ErrorFixerAgent
from termux_cyber_framework.core.domain.models import Command, Error

@pytest.fixture
def mock_generative_model():
    """Fixture to mock the genai.GenerativeModel."""
    mock_model = MagicMock()
    mock_model.generate_content_async = AsyncMock()
    return mock_model

@pytest.fixture
def error_fixer_agent(mock_generative_model, monkeypatch):
    """Fixture to create an ErrorFixerAgent with a mocked model."""
    mock_configure = MagicMock()
    monkeypatch.setattr("google.generativeai.configure", mock_configure)

    mock_gen_model_class = MagicMock(return_value=mock_generative_model)
    monkeypatch.setattr("google.generativeai.GenerativeModel", mock_gen_model_class)

    agent = ErrorFixerAgent(api_key="test_key")
    return agent

@pytest.mark.asyncio
async def test_suggest_fix_success(error_fixer_agent, mock_generative_model):
    # Arrange
    mock_response = MagicMock()
    mock_response.text = '{"tool": "sudo", "args": ["nmap"]}'
    mock_generative_model.generate_content_async.return_value = mock_response

    command = Command(tool_name="nmap", args=[], raw_command="nmap")
    error = Error(message="Permission denied")

    # Act
    fix_command = await error_fixer_agent.suggest_fix(command, error)

    # Assert
    assert isinstance(fix_command, Command)
    assert fix_command.tool_name == "sudo"
    assert fix_command.args == ["nmap"]
    mock_generative_model.generate_content_async.assert_called_once()

@pytest.mark.asyncio
async def test_suggest_fix_no_fix(error_fixer_agent, mock_generative_model):
    # Arrange
    mock_response = MagicMock()
    mock_response.text = "NO_FIX"
    mock_generative_model.generate_content_async.return_value = mock_response

    command = Command(tool_name="nmap", args=[], raw_command="nmap")
    error = Error(message="Host is down")

    # Act
    fix_command = await error_fixer_agent.suggest_fix(command, error)

    # Assert
    assert fix_command is None

@pytest.mark.asyncio
async def test_suggest_fix_invalid_json(error_fixer_agent, mock_generative_model):
    # Arrange
    mock_response = MagicMock()
    mock_response.text = "this is not json"
    mock_generative_model.generate_content_async.return_value = mock_response

    command = Command(tool_name="nmap", args=[], raw_command="nmap")
    error = Error(message="some error")

    # Act
    fix_command = await error_fixer_agent.suggest_fix(command, error)

    # Assert
    assert fix_command is None
