import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from termux_cyber_framework.core.use_cases.orchestrator_agent import OrchestratorAgent
from termux_cyber_framework.adapters.command_parser.master_ai_interpreter import MasterAIInterpreter
from termux_cyber_framework.core.domain.models import Command, ExecutionResult

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
        "auto_editor": MagicMock(),
        "scenario_planner": MagicMock(),
        "data_collector": MagicMock(),
        "network_agent": MagicMock(),
        "update_agent": MagicMock(),
        "config_manager": MagicMock(),
        "dependency_auditor": MagicMock(),
        "knowledge_agent": MagicMock(),
        "pentestgpt_agent": MagicMock(),
        "pentestgpt_service_manager": MagicMock(),
        "logger": MagicMock(),
        "config": MagicMock(),
        "audit_logger": MagicMock(),
        "consent_service": MagicMock(),
        "execution_history": MagicMock()
    }
    agents["master_interpreter"].interpret = AsyncMock()
    # Mock the async method on the agent
    agents["pentestgpt_agent"].ensure_environment_is_ready = AsyncMock()
    return agents

# ... (other tests are unchanged)

@pytest.mark.asyncio
async def test_handle_input_routes_to_pentest_analysis_success(mock_agents):
    """Test that 'run_pentest_analysis' intent calls the service manager on success."""
    mock_agents["master_interpreter"].interpret.return_value = {"intent": "run_pentest_analysis", "parameters": {}}
    mock_agents["pentestgpt_agent"].ensure_environment_is_ready.return_value = "test_model"
    mock_agents["pentestgpt_service_manager"].start_session.return_value = True
    orchestrator = OrchestratorAgent(**mock_agents)

    result = await orchestrator.handle_input("run pentest analysis")

    mock_agents["pentestgpt_agent"].ensure_environment_is_ready.assert_called_once()
    mock_agents["pentestgpt_service_manager"].start_session.assert_called_once_with("test_model")
    assert "service started successfully" in result

@pytest.mark.asyncio
async def test_handle_input_routes_to_pentest_analysis_env_fail(mock_agents):
    """Test that 'run_pentest_analysis' fails gracefully if env setup fails."""
    mock_agents["master_interpreter"].interpret.return_value = {"intent": "run_pentest_analysis", "parameters": {}}
    mock_agents["pentestgpt_agent"].ensure_environment_is_ready.return_value = None # Simulate failure
    orchestrator = OrchestratorAgent(**mock_agents)

    result = await orchestrator.handle_input("run pentest analysis")

    mock_agents["pentestgpt_agent"].ensure_environment_is_ready.assert_called_once()
    mock_agents["pentestgpt_service_manager"].start_session.assert_not_called()
    assert "Failed to set up" in result

@pytest.mark.asyncio
async def test_handle_input_routes_to_pentest_analysis_service_fail(mock_agents):
    """Test that 'run_pentest_analysis' fails gracefully if service start fails."""
    mock_agents["master_interpreter"].interpret.return_value = {"intent": "run_pentest_analysis", "parameters": {}}
    mock_agents["pentestgpt_agent"].ensure_environment_is_ready.return_value = "test_model"
    mock_agents["pentestgpt_service_manager"].start_session.return_value = False # Simulate failure
    orchestrator = OrchestratorAgent(**mock_agents)

    result = await orchestrator.handle_input("run pentest analysis")

    mock_agents["pentestgpt_service_manager"].start_session.assert_called_once_with("test_model")
    assert "Failed to start" in result
# I will now fill in the rest of the test file
@pytest.mark.asyncio
async def test_handle_input_routes_to_run_tool(mock_agents):
    mock_agents["master_interpreter"].interpret.return_value = {"intent": "run_tool", "parameters": {"natural_language_command": "scan example.com"}}
    orchestrator = OrchestratorAgent(**mock_agents)
    mock_command = Command(tool_name="test_tool", raw_command="scan example.com")
    mock_result = ExecutionResult(command=mock_command, success=True, output="mocked output")
    orchestrator._handle_run_tool = AsyncMock(return_value=mock_result)
    await orchestrator.handle_input("scan example.com")
    orchestrator._handle_run_tool.assert_called_once_with("scan example.com")

@pytest.mark.asyncio
async def test_handle_input_routes_to_update_system(mock_agents):
    mock_agents["master_interpreter"].interpret.return_value = {"intent": "update_system", "parameters": {}}
    orchestrator = OrchestratorAgent(**mock_agents)
    orchestrator.update_system = AsyncMock(return_value="System updated.")
    await orchestrator.handle_input("update the system")
    orchestrator.update_system.assert_called_once()

@pytest.mark.asyncio
async def test_handle_input_routes_to_set_api_key(mock_agents):
    mock_agents["master_interpreter"].interpret.return_value = {"intent": "set_api_key", "parameters": {"service": "google", "api_key": "123"}}
    orchestrator = OrchestratorAgent(**mock_agents)
    await orchestrator.handle_input("set key")
    mock_agents["config_manager"].set_api_key.assert_called_once_with("google", "123")

@pytest.mark.asyncio
async def test_handle_input_routes_to_audit(mock_agents):
    mock_agents["master_interpreter"].interpret.return_value = {"intent": "audit_dependencies", "parameters": {}}
    orchestrator = OrchestratorAgent(**mock_agents)
    await orchestrator.handle_input("run audit")
    mock_agents["dependency_auditor"].run_audit.assert_called_once()

@pytest.mark.asyncio
async def test_handle_input_unknown_intent(mock_agents):
    mock_agents["master_interpreter"].interpret.return_value = {"intent": "unknown", "parameters": {}}
    orchestrator = OrchestratorAgent(**mock_agents)
    result = await orchestrator.handle_input("gibberish")
    assert isinstance(result, ExecutionResult)
    assert result.success is False
    assert "Could not understand" in result.error.message
