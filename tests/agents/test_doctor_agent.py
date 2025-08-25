import pytest
from unittest.mock import MagicMock, AsyncMock
from termux_cyber_framework.agents.doctor_agent import DoctorAgent
from termux_cyber_framework.core.domain.models import Tool

@pytest.fixture
def mock_tool_installer():
    return MagicMock()

@pytest.fixture
def mock_config_manager():
    return MagicMock()

@pytest.fixture
def mock_master_interpreter():
    interpreter = MagicMock()
    interpreter._validate_api_key = AsyncMock(return_value=True)
    return interpreter

@pytest.fixture
def doctor_agent(tmp_path, mock_tool_installer, mock_config_manager, mock_master_interpreter):
    catalog_path = tmp_path / "catalog.json"
    with open(catalog_path, "w") as f:
        f.write('[{"name": "nmap", "description": "A scanner", "install_info": {"method": "pkg", "source": "nmap"}}]')

    return DoctorAgent(
        tool_installer=mock_tool_installer,
        config_manager=mock_config_manager,
        master_interpreter=mock_master_interpreter,
        tool_catalog_path=str(catalog_path)
    )

@pytest.mark.asyncio
async def test_run_health_checks_all_ok(doctor_agent, mock_tool_installer, mock_config_manager, mock_master_interpreter):
    # Arrange
    mock_config_manager.config_exists.return_value = True
    mock_config_manager.get_api_key.return_value = "valid_key"
    mock_tool_installer.is_installed.return_value = True
    mock_master_interpreter._validate_api_key.return_value = True

    # Act
    results = await doctor_agent.run_health_checks()

    # Assert
    assert len(results) == 4
    assert all(check['status'] == 'OK' for check in results)
    mock_master_interpreter._validate_api_key.assert_called_once_with("valid_key")

@pytest.mark.asyncio
async def test_run_health_checks_with_warnings_and_errors(doctor_agent, mock_tool_installer, mock_config_manager, mock_master_interpreter):
    # Arrange
    mock_config_manager.config_exists.return_value = False
    mock_config_manager.get_api_key.return_value = "invalid_key"
    mock_tool_installer.is_installed.return_value = False
    mock_master_interpreter._validate_api_key.return_value = False

    # Act
    results = await doctor_agent.run_health_checks()

    # Assert
    assert len(results) == 4

    config_check = next(c for c in results if c['check'] == 'Configuration File')
    key_check = next(c for c in results if c['check'] == 'Gemini API Key')
    conn_check = next(c for c in results if c['check'] == 'Gemini API Connectivity')
    tool_check = next(c for c in results if c['check'] == 'Tool: nmap')

    assert config_check['status'] == 'ERROR'
    assert key_check['status'] == 'OK'
    assert conn_check['status'] == 'ERROR'
    assert tool_check['status'] == 'INFO'
