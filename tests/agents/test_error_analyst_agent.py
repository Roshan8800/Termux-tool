import pytest
from unittest.mock import AsyncMock, MagicMock
from termux_cyber_framework.agents.error_analyst_agent import ErrorAnalystAgent
from termux_cyber_framework.agents.knowledge_agent import KnowledgeAgent
from termux_cyber_framework.core.domain.models import Command, Error

@pytest.fixture
def mock_generative_model():
    """Fixture to mock the genai.GenerativeModel."""
    mock_model = MagicMock()
    mock_model.generate_content_async = AsyncMock()
    return mock_model

@pytest.fixture
def mock_knowledge_agent():
    """Fixture to mock the KnowledgeAgent."""
    mock_agent = MagicMock(spec=KnowledgeAgent)
    mock_agent.query = AsyncMock()
    return mock_agent

@pytest.fixture
def error_analyst_agent(mock_generative_model, mock_knowledge_agent, monkeypatch):
    """Fixture to create an ErrorAnalystAgent with mocked dependencies."""
    mock_configure = MagicMock()
    monkeypatch.setattr("google.generativeai.configure", mock_configure)

    mock_gen_model_class = MagicMock(return_value=mock_generative_model)
    monkeypatch.setattr("google.generativeai.GenerativeModel", mock_gen_model_class)

    agent = ErrorAnalystAgent(api_key="test_key", knowledge_agent=mock_knowledge_agent)
    return agent

@pytest.mark.asyncio
async def test_analyze_error_success(error_analyst_agent, mock_generative_model, mock_knowledge_agent):
    # Arrange
    mock_generative_model.generate_content_async.return_value = MagicMock(text="Primary analysis.")
    mock_knowledge_agent.query.return_value = "Knowledge context."

    command = Command(tool_name="test", args=[], raw_command="test command")
    error = Error(message="Something went wrong")

    # Act
    analysis = await error_analyst_agent.analyze_error(command, error)

    # Assert
    assert "Primary analysis." in analysis
    assert "Knowledge context." in analysis
    mock_generative_model.generate_content_async.assert_called_once()
    mock_knowledge_agent.query.assert_called_once()

@pytest.mark.asyncio
async def test_analyze_error_disabled_if_no_api_key(mock_knowledge_agent):
    # Arrange
    agent = ErrorAnalystAgent(api_key=None, knowledge_agent=mock_knowledge_agent)
    command = Command(tool_name="test", args=[], raw_command="test command")
    error = Error(message="Something went wrong")

    # Act
    analysis = await agent.analyze_error(command, error)

    # Assert
    assert "disabled" in analysis
    mock_knowledge_agent.query.assert_not_called()
