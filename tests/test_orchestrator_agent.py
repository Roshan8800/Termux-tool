import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from termux_cyber_framework.core.use_cases.orchestrator_agent import OrchestratorAgent
from termux_cyber_framework.adapters.command_parser.master_ai_interpreter import MasterAIInterpreter
from termux_cyber_framework.core.domain.models import Command, ExecutionResult

# A simplified setup fixture for the new tests
@pytest.fixture
def mock_agents():
    """Provides a dictionary of mocked agents for testing the orchestrator."""
    agents = {
        "master_interpreter": MagicMock(spec=MasterAIInterpreter),
        "tool_command_parser": MagicMock(),
        "tool_adapters": {"nmap": MagicMock()},
        "report_generators": [],
        "error_analyst": MagicMock(),
        "error_fixer": MagicMock(),
        "tool_installer": MagicMock(),
        "security_advisor": MagicMock(),
        "network_agent": MagicMock(),
        "update_agent": MagicMock(),
        "config_manager": MagicMock(),
        "dependency_auditor": MagicMock(),
        "knowledge_agent": MagicMock(),
        "pentestgpt_agent": MagicMock(),
        "logger": MagicMock(),
        "config": MagicMock(),
        "audit_logger": MagicMock(),
        "consent_service": MagicMock(),
        "execution_history": MagicMock()
    }
    # Mock the interpret method to be async
    agents["master_interpreter"].interpret = AsyncMock()
    return agents

@pytest.mark.asyncio
async def test_handle_input_routes_to_run_tool(mock_agents):
    """Test that 'run_tool' intent calls the _handle_run_tool method."""
    # Arrange
    mock_agents["master_interpreter"].interpret.return_value = {
        "intent": "run_tool",
        "parameters": {"natural_language_command": "scan example.com"}
    }
    orchestrator = OrchestratorAgent(**mock_agents)

    # Patch the actual handler method to check if it's called
    mock_command = Command(tool_name="test_tool", raw_command="scan example.com")
    mock_result = ExecutionResult(command=mock_command, success=True, output="mocked output")
    orchestrator._handle_run_tool = AsyncMock(return_value=mock_result)

    # Act
    await orchestrator.handle_input("scan example.com")

    # Assert
    orchestrator._handle_run_tool.assert_called_once_with("scan example.com")

@pytest.mark.asyncio
async def test_handle_input_routes_to_update_system(mock_agents):
    """Test that 'update_system' intent calls the update_system method."""
    mock_agents["master_interpreter"].interpret.return_value = {
        "intent": "update_system",
        "parameters": {}
    }
    orchestrator = OrchestratorAgent(**mock_agents)
    orchestrator.update_system = AsyncMock(return_value="System updated.")

    await orchestrator.handle_input("update the system")

    orchestrator.update_system.assert_called_once()

@pytest.mark.asyncio
async def test_handle_input_routes_to_set_api_key(mock_agents):
    """Test that 'set_api_key' intent calls the config manager."""
    mock_agents["master_interpreter"].interpret.return_value = {
        "intent": "set_api_key",
        "parameters": {"service": "google", "api_key": "123"}
    }
    orchestrator = OrchestratorAgent(**mock_agents)

    await orchestrator.handle_input("set key")

    mock_agents["config_manager"].set_api_key.assert_called_once_with("google", "123")

@pytest.mark.asyncio
async def test_handle_input_routes_to_audit(mock_agents):
    """Test that 'audit_dependencies' intent calls the auditor."""
    mock_agents["master_interpreter"].interpret.return_value = {
        "intent": "audit_dependencies",
        "parameters": {}
    }
    orchestrator = OrchestratorAgent(**mock_agents)

    await orchestrator.handle_input("run audit")

    mock_agents["dependency_auditor"].run_audit.assert_called_once()

@pytest.mark.asyncio
async def test_handle_input_unknown_intent(mock_agents):
    """Test that an unknown intent returns an error message."""
    mock_agents["master_interpreter"].interpret.return_value = {
        "intent": "unknown",
        "parameters": {}
    }
    orchestrator = OrchestratorAgent(**mock_agents)
    result = await orchestrator.handle_input("gibberish")

    assert isinstance(result, ExecutionResult)
    assert result.success is False
    assert "Could not understand" in result.error.message

@pytest.mark.asyncio
async def test_handle_input_routes_to_pentest_analysis(mock_agents):
    """Test that 'run_pentest_analysis' intent calls the pentestgpt agent."""
    mock_agents["master_interpreter"].interpret.return_value = {
        "intent": "run_pentest_analysis",
        "parameters": {"model": "test_model"}
    }
    # Mock the new method name and its return value
    mock_agents["pentestgpt_agent"].ensure_environment_is_ready = AsyncMock(return_value="test_model")
    orchestrator = OrchestratorAgent(**mock_agents)

    result = await orchestrator.handle_input("run pentest analysis")

    # Assert the correct method was called
    mock_agents["pentestgpt_agent"].ensure_environment_is_ready.assert_called_once_with(override_model="test_model")
    # Assert the orchestrator returns the expected confirmation message
    assert "PentestGPT environment is ready" in result
