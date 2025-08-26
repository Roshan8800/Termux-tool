import pytest
import json
from unittest.mock import MagicMock, AsyncMock
from termux_cyber_framework.agents.knowledge_agent import KnowledgeAgent
from termux_cyber_framework.agents.file_manager_agent import FileManagerAgent
from termux_cyber_framework.core.use_cases.ports import LoggerPort, AIProcessingPort, LogLevel

@pytest.fixture
def mock_ai_service():
    """Provides a mock AIProcessingPort."""
    service = MagicMock(spec=AIProcessingPort)
    service.answer_knowledge_question = AsyncMock()
    return service

@pytest.fixture
def mock_file_manager():
    """Provides a mock FileManagerAgent."""
    manager = MagicMock(spec=FileManagerAgent)
    manager.read_file.return_value = ""  # Default to no cache
    manager.write_file.return_value = None
    return manager

@pytest.fixture
def mock_logger():
    """Provides a mock LoggerPort."""
    return MagicMock(spec=LoggerPort)

@pytest.fixture
def tool_catalog():
    """Provides a sample tool catalog."""
    return [{"name": "nmap", "description": "scanner"}, {"name": "sqlmap", "description": "injector"}]

@pytest.fixture
def knowledge_agent(mock_ai_service, mock_file_manager, mock_logger, tool_catalog):
    """Provides a KnowledgeAgent instance with mocked dependencies."""
    return KnowledgeAgent(
        ai_service=mock_ai_service,
        file_manager=mock_file_manager,
        logger=mock_logger,
        tool_catalog=tool_catalog
    )

@pytest.mark.asyncio
async def test_query_uses_cache(knowledge_agent, mock_ai_service, mock_file_manager):
    # Arrange
    question = "how do i use nmap?"
    cached_answer = "This is the cached answer for nmap."
    mock_file_manager.read_file.return_value = json.dumps({question: cached_answer})

    # Re-initialize agent to load the cache
    knowledge_agent._load_cache()

    # Act
    answer = await knowledge_agent.query(question)

    # Assert
    assert answer == cached_answer
    mock_ai_service.answer_knowledge_question.assert_not_called()
    knowledge_agent.logger.log.assert_any_call(f"Returning cached response for question: '{question}'", level=LogLevel.INFO)

@pytest.mark.asyncio
async def test_query_calls_ai_service_and_caches_result(knowledge_agent, mock_ai_service, mock_file_manager):
    # Arrange
    question = "what is sql injection?"
    ai_answer = "SQL injection is a vulnerability..."
    mock_ai_service.answer_knowledge_question.return_value = ai_answer

    # Act
    answer = await knowledge_agent.query(question)

    # Assert
    assert answer == ai_answer
    mock_ai_service.answer_knowledge_question.assert_called_once_with(question, tool_context=None)
    mock_file_manager.write_file.assert_called_once()
    # Check that the cache was updated correctly
    written_content = mock_file_manager.write_file.call_args[0][1]
    cache_data = json.loads(written_content)
    assert cache_data[question.lower()] == ai_answer

@pytest.mark.asyncio
async def test_query_detects_tool_and_passes_context(knowledge_agent, mock_ai_service):
    # Arrange
    question = "how to use sqlmap for blind injection?"
    ai_answer = "For blind injection with sqlmap, you can use..."
    mock_ai_service.answer_knowledge_question.return_value = ai_answer

    # Act
    answer = await knowledge_agent.query(question)

    # Assert
    assert answer == ai_answer
    # Verify that the detected tool name was passed as context
    mock_ai_service.answer_knowledge_question.assert_called_once_with(question, tool_context="sqlmap")
