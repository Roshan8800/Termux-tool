import pytest
from unittest.mock import AsyncMock, MagicMock
from termux_cyber_framework.agents.security_advisor_agent import SecurityAdvisorAgent
from termux_cyber_framework.core.use_cases.ports import AIProcessingPort
from termux_cyber_framework.core.domain.models import Command, ExecutionResult
from datetime import datetime

@pytest.fixture
def mock_ai_service():
    """Provides a mock AIProcessingPort."""
    service = MagicMock(spec=AIProcessingPort)
    service.summarize_execution_result = AsyncMock()
    return service

@pytest.fixture
def security_advisor_agent(mock_ai_service):
    """Provides a SecurityAdvisorAgent instance with a mocked AI service."""
    return SecurityAdvisorAgent(ai_service=mock_ai_service)

@pytest.mark.asyncio
async def test_provide_advice_delegates_to_service(security_advisor_agent, mock_ai_service):
    # Arrange
    command = Command(tool_name="nmap", args=["example.com"], raw_command="nmap example.com")
    result = ExecutionResult(
        command=command,
        success=True,
        output="PORT 80/tcp open",
        error=None,
        start_time=datetime.now(),
        end_time=datetime.now()
    )
    expected_advice = "You should run nikto next."
    mock_ai_service.summarize_execution_result.return_value = expected_advice

    # Act
    advice = await security_advisor_agent.provide_advice(result)

    # Assert
    mock_ai_service.summarize_execution_result.assert_called_once_with(result)
    assert advice == expected_advice
