import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from termux_cyber_framework.core.use_cases.orchestrator_agent import OrchestratorAgent
from termux_cyber_framework.adapters.command_parser.master_ai_interpreter import MasterAIInterpreter
from termux_cyber_framework.core.domain.models import Command, ExecutionResult, Error

@pytest.fixture
def mock_agents():
    """Provides a dictionary of mocked agents for testing the orchestrator."""
    agents = {
        "master_interpreter": MagicMock(spec=MasterAIInterpreter),
        "tool_command_parser": MagicMock(),
        "tool_adapters": {"nmap": MagicMock(), "nikto": MagicMock()},
        "report_generators": [],
        "error_analyst": MagicMock(),
        "error_fixer": MagicMock(),
        "auto_editor": MagicMock(),
        "scenario_planner": MagicMock(),
        "data_collector": MagicMock(),
        "user_interaction_agent": MagicMock(),
        "tool_installer": MagicMock(),
        "security_advisor": MagicMock(),
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
    # Mock all async methods on the created mocks
    for agent in agents.values():
        if isinstance(agent, MagicMock):
            for method_name in dir(agent):
                if asyncio.iscoroutinefunction(getattr(agent, method_name, None)):
                    setattr(agent, method_name, AsyncMock())

    agents["master_interpreter"].interpret = AsyncMock()
    agents["user_interaction_agent"].present_result = AsyncMock()
    agents["pentestgpt_agent"].ensure_environment_is_ready = AsyncMock()
    agents["scenario_planner"].create_plan = AsyncMock()
    agents["data_collector"].process_and_store_result = AsyncMock()
    return agents

@pytest.mark.asyncio
async def test_handle_input_routes_to_run_tool(mock_agents):
    """Test that 'run_tool' intent calls the correct handler."""
    mock_agents["master_interpreter"].interpret.return_value = {"intent": "run_tool", "parameters": {"natural_language_command": "scan example.com"}}
    orchestrator = OrchestratorAgent(**mock_agents)
    orchestrator._handle_run_tool = AsyncMock()

    await orchestrator.handle_input("scan example.com")

    orchestrator._handle_run_tool.assert_called_once_with("scan example.com")
    mock_agents["user_interaction_agent"].present_result.assert_called_once()

@pytest.mark.asyncio
async def test_handle_input_unknown_intent(mock_agents):
    """Test that an unknown intent results in an error presentation."""
    mock_agents["master_interpreter"].interpret.return_value = {"intent": "unknown", "parameters": {}}
    orchestrator = OrchestratorAgent(**mock_agents)

    await orchestrator.handle_input("gibberish")

    mock_agents["user_interaction_agent"].present_result.assert_called_once()
    result_arg = mock_agents["user_interaction_agent"].present_result.call_args[0][0]
    assert isinstance(result_arg, ExecutionResult)
    assert not result_arg.success
    assert "Could not understand" in result_arg.error.message

@pytest.mark.asyncio
async def test_handle_input_routes_to_run_scenario(mock_agents):
    """Test that the 'run_scenario' intent is correctly handled."""
    goal = "test scenario"
    mock_agents["master_interpreter"].interpret.return_value = {"intent": "run_scenario", "parameters": {"goal": goal}}
    orchestrator = OrchestratorAgent(**mock_agents)
    orchestrator._handle_run_scenario = AsyncMock()

    await orchestrator.handle_input(goal)

    orchestrator._handle_run_scenario.assert_called_once_with(goal)
    mock_agents["user_interaction_agent"].present_result.assert_called_once()
