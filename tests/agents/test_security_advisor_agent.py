import pytest
from unittest.mock import AsyncMock, MagicMock
from termux_cyber_framework.agents.security_advisor_agent import SecurityAdvisorAgent
from termux_cyber_framework.core.domain.models import Command, ExecutionResult, Error
from datetime import datetime

@pytest.fixture
def mock_generative_model():
    """Fixture to mock the genai.GenerativeModel."""
    mock_model = MagicMock()
    mock_model.generate_content_async = AsyncMock()
    return mock_model

@pytest.fixture
def security_advisor_agent(mock_generative_model, monkeypatch):
    """Fixture to create a SecurityAdvisorAgent with a mocked model."""
    mock_configure = MagicMock()
    monkeypatch.setattr("google.generativeai.configure", mock_configure)

    mock_gen_model_class = MagicMock(return_value=mock_generative_model)
    monkeypatch.setattr("google.generativeai.GenerativeModel", mock_gen_model_class)

    agent = SecurityAdvisorAgent(api_key="test_key")
    return agent

@pytest.mark.asyncio
async def test_provide_advice_success(security_advisor_agent, mock_generative_model):
    # Arrange
    mock_response = MagicMock()
    mock_response.text = "You should run nikto next."
    mock_generative_model.generate_content_async.return_value = mock_response

    command = Command(tool_name="nmap", args=["example.com"], raw_command="nmap example.com")
    result = ExecutionResult(
        command=command,
        success=True,
        output="PORT 80/tcp open",
        error=None,
        start_time=datetime.now(),
        end_time=datetime.now()
    )

    # Act
    advice = await security_advisor_agent.provide_advice(result)

    # Assert
    assert advice == "You should run nikto next."
    mock_generative_model.generate_content_async.assert_called_once()
    prompt = mock_generative_model.generate_content_async.call_args[0][0]
    assert "nmap example.com" in prompt
    assert "PORT 80/tcp open" in prompt

@pytest.mark.asyncio
async def test_provide_advice_on_failure(security_advisor_agent, mock_generative_model):
    # Arrange
    command = Command(tool_name="nmap", args=[], raw_command="nmap")
    result = ExecutionResult(
        command=command,
        success=False,
        output="",
        error=Error(message="some error"),
        start_time=datetime.now(),
        end_time=datetime.now()
    )

    # Act
    advice = await security_advisor_agent.provide_advice(result)

    # Assert
    assert "No advice to give" in advice
    mock_generative_model.generate_content_async.assert_not_called()
