import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock

# Mock the genai module
import sys
mock_genai = MagicMock()
sys.modules['google.generativeai'] = mock_genai

from termux_cyber_framework.agents.scenario_planner_agent import ScenarioPlannerAgent
from termux_cyber_framework.core.domain.models import Command

@pytest.fixture
def mock_tool_catalog():
    """Provides a mock tool catalog."""
    return [
        {"name": "nmap", "description": "Port scanner"},
        {"name": "sqlmap", "description": "SQL injection tool"}
    ]

@pytest.fixture
def agent(mock_tool_catalog):
    """Fixture to create a ScenarioPlannerAgent with a mocked AI model."""
    agent = ScenarioPlannerAgent(api_key="fake_key", tool_catalog=mock_tool_catalog)
    agent.model = MagicMock()
    agent.model.generate_content_async = AsyncMock()
    return agent

@pytest.mark.asyncio
async def test_create_plan_success(agent):
    """Test successful plan generation."""
    # Arrange
    goal = "scan and find sql injection"
    mock_plan_json = """
    [
      {
        "tool": "nmap",
        "args": ["-sV", "example.com"]
      },
      {
        "tool": "sqlmap",
        "args": ["-u", "example.com"]
      }
    ]
    """
    mock_response = MagicMock()
    mock_response.text = mock_plan_json
    agent.model.generate_content_async.return_value = mock_response

    # Act
    plan = await agent.create_plan(goal)

    # Assert
    assert len(plan) == 2
    assert isinstance(plan[0], Command)
    assert plan[0].tool_name == "nmap"
    assert plan[1].tool_name == "sqlmap"
    agent.model.generate_content_async.assert_called_once()

@pytest.mark.asyncio
async def test_create_plan_invalid_json(agent):
    """Test that an empty plan is returned if the AI provides malformed JSON."""
    # Arrange
    goal = "test goal"
    mock_response = MagicMock()
    mock_response.text = "this is not json"
    agent.model.generate_content_async.return_value = mock_response

    # Act
    plan = await agent.create_plan(goal)

    # Assert
    assert plan == []

@pytest.mark.asyncio
async def test_create_plan_ai_fails(agent):
    """Test that an empty plan is returned if the AI call fails."""
    # Arrange
    goal = "test goal"
    agent.model.generate_content_async.side_effect = Exception("AI Error")

    # Act
    plan = await agent.create_plan(goal)

    # Assert
    assert plan == []

@pytest.mark.asyncio
async def test_create_plan_no_model(agent):
    """Test that an empty plan is returned if the model is not configured."""
    # Arrange
    agent.model = None
    goal = "test goal"

    # Act
    plan = await agent.create_plan(goal)

    # Assert
    assert plan == []
