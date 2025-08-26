import pytest
from unittest.mock import AsyncMock, MagicMock
from termux_cyber_framework.agents.error_fixer_agent import ErrorFixerAgent
from termux_cyber_framework.core.use_cases.ports import AIProcessingPort
from termux_cyber_framework.core.domain.models import Command, Error

@pytest.fixture
def mock_ai_service():
    """Provides a mock AIProcessingPort."""
    service = MagicMock(spec=AIProcessingPort)
    service.suggest_command_fix = AsyncMock()
    return service

@pytest.fixture
def error_fixer_agent(mock_ai_service):
    """Provides an ErrorFixerAgent instance with a mocked AI service."""
    return ErrorFixerAgent(ai_service=mock_ai_service)

@pytest.mark.asyncio
async def test_suggest_fix_delegates_to_service(error_fixer_agent, mock_ai_service):
    # Arrange
    command = Command(tool_name="nmap", args=[], raw_command="nmap")
    error = Error(message="Permission denied")
    expected_fix = Command(tool_name="sudo", args=["nmap"], raw_command="nmap")

    mock_ai_service.suggest_command_fix.return_value = expected_fix

    # Act
    fix_command = await error_fixer_agent.suggest_fix(command, error)

    # Assert
    mock_ai_service.suggest_command_fix.assert_called_once_with(command, error)
    assert fix_command == expected_fix

@pytest.mark.asyncio
async def test_suggest_fix_handles_no_fix_from_service(error_fixer_agent, mock_ai_service):
    # Arrange
    command = Command(tool_name="nmap", args=[], raw_command="nmap")
    error = Error(message="Host is down")

    # Simulate the service finding no fix
    mock_ai_service.suggest_command_fix.return_value = None

    # Act
    fix_command = await error_fixer_agent.suggest_fix(command, error)

    # Assert
    mock_ai_service.suggest_command_fix.assert_called_once_with(command, error)
    assert fix_command is None

@pytest.mark.asyncio
async def test_suggest_fix_handles_service_exception(error_fixer_agent, mock_ai_service):
    # Arrange
    command = Command(tool_name="nmap", args=[], raw_command="nmap")
    error = Error(message="Some error")

    # Simulate the service raising an exception
    mock_ai_service.suggest_command_fix.side_effect = Exception("AI Service exploded")

    # Act & Assert
    # The agent should probably not handle the exception itself, but let it propagate
    # to the orchestrator. This depends on the desired error handling strategy.
    # For now, let's assume it propagates.
    with pytest.raises(Exception, match="AI Service exploded"):
        await error_fixer_agent.suggest_fix(command, error)

    mock_ai_service.suggest_command_fix.assert_called_once_with(command, error)
