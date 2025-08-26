import pytest
from unittest.mock import MagicMock, AsyncMock
from termux_cyber_framework.agents.scenario_planner_agent import ScenarioPlannerAgent
from termux_cyber_framework.core.use_cases.ports import AIProcessingPort
from termux_cyber_framework.core.domain.models import Command

@pytest.fixture
def mock_ai_service():
    """Provides a mock AIProcessingPort."""
    service = MagicMock(spec=AIProcessingPort)
    service.plan_scenario = AsyncMock()
    return service

@pytest.fixture
def agent(mock_ai_service):
    """Provides a ScenarioPlannerAgent instance with a mocked AI service."""
    return ScenarioPlannerAgent(ai_service=mock_ai_service)

@pytest.mark.asyncio
async def test_plan_attack_scenario_delegates_to_service(agent, mock_ai_service):
    # Arrange
    goal = "Find and exploit SQL injection vulnerabilities on example.com"
    expected_plan = [
        Command(tool_name="nmap", args=["-p", "80,443", "example.com"], raw_command="nmap -p 80,443 example.com"),
        Command(tool_name="nikto", args=["-h", "http://example.com"], raw_command="nikto -h http://example.com")
    ]
    mock_ai_service.plan_scenario.return_value = expected_plan

    # Act
    plan = await agent.plan_attack_scenario(goal)

    # Assert
    mock_ai_service.plan_scenario.assert_called_once_with(goal)
    assert plan == expected_plan
