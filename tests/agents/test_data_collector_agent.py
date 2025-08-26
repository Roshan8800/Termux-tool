import pytest
from unittest.mock import MagicMock, AsyncMock
from termux_cyber_framework.agents.data_collector_agent import DataCollectorAgent
from termux_cyber_framework.core.use_cases.ports import AIProcessingPort
from termux_cyber_framework.core.domain.models import Command, ExecutionResult
from datetime import datetime

@pytest.fixture
def mock_ai_service():
    """Provides a mock AIProcessingPort."""
    service = MagicMock(spec=AIProcessingPort)
    service.extract_data_from_output = AsyncMock()
    return service

@pytest.fixture
def agent(mock_ai_service):
    """Provides a DataCollectorAgent instance with a mocked AI service."""
    return DataCollectorAgent(ai_service=mock_ai_service)

@pytest.mark.asyncio
async def test_collect_data_delegates_to_service(agent, mock_ai_service):
    # Arrange
    command = Command(tool_name="nmap", args=["example.com"], raw_command="nmap example.com")
    result = ExecutionResult(
        command=command,
        success=True,
        output="Nmap scan report for example.com (93.184.216.34)",
        error=None,
        start_time=datetime.now(),
        end_time=datetime.now()
    )
    expected_data = [
        {"type": "domain_name", "value": "example.com"},
        {"type": "ip_address", "value": "93.184.216.34"}
    ]
    mock_ai_service.extract_data_from_output.return_value = expected_data

    # Act
    data = await agent.collect_data(result)

    # Assert
    mock_ai_service.extract_data_from_output.assert_called_once_with(result)
    assert data == expected_data
