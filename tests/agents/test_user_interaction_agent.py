import pytest
from unittest.mock import patch, MagicMock, AsyncMock

# Mock the genai module
import sys
mock_genai = MagicMock()
sys.modules['google.generativeai'] = mock_genai

from termux_cyber_framework.agents.user_interaction_agent import UserInteractionAgent
from termux_cyber_framework.core.domain.models import ExecutionResult, Command, Error
from rich.console import Console

@pytest.fixture
def mock_console():
    """Provides a mock Console object."""
    return MagicMock(spec=Console)

@pytest.fixture
def agent(mock_console):
    """Fixture to create a UserInteractionAgent with a mocked AI model and console."""
    agent = UserInteractionAgent(console=mock_console, api_key="fake_key")
    agent.model = MagicMock()
    agent.model.generate_content_async = AsyncMock()
    return agent

@pytest.mark.asyncio
async def test_present_result_success(agent, mock_console):
    """Test that a successful result is summarized by the AI."""
    # Arrange
    result = ExecutionResult(command=Command(tool_name="nmap", raw_command="nmap test", args=[]), success=True, output="...")
    agent.model.generate_content_async.return_value.text = "AI summary of success."

    # Act
    await agent.present_result(result)

    # Assert
    agent.model.generate_content_async.assert_called_once()
    mock_console.print.assert_called_once()
    panel = mock_console.print.call_args[0][0]
    assert "AI summary of success." in panel.renderable

@pytest.mark.asyncio
async def test_present_result_error(agent, mock_console):
    """Test that a failed result is explained by the AI."""
    # Arrange
    error = Error(message="It broke")
    result = ExecutionResult(command=Command(tool_name="nmap", raw_command="nmap test", args=[]), success=False, error=error)
    agent.model.generate_content_async.return_value.text = "AI explanation of error."

    # Act
    await agent.present_result(result)

    # Assert
    agent.model.generate_content_async.assert_called_once()
    mock_console.print.assert_called_once()
    panel = mock_console.print.call_args[0][0]
    assert "AI explanation of error." in panel.renderable

@pytest.mark.asyncio
async def test_present_result_fallback(agent, mock_console):
    """Test the graceful fallback when the AI call fails."""
    # Arrange
    result = ExecutionResult(command=Command(tool_name="nmap", raw_command="nmap test", args=[]), success=True, output="Raw output here.")
    agent.model.generate_content_async.side_effect = Exception("AI API is down")

    # Act
    await agent.present_result(result)

    # Assert
    assert mock_console.print.call_count == 2
    panel = mock_console.print.call_args_list[1][0][0]
    assert "Raw output here." in panel.renderable

@pytest.mark.asyncio
async def test_present_result_scenario(agent, mock_console):
    """Test that a scenario result is summarized."""
    # Arrange
    results = [ExecutionResult(command=Command(tool_name="nmap", raw_command="nmap test", args=[]), success=True, output="...")]
    agent.model.generate_content_async.return_value.text = "AI summary of scenario."

    # Act
    await agent.present_result(results)

    # Assert
    agent.model.generate_content_async.assert_called_once()
    mock_console.print.assert_called_once()
    panel = mock_console.print.call_args[0][0]
    assert "AI summary of scenario." in panel.renderable
