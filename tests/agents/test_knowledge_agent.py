import pytest
import json
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

# Mock the genai module at the top level
import sys
mock_genai = MagicMock()
sys.modules['google.generativeai'] = mock_genai

from termux_cyber_framework.agents.knowledge_agent import KnowledgeAgent
from termux_cyber_framework.agents.file_manager_agent import FileManagerAgent
from termux_cyber_framework.core.use_cases.ports import LoggerPort

@pytest.fixture
def mock_file_manager():
    """Provides a mock FileManagerAgent."""
    return MagicMock(spec=FileManagerAgent)

@pytest.fixture
def mock_logger():
    """Provides a mock LoggerPort."""
    return MagicMock(spec=LoggerPort)

@pytest.fixture
def agent(mock_file_manager, mock_logger):
    """Provides a fully mocked KnowledgeAgent instance."""
    with patch('termux_cyber_framework.agents.knowledge_agent.KnowledgeAgent._initialize_model'):
        # Mock the file reads that happen during __init__
        mock_file_manager.read_file.side_effect = [
            json.dumps([{"name": "nmap"}]), # tool catalog
            json.dumps({}) # empty cache
        ]

        agent_instance = KnowledgeAgent(
            api_key="fake_key",
            file_manager=mock_file_manager,
            logger=mock_logger,
            tool_catalog_path="/fake/path"
        )
        # Manually set a mock model instance for tests to use
        agent_instance.model = MagicMock()
        agent_instance.model.generate_content_async = AsyncMock()

        # Reset side effect after init
        mock_file_manager.read_file.side_effect = None
        yield agent_instance

def test_init_handles_no_api_key(mock_file_manager, mock_logger):
    """Test agent initialization without an API key."""
    mock_file_manager.read_file.return_value = "{}"
    agent = KnowledgeAgent(api_key=None, file_manager=mock_file_manager, logger=mock_logger, tool_catalog_path="")
    assert agent.model is None
    result = asyncio.run(agent.query("test"))
    assert "disabled" in result

@pytest.mark.asyncio
async def test_query_uses_cache(agent):
    """Test that a second query for the same question hits the cache."""
    # Arrange
    question = "how do i use nmap?"
    cached_answer = "cached nmap answer"
    agent.query_cache = {question.lower(): cached_answer}

    # Act
    result = await agent.query(question)

    # Assert
    assert result == cached_answer
    agent.model.generate_content_async.assert_not_called()

@pytest.mark.asyncio
async def test_query_saves_to_cache(agent, mock_file_manager):
    """Test that a new query's result is saved to the cache."""
    # Arrange
    question = "what is xss?"
    ai_answer = "a fresh answer"
    agent.query_cache = {}

    mock_response = MagicMock()
    mock_response.text = ai_answer
    agent.model.generate_content_async.return_value = mock_response

    # Act
    result = await agent.query(question)

    # Assert
    assert result == ai_answer
    mock_file_manager.write_file.assert_called_once()
    written_content = mock_file_manager.write_file.call_args[0][1]
    cache_data = json.loads(written_content)
    assert cache_data[question.lower()] == ai_answer
