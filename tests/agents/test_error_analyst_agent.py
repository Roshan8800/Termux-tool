import pytest
from unittest.mock import AsyncMock, MagicMock
from termux_cyber_framework.agents.error_analyst_agent import ErrorAnalystAgent
from termux_cyber_framework.agents.knowledge_agent import KnowledgeAgent
from termux_cyber_framework.core.use_cases.ports import AIProcessingPort
from termux_cyber_framework.core.domain.models import Command, Error

@pytest.fixture
def mock_ai_service():
    """Provides a mock AIProcessingPort."""
    service = MagicMock(spec=AIProcessingPort)
    service.analyze_error = AsyncMock()
    return service

@pytest.fixture
def mock_knowledge_agent():
    """Provides a mock KnowledgeAgent."""
    agent = MagicMock(spec=KnowledgeAgent)
    agent.query = AsyncMock()
    return agent

@pytest.fixture
def agent(mock_ai_service, mock_knowledge_agent):
    """Provides an ErrorAnalystAgent instance with mocked dependencies."""
    return ErrorAnalystAgent(
        ai_service=mock_ai_service,
        knowledge_agent=mock_knowledge_agent
    )

@pytest.mark.asyncio
async def test_analyze_error_combines_results(agent, mock_ai_service, mock_knowledge_agent):
    """
    Test that analyze_error calls both the AI service and the knowledge agent
    and correctly combines their responses.
    """
    # Arrange
    command = Command(tool_name="test", args=[], raw_command="test command")
    error = Error(message="Something went wrong")

    mock_ai_service.analyze_error.return_value = "Primary AI analysis."
    mock_knowledge_agent.query.return_value = "Additional knowledge context."

    # Act
    analysis = await agent.analyze_error(command, error)

    # Assert
    mock_ai_service.analyze_error.assert_called_once_with(command, error)
    mock_knowledge_agent.query.assert_called_once()

    assert "Primary AI analysis." in analysis
    assert "Additional knowledge context." in analysis

@pytest.mark.asyncio
async def test_analyze_error_handles_knowledge_agent_failure(agent, mock_ai_service, mock_knowledge_agent):
    """
    Test that the analysis still works if the knowledge agent provides no useful info.
    """
    # Arrange
    command = Command(tool_name="test", args=[], raw_command="test command")
    error = Error(message="Something went wrong")

    mock_ai_service.analyze_error.return_value = "Primary AI analysis."
    # Simulate a response from the knowledge agent that should be ignored
    mock_knowledge_agent.query.return_value = "An error occurred while querying."

    # Act
    analysis = await agent.analyze_error(command, error)

    # Assert
    assert "Primary AI analysis." in analysis
    assert "An error occurred" not in analysis # The knowledge agent's error message shouldn't be in the final output
