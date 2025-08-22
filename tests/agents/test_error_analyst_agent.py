import pytest
from unittest.mock import AsyncMock, MagicMock
from termux_cyber_framework.agents.error_analyst_agent import ErrorAnalystAgent
from termux_cyber_framework.core.domain.models import Command, Error

@pytest.fixture
def mock_generative_model():
    """Fixture to mock the genai.GenerativeModel."""
    mock_model = MagicMock()
    mock_model.generate_content_async = AsyncMock()
    return mock_model

@pytest.fixture
def error_analyst_agent(mock_generative_model, monkeypatch):
    """Fixture to create an ErrorAnalystAgent with a mocked model."""
    # Patch the genai.GenerativeModel to return our mock
    mock_configure = MagicMock()
    monkeypatch.setattr("google.generativeai.configure", mock_configure)

    mock_gen_model_class = MagicMock(return_value=mock_generative_model)
    monkeypatch.setattr("google.generativeai.GenerativeModel", mock_gen_model_class)

    agent = ErrorAnalystAgent(api_key="test_key")
    return agent

@pytest.mark.asyncio
async def test_analyze_error_success(error_analyst_agent, mock_generative_model):
    # Arrange
    mock_response = MagicMock()
    mock_response.text = "This is a mock AI analysis."
    mock_generative_model.generate_content_async.return_value = mock_response

    command = Command(tool_name="test", args=[], raw_command="test command")
    error = Error(message="Something went wrong")

    # Act
    analysis = await error_analyst_agent.analyze_error(command, error)

    # Assert
    assert analysis == "This is a mock AI analysis."
    mock_generative_model.generate_content_async.assert_called_once()
    prompt = mock_generative_model.generate_content_async.call_args[0][0]
    assert "test command" in prompt
    assert "Something went wrong" in prompt

@pytest.mark.asyncio
async def test_analyze_error_api_fails(error_analyst_agent, mock_generative_model):
    # Arrange
    mock_generative_model.generate_content_async.side_effect = Exception("API Failure")

    command = Command(tool_name="test", args=[], raw_command="test command")
    error = Error(message="Something went wrong")

    # Act
    analysis = await error_analyst_agent.analyze_error(command, error)

    # Assert
    assert "AI error analysis failed: API Failure" in analysis
